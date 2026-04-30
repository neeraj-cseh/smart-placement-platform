from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, DailyGoal, UserStreak


class CustomUserAdmin(UserAdmin):
    model = User

    list_display = ('email', 'name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')

    ordering = ('email',)
    search_fields = ('email',)

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
admin.site.register(UserProfile)
admin.site.register(DailyGoal)
admin.site.register(UserStreak)