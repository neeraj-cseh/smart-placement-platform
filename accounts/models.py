from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    branch = models.CharField(max_length=100, blank=True)
    college = models.CharField(max_length=160, blank=True)
    degree = models.CharField(max_length=120, blank=True)
    graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)
    cgpa = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    has_backlog = models.BooleanField(default=False)
    location = models.CharField(max_length=120, blank=True)
    preferred_role = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    linkedin_url = models.URLField(blank=True, max_length=500)
    github_url = models.URLField(blank=True, max_length=500)
    portfolio_url = models.URLField(blank=True, max_length=500)
    resume_headline = models.CharField(max_length=180, blank=True)
    bio = models.TextField(blank=True)
    skills = models.JSONField(blank=True, null=True)
    target_companies = models.JSONField(blank=True, null=True)
    weekly_goal_hours = models.PositiveSmallIntegerField(default=12)
    timezone = models.CharField(max_length=80, default="Asia/Kolkata")
    email_notifications = models.BooleanField(default=True)
    product_updates = models.BooleanField(default=False)
    public_profile = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class DailyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_goals')

    goal_text = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user.email} - {self.goal_text}"


class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')

    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)

    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.current_streak}"
