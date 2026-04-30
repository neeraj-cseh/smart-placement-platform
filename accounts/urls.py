from django.urls import path
from .views import (
    RegisterView, LoginView, ProfileView,
    DailyGoalView, DailyGoalUpdateView,
    StreakView, DashboardView
)

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('goals/', DailyGoalView.as_view()),
    path('goals/<int:pk>/', DailyGoalUpdateView.as_view()),
    path('streak/', StreakView.as_view()),
    path('dashboard/', DashboardView.as_view()),
]