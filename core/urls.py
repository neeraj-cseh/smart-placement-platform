from django.urls import path
from .views import (
    TrackListView,
    TopicByTrackView,
    CompleteTopicView,
    TrackProgressView,
    QuestionByTopicView,
    SubmitAnswerView,
    WeakTopicView,
    TestDetailView,
    StartTestView,
    SubmitTestView,
    TopicAccuracyView,
    OverallPerformanceView,
    AnalyticsDashboardView,
    AIExplanationView,
)

urlpatterns = [
    path('tracks/', TrackListView.as_view()),
    path('tracks/<int:track_id>/topics/', TopicByTrackView.as_view()),
    path('topics/<int:topic_id>/complete/', CompleteTopicView.as_view()),
    path('tracks/<int:track_id>/progress/', TrackProgressView.as_view()),
    path('topics/<int:topic_id>/questions/', QuestionByTopicView.as_view()),
    path('questions/<int:question_id>/submit/', SubmitAnswerView.as_view()),
    path('weak-topics/', WeakTopicView.as_view()),
    path('tests/<int:test_id>/', TestDetailView.as_view()),
    path('tests/<int:test_id>/start/', StartTestView.as_view()),
    path('tests/submit/', SubmitTestView.as_view()),
    path('analytics/topic-accuracy/', TopicAccuracyView.as_view()),
    path('analytics/overall-performance/', OverallPerformanceView.as_view()),
    path('analytics/dashboard/', AnalyticsDashboardView.as_view()),
    path('ai/explain/', AIExplanationView.as_view()),
]