# Database Schema

## Overview
The database is heavily normalized to 3NF for core relations.

n**: `ProfilePage.jsx` renders controlled forms.
* **Backend implementation**: `UserProfile` model extends the `User` model.
* **Database interaction**: `accounts_userprofile`. `get_or_create` ensures a profile always exists on fetch.
* **APIs involved**: `GET / PUT /api/auth/profile/`.
* **Business logic**: Accepts partial updates (`PATCH/PUT partial=True`).
* **Validation**: DRF `MinValueValidator(0.0)` for CGPA.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: `400 Bad Request` mapping field-level errors to the UI.
* **State management**: Profiles are fetched on-mount and cached locally in component state.
* **Performance optimization**: Minimal payloads; JSON arrays used for `skills` to avoid excessive JOINs.
* **Security considerations**: Enforced isolation; a user can only query their own `request.user` profile.
* **Future improvements**: Implement S3-backed avatar uploads.

## 3. Dashboard
* **Objective**: Provide a real-time, aggregated telemetry view of a user's readiness and activity.
* **Design approach**: Heavy server-side aggregation returning a massive single payload to minimize client network waterfalls.
* **Frontend implementation**: `DashboardPage.jsx` consumes the payload, rendering `recharts` SVG radars and bar charts.
* **Backend implementation**: `DashboardView` computes a Readiness Score (35% Practice, 25% Track, etc.).
* **Database interaction**: Heavy aggregations on `UserAnswer`, `TestAttempt`, and `Topic`.
* **APIs involved**: `GET /api/auth/dashboard/`.
* **Business logic**: Computes accuracy ratios via `.annotate(Count('id', filter=Q(is_correct=True)))`.
* **Validation**: Rejects Admin users, directing them to the Admin Portal.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Fails safely; missing data renders empty charts.
* **State management**: Single overarching React state object.
* **Performance optimization**: Replaces Python `for` loops with Django ORM `annotate` to let MySQL do the math.
* **Security c # Reusing extracted schema details