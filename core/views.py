from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from accounts.models import User, UserProfile
from .models import (
    ActivityEvent,
    CompanyTarget,
    DailyPlanItem,
    Track,
    Topic,
    UserTopicProgress,
    Question,
    UserAnswer,
    Test,
    TestAttempt,
)
from .serializers import TrackSerializer, TopicSerializer, QuestionSerializer, TestSerializer
from .bootstrap import COMPANY_CATALOG, ensure_platform_catalog, ensure_user_preparation_data
import os
import requests


def percentage(part, total):
    if not total:
        return 0
    return round((part / total) * 100)


def bounded_percentage(value):
    return max(0, min(100, int(round(value or 0))))


def tone_for_progress(value):
    if value >= 75:
        return "green"
    if value >= 40:
        return "amber"
    if value > 0:
        return "cyan"
    return "slate"


def learning_status_label(status):
    labels = {
        "completed": "Completed",
        "in_progress": "In progress",
        "current": "Current focus",
        "ready": "Ready",
        "locked": "Locked",
    }
    return labels.get(status, "Ready")


def company_catalog_for(name):
    return COMPANY_CATALOG.get(name, {
        "name": name,
        "full_name": name,
        "official_url": "",
        "source_label": "Internal target",
        "source_note": "Student-defined target company. Add official career research before applying.",
        "roles": [],
        "campus_focus": [],
        "eligibility_notes": [],
        "prep_focus": [],
        "salary_note": "Verify compensation from official hiring communication.",
        "hiring_signal": "Research the current role and align preparation.",
    })


def admin_relative_time(moment, now):
    if not moment:
        return ""

    delta = now - moment
    seconds = max(0, int(delta.total_seconds()))

    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        return f"{seconds // 60} min ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    if seconds < 172800:
        return "Yesterday"
    return f"{seconds // 86400} days ago"


def difficulty_mix(topic):
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for row in topic.questions.values("difficulty").annotate(total=Count("id")):
        counts[row["difficulty"]] = row["total"]
    return counts


def topic_accuracy_for_user(user, topic):
    answers = UserAnswer.objects.filter(user=user, question__topic=topic)
    total = answers.count()
    correct = answers.filter(is_correct=True).count()
    return {
        "attempts": total,
        "correct": correct,
        "accuracy": percentage(correct, total),
    }


class TrackListView(APIView):
    def get(self, request):
        ensure_platform_catalog()
        tracks = Track.objects.all()
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)


class LearningPathView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        user = request.user

        progress_lookup = {
            progress.topic_id: progress
            for progress in UserTopicProgress.objects.filter(user=user).select_related("topic")
        }

        question_totals = {
            row["topic_id"]: row["total"]
            for row in Question.objects.values("topic_id").annotate(total=Count("id"))
        }

        difficulty_counts = {}
        for row in Question.objects.values("topic_id", "difficulty").annotate(total=Count("id")):
            topic_mix = difficulty_counts.setdefault(row["topic_id"], {"easy": 0, "medium": 0, "hard": 0})
            topic_mix[row["difficulty"]] = row["total"]

        answer_stats = {}
        for row in UserAnswer.objects.filter(user=user).values("question__topic_id").annotate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        ):
            answer_stats[row["question__topic_id"]] = {
                "total": row["total"],
                "correct": row["correct"],
            }

        tracks_payload = []
        all_topics = []
        current_assigned = False

        for track in Track.objects.all().order_by("name", "id"):
            topics = list(track.topics.filter(is_active=True).order_by("order", "id"))
            total_topics = len(topics)
            completed_topics = 0
            track_question_count = 0
            remaining_minutes = 0
            previous_topics_complete = True
            topic_payload = []

            for index, topic in enumerate(topics):
                progress = progress_lookup.get(topic.id)
                is_completed = bool(progress and progress.is_completed)
                completed_at = progress.completed_at if progress and progress.completed_at else None
                stats = answer_stats.get(topic.id, {"total": 0, "correct": 0})
                attempts = stats["total"]
                correct = stats["correct"]
                accuracy = percentage(correct, attempts)
                question_count = question_totals.get(topic.id, 0)
                estimate = max(20, (question_count or 4) * 5)
                has_started = attempts > 0 or bool(progress)
                is_locked = not is_completed and not has_started and not previous_topics_complete

                if is_completed:
                    status_key = "completed"
                    completed_topics += 1
                elif attempts > 0:
                    status_key = "in_progress"
                elif is_locked:
                    status_key = "locked"
                else:
                    status_key = "ready"

                if not is_completed and not is_locked and not current_assigned:
                    status_key = "current"
                    current_assigned = True

                if not is_completed:
                    remaining_minutes += estimate

                topic_tone = "green" if is_completed else "slate" if is_locked else tone_for_progress(accuracy if attempts else 40)
                item = {
                    "id": topic.id,
                    "track_id": track.id,
                    "track_name": track.name,
                    "name": topic.name,
                    "description": topic.description,
                    "order": topic.order,
                    "checkpoint": f"{index + 1}/{total_topics}",
                    "is_completed": is_completed,
                    "is_locked": is_locked,
                    "status": status_key,
                    "status_label": learning_status_label(status_key),
                    "tone": topic_tone,
                    "question_count": question_count,
                    "attempts": attempts,
                    "correct_answers": correct,
                    "accuracy": accuracy,
                    "difficulty_mix": difficulty_counts.get(topic.id, {"easy": 0, "medium": 0, "hard": 0}),
                    "estimated_minutes": estimate,
                    "completed_at": completed_at.isoformat() if completed_at else None,
                }
                topic_payload.append(item)
                all_topics.append(item)
                track_question_count += question_count

                if not is_completed:
                    previous_topics_complete = False

            track_progress = percentage(completed_topics, total_topics)
            tracks_payload.append({
                "id": track.id,
                "name": track.name,
                "description": track.description,
                "status": "Completed" if total_topics and completed_topics == total_topics else "Active" if completed_topics else "Available",
                "tone": tone_for_progress(track_progress),
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "progress_percentage": track_progress,
                "question_count": track_question_count,
                "estimated_remaining_minutes": remaining_minutes,
                "topics": topic_payload,
            })

        focus_candidates = [
            topic
            for topic in all_topics
            if not topic["is_completed"] and not topic["is_locked"]
        ]
        focus_candidates.sort(key=lambda topic: (
            0 if topic["attempts"] > 0 and topic["accuracy"] < 60 else 1,
            0 if topic["status"] == "current" else 1,
            topic["track_name"],
            topic["order"],
            topic["id"],
        ))
        focus_queue = [
            {
                **topic,
                "reason": (
                    "Accuracy below target"
                    if topic["attempts"] > 0 and topic["accuracy"] < 60
                    else "Next unlocked checkpoint"
                ),
            }
            for topic in focus_candidates[:5]
        ]

        recent_completions = [
            {
                "id": progress.topic_id,
                "topic": progress.topic.name,
                "track": progress.topic.track.name if progress.topic.track else "Learning path",
                "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
            }
            for progress in UserTopicProgress.objects.filter(
                user=user,
                is_completed=True,
                completed_at__isnull=False,
            ).select_related("topic", "topic__track").order_by("-completed_at")[:5]
        ]

        total_topics = len(all_topics)
        completed_topics = sum(1 for topic in all_topics if topic["is_completed"])
        completed_tracks = sum(
            1 for track in tracks_payload
            if track["total_topics"] and track["completed_topics"] == track["total_topics"]
        )
        total_questions = sum(topic["question_count"] for topic in all_topics)
        attempted_topics = sum(1 for topic in all_topics if topic["attempts"] > 0)
        remaining_minutes = sum(topic["estimated_minutes"] for topic in all_topics if not topic["is_completed"])

        return Response({
            "summary": {
                "total_tracks": len(tracks_payload),
                "completed_tracks": completed_tracks,
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "attempted_topics": attempted_topics,
                "total_questions": total_questions,
                "remaining_minutes": remaining_minutes,
                "progress_percentage": percentage(completed_topics, total_topics),
                "next_topic": focus_queue[0] if focus_queue else None,
            },
            "tracks": tracks_payload,
            "focus_queue": focus_queue,
            "recent_completions": recent_completions,
        })


class TopicByTrackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, track_id):
        ensure_user_preparation_data(request.user)
        topics = Topic.objects.filter(track_id=track_id).order_by('order')

        response_data = []

        for topic in topics:
            progress = UserTopicProgress.objects.filter(
                user=request.user,
                topic=topic,
                is_completed=True
            ).first()

            response_data.append({
                "id": topic.id,
                "name": topic.name,
                "description": topic.description,
                "order": topic.order,
                "is_completed": True if progress else False
            })

        return Response(response_data)

# ✅ NEW
class CompleteTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topic_id):
        ensure_user_preparation_data(request.user)
        try:
            topic = Topic.objects.get(id=topic_id, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=404)

        progress, created = UserTopicProgress.objects.get_or_create(
            user=request.user,
            topic=topic
        )

        was_completed = progress.is_completed
        progress.is_completed = True
        progress.completed_at = progress.completed_at or timezone.now()
        progress.save()

        if not was_completed:
            ActivityEvent.objects.create(
                user=request.user,
                event_type="Path",
                title=f"Completed {topic.name}",
                occurred_at=timezone.now(),
                metadata={"topic_id": topic.id, "track_id": topic.track_id},
            )

        return Response({
            "message": "Topic marked as completed",
            "topic_id": topic.id,
            "is_completed": True,
            "completed_at": progress.completed_at,
        })


class TopicProgressUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, topic_id):
        ensure_user_preparation_data(request.user)
        try:
            topic = Topic.objects.get(id=topic_id, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=404)

        raw_value = request.data.get("is_completed")
        if isinstance(raw_value, bool):
            is_completed = raw_value
        elif isinstance(raw_value, str) and raw_value.lower() in ["true", "false", "1", "0", "yes", "no"]:
            is_completed = raw_value.lower() in ["true", "1", "yes"]
        else:
            return Response({"error": "is_completed must be a boolean."}, status=400)

        progress, created = UserTopicProgress.objects.get_or_create(
            user=request.user,
            topic=topic,
        )

        was_completed = progress.is_completed
        progress.is_completed = is_completed
        progress.completed_at = timezone.now() if is_completed else None
        progress.save()

        if is_completed and not was_completed:
            ActivityEvent.objects.create(
                user=request.user,
                event_type="Path",
                title=f"Completed {topic.name}",
                occurred_at=timezone.now(),
                metadata={"topic_id": topic.id, "track_id": topic.track_id},
            )

        return Response({
            "message": "Topic progress updated",
            "topic_id": topic.id,
            "is_completed": progress.is_completed,
            "completed_at": progress.completed_at,
        })
    
class TrackProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, track_id):
        ensure_user_preparation_data(request.user)
        total_topics = Topic.objects.filter(track_id=track_id).count()

        completed_topics = UserTopicProgress.objects.filter(
            user=request.user,
            topic__track_id=track_id,
            is_completed=True
        ).count()

        progress = 0
        if total_topics > 0:
            progress = (completed_topics / total_topics) * 100

        return Response({
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "progress_percentage": round(progress, 2)
        })
    
class QuestionByTopicView(APIView):
    def get(self, request, topic_id):
        ensure_platform_catalog()
        questions = Question.objects.filter(topic_id=topic_id)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)
    
class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        ensure_user_preparation_data(request.user)
        user_answer = request.data.get("answer")

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        is_correct = (user_answer == question.correct_answer)

        # ✅ SAVE USER ANSWER
        UserAnswer.objects.create(
            user=request.user,
            question=question,
            selected_answer=user_answer,
            is_correct=is_correct
        )

        return Response({
            "correct": is_correct
        })
    
class WeakTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        topics = Topic.objects.all()

        weak_topics = []

        for topic in topics:
            total = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic
            ).count()

            if total == 0:
                continue

            correct = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic,
                is_correct=True
            ).count()

            accuracy = (correct / total) * 100

            if accuracy < 50:
                weak_topics.append({
                    "topic": topic.name,
                    "accuracy": round(accuracy, 2)
                })

        return Response(weak_topics)
    
class TestDetailView(APIView):
    def get(self, request, test_id):
        ensure_platform_catalog()
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test not found"}, status=404)

        serializer = TestSerializer(test)
        return Response(serializer.data)

from rest_framework.permissions import IsAuthenticated

class StartTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):
        ensure_user_preparation_data(request.user)
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test not found"}, status=404)

        attempt = TestAttempt.objects.create(
            user=request.user,
            test=test,
            total_questions=test.questions.count()
        )

        return Response({
            "message": "Test started",
            "attempt_id": attempt.id,
            "total_questions": attempt.total_questions
        })

from django.utils import timezone

class SubmitTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        attempt_id = request.data.get("attempt_id")
        answers = request.data.get("answers", {})

        try:
            attempt = TestAttempt.objects.get(id=attempt_id, user=request.user)
        except TestAttempt.DoesNotExist:
            return Response({"error": "Invalid attempt"}, status=404)

        score = 0
        detailed_result = []

        for q_id, user_ans in answers.items():
            try:
                question = Question.objects.get(id=q_id)
            except Question.DoesNotExist:
                continue

            is_correct = (user_ans == question.correct_answer)

            if is_correct:
                score += 1

            detailed_result.append({
                "question_id": q_id,
                "your_answer": user_ans,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct
            })

        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save()

        return Response({
            "score": score,
            "total": attempt.total_questions,
            "results": detailed_result
        })
    
class TopicAccuracyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        topics = Topic.objects.all()
        result = []

        for topic in topics:
            total = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic
            ).count()

            if total == 0:
                continue

            correct = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic,
                is_correct=True
            ).count()

            accuracy = (correct / total) * 100

            result.append({
                "topic": topic.name,
                "accuracy": round(accuracy, 2)
            })

        return Response(result)
    
class OverallPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        total = UserAnswer.objects.filter(user=request.user).count()

        correct = UserAnswer.objects.filter(
            user=request.user,
            is_correct=True
        ).count()

        accuracy = 0
        if total > 0:
            accuracy = (correct / total) * 100

        return Response({
            "total_attempts": total,
            "correct_answers": correct,
            "accuracy": round(accuracy, 2)
        })
    
class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)

        # 🔹 Overall Performance
        total = UserAnswer.objects.filter(user=request.user).count()
        correct = UserAnswer.objects.filter(
            user=request.user,
            is_correct=True
        ).count()

        overall_accuracy = 0
        if total > 0:
            overall_accuracy = (correct / total) * 100

        overall_data = {
            "total_attempts": total,
            "correct_answers": correct,
            "accuracy": round(overall_accuracy, 2)
        }

        # 🔹 Topic-wise Accuracy
        topics = Topic.objects.all()
        topic_data = []

        for topic in topics:
            t_total = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic
            ).count()

            if t_total == 0:
                continue

            t_correct = UserAnswer.objects.filter(
                user=request.user,
                question__topic=topic,
                is_correct=True
            ).count()

            t_accuracy = (t_correct / t_total) * 100

            topic_data.append({
                "topic": topic.name,
                "accuracy": round(t_accuracy, 2)
            })

        # 🔹 Weak Topics (<50%)
        weak_topics = [
            t for t in topic_data if t["accuracy"] < 50
        ]

        return Response({
            "overall": overall_data,
            "topics": topic_data,
            "weak_topics": weak_topics
        })


class PracticeDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        topics = Topic.objects.filter(is_active=True).select_related("track").prefetch_related("questions").order_by("track__name", "order", "id")
        tests = Test.objects.prefetch_related("topics", "questions").order_by("name")

        topic_cards = []
        weak_candidates = []
        total_questions = 0
        total_attempts = UserAnswer.objects.filter(user=request.user).count()
        correct_attempts = UserAnswer.objects.filter(user=request.user, is_correct=True).count()

        for topic in topics:
            stats = topic_accuracy_for_user(request.user, topic)
            question_count = topic.questions.count()
            total_questions += question_count
            priority = "high" if stats["attempts"] and stats["accuracy"] < 55 else "medium" if stats["accuracy"] < 70 else "steady"
            card = {
                "id": topic.id,
                "name": topic.name,
                "track": topic.track.name if topic.track else "General",
                "description": topic.description,
                "question_count": question_count,
                "difficulty_mix": difficulty_mix(topic),
                "attempts": stats["attempts"],
                "accuracy": stats["accuracy"],
                "priority": priority,
                "tone": tone_for_progress(stats["accuracy"] if stats["attempts"] else 40),
                "recommended_minutes": 25 if priority == "high" else 18 if priority == "medium" else 12,
            }
            topic_cards.append(card)
            if priority == "high":
                weak_candidates.append(card)

        recommended = sorted(
            topic_cards,
            key=lambda item: (
                0 if item["priority"] == "high" else 1,
                item["attempts"],
                item["accuracy"],
                item["track"],
            ),
        )[:6]

        test_payload = []
        for test in tests:
            latest_attempt = TestAttempt.objects.filter(
                user=request.user,
                test=test,
                completed_at__isnull=False,
            ).order_by("-completed_at").first()
            test_payload.append({
                "id": test.id,
                "name": test.name,
                "description": test.description,
                "duration_minutes": test.duration_minutes,
                "question_count": test.questions.count(),
                "topic_count": test.topics.count(),
                "last_score": percentage(latest_attempt.score, latest_attempt.total_questions) if latest_attempt else None,
                "last_completed_at": latest_attempt.completed_at.isoformat() if latest_attempt else None,
            })

        sample_topic = recommended[0] if recommended else topic_cards[0] if topic_cards else None
        sample_questions = []
        if sample_topic:
            sample_questions = [
                {
                    "id": question.id,
                    "question_text": question.question_text,
                    "difficulty": question.difficulty,
                    "options": {
                        "A": question.option_a,
                        "B": question.option_b,
                        "C": question.option_c,
                        "D": question.option_d,
                    },
                }
                for question in Question.objects.filter(topic_id=sample_topic["id"]).order_by("difficulty", "id")[:6]
            ]

        return Response({
            "summary": {
                "total_topics": len(topic_cards),
                "total_questions": total_questions,
                "attempts": total_attempts,
                "accuracy": percentage(correct_attempts, total_attempts),
                "weak_topics": len(weak_candidates),
            },
            "recommended": recommended,
            "topics": topic_cards,
            "tests": test_payload,
            "sample_topic": sample_topic,
            "sample_questions": sample_questions,
            "daily_drills": [
                {"label": "Aptitude sprint", "duration": "20 min", "target": "15 questions", "tone": "amber"},
                {"label": "DSA implementation", "duration": "30 min", "target": "2 problems", "tone": "cyan"},
                {"label": "SQL accuracy", "duration": "18 min", "target": "8 queries", "tone": "green"},
                {"label": "Project explanation", "duration": "12 min", "target": "1 story", "tone": "violet"},
            ],
        })


class FullAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        today = timezone.localdate()
        answers = UserAnswer.objects.filter(user=request.user)
        attempts = TestAttempt.objects.filter(user=request.user, completed_at__isnull=False, total_questions__gt=0)
        total_answers = answers.count()
        correct_answers = answers.filter(is_correct=True).count()

        topic_payload = []
        for topic in Topic.objects.filter(is_active=True).select_related("track").order_by("track__name", "order", "id"):
            stats = topic_accuracy_for_user(request.user, topic)
            topic_payload.append({
                "topic": topic.name,
                "track": topic.track.name if topic.track else "General",
                "accuracy": stats["accuracy"],
                "attempts": stats["attempts"],
                "correct": stats["correct"],
                "tone": tone_for_progress(stats["accuracy"] if stats["attempts"] else 0),
            })

        track_payload = []
        for track in Track.objects.all().order_by("name"):
            total_topics = track.topics.filter(is_active=True).count()
            completed_topics = UserTopicProgress.objects.filter(
                user=request.user,
                topic__track=track,
                is_completed=True,
            ).count()
            track_payload.append({
                "track": track.name,
                "progress": percentage(completed_topics, total_topics),
                "completed_topics": completed_topics,
                "total_topics": total_topics,
            })

        weekly = []
        for days_ago in range(13, -1, -1):
            day = today - timedelta(days=days_ago)
            day_answers = answers.filter(created_at__date=day)
            day_total = day_answers.count()
            day_correct = day_answers.filter(is_correct=True).count()
            weekly.append({
                "day": day.strftime("%d %b"),
                "solved": day_answers.filter(is_correct=True).values("question_id").distinct().count(),
                "accuracy": percentage(day_correct, day_total),
            })

        test_history = [
            {
                "test": attempt.test.name,
                "score": percentage(attempt.score, attempt.total_questions),
                "raw": f"{attempt.score}/{attempt.total_questions}",
                "completed_at": attempt.completed_at.isoformat(),
            }
            for attempt in attempts.select_related("test").order_by("-completed_at")[:8]
        ]

        weak_topics = [
            item for item in topic_payload
            if item["attempts"] > 0 and item["accuracy"] < 60
        ][:6]

        return Response({
            "summary": {
                "overall_accuracy": percentage(correct_answers, total_answers),
                "attempts": total_answers,
                "correct": correct_answers,
                "tests_taken": attempts.count(),
                "topics_practiced": answers.values("question__topic_id").distinct().count(),
            },
            "topic_accuracy": topic_payload,
            "track_progress": track_payload,
            "weekly_momentum": weekly,
            "test_history": test_history,
            "weak_topics": weak_topics,
            "insights": [
                "Prioritize weak topics below 60% before the next mock test.",
                "Maintain a daily mix of aptitude, DSA, SQL, and communication practice.",
                "Company readiness improves fastest when profile, projects, and role-specific drills are aligned.",
            ],
        })


class CompaniesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        targets = CompanyTarget.objects.filter(user=request.user, is_active=True).order_by("order", "name")

        companies = []
        for target in targets:
            catalog = company_catalog_for(target.name)
            companies.append({
                "name": target.name,
                "full_name": catalog["full_name"],
                "readiness": bounded_percentage(target.readiness_percentage),
                "focus": target.focus,
                "tone": target.tone,
                "roles": catalog["roles"],
                "campus_focus": catalog["campus_focus"],
                "eligibility_notes": catalog["eligibility_notes"],
                "prep_focus": catalog["prep_focus"],
                "official_url": catalog["official_url"],
                "source_label": catalog["source_label"],
                "source_note": catalog["source_note"],
                "salary_note": catalog["salary_note"],
                "hiring_signal": catalog["hiring_signal"],
            })

        average = round(sum(company["readiness"] for company in companies) / len(companies)) if companies else 0
        current_target = max(companies, key=lambda company: company["readiness"], default=None)

        return Response({
            "summary": {
                "target_count": len(companies),
                "average_readiness": average,
                "current_target": current_target,
                "source_count": len([company for company in companies if company["official_url"]]),
            },
            "companies": companies,
            "checklist": [
                "Verify official career portal before applying.",
                "Match resume projects to the target role.",
                "Practice the company-specific focus areas this week.",
                "Keep academic, backlog, and document details consistent.",
            ],
            "sources": [
                {
                    "company": catalog["name"],
                    "label": catalog["source_label"],
                    "url": catalog["official_url"],
                }
                for catalog in COMPANY_CATALOG.values()
            ],
        })


class CompanyTargetUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, company_name):
        ensure_user_preparation_data(request.user)
        target, _ = CompanyTarget.objects.get_or_create(
            user=request.user,
            name=company_name,
            defaults={
                "readiness_percentage": 0,
                "focus": "Research official role requirements",
                "tone": "slate",
                "order": CompanyTarget.objects.filter(user=request.user).count() + 1,
                "is_active": True,
            },
        )

        if "readiness" in request.data:
            target.readiness_percentage = bounded_percentage(request.data.get("readiness"))
            target.tone = "green" if target.readiness_percentage >= 70 else "amber" if target.readiness_percentage >= 50 else "red"
        if "focus" in request.data:
            target.focus = str(request.data.get("focus", ""))[:180]
        if "is_active" in request.data:
            target.is_active = bool(request.data.get("is_active"))
        target.save()

        return Response({
            "message": "Company target updated",
            "name": target.name,
            "readiness": target.readiness_percentage,
            "focus": target.focus,
            "tone": target.tone,
            "is_active": target.is_active,
        })


class AdminOverviewView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        ensure_platform_catalog()
        now = timezone.now()
        users = User.objects.all().order_by("-created_at")
        user_count = users.count()

        profile_lookup = {
            profile.user_id: profile
            for profile in UserProfile.objects.filter(user__in=users)
        }

        user_payload = []
        for user in users:
            profile = profile_lookup.get(user.id)
            completed_topics = UserTopicProgress.objects.filter(user=user, is_completed=True).count()
            answer_count = UserAnswer.objects.filter(user=user).count()
            company_count = CompanyTarget.objects.filter(user=user, is_active=True).count()
            profile_bits = []
            if profile and profile.branch:
                profile_bits.append(profile.branch)
            if profile and profile.preferred_role:
                profile_bits.append(profile.preferred_role)

            name_source = user.name or user.email
            user_payload.append({
                "id": user.id,
                "name": user.name or "Unnamed user",
                "email": user.email,
                "initials": "".join(part[0] for part in name_source.replace("@", " ").replace(".", " ").split()[:2]).upper() or "U",
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "profile_summary": " / ".join(profile_bits) if profile_bits else "Profile pending",
                "stats": {
                    "completed_topics": completed_topics,
                    "answers": answer_count,
                    "company_targets": company_count,
                },
            })

        track_payload = []
        for track in Track.objects.all().order_by("name"):
            topics = track.topics.filter(is_active=True)
            topic_count = topics.count()
            question_count = Question.objects.filter(topic__track=track).count()
            completion_total = topic_count * user_count
            completed_total = UserTopicProgress.objects.filter(topic__track=track, is_completed=True).count()
            track_payload.append({
                "id": track.id,
                "name": track.name,
                "description": track.description,
                "topic_count": topic_count,
                "question_count": question_count,
                "completion_rate": percentage(completed_total, completion_total),
                "topics": [
                    {
                        "id": topic.id,
                        "name": topic.name,
                        "description": topic.description,
                        "order": topic.order,
                        "is_active": topic.is_active,
                        "question_count": topic.questions.count(),
                    }
                    for topic in track.topics.all().order_by("order", "name")
                ],
            })

        activity_payload = [
            {
                "type": event.event_type,
                "title": event.title,
                "user": event.user.name or event.user.email,
                "time": admin_relative_time(event.occurred_at, now),
            }
            for event in ActivityEvent.objects.select_related("user").order_by("-occurred_at", "-id")[:8]
        ]

        company_target_payload = [
            {
                "id": target.id,
                "user_id": target.user_id,
                "user": target.user.name or target.user.email,
                "email": target.user.email,
                "name": target.name,
                "readiness": bounded_percentage(target.readiness_percentage),
                "focus": target.focus,
                "tone": target.tone,
                "is_active": target.is_active,
            }
            for target in CompanyTarget.objects.select_related("user").order_by("user__email", "order", "name")
        ]

        return Response({
            "summary": {
                "users": user_count,
                "active_users": users.filter(is_active=True).count(),
                "admins": users.filter(is_staff=True).count(),
                "tracks": Track.objects.count(),
                "topics": Topic.objects.filter(is_active=True).count(),
                "questions": Question.objects.count(),
                "daily_plan_items": DailyPlanItem.objects.count(),
                "company_targets": CompanyTarget.objects.filter(is_active=True).count(),
                "events": ActivityEvent.objects.count(),
            },
            "users": user_payload,
            "tracks": track_payload,
            "company_targets": company_target_payload,
            "activity": activity_payload,
        })


class AdminUserUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_superuser and user.id != request.user.id:
            return Response({"error": "Super admin accounts can only be edited directly in Django admin."}, status=status.HTTP_400_BAD_REQUEST)

        changed_fields = []
        if "is_staff" in request.data and not user.is_superuser:
            user.is_staff = bool(request.data.get("is_staff"))
            changed_fields.append("is_staff")
        if "is_active" in request.data and not user.is_superuser:
            user.is_active = bool(request.data.get("is_active"))
            changed_fields.append("is_active")
        if "name" in request.data:
            user.name = str(request.data.get("name", "")).strip()[:255] or user.name
            changed_fields.append("name")

        if changed_fields:
            user.save(update_fields=sorted(set(changed_fields)))

        return Response({
            "message": "User updated",
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        })


class AdminContentView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        item_type = request.data.get("type")

        if item_type == "track":
            name = str(request.data.get("name", "")).strip()
            description = str(request.data.get("description", "")).strip()
            if not name:
                return Response({"error": "Track name is required."}, status=status.HTTP_400_BAD_REQUEST)

            track, created = Track.objects.get_or_create(name=name, defaults={"description": description})
            if not created and description:
                track.description = description
                track.save(update_fields=["description"])

            return Response({
                "message": "Track created" if created else "Track updated",
                "id": track.id,
                "name": track.name,
                "description": track.description,
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        if item_type == "topic":
            try:
                track = Track.objects.get(id=request.data.get("track_id"))
            except (Track.DoesNotExist, ValueError, TypeError):
                return Response({"error": "Valid track_id is required."}, status=status.HTTP_400_BAD_REQUEST)

            name = str(request.data.get("name", "")).strip()
            description = str(request.data.get("description", "")).strip()
            if not name:
                return Response({"error": "Topic name is required."}, status=status.HTTP_400_BAD_REQUEST)

            topic = Topic.objects.create(
                track=track,
                name=name,
                description=description,
                order=int(request.data.get("order") or track.topics.count() + 1),
                is_active=True,
            )

            return Response({
                "message": "Topic created",
                "id": topic.id,
                "name": topic.name,
                "track_id": track.id,
            }, status=status.HTTP_201_CREATED)

        return Response({"error": "type must be either track or topic."}, status=status.HTTP_400_BAD_REQUEST)


class AdminTrackDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, track_id):
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            return Response({"error": "Track not found"}, status=status.HTTP_404_NOT_FOUND)

        changed_fields = []
        if "name" in request.data:
            name = str(request.data.get("name", "")).strip()
            if not name:
                return Response({"error": "Track name cannot be blank."}, status=status.HTTP_400_BAD_REQUEST)
            track.name = name
            changed_fields.append("name")
        if "description" in request.data:
            track.description = str(request.data.get("description", "")).strip()
            changed_fields.append("description")
        if changed_fields:
            track.save(update_fields=sorted(set(changed_fields)))

        return Response({"message": "Track updated", "id": track.id, "name": track.name, "description": track.description})

    def delete(self, request, track_id):
        try:
            track = Track.objects.get(id=track_id)
        except Track.DoesNotExist:
            return Response({"error": "Track not found"}, status=status.HTTP_404_NOT_FOUND)

        if track.topics.exists():
            return Response({"error": "Delete or move this track's topics before deleting the track."}, status=status.HTTP_400_BAD_REQUEST)

        track.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminTopicDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, topic_id):
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

        changed_fields = []
        if "name" in request.data:
            name = str(request.data.get("name", "")).strip()
            if not name:
                return Response({"error": "Topic name cannot be blank."}, status=status.HTTP_400_BAD_REQUEST)
            topic.name = name
            changed_fields.append("name")
        if "description" in request.data:
            topic.description = str(request.data.get("description", "")).strip()
            changed_fields.append("description")
        if "order" in request.data:
            topic.order = int(request.data.get("order") or 0)
            changed_fields.append("order")
        if "is_active" in request.data:
            topic.is_active = bool(request.data.get("is_active"))
            changed_fields.append("is_active")
        if "track_id" in request.data:
            try:
                topic.track = Track.objects.get(id=request.data.get("track_id"))
            except (Track.DoesNotExist, ValueError, TypeError):
                return Response({"error": "Valid track_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            changed_fields.append("track")
        if changed_fields:
            topic.save(update_fields=sorted(set(changed_fields)))

        return Response({"message": "Topic updated", "id": topic.id, "name": topic.name, "is_active": topic.is_active})

    def delete(self, request, topic_id):
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

        has_student_history = UserAnswer.objects.filter(question__topic=topic).exists() or UserTopicProgress.objects.filter(topic=topic).exists()
        if has_student_history:
            topic.is_active = False
            topic.save(update_fields=["is_active"])
            return Response({"message": "Topic archived because student history exists.", "id": topic.id, "is_active": False})

        topic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminCompanyTargetView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            user = User.objects.get(id=request.data.get("user_id"))
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Valid user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        name = str(request.data.get("name", "")).strip()
        if not name:
            return Response({"error": "Company name is required."}, status=status.HTTP_400_BAD_REQUEST)

        target, created = CompanyTarget.objects.get_or_create(
            user=user,
            name=name,
            defaults={
                "readiness_percentage": bounded_percentage(request.data.get("readiness", 0)),
                "focus": str(request.data.get("focus", "")).strip()[:180],
                "tone": "slate",
                "order": CompanyTarget.objects.filter(user=user).count() + 1,
                "is_active": True,
            },
        )

        if not created:
            target.is_active = True
            target.readiness_percentage = bounded_percentage(request.data.get("readiness", target.readiness_percentage))
            target.focus = str(request.data.get("focus", target.focus)).strip()[:180]

        target.tone = "green" if target.readiness_percentage >= 70 else "amber" if target.readiness_percentage >= 50 else "red"
        target.save()

        return Response({"message": "Company target created" if created else "Company target restored", "id": target.id}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class AdminCompanyTargetDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, target_id):
        try:
            target = CompanyTarget.objects.get(id=target_id)
        except CompanyTarget.DoesNotExist:
            return Response({"error": "Company target not found"}, status=status.HTTP_404_NOT_FOUND)

        if "readiness" in request.data:
            target.readiness_percentage = bounded_percentage(request.data.get("readiness"))
            target.tone = "green" if target.readiness_percentage >= 70 else "amber" if target.readiness_percentage >= 50 else "red"
        if "focus" in request.data:
            target.focus = str(request.data.get("focus", "")).strip()[:180]
        if "is_active" in request.data:
            target.is_active = bool(request.data.get("is_active"))
        target.save()

        return Response({"message": "Company target updated", "id": target.id})

    def delete(self, request, target_id):
        try:
            target = CompanyTarget.objects.get(id=target_id)
        except CompanyTarget.DoesNotExist:
            return Response({"error": "Company target not found"}, status=status.HTTP_404_NOT_FOUND)

        target.is_active = False
        target.save(update_fields=["is_active"])
        return Response({"message": "Company target archived", "id": target.id, "is_active": False})
    
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class AIExplanationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        question_id = request.data.get("question_id")

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)

        prompt = f"""
        Question: {question.question_text}
        Options:
        A: {question.option_a}
        B: {question.option_b}
        C: {question.option_c}
        D: {question.option_d}

        Correct Answer: {question.correct_answer}

        Explain why the correct answer is right in simple terms.
        """

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama-3.1-8b-instant",   # ✅ updated
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        print("AI RESPONSE:", result)

        # ✅ SAFE extraction
        if "choices" in result:
            explanation = result["choices"][0]["message"]["content"]
        else:
            explanation = result.get("error", {}).get("message", "AI failed")

        return Response({
            "explanation": explanation
        })
    
