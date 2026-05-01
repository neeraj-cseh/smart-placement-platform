from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, DailyGoal, UserStreak


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('email', 'name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')

    ordering = ('email',)
    search_fields = ('email', 'name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )


admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'preferred_role', 'cgpa', 'has_backlog', 'weekly_goal_hours')
    list_filter = ('has_backlog', 'public_profile', 'email_notifications')
    search_fields = ('user__email', 'user__name', 'branch', 'college', 'preferred_role')


@admin.register(DailyGoal)
class DailyGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_text', 'completed', 'date')
    list_filter = ('completed', 'date')
    search_fields = ('user__email', 'goal_text')


@admin.register(UserStreak)
class UserStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'longest_streak', 'last_active_date')
    search_fields = ('user__email', 'user__name')
