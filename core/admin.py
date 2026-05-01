from django.contrib import admin
from .models import (
    Topic,
    Track,
    UserTopicProgress,
    Question,
    UserAnswer,
    Test,
    TestAttempt,
    DailyPlanItem,
    CompanyTarget,
    RevisionQueueItem,
    InterviewReadiness,
    ActivityEvent,
)

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'track', 'order', 'is_active')
    list_filter = ('track', 'is_active')
    search_fields = ('name', 'description', 'track__name')
    ordering = ('track__name', 'order', 'name')


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'topic__track')
    search_fields = ('user__email', 'topic__name')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'difficulty', 'question_text')
    list_filter = ('difficulty', 'topic__track')
    search_fields = ('question_text', 'topic__name')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'selected_answer', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'question__topic__track')
    search_fields = ('user__email', 'question__question_text')


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_minutes', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('topics', 'questions')


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'total_questions', 'completed_at')
    list_filter = ('test', 'completed_at')
    search_fields = ('user__email', 'test__name')


@admin.register(DailyPlanItem)
class DailyPlanItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'status', 'progress_percentage', 'date', 'is_completed')
    list_filter = ('date', 'is_completed', 'tone')
    search_fields = ('user__email', 'title', 'detail')


@admin.register(CompanyTarget)
class CompanyTargetAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'readiness_percentage', 'tone', 'is_active')
    list_filter = ('tone', 'is_active')
    search_fields = ('user__email', 'name', 'focus')


@admin.register(RevisionQueueItem)
class RevisionQueueItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'cycle_label', 'duration_minutes', 'due_date', 'is_completed')
    list_filter = ('due_date', 'is_completed')
    search_fields = ('user__email', 'title')


@admin.register(InterviewReadiness)
class InterviewReadinessAdmin(admin.ModelAdmin):
    list_display = ('user', 'area', 'score', 'max_score', 'progress_percentage')
    list_filter = ('area',)
    search_fields = ('user__email', 'area')


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'title', 'occurred_at')
    list_filter = ('event_type',)
    search_fields = ('user__email', 'title')
