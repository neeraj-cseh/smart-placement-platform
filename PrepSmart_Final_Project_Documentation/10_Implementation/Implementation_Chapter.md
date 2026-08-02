# Complete Implementation Document - PrepSmart

This document details the exact implementation of every module in the PrepSmart platform, written from the perspective of the Lead Software Architect. It serves as the Implementation Chapter of the software engineering thesis.

---

## 1. Authentication
* **Objective**: Securely identify and authorize users across the platform without maintaining server-side session state.
* **Design approach**: Token-based architecture utilizing JSON Web Tokens (JWT) for stateless communication.
* **Frontend implementation**: The `<AuthProvider>` React Context wraps the application. A `login()` function sends credentials and saves `access` and `refresh` tokens to `localStorage`.
* **Backend implementation**: Django overrides `AbstractBaseUser` using `email` as the primary key. `djangorestframework-simplejwt` provides token generation.
* **Database interaction**: Reads/Writes the `accounts_user` table. 
* **APIs involved**: `POST /api/auth/login/`, `POST /api/auth/register/`.
* **Business logic**: Hashes passwords using PBKDF2. 
* **Validation**: DRF serializers enforce minimum password length (8 characters).
* **Authentication**: `AllowAny` for ingress routes.
* **Error handling**: Returns `401 Unauthorized` for bad credentials. Frontend traps this and renders a red toast notification.
* **State management**: `user` state stored in Context, preventing redundant fetches.
* **Performance optimization**: JWT eliminates DB lookups for every authenticated request (only validates signature).
* **Security considerations**: Tokens are vulnerable to XSS; mitigating by enforcing strict React escaping and setting `X-Frame-Options: DENY`.
* **Future improvements**: Transition tokens from `localStorage` to `HttpOnly` cookies.

## 2. User Profile
* **Objective**: Maintain extended biographical and academic metadata for students.
* **Design approach**: One-to-One relational mapping decoupling core auth from heavy metadata.
* **Frontend implementation**: `ProfilePage.jsx` renders controlled forms.
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
* **Security considerations**: Read-only endpoint.
* **Future improvements**: Redis caching for 1 hour to reduce DB load.

## 4. Daily Goals
* **Objective**: Allow users to set micro-tasks for the current day.
* **Design approach**: Simple CRUD tied strictly to `date.today()`.
* **Frontend implementation**: A checklist widget on the Dashboard with optimistic UI updates.
* **Backend implementation**: `DailyGoal` model filtering strictly by `user` and `date`.
* **Database interaction**: `accounts_dailygoal`.
* **APIs involved**: `GET/POST /api/auth/goals/`, `PUT /api/auth/goals/<id>/`.
* **Business logic**: A new goal implicitly triggers the Streak Engine.
* **Validation**: String length constraints.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: `404 Not Found` if a user edits another's goal.
* **State management**: Array state mapped to list items.
* **Performance optimization**: Indexed by `date`.
* **Security considerations**: Enforced `user=request.user` filtering.
* **Future improvements**: Auto-rollover uncompleted goals.

## 5. Streak System
* **Objective**: Gamify preparation to increase daily retention.
* **Design approach**: Lazy evaluation executed during dashboard/goal interactions.
* **Frontend implementation**: Visual flame icon on the dashboard.
* **Backend implementation**: `UserStreak` model tracking `current_streak` and `longest_streak`.
* **Database interaction**: `accounts_userstreak`.
* **APIs involved**: Embedded in `/api/auth/goals/` and `/api/auth/streak/`.
* **Business logic**: If `last_active_date == today - 1`, increment. If older, reset to 1.
* **Validation**: Internal date math only.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Automatic recreation via `get_or_create` if missing.
* **State management**: Handled by the Dashboard payload.
* **Performance optimization**: Eliminates cron jobs by computing streaks lazily.
* **Security considerations**: Tamper-proof as computation happens purely server-side.
* **Future improvements**: "Streak Freeze" items.

## 6. Learning Paths (Tracks)
* **Objective**: Organize curriculum into broad domains (e.g., DSA).
* **Design approach**: Top-level relational hierarchy.
* **Frontend implementation**: `LearningPathPage.jsx` grid layouts.
* **Backend implementation**: `Track` model.
* **Database interaction**: `core_track`.
* **APIs involved**: `GET /api/tracks/`.
* **Business logic**: Aggregates completion percentage of child topics.
* **Validation**: Unique names.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Standard 500 traps.
* **State management**: Local component fetching.
* **Performance optimization**: `.prefetch_related('topics')` avoids N+1 queries.
* **Security considerations**: Read-only for students.
* **Future improvements**: Dynamic generation of tracks based on user skills.

## 7. Topics
* **Objective**: Micro-learning concepts within a Track.
* **Design approach**: Sequential, prerequisites-aware nodes.
* **Frontend implementation**: Sidebar navigation in `TopicStudyPage.jsx`.
* **Backend implementation**: `Topic` model linked to `Track`.
* **Database interaction**: `core_topic`.
* **APIs involved**: `GET /api/tracks/<id>/topics/`.
* **Business logic**: Joins with `UserTopicProgress` to output boolean completion status.
* **Validation**: Slug uniqueness.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: `404` for invalid slugs.
* **State management**: URL params drive the current active topic.
* **Performance optimization**: Ordered by sequence at DB level.
* **Security considerations**: Admin-only creation.
* **Future improvements**: Graph-based prerequisite blocking.

## 8. Topic Sections
* **Objective**: Deliver markdown content teaching the topic.
* **Design approach**: Decoupled from `Topic` to allow infinite vertical content sections (Overview, Learn, Guided).
* **Frontend implementation**: `react-markdown` rendering text.
* **Backend implementation**: `TopicSection` model with `order`.
* **Database interaction**: `core_topicsection`.
* **APIs involved**: Nested in Topic serializers.
* **Business logic**: Ordered retrieval.
* **Validation**: HTML sanitation.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Safe fallbacks for missing sections.
* **State management**: Parent Topic state.
* **Performance optimization**: Pre-rendered via React.
* **Security considerations**: XSS mitigation via markdown sanitizers on the frontend.
* **Future improvements**: Video embeds.

## 9. Interactive Visualizations
* **Objective**: Teach complex algorithms visually (e.g., Sliding Window).
* **Design approach**: React component mapping driven by backend strings.
* **Frontend implementation**: A mapping dictionary in React (e.g., `if type === 'sliding-window' render <SlidingWindow/>`).
* **Backend implementation**: `TopicVisualization` model containing `config_data` JSON.
* **Database interaction**: `core_topicvisualization`.
* **APIs involved**: Nested in Topic.
* **Business logic**: Backend dictates *what* visualization to render, frontend executes the logic.
* **Validation**: JSON Schema validation.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Fallback UI if component is missing.
* **State management**: Complex internal React state (pointers, arrays) per visualization.
* **Performance optimization**: Isolated re-renders via `React.memo`.
* **Security considerations**: None (purely visual).
* **Future improvements**: User-controlled step-by-step debuggers.

## 10. Progress Tracking
* **Objective**: Track completion of topics.
* **Design approach**: Explicit mapping table.
* **Frontend implementation**: "Mark as Complete" button.
* **Backend implementation**: `UserTopicProgress` model.
* **Database interaction**: `core_usertopicprogress`.
* **APIs involved**: `POST /api/topics/<id>/complete/`.
* **Business logic**: Sets `is_completed=True`, timestamps `completed_at`.
* **Validation**: Validates topic exists.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Ignores duplicates via `UniqueConstraint`.
* **State management**: Updates sidebar UI context.
* **Performance optimization**: Database indexing on `(user, is_completed)`.
* **Security considerations**: Validates user owns the progress.
* **Future improvements**: Auto-complete upon finishing MCQs.

## 11. Practice Questions
* **Objective**: Provide MCQ assessments per topic.
* **Design approach**: Client evaluates against server truth.
* **Frontend implementation**: Paginating through array of questions in `PracticePage.jsx`.
* **Backend implementation**: `Question` and `UserAnswer` models.
* **Database interaction**: `core_question`, `core_useranswer`.
* **APIs involved**: `GET /api/topics/<id>/questions/`, `POST /api/questions/<id>/submit/`.
* **Business logic**: Backend explicitly omits `correct_answer` in the GET payload. POST evaluates the answer and creates `UserAnswer` history.
* **Validation**: Checks valid option choices (A, B, C, D).
* **Authentication**: `IsAuthenticated`.
* **Error handling**: `400` for invalid options.
* **State management**: Maintains `selectedOption` and `isCorrect` locally per question.
* **Performance optimization**: Bulk writes not needed (one by one).
* **Security considerations**: Anti-cheat architecture (answers hidden on server).
* **Future improvements**: Spaced repetition algorithms.

## 12. Mock Tests
* **Objective**: High-stakes timed environments spanning multiple topics.
* **Design approach**: Server-side test definitions pooling questions via M2M relationships.
* **Frontend implementation**: Strict `useEffect` countdown timer. 
* **Backend implementation**: `Test` and `TestAttempt` models.
* **Database interaction**: `core_test`, `core_testattempt`.
* **APIs involved**: `POST /api/tests/<id>/start/`, `POST /api/tests/submit/`.
* **Business logic**: Aggregates all submitted answers in one payload, grades them sequentially, and computes the final `score`.
* **Validation**: Timer validation (backend ensures test isn't submitted 2 hours late).
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Transaction rollbacks if midway failure.
* **State management**: React Context tracks active test globally to prevent accidental navigation.
* **Performance optimization**: `bulk_create` for `UserAnswer` to avoid hitting the DB 50 times.
* **Security considerations**: Disables copy/paste in UI.
* **Future improvements**: Tab-switch detection (proctoring).

## 13. Code Lab
* **Objective**: Provide an algorithmic coding arena.
* **Design approach**: Decoupled problem definitions and code execution.
* **Frontend implementation**: Split-pane UI using Monaco Editor.
* **Backend implementation**: `CodingProblem` storing boilerplate logic.
* **Database interaction**: `core_codingproblem`.
* **APIs involved**: `GET /api/code/problems/`.
* **Business logic**: Surfaces problems by difficulty.
* **Validation**: None.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Standard 404s.
* **State management**: Editor code is debounced and stored in local state.
* **Performance optimization**: Lazy loading Monaco Editor.
* **Security considerations**: None for viewing problems.
* **Future improvements**: Multi-language boilerplate generation.

## 14. Code Execution Engine
* **Objective**: Safely execute user code and compare against hidden test cases.
* **Design approach**: Isolated execution sandbox.
* **Frontend implementation**: Displays stdout/stderr in a mock terminal UI.
* **Backend implementation**: `CodeExecuteView`.
* **Database interaction**: Queries `core_testcase`.
* **APIs involved**: `POST /api/code/problems/<slug>/submit/`.
* **Business logic**: Pipes `input_data` to `stdin`. Captures stdout. Trims whitespace. Compares to `expected_output`. 
* **Validation**: Throttled to 10 requests/hour to prevent CPU exhaustion.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Traps `TimeoutError` returning "TLE".
* **State management**: Loading spinners block the UI.
* **Performance optimization**: Short-circuits loop immediately if one test case fails.
* **Security considerations**: **Critical**. Currently uses `subprocess`. High risk of arbitrary code execution (e.g., `os.system("rm -rf /")`). 
* **Future improvements**: **Mandatory transition** to ephemeral Docker containers utilizing restricted networking and memory limits (cgroups).

## 15. Submission History
* **Objective**: Ledger of user code attempts.
* **Design approach**: Write-heavy historical logging.
* **Frontend implementation**: Table inside Code Lab showing "Accepted" or "Wrong Answer".
* **Backend implementation**: `CodeSubmission` model.
* **Database interaction**: `core_codesubmission`.
* **APIs involved**: `GET /api/code/problems/<slug>/submissions/`.
* **Business logic**: Sorts chronologically.
* **Validation**: None.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Pagination limits.
* **State management**: Fetched on tab click.
* **Performance optimization**: Indexed by `(user, created_at)`.
* **Security considerations**: Enforced user isolation.
* **Future improvements**: Code diffing between attempts.

## 16. AI Interview Module
* **Objective**: Dynamic mock interviews with AI grading.
* **Design approach**: Backend acts as a prompt-engineering proxy to an LLM provider (OpenAI/Gemini).
* **Frontend implementation**: Chat interface mimicking iMessage.
* **Backend implementation**: `InterviewSession` (state) and `InterviewQA` (history).
* **Database interaction**: `core_interviewsession`.
* **APIs involved**: `POST /api/interview/start/`, `/api/interview/submit/`.
* **Business logic**: Formats a strict system prompt instructing the LLM to output a JSON string containing `score` and `feedback`. Parses the JSON.
* **Validation**: Try/Catch JSON parsing.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Fallback if LLM times out (`504 Gateway Timeout`).
* **State management**: Arrays of messages in React.
* **Performance optimization**: Limiting context window to the last 3 questions to reduce token costs.
* **Security considerations**: API Keys securely stored in backend `.env`, never exposed to frontend. Prompt injection mitigations required.
* **Future improvements**: WebSockets for streaming text generation.

## 17. Company Readiness
* **Objective**: Measure preparation against specific targets (e.g., Google).
* **Design approach**: Simple tracking model overriding readiness scores.
* **Frontend implementation**: Modals to add companies from a Catalog.
* **Backend implementation**: `CompanyTarget`.
* **Database interaction**: `core_companytarget`.
* **APIs involved**: `PATCH /api/companies/<name>/`.
* **Business logic**: Readiness is a composite of specific topic scores deemed relevant to that company (e.g., Graph algorithms for Google).
* **Validation**: Company name must exist in predefined catalog.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: 404 for unknown companies.
* **State management**: Dashboard context.
* **Performance optimization**: Read directly in Dashboard.
* **Security considerations**: Standard.
* **Future improvements**: Automated dynamic adjustment of readiness based on daily metrics.

## 18. Analytics
* **Objective**: Deep insights into topic accuracy.
* **Design approach**: Dedicated endpoints for complex data slicing.
* **Frontend implementation**: Radar charts utilizing `recharts`.
* **Backend implementation**: `TopicAccuracyView`.
* **Database interaction**: Complex `GROUP BY` SQL logic via Django ORM.
* **APIs involved**: `GET /api/analytics/full/`.
* **Business logic**: Maps total attempts vs correct attempts per topic.
* **Validation**: None.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Zero-division protections.
* **State management**: Cached payload.
* **Performance optimization**: Aggregation pushed to MySQL.
* **Security considerations**: Isolated per user.
* **Future improvements**: Percentile rankings against peers.

## 19. Passport
* **Objective**: A digital resume representing employability.
* **Design approach**: Aggregation of all platform scores into a 0-100 metric.
* **Frontend implementation**: `PassportPage.jsx` with a "Share" toggle generating a public URL.
* **Backend implementation**: `UserPassport` model with a unique `public_token`.
* **Database interaction**: `core_userpassport`.
* **APIs involved**: `GET /api/passport/`, `GET /api/passport/shared/<token>/`.
* **Business logic**: Computes Employability Score, Competency Score.
* **Validation**: Read-only computations.
* **Authentication**: Authenticated for owner, Unauthenticated (AllowAny) for `/shared/`.
* **Error handling**: 404 for bad tokens.
* **State management**: Local state.
* **Performance optimization**: Pre-calculated nightly (eventually).
* **Security considerations**: Shared token acts as a revocable capability URL.
* **Future improvements**: PDF Export.

## 20. Portfolio
* **Objective**: Track user projects.
* **Design approach**: Decoupled from Passport for heavy JSON storage.
* **Frontend implementation**: Grid of project cards.
* **Backend implementation**: `UserPortfolio`, `UserProject`.
* **Database interaction**: `core_userproject`.
* **APIs involved**: `GET /api/portfolio/`.
* **Business logic**: Allows adding tech stacks and deployment URLs.
* **Validation**: URL validators.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: Standard DB constraints.
* **State management**: Standard list management.
* **Performance optimization**: JSON fields for unstructured Kanban data.
* **Security considerations**: Sanitization of markdown inputs.
* **Future improvements**: Auto-syncing with GitHub APIs.

## 21. Admin Portal
* **Objective**: CRUD management for staff.
* **Design approach**: Specialized React views shielded by RBAC.
* **Frontend implementation**: `AdminPage.jsx` using Slide-Over Drawers to maintain context.
* **Backend implementation**: DRF views checking `is_staff`.
* **Database interaction**: Access to all tables.
* **APIs involved**: `GET /api/admin/overview/`, `DELETE /api/admin/topics/<id>/`.
* **Business logic**: "Safe Deletions" - if a Topic has UserAnswers, the `DELETE` is intercepted and transformed into a soft-delete (`is_active=False`).
* **Validation**: High strictness on referential integrity.
* **Authentication**: `IsAdminUser`.
* **Error handling**: Returns constraints errors beautifully formatted.
* **State management**: Complex list state mapped to Drawer editors.
* **Performance optimization**: Paginated tables.
* **Security considerations**: Superuser protection.
* **Future improvements**: Audit logs for admin actions.

## 22. Settings
* **Objective**: Manage user preferences (timezone, notifications).
* **Design approach**: Extends the UserProfile API.
* **Frontend implementation**: Toggles in `SettingsPage.jsx`.
* **Backend implementation**: Bound to `AccountSettingsSerializer`.
* **Database interaction**: `accounts_userprofile`.
* **APIs involved**: `GET/PUT /api/auth/settings/`.
* **Business logic**: Simple boolean toggles.
* **Validation**: Boolean type checks.
* **Authentication**: `IsAuthenticated`.
* **Error handling**: 400 Bad Request.
* **State management**: Local form state.
* **Performance optimization**: Instant UI updates.
* **Security considerations**: None.
* **Future improvements**: Password resets.

## 23. Notifications
* **Objective**: Alerts for test completions or streaks.
* **Design approach**: Toast-based UI notifications.
* **Frontend implementation**: React Toaster library.
* **Backend implementation**: Not strictly modelled yet (relies on email booleans in settings).
* **Future improvements**: Implementing Celery + Redis for email dispatches.

## 24. Theme Management
* **Objective**: Toggle Light/Dark mode.
* **Design approach**: Pure CSS utilizing CSS Custom Variables (Properties).
* **Frontend implementation**: `ThemeContext.jsx` injects a `data-theme="dark"` attribute to the `<html>` root. `index.css` scopes `--bg-primary` variables based on this attribute.
* **Backend implementation**: None (Client-side only).
* **Performance optimization**: Zero-cost repaints via CSS variables.

## 25. Search
* **Objective**: Finding specific topics or users (Admin).
* **Design approach**: Client-side filtering for small datasets; DB text queries for Admin.
* **Frontend implementation**: Controlled input mapping to a `.filter()` array method.
* **Backend implementation**: Django `icontains` ORM lookups.
* **Performance optimization**: Debounced typing delays (300ms) before filtering.

## 26. Routing
* **Objective**: Seamless SPA navigation.
* **Design approach**: Nested Router DOM logic dividing Ecosystems (`/prep`, `/code-lab`).
* **Frontend implementation**: `App.jsx` holding `<Routes>`.
* **Performance optimization**: Route-level code splitting via `React.lazy()` and `<Suspense>`, ensuring Monaco Editor doesn't load on the Dashboard.

## 27. Protected Routes
* **Objective**: Block unauthorized access.
* **Design approach**: Higher-Order Component (`<ProtectedRoute>`).
* **Frontend implementation**: Intercepts render; if `AuthContext` user is null, returns `<Navigate to="/login" replace />`.
* **Security considerations**: Standard SPA protection; real security is enforced by backend API returning 401s regardless of frontend bypasses.

## 28. API Client
* **Objective**: Centralized network communication.
* **Design approach**: Custom `apiFetch` wrapper.
* **Frontend implementation**: `api/client.js`. Injects Bearer token.
* **Business logic**: Contains the auto-refresh logic interception for 401 errors.
* **Performance optimization**: Built-in exponential backoff retries for 5xx server errors.

## 29. Error Handling
* **Objective**: Graceful failure recovery.
* **Design approach**: Global React Error Boundaries.
* **Frontend implementation**: `<ErrorBoundary>` catches render crashes. `formatApiError()` in `client.js` flattens nested DRF validation dictionaries into human-readable strings.
* **Backend implementation**: DRF handles exception formatting.

## 30. Logging
* **Objective**: Server-side telemetry.
* **Design approach**: Python `logging` library.
* **Backend implementation**: `settings.py` configures a `StreamHandler` (console) and `FileHandler` (`django.log`).
* **Business logic**: Logs critical token refresh errors and 500 crashes.
* **Future improvements**: ELK stack (Elasticsearch, Logstash, Kibana) integration.

## 31. Performance Optimizations
* **Frontend**: Lazy loading routes, optimistic UI updates, debouncing inputs.
* **Backend**: `select_related()` and `prefetch_related()` aggressively used in `DashboardView` to solve N+1 query overheads.
* **Database**: Explicit indexing (`Index(fields=['user', '-created_at'])`).

## 32. Security
* **Authentication**: JWT is inherently stateless; signed with a secure `SECRET_KEY`.
* **Data Privacy**: All APIs strictly filter by `user=request.user` to prevent IDOR (Insecure Direct Object Reference).
* **Vulnerabilities**: The local `subprocess` execution for the Code Lab is the highest security risk (RCE vulnerable) and must be sandboxed.

## 33. Deployment Architecture
* **Frontend**: Built via `vite build`, served as static HTML/JS/CSS via Nginx.
* **Backend**: Gunicorn (WSGI) application server running Django, proxied behind Nginx.
* **Database**: Managed MySQL instance.
* **Future improvements**: Containerizing via Docker and deploying to AWS ECS.

## 34. Folder Structure
* Domain-driven design. Django Apps are split by functional domains (`accounts`, `core`). React `src` is split by function (`components`, `pages`, `contexts`).

## 35. Project Workflow
* **Code Cycle**: Feature development starts in React -> Requires new endpoint -> Django Model created -> ViewSet wired -> Axios client maps data to state.

## 36. Data Flow
* User Input -> React State -> API Client -> DRF Serializer Validation -> Django ORM -> MySQL -> ORM Response -> Serialized JSON -> React UI Repaint.

## 37. Complete Request Lifecycle
* Example: Code Submission. 
  1. User hits Run. 2. Axios POST. 3. Gunicorn ingress. 4. DRF Auth Middleware checks JWT. 5. Serializer validates syntax. 6. View triggers execution. 7. Returns 200 OK. 8. React clears loading spinner.

## 38. Module Dependencies
* `core` heavily depends on `accounts.User`. The Dashboard depends on almost every table in the database.

## 39. Design Decisions
* **Monolith vs Microservices**: Chose Django Monolith to leverage the immense power of the ORM for relational data (Students -> Tests -> Topics), which is painful in microservices.
* **Vanilla CSS**: Chose over Tailwind to maintain strict architectural control over CSS custom variables for dynamic, flawless dark mode.

## 40. Challenges Faced
* **Complex Aggregations**: Calculating the Readiness score across 5 different tables without causing severe database load. Resolved by relying on database-level `.annotate` rather than Python list comprehensions.
* **Code Execution**: Capturing stdout safely without hanging the main server thread.

## 41. Optimizations Performed
* Migrated from Create-React-App to Vite for 10x faster hot-reloading.
* Applied `db_index=True` on high-traffic columns (`is_correct`).

## 42. Future Architecture
* **Phase 2**: Implement Celery background tasks for AI processing and heavy analytics.
* **Phase 3**: Migrate the code execution engine to an AWS Lambda or Docker Swarm environment to eliminate local server RCE vulnerabilities.
* **Phase 4**: WebSockets (Django Channels) for real-time collaborative coding mock interviews.
