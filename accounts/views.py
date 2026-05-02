import logging
from django.db import models, transaction
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .serializers import (
    AccountSettingsSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    DailyGoalSerializer,
)
from .models import UserProfile, DailyGoal, UserStreak
from datetime import date, timedelta
from core.models import (
    ActivityEvent,
    CompanyTarget,
    DailyPlanItem,
    InterviewReadiness,
    RevisionQueueItem,
    TestAttempt,
    Topic,
    Track,
    UserAnswer,
    UserTopicProgress,
)
from core.bootstrap import COMPANY_CATALOG, ensure_platform_catalog, ensure_user_preparation_data

logger = logging.getLogger(__name__)


class LoginThrottle(AnonRateThrottle):
    rate = '5/minute'


def percentage(part, total):
    if not total:
        return 0
    return round((part / total) * 100)


def bounded_percentage(value):
    return max(0, min(100, int(round(value or 0))))


def tone_for_score(value):
    if value >= 70:
        return "green"
    if value >= 50:
        return "amber"
    if value > 0:
        return "red"
    return "slate"


def format_date_label(day):
    return f"{day.strftime('%A')}, {day.day} {day.strftime('%B %Y')}"


def initials(name_or_email):
    source = (name_or_email or "").strip()
    if not source:
        return "U"
    parts = source.replace("@", " ").replace(".", " ").split()
    return "".join(part[0] for part in parts[:2]).upper()


def relative_time(moment, now):
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


def token_payload_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "initials": initials(user.name or user.email),
            "is_admin": user.is_staff or user.is_superuser,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        },
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ensure_platform_catalog()
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            profile_data = {
                key: serializer.validated_data.get(key)
                for key in [
                    "branch", "college", "degree", "graduation_year",
                    "cgpa", "location", "preferred_role",
                    "has_backlog", "target_companies",
                ]
                if key in serializer.validated_data
            }
            ensure_user_preparation_data(user, profile_data=profile_data)

            return Response({
                "message": "User registered successfully",
                **token_payload_for_user(user),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        if not (user.is_staff or user.is_superuser):
            ensure_user_preparation_data(user)

        return Response({
            "message": "Login successful",
            **token_payload_for_user(user),
        })


class SessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "initials": initials(user.name or user.email),
            "is_admin": user.is_staff or user.is_superuser,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        })


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return Response({
                "access": str(access_token),
            })
        except Exception:
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        return Response({"message": "Logged out successfully"})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ensure_user_preparation_data(request.user)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = AccountSettingsSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        ensure_user_preparation_data(request.user)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = AccountSettingsSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DailyGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        goals = DailyGoal.objects.filter(user=request.user, date=today).order_by('-created_at')
        serializer = DailyGoalSerializer(goals, many=True)
        return Response(serializer.data)

    def post(self, request):
        today = date.today()

        data = request.data.copy()
        data['date'] = today

        serializer = DailyGoalSerializer(data=data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            streak, created = UserStreak.objects.get_or_create(user=request.user)

            if streak.last_active_date == today:
                pass
            elif streak.last_active_date == today - timedelta(days=1):
                streak.current_streak += 1
            else:
                streak.current_streak = 1

            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak

            streak.last_active_date = today
            streak.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DailyGoalUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            goal = DailyGoal.objects.get(id=pk, user=request.user)
        except DailyGoal.DoesNotExist:
            return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DailyGoalSerializer(goal, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StreakView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        streak, created = UserStreak.objects.get_or_create(user=request.user)

        return Response({
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak
        })


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff or request.user.is_superuser:
            return Response(
                {"detail": "Admin accounts use the admin console instead of the student dashboard."},
                status=status.HTTP_403_FORBIDDEN,
            )

        ensure_user_preparation_data(request.user)
        user = request.user
        today = timezone.localdate()
        now = timezone.now()

        profile = getattr(user, 'profile', None)
        if not profile:
            profile, _ = UserProfile.objects.get_or_create(user=user)
        streak, _ = UserStreak.objects.get_or_create(user=user)

        answers_qs = UserAnswer.objects.filter(user=user)
        total_answers = answers_qs.count()
        correct_answers = answers_qs.filter(is_correct=True).count()
        average_accuracy = percentage(correct_answers, total_answers)
        problems_solved = answers_qs.filter(is_correct=True).values("question_id").distinct().count()

        completed_attempts = TestAttempt.objects.filter(
            user=user,
            completed_at__isnull=False,
            total_questions__gt=0,
        )
        tests_taken = completed_attempts.count()
        mock_accuracy = 0
        if tests_taken:
            mock_accuracy = round(
                sum(percentage(attempt.score, attempt.total_questions) for attempt in completed_attempts) / tests_taken
            )

        created_date = timezone.localtime(user.created_at).date() if user.created_at else today
        prep_day = max(1, (today - created_date).days + 1)

        track_scores = []
        track_payload = []

        tracks_qs = Track.objects.prefetch_related('topics').all().order_by("name")
        for track in tracks_qs:
            total_topics = track.topics.filter(is_active=True).count()
            completed_topics = UserTopicProgress.objects.filter(
                user=user,
                topic__track=track,
                topic__is_active=True,
                is_completed=True,
            ).count()
            progress = percentage(completed_topics, total_topics)
            track_scores.append(progress)

            next_topic = Topic.objects.filter(
                track=track,
                is_active=True,
            ).exclude(
                user_progress__user=user,
                user_progress__is_completed=True,
            ).order_by("order", "id").first()

            track_payload.append({
                "name": track.name,
                "status": "Active" if progress > 0 else "Available",
                "progress": progress,
                "next": next_topic.name if next_topic else "Completed" if total_topics else "No topics added",
                "tone": tone_for_score(progress),
            })

        track_average = round(sum(track_scores) / len(track_scores)) if track_scores else 0

        topic_answer_counts = {}
        for row in answers_qs.values("question__topic_id").annotate(
            total=models.Count("id"),
            correct=models.Count("id", filter=Q(is_correct=True)),
        ):
            topic_answer_counts[row["question__topic_id"]] = {
                "total": row["total"],
                "correct": row["correct"],
            }

        topics_qs = Topic.objects.filter(is_active=True).select_related("track").order_by("track__name", "order", "id")
        subject_mastery = []
        for topic in topics_qs:
            stats = topic_answer_counts.get(topic.id, {"total": 0, "correct": 0})
            accuracy = percentage(stats["correct"], stats["total"])
            subject_mastery.append({
                "topic": topic.name,
                "value": accuracy,
                "next": topic.description[:80] if topic.description else "Continue practice",
                "tone": tone_for_score(accuracy),
                "attempts": stats["total"],
            })

        weak_priorities = [
            {
                "topic": item["topic"],
                "score": item["value"],
                "recommendation": item["next"],
            }
            for item in sorted(
                [item for item in subject_mastery if item["attempts"] > 0 and item["value"] < 50],
                key=lambda row: row["value"],
            )[:3]
        ]

        weekly_trend = []
        for days_ago in range(6, -1, -1):
            day = today - timedelta(days=days_ago)
            day_answers = answers_qs.filter(created_at__date=day)
            day_total = day_answers.count()
            day_correct = day_answers.filter(is_correct=True).count()
            weekly_trend.append({
                "day": day.strftime("%a"),
                "solved": day_answers.filter(is_correct=True).values("question_id").distinct().count(),
                "accuracy": percentage(day_correct, day_total),
            })

        company_targets = CompanyTarget.objects.filter(user=user, is_active=True)
        company_payload = [
            {
                "name": company.name,
                "full_name": COMPANY_CATALOG.get(company.name, {}).get("full_name", company.name),
                "readiness": bounded_percentage(company.readiness_percentage),
                "focus": company.focus,
                "tone": company.tone,
                "roles": COMPANY_CATALOG.get(company.name, {}).get("roles", []),
                "official_url": COMPANY_CATALOG.get(company.name, {}).get("official_url", ""),
            }
            for company in company_targets
        ]

        if not company_payload and isinstance(profile.target_companies, list):
            company_payload = [
                {
                    "name": str(company),
                    "full_name": COMPANY_CATALOG.get(str(company), {}).get("full_name", str(company)),
                    "readiness": 0,
                    "focus": "Readiness not assessed",
                    "tone": "slate",
                    "roles": COMPANY_CATALOG.get(str(company), {}).get("roles", []),
                    "official_url": COMPANY_CATALOG.get(str(company), {}).get("official_url", ""),
                }
                for company in profile.target_companies
            ]

        company_average = round(
            sum(company["readiness"] for company in company_payload) / len(company_payload)
        ) if company_payload else 0

        interview_items = InterviewReadiness.objects.filter(user=user)
        interview_payload = [
            {
                "area": item.area,
                "score": f"{item.score}/{item.max_score}",
                "progress": bounded_percentage(item.progress_percentage),
            }
            for item in interview_items
        ]
        interview_average = round(
            sum(item["progress"] for item in interview_payload) / len(interview_payload)
        ) if interview_payload else 0

        readiness_score = round(
            (average_accuracy * 0.35)
            + (track_average * 0.25)
            + (mock_accuracy * 0.15)
            + (company_average * 0.15)
            + (interview_average * 0.10)
        )

        plan_items = DailyPlanItem.objects.filter(user=user, date=today)
        plan_payload = [
            {
                "task": item.title,
                "detail": item.detail,
                "status": item.status or ("Completed" if item.is_completed else "Pending"),
                "progress": bounded_percentage(item.progress_percentage),
                "tone": item.tone,
            }
            for item in plan_items
        ]

        if not plan_payload:
            goals = DailyGoal.objects.filter(user=user, date=today).order_by("created_at")
            plan_payload = [
                {
                    "task": goal.goal_text,
                    "detail": "Daily goal",
                    "status": "Completed" if goal.completed else "Pending",
                    "progress": 100 if goal.completed else 0,
                    "tone": "green" if goal.completed else "cyan",
                }
                for goal in goals
            ]

        completed_plan_count = sum(1 for item in plan_payload if item["progress"] >= 100)

        revision_payload = [
            {
                "title": item.title,
                "cycle": item.cycle_label,
                "duration": f"{item.duration_minutes} min",
            }
            for item in RevisionQueueItem.objects.filter(
                user=user,
                due_date__lte=today,
                is_completed=False,
            )[:5]
        ]

        explicit_activity = [
            {
                "type": event.event_type,
                "title": event.title,
                "time": relative_time(event.occurred_at, now),
                "occurred_at": event.occurred_at,
            }
            for event in ActivityEvent.objects.filter(user=user).order_by('-occurred_at', '-id')[:6]
        ]

        derived_activity = []
        for answer in answers_qs.select_related("question__topic").order_by("-created_at")[:4]:
            topic_name = answer.question.topic.name if answer.question and answer.question.topic else "Practice"
            derived_activity.append({
                "type": topic_name[:12],
                "title": f"{'Correct' if answer.is_correct else 'Reviewed'} answer in {topic_name}",
                "time": relative_time(answer.created_at, now),
                "occurred_at": answer.created_at,
            })

        for attempt in completed_attempts.select_related("test").order_by("-completed_at")[:3]:
            derived_activity.append({
                "type": "Mock",
                "title": f"Completed {attempt.test.name} with {percentage(attempt.score, attempt.total_questions)}%",
                "time": relative_time(attempt.completed_at, now),
                "occurred_at": attempt.completed_at,
            })

        activity_payload = sorted(
            explicit_activity + derived_activity,
            key=lambda row: row["occurred_at"],
            reverse=True,
        )[:6]
        for item in activity_payload:
            item.pop("occurred_at", None)

        target_company = company_payload[0] if company_payload else None
        subtitle_parts = []
        if profile.branch:
            subtitle_parts.append(profile.branch)
        if profile.cgpa is not None:
            subtitle_parts.append(f"{profile.cgpa} CGPA")

        hour = now.hour
        if hour < 12:
            greeting = f"Good morning, {user.name.split()[0] if user.name else 'there'}"
        elif hour < 17:
            greeting = f"Good afternoon, {user.name.split()[0] if user.name else 'there'}"
        else:
            greeting = f"Good evening, {user.name.split()[0] if user.name else 'there'}"

        return Response({
            "user": {
                "name": user.name,
                "email": user.email,
                "initials": initials(user.name or user.email),
                "is_admin": user.is_staff or user.is_superuser,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "subtitle": " - ".join(subtitle_parts) if subtitle_parts else "Profile incomplete",
                "profile": UserProfileSerializer(profile).data,
            },
            "header": {
                "date_label": format_date_label(today),
                "greeting": greeting,
                "subtitle": f"Placement readiness dashboard - Day {prep_day} of preparation",
            },
            "sidebar": {
                "current_target": {
                    "name": target_company["name"] if target_company else "No target set",
                    "full_name": target_company["full_name"] if target_company else "",
                    "summary": target_company["focus"] if target_company else "Add a company target",
                    "readiness_label": f"{target_company['readiness']}% ready" if target_company else "0% ready",
                    "tone": target_company["tone"] if target_company else "slate",
                    "roles": target_company["roles"] if target_company else [],
                    "official_url": target_company["official_url"] if target_company else "",
                    "readiness": target_company["readiness"] if target_company else 0,
                }
            },
            "metrics": [
                {
                    "label": "Placement readiness",
                    "value": f"{readiness_score}%",
                    "change": "Computed from live progress",
                    "tone": "cyan",
                    "icon": "target",
                },
                {
                    "label": "Problems solved",
                    "value": str(problems_solved),
                    "change": f"{total_answers} total attempts",
                    "tone": "green",
                    "icon": "check",
                },
                {
                    "label": "Day streak",
                    "value": str(streak.current_streak),
                    "change": f"best streak {streak.longest_streak}",
                    "tone": "amber",
                    "icon": "flame",
                },
                {
                    "label": "Average accuracy",
                    "value": f"{average_accuracy}%",
                    "change": f"{correct_answers}/{total_answers} correct",
                    "tone": "violet",
                    "icon": "line",
                },
            ],
            "todays_plan": {
                "title": "Today's plan",
                "subtitle": "Focused work for the next 90 minutes",
                "completed_count": completed_plan_count,
                "total_count": len(plan_payload),
                "readiness": {
                    "value": readiness_score,
                    "label": "Placement readiness",
                    "description": (
                        f"Main blocker: {weak_priorities[0]['topic']} at {weak_priorities[0]['score']}%."
                        if weak_priorities else
                        "No weak topic has crossed the alert threshold yet."
                    ),
                },
                "items": plan_payload,
            },
            "learning_tracks": track_payload,
            "weekly_momentum": weekly_trend,
            "subject_mastery": subject_mastery,
            "company_readiness": company_payload,
            "weakness_priorities": weak_priorities,
            "revision_queue": revision_payload,
            "interview_prep": interview_payload,
            "recent_activity": activity_payload,
        })
