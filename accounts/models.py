from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


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


# ✅ NEW MODEL
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    branch = models.CharField(max_length=100)
    cgpa = models.FloatField(null=True, blank=True)
    has_backlog = models.BooleanField(default=False)
    target_companies = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
    
class DailyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    goal_text = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)

    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.goal_text}"
    
class UserStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)

    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.current_streak}"