from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, UserProfileSerializer, DailyGoalSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import UserProfile, DailyGoal, UserStreak
from datetime import date
from datetime import date, timedelta


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "message": "User registered successfully",
                "email": user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ NEW
class DailyGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = date.today()
        goals = DailyGoal.objects.filter(user=request.user, date=today)
        serializer = DailyGoalSerializer(goals, many=True)
        return Response(serializer.data)

    def post(self, request):
        today = date.today()

        data = request.data.copy()
        data['date'] = today

        serializer = DailyGoalSerializer(data=data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            # ✅ STREAK LOGIC
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

# ✅ NEW VIEW
class DailyGoalUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            goal = DailyGoal.objects.get(id=pk, user=request.user)
        except DailyGoal.DoesNotExist:
            return Response({"error": "Goal not found"}, status=404)

        serializer = DailyGoalSerializer(goal, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

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
        today = date.today()

        # profile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile_data = UserProfileSerializer(profile).data

        # goals
        goals = DailyGoal.objects.filter(user=request.user, date=today)
        goals_data = DailyGoalSerializer(goals, many=True).data

        # streak
        streak, _ = UserStreak.objects.get_or_create(user=request.user)

        return Response({
            "profile": profile_data,
            "goals": goals_data,
            "streak": {
                "current_streak": streak.current_streak,
                "longest_streak": streak.longest_streak
            }
        })