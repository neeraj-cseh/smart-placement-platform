from rest_framework import serializers
from .models import User, UserProfile, DailyGoal
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(required=False, allow_blank=True, write_only=True)
    college = serializers.CharField(required=False, allow_blank=True, write_only=True)
    degree = serializers.CharField(required=False, allow_blank=True, write_only=True)
    graduation_year = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    cgpa = serializers.FloatField(required=False, allow_null=True, write_only=True)
    location = serializers.CharField(required=False, allow_blank=True, write_only=True)
    preferred_role = serializers.CharField(required=False, allow_blank=True, write_only=True)
    has_backlog = serializers.BooleanField(required=False, write_only=True)
    target_companies = serializers.JSONField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'name', 'password',
            'branch', 'college', 'degree', 'graduation_year',
            'cgpa', 'location', 'preferred_role',
            'has_backlog', 'target_companies',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        validate_password(value)
        return value

    def validate_cgpa(self, value):
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("CGPA must be between 0 and 10.")
        return value

    def create(self, validated_data):
        profile_data = {}
        for field in [
            "branch", "college", "degree", "graduation_year",
            "cgpa", "location", "preferred_role",
            "has_backlog", "target_companies",
        ]:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)

        user = User.objects.create_user(**validated_data)

        if profile_data:
            UserProfile.objects.update_or_create(user=user, defaults=profile_data)

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', required=False)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'name', 'email',
            'branch', 'college', 'degree', 'graduation_year',
            'cgpa', 'has_backlog', 'location', 'preferred_role',
            'phone', 'linkedin_url', 'github_url', 'portfolio_url',
            'resume_headline', 'bio', 'skills', 'target_companies',
            'weekly_goal_hours', 'timezone',
            'email_notifications', 'product_updates', 'public_profile',
        ]


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'name' in user_data:
            instance.user.name = user_data['name']
            instance.user.save(update_fields=['name'])
        return super().update(instance, validated_data)
class AccountSettingsSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'name', 'email',
            'weekly_goal_hours', 'timezone',
            'email_notifications', 'product_updates', 'public_profile',
        ]

    def validate_weekly_goal_hours(self, value):
        if value < 1 or value > 80:
            raise serializers.ValidationError("Weekly goal hours must be between 1 and 80.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if 'name' in user_data:
            instance.user.name = user_data['name']
            instance.user.save(update_fields=['name'])

        return super().update(instance, validated_data)


class DailyGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyGoal
        fields = ['id', 'goal_text', 'completed', 'date']
        read_only_fields = ['date']

    def validate_goal_text(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Goal text cannot be empty.")
        return value.strip()
