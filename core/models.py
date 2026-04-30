from django.db import models


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

    def __str__(self):
        return f"{self.track.name} - {self.name}"
    
class UserTopicProgress(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    is_completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'topic')

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

    correct_answer = models.CharField(max_length=1)  # A/B/C/D

    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}"
    
class UserAnswer(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_answer = models.CharField(max_length=1)
    is_correct = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Q{self.question.id}"

class Test(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    topics = models.ManyToManyField(Topic)
    questions = models.ManyToManyField(Question)

    duration_minutes = models.IntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class TestAttempt(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.test.name}"