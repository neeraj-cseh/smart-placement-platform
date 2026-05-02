import logging
import os
import subprocess
import sys
import tempfile
import time
import requests
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

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
    CodeSubmission,
    InterviewSession,
    InterviewQA,
)
from .serializers import TrackSerializer, TopicSerializer, QuestionSerializer, TestSerializer, TestSummarySerializer, CodeSubmissionSerializer, InterviewSessionSerializer
from .bootstrap import COMPANY_CATALOG, ensure_platform_catalog, ensure_user_preparation_data

logger = logging.getLogger(__name__)


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


def difficulty_mix_for_questions(questions):
    mix = {"easy": 0, "medium": 0, "hard": 0}
    for question in questions:
        mix[question.difficulty] = mix.get(question.difficulty, 0) + 1
    return mix


def test_sections_for(test):
    sections = []
    for topic in test.topics.all().order_by("track__name", "order", "name"):
        sections.append({
            "id": topic.id,
            "name": topic.name,
            "track": topic.track.name if topic.track else "General",
            "question_count": test.questions.filter(topic=topic).count(),
        })
    return sections


def test_payload(test, latest_attempt=None, best_attempt=None, attempt_count=0):
    questions = list(test.questions.select_related("topic", "topic__track").all())
    total_questions = len(questions)
    duration = max(1, test.duration_minutes or 1)
    return {
        "id": test.id,
        "name": test.name,
        "description": test.description,
        "duration_minutes": duration,
        "question_count": total_questions,
        "topic_count": test.topics.count(),
        "sections": test_sections_for(test),
        "difficulty_mix": difficulty_mix_for_questions(questions),
        "marks_per_question": 1,
        "total_marks": total_questions,
        "passing_score": 60,
        "pace_seconds_per_question": round((duration * 60) / total_questions) if total_questions else 0,
        "last_score": percentage(latest_attempt.score, latest_attempt.total_questions) if latest_attempt else None,
        "best_score": percentage(best_attempt.score, best_attempt.total_questions) if best_attempt else None,
        "last_completed_at": latest_attempt.completed_at.isoformat() if latest_attempt and latest_attempt.completed_at else None,
        "attempt_count": attempt_count,
        "instructions": [
            "Answer every question before the timer ends.",
            "Use the question palette to revisit unanswered or marked questions.",
            "The test auto-submits when the timer reaches zero.",
        ],
    }


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


def topic_accuracy_for_user(user, topic_id, answer_stats):
    stats = answer_stats.get(topic_id, {"total": 0, "correct": 0})
    return {
        "attempts": stats["total"],
        "correct": stats["correct"],
        "accuracy": percentage(stats["correct"], stats["total"]),
    }


class HealthView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({
            "status": "healthy",
            "version": "1.0.0",
            "debug": os.getenv("DEBUG", "False") == "True",
        })


class LandingView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ensure_platform_catalog()
        track_count = Track.objects.filter(topics__is_active=True).distinct().count()
        topic_count = Topic.objects.filter(is_active=True).count()
        question_count = Question.objects.count()
        test_count = Test.objects.count()

        return Response({
            "brand": {
                "name": "PrepSmart",
                "initials": "PS",
            },
            "hero": {
                "title": "PrepSmart",
                "eyebrow": "Placement readiness platform",
                "subtitle": "A backend-driven preparation workspace for learning paths, mock tests, coding practice, interview drills, analytics, and company readiness.",
                "primary_action": {"label": "Start preparing", "href": "/signup"},
                "secondary_action": {"label": "Sign in", "href": "/login"},
            },
            "metrics": [
                {"label": "Learning tracks", "value": track_count},
                {"label": "Active topics", "value": topic_count},
                {"label": "Practice questions", "value": question_count},
                {"label": "Mock tests", "value": test_count},
            ],
            "features": [
                {"id": "learning", "title": "Structured learning", "description": "Track-by-track preparation with topic progress, checkpoints, and focus queues."},
                {"id": "tests", "title": "Realistic mock tests", "description": "Timed tests with sections, question palettes, auto-submit, and score history."},
                {"id": "code", "title": "Code execution", "description": "Run Python code with stdin, output, errors, execution time, and saved submissions."},
                {"id": "analytics", "title": "Progress analytics", "description": "Backend-calculated accuracy, weak topics, weekly momentum, and test history."},
                {"id": "companies", "title": "Company readiness", "description": "Target company roles, official portals, eligibility notes, and readiness tracking."},
                {"id": "admin", "title": "Admin management", "description": "Manage tracks, topics, questions, tests, users, and company targets from one console."},
            ],
            "feature_heading": "Platform modules",
            "workflow": [
                {"step": "1", "title": "Set your profile", "description": "Add academic and role details so preparation data is personalized."},
                {"step": "2", "title": "Follow the path", "description": "Complete topics and practice questions from backend-managed content."},
                {"step": "3", "title": "Take mocks", "description": "Use timed tests and analytics to close weak areas before interviews."},
            ],
        })


class TrackListView(APIView):
    permission_classes = []

    def get(self, request):
        ensure_platform_catalog()
        tracks = Track.objects.all().order_by('name')
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

        completed_topic_ids = set(
            UserTopicProgress.objects.filter(
                user=request.user,
                is_completed=True
            ).values_list('topic_id', flat=True)
        )

        response_data = []
        for topic in topics:
            response_data.append({
                "id": topic.id,
                "name": topic.name,
                "description": topic.description,
                "order": topic.order,
                "is_completed": topic.id in completed_topic_ids
            })

        return Response(response_data)


class CompleteTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topic_id):
        ensure_user_preparation_data(request.user)
        try:
            topic = Topic.objects.get(id=topic_id, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

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
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

        raw_value = request.data.get("is_completed")
        if isinstance(raw_value, bool):
            is_completed = raw_value
        elif isinstance(raw_value, str) and raw_value.lower() in ["true", "false", "1", "0", "yes", "no"]:
            is_completed = raw_value.lower() in ["true", "1", "yes"]
        else:
            return Response({"error": "is_completed must be a boolean."}, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = [IsAuthenticated]

    def get(self, request, topic_id):
        ensure_platform_catalog()
        questions = Question.objects.filter(topic_id=topic_id).order_by('difficulty', 'id')
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        ensure_user_preparation_data(request.user)
        user_answer = request.data.get("answer")

        if not user_answer or user_answer.upper() not in ["A", "B", "C", "D"]:
            return Response({"error": "Answer must be one of A, B, C, or D."}, status=status.HTTP_400_BAD_REQUEST)

        user_answer = user_answer.upper()

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        is_correct = (user_answer == question.correct_answer)

        UserAnswer.objects.create(
            user=request.user,
            question=question,
            selected_answer=user_answer,
            is_correct=is_correct
        )

        return Response({
            "correct": is_correct,
            "correct_answer": question.correct_answer,
        })


class WeakTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)

        answer_stats = {}
        for row in UserAnswer.objects.filter(user=request.user).values("question__topic_id").annotate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        ):
            answer_stats[row["question__topic_id"]] = {
                "total": row["total"],
                "correct": row["correct"],
            }

        weak_topics = []
        for topic_id, stats in answer_stats.items():
            if stats["total"] == 0:
                continue
            accuracy = percentage(stats["correct"], stats["total"])
            if accuracy < 50:
                try:
                    topic = Topic.objects.get(id=topic_id)
                    weak_topics.append({
                        "id": topic.id,
                        "topic": topic.name,
                        "track": topic.track.name if topic.track else "General",
                        "accuracy": round(accuracy, 2),
                    })
                except Topic.DoesNotExist:
                    continue

        weak_topics.sort(key=lambda x: x["accuracy"])
        return Response(weak_topics)


class TestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        tests = Test.objects.prefetch_related("topics", "questions").all().order_by('name')

        latest_attempts = {}
        best_attempts = {}
        attempt_counts = {}
        for attempt in TestAttempt.objects.filter(
            user=request.user,
            completed_at__isnull=False,
            total_questions__gt=0,
        ).select_related("test").order_by("test_id", "-completed_at"):
            attempt_counts[attempt.test_id] = attempt_counts.get(attempt.test_id, 0) + 1
            latest_attempts.setdefault(attempt.test_id, attempt)
            current_best = best_attempts.get(attempt.test_id)
            if not current_best or percentage(attempt.score, attempt.total_questions) > percentage(current_best.score, current_best.total_questions):
                best_attempts[attempt.test_id] = attempt

        payload = [
            test_payload(
                test,
                latest_attempt=latest_attempts.get(test.id),
                best_attempt=best_attempts.get(test.id),
                attempt_count=attempt_counts.get(test.id, 0),
            )
            for test in tests
        ]

        return Response({
            "summary": {
                "test_count": len(payload),
                "total_questions": sum(item["question_count"] for item in payload),
                "completed_attempts": sum(item["attempt_count"] for item in payload),
                "average_duration": round(sum(item["duration_minutes"] for item in payload) / len(payload)) if payload else 0,
            },
            "tests": payload,
        })


class TestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id):
        ensure_platform_catalog()
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TestSerializer(test)
        data = serializer.data
        data.update(test_payload(test))
        return Response(data)


class StartTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):
        ensure_user_preparation_data(request.user)
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

        attempt = TestAttempt.objects.create(
            user=request.user,
            test=test,
            total_questions=test.questions.count()
        )

        return Response({
            "message": "Test started",
            "attempt_id": attempt.id,
            "total_questions": attempt.total_questions,
            "duration_minutes": test.duration_minutes,
            "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
            "expires_at": (attempt.started_at + timedelta(minutes=test.duration_minutes)).isoformat() if attempt.started_at else None,
        })


class SubmitTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        attempt_id = request.data.get("attempt_id")
        answers = request.data.get("answers", {})

        try:
            attempt = TestAttempt.objects.get(id=attempt_id, user=request.user)
        except TestAttempt.DoesNotExist:
            return Response({"error": "Invalid attempt"}, status=status.HTTP_404_NOT_FOUND)

        if attempt.completed_at:
            return Response({"error": "Test already submitted"}, status=status.HTTP_400_BAD_REQUEST)

        questions = list(attempt.test.questions.select_related("topic").all())
        question_ids = [question.id for question in questions]
        score = 0
        detailed_result = []

        for question in questions:
            user_ans = answers.get(str(question.id), answers.get(question.id, ""))
            if user_ans is None:
                user_ans = ""
            user_ans = str(user_ans).upper().strip()

            is_correct = (user_ans.upper() == question.correct_answer.upper())

            if is_correct:
                score += 1

            detailed_result.append({
                "question_id": question.id,
                "topic": question.topic.name if question.topic else "General",
                "question_text": question.question_text,
                "your_answer": user_ans,
                "correct_answer": question.correct_answer,
                "is_correct": is_correct,
                "is_unanswered": not bool(user_ans),
            })

        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save()

        ActivityEvent.objects.create(
            user=request.user,
            event_type="Mock",
            title=f"Completed {attempt.test.name} with {percentage(score, attempt.total_questions)}%",
            occurred_at=timezone.now(),
            metadata={"test_id": attempt.test.id, "score": score, "total": attempt.total_questions},
        )

        return Response({
            "score": score,
            "total": attempt.total_questions,
            "percentage": percentage(score, attempt.total_questions),
            "correct": score,
            "incorrect": len([result for result in detailed_result if result["your_answer"] and not result["is_correct"]]),
            "unanswered": len([result for result in detailed_result if result["is_unanswered"]]),
            "submitted_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            "results": detailed_result,
        })


class TopicAccuracyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)

        answer_stats = {}
        for row in UserAnswer.objects.filter(user=request.user).values("question__topic_id").annotate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        ):
            answer_stats[row["question__topic_id"]] = {
                "total": row["total"],
                "correct": row["correct"],
            }

        topic_data = []
        for topic in Topic.objects.filter(is_active=True).select_related("track"):
            stats = answer_stats.get(topic.id, {"total": 0, "correct": 0})
            if stats["total"] == 0:
                continue

            accuracy = percentage(stats["correct"], stats["total"])
            topic_data.append({
                "id": topic.id,
                "topic": topic.name,
                "track": topic.track.name if topic.track else "General",
                "accuracy": round(accuracy, 2),
                "attempts": stats["total"],
                "correct": stats["correct"],
            })

        topic_data.sort(key=lambda x: x["accuracy"])
        return Response(topic_data)


class OverallPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)

        stats = UserAnswer.objects.filter(user=request.user).aggregate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        )

        total = stats["total"] or 0
        correct = stats["correct"] or 0
        accuracy = percentage(correct, total)

        return Response({
            "total_attempts": total,
            "correct_answers": correct,
            "accuracy": round(accuracy, 2),
        })


class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)

        stats = UserAnswer.objects.filter(user=request.user).aggregate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        )
        overall_accuracy = percentage(stats["correct"] or 0, stats["total"] or 0)

        answer_stats = {}
        for row in UserAnswer.objects.filter(user=request.user).values("question__topic_id").annotate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        ):
            answer_stats[row["question__topic_id"]] = {
                "total": row["total"],
                "correct": row["correct"],
            }

        topic_data = []
        weak_topics = []
        for topic in Topic.objects.filter(is_active=True).select_related("track"):
            stats_t = answer_stats.get(topic.id, {"total": 0, "correct": 0})
            if stats_t["total"] == 0:
                continue

            accuracy = percentage(stats_t["correct"], stats_t["total"])
            entry = {
                "id": topic.id,
                "topic": topic.name,
                "track": topic.track.name if topic.track else "General",
                "accuracy": round(accuracy, 2),
            }
            topic_data.append(entry)

            if accuracy < 50:
                weak_topics.append(entry)

        return Response({
            "overall": {
                "total_attempts": stats["total"] or 0,
                "correct_answers": stats["correct"] or 0,
                "accuracy": round(overall_accuracy, 2),
            },
            "topics": topic_data,
            "weak_topics": weak_topics,
        })


class PracticeDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)

        answer_stats = {}
        for row in UserAnswer.objects.filter(user=request.user).values("question__topic_id").annotate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        ):
            answer_stats[row["question__topic_id"]] = {
                "total": row["total"],
                "correct": row["correct"],
            }

        question_totals = {
            row["topic_id"]: row["total"]
            for row in Question.objects.values("topic_id").annotate(total=Count("id"))
        }

        difficulty_counts = {}
        for row in Question.objects.values("topic_id", "difficulty").annotate(total=Count("id")):
            topic_mix = difficulty_counts.setdefault(row["topic_id"], {"easy": 0, "medium": 0, "hard": 0})
            topic_mix[row["difficulty"]] = row["total"]

        topics = Topic.objects.filter(is_active=True).select_related("track").order_by("track__name", "order", "id")

        topic_cards = []
        weak_candidates = []
        total_questions = 0
        total_attempts = UserAnswer.objects.filter(user=request.user).count()
        correct_attempts = UserAnswer.objects.filter(user=request.user, is_correct=True).count()

        for topic in topics:
            stats = topic_accuracy_for_user(request.user, topic.id, answer_stats)
            question_count = question_totals.get(topic.id, 0)
            total_questions += question_count
            priority = "high" if stats["attempts"] and stats["accuracy"] < 55 else "medium" if stats["accuracy"] < 70 else "steady"
            card = {
                "id": topic.id,
                "name": topic.name,
                "track": topic.track.name if topic.track else "General",
                "description": topic.description,
                "question_count": question_count,
                "difficulty_mix": difficulty_counts.get(topic.id, {"easy": 0, "medium": 0, "hard": 0}),
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

        tests = Test.objects.all().order_by("name")
        test_attempts_lookup = {}
        for attempt in TestAttempt.objects.filter(
            user=request.user,
            completed_at__isnull=False,
        ).order_by("test_id", "-completed_at"):
            if attempt.test_id not in test_attempts_lookup:
                test_attempts_lookup[attempt.test_id] = attempt

        test_payload = []
        for test in tests:
            latest_attempt = test_attempts_lookup.get(test.id)
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
        })


class FullAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        today = timezone.localdate()
        answers = UserAnswer.objects.filter(user=request.user)
        attempts = TestAttempt.objects.filter(user=request.user, completed_at__isnull=False, total_questions__gt=0)

        answer_stats = {}
        for row in answers.values("question__topic_id").annotate(
            total=Count("id"),
            correct=Count("id", filter=Q(is_correct=True)),
        ):
            answer_stats[row["question__topic_id"]] = {
                "total": row["total"],
                "correct": row["correct"],
            }

        topics_qs = Topic.objects.filter(is_active=True).select_related("track").order_by("track__name", "order", "id")
        topic_payload = []
        for topic in topics_qs:
            stats = answer_stats.get(topic.id, {"total": 0, "correct": 0})
            topic_payload.append({
                "topic": topic.name,
                "track": topic.track.name if topic.track else "General",
                "accuracy": percentage(stats["correct"], stats["total"]),
                "attempts": stats["total"],
                "correct": stats["correct"],
                "tone": tone_for_progress(percentage(stats["correct"], stats["total"]) if stats["total"] else 0),
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

        total_answers = answers.count()
        correct_answers = answers.filter(is_correct=True).count()

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
            try:
                target.readiness_percentage = bounded_percentage(int(request.data.get("readiness", 0)))
            except (ValueError, TypeError):
                pass
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
        users = list(User.objects.all().order_by("-created_at")[:100])
        user_ids = [user.id for user in users]
        user_count = len(users)

        profile_lookup = {
            profile.user_id: profile
            for profile in UserProfile.objects.filter(user_id__in=user_ids)
        }

        answer_counts = {}
        for row in UserAnswer.objects.values("user_id").annotate(total=Count("id")):
            answer_counts[row["user_id"]] = row["total"]

        topic_counts = {}
        for row in UserTopicProgress.objects.filter(is_completed=True).values("user_id").annotate(total=Count("id")):
            topic_counts[row["user_id"]] = row["total"]

        company_counts = {}
        for row in CompanyTarget.objects.filter(is_active=True).values("user_id").annotate(total=Count("id")):
            company_counts[row["user_id"]] = row["total"]

        user_payload = []
        for user in users:
            profile = profile_lookup.get(user.id)
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
                    "completed_topics": topic_counts.get(user.id, 0),
                    "answers": answer_counts.get(user.id, 0),
                    "company_targets": company_counts.get(user.id, 0),
                },
            })

        tracks_qs = Track.objects.all().order_by("name")
        track_question_counts = {}
        for row in Question.objects.values("topic__track_id").annotate(total=Count("id")):
            track_question_counts[row["topic__track_id"]] = row["total"]

        track_completion_counts = {}
        for row in UserTopicProgress.objects.filter(is_completed=True).values("topic__track_id").annotate(total=Count("id")):
            track_completion_counts[row["topic__track_id"]] = row["total"]

        topic_question_counts = {}
        for row in Question.objects.values("topic_id").annotate(total=Count("id")):
            topic_question_counts[row["topic_id"]] = row["total"]

        track_payload = []
        for track in tracks_qs:
            topics = track.topics.filter(is_active=True)
            topic_count = topics.count()
            question_count = track_question_counts.get(track.id, 0)
            completion_total = topic_count * user_count
            completed_total = track_completion_counts.get(track.id, 0)

            topics_data = []
            for topic in topics.order_by("order", "name"):
                topics_data.append({
                    "id": topic.id,
                    "name": topic.name,
                    "description": topic.description,
                    "order": topic.order,
                    "is_active": topic.is_active,
                    "question_count": topic_question_counts.get(topic.id, 0),
                })

            track_payload.append({
                "id": track.id,
                "name": track.name,
                "description": track.description,
                "topic_count": topic_count,
                "question_count": question_count,
                "completion_rate": percentage(completed_total, completion_total),
                "topics": topics_data,
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
            for target in CompanyTarget.objects.select_related("user").order_by("user__email", "order", "name")[:100]
        ]

        question_payload = [
            {
                "id": question.id,
                "topic_id": question.topic_id,
                "topic": question.topic.name if question.topic else "General",
                "track": question.topic.track.name if question.topic and question.topic.track else "General",
                "question_text": question.question_text,
                "difficulty": question.difficulty,
                "correct_answer": question.correct_answer,
            }
            for question in Question.objects.select_related("topic", "topic__track").order_by("-created_at", "-id")[:120]
        ]

        tests_qs = Test.objects.prefetch_related("topics", "questions").all().order_by("name")
        tests_payload = [test_payload(test) for test in tests_qs]

        return Response({
            "summary": {
                "users": User.objects.count(),
                "active_users": User.objects.filter(is_active=True).count(),
                "admins": User.objects.filter(is_staff=True).count(),
                "tracks": Track.objects.count(),
                "topics": Topic.objects.filter(is_active=True).count(),
                "questions": Question.objects.count(),
                "daily_plan_items": DailyPlanItem.objects.count(),
                "company_targets": CompanyTarget.objects.filter(is_active=True).count(),
                "events": ActivityEvent.objects.count(),
            },
            "users": user_payload,
            "tracks": track_payload,
            "questions": question_payload,
            "tests": tests_payload,
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

        if item_type == "question":
            try:
                topic = Topic.objects.get(id=request.data.get("topic_id"))
            except (Topic.DoesNotExist, ValueError, TypeError):
                return Response({"error": "Valid topic_id is required."}, status=status.HTTP_400_BAD_REQUEST)

            question_text = str(request.data.get("question_text", "")).strip()
            options = {
                "option_a": str(request.data.get("option_a", "")).strip(),
                "option_b": str(request.data.get("option_b", "")).strip(),
                "option_c": str(request.data.get("option_c", "")).strip(),
                "option_d": str(request.data.get("option_d", "")).strip(),
            }
            correct_answer = str(request.data.get("correct_answer", "")).strip().upper()
            difficulty = str(request.data.get("difficulty", "medium")).strip().lower()

            if not question_text or not all(options.values()):
                return Response({"error": "Question text and all four options are required."}, status=status.HTTP_400_BAD_REQUEST)
            if correct_answer not in ["A", "B", "C", "D"]:
                return Response({"error": "correct_answer must be A, B, C, or D."}, status=status.HTTP_400_BAD_REQUEST)
            if difficulty not in ["easy", "medium", "hard"]:
                return Response({"error": "difficulty must be easy, medium, or hard."}, status=status.HTTP_400_BAD_REQUEST)

            question = Question.objects.create(
                topic=topic,
                question_text=question_text,
                correct_answer=correct_answer,
                difficulty=difficulty,
                **options,
            )

            return Response({
                "message": "Question created",
                "id": question.id,
                "topic_id": topic.id,
            }, status=status.HTTP_201_CREATED)

        if item_type == "test":
            name = str(request.data.get("name", "")).strip()
            description = str(request.data.get("description", "")).strip()
            if not name:
                return Response({"error": "Test name is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                duration_minutes = max(1, int(request.data.get("duration_minutes") or 30))
            except (ValueError, TypeError):
                duration_minutes = 30

            test, created = Test.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "duration_minutes": duration_minutes,
                },
            )
            if not created:
                test.description = description or test.description
                test.duration_minutes = duration_minutes
                test.save(update_fields=["description", "duration_minutes"])

            topic_ids = request.data.get("topic_ids") or []
            question_ids = request.data.get("question_ids") or []
            topics = Topic.objects.filter(id__in=topic_ids, is_active=True)
            questions = Question.objects.filter(id__in=question_ids)
            if not questions.exists() and topics.exists():
                questions = Question.objects.filter(topic__in=topics).order_by("topic__order", "id")[:20]

            if topics.exists():
                test.topics.set(topics)
            if questions.exists():
                test.questions.set(questions)

            return Response({
                "message": "Test created" if created else "Test updated",
                "id": test.id,
                "name": test.name,
                "question_count": test.questions.count(),
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        return Response({"error": "type must be track, topic, question, or test."}, status=status.HTTP_400_BAD_REQUEST)


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
            try:
                topic.order = int(request.data.get("order") or 0)
                changed_fields.append("order")
            except (ValueError, TypeError):
                return Response({"error": "Order must be a number."}, status=status.HTTP_400_BAD_REQUEST)
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

        try:
            readiness = int(request.data.get("readiness", 0))
        except (ValueError, TypeError):
            readiness = 0

        target, created = CompanyTarget.objects.get_or_create(
            user=user,
            name=name,
            defaults={
                "readiness_percentage": bounded_percentage(readiness),
                "focus": str(request.data.get("focus", "")).strip()[:180],
                "tone": "slate",
                "order": CompanyTarget.objects.filter(user=user).count() + 1,
                "is_active": True,
            },
        )

        if not created:
            target.is_active = True
            try:
                target.readiness_percentage = bounded_percentage(int(request.data.get("readiness", target.readiness_percentage)))
            except (ValueError, TypeError):
                pass
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
            try:
                target.readiness_percentage = bounded_percentage(int(request.data.get("readiness", 0)))
            except (ValueError, TypeError):
                pass
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
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        if not GROQ_API_KEY:
            return Response({"error": "AI service is not configured."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

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
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.Timeout:
            return Response({"error": "AI request timed out. Try again later."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.RequestException as e:
            logger.error(f"AI request failed: {str(e)}")
            return Response({"error": "AI service unavailable. Try again later."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if "choices" in result and result["choices"]:
            explanation = result["choices"][0]["message"]["content"]
        else:
            explanation = result.get("error", {}).get("message", "AI failed to generate a response.")

        return Response({
            "explanation": explanation
        })


class CodeExecuteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        code = request.data.get("code", "")
        language = request.data.get("language", "python")
        stdin = request.data.get("stdin", "")

        if not code.strip():
            return Response({"error": "Code cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        if language != "python":
            return Response({"error": "Only Python is supported."}, status=status.HTTP_400_BAD_REQUEST)

        if len(code) > 20000:
            return Response({"error": "Code is too large for the browser runner."}, status=status.HTTP_400_BAD_REQUEST)

        started = time.perf_counter()
        try:
            with tempfile.TemporaryDirectory(prefix="prepsmart_code_") as tmp_dir:
                code_path = os.path.join(tmp_dir, "main.py")
                with open(code_path, "w", encoding="utf-8") as code_file:
                    code_file.write(code)

                completed = subprocess.run(
                    [sys.executable, code_path],
                    input=stdin or "",
                    capture_output=True,
                    text=True,
                    timeout=8,
                    cwd=tmp_dir,
                    check=False,
                )

            elapsed_ms = int((time.perf_counter() - started) * 1000)
            output = completed.stdout or ""
            error_output = completed.stderr or ""
            code_obj = CodeSubmission.objects.create(
                user=request.user,
                code=code,
                language="python",
                output=output,
                error_output=error_output,
                execution_time_ms=elapsed_ms,
                stdin=stdin,
            )

            return Response({
                "id": code_obj.id,
                "output": output,
                "error": error_output,
                "success": completed.returncode == 0,
                "exit_code": completed.returncode,
                "execution_time_ms": elapsed_ms,
            })
        except subprocess.TimeoutExpired:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            code_obj = CodeSubmission.objects.create(
                user=request.user,
                code=code,
                language="python",
                output="",
                error_output="Execution timed out after 8 seconds.",
                execution_time_ms=elapsed_ms,
                stdin=stdin,
            )
            return Response({
                "id": code_obj.id,
                "output": "",
                "error": code_obj.error_output,
                "success": False,
                "exit_code": None,
                "execution_time_ms": elapsed_ms,
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        except OSError as e:
            logger.error(f"Local code execution failed: {str(e)}")
            return Response({"error": "Code execution failed on the local runner."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class CodeWorkspaceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        submissions = CodeSubmission.objects.filter(user=request.user).order_by("-created_at")[:8]
        return Response({
            "language": "python",
            "runtime": f"Python {sys.version_info.major}.{sys.version_info.minor}",
            "timeout_seconds": 8,
            "starter_code": "import sys\n\ntext = sys.stdin.read().strip()\nprint(text if text else \"Ready to code\")\n",
            "default_stdin": "",
            "examples": [
                {
                    "title": "Read numbers and sum",
                    "stdin": "4\n10 20 30 40\n",
                    "code": "n = int(input())\nvalues = list(map(int, input().split()))\nprint(sum(values[:n]))\n",
                },
                {
                    "title": "Two pointer reverse",
                    "stdin": "placement\n",
                    "code": "s = input().strip()\nprint(s[::-1])\n",
                },
                {
                    "title": "Frequency map",
                    "stdin": "a b a c b a\n",
                    "code": "from collections import Counter\nwords = input().split()\nprint(dict(Counter(words)))\n",
                },
            ],
            "recent_submissions": CodeSubmissionSerializer(submissions, many=True).data,
        })


class CodeSubmissionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        submissions = CodeSubmission.objects.filter(user=request.user).order_by("-created_at")[:20]
        serializer = CodeSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


INTERVIEW_QUESTIONS = {
    "general": [
        {"question": "Tell me about yourself and what motivated you to pursue a career in technology?", "area": "Introduction"},
        {"question": "Describe a project you built that you're most proud of. What was your role and what impact did it have?", "area": "Project"},
        {"question": "How do you approach debugging a problem you've never seen before?", "area": "Problem Solving"},
        {"question": "What is your greatest strength as a developer and how has it helped you in your projects?", "area": "Self Awareness"},
        {"question": "Where do you see yourself in 3 years and how does this role fit into your career plan?", "area": "Career Goals"},
    ],
    "technical": [
        {"question": "Explain the difference between a process and a thread in simple terms.", "area": "OS Concepts"},
        {"question": "What is the difference between SQL and NoSQL databases? When would you choose one over the other?", "area": "Database"},
        {"question": "Describe how HTTP works. What happens when you type a URL in your browser?", "area": "Networking"},
        {"question": "What is the difference between authentication and authorization? How does JWT work?", "area": "Security"},
        {"question": "Explain RESTful API design principles. What makes a good API?", "area": "API Design"},
    ],
    "dsa": [
        {"question": "How would you explain time complexity to someone who has never studied computer science?", "area": "Complexity"},
        {"question": "When would you use a hash map over an array? Give a practical example.", "area": "Data Structures"},
        {"question": "Describe a situation where recursion is the best approach and explain how it works.", "area": "Recursion"},
        {"question": "How do you decide between BFS and DFS for graph traversal?", "area": "Graphs"},
        {"question": "What is dynamic programming and when should you use it?", "area": "Dynamic Programming"},
    ],
}


class InterviewConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        labels = {
            "general": ("General", "Introduction, projects, career goals"),
            "technical": ("Technical", "OS, DBMS, networking, APIs"),
            "dsa": ("DSA", "Data structures, algorithms, complexity"),
        }
        return Response({
            "categories": [
                {
                    "id": key,
                    "label": labels.get(key, (key.title(), ""))[0],
                    "description": labels.get(key, (key.title(), ""))[1],
                    "question_count": len(questions),
                }
                for key, questions in INTERVIEW_QUESTIONS.items()
            ]
        })


class InterviewStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        category = request.data.get("category", "general")

        if category not in INTERVIEW_QUESTIONS:
            return Response({"error": f"Category must be one of: {', '.join(INTERVIEW_QUESTIONS.keys())}"}, status=status.HTTP_400_BAD_REQUEST)

        session = InterviewSession.objects.create(
            user=request.user,
            category=category,
            total_questions=len(INTERVIEW_QUESTIONS[category]),
        )

        first_q = INTERVIEW_QUESTIONS[category][0]
        return Response({
            "session_id": session.id,
            "category": category,
            "total_questions": session.total_questions,
            "current_question": first_q,
            "question_index": 0,
        })


class InterviewNextQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        session_id = request.data.get("session_id")

        try:
            session = InterviewSession.objects.get(id=session_id, user=request.user, status='active')
        except InterviewSession.DoesNotExist:
            return Response({"error": "Active interview session not found"}, status=status.HTTP_404_NOT_FOUND)

        questions = INTERVIEW_QUESTIONS.get(session.category, [])
        next_idx = session.current_question_index + 1

        if next_idx >= len(questions):
            return Response({"error": "No more questions. Submit your answer or end the interview."}, status=status.HTTP_400_BAD_REQUEST)

        session.current_question_index = next_idx
        session.save()

        return Response({
            "current_question": questions[next_idx],
            "question_index": next_idx,
            "total_questions": session.total_questions,
        })


class InterviewSubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        session_id = request.data.get("session_id")
        answer = request.data.get("answer", "")

        if not answer.strip():
            return Response({"error": "Answer cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = InterviewSession.objects.get(id=session_id, user=request.user, status='active')
        except InterviewSession.DoesNotExist:
            return Response({"error": "Active interview session not found"}, status=status.HTTP_404_NOT_FOUND)

        questions = INTERVIEW_QUESTIONS.get(session.category, [])
        current_q = questions[session.current_question_index]

        qa_pair = InterviewQA.objects.create(
            session=session,
            question=current_q["question"],
            user_answer=answer,
            score=0,
            max_score=20,
        )

        if GROQ_API_KEY:
            try:
                ai_prompt = f"""Evaluate this interview answer. Give a score out of 20 and brief feedback.

Question: {current_q['question']}
Candidate's Answer: {answer}

Respond with JSON: {{"score": <number>, "feedback": "<brief feedback>"}}"""

                ai_response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": ai_prompt}],
                        "temperature": 0.5,
                    },
                    timeout=30,
                )
                ai_response.raise_for_status()
                result = ai_response.json()

                if "choices" in result and result["choices"]:
                    import json as json_mod
                    try:
                        ai_text = result["choices"][0]["message"]["content"]
                        parsed = json_mod.loads(ai_text)
                        qa_pair.score = min(20, max(0, int(parsed.get("score", 10))))
                        qa_pair.ai_feedback = parsed.get("feedback", "Good effort. Keep practicing.")
                        qa_pair.save()
                    except (json_mod.JSONDecodeError, ValueError, KeyError):
                        qa_pair.ai_feedback = "Answer recorded. AI feedback unavailable."
                        qa_pair.save()
            except Exception as e:
                logger.error(f"AI interview feedback failed: {str(e)}")
                qa_pair.ai_feedback = "Answer recorded. AI feedback unavailable due to service issue."
                qa_pair.save()

        session.score += qa_pair.score
        session.save()

        return Response({
            "message": "Answer submitted",
            "score": qa_pair.score,
            "max_score": qa_pair.max_score,
            "feedback": qa_pair.ai_feedback,
            "total_score": session.score,
        })


class InterviewEndView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        session_id = request.data.get("session_id")

        try:
            session = InterviewSession.objects.get(id=session_id, user=request.user, status='active')
        except InterviewSession.DoesNotExist:
            return Response({"error": "Active interview session not found"}, status=status.HTTP_404_NOT_FOUND)

        session.status = 'completed'
        session.completed_at = timezone.now()
        session.save()

        qa_pairs = InterviewQA.objects.filter(session=session)
        total_possible = qa_pairs.count() * 20
        final_percentage = percentage(session.score, total_possible) if total_possible > 0 else 0

        return Response({
            "message": "Interview completed",
            "session_id": session.id,
            "category": session.category,
            "total_score": session.score,
            "max_possible_score": total_possible,
            "percentage": final_percentage,
            "questions_answered": qa_pairs.count(),
            "qa_pairs": [
                {
                    "question": qa.question,
                    "your_answer": qa.user_answer,
                    "score": f"{qa.score}/{qa.max_score}",
                    "feedback": qa.ai_feedback,
                }
                for qa in qa_pairs
            ],
        })


class InterviewHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = InterviewSession.objects.filter(user=request.user).order_by("-started_at")[:10]
        serializer = InterviewSessionSerializer(sessions, many=True)
        return Response(serializer.data)
