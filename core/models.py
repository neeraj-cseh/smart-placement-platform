from django.db import models
from django.core.validators import MinLengthValidator


class Track(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='topics', null=True, blank=True)

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('track', 'order', 'id')

    def __str__(self):
        track_name = self.track.name if self.track else "General"
        return f"{track_name} - {self.name}"


class UserTopicProgress(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='topic_progress')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='user_progress')

    is_completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'topic'], name='unique_user_topic_progress')
        ]
        indexes = [
            models.Index(fields=['user', 'is_completed'], name='idx_user_completed'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.topic.name}"


class Question(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')

    question_text = models.TextField()

    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    correct_answer = models.CharField(max_length=1, validators=[MinLengthValidator(1)])

    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('topic', 'id')

    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}"


class UserAnswer(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')

    selected_answer = models.CharField(max_length=1)
    is_correct = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user', 'is_correct'], name='idx_user_correct'),
            models.Index(fields=['user', 'question'], name='idx_user_question'),
            models.Index(fields=['created_at'], name='idx_created_at'),
        ]

    def __str__(self):
        return f"{self.user.email} - Q{self.question.id}"


class Test(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    topics = models.ManyToManyField(Topic, related_name='tests')
    questions = models.ManyToManyField(Question, related_name='tests')

    duration_minutes = models.IntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TestAttempt(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='test_attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-started_at',)
        indexes = [
            models.Index(fields=['user', 'completed_at'], name='idx_user_completed_attempts'),
            models.Index(fields=['user', 'test'], name='idx_user_test'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.test.name}"


class DailyPlanItem(models.Model):
    TONE_CHOICES = (
        ('cyan', 'Cyan'),
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
        ('violet', 'Violet'),
        ('slate', 'Slate'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='daily_plan_items')

    title = models.CharField(max_length=180)
    detail = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=80, blank=True)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='cyan')

    date = models.DateField()
    order = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date', 'order', 'id')

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class CompanyTarget(models.Model):
    TONE_CHOICES = (
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
        ('slate', 'Slate'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='company_targets')

    name = models.CharField(max_length=120)
    readiness_percentage = models.PositiveSmallIntegerField(default=0)
    focus = models.CharField(max_length=180, blank=True)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='slate')
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', 'name')
        indexes = [
            models.Index(fields=['user', 'is_active'], name='idx_user_active_company'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.name}"


class RevisionQueueItem(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='revision_queue_items')

    title = models.CharField(max_length=180)
    cycle_label = models.CharField(max_length=50)
    duration_minutes = models.PositiveSmallIntegerField(default=10)
    due_date = models.DateField()
    order = models.PositiveSmallIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('due_date', 'order', 'id')

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class InterviewReadiness(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='interview_readiness_items')

    area = models.CharField(max_length=80)
    score = models.PositiveSmallIntegerField(default=0)
    max_score = models.PositiveSmallIntegerField(default=10)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    order = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order', 'area')

    def __str__(self):
        return f"{self.user.email} - {self.area}"


class ActivityEvent(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='activity_events')

    event_type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    occurred_at = models.DateTimeField()
    metadata = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-occurred_at', '-id')
        indexes = [
            models.Index(fields=['user', '-occurred_at'], name='idx_user_activity'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.event_type}"


class CodeSubmission(models.Model):
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='code_submissions')

    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='python')
    output = models.TextField(blank=True, null=True)
    error_output = models.TextField(blank=True, null=True)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    memory_kb = models.IntegerField(null=True, blank=True)
    stdin = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['user', '-created_at'], name='idx_user_code_subs'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.language} ({self.created_at})"


class InterviewSession(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='interview_sessions')

    category = models.CharField(max_length=50, default='general')
    current_question_index = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=5)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=100)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-started_at',)

    def __str__(self):
        return f"{self.user.email} - {self.category} ({self.status})"


class InterviewQA(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='qa_pairs')

    question = models.TextField()
    user_answer = models.TextField()
    ai_feedback = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QA #{self.id} (Session {self.session_id})"
