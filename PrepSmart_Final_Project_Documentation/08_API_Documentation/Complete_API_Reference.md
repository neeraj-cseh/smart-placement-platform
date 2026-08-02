# PrepSmart API Documentation

This document provides exhaustive technical documentation for the entire API surface of the PrepSmart platform. Every endpoint is detailed for backend and frontend developers to understand exactly how data flows across the system.

---

## 1. Authentication & Accounts API

### `POST /api/auth/register/`
* **Purpose**: Registers a new user on the platform and initializes their profile and starting streaks.
* **Authentication**: `AllowAny`
* **Request Body**: `{"email": "...", "password": "...", "name": "...", "college": "...", ...}`
* **Response Body**: `{"message": "User registered", "access": "<jwt>", "refresh": "<jwt>", "user": {"id": 1, ...}}`
* **Status Codes**: `201 Created`, `400 Bad Request`.
* **Validation**: Serializer checks for valid email format, unique email constraint in DB, and strong password constraints (min length 8).
* **Business Logic**: Creates `User`, then creates `UserProfile` with metadata, seeds initial `DailyGoal` and `CompanyTarget` records to ensure the dashboard works on first login. Issues initial JWT tokens.
* **Possible Errors**: Email already exists (`400`), weak password (`400`).
* **Frontend Caller**: `AuthPage.jsx` (Signup mode).
* **DB Tables**: `accounts_user`, `accounts_userprofile`, `core_companytarget`.
* **Future Improvements**: Implement email verification (OTP/Magic link) before issuing tokens.

### `POST /api/auth/login/`
* **Purpose**: Authenticates a user and issues short-lived access and long-lived refresh JWTs.
* **Authentication**: `AllowAny`. (Throttled to 5 requests/minute).
* **Request Body**: `{"email": "...", "password": "..."}`
* **Response Body**: `{"message": "Login successful", "access": "<jwt>", "refresh": "<jwt>", "user": {...}}`
* **Status Codes**: `200 OK`, `401 Unauthorized`, `400 Bad Request`.
* **Validation**: Checks if email and password are provided.
* **Business Logic**: Calls Django's `authenticate()`. If valid, triggers `RefreshToken.for_user()`.
* **Possible Errors**: Invalid credentials (`401`).
* **Frontend Caller**: `AuthPage.jsx` (Login mode), `client.js` on silent refresh failures.
* **DB Tables**: `accounts_user`.
* **Future Improvements**: Implement brute-force protection locking accounts after 5 failed attempts.

### `GET /api/auth/session/`
* **Purpose**: Hydrates the frontend AuthContext with the current user's role and details.
* **Authentication**: `IsAuthenticated` (Bearer Token required).
* **Request Body**: None.
* **Response Body**: `{"id": 1, "email": "...", "name": "...", "initials": "...", "is_admin": false}`
* **Status Codes**: `200 OK`, `401 Unauthorized`.
* **Validation**: DRF's JWTAuthentication validates token signature and expiry.
* **Business Logic**: Simply serializes the `request.user` object.
* **Possible Errors**: Invalid token, expired token (`401`).
* **Frontend Caller**: `AuthContext.jsx` on initial app load.
* **DB Tables**: `accounts_user`.
* **Future Improvements**: Include feature flags in the session payload.

### `POST /api/auth/token/refresh/`
* **Purpose**: Rotates an expired access token using a valid refresh token.
* **Authentication**: `AllowAny`
* **Request Body**: `{"refresh": "<jwt>"}`
* **Response Body**: `{"access": "<new_jwt>"}`
* **Status Codes**: `200 OK`, `401 Unauthorized`.
* **Validation**: SimpleJWT library validates the refresh token signature.
* **Business Logic**: Generates a new access token for another 30 minutes.
* **Possible Errors**: Refresh token is expired or malformed (`401`).
* **Frontend Caller**: `api/client.js` (Axios interceptor).
* **DB Tables**: None directly (token validated cryptographically).
* **Future Improvements**: Enable `ROTATE_REFRESH_TOKENS = True` to rotate the refresh token as well for heightened security.

### `POST /api/auth/logout/`
* **Purpose**: Invalidates the user's current session by blacklisting the refresh token.
* **Authentication**: `IsAuthenticated`
* **Request Body**: `{"refresh": "<jwt>"}`
* **Response Body**: `{"message": "Logged out successfully"}`
* **Status Codes**: `200 OK`.
* **Validation**: None.
* **Business Logic**: Adds the provided refresh token to the SimpleJWT blacklist.
* **Possible Errors**: None (fails gracefully if token is missing).
* **Frontend Caller**: `AuthContext.jsx` (`logout()` function).
* **DB Tables**: `outstanding_token`, `blacklisted_token`.
* **Future Improvements**: Push logout event to analytics pipeline.

### `GET / PUT /api/auth/profile/`
* **Purpose**: Retrieve or update the user's extended biographical profile.
* **Authentication**: `IsAuthenticated`
* **Request Body**: (PUT only) `{"college": "...", "cgpa": 9.2, "github_url": "..."}`
* **Response Body**: `{"branch": "...", "cgpa": 9.2, ...}`
* **Status Codes**: `200 OK`, `400 Bad Request`.
* **Validation**: Serializer validates URL formats (github_url) and float constraints (CGPA 0.0 - 10.0).
* **Business Logic**: `get_or_create` ensures a profile exists. PUT applies `partial=True` updates.
* **Possible Errors**: Validation failure on CGPA (`400`).
* **Frontend Caller**: `ProfilePage.jsx`.
* **DB Tables**: `accounts_userprofile`.
* **Future Improvements**: S3 integration for uploading profile pictures.

### `GET / POST / PUT /api/auth/goals/`
* **Purpose**: Manage the daily micro-tasks for the user.
* **Authentication**: `IsAuthenticated`
* **Request Body**: (POST/PUT) `{"goal_text": "...", "completed": true}`
* **Response Body**: Array of Goal objects, or single Goal object.
* **Status Codes**: `200 OK`, `201 Created`, `400 Bad Request`.
* **Validation**: String length constraints.
* **Business Logic**: POST creates a goal mapped to `date.today()`. POSTing a goal *also* triggers the streak calculation logic, updating `UserStreak`.
* **Possible Errors**: Invalid payload.
* **Frontend Caller**: `DashboardPage.jsx` (Daily Plan Widget).
* **DB Tables**: `accounts_dailygoal`, `accounts_userstreak`.
* **Future Improvements**: Background task to roll over uncompleted goals to the next day.

### `GET /api/auth/dashboard/`
* **Purpose**: The most complex endpoint in the system; aggregates all analytics for the main dashboard.
* **Authentication**: `IsAuthenticated`
* **Request Body**: None.
* **Response Body**: Massive nested JSON containing `metrics`, `subject_mastery`, `learning_tracks`, `weekly_momentum`, and `readiness_score`.
* **Status Codes**: `200 OK`, `403 Forbidden` (if Admin).
* **Validation**: Blocks Staff/Admin users (directs them to use Admin portal).
* **Business Logic**: Calculates Readiness Score (35% Practice + 25% Track + 15% Mock + 15% Company + 10% AI). Uses `.annotate(Count('id'))` on `UserAnswer` to group accuracy by `topic_id`. Determines the next uncompleted topic per track. Formats the Activity Feed by chronologically sorting explicit `ActivityEvent` and derived events (recent code submissions).
* **Possible Errors**: None.
* **Frontend Caller**: `DashboardPage.jsx`.
* **DB Tables**: Hits almost every table: `UserAnswer`, `TestAttempt`, `Topic`, `Track`, `CompanyTarget`, `ActivityEvent`.
* **Future Improvements**: Implement a Redis cache layer; this endpoint is highly DB-intensive.

---

## 2. Learning Ecosystem API (`core`)

### `GET /api/tracks/`
* **Purpose**: Fetches all macro-learning tracks.
* **Authentication**: `IsAuthenticated`
* **Response Body**: `[{"id": 1, "name": "DSA", "description": "..."}, ...]`
* **Frontend Caller**: `LearningPathPage.jsx`.
* **DB Tables**: `core_track`.

### `GET /api/tracks/<id>/topics/`
* **Purpose**: Fetches all active sub-topics for a specific track, ordered by sequence.
* **Authentication**: `IsAuthenticated`
* **Response Body**: `[{"id": 1, "name": "Arrays", "is_completed": true}, ...]`
* **Business Logic**: Joins `Topic` with `UserTopicProgress` to inject the `is_completed` boolean specific to the requesting user.
* **Frontend Caller**: `TopicStudyPage.jsx` (Sidebar navigation).
* **DB Tables**: `core_topic`, `core_usertopicprogress`.

### `GET /api/topics/<slug>/questions/`
* **Purpose**: Fetches MCQs to practice a specific topic.
* **Authentication**: `IsAuthenticated`
* **Response Body**: `[{"id": 10, "question_text": "...", "option_a": "...", ...}]` (Excludes `correct_answer`).
* **Validation**: Ensures the topic exists and is active.
* **Business Logic**: Returns questions. Deliberately omits the `correct_answer` field in the serializer so users cannot inspect the network payload to cheat.
* **Frontend Caller**: `PracticePage.jsx` / `TopicStudyPage.jsx`.
* **DB Tables**: `core_question`.

### `POST /api/questions/<id>/submit/`
* **Purpose**: Evaluates a user's answer to an MCQ.
* **Authentication**: `IsAuthenticated`
* **Request Body**: `{"selected_answer": "B"}`
* **Response Body**: `{"is_correct": true, "correct_answer": "B", "explanation": "..."}`
* **Business Logic**: 
  1. Queries DB for `question.correct_answer`.
  2. Compares with user input.
  3. Creates a `UserAnswer` record.
  4. Returns the result and the explanation.
* **Frontend Caller**: `PracticePage.jsx`.
* **DB Tables**: `core_question`, `core_useranswer`.

### `POST /api/topics/<id>/complete/`
* **Purpose**: Marks a topic as 100% completed for the user.
* **Authentication**: `IsAuthenticated`
* **Business Logic**: Creates or updates `UserTopicProgress` setting `is_completed=True`. Updates Track completion percentages.
* **Frontend Caller**: `TopicStudyPage.jsx` (Mark as Complete button).
* **DB Tables**: `core_usertopicprogress`.

---

## 3. Code Lab API (`core`)

### `GET /api/code/problems/`
* **Purpose**: Fetches the list of algorithmic challenges.
* **Authentication**: `IsAuthenticated`
* **Response Body**: `[{"slug": "two-sum", "difficulty": "easy", "acceptance_rate": 55.4, ...}]`
* **Frontend Caller**: `ProblemArenaPage.jsx`.
* **DB Tables**: `core_codingproblem`.

### `GET /api/code/problems/<slug>/`
* **Purpose**: Fetches the full problem statement and boilerplate code.
* **Authentication**: `IsAuthenticated`
* **Response Body**: `{"title": "Two Sum", "description": "...", "starter_code": {"python": "def twoSum():..."}}`
* **Business Logic**: Does NOT return hidden `TestCase` data.
* **Frontend Caller**: `ProblemSolvingPage.jsx`.
* **DB Tables**: `core_codingproblem`.

### `POST /api/code/problems/<slug>/run/`
* **Purpose**: Dry-runs code against the public (visible) test cases only.
* **Authentication**: `IsAuthenticated`
* **Request Body**: `{"language": "python", "code": "def solve():..."}`
* **Response Body**: `{"status": "Accepted", "output": "...", "execution_time": 45}`
* **Business Logic**: Fetches `TestCase` where `is_hidden=False`. Executes code in isolated subprocess. Returns stdout without saving a submission record to the database.
* **Frontend Caller**: `CodingWorkspacePage.jsx` (Run button).
* **DB Tables**: `core_testcase`.

### `POST /api/code/problems/<slug>/submit/`
* **Purpose**: Evaluates code against ALL test cases (hidden and public) and records the attempt.
* **Authentication**: `IsAuthenticated`. Throttled to 10/hour to prevent abusive compute usage.
* **Request Body**: `{"language": "python", "code": "def solve():..."}`
* **Response Body**: `{"status": "Wrong Answer", "failed_case": {"input": "...", "expected": "...", "actual": "..."}, ...}`
* **Business Logic**: 
  1. Fetches all `TestCase` objects.
  2. Executes code.
  3. If stdout matches expected for all, status is "Accepted".
  4. Saves `CodeSubmission` record logging memory, time, and code.
* **Frontend Caller**: `ProblemSolvingPage.jsx` (Submit button).
* **DB Tables**: `core_testcase`, `core_codesubmission`.
* **Future Improvements**: Offload execution to an isolated Docker swarm. Currently vulnerable to malicious `subprocess` exploits if not heavily sandboxed.

### `GET /api/code/problems/<slug>/submissions/`
* **Purpose**: Fetches a user's past code attempts for a specific problem.
* **Authentication**: `IsAuthenticated`
* **Response Body**: `[{"id": 4, "status": "Accepted", "created_at": "...", "code": "..."}, ...]`
* **Frontend Caller**: `ProblemSolvingPage.jsx` (Submissions Tab).
* **DB Tables**: `core_codesubmission`.

---

## 4. AI Interview API (`core`)

### `POST /api/interview/start/`
* **Purpose**: Initializes a new mock interview session.
* **Authentication**: `IsAuthenticated`
* **Request Body**: `{"category": "technical"}`
* **Response Body**: `{"session_id": 12, "total_questions": 5}`
* **Business Logic**: Creates an `InterviewSession` record with `status='active'`.
* **Frontend Caller**: `AIInterviewPage.jsx` (Start screen).
* **DB Tables**: `core_interviewsession`.

### `GET /api/interview/question/`
* **Purpose**: Asks the LLM to generate the next question contextually.
* **Authentication**: `IsAuthenticated`
* **Business Logic**: Fetches past `InterviewQA` pairs. Prompts the LLM API to generate a follow-up question based on the user's previous answer, or a new question if starting.
* **Frontend Caller**: `AIInterviewPage.jsx` (Chat UI).
* **DB Tables**: `core_interviewqa`.

### `POST /api/interview/submit/`
* **Purpose**: Submits a user's typed answer for AI evaluation.
* **Authentication**: `IsAuthenticated`
* **Request Body**: `{"session_id": 12, "answer": "I would use a HashMap because..."}`
* **Response Body**: `{"feedback": "Good choice, O(1) lookup...", "score": 18, "max_score": 20}`
* **Business Logic**: 
  1. Proxies request to OpenAI/Gemini with strict system prompt defining grading rubric.
  2. Parses JSON response.
  3. Saves `InterviewQA` record.
  4. Updates `InterviewSession.current_question_index`.
* **Possible Errors**: Upstream LLM timeout (`504`).
* **Frontend Caller**: `AIInterviewPage.jsx` (Send button).
* **DB Tables**: `core_interviewqa`, `core_interviewsession`.
* **Future Improvements**: Use WebSockets for streaming the LLM response character-by-character to the frontend.

### `POST /api/interview/end/`
* **Purpose**: Finalizes the session and computes total score.
* **Authentication**: `IsAuthenticated`
* **Business Logic**: Sums up scores from all `InterviewQA` records. Sets `status='completed'`, `completed_at=now()`.
* **DB Tables**: `core_interviewsession`.

---

## 5. Mock Tests API (`core`)

### `GET /api/tests/`
* **Purpose**: Lists available mock exams.
* **Authentication**: `IsAuthenticated`
* **Response Body**: `[{"id": 1, "name": "TCS Ninja Mock", "duration_minutes": 60, ...}]`
* **Frontend Caller**: `MockTestsPage.jsx`.
* **DB Tables**: `core_test`.

### `POST /api/tests/<id>/start/`
* **Purpose**: Begins a test session, returning the question payload.
* **Authentication**: `IsAuthenticated`
* **Response Body**: Returns the Test metadata and ALL associated questions (omitting correct answers). Creates an initial `TestAttempt` record with `started_at`.
* **Frontend Caller**: `MockTestsPage.jsx` (Test UI).
* **DB Tables**: `core_test`, `core_testattempt`, `core_question`.

### `POST /api/tests/submit/`
* **Purpose**: Evaluates an entire submitted mock test payload.
* **Authentication**: `IsAuthenticated`
* **Request Body**: `{"test_id": 1, "answers": {"q_10": "A", "q_11": "C", ...}}`
* **Response Body**: `{"score": 18, "total": 20}`
* **Business Logic**: 
  1. Iterates through submitted dictionary.
  2. Compares against DB `correct_answer`.
  3. Bulk creates `UserAnswer` records.
  4. Updates the `TestAttempt` with final `score` and `completed_at=now()`.
* **Frontend Caller**: `MockTestsPage.jsx` (Submit Test button).
* **DB Tables**: `core_testattempt`, `core_useranswer`, `core_question`.

---

## 6. Admin Operations API

### `GET /api/admin/overview/`
* **Purpose**: Initial payload for the Admin Dashboard.
* **Authentication**: `IsAuthenticated` + `IsAdminUser` (Staff check).
* **Response Body**: Aggregates counts of Users, Tracks, Questions, Tests, and recent platform activity.
* **Frontend Caller**: `AdminPage.jsx`.

### `DELETE /api/admin/topics/<id>/`
* **Purpose**: Safe deletion of a topic.
* **Authentication**: `IsAdminUser`
* **Business Logic**: Intercepts the DELETE command. If `UserAnswer` records are linked to questions within this topic, it blocks the hard delete and instead executes a soft-delete (`UPDATE core_topic SET is_active=False WHERE id=X`). This preserves historical student data.
* **Status Codes**: `204 No Content` (Deleted), `200 OK` (Soft Deleted).
* **Frontend Caller**: `AdminPage.jsx` (Drawer actions).
* **DB Tables**: `core_topic`, `core_question`, `core_useranswer`.
