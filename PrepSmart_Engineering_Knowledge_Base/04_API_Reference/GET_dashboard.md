# API: Dashboard Analytics
* **Purpose**: Aggregated telemetry for the user dashboard.
* **Method**: GET
* **URL**: `/api/auth/dashboard/`
* **Authentication**: `IsAuthenticated`
* **Response**: Massive JSON payload containing `readiness_score`, `streaks`, `topic_accuracy`.
* **Database Interaction**: Heavily uses `.annotate()` and `.aggregate()` across `core_useranswer`, `core_testattempt`.
