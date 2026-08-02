import logging
import os
import subprocess
import sys
import tempfile
import time
import requests
from datetime import timedelta
from django.shortcuts import get_object_or_404

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.throttling import UserRateThrottle

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
    InterviewReadiness,
    UserResume,
    CodingContest,
)
from .serializers import TrackSerializer, TopicSerializer, QuestionSerializer, TestSerializer, TestSummarySerializer, CodeSubmissionSerializer, InterviewSessionSerializer
from .bootstrap import COMPANY_CATALOG, ensure_platform_catalog, ensure_user_preparation_data

logger = logging.getLogger(__name__)


class CodeExecutionThrottle(UserRateThrottle):
    scope = 'code_execution'
    rate = '1000/hour'


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
    sections = test_sections_for(test)
    return {
        "id": test.id,
        "name": test.name,
        "description": test.description,
        "duration_minutes": duration,
        "question_count": total_questions,
        "topic_count": test.topics.count(),
        "sections": sections,
        "topic_ids": [section["id"] for section in sections],
        "question_ids": [question.id for question in questions],
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

    def post(self, request):
        return self.get(request)

    def get(self, request):
        ensure_user_preparation_data(request.user)
        targets = CompanyTarget.objects.filter(user=request.user, is_active=True).order_by("order", "name")
        
        # Get dynamic inputs for eligibility check (default to user's profile or 8.5/0)
        cgpa_input = request.data.get("cgpa") or request.query_params.get("cgpa") or 8.5
        backlogs_input = request.data.get("backlogs") or request.query_params.get("backlogs") or 0
        
        try:
            cgpa_val = float(cgpa_input)
            backlogs_val = int(backlogs_input)
        except (ValueError, TypeError):
            cgpa_val = 8.5
            backlogs_val = 0
        
        from core.bootstrap import DEFAULT_COMPANIES, AI_STRATEGIES, DEADLINES, PIPELINE_STAGES
        if not targets.exists():
            for order, (name, readiness, focus, tone) in enumerate(DEFAULT_COMPANIES, start=1):
                CompanyTarget.objects.update_or_create(
                    user=request.user,
                    name=name,
                    defaults={
                        "readiness_percentage": readiness,
                        "focus": focus,
                        "tone": tone,
                        "order": order,
                        "is_active": True,
                    },
                )
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
                "icon": catalog.get("icon", "🏢"),
                "color": catalog.get("color", "#6366f1"),
                "oa": catalog.get("oa", 60),
                "interview": catalog.get("interview", 55),
                "diff": catalog.get("diff", "Medium"),
                "pattern": catalog.get("pattern", "DSA + SD"),
                "radar": catalog.get("radar", [75,65,80,60,70,63]),
                "package": catalog.get("package", "Not specified"),
                "min_cgpa": catalog.get("min_cgpa", 6.0),
                "max_backlogs": catalog.get("max_backlogs", 0),
                "type": "Product" if catalog.get("diff") in ["High", "Expert"] else "Service",
                "skills": {
                    "DSA": catalog.get("radar", [0,0,0,0,0,0])[0],
                    "SystemDesign": catalog.get("radar", [0,0,0,0,0,0])[1],
                    "Projects": catalog.get("radar", [0,0,0,0,0,0])[2]
                },
                "is_eligible": catalog.get("min_cgpa", 0) <= cgpa_val and catalog.get("max_backlogs", 0) >= backlogs_val,
                "requirements": " ".join(catalog.get("eligibility_notes", [])),
                "processes": catalog.get("campus_focus", [])
            })

        average = round(sum(company["readiness"] for company in companies) / len(companies)) if companies else 0
        current_target = max(companies, key=lambda company: company["readiness"], default=None)

        return Response({
            "summary": {
                "target_count": len(companies),
                "average_readiness": average,
                "current_target": current_target,
                "source_count": len([company for company in companies if company["official_url"]]),
                "ai_strategies": AI_STRATEGIES,
                "deadlines": DEADLINES,
                "pipeline_stages": PIPELINE_STAGES,
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


class CompanyDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company_name):
        target = CompanyTarget.objects.filter(user=request.user, name__iexact=company_name).first()
        
        from .bootstrap import COMPANY_CATALOG
        catalog_key = next((k for k in COMPANY_CATALOG.keys() if k.lower() == company_name.lower()), None)
        
        if not catalog_key:
            return Response({"error": "Company not found in catalog."}, status=404)
            
        catalog = COMPANY_CATALOG[catalog_key]
        
        response_data = {
            **catalog,
            "readiness": target.readiness_percentage if target else 0,
            "focus": target.focus if target else "",
            "is_tracked": bool(target and target.is_active),
            "type": "Product" if catalog.get("diff") in ["High", "Expert"] else "Service",
            "skills": {
                "DSA": catalog.get("radar", [0,0,0,0,0,0])[0],
                "SystemDesign": catalog.get("radar", [0,0,0,0,0,0])[1],
                "Projects": catalog.get("radar", [0,0,0,0,0,0])[2]
            }
        }
        
        return Response(response_data, status=200)


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
                "option_a": question.option_a,
                "option_b": question.option_b,
                "option_c": question.option_c,
                "option_d": question.option_d,
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


class AdminQuestionDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        changed_fields = []
        if "topic_id" in request.data:
            try:
                question.topic = Topic.objects.get(id=request.data.get("topic_id"), is_active=True)
            except (Topic.DoesNotExist, ValueError, TypeError):
                return Response({"error": "Valid topic_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            changed_fields.append("topic")

        if "question_text" in request.data:
            question_text = str(request.data.get("question_text", "")).strip()
            if not question_text:
                return Response({"error": "Question text cannot be blank."}, status=status.HTTP_400_BAD_REQUEST)
            question.question_text = question_text
            changed_fields.append("question_text")

        for option_field in ["option_a", "option_b", "option_c", "option_d"]:
            if option_field in request.data:
                option_text = str(request.data.get(option_field, "")).strip()
                if not option_text:
                    return Response({"error": "All four options are required."}, status=status.HTTP_400_BAD_REQUEST)
                setattr(question, option_field, option_text)
                changed_fields.append(option_field)

        if "correct_answer" in request.data:
            correct_answer = str(request.data.get("correct_answer", "")).strip().upper()
            if correct_answer not in ["A", "B", "C", "D"]:
                return Response({"error": "correct_answer must be A, B, C, or D."}, status=status.HTTP_400_BAD_REQUEST)
            question.correct_answer = correct_answer
            changed_fields.append("correct_answer")

        if "difficulty" in request.data:
            difficulty = str(request.data.get("difficulty", "")).strip().lower()
            if difficulty not in ["easy", "medium", "hard"]:
                return Response({"error": "difficulty must be easy, medium, or hard."}, status=status.HTTP_400_BAD_REQUEST)
            question.difficulty = difficulty
            changed_fields.append("difficulty")

        if changed_fields:
            question.save(update_fields=sorted(set(changed_fields)))

        return Response({
            "message": "Question updated",
            "id": question.id,
            "topic_id": question.topic_id,
            "question_text": question.question_text,
            "difficulty": question.difficulty,
            "correct_answer": question.correct_answer,
        })

    def delete(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        if UserAnswer.objects.filter(question=question).exists():
            return Response(
                {"error": "This question has student answer history and cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminTestDetailView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

        changed_fields = []
        if "name" in request.data:
            name = str(request.data.get("name", "")).strip()
            if not name:
                return Response({"error": "Test name cannot be blank."}, status=status.HTTP_400_BAD_REQUEST)
            test.name = name
            changed_fields.append("name")

        if "description" in request.data:
            test.description = str(request.data.get("description", "")).strip()
            changed_fields.append("description")

        if "duration_minutes" in request.data:
            try:
                test.duration_minutes = max(1, int(request.data.get("duration_minutes") or 30))
                changed_fields.append("duration_minutes")
            except (ValueError, TypeError):
                return Response({"error": "Duration must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        if changed_fields:
            test.save(update_fields=sorted(set(changed_fields)))

        topic_ids = request.data.get("topic_ids")
        question_ids = request.data.get("question_ids")

        if topic_ids is not None:
            topics = Topic.objects.filter(id__in=topic_ids, is_active=True)
            test.topics.set(topics)
            if question_ids is None:
                questions = Question.objects.filter(topic__in=topics).order_by("topic__order", "id")[:20]
                test.questions.set(questions)

        if question_ids is not None:
            questions = Question.objects.filter(id__in=question_ids)
            test.questions.set(questions)
            if topic_ids is None:
                test.topics.set(Topic.objects.filter(id__in=questions.values_list("topic_id", flat=True)))

        return Response({"message": "Test updated", "test": test_payload(test)})

    def delete(self, request, test_id):
        try:
            test = Test.objects.get(id=test_id)
        except Test.DoesNotExist:
            return Response({"error": "Test not found"}, status=status.HTTP_404_NOT_FOUND)

        if TestAttempt.objects.filter(test=test).exists():
            return Response(
                {"error": "This test has student attempts and cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        test.delete()
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
    throttle_classes = [CodeExecutionThrottle]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        code = request.data.get("code", "")
        language = request.data.get("language", "python")
        stdin = request.data.get("stdin", "")

        if not code.strip():
            return Response({"error": "Code cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        supported_langs = ["python", "javascript", "sql", "cpp", "c", "java"]
        if language not in supported_langs:
            return Response({"error": f"Only {', '.join(supported_langs)} are supported."}, status=status.HTTP_400_BAD_REQUEST)

        if len(code) > 20000:
            return Response({"error": "Code is too large for the browser runner."}, status=status.HTTP_400_BAD_REQUEST)

        res = execute_code_locally(code, stdin, language)
        
        # Save general workspace code submission
        code_obj = CodeSubmission.objects.create(
            user=request.user,
            code=code,
            language=language,
            output=res["output"],
            error_output=res["error"],
            execution_time_ms=res["execution_time_ms"],
            stdin=stdin,
            status="Accepted" if res["success"] else "Runtime Error" if not res["timeout"] else "TLE",
        )

        return Response({
            "id": code_obj.id,
            "output": res["output"],
            "error": res["error"],
            "success": res["success"],
            "exit_code": res["exit_code"],
            "execution_time_ms": res["execution_time_ms"],
        })


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


from .interview_data import INTERVIEW_QUESTIONS, INTERVIEW_TYPES


class InterviewConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        



        return Response({
            "categories": [
                {
                    "id": key,
                    "label": key.title(),
                    "question_count": len(questions),
                }
                for key, questions in INTERVIEW_QUESTIONS.items()
            ],
            "interview_types": INTERVIEW_TYPES,
        })


class InterviewStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        category = request.data.get("category", "general")

        if category not in INTERVIEW_QUESTIONS:
            category = "general"

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
                import json as json_mod
                from groq import Groq
                client = Groq(api_key=GROQ_API_KEY)
                
                ai_prompt = f"""Act as a supportive, expert Interview Coach. The user is practicing their interview skills.
Question: {current_q['question']}
Candidate's Answer: {answer}

Provide constructive, qualitative coaching feedback on their answer. Highlight what they did well, what could be improved, and how to structure it better.
Do NOT provide a numerical score.

Respond with strictly valid JSON only: {{"coach_feedback": "<your supportive feedback here>"}}"""

                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": ai_prompt}],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                ai_text = response.choices[0].message.content
                parsed = json_mod.loads(ai_text)
                qa_pair.score = 20 # Score is deprecated, default to max
                qa_pair.ai_feedback = parsed.get("coach_feedback", "Great effort. Keep practicing your delivery.")
                qa_pair.save()
            except Exception as e:
                logger.error(f"AI interview coaching failed: {str(e)}")
                qa_pair.score = 20
                qa_pair.ai_feedback = "Answer recorded! Remember to focus on structuring your thoughts clearly."
                qa_pair.save()
        else:
            # No API Key fallback
            qa_pair.score = 20
            qa_pair.ai_feedback = "Answer recorded! Great points, keep it up."
            qa_pair.save()

        session.score += qa_pair.score
        session.save()

        return Response({
            "message": "Answer submitted",
            "feedback": qa_pair.ai_feedback,
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


class ResumeOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get_default_data(self):
        return {
            "alignments": {
                "Amazon": {"score": 74, "details": "Amazon prefers ownership-oriented impact statements. Graph-related experience is underrepresented."},
                "Google": {"score": 48, "details": "Google profile lacks strong algorithmic depth. Emphasize graph traversals and complexity analyses."},
                "Microsoft": {"score": 62, "details": "Microsoft alignment is moderate. Needs scalable systems design descriptions in projects."},
                "TCS": {"score": 88, "details": "TCS alignment is high. General aptitude and base skills are fully matched."},
                "Infosys": {"score": 84, "details": "Infosys alignment is high. Highlight database normalization and coding fundamentals."},
                "Oracle": {"score": 76, "details": "Oracle alignment is strong. Highlight query optimizations and window functions."},
                "Adobe": {"score": 58, "details": "Adobe alignment is moderate. Emphasize UI component scaling and product design patterns."}
            },
            "analyzer": {
                "structure": {"score": 80, "status": "Good", "issues": ["Education details should be at the top for university recruits."]},
                "readability": {"score": 85, "status": "Excellent", "issues": []},
                "technical_depth": {"score": 60, "status": "Moderate", "issues": ["Lacks mention of multithreading, concurrency, or advanced caching concepts."]},
                "projects_quality": {"score": 58, "status": "Needs Work", "issues": ["Scale metrics (users, requests/sec, performance gains) are missing."]},
                "communication": {"score": 72, "status": "Good", "issues": ["Passive voice detected in three bullet points under Experience."]}
            },
            "ats": {
                "matched_keywords": ["React", "Django", "JavaScript", "SQL", "REST API", "Git", "HTML", "CSS", "Python", "SQLite"],
                "missing_keywords": ["Docker", "Redis", "System Design", "AWS", "Graphs", "Unit Testing", "CI/CD", "PostgreSQL"],
                "formatting_score": 92,
                "readability_score": 84,
                "parsing_issues": []
            },
            "projects": [
                {
                    "title": "AI Placement Command Center Dashboard",
                    "sophistication": "Medium",
                    "recruiter_appeal": "High",
                    "stack": ["React", "Django", "SQLite"],
                    "issues": ["No caching or scalability explanation.", "Needs clear performance measurements."],
                    "suggestions": [
                        "Add Redis for caching session views and state.",
                        "Mention measurable user usage metrics (e.g. supporting 500+ active placement tests)."
                    ]
                },
                {
                    "title": "Realtime Chat Space",
                    "sophistication": "Medium",
                    "recruiter_appeal": "Medium",
                    "stack": ["WebSockets", "Node.js"],
                    "issues": ["Lacks description of server utilization or message queueing."],
                    "suggestions": [
                        "Mention message latency statistics (e.g. sub-50ms message roundtrip).",
                        "Incorporate a mock message queue (e.g. RabbitMQ) to handle server crashes."
                    ]
                }
            ],
            "recruiter_simulation": {
                "eye_tracking_heatmap": {
                    "contact_info": 95,
                    "summary": 82,
                    "skills": 78,
                    "experience": 45,
                    "projects": 50,
                    "education": 85
                },
                "rejection_risks": [
                    "Experience bullet points contain zero quantified results.",
                    "Skills section contains keyword lists without proficiency indicators.",
                    "No links to hosted projects or active live deployments."
                ],
                "commentary": [
                    {"section": "Contact Info", "comment": "Good. Clean layout, links to Github and Linkedin are visible and clickable.", "pos": "top"},
                    {"section": "Summary", "comment": "A bit generic. Emphasize systems architecture and actual deliverables instead of vague verbs.", "pos": "middle"},
                    {"section": "Skills", "comment": "Crowded. Group technical items clearly by Languages, Frameworks, and Tools.", "pos": "middle"},
                    {"section": "Experience", "comment": "Weak. Bullet points are too brief and explain responsibilities rather than achievements.", "pos": "lower"},
                    {"section": "Projects", "comment": "Tech stack is interesting, but what scale did these systems handle?", "pos": "lower"}
                ]
            },
            "competitiveness": {
                "overall_percentile": 72,
                "sde_percentile": 68,
                "service_companies_tier": "Top 15%",
                "product_companies_tier": "Top 32%",
                "communication_percentile": 75,
                "technical_percentile": 66
            },
            "rewriter_history": [
                {
                    "before": "Built a web app using React and Django.",
                    "after": "Architected a scalable React-Django analytics dashboard, optimizing state queries to support 500+ active placement simulation trials.",
                    "tone": "Quantified"
                },
                {"before": "Responsible for writing SQL queries.", "after": "Optimized complex analytical SQL queries and database index structures, reducing overall dashboard load latency by 42%.", "tone": "Technical"},
                {"before": "Worked in a team for college project.", "after": "Led a 4-person software engineering team to design and deploy an open-source, synchronized peer interview canvas using WebSockets.", "tone": "Leader"}
            ],
            "branding_copilot": {
                "linkedin": [
                    {"id": 1, "task": "Optimize headline to highlight full-stack SDE capabilities.", "done": False},
                    {"id": 2, "task": "Add project links to Featured section.", "done": True},
                    {"id": 3, "task": "Write LinkedIn summary highlighting placement-ready skills.", "done": False}
                ],
                "github": [
                    {"id": 4, "task": "Add professional README file to all primary repos.", "done": True},
                    {"id": 5, "task": "Host live demo links in repo description headers.", "done": False}
                ],
                "portfolio": [
                    {"id": 6, "task": "Add system architecture diagrams to standout projects.", "done": False}
                ]
            }
        }

    def get(self, request):
        ensure_user_preparation_data(request.user)
        resume, created = UserResume.objects.get_or_create(
            user=request.user,
            defaults={
                "file_name": "neeraj_srinivas_resume.pdf",
                "overall_score": 68,
                "ats_score": 65,
                "recruiter_score": 62,
                "analysis_data": self.get_default_data()
            }
        )
        return Response({
            "id": resume.id,
            "file_name": resume.file_name,
            "uploaded_at": resume.uploaded_at.isoformat(),
            "overall_score": resume.overall_score,
            "ats_score": resume.ats_score,
            "recruiter_score": resume.recruiter_score,
            "analysis_data": resume.analysis_data
        })

    def post(self, request):
        ensure_user_preparation_data(request.user)
        action = request.data.get("action", "upload")

        resume, _ = UserResume.objects.get_or_create(
            user=request.user,
            defaults={
                "file_name": "neeraj_srinivas_resume.pdf",
                "overall_score": 68,
                "ats_score": 65,
                "recruiter_score": 62,
                "analysis_data": self.get_default_data()
            }
        )

        if action == "upload":
            file_name = request.data.get("file_name", "new_resume.pdf")
            # Upgrade scores slightly to simulate AI scan improvements
            resume.file_name = file_name
            resume.overall_score = min(98, resume.overall_score + 10)
            resume.ats_score = min(98, resume.ats_score + 8)
            resume.recruiter_score = min(98, resume.recruiter_score + 12)
            
            # Dynamically shift some default analytics to reflect new upload
            current_data = resume.analysis_data
            if not current_data:
                current_data = self.get_default_data()
            
            current_data["ats"]["formatting_score"] = min(100, current_data["ats"]["formatting_score"] + 5)
            current_data["ats"]["readability_score"] = min(100, current_data["ats"]["readability_score"] + 6)
            current_data["competitiveness"]["overall_percentile"] = min(99, current_data["competitiveness"]["overall_percentile"] + 7)
            
            # Resolve a few issues
            if current_data["analyzer"]["structure"]["issues"]:
                current_data["analyzer"]["structure"]["issues"] = []
                current_data["analyzer"]["structure"]["score"] = 95
            
            resume.analysis_data = current_data
            resume.save()

            ActivityEvent.objects.create(
                user=request.user,
                event_type="Resume",
                title=f"Uploaded and optimized resume: {file_name} (Score: {resume.overall_score}%)",
                occurred_at=timezone.now(),
                metadata={"file_name": file_name, "score": resume.overall_score}
            )

            return Response({
                "message": "Resume uploaded and optimized successfully",
                "id": resume.id,
                "file_name": resume.file_name,
                "uploaded_at": resume.uploaded_at.isoformat(),
                "overall_score": resume.overall_score,
                "ats_score": resume.ats_score,
                "recruiter_score": resume.recruiter_score,
                "analysis_data": resume.analysis_data
            })

        elif action == "rewrite":
            before = request.data.get("before", "")
            tone = request.data.get("tone", "Quantified")
            target_company = request.data.get("target_company", "General")

            # Simple heuristic rewrites for simulated AI responses
            after = f"Refactored {before.lower()} with target metrics, enhancing query speeds by 38% and database scalability."
            if tone == "Quantified":
                after = f"Engineered core dashboard metrics to optimize {before.lower()}, achieving 94% execution accuracy and supporting 500+ active sessions."
            elif tone == "Technical":
                after = f"Architected high-efficiency backend routes to scale {before.lower()}, incorporating index optimizations and reducing API latency by 45%."
            elif tone == "Leader":
                after = f"Spearheaded a cross-functional team of engineers to develop and launch {before.lower()}, accelerating sprint cycles by 25%."
            elif tone == "Impact-Driven":
                after = f"Delivered comprehensive product integrations for {before.lower()}, directly improving overall user conversion rate by 18%."

            if target_company == "Amazon":
                after += " (Aligned to Amazon Principle: Customer Obsession & Ownership)"
            elif target_company == "Google":
                after += " (Aligned to Google: Googlyness & Algorithmic Excellence)"

            current_data = resume.analysis_data
            if not current_data:
                current_data = self.get_default_data()

            current_data["rewriter_history"].insert(0, {
                "before": before,
                "after": after,
                "tone": tone
            })
            resume.analysis_data = current_data
            resume.save()

            return Response({
                "before": before,
                "after": after,
                "tone": tone,
                "rewriter_history": current_data["rewriter_history"]
            })

        elif action == "branding":
            task_id = int(request.data.get("task_id", 0))
            category = request.data.get("category", "linkedin") # linkedin, github, portfolio
            done = bool(request.data.get("done", True))

            current_data = resume.analysis_data
            if not current_data:
                current_data = self.get_default_data()

            for item in current_data["branding_copilot"].get(category, []):
                if item["id"] == task_id:
                    item["done"] = done
                    break

            resume.analysis_data = current_data
            resume.save()

            return Response({
                "message": "Branding task status updated",
                "branding_copilot": current_data["branding_copilot"]
            })

        return Response({"error": "Invalid action specified"}, status=status.HTTP_400_BAD_REQUEST)


class PassportOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get_dynamic_data(self, user):
        from core.models import UserCertificate
        
        skills = {}
        base_skills = ["DSA", "Graphs", "Trees", "DP", "SQL", "DBMS", "OS", "Aptitude", "Communication", "System Design"]
        
        for skill in base_skills:
            skills[skill] = {
                "mastery": 0, "confidence": 0, "solved": 0, "relevance": "Medium",
                "validated": False, "cert_id": None, "hash": None
            }

        certs = UserCertificate.objects.filter(user=user)
        for cert in certs:
            if cert.skill_name in skills:
                skills[cert.skill_name].update({
                    "validated": True,
                    "mastery": cert.skill_score,
                    "confidence": cert.trust_score,
                    "cert_id": cert.certificate_id,
                    "hash": cert.cryptographic_hash
                })

        timeline = []
        for cert in certs:
            timeline.append({
                "id": cert.id,
                "date": cert.verification_date.strftime("%Y-%m-%d"),
                "type": "Verification",
                "title": f"{cert.skill_name} Verified",
                "desc": f"Passed verification with {cert.trust_score}% trust score.",
                "badge": cert.readiness_level
            })
            
        return {
            "skills": skills,
            "timeline": timeline,
            "credibility_analyzer": {
                "radar_data": [
                    {"subject": "Code Verification", "A": 0, "fullMark": 100},
                    {"subject": "Milestone Consistency", "A": 0, "fullMark": 100},
                    {"subject": "Drill Honesty", "A": 0, "fullMark": 100},
                    {"subject": "Project Evidence", "A": 0, "fullMark": 100},
                    {"subject": "Interview Alignment", "A": 0, "fullMark": 100}
                ],
                "inflated_claims": [],
                "weak_evidence": [],
                "checklists": []
            },
            "reputation": {
                "level": "Verified Profile" if certs.exists() else "Unverified Profile",
                "badges": [],
                "rank": "Unranked"
            },
            "copilot": {
                "improvement_plan": "Complete assessments and challenges to build your verified skill graph.",
                "validation_roadmap": []
            }
        }

    def get(self, request):
        from core.models import UserPassport, UserCertificate
        passport, created = UserPassport.objects.get_or_create(user=request.user)
        
        # Always calculate dynamic data instead of relying on saved mock data
        dynamic_data = self.get_dynamic_data(request.user)
        passport.passport_data = dynamic_data
        
        # Calculate scores dynamically based on actual UserCertificates
        certs = UserCertificate.objects.filter(user=request.user)
        
        if certs.exists():
            avg_skill = sum(c.skill_score for c in certs) // certs.count()
            avg_trust = sum(c.trust_score for c in certs) // certs.count()
            
            passport.competency_score = avg_skill
            passport.employability_score = (avg_skill + avg_trust) // 2
            passport.recruiter_trust_score = f"{avg_trust}%"
            
            if certs.count() >= 5:
                passport.readiness_tier = "Product Company Ready"
            elif certs.count() >= 2:
                passport.readiness_tier = "Startup Ready"
            else:
                passport.readiness_tier = "In Training"
        else:
            passport.competency_score = 0
            passport.employability_score = 0
            passport.recruiter_trust_score = "Unverified"
            passport.readiness_tier = "Unverified"
            
        passport.save()

        profile = getattr(request.user, 'profile', None)
        user_info = {
            "name": request.user.name,
            "email": request.user.email,
            "college": profile.college if profile else "",
            "branch": profile.branch if profile else "",
            "cgpa": profile.cgpa if profile else None,
            "graduation_year": profile.graduation_year if profile else None
        }

        return Response({
            "employability_score": passport.employability_score,
            "competency_score": passport.competency_score,
            "recruiter_trust_score": passport.recruiter_trust_score,
            "readiness_tier": passport.readiness_tier,
            "is_public": passport.is_public,
            "public_token": passport.public_token,
            "user_info": user_info,
            "passport_data": passport.passport_data
        })

    def post(self, request):
        from core.models import UserPassport
        action = request.data.get("action")
        passport, _ = UserPassport.objects.get_or_create(user=request.user)
        
        dynamic_data = self.get_dynamic_data(request.user)

        if action == "verify":
            skill_name = request.data.get("skill")
            skills = dynamic_data.get("skills", {})

            if skill_name in skills:
                import uuid
                import random
                from core.models import UserCertificate
                
                # Check if it already exists
                cert, created = UserCertificate.objects.get_or_create(
                    user=request.user,
                    skill_name=skill_name,
                    defaults={
                        'skill_score': random.randint(70, 95),
                        'trust_score': random.randint(80, 98),
                        'readiness_level': 'High Confidence',
                        'evidence_data': {'source': 'passport_sweep'}
                    }
                )
                
                if not created:
                    cert.skill_score = min(100, cert.skill_score + 8)
                    cert.trust_score = min(100, cert.trust_score + 10)
                    cert.save()

                # Recompute dynamic data to include the newly verified skill
                dynamic_data = self.get_dynamic_data(request.user)
                passport.passport_data = dynamic_data
                
                # Calculate scores dynamically based on actual UserCertificates
                certs = UserCertificate.objects.filter(user=request.user)
                if certs.exists():
                    avg_skill = sum(c.skill_score for c in certs) // certs.count()
                    avg_trust = sum(c.trust_score for c in certs) // certs.count()
                    passport.competency_score = avg_skill
                    passport.employability_score = (avg_skill + avg_trust) // 2
                    passport.recruiter_trust_score = f"{avg_trust}%"
                    
                    if certs.count() >= 5:
                        passport.readiness_tier = "Product Company Ready"
                    elif certs.count() >= 2:
                        passport.readiness_tier = "Startup Ready"
                    else:
                        passport.readiness_tier = "In Training"
                else:
                    passport.competency_score = 0
                    passport.employability_score = 0
                    passport.recruiter_trust_score = "Unverified"
                    passport.readiness_tier = "Unverified"

                passport.save()

                return Response({
                    "message": f"{skill_name} verified successfully",
                    "employability_score": passport.employability_score,
                    "competency_score": passport.competency_score,
                    "passport_data": passport.passport_data
                })
            return Response({"error": "Skill not found"}, status=status.HTTP_404_NOT_FOUND)

        elif action == "share":
            is_public = bool(request.data.get("is_public", True))
            passport.is_public = is_public
            if request.data.get("reset_token"):
                import uuid
                passport.public_token = str(uuid.uuid4())
            passport.save()

            return Response({
                "message": "Sharing settings updated",
                "is_public": passport.is_public,
                "public_token": passport.public_token
            })

        elif action == "copilot_checklist":
            task_id = int(request.data.get("task_id", 0))
            done = bool(request.data.get("done", True))
            
            checklists = dynamic_data.get("credibility_analyzer", {}).get("checklists", [])
            for item in checklists:
                if item["id"] == task_id:
                    item["done"] = done
                    break

            passport.passport_data = dynamic_data
            passport.save()

            return Response({
                "message": "Checklist updated",
                "passport_data": passport.passport_data
            })

        return Response({"error": "Invalid action specified"}, status=status.HTTP_400_BAD_REQUEST)


class PublicPassportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        from core.models import UserPassport, UserCertificate
        passport = get_object_or_404(UserPassport, public_token=token)
        if not passport.is_public:
            return Response({"error": "This profile is private"}, status=status.HTTP_403_FORBIDDEN)

        # Calculate scores dynamically based on actual UserCertificates
        certs = UserCertificate.objects.filter(user=passport.user)
        if certs.exists():
            avg_skill = sum(c.skill_score for c in certs) // certs.count()
            avg_trust = sum(c.trust_score for c in certs) // certs.count()
            passport.competency_score = avg_skill
            passport.employability_score = (avg_skill + avg_trust) // 2
            passport.recruiter_trust_score = f"{avg_trust}%"
            
            if certs.count() >= 5:
                passport.readiness_tier = "Product Company Ready"
            elif certs.count() >= 2:
                passport.readiness_tier = "Startup Ready"
            else:
                passport.readiness_tier = "In Training"
        else:
            passport.competency_score = 0
            passport.employability_score = 0
            passport.recruiter_trust_score = "Unverified"
            passport.readiness_tier = "Unverified"

        profile = getattr(passport.user, 'profile', None)
        user_info = {
            "name": passport.user.name,
            "college": profile.college if profile else "",
            "branch": profile.branch if profile else "",
            "graduation_year": profile.graduation_year if profile else None
        }

        return Response({
            "employability_score": passport.employability_score,
            "competency_score": passport.competency_score,
            "recruiter_trust_score": passport.recruiter_trust_score,
            "readiness_tier": passport.readiness_tier,
            "user_info": user_info,
            "passport_data": passport.passport_data
        })


class VerificationDashboardView(APIView):
    def get(self, request):
        from core.models import UserCertificate
        from django.utils.timezone import now
        
        certs = UserCertificate.objects.filter(user=request.user)

        cert_list = []
        for c in certs:
            cert_list.append({
                "id": c.id,
                "skill_name": c.skill_name,
                "skill_score": c.skill_score,
                "trust_score": c.trust_score,
                "readiness_level": c.readiness_level,
                "verification_date": c.verification_date.strftime("%Y-%m-%d"),
                "certificate_id": c.certificate_id,
                "cryptographic_hash": c.cryptographic_hash,
                "evidence_data": c.evidence_data,
                "is_public": c.is_public,
                "sharing_token": c.sharing_token
            })

        # Calculate aggregates
        avg_skill = sum(c.skill_score for c in certs) // certs.count() if certs.exists() else 0
        avg_trust = sum(c.trust_score for c in certs) // certs.count() if certs.exists() else 0

        # Construct full response payload
        profile = getattr(request.user, 'profile', None)
        user_info = {
            "name": request.user.name,
            "college": profile.college if profile else "PrepSmart Institute",
            "branch": profile.branch if profile else "Computer Science",
            "graduation_year": profile.graduation_year if profile else 2026
        }

        # Mock arena challenges
        challenges = []

        # Growth milestones
        timeline = []
        for c in certs:
            timeline.append({
                "id": c.id,
                "date": c.verification_date.strftime("%Y-%m-%d"),
                "type": "Verification",
                "title": f"{c.skill_name} Verified",
                "desc": f"Passed verification with {c.trust_score}% trust score.",
                "badge": c.readiness_level
            })

        # Evidence chart counts
        evidence_chart = []
        for c in certs:
            evidence_chart.append({
                "name": c.skill_name,
                "solved": c.skill_score + 25
            })

        # AI Copilot advice
        copilot_guidance = {
            "advice": "No mock data available. Start taking assessments to build your verification profile.",
            "strategy": "Complete coding challenges in the practice arena.",
            "checklist": []
        }

        return Response({
            "user_info": user_info,
            "employability_confidence": (avg_skill + avg_trust) // 2 if certs.exists() else 0,
            "verification_progress": min(100, certs.count() * 10),
            "verified_competency_score": avg_skill,
            "avg_trust_score": avg_trust,
            "certificates": cert_list,
            "challenges": challenges,
            "timeline": timeline,
            "evidence_chart": evidence_chart,
            "copilot": copilot_guidance
        })

    def post(self, request):
        from core.models import UserCertificate
        action = request.data.get("action")
        
        if action == "issue_certificate":
            skill_name = request.data.get("skill_name")
            skill_score = int(request.data.get("skill_score", 75))
            trust_score = int(request.data.get("trust_score", 80))
            readiness_level = request.data.get("readiness_level", "High Confidence")
            
            # Check if there is an existing certificate
            cert, created = UserCertificate.objects.get_or_create(
                user=request.user,
                skill_name=skill_name,
                defaults={
                    "skill_score": skill_score,
                    "trust_score": trust_score,
                    "readiness_level": readiness_level,
                    "evidence_data": {
                        "solved_problems": 85,
                        "assessments": 4,
                        "mock_interviews": 2,
                        "consistency": 90,
                        "pressure_verified": True
                    }
                }
            )
            if not created:
                # Update existing score
                cert.skill_score = max(cert.skill_score, skill_score)
                cert.trust_score = max(cert.trust_score, trust_score)
                cert.readiness_level = readiness_level
                cert.save()

            return Response({
                "message": "Certificate issued successfully",
                "certificate_id": cert.certificate_id,
                "cryptographic_hash": cert.cryptographic_hash,
                "sharing_token": cert.sharing_token
            })
            
        elif action == "toggle_visibility":
            cert_id = request.data.get("certificate_id")
            cert = get_object_or_404(UserCertificate, user=request.user, certificate_id=cert_id)
            cert.is_public = not cert.is_public
            cert.save()
            return Response({
                "message": f"Certificate visibility toggled to {'public' if cert.is_public else 'private'}",
                "is_public": cert.is_public
            })
            
        return Response({"error": "Invalid action"}, status=400)


class PublicCertificateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        from core.models import UserCertificate
        cert = get_object_or_404(UserCertificate, sharing_token=token)
        if not cert.is_public:
            return Response({"error": "This certificate is private"}, status=status.HTTP_403_FORBIDDEN)

        profile = getattr(cert.user, 'profile', None)
        user_info = {
            "name": cert.user.name,
            "college": profile.college if profile else "PrepSmart Institute",
            "branch": profile.branch if profile else "Computer Science",
            "graduation_year": profile.graduation_year if profile else 2026
        }

        return Response({
            "user_info": user_info,
            "skill_name": cert.skill_name,
            "skill_score": cert.skill_score,
            "trust_score": cert.trust_score,
            "readiness_level": cert.readiness_level,
            "verification_date": cert.verification_date.strftime("%Y-%m-%d"),
            "certificate_id": cert.certificate_id,
            "cryptographic_hash": cert.cryptographic_hash,
            "evidence_data": cert.evidence_data
        })


class PortfolioDashboardView(APIView):
    def _get_dashboard_data(self, request):
        from core.models import UserPortfolio, UserProject
        
        portfolio, created = UserPortfolio.objects.get_or_create(
            user=request.user,
            defaults={
                "portfolio_strength": 78,
                "recruiter_attractiveness": 72,
                "competitiveness_score": 70,
                "selected_template": "SDE Portfolio",
                "analytics": {
                    "views": [12, 18, 15, 24, 30, 28, 35],
                    "recruiter_clicks": [2, 4, 3, 5, 8, 7, 11],
                    "timeline": ["2026-05-23", "2026-05-24", "2026-05-25", "2026-05-26", "2026-05-27", "2026-05-28", "2026-05-29"]
                },
                "copilot_advice": {
                    "advice": "Your backend project coverage is highly robust. However, target optimization for Tier-1 companies shows a gap in AI-focused implementations.",
                    "strategy": "Generate and complete one advanced AI/ML project. Additionally, ensure all active projects have validated compiler execution evidence synced.",
                    "checklist": [
                        {"id": 1, "task": "Add architecture diagrams to all active projects", "done": False},
                        {"id": 2, "task": "Deploy at least one project publicly and sync URL", "done": False},
                        {"id": 3, "task": "Verify code quality through evaluation sweep", "done": True}
                    ]
                }
            }
        )

        projects = UserProject.objects.filter(user=request.user)
        if not projects.exists():
            # Seed default projects for high-fidelity initial experience
            project1 = UserProject.objects.create(
                user=request.user,
                title="Amazon-style Distributed Inventory Command Console",
                description="A high-performance distributed inventory command platform designed to optimize warehouse storage locks, utilize concurrent read/write pools, and survive 10k RPS traffic surges.",
                domain="Backend Engineering",
                tech_stack=["Go", "Redis", "Kafka", "Docker", "PostgreSQL"],
                difficulty="Hard",
                status="Active",
                milestones=[
                    {"id": 1, "title": "Setup Kafka Producer/Consumer Workers", "desc": "Establish robust pub/sub log streams to synchronize transactions across multiple mock warehouses.", "done": True},
                    {"id": 2, "title": "Implement Redis Lock Contention Strategy", "desc": "Eliminate double-booking conflicts on checkouts with locking mechanisms.", "done": False},
                    {"id": 3, "title": "Deploy to Local Cluster & Run Load Tests", "desc": "Verify throughput and document API response times under high-concurrency loops.", "done": False}
                ],
                kanban_board={
                    "todo": [
                        {"id": "t1", "title": "Write Docker-compose configurations", "desc": "Setup standard clusters for PostgreSQL and Kafka locally."},
                        {"id": "t2", "title": "Benchmark checkout throughput", "desc": "Run vegeta load-attacks to verify system bottlenecks."}
                    ],
                    "in_progress": [
                        {"id": "t3", "title": "Build checkout lock endpoints", "desc": "Write Go API endpoints integrating Redis transaction locks."}
                    ],
                    "review": [],
                    "done": [
                        {"id": "t4", "title": "Setup local workspace and database models", "desc": "Implement initial GORM configurations."}
                    ]
                },
                impact_scores={
                    "technical_depth": 88,
                    "business_value": 85,
                    "complexity": 90,
                    "deployment_quality": 82,
                    "documentation_quality": 85,
                    "overall_score": 86
                },
                evaluation_report={
                    "architecture_quality": "Highly resilient multi-tier message architecture. Database connection pooling is optimized.",
                    "scalability_score": 88,
                    "complexity_score": 90,
                    "innovation_score": 82,
                    "recruiter_relevance_score": 92,
                    "improvement_suggestions": "Introduce distributed tracing with OpenTelemetry to identify queue processing delays under peak load."
                },
                github_url="https://github.com/prepsmart-mala/distributed-inventory",
                deployment_url="https://inventory-command.prepsmart.dev",
                architecture_diagram="graph TD\n    Client -->|REST API| API_Gateway\n    API_Gateway -->|Auth Check| Auth_Service\n    API_Gateway -->|Queue Events| Kafka_Broker\n    Kafka_Broker -->|Consume| Inventory_Worker\n    Inventory_Worker -->|Distributed Lock| Redis_Cache\n    Inventory_Worker -->|Write State| PostgreSQL_DB"
            )

            project2 = UserProject.objects.create(
                user=request.user,
                title="AI Resume Intelligence & Matcher Core",
                description="An advanced parser and matcher utilizing LLM embeddings, similarity scores, and custom keyword extractions to align applicant resumes against target SDE profiles.",
                domain="AI/ML",
                tech_stack=["Python", "FastAPI", "PyTorch", "Qdrant", "Hugging Face"],
                difficulty="Medium",
                status="Evaluated",
                milestones=[
                    {"id": 1, "title": "Build Text Extraction Workers", "desc": "Utilize layout-aware libraries to parse complex PDF and Docx formats.", "done": True},
                    {"id": 2, "title": "Setup Vector Database Indexes", "desc": "Store and search resume dense vectors via Qdrant cosine-similarity checks.", "done": True},
                    {"id": 3, "title": "Implement LLM Suggestion Agent", "desc": "Generate real-time re-writing feedback for weak resume bullets.", "done": True}
                ],
                kanban_board={
                    "todo": [],
                    "in_progress": [],
                    "review": [],
                    "done": [
                        {"id": "t5", "title": "Setup Qdrant instance", "desc": "Establish local vector database indexes."},
                        {"id": "t6", "title": "Build FastAPI match engine", "desc": "Write endpoints for matching scores."}
                    ]
                },
                impact_scores={
                    "technical_depth": 82,
                    "business_value": 90,
                    "complexity": 78,
                    "deployment_quality": 85,
                    "documentation_quality": 88,
                    "overall_score": 85
                },
                evaluation_report={
                    "architecture_quality": "Excellent microservice structuring. Similarity scoring logic is clean and fast.",
                    "scalability_score": 82,
                    "complexity_score": 78,
                    "innovation_score": 90,
                    "recruiter_relevance_score": 88,
                    "improvement_suggestions": "Benchmark inference caching using Redis to avoid redundant embedding generation overhead."
                },
                github_url="https://github.com/prepsmart-mala/resume-intelligence",
                deployment_url="https://resume-intelligence.prepsmart.dev",
                architecture_diagram="graph LR\n    User -->|Upload PDF| Parser\n    Parser -->|Raw Text| Embedding_Model\n    Embedding_Model -->|Dense Vector| Vector_Store[Qdrant]\n    Vector_Store -->|Cosine Match| Target_Profiles"
            )
            projects = UserProject.objects.filter(user=request.user)

        project_list = []
        for p in projects:
            project_list.append({
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "domain": p.domain,
                "tech_stack": p.tech_stack,
                "difficulty": p.difficulty,
                "status": p.status,
                "milestones": p.milestones,
                "kanban_board": p.kanban_board,
                "impact_scores": p.impact_scores,
                "evaluation_report": p.evaluation_report,
                "deployment_url": p.deployment_url,
                "github_url": p.github_url,
                "architecture_diagram": p.architecture_diagram,
                "resume_sync_status": p.resume_sync_status,
                "created_at": p.created_at.strftime("%Y-%m-%d")
            })

        profile = getattr(request.user, 'profile', None)
        user_info = {
            "name": request.user.name,
            "college": profile.college if profile else "PrepSmart Institute",
            "branch": profile.branch if profile else "Computer Science",
            "graduation_year": profile.graduation_year if profile else 2026
        }

        return {
            "user_info": user_info,
            "portfolio": {
                "id": portfolio.id,
                "portfolio_strength": portfolio.portfolio_strength,
                "recruiter_attractiveness": portfolio.recruiter_attractiveness,
                "competitiveness_score": portfolio.competitiveness_score,
                "selected_template": portfolio.selected_template,
                "public_url_slug": portfolio.public_url_slug,
                "is_public": portfolio.is_public,
                "analytics": portfolio.analytics,
                "copilot_advice": portfolio.copilot_advice
            },
            "projects": project_list
        }

    def get(self, request):
        return Response(self._get_dashboard_data(request))

    def post(self, request):
        from core.models import UserPortfolio, UserProject, UserResume
        action = request.data.get("action")

        if action == "generate_project":
            domain = request.data.get("domain", "Full Stack")
            difficulty = request.data.get("difficulty", "Medium")
            target_company = request.data.get("target_company", "Google")

            # Project definitions mapped dynamically to domain + company
            company_projects = {
                "Google": {
                    "AI/ML": {
                        "title": "Google-scale Distributed Vector Retrieval System",
                        "description": "An ultra-fast custom vector embedding and similarity database proxy designed to serve neural-search queries in under 5ms using custom graph-index caching.",
                        "tech_stack": ["Python", "FastAPI", "HuggingFace", "Redis", "C++"],
                        "diagram": "graph TD\n    Query -->|Dense Vector| Cache[Redis Cache]\n    Cache -->|Miss| IndexSearch[C++ Graph Search]\n    IndexSearch -->|Read HNSW| RawEmbeds"
                    },
                    "Backend Engineering": {
                        "title": "Google Drive Sync Engine Emulator",
                        "description": "A distributed file synchronization worker pool optimizing chunk-based file diff uploads, file locking pipelines, and hash validations.",
                        "tech_stack": ["Go", "gRPC", "Docker", "SQLite", "MinIO"],
                        "diagram": "graph LR\n    FileWatcher -->|Local Change| ChunkWorker\n    ChunkWorker -->|Delta RPC| Sync_Server\n    Sync_Server -->|Write delta| Chunk_Store"
                    }
                },
                "Amazon": {
                    "Web Development": {
                        "title": "Amazon Prime Video Content Optimization Portal",
                        "description": "A high-fidelity serverless analytics dashboard optimizing video delivery networks, encoding jobs, and cache retention statistics.",
                        "tech_stack": ["React", "NodeJS", "DynamoDB", "AWS Lambda", "S3"],
                        "diagram": "graph TD\n    React_App -->|HTTP| Lambda_API\n    Lambda_API -->|Read CDN logs| DynamoDB\n    Lambda_API -->|Store stats| S3"
                    },
                    "Cloud": {
                        "title": "Automated AWS Elastic Cluster Auto-Scaler",
                        "description": "A cloud infrastructure daemon monitoring CPU, memory, and connection pools, triggering automated instance spin-ups via custom cloud scripts.",
                        "tech_stack": ["Python", "Boto3", "AWS ECS", "CloudWatch", "Grafana"],
                        "diagram": "graph LR\n    Daemon -->|Poll metrics| CloudWatch\n    Daemon -->|Trigger scaling| ECS_Cluster\n    ECS_Cluster -->|Push metrics| Grafana"
                    }
                }
            }

            # Fallback default projects by domain
            fallback_projects = {
                "AI/ML": {
                    "title": "Neural Recommendation Engine Core",
                    "description": "A real-time deep learning recommendation subsystem utilizing neural collaborative filtering to predict user purchase probabilities.",
                    "tech_stack": ["Python", "TensorFlow", "FastAPI", "MongoDB"],
                    "diagram": "graph LR\n    UserHistory -->|Embed| Model[NCF Model]\n    Model -->|Rank list| API_Server\n    API_Server -->|Return payload| Client"
                },
                "Web Development": {
                    "title": "High-Fidelity Real-Time Whiteboard Sandbox",
                    "description": "A collaborative graphic design and drawing sandbox utilizing WebSockets, canvas buffer synchronization, and document revision tracking.",
                    "tech_stack": ["React", "TypeScript", "NodeJS", "Socket.io", "Redis"],
                    "diagram": "graph TD\n    Client1 -->|Draw Event| WebSocket\n    Client2 -->|Draw Event| WebSocket\n    WebSocket -->|Sync state| Redis"
                },
                "Data Analytics": {
                    "title": "Streaming Clickstream Analytics Processor",
                    "description": "A robust data pipeline aggregating website user clickstreams, computing session bounce rates, and publishing analytics charts.",
                    "tech_stack": ["Python", "Apache Spark", "Elasticsearch", "Kibana", "Kafka"],
                    "diagram": "graph LR\n    WebLogs --> Kafka\n    Kafka --> Spark_Streaming\n    Spark_Streaming --> Elasticsearch\n    Elasticsearch --> Kibana"
                },
                "Cyber Security": {
                    "title": "Zero-Trust Service Mesh Authentication Gateway",
                    "description": "A secure API gateway proxy validating microservice mutual TLS (mTLS), checking JWT scope authorizations, and blocking rate-violating IPs.",
                    "tech_stack": ["Go", "Envoy", "Opa", "Docker", "Prometheus"],
                    "diagram": "graph TD\n    Client --> mTLS\n    mTLS --> Gateway[Envoy API Gateway]\n    Gateway -->|Verify Policy| OPA\n    Gateway --> Backend_Service"
                },
                "Cloud": {
                    "title": "Automated Multi-Region Terraform Deployer",
                    "description": "An infrastructure management script orchestrating secure cloud deployments, load-balancers setup, and multi-region database replication states.",
                    "tech_stack": ["Terraform", "GitHub Actions", "Docker", "AWS", "Prometheus"],
                    "diagram": "graph LR\n    CI_Pipeline -->|Run Apply| Terraform\n    Terraform -->|Provision AWS| Multi_Region_Infra\n    Multi_Region_Infra -->|Monitor| Prometheus"
                },
                "Backend Engineering": {
                    "title": "Distributed Task Scheduler & Job Queue",
                    "description": "An asynchronous transaction worker queue parsing background jobs, scheduling recurring cron triggers, and handling workers crash recovery.",
                    "tech_stack": ["Go", "Redis", "Docker", "PostgreSQL", "Prometheus"],
                    "diagram": "graph TD\n    Client -->|Enqueue| Task_Store[Redis Queue]\n    Task_Store --> Worker1\n    Task_Store --> Worker2\n    Worker1 -->|DB Write| PostgreSQL"
                },
                "Full Stack": {
                    "title": "Real-Time Developer Collaborative IDE",
                    "description": "A collaborative code workspace enabling multiple developers to concurrently edit files, compile, and run code in isolated sandboxes.",
                    "tech_stack": ["React", "TypeScript", "NodeJS", "Socket.io", "Docker"],
                    "diagram": "graph TD\n    Dev1 --> Workspace\n    Dev2 --> Workspace\n    Workspace --> Socket_Server\n    Socket_Server --> Sandbox_Worker[Docker Runner]"
                },
                "Mobile Development": {
                    "title": "AI-Driven Travel Planner App",
                    "description": "A mobile application generating customized, geo-located itinerary schedules utilizing LLM API suggestions.",
                    "tech_stack": ["Flutter", "Dart", "Firebase", "Google Maps API", "OpenAI"],
                    "diagram": "graph LR\n    MobileApp --> Firebase_Auth\n    MobileApp --> MapService[Google Maps]\n    MobileApp --> LLMService[OpenAI API]"
                }
            }

            company_data = company_projects.get(target_company, company_projects["Google"])
            project_template = company_data.get(domain, fallback_projects.get(domain, fallback_projects["Full Stack"]))

            project = UserProject.objects.create(
                user=request.user,
                title=project_template["title"],
                description=project_template["description"],
                domain=domain,
                tech_stack=project_template["tech_stack"],
                difficulty=difficulty,
                status="Active",
                milestones=[
                    {"id": 1, "title": "Setup Core Service Interfaces & Repositories", "desc": "Define system boundaries, initial data schema, and API route footprints.", "done": False},
                    {"id": 2, "title": "Implement Concurrency and Database Logic", "desc": "Write data transactions, lock contentions, or neural indexing functions.", "done": False},
                    {"id": 3, "title": "Setup Isolated Docker Workspace & Deployment", "desc": "Create Docker files, configure CI workflows, and publish to development cluster.", "done": False}
                ],
                kanban_board={
                    "todo": [
                        {"id": "t_gen1", "title": "Write Dockerfile and compose settings", "desc": "Setup database and background storage clusters."},
                        {"id": "t_gen2", "title": "Build baseline API documentation", "desc": "Document all routes, request parameters, and response templates."}
                    ],
                    "in_progress": [
                        {"id": "t_gen3", "title": "Initialize repository structure", "desc": "Configure core boilerplate interfaces and settings."}
                    ],
                    "review": [],
                    "done": []
                },
                impact_scores={
                    "technical_depth": 0,
                    "business_value": 0,
                    "complexity": 0,
                    "deployment_quality": 0,
                    "documentation_quality": 0,
                    "overall_score": 0
                },
                evaluation_report={},
                github_url=f"https://github.com/prepsmart-mala/{domain.lower().replace(' ', '-')}-app",
                deployment_url=f"https://{domain.lower().replace(' ', '-')}-app.prepsmart.dev",
                architecture_diagram=project_template["diagram"]
            )

            # Update portfolio strength
            portfolio = request.user.portfolio
            portfolio.portfolio_strength = min(100, portfolio.portfolio_strength + 3)
            portfolio.save()

            response_data = self._get_dashboard_data(request)
            response_data["project"] = {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "domain": project.domain,
                "tech_stack": project.tech_stack,
                "difficulty": project.difficulty,
                "status": project.status,
                "milestones": project.milestones,
                "kanban_board": project.kanban_board,
                "github_url": project.github_url,
                "deployment_url": project.deployment_url,
                "architecture_diagram": project.architecture_diagram,
                "resume_sync_status": project.resume_sync_status,
                "created_at": project.created_at.strftime("%Y-%m-%d")
            }
            return Response(response_data)

        elif action == "sync_to_resume":
            project_id = request.data.get("project_id")
            project = get_object_or_404(UserProject, user=request.user, id=project_id)
            project.resume_sync_status = not project.resume_sync_status
            project.save()

            # Optional: sync content directly to UserResume model
            try:
                resume = request.user.resume
                if project.resume_sync_status:
                    if "resume_projects" not in resume.analysis_data:
                        resume.analysis_data["resume_projects"] = []
                    
                    # Avoid duplicate entry
                    if not any(p["id"] == project.id for p in resume.analysis_data["resume_projects"]):
                        resume.analysis_data["resume_projects"].append({
                            "id": project.id,
                            "title": project.title,
                            "description": project.description,
                            "tech_stack": project.tech_stack
                        })
                else:
                    if "resume_projects" in resume.analysis_data:
                        resume.analysis_data["resume_projects"] = [
                            p for p in resume.analysis_data["resume_projects"] if p["id"] != project.id
                        ]
                resume.save()
            except UserResume.DoesNotExist:
                pass # Sync flag updated on project successfully

            response_data = self._get_dashboard_data(request)
            response_data["resume_sync_status"] = project.resume_sync_status
            return Response(response_data)

        elif action in ["update_kanban", "update_board_state"]:
            project_id = request.data.get("project_id")
            kanban_board = request.data.get("kanban_board")
            project = get_object_or_404(UserProject, user=request.user, id=project_id)
            project.kanban_board = kanban_board
            project.save()

            response_data = self._get_dashboard_data(request)
            return Response(response_data)

        elif action == "update_milestones_state":
            project_id = request.data.get("project_id")
            milestones = request.data.get("milestones")
            project = get_object_or_404(UserProject, user=request.user, id=project_id)
            project.milestones = milestones
            project.save()

            response_data = self._get_dashboard_data(request)
            return Response(response_data)

        elif action == "evaluate_project":
            project_id = request.data.get("project_id")
            project = get_object_or_404(UserProject, user=request.user, id=project_id)
            
            # Simulate Project Evaluation Engine running
            import random
            
            tech_d = random.randint(12, 18) + 78 # 78 - 96
            biz_v = random.randint(12, 18) + 76 # 76 - 94
            compl = random.randint(15, 20) + 75 # 75 - 95
            depl = random.randint(10, 18) + 80 # 80 - 98
            doc = random.randint(15, 20) + 78 # 78 - 98
            overall = (tech_d + biz_v + compl + depl + doc) // 5

            project.status = "Evaluated"
            project.impact_scores = {
                "technical_depth": tech_d,
                "business_value": biz_v,
                "complexity": compl,
                "deployment_quality": depl,
                "documentation_quality": doc,
                "overall_score": overall
            }

            project.evaluation_report = {
                "architecture_quality": f"Outstanding abstraction layers. Code complexity patterns align with production code. Tech stack {', '.join(project.tech_stack)} is utilized correctly.",
                "scalability_score": compl,
                "complexity_score": compl,
                "innovation_score": biz_v,
                "recruiter_relevance_score": tech_d + 2,
                "improvement_suggestions": "Configure CI integration tests via GitHub Actions. Document load benchmarks utilizing Vegeta or Locust under concurrent API streams."
            }
            project.save()

            # Boost overall portfolio strength
            portfolio = request.user.portfolio
            portfolio.portfolio_strength = min(100, portfolio.portfolio_strength + 5)
            portfolio.recruiter_attractiveness = min(100, portfolio.recruiter_attractiveness + 6)
            portfolio.competitiveness_score = min(100, portfolio.competitiveness_score + 4)
            portfolio.save()

            response_data = self._get_dashboard_data(request)
            return Response(response_data)

        elif action == "update_template":
            template_name = request.data.get("template_name", "SDE Portfolio")
            portfolio = request.user.portfolio
            portfolio.selected_template = template_name
            portfolio.save()

            response_data = self._get_dashboard_data(request)
            return Response(response_data)

        elif action == "toggle_visibility":
            portfolio = request.user.portfolio
            portfolio.is_public = not portfolio.is_public
            portfolio.save()

            response_data = self._get_dashboard_data(request)
            return Response(response_data)

        return Response({"error": "Invalid action"}, status=400)


class PublicPortfolioView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        from core.models import UserPortfolio, UserProject
        portfolio = get_object_or_404(UserPortfolio, public_url_slug=slug)
        if not portfolio.is_public:
            return Response({"error": "This portfolio is set to private by the student"}, status=status.HTTP_403_FORBIDDEN)

        projects = UserProject.objects.filter(user=portfolio.user)
        project_list = []
        for p in projects:
            project_list.append({
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "domain": p.domain,
                "tech_stack": p.tech_stack,
                "difficulty": p.difficulty,
                "status": p.status,
                "impact_scores": p.impact_scores,
                "evaluation_report": p.evaluation_report,
                "deployment_url": p.deployment_url,
                "github_url": p.github_url,
                "architecture_diagram": p.architecture_diagram
            })

        # Profile info
        profile = getattr(portfolio.user, 'profile', None)
        user_info = {
            "name": portfolio.user.name,
            "college": profile.college if profile else "PrepSmart Institute",
            "branch": profile.branch if profile else "Computer Science",
            "graduation_year": profile.graduation_year if profile else 2026
        }

        # Track views
        if "views" in portfolio.analytics:
            views_list = portfolio.analytics["views"]
            if len(views_list) > 0:
                views_list[-1] = views_list[-1] + 1
                portfolio.save()

        return Response({
            "user_info": user_info,
            "portfolio": {
                "portfolio_strength": portfolio.portfolio_strength,
                "recruiter_attractiveness": portfolio.recruiter_attractiveness,
                "competitiveness_score": portfolio.competitiveness_score,
                "selected_template": portfolio.selected_template
            },
            "projects": project_list
        })


def ensure_coding_problems_mock_data():
    from core.models import CodingProblem
    if not CodingProblem.objects.exists():
        from core.bootstrap import ensure_coding_problems_and_testcases
        ensure_coding_problems_and_testcases()



PYTHON_WRAPPERS = {
    "two-sum": """
import sys
import ast

# User code starts here
{user_code}
# User code ends here

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        try:
            nums_str = lines[0].split("=")[-1].strip() if "=" in lines[0] else lines[0]
            nums = ast.literal_eval(nums_str)
        except:
            nums = list(map(int, lines[0].replace("[","").replace("]","").replace(","," ").split()))
            
        try:
            target_str = lines[1].split("=")[-1].strip() if "=" in lines[1] else lines[1]
            target = int(target_str)
        except:
            target = int(lines[1])
            
        sol = Solution()
        # Support both solve and twoSum
        func = getattr(sol, "solve", getattr(sol, "twoSum", None))
        if func:
            res = func(nums, target)
            if hasattr(res, "__iter__"):
                print(" ".join(map(str, res)))
            else:
                print(res)
        else:
            print("Error: Solution class must have a solve() or twoSum() method")
""",
    "linked-list-cycle": """
import sys

class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

# User code starts here
{user_code}
# User code ends here

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        vals = list(map(int, lines[0].split()))
        pos = int(lines[1])
        if not vals:
            print("false")
            sys.exit(0)
        
        nodes = [ListNode(x) for x in vals]
        for i in range(len(nodes) - 1):
            nodes[i].next = nodes[i+1]
        if pos >= 0 and pos < len(nodes):
            nodes[-1].next = nodes[pos]
            
        sol = Solution()
        func = getattr(sol, "solve", getattr(sol, "hasCycle", None))
        if func:
            print("true" if func(nodes[0]) else "false")
        else:
            print("Error: Solution class must have a solve() or hasCycle() method")
""",
    "invert-binary-tree": """
import sys

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# User code starts here
{user_code}
# User code ends here

def build_tree(vals):
    if not vals:
        return None
    root = TreeNode(vals[0])
    queue = [root]
    i = 1
    while queue and i < len(vals):
        curr = queue.pop(0)
        if vals[i] is not None:
            curr.left = TreeNode(vals[i])
            queue.append(curr.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            curr.right = TreeNode(vals[i])
            queue.append(curr.right)
        i += 1
    return root

def serialize(root):
    if not root:
        return ""
    res = []
    queue = [root]
    while queue:
        curr = queue.pop(0)
        if curr:
            res.append(str(curr.val))
            queue.append(curr.left)
            queue.append(curr.right)
        else:
            res.append("null")
    # Clean tail nulls
    while res and res[-1] == "null":
        res.pop()
    return " ".join(res)

if __name__ == "__main__":
    line = sys.stdin.read().strip()
    if not line:
        print("")
        sys.exit(0)
    vals = [None if x == "null" else int(x) for x in line.split()]
    root = build_tree(vals)
    sol = Solution()
    func = getattr(sol, "solve", getattr(sol, "invertTree", None))
    if func:
        inverted = func(root)
        print(serialize(inverted))
    else:
        print("Error: Solution class must have a solve() or invertTree() method")
""",
    "number-of-islands": """
import sys

# User code starts here
{user_code}
# User code ends here

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if not lines:
        print(0)
        sys.exit(0)
    grid = [list(line.strip().split()) for line in lines]
    sol = Solution()
    func = getattr(sol, "solve", getattr(sol, "numIslands", None))
    if func:
        print(func(grid))
    else:
        print("Error: Solution class must have a solve() or numIslands() method")
"""
}


def execute_code_locally(code, stdin, language="python", timeout=8):
    import time
    import tempfile
    import os
    import sys
    import subprocess
    started = time.perf_counter()
    
    if language == "sql":
        import sqlite3
        try:
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            # Seed mock data
            cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, role TEXT)")
            cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", [
                (1, "Alice Smith", "alice@example.com", "Admin"),
                (2, "Bob Jones", "bob@example.com", "Developer"),
                (3, "Charlie Brown", "charlie@example.com", "Student"),
                (4, "David Green", "david@example.com", "Recruiter")
            ])
            cursor.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER)")
            cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", [
                (1, "SaaS License", 99.99, 50),
                (2, "Developer Guide", 19.99, 200),
                (3, "PrepSmart Pro Book", 29.99, 150)
            ])
            cursor.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, product_id INTEGER, amount REAL, order_date TEXT)")
            cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", [
                (1, 3, 2, 19.99, "2026-05-20"),
                (2, 3, 3, 29.99, "2026-05-21"),
                (3, 2, 1, 99.99, "2026-05-22")
            ])
            conn.commit()
            
            # Execute multiple statements if present
            statements = [s.strip() for s in code.split(";") if s.strip()]
            output_lines = []
            for stmt in statements:
                cursor.execute(stmt)
                if cursor.description:
                    cols = [d[0] for d in cursor.description]
                    rows = cursor.fetchall()
                    col_widths = [len(c) for c in cols]
                    for r in rows:
                        for idx, val in enumerate(r):
                            col_widths[idx] = max(col_widths[idx], len(str(val)))
                    # Format table
                    header = " | ".join(cols[i].ljust(col_widths[i]) for i in range(len(cols)))
                    separator = "-+-".join("-" * col_widths[i] for i in range(len(cols)))
                    table_lines = [header, separator]
                    for r in rows:
                        table_lines.append(" | ".join(str(r[i]).ljust(col_widths[i]) for i in range(len(cols))))
                    output_lines.append("\n".join(table_lines))
                else:
                    output_lines.append(f"Statement executed successfully. Affected rows: {cursor.rowcount}")
            conn.close()
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return {
                "output": "\n\n".join(output_lines),
                "error": "",
                "success": True,
                "exit_code": 0,
                "execution_time_ms": elapsed_ms,
                "timeout": False
            }
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return {
                "output": "",
                "error": str(e),
                "success": False,
                "exit_code": 1,
                "execution_time_ms": elapsed_ms,
                "timeout": False
            }

    try:
        import requests
        lang_map = {
            "python": {"language": "python", "version": "3.10.0"},
            "javascript": {"language": "javascript", "version": "18.15.0"},
            "cpp": {"language": "c++", "version": "10.2.0"},
            "c": {"language": "c", "version": "10.2.0"},
            "java": {"language": "java", "version": "15.0.2"}
        }
        
        if language not in lang_map:
            return {
                "output": "",
                "error": f"Unsupported language: {language}",
                "success": False,
                "exit_code": 1,
                "execution_time_ms": 0,
                "timeout": False
            }

        payload = {
            "language": lang_map[language]["language"],
            "version": lang_map[language]["version"],
            "files": [{"name": f"main.{language}", "content": code}],
            "stdin": stdin or "",
            "args": [],
            "compile_timeout": 10000,
            "run_timeout": timeout * 1000,
            "compile_memory_limit": -1,
            "run_memory_limit": -1
        }
        
        try:
            response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload, timeout=timeout + 2)
            response.raise_for_status()
            result = response.json()
            
            run_result = result.get("run", {})
            compile_result = result.get("compile", {})
            
            if compile_result.get("code", 0) != 0:
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                return {
                    "output": "",
                    "error": compile_result.get("stderr", "Compilation error"),
                    "success": False,
                    "exit_code": compile_result.get("code", 1),
                    "execution_time_ms": elapsed_ms,
                    "timeout": False
                }
                
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            is_timeout = run_result.get("signal") == "SIGKILL"
            
            return {
                "output": run_result.get("stdout", ""),
                "error": run_result.get("stderr", ""),
                "success": run_result.get("code", 1) == 0 and not is_timeout,
                "exit_code": run_result.get("code", 1),
                "execution_time_ms": elapsed_ms,
                "timeout": is_timeout
            }
            
        except requests.exceptions.Timeout:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return {
                "output": "",
                "error": f"Execution timed out after {timeout} seconds.",
                "success": False,
                "exit_code": None,
                "execution_time_ms": elapsed_ms,
                "timeout": True
            }
    except Exception as e:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return {
            "output": "",
            "error": str(e),
            "success": False,
            "exit_code": None,
            "execution_time_ms": elapsed_ms,
            "timeout": False
        }


class CodeLabDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from core.models import CodingProblem, CodingContest, CodeSubmission
        from core.serializers import CodeSubmissionSerializer
        
        # Aggregate statistics strictly for problems (ignoring problem__isnull=False general workspace submissions)
        submissions = CodeSubmission.objects.filter(user=request.user, problem__isnull=False)
        total_attempts = submissions.count()
        accepted_subs = submissions.filter(status="Accepted")
        solved_problem_ids = accepted_subs.order_by().values_list("problem_id", flat=True).distinct()
        
        solved_count = len(solved_problem_ids)
        solved_easy = CodingProblem.objects.filter(id__in=solved_problem_ids, difficulty="Easy").count()
        solved_medium = CodingProblem.objects.filter(id__in=solved_problem_ids, difficulty="Medium").count()
        solved_hard = CodingProblem.objects.filter(id__in=solved_problem_ids, difficulty="Hard").count()
        
        total_problems = CodingProblem.objects.count()
        total_easy = CodingProblem.objects.filter(difficulty="Easy").count()
        total_medium = CodingProblem.objects.filter(difficulty="Medium").count()
        total_hard = CodingProblem.objects.filter(difficulty="Hard").count()
        
        acceptance_rate = 0
        if total_attempts > 0:
            acceptance_rate = int((accepted_subs.count() / total_attempts) * 100)
            
        # Topic mastery percentages
        all_problems = CodingProblem.objects.all()
        topics = {}
        for p in all_problems:
            for topic in p.topics:
                if topic not in topics:
                    topics[topic] = {"total": 0, "solved": 0}
                topics[topic]["total"] += 1
                if p.id in solved_problem_ids:
                    topics[topic]["solved"] += 1
                    
        topic_mastery = []
        for name, counts in topics.items():
            rate = int((counts["solved"] / counts["total"]) * 100) if counts["total"] > 0 else 0
            topic_mastery.append({"topic": name, "mastery": rate, "solved": counts["solved"], "total": counts["total"]})
            
        # Daily challenge problem
        daily_problem = CodingProblem.objects.filter(difficulty="Easy").first()
        daily_challenge = {}
        if daily_problem:
            daily_challenge = {
                "title": daily_problem.title,
                "slug": daily_problem.slug,
                "difficulty": daily_problem.difficulty,
                "topics": daily_problem.topics,
                "xp_reward": 150,
                "is_solved": daily_problem.id in solved_problem_ids
            }
            
        # Contest overview
        contests = CodingContest.objects.filter(is_active=True).order_by("start_time")
        contests_data = [{
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "start_time": c.start_time.isoformat(),
            "end_time": c.end_time.isoformat(),
            "duration_minutes": c.duration_minutes
        } for c in contests]
        
        # Recent submissions
        recent = submissions.order_by("-created_at")[:10]
        recent_data = [{
            "id": s.id,
            "problem_title": s.problem.title if s.problem else "General Workspace",
            "problem_slug": s.problem.slug if s.problem else "",
            "status": s.status,
            "language": s.language,
            "execution_time_ms": s.execution_time_ms,
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M")
        } for s in recent]

        return Response({
            "solved_count": solved_count,
            "total_problems": total_problems,
            "solved_easy": solved_easy,
            "total_easy": total_easy,
            "solved_medium": solved_medium,
            "total_medium": total_medium,
            "solved_hard": solved_hard,
            "total_hard": total_hard,
            "acceptance_rate": acceptance_rate,
            "topic_mastery": topic_mastery,
            "daily_challenge": daily_challenge,
            "contests": contests_data,
            "recent_submissions": recent_data
        })


class ProblemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from core.models import CodingProblem, CodeSubmission, UserProblemBookmark
        
        problems = CodingProblem.objects.all().order_by("id")
        
        # User solved mapping
        solved_ids = set(CodeSubmission.objects.filter(
            user=request.user, status="Accepted"
        ).values_list("problem_id", flat=True).distinct())
        
        # User attempted mapping
        attempted_ids = set(CodeSubmission.objects.filter(
            user=request.user
        ).exclude(status="Accepted").values_list("problem_id", flat=True).distinct())
        
        # User bookmarks
        bookmarked_ids = set(UserProblemBookmark.objects.filter(
            user=request.user
        ).values_list("problem_id", flat=True))
        
        data = [{
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty,
            "topics": p.topics,
            "companies": p.companies,
            "relevance_score": p.relevance_score,
            "readiness_impact": p.readiness_impact,
            "acceptance_rate": getattr(p, 'acceptance_rate', 50.0),
            "is_solved": p.id in solved_ids,
            "is_attempted": p.id in attempted_ids and p.id not in solved_ids,
            "is_bookmarked": p.id in bookmarked_ids
        } for p in problems]
        
        return Response(data)


class ProblemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        from core.models import CodingProblem
        problem = get_object_or_404(CodingProblem, slug=slug)
        
        return Response({
            "id": problem.id,
            "title": problem.title,
            "slug": problem.slug,
            "difficulty": problem.difficulty,
            "topics": problem.topics,
            "companies": problem.companies,
            "relevance_score": problem.relevance_score,
            "readiness_impact": problem.readiness_impact,
            "description": problem.description,
            "constraints": problem.constraints,
            "examples": problem.examples,
            "hints": problem.hints,
            "starter_code": problem.starter_code,
            "acceptance_rate": getattr(problem, 'acceptance_rate', 50.0),
            "testcases": problem.testcases
        })


class ProblemBookmarkToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        from core.models import CodingProblem, UserProblemBookmark
        problem = get_object_or_404(CodingProblem, slug=slug)
        
        bookmark, created = UserProblemBookmark.objects.get_or_create(user=request.user, problem=problem)
        if not created:
            bookmark.delete()
            return Response({"status": "removed", "bookmarked": False})
        return Response({"status": "added", "bookmarked": True})


class CodeRunView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        from core.models import CodingProblem
        
        problem = get_object_or_404(CodingProblem, slug=slug)
        code = request.data.get("code", "")
        stdin = request.data.get("stdin", "")
        language = request.data.get("language", "python")
        
        if not code:
            return Response({"error": "No code content provided"}, status=400)
            
        # Format code using driver wrapper if Python
        executable_code = code
        if language == "python" and slug in PYTHON_WRAPPERS:
            executable_code = PYTHON_WRAPPERS[slug].format(user_code=code)
            
        run_res = execute_code_locally(executable_code, stdin)
        return Response(run_res)


class CodeSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        from core.models import CodingProblem, CodeSubmission, UserPassport
        
        problem = get_object_or_404(CodingProblem, slug=slug)
        code = request.data.get("code", "")
        language = request.data.get("language", "python")
        
        if not code:
            return Response({"error": "No code content provided"}, status=400)
            
        # Check all testcases
        all_passed = True
        status_result = "Accepted"
        failed_testcase = None
        times = []
        passed_cases = 0
        total_cases = len(problem.testcases)
        
        for idx, tc in enumerate(problem.testcases):
            tc_input = tc["input"]
            tc_expected = tc["expected"]
            
            executable_code = code
            if language == "python" and slug in PYTHON_WRAPPERS:
                executable_code = PYTHON_WRAPPERS[slug].format(user_code=code)
                
            res = execute_code_locally(executable_code, tc_input)
            times.append(res["execution_time_ms"])
            
            if res["timeout"]:
                all_passed = False
                status_result = "Time Limit Exceeded"
                failed_testcase = {
                    "index": idx + 1,
                    "is_hidden": tc.get("is_hidden", True),
                    "input": tc_input if not tc.get("is_hidden", True) else None,
                    "expected": tc_expected if not tc.get("is_hidden", True) else None,
                    "reason": "Execution timed out"
                }
                break
            elif not res["success"]:
                all_passed = False
                status_result = "Runtime Error"
                failed_testcase = {
                    "index": idx + 1,
                    "is_hidden": tc.get("is_hidden", True),
                    "input": tc_input if not tc.get("is_hidden", True) else None,
                    "expected": tc_expected if not tc.get("is_hidden", True) else None,
                    "reason": res["error"]
                }
                break
            elif res["output"].strip() != tc_expected.strip():
                all_passed = False
                status_result = "Wrong Answer"
                failed_testcase = {
                    "index": idx + 1,
                    "is_hidden": tc.get("is_hidden", False),
                    "input": tc_input if not tc.get("is_hidden", False) else None,
                    "expected": tc_expected if not tc.get("is_hidden", False) else None,
                    "received": res["output"] if not tc.get("is_hidden", False) else None
                }
                break
            
            passed_cases += 1
                
        # Count attempts
        prev_attempts = CodeSubmission.objects.filter(user=request.user, problem=problem).count()
        avg_time = int(sum(times) / len(times)) if times else 0
        
        submission = CodeSubmission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            output=res["output"] if not all_passed and not res["timeout"] else "All tests passed!",
            error_output=res["error"] if not all_passed else "",
            execution_time_ms=avg_time,
            status=status_result,
            attempt_number=prev_attempts + 1
        )
        
        # Award SDE Readiness / Passport increases on first accept
        readiness_increase = 0
        xp_earned = 0
        if all_passed and prev_attempts == 0:
            readiness_increase = problem.readiness_impact
            xp_earned = 100 if problem.difficulty == "Easy" else 200 if problem.difficulty == "Medium" else 350
            
            passport, created = UserPassport.objects.get_or_create(user=request.user)
            passport.competency_score = min(100, passport.competency_score + readiness_increase)
            passport.employability_score = min(100, passport.employability_score + readiness_increase)
            passport.save()
            
        return Response({
            "id": submission.id,
            "success": all_passed,
            "status": status_result,
            "execution_time_ms": avg_time,
            "passed_cases": passed_cases,
            "total_cases": total_cases,
            "failed_testcase": failed_testcase,
            "readiness_increase": readiness_increase,
            "xp_earned": xp_earned
        })


class ProblemSubmissionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        from core.models import CodingProblem, CodeSubmission
        problem = get_object_or_404(CodingProblem, slug=slug)
        submissions = CodeSubmission.objects.filter(
            user=request.user, problem=problem
        ).order_by("-created_at")
        
        data = [{
            "id": sub.id,
            "status": sub.status,
            "language": sub.language,
            "execution_time_ms": sub.execution_time_ms,
            "memory_kb": sub.memory_kb,
            "created_at": sub.created_at,
            "code": sub.code
        } for sub in submissions]
        return Response(data)


class ProblemEditorialView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        from core.models import CodingProblem, CodeSubmission
        problem = get_object_or_404(CodingProblem, slug=slug)
        
        # Check if user has solved it
        is_solved = CodeSubmission.objects.filter(
            user=request.user, problem=problem, status="Accepted"
        ).exists()
        
        # Mock editorial content for now
        editorial_content = f"""# Editorial: {problem.title}

{"You must solve the problem first to view the full official solution code!" if not is_solved else "Congratulations on solving this! Here is the optimal approach."}

### Approach: Hash Map (O(n) time)
We can use a hash map to store the values we have seen so far and their indices.
As we iterate through the array, we check if the complement (`target - current_value`) exists in the map.

```python
class Solution:
    def solve(self, nums, target):
        seen = {{}}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
```

### Complexity Analysis
- **Time Complexity:** O(N). We traverse the list containing N elements exactly once. Each lookup in the table costs only O(1) time.
- **Space Complexity:** O(N). The extra space required depends on the number of items stored in the hash table, which stores at most N elements.
"""
        return Response({
            "content": editorial_content,
            "is_solved": is_solved
        })


class AIMentorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        from core.models import CodingProblem, CodeSubmission
        problem = get_object_or_404(CodingProblem, slug=slug)
        
        # AI assistance is locked until the user has made at least one submission
        has_submission = CodeSubmission.objects.filter(
            user=request.user, problem=problem
        ).exists()
        if not has_submission:
            return Response({
                "error": "AI assistance unlocks after your first submission. Try solving the problem first!",
                "locked": True
            }, status=200)
        
        code = request.data.get("code", "")
        action = request.data.get("action", "give_hint")
        error_msg = request.data.get("error_message", "")
        
        # Parse context
        latest_submission = CodeSubmission.objects.filter(
            user=request.user, problem=problem
        ).order_by("-created_at").first()
        
        response_text = ""
        
        if action == "explain_error":
            if error_msg:
                # Deep parsing simulation
                if "SyntaxError" in error_msg:
                    response_text = f"💡 **AI Compiler Analysis:** I detected a `SyntaxError` in your code snippet:\n```python\n{error_msg.splitlines()[-1] if error_msg else ''}\n```\nThis indicates a structural issue. Check for missing colons (`:`), unbalanced parentheses, or indentation mismatches near this line."
                elif "IndexError" in error_msg:
                    response_text = f"💡 **AI Runtime Analysis:** Your code threw an `IndexError`. Looking at your constraints (`{problem.constraints[0] if problem.constraints else 'N/A'}`), you might be accessing an array element beyond `len(nums) - 1`. Double check your loop bounds."
                elif "KeyError" in error_msg:
                    response_text = "💡 **AI Runtime Analysis:** A `KeyError` means you tried to access a dictionary key that doesn't exist. Before doing `map[key]`, either check `if key in map:` or use `map.get(key, default_value)`."
                else:
                    response_text = f"💡 **AI Trace Analysis:** I parsed your trace:\n`{error_msg[:100]}...`\nMake sure your variables are initialized before use and match the expected types defined in the function signature."
            else:
                response_text = "💡 **AI Compiler Analysis:** Your code compiled successfully without throwing fatal exceptions. If you are failing test cases, it is a logical error, not a runtime crash."
                
        elif action == "give_hint":
            import random
            hints = problem.hints or ["Consider tracking state using an auxiliary data structure."]
            response_text = f"💡 **AI Mentor Hint:**\n\n* {random.choice(hints)}\n\n*Think about how the constraints ({', '.join(problem.constraints[:2])}) limit your brute-force options.*"
            
        elif action == "optimize_code":
            # Heuristic complexity analyzer
            nested_loops = code.count("for ") + code.count("while ")
            uses_hash = "dict" in code or "{}" in code or "set(" in code or "Map(" in code
            
            if nested_loops >= 2 and not uses_hash:
                response_text = "🚀 **AI Complexity Analyzer:**\n\n**Time Complexity:** $\\mathcal{O}(n^2)$ (Detected nested loops).\n**Space Complexity:** $\\mathcal{O}(1)$\n\n**Optimization:** You can optimize this! The constraints state `n <= 10^4`, so $\\mathcal{O}(n^2)$ will take $\\sim 10^8$ operations (borderline TLE). Try using a Hash Map to trade space for time, dropping Time Complexity to $\\mathcal{O}(n)$."
            elif uses_hash:
                response_text = "🚀 **AI Complexity Analyzer:**\n\n**Time Complexity:** $\\mathcal{O}(n)$ (Detected linear pass with constant-time hash lookups).\n**Space Complexity:** $\\mathcal{O}(n)$ (Auxiliary hash structure).\n\n**Optimization:** Excellent! This is the optimal time complexity for this constraint profile."
            else:
                response_text = "🚀 **AI Complexity Analyzer:**\n\n**Time Complexity:** $\\mathcal{O}(n)$\n**Space Complexity:** $\\mathcal{O}(1)$\n\n**Optimization:** Your approach appears to use a single pass with constant space. This is highly optimal. Ensure your pointer logic covers all edge cases!"
                
        elif action == "explain_solution":
            response_text = f"📖 **AI Solution Architecture for '{problem.title}':**\n\n1. **State Tracking**: Initialize required variables to hold the accumulator or map.\n2. **Traversal**: Loop through the input structure exactly once (if possible).\n3. **Logic Gate**: At each step, check if the current element satisfies the target condition (e.g., matching a complement or cycle node).\n4. **Update & Return**: If found, return the indices/node. Otherwise, update your state tracker and continue."
                
        elif action == "dry_run":
            ex = problem.examples[0] if problem.examples else {"input": "Example", "output": "Target"}
            response_text = f"🔍 **AI Execution Simulation:**\nLet's dry-run your logic against Example 1:\n- **Input**: `{ex.get('input')}`\n- **Expected Output**: `{ex.get('output')}`\n\nTrace the state of your variables on the first iteration. Does your `if` condition trigger correctly? Simulate it line-by-line."

        return Response({
            "action": action,
            "response": response_text
        })


class ContestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from core.models import CodingContest
        contests = CodingContest.objects.filter(is_active=True).order_by("start_time")
        
        # Live rankings mock
        mock_rankings = []
        
        data = [{
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "start_time": c.start_time.isoformat(),
            "end_time": c.end_time.isoformat(),
            "duration_minutes": c.duration_minutes,
            "platform": c.platform,
            "external_url": c.external_url,
            "problems": [{"title": p.title, "slug": p.slug, "difficulty": p.difficulty} for p in c.problems.all()]
        } for c in contests]
        
        return Response({
            "contests": data,
            "leaderboard": mock_rankings
        })


class ContestLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, contest_id):
        from core.models import CodingContest, CodeSubmission
        
        contest = get_object_or_404(CodingContest, id=contest_id, is_active=True)
        
        # Get all users who have submitted code for problems in this contest
        # during the contest time window
        submissions = CodeSubmission.objects.filter(
            problem__contests=contest,
            status="Accepted",
            created_at__gte=contest.start_time,
            created_at__lte=contest.end_time
        )
        
        # Aggregate stats
        user_stats = {}
        for sub in submissions:
            uid = sub.user.id
            if uid not in user_stats:
                user_stats[uid] = {
                    "user_id": uid,
                    "name": sub.user.name,
                    "solved_problems": set(),
                    "total_time_penalty": 0
                }
            
            # If this problem is not already solved by them, add it and the time penalty
            if sub.problem.id not in user_stats[uid]["solved_problems"]:
                user_stats[uid]["solved_problems"].add(sub.problem.id)
                # Penalty is minutes from contest start
                minutes_taken = int((sub.created_at - contest.start_time).total_seconds() / 60)
                user_stats[uid]["total_time_penalty"] += minutes_taken
                
        # Format for output
        leaderboard = []
        for uid, stats in user_stats.items():
            solved_count = len(stats["solved_problems"])
            leaderboard.append({
                "user_id": stats["user_id"],
                "name": stats["name"],
                "score": solved_count * 100, # Mock 100 points per problem
                "penalty": stats["total_time_penalty"],
                "solved": solved_count
            })
            
        # Sort by score descending, then penalty ascending
        leaderboard.sort(key=lambda x: (-x["score"], x["penalty"]))
        
        # Assign ranks
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
            
        return Response({
            "contest_id": contest.id,
            "title": contest.title,
            "participants": len(leaderboard),
            "leaderboard": leaderboard
        })


class ProblemSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CodeExecutionThrottle]

    def post(self, request, slug):
        from django.shortcuts import get_object_or_404
        from core.models import CodingProblem, CodeSubmission
        from core.services.judge_service import evaluate_submission
        
        p = get_object_or_404(CodingProblem, slug=slug)
        code = request.data.get("code", "")
        language = request.data.get("language", "python")
        is_submit = request.data.get("is_submit", False)
        
        if not code.strip():
            return Response({"error": "Code cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
            
        sub = CodeSubmission.objects.create(
            user=request.user,
            problem=p,
            code=code,
            language=language,
            status="Pending"
        )
        
        sub = evaluate_submission(sub.id, is_submit=is_submit)
        
        return Response({
            "status": sub.status,
            "success": sub.status == "Accepted",
            "execution_time_ms": sub.execution_time_ms,
            "memory_kb": sub.memory_kb,
            "error_output": sub.error_output
        })
class SnippetListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from core.models import CodeSnippet
        snippets = CodeSnippet.objects.filter(user=request.user).order_by('-updated_at')
        return Response([{
            "id": s.id,
            "title": s.title,
            "code": s.code,
            "language": s.language,
            "updated_at": s.updated_at.isoformat()
        } for s in snippets])

    def post(self, request):
        from core.models import CodeSnippet
        title = request.data.get("title", "Untitled Snippet")
        code = request.data.get("code", "")
        language = request.data.get("language", "python")
        
        snippet = CodeSnippet.objects.create(
            user=request.user,
            title=title,
            code=code,
            language=language
        )
        return Response({
            "id": snippet.id,
            "title": snippet.title,
            "code": snippet.code,
            "language": snippet.language,
            "updated_at": snippet.updated_at.isoformat()
        }, status=status.HTTP_201_CREATED)

class SnippetDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        from core.models import CodeSnippet
        from django.shortcuts import get_object_or_404
        snippet = get_object_or_404(CodeSnippet, pk=pk, user=request.user)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PrepCurrentTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        user = request.user
        
        # Get all active topics
        topics = Topic.objects.filter(is_active=True).order_by('track__name', 'order', 'id')
        progress_lookup = {
            p.topic_id: p for p in UserTopicProgress.objects.filter(user=user)
        }

        current_topic = None
        previous_completed = True
        for topic in topics:
            progress = progress_lookup.get(topic.id)
            is_completed = progress.is_completed if progress else False
            
            if not is_completed and previous_completed:
                current_topic = topic
                break
                
            previous_completed = is_completed

        if not current_topic and topics.exists():
            current_topic = topics.last()

        if not current_topic:
            return Response({"error": "No topics found"}, status=status.HTTP_404_NOT_FOUND)

        # Map dynamic practice URL
        practice_url = f"/code-lab/arena?topic={current_topic.name}"
        if "arrays" in current_topic.name.lower() or "strings" in current_topic.name.lower():
            practice_url = "/code-lab/arena/two-sum"
        elif "list" in current_topic.name.lower():
            practice_url = "/code-lab/arena/linked-list-cycle"
        elif "tree" in current_topic.name.lower():
            practice_url = "/code-lab/arena/invert-binary-tree"
        elif "graph" in current_topic.name.lower():
            practice_url = "/code-lab/arena/number-of-islands"

        return Response({
            "id": current_topic.id,
            "name": current_topic.name,
            "description": current_topic.description,
            "track_id": current_topic.track_id,
            "track_name": current_topic.track.name if current_topic.track else "General",
            "practice_url": practice_url
        })


class PrepTopicJourneyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        user = request.user
        
        track_id = request.query_params.get("track")
        if track_id:
            tracks = Track.objects.filter(id=track_id)
        else:
            tracks = Track.objects.all().order_by("name", "id")

        if not tracks.exists():
            return Response({"tracks": [], "focus_queue": []})

        progress_lookup = {
            progress.topic_id: progress
            for progress in UserTopicProgress.objects.filter(user=user).select_related("topic")
        }

        question_totals = {
            row["topic_id"]: row["total"]
            for row in Question.objects.values("topic_id").annotate(total=Count("id"))
        }

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

        from core.models import TopicDependency
        dependency_lookup = {}
        for dep in TopicDependency.objects.all():
            if dep.topic_id not in dependency_lookup:
                dependency_lookup[dep.topic_id] = []
            dependency_lookup[dep.topic_id].append(dep.prerequisite_id)

        for track in tracks:
            topics = list(track.topics.filter(is_active=True).order_by("order", "id"))
            total_topics = len(topics)
            completed_topics = 0
            track_question_count = 0
            remaining_minutes = 0
            previous_topics_complete = True
            topic_payload = []

            # Compute completed topic IDs for locking checks
            completed_topic_ids = {t_id for t_id, p in progress_lookup.items() if p.is_completed}

            for index, topic in enumerate(topics):
                progress = progress_lookup.get(topic.id)
                is_completed = bool(progress and progress.is_completed)
                completed_at = progress.completed_at if progress and progress.completed_at else None
                stats = answer_stats.get(topic.id, {"total": 0, "correct": 0})
                attempts = stats["total"]
                correct = stats["correct"]
                accuracy = (int(correct * 100 / attempts) if attempts else 0)
                question_count = question_totals.get(topic.id, 0)
                estimate = max(20, (question_count or 4) * 5)
                has_started = attempts > 0 or bool(progress)
                
                # Check prerequisites
                prereq_ids = dependency_lookup.get(topic.id, [])
                if prereq_ids:
                    prereqs_complete = True
                    for pid in prereq_ids:
                        if pid not in completed_topic_ids:
                            prereqs_complete = False
                            break
                    is_locked = not prereqs_complete
                else:
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

                # Map dynamic practice URL
                practice_url = f"/code-lab/arena?topic={topic.slug}"

                item = {
                    "id": topic.id,
                    "track_id": track.id,
                    "track_name": track.name,
                    "name": topic.name,
                    "slug": topic.slug,
                    "description": topic.description,
                    "order": topic.order,
                    "checkpoint": f"{index + 1}/{total_topics}",
                    "is_completed": is_completed,
                    "is_locked": is_locked,
                    "status": status_key,
                    "status_label": status_key.replace('_', ' ').title(),
                    "tone": "green" if is_completed else "slate" if is_locked else "blue" if status_key == "current" else "amber",
                    "question_count": question_count,
                    "attempts": attempts,
                    "correct_answers": correct,
                    "accuracy": accuracy,
                    "estimated_minutes": estimate,
                    "completed_at": completed_at.isoformat() if completed_at else None,
                    "practice_url": practice_url,
                }
                topic_payload.append(item)
                all_topics.append(item)
                track_question_count += question_count

                if not is_completed:
                    previous_topics_complete = False

            track_progress = (int(completed_topics * 100 / total_topics) if total_topics else 0)
            tracks_payload.append({
                "id": track.id,
                "name": track.name,
                "description": track.description,
                "status": "Completed" if total_topics and completed_topics == total_topics else "Active" if completed_topics else "Available",
                "tone": "green" if track_progress == 100 else "blue" if track_progress > 0 else "slate",
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
        focus_candidates.sort(key=lambda x: (x["status"] != "current", x["track_name"], x["order"]))
        focus_queue = [
            {
                **topic,
                "reason": "Next unlocked checkpoint" if topic["status"] == "current" else "Ready to start",
            }
            for topic in focus_candidates[:5]
        ]

        return Response({
            "tracks": tracks_payload,
            "focus_queue": focus_queue,
        })


class PrepRoadmapsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        user = request.user
        
        tracks = Track.objects.all().order_by("name", "id")
        progress_lookup = {
            progress.topic_id: progress
            for progress in UserTopicProgress.objects.filter(user=user)
        }

        payload = []
        for track in tracks:
            topics = track.topics.filter(is_active=True)
            total_topics = topics.count()
            completed_topics = sum(
                1 for t in topics if progress_lookup.get(t.id) and progress_lookup[t.id].is_completed
            )
            track_progress = int(completed_topics * 100 / total_topics) if total_topics else 0
            
            payload.append({
                "id": track.id,
                "name": track.name,
                "description": track.description,
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "progress_percentage": track_progress,
                "status": "Completed" if total_topics and completed_topics == total_topics else "Active" if completed_topics else "Available"
            })
            
        return Response({"tracks": payload})


class PrepMilestonesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        user = request.user

        tests = Test.objects.prefetch_related("topics").all().order_by("name")
        
        completed_topic_ids = set(
            UserTopicProgress.objects.filter(
                user=user, is_completed=True
            ).values_list("topic_id", flat=True)
        )

        attempts = TestAttempt.objects.filter(user=user, completed_at__isnull=False)
        best_scores = {}
        attempt_counts = {}
        for a in attempts:
            attempt_counts[a.test_id] = attempt_counts.get(a.test_id, 0) + 1
            score_pct = int(a.score * 100 / a.total_questions) if a.total_questions else 0
            best_scores[a.test_id] = max(best_scores.get(a.test_id, 0), score_pct)

        payload = []
        for test in tests:
            test_topics = test.topics.all()
            is_locked = False
            if test_topics.exists():
                for topic in test_topics:
                    if topic.id not in completed_topic_ids:
                        is_locked = True
                        break

            payload.append({
                "id": test.id,
                "name": test.name,
                "description": test.description,
                "duration_minutes": test.duration_minutes,
                "question_count": test.questions.count(),
                "attempt_count": attempt_counts.get(test.id, 0),
                "best_score": best_scores.get(test.id, None),
                "is_locked": is_locked,
                "topics": [{"id": t.id, "name": t.name} for t in test_topics]
            })

        return Response({"tests": payload})


class PrepCompleteTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ensure_user_preparation_data(request.user)
        topic_id = request.data.get("topic_id")
        if not topic_id:
            return Response({"error": "topic_id is required"}, status=status.HTTP_400_BAD_REQUEST)

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


class PrepTopicDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        ensure_user_preparation_data(request.user)
        user = request.user
        from core.models import Topic, TopicSection, TopicVisualization, TopicRevision, Question, UserTopicProgress
        try:
            topic = Topic.objects.get(slug=slug, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get user progress
        progress = UserTopicProgress.objects.filter(user=user, topic=topic).first()
        is_completed = progress.is_completed if progress else False

        # Get sections
        sections = TopicSection.objects.filter(topic=topic).order_by('order', 'id')
        sections_data = [{
            "id": s.id,
            "title": s.title,
            "content_markdown": s.content_markdown,
            "section_type": s.section_type,
            "order": s.order
        } for s in sections]

        # Get visualization
        vis_data = None
        if hasattr(topic, 'visualization'):
            vis = topic.visualization
            vis_data = {
                "id": vis.id,
                "title": vis.title,
                "visualization_type": vis.visualization_type,
                "config_data": vis.config_data
            }

        # Get revision
        rev_data = None
        if hasattr(topic, 'revision'):
            rev = topic.revision
            rev_data = {
                "id": rev.id,
                "key_takeaways": rev.key_takeaways,
                "cheat_sheet_markdown": rev.cheat_sheet_markdown
            }

        # Get quiz questions
        questions = Question.objects.filter(topic=topic).order_by('id')
        questions_data = [{
            "id": q.id,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "difficulty": q.difficulty,
            "explanation": q.explanation
        } for q in questions]

        # Get coding problems
        from core.models import CodingProblem, CodeSubmission
        problems = CodingProblem.objects.all()
        topic_name = topic.name.lower()
        matched_problems = []
        solved_ids = CodeSubmission.objects.filter(
            user=user, status="Accepted"
        ).values_list("problem_id", flat=True).distinct()

        for p in problems:
            is_match = False
            for t in p.topics:
                if t.lower() == topic.slug.lower() or t.lower() == topic_name:
                    is_match = True
                    break
            if is_match:
                matched_problems.append({
                    "id": p.id,
                    "title": p.title,
                    "slug": p.slug,
                    "difficulty": p.difficulty,
                    "topics": p.topics,
                    "companies": p.companies,
                    "is_solved": p.id in solved_ids
                })

        if topic.domain != "dsa":
            matched_problems = []

        # Get locked status based on dependencies
        from core.models import TopicDependency
        prereqs = TopicDependency.objects.filter(topic=topic)
        is_locked = False
        if prereqs.exists():
            completed_topic_ids = set(
                UserTopicProgress.objects.filter(user=user, is_completed=True)
                .values_list("topic_id", flat=True)
            )
            for prereq in prereqs:
                if prereq.prerequisite_id not in completed_topic_ids:
                    is_locked = True
                    break

        return Response({
            "id": topic.id,
            "name": topic.name,
            "slug": topic.slug,
            "domain": getattr(topic, 'domain', 'dsa'),
            "description": topic.description,
            "interview_frequency": topic.interview_frequency,
            "target_companies": topic.target_companies,
            "why_it_matters": topic.why_it_matters,
            "is_completed": is_completed,
            "is_locked": is_locked,
            "sections": sections_data,
            "visualization": vis_data,
            "revision": rev_data,
            "questions": questions_data,
            "problems": matched_problems
        })


class PrepTopicCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        ensure_user_preparation_data(request.user)
        user = request.user
        from core.models import Topic, UserTopicProgress
        try:
            topic = Topic.objects.get(slug=slug, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

        progress, created = UserTopicProgress.objects.get_or_create(
            user=user,
            topic=topic
        )

        was_completed = progress.is_completed
        progress.is_completed = True
        progress.completed_at = progress.completed_at or timezone.now()
        progress.save()

        if not was_completed:
            from core.models import ActivityEvent
            ActivityEvent.objects.create(
                user=user,
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


class PrepTopicDraftView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        user = request.user
        from core.models import Topic, UserDraft
        try:
            topic = Topic.objects.get(slug=slug, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)
        
        drafts = UserDraft.objects.filter(user=user, topic=topic)
        payload = {d.exercise_id: d.content for d in drafts}
        return Response(payload)

    def post(self, request, slug):
        user = request.user
        from core.models import Topic, UserDraft
        try:
            topic = Topic.objects.get(slug=slug, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)
        
        drafts_data = request.data.get('drafts', {})
        if not isinstance(drafts_data, dict):
            return Response({"error": "drafts must be a dictionary"}, status=status.HTTP_400_BAD_REQUEST)

        for exercise_id, content in drafts_data.items():
            UserDraft.objects.update_or_create(
                user=user,
                topic=topic,
                exercise_id=exercise_id,
                defaults={'content': content}
            )

        return Response({"message": "Drafts saved successfully"})


class PrepTopicQuizSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        ensure_user_preparation_data(request.user)
        user = request.user
        from core.models import Topic, Question, UserAnswer, UserTopicProgress
        try:
            topic = Topic.objects.get(slug=slug, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

        answers = request.data.get("answers", {})
        if not isinstance(answers, dict):
            return Response({"error": "answers dict is required"}, status=status.HTTP_400_BAD_REQUEST)

        questions = Question.objects.filter(topic=topic)
        if not questions.exists():
            return Response({"error": "No quiz questions found for this topic"}, status=status.HTTP_400_BAD_REQUEST)

        total_questions = questions.count()
        correct_count = 0
        results = []

        for q in questions:
            selected = answers.get(str(q.id)) or answers.get(q.id)
            if not selected:
                is_correct = False
                selected = ""
            else:
                is_correct = (selected.upper() == q.correct_answer.upper())

            UserAnswer.objects.update_or_create(
                user=user,
                question=q,
                defaults={
                    "selected_answer": selected,
                    "is_correct": is_correct
                }
            )

            if is_correct:
                correct_count += 1

            results.append({
                "question_id": q.id,
                "selected": selected,
                "correct_answer": q.correct_answer,
                "is_correct": is_correct
            })

        accuracy = int(correct_count * 100 / total_questions) if total_questions else 0
        quiz_passed = accuracy >= 60

        is_completed = False
        completed_at = None
        if quiz_passed:
            progress, created = UserTopicProgress.objects.get_or_create(
                user=user,
                topic=topic
            )
            was_completed = progress.is_completed
            progress.is_completed = True
            progress.completed_at = progress.completed_at or timezone.now()
            progress.save()
            is_completed = True
            completed_at = progress.completed_at

            if not was_completed:
                from core.models import ActivityEvent
                ActivityEvent.objects.create(
                    user=user,
                    event_type="Path",
                    title=f"Completed {topic.name} via Quiz",
                    occurred_at=timezone.now(),
                    metadata={"topic_id": topic.id, "track_id": topic.track_id},
                )

        return Response({
            "total_questions": total_questions,
            "correct_count": correct_count,
            "accuracy": accuracy,
            "passed": quiz_passed,
            "results": results,
            "is_completed": is_completed,
            "completed_at": completed_at
        })


class PrepTopicAIContextView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        ensure_user_preparation_data(request.user)
        user = request.user
        from core.models import Topic, UserTopicProgress, UserAnswer
        try:
            topic = Topic.objects.get(slug=slug, is_active=True)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

        completed_topics = Topic.objects.filter(
            user_progress__user=user,
            user_progress__is_completed=True
        ).values_list('name', flat=True)

        from core.models import TopicDependency
        prereqs = TopicDependency.objects.filter(topic=topic)
        prereq_status = []
        for p in prereqs:
            is_prereq_done = p.prerequisite.name in completed_topics
            prereq_status.append({
                "name": p.prerequisite.name,
                "is_completed": is_prereq_done
            })

        from django.db.models import Count, Q
        weaknesses = []
        low_accuracy_topics = UserAnswer.objects.filter(user=user).values(
            'question__topic__name'
        ).annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        )
        for lat in low_accuracy_topics:
            total = lat['total']
            correct = lat['correct']
            topic_name = lat['question__topic__name']
            accuracy = (correct / total) if total else 1.0
            if accuracy < 0.6:
                weaknesses.append({
                    "topic_name": topic_name,
                    "accuracy_pct": int(accuracy * 100),
                    "reason": f"Low quiz accuracy ({int(accuracy * 100)}%)"
                })

        from core.models import CodeSubmission
        failed_subs = CodeSubmission.objects.filter(user=user).exclude(status="Accepted").select_related('problem')
        for fs in failed_subs:
            if not fs.problem or not fs.problem.topics:
                continue
            tags = fs.problem.topics
            if isinstance(tags, list):
                for tag in tags:
                    if tag not in [w['topic_name'] for w in weaknesses]:
                        weaknesses.append({
                            "topic_name": tag,
                            "reason": f"Has failed coding submissions in {tag}"
                        })

        return Response({
            "current_topic": {
                "id": topic.id,
                "name": topic.name,
                "slug": topic.slug,
                "why_it_matters": topic.why_it_matters,
                "interview_frequency": topic.interview_frequency
            },
            "completed_topics": list(completed_topics),
            "prerequisites": prereq_status,
            "weaknesses": weaknesses[:3]
        })


class PrepTopicAIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        ensure_user_preparation_data(request.user)
        msg = "💡 **System Notice:** The Generative AI Assistant feature is currently disabled because an LLM API Key (e.g., Google Gemini or OpenAI) has not been configured. Please implement genuine LLM API integration to enable contextual chat capabilities."
        return Response({"response": msg})



class ProblemsByTopicView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, topic_id):
        from core.models import Topic, CodingProblem, CodeSubmission
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            return Response({"error": "Topic not found"}, status=status.HTTP_404_NOT_FOUND)

        problems = CodingProblem.objects.all()
        topic_name = topic.name.lower()
        matched = []
        solved_ids = CodeSubmission.objects.filter(
            user=request.user, status="Accepted"
        ).values_list("problem_id", flat=True).distinct()

        for p in problems:
            is_match = False
            for t in p.topics:
                if t.lower() in topic_name or topic_name in t.lower():
                    is_match = True
                    break
            if is_match:
                matched.append({
                    "id": p.id,
                    "title": p.title,
                    "slug": p.slug,
                    "difficulty": p.difficulty,
                    "topics": p.topics,
                    "companies": p.companies,
                    "is_solved": p.id in solved_ids
                })
        
        return Response(matched)


class UserProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        
        user = request.user
        from accounts.models import UserStreak
        from core.models import CodingProblem, CodeSubmission
        
        submissions = CodeSubmission.objects.filter(user=user)
        solved_ids = submissions.filter(status="Accepted").values_list("problem_id", flat=True).distinct()
        solved_count = len(solved_ids)
        total_problems = CodingProblem.objects.count()
        
        total_subs = submissions.count()
        accepted_subs = submissions.filter(status="Accepted").count()
        acceptance_rate = round(accepted_subs * 100.0 / total_subs, 1) if total_subs else 0.0
        
        streak_obj = UserStreak.objects.filter(user=user).first()
        streak = streak_obj.current_streak if streak_obj else 0
        
        solved_problems = CodingProblem.objects.filter(id__in=solved_ids)
        xp = 0
        for p in solved_problems:
            if p.difficulty == "Easy":
                xp += 50
            elif p.difficulty == "Medium":
                xp += 100
            elif p.difficulty == "Hard":
                xp += 250
        
        if xp == 0:
            xp = 1200
            
        return Response({
            "solved_count": solved_count,
            "total_problems": total_problems,
            "acceptance_rate": acceptance_rate,
            "streak": streak,
            "xp": xp
        })




import os
import json
from groq import Groq

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

