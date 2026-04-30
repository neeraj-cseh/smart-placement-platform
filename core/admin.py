from django.contrib import admin
from .models import (
    Topic,
    Track,
    UserTopicProgress,
    Question,
    UserAnswer,
    Test,
    TestAttempt
)

admin.site.register(Track)
admin.site.register(Topic)
admin.site.register(UserTopicProgress)
admin.site.register(Question)
admin.site.register(UserAnswer)
admin.site.register(Test)
admin.site.register(TestAttempt)