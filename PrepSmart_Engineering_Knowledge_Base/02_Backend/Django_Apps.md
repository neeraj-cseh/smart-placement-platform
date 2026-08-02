# Backend Apps Structure

## `accounts` App
* **Objective**: Identity, authentication, profiles, daily goals, gamification.
* **Folder Structure**: standard django app (`models.py`, `views.py`, `urls.py`, `serializers.py`).
* **Models**: `User`, `UserProfile`, `UserStreak`, `DailyGoal`.

## `core` App
* **Objective**: Curriculum, Code Lab, AI Interviews, Analytics, Mock Tests.
* **Models**: `Track`, `Topic`, `Question`, `UserAnswer`, `CodingProblem`, `TestCase`, `InterviewSession`.
