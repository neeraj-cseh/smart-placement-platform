# Project Knowledge Base

## What Exists
- Project: Smart Placement / PrepSmart platform.
- Backend: Django + Django REST Framework app at `manage.py`, `config/`, `accounts/`, `core/`.
- Frontend: Vite React app at `frontend-react/`.
- Database: SQLite file `db.sqlite3`; Django settings also include `mysqlclient` dependency but configured database is SQLite in `config/settings.py`.
- Seed/data scripts: root `seed_*.py`, `rewrite_*.py`, `fix_*.py`, `scripts/`, `scratch/`, `test-artifacts/`.
- Existing generated documentation folders: `PrepSmart_Engineering_Knowledge_Base/`, `PrepSmart_Final_Project_Documentation/`.

## Backend Apps

### `config`
- What exists: Django project configuration.
- Where: `config/settings.py`, `config/urls.py`, `config/asgi.py`, `config/wsgi.py`.
- Connects to: includes `accounts.urls` at `/api/auth/`, `core.urls` at `/api/`, Django admin at `/admin/`.
- Authentication: `AUTH_USER_MODEL = accounts.User`; DRF JWT authentication via SimpleJWT.
- Middleware: Django standard middleware plus CORS middleware.
- Security: JWT auth; CORS configured in settings; `.env` loaded by `python-dotenv`.

### `accounts`
- What exists: custom user model, profile/settings/goals/streak auth APIs.
- Where: `accounts/models.py`, `accounts/serializers.py`, `accounts/views.py`, `accounts/urls.py`, `accounts/admin.py`.
- Connects to: `core.bootstrap.ensure_platform_catalog`, `core.bootstrap.ensure_user_preparation_data`, and core progress models for dashboard calculations.
- Models used: `User`, `UserProfile`, `DailyGoal`, `UserStreak`.
- Authentication: email/password login; SimpleJWT access/refresh token generation; logout attempts refresh-token blacklist.
- Permissions: public register/login/refresh; authenticated session/profile/settings/goals/streak/dashboard.
- Validation: password length and Django password validation; CGPA range 0-10; weekly goal hours 1-80; non-empty daily goal text.
- Error handling: returns 400 for missing credentials/validation errors, 401 invalid credentials/token, 403 admin dashboard access, 404 missing goal.
- Security: `LoginThrottle` rate `5/minute`; password stored through `set_password`; JWT returned to client.
- Known limitations: frontend calls `/api/auth/change-password/`, but no matching backend route exists.

### `core`
- What exists: learning path, prep journey, mock tests, analytics, admin content APIs, AI explanation/interview APIs, resume/passport/portfolio APIs, code execution/code lab APIs, contests, snippets.
- Where: `core/models.py`, `core/serializers.py`, `core/views.py`, `core/urls.py`, `core/bootstrap.py`, `core/services/judge_service.py`, `core/scheduler.py`, `core/management/commands/*.py`.
- Connects to: `accounts.User`; frontend API client calls `/api/...`; management commands seed/sync data.
- Models used: all `core.models` tables listed in Database Inventory.
- Permissions: most APIViews use `IsAuthenticated`; landing/health/public shared views use public access where coded; admin APIs check staff/superuser in views.
- Business logic: topic completion, quiz scoring, readiness/dashboard scoring, mock test attempts, company readiness, interview sessions, resume/passport/portfolio generation, code execution and judging, contest sync, snippets/bookmarks.
- Error handling: APIViews return DRF `Response` with 400/401/403/404/500 depending on validation, missing objects, permissions, execution errors.
- External services: Kontests API in `core/management/commands/sync_contests.py`; Groq client helper exists at bottom of `core/views.py` using `GROQ_API_KEY`.
- Known limitations: AI topic chat returns disabled system notice; global frontend assistant uses mock responses; contest leaderboard uses mock rankings; code execution uses local subprocess execution; memory usage is mocked in judge service.

## Models And Tables

### Accounts Models
- `accounts.User` -> table `accounts_user`: `id`, `password`, `last_login`, `is_superuser`, `email`, `name`, `is_active`, `is_staff`, `created_at`; M2M `groups`, `user_permissions`.
- `accounts.UserProfile` -> table `accounts_userprofile`: one-to-one `user`; branch/college/degree/graduation_year/cgpa/has_backlog/location/preferred_role/phone/URLs/headline/bio/skills/target_companies/weekly_goal_hours/timezone/notification/public fields.
- `accounts.DailyGoal` -> table `accounts_dailygoal`: FK `user`, `goal_text`, `completed`, `date`, `created_at`.
- `accounts.UserStreak` -> table `accounts_userstreak`: one-to-one `user`, `current_streak`, `longest_streak`, `last_active_date`.

### Core Models
- `Track` -> `core_track`: `name`, `description`, `created_at`.
- `Topic` -> `core_topic`: FK `track`, `name`, `slug`, `description`, `order`, `domain`, `interview_frequency`, `target_companies`, `why_it_matters`, `is_active`, `created_at`.
- `TopicDependency` -> `core_topicdependency`: FK `topic`, FK `prerequisite`.
- `TopicSection` -> `core_topicsection`: FK `topic`, `title`, `content_markdown`, `section_type`, `order`.
- `TopicVisualization` -> `core_topicvisualization`: one-to-one `topic`, `title`, `visualization_type`, `config_data`.
- `TopicRevision` -> `core_topicrevision`: one-to-one `topic`, `key_takeaways`, `cheat_sheet_markdown`.
- `UserTopicProgress` -> `core_usertopicprogress`: FK `user`, FK `topic`, `is_completed`, `completed_at`.
- `Question` -> `core_question`: FK `topic`, `question_text`, options A-D, `correct_answer`, `difficulty`, `explanation`, `created_at`.
- `UserAnswer` -> `core_useranswer`: FK `user`, FK `question`, `selected_answer`, `is_correct`, `created_at`.
- `Test` -> `core_test`: `name`, `description`, `duration_minutes`, `created_at`; M2M `topics`, `questions`.
- `TestAttempt` -> `core_testattempt`: FK `user`, FK `test`, `score`, `total_questions`, `started_at`, `completed_at`.
- `DailyPlanItem` -> `core_dailyplanitem`: FK `user`, title/detail/status/progress/tone/date/order/completion timestamps.
- `CompanyTarget` -> `core_companytarget`: FK `user`, `name`, `readiness_percentage`, `focus`, `tone`, `order`, `is_active`, timestamps.
- `RevisionQueueItem` -> `core_revisionqueueitem`: FK `user`, `title`, `cycle_label`, `duration_minutes`, `due_date`, `order`, `is_completed`, timestamps.
- `InterviewReadiness` -> `core_interviewreadiness`: FK `user`, `area`, `score`, `max_score`, `progress_percentage`, `order`, timestamps.
- `ActivityEvent` -> `core_activityevent`: FK `user`, `event_type`, `title`, `occurred_at`, `metadata`, `created_at`.
- `CodeSubmission` -> `core_codesubmission`: FK `user`, FK `problem`, `code`, `language`, `output`, `error_output`, `execution_time_ms`, `memory_kb`, `stdin`, `status`, `attempt_number`, `created_at`.
- `InterviewSession` -> `core_interviewsession`: FK `user`, `category`, `current_question_index`, `total_questions`, `status`, `score`, `max_score`, timestamps.
- `InterviewQA` -> `core_interviewqa`: FK `session`, `question`, `user_answer`, `ai_feedback`, `score`, `max_score`, `created_at`.
- `UserDraft` -> `core_userdraft`: FK `user`, FK `topic`, `exercise_id`, `content`, `updated_at`.
- `UserResume` -> `core_userresume`: one-to-one `user`, `file_name`, `uploaded_at`, `overall_score`, `ats_score`, `recruiter_score`, `analysis_data`.
- `UserPassport` -> `core_userpassport`: one-to-one `user`, scores/tier/data/public token/timestamps.
- `UserCertificate` -> `core_usercertificate`: FK `user`, skill/trust/readiness/certificate/hash/evidence/public fields.
- `UserProject` -> `core_userproject`: FK `user`, title/description/domain/tech_stack/difficulty/status/milestones/kanban/impact/evaluation/deploy/github/architecture/resume sync/timestamps.
- `UserPortfolio` -> `core_userportfolio`: one-to-one `user`, strength/recruiter/competitiveness/template/slug/public/analytics/copilot/timestamps.
- `CodingProblem` -> `core_codingproblem`: title/slug/difficulty/topics/companies/relevance/readiness/acceptance/function/description/constraints/examples/hints/starter/signature/timestamps.
- `TestCase` -> `core_testcase`: FK `problem`, `input_data`, `expected_output`, `is_hidden`, `order`.
- `CodingContest` -> `core_codingcontest`: title/description/start/end/duration/is_active/platform/external_url; M2M `problems`.
- `CodeSnippet` -> `core_codesnippet`: FK `user`, title/code/language/timestamps.
- `UserProblemBookmark` -> `core_userproblembookmark`: FK `user`, FK `problem`, `created_at`.

## API Inventory

### Auth APIs
- `POST /api/auth/register/` -> `accounts.views.RegisterView`.
- `POST /api/auth/login/` -> `LoginView`.
- `GET /api/auth/session/` -> `SessionView`.
- `POST /api/auth/token/refresh/` -> `RefreshTokenView`.
- `POST /api/auth/logout/` -> `LogoutView`.
- `GET|PUT /api/auth/profile/` -> `ProfileView`.
- `GET|PUT /api/auth/settings/` -> `AccountSettingsView`.
- `GET|POST /api/auth/goals/` -> `DailyGoalView`.
- `PUT /api/auth/goals/<pk>/` -> `DailyGoalUpdateView`.
- `GET /api/auth/streak/` -> `StreakView`.
- `GET /api/auth/dashboard/` -> `DashboardView`.
- `PUT /api/auth/change-password/` -> Not Implemented.

### Core APIs
- `GET /api/health/` -> `HealthView`.
- `GET /api/landing/` -> `LandingView`.
- `GET /api/learning-path/` -> `LearningPathView`.
- `GET /api/practice/` -> `PracticeDashboardView`.
- `GET /api/analytics/full/` -> `FullAnalyticsView`.
- `GET /api/analytics/topic-accuracy/` -> `TopicAccuracyView`.
- `GET /api/analytics/overall-performance/` -> `OverallPerformanceView`.
- `GET /api/analytics/dashboard/` -> `AnalyticsDashboardView`.
- `GET /api/companies/` -> `CompaniesView`.
- `PATCH /api/companies/<company_name>/` -> `CompanyTargetUpdateView`.
- `GET /api/companies/<company_name>/details/` -> `CompanyDetailAPIView`.
- `GET /api/tracks/` -> `TrackListView`.
- `GET /api/tracks/<track_id>/topics/` -> `TopicByTrackView`.
- `POST /api/topics/<topic_id>/complete/` -> `CompleteTopicView`.
- `PATCH /api/topics/<topic_id>/progress/` -> `TopicProgressUpdateView`.
- `GET /api/tracks/<track_id>/progress/` -> `TrackProgressView`.
- `GET /api/topics/<topic_id>/questions/` -> `QuestionByTopicView`.
- `POST /api/questions/<question_id>/submit/` -> `SubmitAnswerView`.
- `GET /api/weak-topics/` -> `WeakTopicView`.
- `GET /api/tests/` -> `TestListView`.
- `GET /api/tests/<test_id>/` -> `TestDetailView`.
- `POST /api/tests/<test_id>/start/` -> `StartTestView`.
- `POST /api/tests/submit/` -> `SubmitTestView`.
- `POST /api/ai/explain/` -> `AIExplanationView`.
- `POST /api/code/execute/` -> `CodeExecuteView`.
- `GET /api/code/workspace/` -> `CodeWorkspaceView`.
- `GET /api/code/submissions/` -> `CodeSubmissionListView`.
- `GET|POST /api/interview/config/` -> `InterviewConfigView`.
- `POST /api/interview/start/` -> `InterviewStartView`.
- `POST /api/interview/question/` -> `InterviewNextQuestionView`.
- `POST /api/interview/submit/` -> `InterviewSubmitAnswerView`.
- `POST /api/interview/end/` -> `InterviewEndView`.
- `GET /api/interview/history/` -> `InterviewHistoryView`.
- `GET /api/resume/` -> `ResumeOverviewView`.
- `GET /api/passport/` -> `PassportOverviewView`.
- `GET /api/passport/shared/<token>/` -> `PublicPassportView`.
- `GET /api/verification/` -> `VerificationDashboardView`.
- `GET /api/verification/shared/<token>/` -> `PublicCertificateView`.
- `GET /api/portfolio/` -> `PortfolioDashboardView`.
- `GET /api/portfolio/shared/<slug>/` -> `PublicPortfolioView`.
- `GET /api/code/dashboard/` -> `CodeLabDashboardView`.
- `GET /api/code/problems/` -> `ProblemListView`.
- `GET /api/code/problems/<slug>/` -> `ProblemDetailView`.
- `POST /api/code/problems/<slug>/run/` -> `CodeRunView`.
- `POST /api/code/problems/<slug>/submit/` -> `CodeSubmitView`.
- `GET /api/code/problems/<slug>/submissions/` -> `ProblemSubmissionListView`.
- `GET /api/code/problems/<slug>/editorial/` -> `ProblemEditorialView`.
- `POST /api/code/problems/<slug>/bookmark/` -> `ProblemBookmarkToggleView`.
- `POST /api/code/problems/<slug>/ai-mentor/` -> `AIMentorView`.
- `GET /api/code/contests/` -> `ContestListView`.
- `GET /api/code/contests/<contest_id>/leaderboard/` -> `ContestLeaderboardView`.
- `GET|POST /api/code/snippets/` -> `SnippetListView`.
- `GET|PUT|DELETE /api/code/snippets/<pk>/` -> `SnippetDetailView`.
- `GET /api/prep/current-topic/` -> `PrepCurrentTopicView`.
- `GET /api/prep/topic-journey/` -> `PrepTopicJourneyView`.
- `GET /api/prep/roadmaps/` -> `PrepRoadmapsView`.
- `GET /api/prep/milestones/` -> `PrepMilestonesView`.
- `POST /api/prep/complete-topic/` -> `PrepCompleteTopicView`.
- `GET /api/prep/topic/<slug>/` -> `PrepTopicDetailView`.
- `POST /api/prep/topic/<slug>/complete/` -> `PrepTopicCompleteView`.
- `GET|POST /api/prep/topic/<slug>/drafts/` -> `PrepTopicDraftView`.
- `POST /api/prep/topic/<slug>/quiz/submit/` -> `PrepTopicQuizSubmitView`.
- `GET /api/prep/topic/<slug>/ai-context/` -> `PrepTopicAIContextView`.
- `POST /api/prep/topic/<slug>/ai-chat/` -> `PrepTopicAIChatView`.
- `GET /api/problems/by-topic/<topic_id>/` -> `ProblemsByTopicView`.
- `GET /api/user/progress/` -> `UserProgressView`.

### Admin APIs
- `GET /api/admin/overview/` -> `AdminOverviewView`.
- `PATCH /api/admin/users/<user_id>/` -> `AdminUserUpdateView`.
- `GET|POST /api/admin/content/` -> `AdminContentView`.
- `GET|PATCH|DELETE /api/admin/tracks/<track_id>/` -> `AdminTrackDetailView`.
- `GET|PATCH|DELETE /api/admin/topics/<topic_id>/` -> `AdminTopicDetailView`.
- `GET|PATCH|DELETE /api/admin/questions/<question_id>/` -> `AdminQuestionDetailView`.
- `GET|PATCH|DELETE /api/admin/tests/<test_id>/` -> `AdminTestDetailView`.
- `GET|POST /api/admin/company-targets/` -> `AdminCompanyTargetView`.
- `GET|PATCH|DELETE /api/admin/company-targets/<target_id>/` -> `AdminCompanyTargetDetailView`.

## Frontend App

### Routing
- Router: `frontend-react/src/App.jsx`.
- Context providers: `ThemeProvider`, `AuthProvider`.
- Error boundary: `ErrorBoundary`.
- Global assistant: `AIAssistant`.
- Protected routes: redirect unauthenticated users to `/login`.
- Admin-only route: `/admin`, requires `user.is_admin`.
- Public routes: `/landing`, `/login`, `/signup`, `/portfolio/shared/:slug`, `/passport/shared/:token`.

### React Page Inventory
- `/` -> `DashboardPage` for students, `AdminPage` for admins, `LandingPage` for guests.
- `/landing` -> `LandingPage`.
- `/login` -> `AuthPage` login mode.
- `/signup` -> `AuthPage` signup mode.
- `/analytics` -> `AnalyticsPage`.
- `/prep/journey` -> `PrepPage`.
- `/prep/roadmaps` -> `LearningPathPage`.
- `/prep/milestones` -> `MockTestsPage`.
- `/prep/topic/:slug` -> `TopicStudyPage`.
- `/code-lab/arena` -> `ProblemArenaPage`.
- `/code-lab/arena/:slug` -> `ProblemSolvingPage`.
- `/code-lab/workspace` -> `CodingWorkspacePage`.
- `/code-lab/contests` -> `ContestHubPage`.
- `/ai/interview` -> `AIInterviewPage`.
- `/career/companies` -> `CompaniesPage`.
- `/career/companies/:name` -> `CompanyDetailPage`.
- `/profile/passport` -> `PassportPage`.
- `/profile/me` -> `ProfilePage`.
- `/settings` -> `SettingsPage`.
- `*` -> `NotFoundPage`.
- Standalone existing but not routed in `App.jsx`: `PracticePage`.

### Components
- Layout: `frontend-react/src/components/Layout.jsx`, `layout.css`.
- Ecosystem layouts: `components/ecosystems/EcosystemLayouts.jsx`.
- Error handling: `components/ErrorBoundary.jsx`.
- Code Lab: `components/CodeLab/AiMentorPane.jsx`, `ContestCard.jsx`.
- UI: `components/ui/Button.jsx`, `Card.jsx`, `Modal.jsx`, `Mermaid.jsx`, TS shadcn-style `button.tsx`, `card.tsx`, `badge.tsx`, `radial-orbital-timeline.tsx`, `demo.tsx`.
- Widgets: `components/widgets/index.jsx`.
- AI: `frontend-react/src/ai/AIAssistant.jsx`, `ai.css`.

### Contexts, Hooks, Stores, Utilities
- `AuthContext`: `frontend-react/src/contexts/AuthContext.jsx`; manages token session, login/register/logout/refetch.
- `ThemeContext`: `frontend-react/src/contexts/ThemeContext.jsx`; stores `theme` in localStorage and sets `data-theme`.
- `useApi`: `frontend-react/src/hooks/useApi.js`; fetch helper hook around `api.get`.
- Hook exports: `frontend-react/src/hooks/index.js`; includes copy-to-clipboard utilities.
- Stores: `frontend-react/src/stores/index.js`; Zustand UI/AI state.
- API client: `frontend-react/src/api/client.js`; base URL from `VITE_API_URL` or `http://127.0.0.1:8000/api`; JWT injection; refresh-token retry; 5xx/network retries.
- Utilities: `frontend-react/src/utils/index.js`, `frontend-react/src/lib/utils.ts`.
- Animation constants: `frontend-react/src/animations/motion.js`.

## Business Logic
- Dashboard readiness: `accounts.views.DashboardView` aggregates answers, tests, tracks, companies, readiness, activity.
- Topic completion: `core.views.CompleteTopicView`, `PrepCompleteTopicView`, `PrepTopicCompleteView`; writes `UserTopicProgress` and `ActivityEvent`.
- Quiz scoring: `SubmitAnswerView`, `PrepTopicQuizSubmitView`; compares selected answer against `correct_answer`; prep quiz passes at 60%.
- Mock tests: `StartTestView`, `SubmitTestView`; creates `TestAttempt`, scores submitted answers.
- Learning path: `LearningPathView`, `PrepTopicJourneyView`, `PrepRoadmapsView`, `PrepMilestonesView`; uses tracks/topics/progress/dependencies.
- Company readiness: `CompaniesView`, `CompanyTargetUpdateView`, `CompanyDetailAPIView`.
- Admin CRUD: `AdminContentView` plus detail views mutate tracks/topics/questions/tests/company targets.
- Interview: `InterviewStartView`, `InterviewNextQuestionView`, `InterviewSubmitAnswerView`, `InterviewEndView`; uses `InterviewSession` and `InterviewQA`.
- Resume/passport/certificates/portfolio: overview/shared views generate or return user-facing readiness artifacts.
- Code execution: `CodeExecuteView`, `CodeRunView`, `CodeSubmitView`, `core.services.judge_service.evaluate_submission`.
- Contest sync: `sync_contests` command fetches `https://kontests.net/api/v1/all`, filters supported platforms, falls back to generated contests on failure.

## Validation And Error Handling
- Serializer validation in `accounts/serializers.py`.
- API object lookup failures return 404.
- Missing required POST fields return 400.
- Invalid JWT refresh returns 401.
- Admin dashboard blocked for non-student dashboard use with 403.
- Frontend API client formats DRF field errors into messages.
- Frontend API client retries 5xx and network `TypeError` up to three times.
- ErrorBoundary renders fallback UI for React render errors.

## Security And Permissions
- JWT access tokens stored in browser `localStorage`.
- Refresh tokens stored in browser `localStorage`.
- Authenticated API requests use `Authorization: Bearer <token>`.
- Login throttle: 5 anonymous login attempts/minute.
- Code execution runs local subprocesses for Python/JavaScript/C++/Java with timeout; this is explicitly high-risk RCE surface.
- Admin frontend route requires `user.is_admin`; backend admin views enforce staff/superuser checks in `core/views.py`.
- Public sharing exists for passport, certificate verification, and portfolio by token/slug.

## Algorithms
- Percentage helpers clamp or round scores.
- Streak update increments if last active date was yesterday, holds if today, resets otherwise.
- Topic locking checks `TopicDependency` against completed `UserTopicProgress`.
- Prep quiz pass threshold: 60%.
- Code judging wraps user code with runner templates, executes test cases, compares JSON output to expected output, returns Accepted/Wrong Answer/Runtime Error/TLE.
- Contest sync filters durations greater than 43,200 minutes and deletes external contests ended more than 30 days ago.
- Frontend landing radar path computes polygon points with trigonometric angles.
- Radial orbital timeline computes circular node coordinates from angle and radius.

## Dependencies

### Python
- `asgiref==3.11.1`
- `Django==6.0.4`
- `django-cors-headers==4.9.0`
- `djangorestframework==3.17.1`
- `djangorestframework_simplejwt==5.5.1` / `djangorestframework-simplejwt==5.5.1`
- `mysqlclient==2.2.8`
- `PyJWT==2.12.1`
- `python-dotenv==1.2.2`
- `requests==2.33.1`
- `sqlparse==0.5.5`
- `tzdata==2026.2`
- Code imports also reference `apscheduler` and `groq`, but they are not listed in `requirements.txt`.

### Frontend Runtime
- `@monaco-editor/react`
- `@radix-ui/react-slot`
- `class-variance-authority`
- `decimal.js-light`
- `framer-motion`
- `lucide-react`
- `mermaid`
- `react`
- `react-dom`
- `react-markdown`
- `react-resizable-panels`
- `react-router-dom`
- `recharts`
- `rehype-katex`
- `remark-gfm`
- `remark-math`
- `zustand`

### Frontend Dev
- `@eslint/js`
- `@types/react`
- `@types/react-dom`
- `@vitejs/plugin-react`
- `eslint`
- `eslint-plugin-react-hooks`
- `eslint-plugin-react-refresh`
- `globals`
- `vite`

## Performance Optimizations
- Frontend pages are lazy-loaded with `React.lazy` and `Suspense` in `App.jsx`.
- API client retries server/network failures.
- Backend uses `select_related`, `prefetch_related`, aggregations, and `values()` in several dashboard/admin/list endpoints.
- Code execution has timeout enforcement.
- APScheduler can sync contests every 12 hours.

## Known Limitations
- `/api/auth/change-password/` is called by `SettingsPage.jsx` but not implemented in backend URLs/views.
- `PrepTopicAIChatView` returns a disabled LLM notice instead of live AI chat.
- `AIAssistant.jsx` generates mock local responses.
- Contest leaderboard data is mock-generated in `ContestLeaderboardView`.
- Judge service reports mocked memory usage.
- Code execution is local subprocess based and not sandboxed at the platform boundary.
- `apscheduler` and `groq` are imported but absent from listed Python requirements.
- `PracticePage.jsx` exists but is not routed in `App.jsx`.
- Duplicate URL entries exist for `/api/interview/end/` and `/api/interview/history/` in `core/urls.py`.

## Future TODOs Already Present
- No explicit `TODO` or `FIXME` markers were found in implementation files.
- Present future/placeholder text in code: AI topic chat disabled until LLM key integration; coding problems for some non-DSA topic screens show "coming soon"; frontend assistant uses mock responses.

## Complete Folder Tree
```text
.
├── accounts/
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/0001_initial.py ... 0007_alter_dailygoal_options_alter_dailygoal_user_and_more.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── admin.py
│   ├── apps.py
│   ├── bootstrap.py
│   ├── interview_data.py
│   ├── management/commands/seed_platform_data.py
│   ├── management/commands/sync_contests.py
│   ├── migrations/0001_initial.py ... 0026_userproblembookmark.py
│   ├── models.py
│   ├── scheduler.py
│   ├── serializers.py
│   ├── services/judge_service.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── frontend-react/
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── eslint.config.js
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── index.css
│       ├── ai/AIAssistant.jsx
│       ├── ai/ai.css
│       ├── animations/motion.js
│       ├── api/client.js
│       ├── components/
│       ├── contexts/AuthContext.jsx
│       ├── contexts/ThemeContext.jsx
│       ├── hooks/
│       ├── lib/utils.ts
│       ├── pages/
│       ├── stores/index.js
│       ├── theme/
│       └── utils/index.js
├── scripts/
├── scratch/
├── test-artifacts/
├── PrepSmart_Engineering_Knowledge_Base/
├── PrepSmart_Final_Project_Documentation/
├── .env
├── .gitignore
├── db.sqlite3
├── django.log
├── manage.py
├── README.md
├── requirements.txt
├── requirements_fixed.txt
├── seed_*.py
├── rewrite_*.py
├── fix_*.py
└── PROJECT_KNOWLEDGE_BASE.md
```

## Complete Database Inventory
- Tables: `accounts_user`, `accounts_userprofile`, `accounts_dailygoal`, `accounts_userstreak`, `core_track`, `core_topic`, `core_topicdependency`, `core_topicsection`, `core_topicvisualization`, `core_topicrevision`, `core_usertopicprogress`, `core_question`, `core_useranswer`, `core_test`, `core_testattempt`, `core_dailyplanitem`, `core_companytarget`, `core_revisionqueueitem`, `core_interviewreadiness`, `core_activityevent`, `core_codesubmission`, `core_interviewsession`, `core_interviewqa`, `core_userdraft`, `core_userresume`, `core_userpassport`, `core_usercertificate`, `core_userproject`, `core_userportfolio`, `core_codingproblem`, `core_testcase`, `core_codingcontest`, `core_codesnippet`, `core_userproblembookmark`.
- Django auth/group/session/token blacklist tables also exist through installed Django and SimpleJWT apps.

## Complete Frontend Page Inventory
- `AdminPage.jsx`, `AIInterviewPage.jsx`, `AnalyticsPage.jsx`, `AuthPage.jsx`, `CodingWorkspacePage.jsx`, `CompaniesPage.jsx`, `CompanyDetailPage.jsx`, `ContestHubPage.jsx`, `DashboardPage.jsx`, `LandingPage.jsx`, `LearningPathPage.jsx`, `MockTestsPage.jsx`, `NotFoundPage.jsx`, `PassportPage.jsx`, `PortfolioPage.jsx`, `PracticePage.jsx`, `PrepPage.jsx`, `ProblemArenaPage.jsx`, `ProblemSolvingPage.jsx`, `ProfilePage.jsx`, `SettingsPage.jsx`, `SharedPassportPage.jsx`, `SharedPortfolioPage.jsx`, `TopicStudyPage.jsx`.

## Complete Backend App Inventory
- Django apps present: `accounts`, `core`, `config`.
- Django management commands: `seed_platform_data`, `sync_contests`.
- Backend services: `core/services/judge_service.py`.
- Scheduler: `core/scheduler.py`.
- Bootstrap/seed data: `core/bootstrap.py`, root seed scripts.

## Complete Dependency Inventory
- Backend dependencies: see Python dependency list above.
- Frontend dependencies: see frontend runtime/dev dependency lists above.
- Browser/local external tools implied: Python, Node.js, npm, Vite, SQLite, local compilers/runtimes for code execution.

## Complete Screenshot Checklist
- Landing: `/landing`.
- Login: `/login`.
- Signup: `/signup`.
- Student dashboard: `/`.
- Admin dashboard: `/admin`.
- Analytics: `/analytics`.
- Prep journey: `/prep/journey`.
- Prep roadmaps: `/prep/roadmaps`.
- Prep milestones/mock tests: `/prep/milestones`.
- Topic study: `/prep/topic/:slug`.
- Code arena: `/code-lab/arena`.
- Problem solving workspace: `/code-lab/arena/:slug`.
- Standalone code workspace: `/code-lab/workspace`.
- Contest hub: `/code-lab/contests`.
- AI interview: `/ai/interview`.
- Companies list: `/career/companies`.
- Company detail: `/career/companies/:name`.
- Passport: `/profile/passport`.
- Public passport: `/passport/shared/:token`.
- Profile editor: `/profile/me`.
- Portfolio: frontend page exists but private route not wired in `App.jsx`; public route `/portfolio/shared/:slug`.
- Public portfolio: `/portfolio/shared/:slug`.
- Settings: `/settings`.
- Not found: unmatched route.
- Practice page: screenshot only if routed manually; not wired in `App.jsx`.

## Complete Diagram Checklist
- Backend app/module diagram: `config`, `accounts`, `core`, management commands, scheduler, services.
- ER diagram from all Django models and FK/M2M relationships.
- Auth flow: register/login/session/refresh/logout/profile/settings.
- Frontend route tree from `App.jsx`.
- API-to-page map from React pages to backend endpoints.
- Learning path/topic dependency diagram from `Track`, `Topic`, `TopicDependency`.
- Mock test flow: list/start/submit/results.
- Code execution/judge flow: editor/run/submit/submission/test cases.
- AI interview session state diagram.
- Passport/certificate/portfolio public sharing flow.
- Admin content CRUD flow.
- Contest sync flow: scheduler/management command/Kontests API/database.
