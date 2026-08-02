# Project Testing Matrix

## Source Coverage

| Area | Source files |
|---|---|
| Backend routes | `config/urls.py`, `accounts/urls.py`, `core/urls.py` |
| Backend models | `accounts/models.py`, `core/models.py` |
| Backend serializers | `accounts/serializers.py`, `core/serializers.py` |
| Backend views/business logic | `accounts/views.py`, `core/views.py`, `core/bootstrap.py`, `core/services/judge_service.py` |
| Frontend routes/pages | `frontend-react/src/App.jsx`, `frontend-react/src/pages/*` |
| Frontend API callers | `frontend-react/src/api/client.js`, `frontend-react/src/contexts/AuthContext.jsx`, `frontend-react/src/hooks/useApi.js`, routed pages |
| Current automated tests | `accounts/tests.py` empty, `core/tests.py` empty |
| Existing ad-hoc scripts | `test-artifacts/test_execution.py`, `test-artifacts/test_groq.py`, `test-artifacts/test_lc.py`, `test-artifacts/test_llc.py`, `test-artifacts/test_piston.py`, `test-artifacts/test_syntax.py` |

## Unit Test Matrix

| ID | Unit | File | Test case | Inputs / setup | Expected result |
|---|---|---|---|---|---|
| UT-001 | `UserManager.create_user` | `accounts/models.py` | Reject missing email | `email=""` | Raises `ValueError("Email is required")` |
| UT-002 | `UserManager.create_user` | `accounts/models.py` | Normalize email and hash password | Mixed-case email, password | Saved user email normalized; password not stored raw |
| UT-003 | `UserManager.create_superuser` | `accounts/models.py` | Set admin flags | Valid email/password/name | `is_staff=True`, `is_superuser=True` |
| UT-004 | `UserProfile.cgpa` validators | `accounts/models.py` | Reject CGPA below range | `cgpa=-1` + `full_clean()` | Validation error |
| UT-005 | `UserProfile.cgpa` validators | `accounts/models.py` | Reject CGPA above range | `cgpa=11` + `full_clean()` | Validation error |
| UT-006 | `RegisterSerializer.validate_password` | `accounts/serializers.py` | Reject password shorter than 8 chars | `password="short"` | Serializer invalid |
| UT-007 | `RegisterSerializer.validate_cgpa` | `accounts/serializers.py` | Reject CGPA outside 0-10 | `cgpa=11` | Serializer invalid |
| UT-008 | `RegisterSerializer.create` | `accounts/serializers.py` | Create user and optional profile data | Valid auth + profile fields | User created; profile fields persisted |
| UT-009 | `UserProfileSerializer.update` | `accounts/serializers.py` | Update nested `user.name` | Payload with `user: {name}` | User name and profile fields updated |
| UT-010 | `AccountSettingsSerializer.validate_weekly_goal_hours` | `accounts/serializers.py` | Enforce 1-80 hour range | `0`, `81` | Serializer invalid |
| UT-011 | `DailyGoalSerializer.validate_goal_text` | `accounts/serializers.py` | Reject blank goal text | Whitespace string | Serializer invalid |
| UT-012 | Helper `percentage` | `accounts/views.py`, `core/views.py` | Zero denominator | `part=1,total=0` | Returns `0` |
| UT-013 | Helper `bounded_percentage` | `accounts/views.py`, `core/views.py` | Clamp bounds | `-5`, `150` | Returns `0`, `100` |
| UT-014 | Helper `tone_for_score` | `accounts/views.py` | Score label thresholds | `90`, `70`, `40` | Returns implemented tone buckets |
| UT-015 | Helper `initials` | `accounts/views.py` | Build initials | Name, email fallback, empty | Returns initials from implementation |
| UT-016 | Helper `relative_time` | `accounts/views.py` | Render recent timestamp labels | Now, minutes ago, days ago | Returns implemented relative labels |
| UT-017 | `Topic.save` | `core/models.py` | Auto-generate slug when empty | Topic with name and no slug | Slug populated |
| UT-018 | `TopicDependency` | `core/models.py` | Enforce unique dependency pair | Duplicate `topic/prerequisite` | Integrity error |
| UT-019 | `UserTopicProgress` | `core/models.py` | Enforce unique user-topic progress | Duplicate user/topic | Integrity error |
| UT-020 | `UserAnswer` | `core/models.py` | Persist answer correctness and timing | User, question, selected answer | Saved with `is_correct` and timestamp |
| UT-021 | `TestAttempt` | `core/models.py` | Persist score totals and completion timestamp | Attempt with score/total | Saved values returned |
| UT-022 | `UserPassport.save` | `core/models.py` | Generate sharing token | New passport without token | Token generated |
| UT-023 | `UserCertificate.save` | `core/models.py` | Generate certificate identifiers | New certificate | `certificate_id`, `verification_hash`, `sharing_token` generated |
| UT-024 | `UserPortfolio.save` | `core/models.py` | Generate public slug | New portfolio | `public_url_slug` generated |
| UT-025 | `UserProblemBookmark` | `core/models.py` | Enforce unique bookmark | Duplicate user/problem | Integrity error |
| UT-026 | `build_runner_code` | `core/services/judge_service.py` | Wrap Python solution | Python code + function name | Runner code calls submitted function |
| UT-027 | `build_runner_code` | `core/services/judge_service.py` | Wrap JavaScript solution | JS code + function name | Runner code parses JSON input and logs JSON |
| UT-028 | `evaluate_submission` | `core/services/judge_service.py` | Submission has no linked problem | CodeSubmission without problem | Status `Error`, error message stored |
| UT-029 | `evaluate_submission` | `core/services/judge_service.py` | Problem has no test cases | Problem without `TestCase` rows | Status `Error`, error message stored |
| UT-030 | `evaluate_submission` | `core/services/judge_service.py` | Accepted result path | Monkeypatch `execute_code_locally` success | Status `Accepted`, all test cases passed |
| UT-031 | `evaluate_submission` | `core/services/judge_service.py` | Wrong answer path | Monkeypatch mismatched output | Status `Wrong Answer` |
| UT-032 | `evaluate_submission` | `core/services/judge_service.py` | Runtime error path | Monkeypatch `success=False` | Status `Runtime Error` |
| UT-033 | `execute_code_locally` | `core/views.py` | Reject unsupported language through caller validation | Unsupported language from API | API returns 400 before execution |
| UT-034 | `execute_code_locally` | `core/views.py` | Timeout process | Infinite loop code | Returns timeout-style failure |
| UT-035 | `formatApiError` | `frontend-react/src/api/client.js` | Format JSON error body | `{error:"x"}` / field errors | User-facing error string |
| UT-036 | API client refresh flow | `frontend-react/src/api/client.js` | Retry once after 401 | Expired access + valid refresh | Refresh endpoint called; original request retried |
| UT-037 | API client retry flow | `frontend-react/src/api/client.js` | Retry 5xx/network errors | Mock 500/TypeError | Retries up to configured count |
| UT-038 | `AuthContext` | `frontend-react/src/contexts/AuthContext.jsx` | Login stores tokens | Valid login response | Access/refresh saved; user state populated |
| UT-039 | `AuthContext` | `frontend-react/src/contexts/AuthContext.jsx` | Logout clears tokens | Existing refresh token | Logout call attempted; local tokens cleared |
| UT-040 | `useApi` | `frontend-react/src/hooks/useApi.js` | GET loading/error state | Successful and failed API mocks | Loading toggles; error captured; data set |

## Integration Test Matrix

| ID | Flow | Source files | Test case | Expected result |
|---|---|---|---|---|
| IT-001 | Registration to session | `accounts/views.py`, `accounts/serializers.py`, `core/bootstrap.py` | Register a student with valid profile fields, then call `/api/auth/session/` | JWT returned; authenticated session returns user identity |
| IT-002 | Registration validation | `accounts/serializers.py` | Register with short password and invalid CGPA | 400 validation response; no user created |
| IT-003 | Login throttle | `accounts/views.py` | Repeat invalid login more than `5/min` | Throttled response from DRF |
| IT-004 | Login to dashboard seed | `accounts/views.py`, `core/bootstrap.py` | Login non-admin user and call `/api/auth/dashboard/` | User prep data exists; dashboard returns metrics |
| IT-005 | Admin dashboard denial | `accounts/views.py` | Authenticate staff/superuser to `/api/auth/dashboard/` | 403 response |
| IT-006 | Profile update | `accounts/views.py`, `accounts/serializers.py`, `frontend-react/src/pages/ProfilePage.jsx` | PUT profile fields from frontend shape | Profile rows updated; nested user name updated |
| IT-007 | Settings update | `accounts/views.py`, `frontend-react/src/pages/SettingsPage.jsx` | PUT valid settings | Settings response includes updated serializer data |
| IT-008 | Missing password change | `frontend-react/src/pages/SettingsPage.jsx`, `accounts/urls.py` | Submit change password form | Frontend calls `/api/auth/change-password/`; backend route does not exist |
| IT-009 | Daily goals and streak | `accounts/views.py` | Create goal today with no prior streak | DailyGoal created; UserStreak current/longest updated |
| IT-010 | Streak continuation | `accounts/views.py` | Create goal with `last_active_date=yesterday` | Current streak increments |
| IT-011 | Streak reset | `accounts/views.py` | Create goal after gap | Current streak resets to 1 |
| IT-012 | Learning path | `core/views.py`, `frontend-react/src/pages/LearningPathPage.jsx` | Authenticated GET `/api/learning-path/` | Tracks, topics, progress, question counts returned |
| IT-013 | Topic completion | `core/views.py`, `frontend-react/src/pages/PrepPage.jsx` | POST `/api/prep/complete-topic/` with valid topic | UserTopicProgress marked completed |
| IT-014 | Topic dependency display | `core/models.py`, `core/views.py`, `frontend-react/src/pages/TopicStudyPage.jsx` | Topic with incomplete prerequisite | Topic/journey payload indicates locked/prerequisite state |
| IT-015 | Topic draft autosave | `core/views.py`, `frontend-react/src/pages/TopicStudyPage.jsx` | POST drafts dictionary | UserDraft upserted for user/topic |
| IT-016 | Topic quiz pass | `core/views.py`, `frontend-react/src/pages/TopicStudyPage.jsx` | Submit answers with accuracy >= 60 | UserAnswer rows saved; topic marked complete |
| IT-017 | Topic quiz fail | `core/views.py` | Submit answers with accuracy below 60 | UserAnswer rows saved; topic not completed by quiz |
| IT-018 | Mock test start/submit | `core/views.py`, `frontend-react/src/pages/MockTestsPage.jsx` | Start a test then submit answers | TestAttempt created, scored, completed |
| IT-019 | Prevent double submit | `core/views.py` | Submit same attempt twice | Second submit returns 400 |
| IT-020 | Analytics aggregation | `core/views.py`, `frontend-react/src/pages/AnalyticsPage.jsx` | Seed answers/test attempts and call analytics endpoints | Aggregated accuracy/performance payloads returned |
| IT-021 | Company readiness update | `core/views.py`, `frontend-react/src/pages/CompaniesPage.jsx` | POST `/api/companies/<name>/` with readiness/focus | CompanyTarget created or updated and reflected in list/detail |
| IT-022 | Admin content CRUD | `core/views.py`, `frontend-react/src/pages/AdminPage.jsx` | Create track, topic, question, test | Rows created and visible in admin overview |
| IT-023 | Admin delete protection | `core/views.py` | Delete track with topics or question/test with history | 400 protection response where implemented |
| IT-024 | AI explanation | `core/views.py` | Valid question with missing `GROQ_API_KEY` | 503 `AI service is not configured.` |
| IT-025 | Code workspace execution | `core/views.py`, `frontend-react/src/pages/CodingWorkspacePage.jsx` | POST runnable Python to `/api/code/execute/` | Output, error, success, exit code returned |
| IT-026 | Problem run | `core/views.py`, `frontend-react/src/pages/ProblemSolvingPage.jsx` | Run code against sample/custom input | Execution result returned without creating judged submission |
| IT-027 | Problem submit | `core/views.py`, `core/services/judge_service.py` | Submit code for problem with test cases | CodeSubmission saved and evaluated |
| IT-028 | Bookmark toggle | `core/views.py` | POST bookmark endpoint twice | First creates bookmark; second removes it |
| IT-029 | Snippet lifecycle | `core/views.py` | POST snippet, list, delete | User-owned snippet created/listed/deleted |
| IT-030 | Interview session | `core/views.py`, `core/interview_data.py`, `frontend-react/src/pages/AIInterviewPage.jsx` | Start session, fetch question, submit answer, end | InterviewSession and InterviewQA rows updated |
| IT-031 | Resume actions | `core/views.py` | POST `upload`, `rewrite`, `branding` | Implemented branch response returned; invalid action 400 |
| IT-032 | Passport sharing | `core/views.py`, `frontend-react/src/pages/PassportPage.jsx` | Toggle public/private and fetch shared token | Public returns data; private returns 403 |
| IT-033 | Certificate sharing | `core/views.py` | Issue certificate, toggle visibility, fetch token | Public returns data; private returns 403 |
| IT-034 | Portfolio actions | `core/views.py`, `frontend-react/src/pages/PortfolioPage.jsx` | Generate project, sync, update state, evaluate, toggle visibility | Implemented action response returned |
| IT-035 | Public portfolio | `core/views.py`, `frontend-react/src/pages/SharedPortfolioPage.jsx` | Fetch shared slug | Public returns data; private returns 403 |
| IT-036 | Contest sync command | `core/management/commands/sync_contests.py` | Mock external contest API success and failure | Creates live contests or fallback demo contests |

## API Test Matrix

| ID | Endpoint | Methods | Authentication | Test cases |
|---|---|---|---|---|
| API-001 | `/api/auth/register/` | POST | AllowAny | Valid registration; duplicate email; short password; CGPA <0 or >10 |
| API-002 | `/api/auth/login/` | POST | AllowAny, throttled | Valid credentials; missing email/password; invalid credentials; throttle after repeated failures |
| API-003 | `/api/auth/session/` | GET | JWT required | Valid token returns user; missing/expired token returns auth error |
| API-004 | `/api/auth/token/refresh/` | POST | AllowAny | Valid refresh returns access; missing refresh 400; invalid refresh 401 |
| API-005 | `/api/auth/logout/` | POST | JWT required | Valid refresh blacklisted; missing/invalid refresh still returns logout message after warning path |
| API-006 | `/api/auth/profile/` | GET, PUT | JWT required | Get profile; update valid profile; invalid nested/profile values |
| API-007 | `/api/auth/settings/` | GET, PUT | JWT required | Get settings; update `weekly_goal_hours` 1-80; reject 0/81 |
| API-008 | `/api/auth/goals/` | GET, POST | JWT required | Get today's goals; create non-empty goal; reject blank goal |
| API-009 | `/api/auth/goals/<pk>/` | PUT | JWT required | Update own goal; reject other user's/missing goal with 404 |
| API-010 | `/api/auth/streak/` | GET | JWT required | Return existing streak; auto-create missing streak |
| API-011 | `/api/auth/dashboard/` | GET | JWT required | Student dashboard success; staff/superuser 403 |
| API-012 | `/api/health/` | GET | Public | Returns health payload |
| API-013 | `/api/landing/` | GET | AllowAny | Returns landing payload |
| API-014 | `/api/tracks/` | GET | Public | Returns active tracks |
| API-015 | `/api/learning-path/` | GET | JWT required | Returns track/topic/progress aggregation |
| API-016 | `/api/tracks/<track_id>/topics/` | GET | JWT required | Valid track; track with no topics |
| API-017 | `/api/topics/<topic_id>/complete/` | POST | JWT required | Valid topic complete; missing topic 404 |
| API-018 | `/api/topics/<topic_id>/progress/` | POST | JWT required | Valid boolean `is_completed`; non-boolean 400; missing topic 404 |
| API-019 | `/api/tracks/<track_id>/progress/` | GET | JWT required | Returns completed/total/progress for track |
| API-020 | `/api/topics/<topic_id>/questions/` | GET | JWT required | Returns active topic questions |
| API-021 | `/api/questions/<question_id>/submit/` | POST | JWT required | Answer A-D accepted; invalid answer 400; missing question 404 |
| API-022 | `/api/weak-topics/` | GET | JWT required | Returns weak topic aggregation from answers |
| API-023 | `/api/tests/` | GET | JWT required | Returns test summaries with latest/best attempt data |
| API-024 | `/api/tests/<test_id>/` | GET | JWT required | Valid test detail; missing test 404 |
| API-025 | `/api/tests/<test_id>/start/` | POST | JWT required | Creates TestAttempt; missing test 404 |
| API-026 | `/api/tests/submit/` | POST | JWT required | Scores answers; invalid attempt 404; already submitted 400 |
| API-027 | `/api/analytics/topic-accuracy/` | GET | JWT required | Returns per-topic accuracy |
| API-028 | `/api/analytics/overall-performance/` | GET | JWT required | Returns aggregate performance |
| API-029 | `/api/analytics/dashboard/` | GET | JWT required | Returns dashboard analytics |
| API-030 | `/api/analytics/full/` | GET | JWT required | Returns full analytics payload |
| API-031 | `/api/practice/` | GET | JWT required | Returns practice dashboard; frontend page exists but is not routed |
| API-032 | `/api/companies/` | GET, POST | JWT required | GET/POST readiness query; CGPA/backlog parsing defaults applied |
| API-033 | `/api/companies/<company_name>/` | POST | JWT required | Update readiness/focus/is_active; readiness int parse failure returns 400 |
| API-034 | `/api/companies/<company_name>/details/` | GET | JWT required | Known company returns catalog detail; unknown company returns fallback catalog data |
| API-035 | `/api/admin/overview/` | GET | Admin only | Admin succeeds; student denied |
| API-036 | `/api/admin/users/<user_id>/` | PATCH | Admin only | Toggle staff/active/name; missing user 404; super admin edit blocked |
| API-037 | `/api/admin/content/` | POST | Admin only | Create track/topic/question/test; validate required fields/type |
| API-038 | `/api/admin/tracks/<track_id>/` | PATCH, DELETE | Admin only | Update valid fields; blank name 400; delete blocked when topics exist |
| API-039 | `/api/admin/topics/<topic_id>/` | PATCH, DELETE | Admin only | Update valid fields; invalid order/track 400; missing 404 |
| API-040 | `/api/admin/questions/<question_id>/` | PATCH, DELETE | Admin only | Validate topic/options/answer/difficulty; delete protection with answer history |
| API-041 | `/api/admin/tests/<test_id>/` | PATCH, DELETE | Admin only | Validate name/duration/topic/question ids; delete protection with attempts |
| API-042 | `/api/admin/company-targets/` | POST | Admin only | Validate user/company/readiness; create/update target |
| API-043 | `/api/admin/company-targets/<target_id>/` | PATCH, DELETE | Admin only | Update/delete target; missing target 404 |
| API-044 | `/api/ai/explain/` | POST | JWT required | Valid question and key; missing question 404; no key 503; timeout 504 |
| API-045 | `/api/code/execute/` | POST | JWT required, throttled | Empty code 400; unsupported language 400; oversized code 400; valid execution |
| API-046 | `/api/code/workspace/` | GET | JWT required | Returns workspace defaults/history |
| API-047 | `/api/code/submissions/` | GET | JWT required | Lists current user's submissions |
| API-048 | `/api/code/dashboard/` | GET | JWT required | Returns code lab dashboard |
| API-049 | `/api/code/problems/` | GET | JWT required | Lists problems; query filters/search/pagination behavior from view |
| API-050 | `/api/code/problems/<slug>/` | GET | JWT required | Valid problem; missing slug behavior |
| API-051 | `/api/code/problems/<slug>/run/` | POST | JWT required | Run sample/custom code; invalid code/language paths |
| API-052 | `/api/code/problems/<slug>/submit/` | POST | JWT required | Submit and evaluate; empty code 400 |
| API-053 | `/api/code/problems/<slug>/submissions/` | GET | JWT required | Lists user's submissions for problem |
| API-054 | `/api/code/problems/<slug>/editorial/` | GET | JWT required | Returns editorial/template payload |
| API-055 | `/api/code/problems/<slug>/bookmark/` | POST | JWT required | Toggle bookmark |
| API-056 | `/api/code/problems/<slug>/ai-mentor/` | POST | JWT required | Actions `explain_error`, `give_hint`, `optimize_code`, `explain_solution`, `dry_run` return canned guidance |
| API-057 | `/api/code/contests/` | GET | JWT required | Lists contests |
| API-058 | `/api/code/contests/<contest_id>/leaderboard/` | GET | JWT required | Returns contest plus mock rankings |
| API-059 | `/api/code/snippets/` | GET, POST | JWT required | List snippets; create snippet with title/code/language defaults |
| API-060 | `/api/code/snippets/<pk>/` | DELETE | JWT required | Delete own snippet; missing/not-owned behavior |
| API-061 | `/api/interview/config/` | GET | JWT required | Returns interview categories/config |
| API-062 | `/api/interview/start/` | POST | JWT required | Start session with category default/general |
| API-063 | `/api/interview/question/` | POST | JWT required | Next question; missing active session 404; exhausted questions 400 |
| API-064 | `/api/interview/submit/` | POST | JWT required | Submit non-empty answer; empty answer 400; missing session 404 |
| API-065 | `/api/interview/end/` | POST | JWT required | End active session; missing active session 404 |
| API-066 | `/api/interview/history/` | GET | JWT required | Return user interview history |
| API-067 | `/api/resume/` | GET, POST | JWT required | GET overview; POST actions `upload`, `rewrite`, `branding`; invalid action 400 |
| API-068 | `/api/passport/` | GET, POST | JWT required | GET dynamic passport; POST `verify`, `share`, `copilot_checklist`; invalid action 400 |
| API-069 | `/api/passport/shared/<token>/` | GET | AllowAny | Public passport returns data; private returns 403 |
| API-070 | `/api/verification/` | GET, POST | JWT required | GET verification dashboard; issue certificate; toggle visibility |
| API-071 | `/api/verification/shared/<token>/` | GET | AllowAny | Public certificate returns data; private returns 403 |
| API-072 | `/api/portfolio/` | GET, POST | JWT required | GET portfolio dashboard; POST implemented actions; invalid action behavior |
| API-073 | `/api/portfolio/shared/<slug>/` | GET | AllowAny | Public portfolio returns data; private returns 403 |
| API-074 | `/api/prep/current-topic/` | GET | JWT required | Returns next/current topic; no topics 404 |
| API-075 | `/api/prep/topic-journey/` | GET | JWT required | Optional `track` filter; returns journey |
| API-076 | `/api/prep/roadmaps/` | GET | JWT required | Returns roadmap cards |
| API-077 | `/api/prep/milestones/` | GET | JWT required | Returns mock test/milestone summaries |
| API-078 | `/api/prep/complete-topic/` | POST | JWT required | Missing `topic_id` 400; missing topic 404; valid completes |
| API-079 | `/api/prep/topic/<slug>/` | GET | JWT required | Valid slug detail; missing topic 404 |
| API-080 | `/api/prep/topic/<slug>/complete/` | POST | JWT required | Valid slug completes; missing topic 404 |
| API-081 | `/api/prep/topic/<slug>/drafts/` | GET, POST | JWT required | GET drafts; POST requires dictionary; bad type 400 |
| API-082 | `/api/prep/topic/<slug>/quiz/submit/` | POST | JWT required | Answers dictionary required; no quiz questions 400; pass/fail scoring |
| API-083 | `/api/prep/topic/<slug>/ai-context/` | GET | JWT required | Returns context; missing topic 404 |
| API-084 | `/api/prep/topic/<slug>/ai-chat/` | POST | JWT required | Returns disabled AI system notice |
| API-085 | `/api/problems/by-topic/<topic_id>/` | GET | JWT required | Valid topic returns problems; missing topic 404 |
| API-086 | `/api/user/progress/` | GET | JWT required | Returns user progress |

## Manual Testing Checklist

| ID | Route / screen | Component | Checklist |
|---|---|---|---|
| MT-001 | `/` | `LandingPage` | Desktop load, mobile load, FAQ search, demo interactions, login/signup links |
| MT-002 | `/landing` | `LandingPage` | Same checks as `/` alias |
| MT-003 | `/login` | `AuthPage` | Login success, invalid credentials, required fields, navigation to signup |
| MT-004 | `/signup` | `AuthPage` | Signup success, required fields, password length error, CGPA error, navigation to login |
| MT-005 | `/analytics` | `AnalyticsPage` | Protected redirect when logged out, charts render, empty/error/loading states |
| MT-006 | `/prep/journey` | `PrepPage` | Track filter, topic cards, complete-topic action, locked prerequisites, loading/error/empty states |
| MT-007 | `/prep/roadmaps` | `LearningPathPage` | Roadmap cards, progress values, route links, loading/error/empty states |
| MT-008 | `/prep/milestones` | `MockTestsPage` | Test list, start test button, empty/error/loading states |
| MT-009 | `/prep/topic/:slug` | `TopicStudyPage` | Sections tabs, quiz submit, draft autosave, topic completion, AI notice, coding-problems coming-soon state |
| MT-010 | `/code-lab/arena` | `ProblemArenaPage` | Search/filter, pagination, problem cards/table, empty/error/loading states |
| MT-011 | `/code-lab/arena/:slug` | `ProblemSolvingPage` | Editor load, run code, submit code, custom stdin, result panels, AI mentor pane |
| MT-012 | `/code-lab/workspace` | `CodingWorkspacePage` | Standalone editor, language selector, stdin, run output, execution errors |
| MT-013 | `/code-lab/contests` | `ContestHubPage` | Contest cards, leaderboard links/modal behavior, loading/error/empty states |
| MT-014 | `/ai/interview` | `AIInterviewPage` | Category selection, start, question flow, answer submit, end session, history |
| MT-015 | `/career/companies` | `CompaniesPage` | Search/filter, readiness inputs, company cards, eligibility values |
| MT-016 | `/career/companies/:name` | `CompanyDetailPage` | Detail metrics, target update, navigation back |
| MT-017 | `/portfolio/shared/:slug` | `SharedPortfolioPage` | Public portfolio load, private/invalid slug error |
| MT-018 | `/profile/passport` | `PassportPage` | Dynamic metrics, verify skill, share toggle, public link behavior |
| MT-019 | `/profile/me` | `ProfilePage` | Load profile, edit fields, save, validation/error state |
| MT-020 | `/passport/shared/:token` | `SharedPassportPage` | Public passport load, private/invalid token error |
| MT-021 | `/settings` | `SettingsPage` | Load settings, save settings, password form shows backend 404 gap |
| MT-022 | `/admin` | `AdminPage` | Admin-only access, users tab, tracks/topics/questions/tests/company targets CRUD, validation errors |
| MT-023 | `*` | `NotFoundPage` | Unknown URL renders 404 page and navigation links |

## Bug History

| ID | Evidence | Current status | Test to preserve |
|---|---|---|---|
| BH-001 | `frontend-react/src/pages/SettingsPage.jsx` calls `/auth/change-password/`; `accounts/urls.py` has no matching route | Known failure | Manual/API test must assert current 404 until implemented |
| BH-002 | `frontend-react/src/pages/PracticePage.jsx` exists; `frontend-react/src/App.jsx` has no route for it | Unrouted page | Route inventory test should fail if expected route is claimed |
| BH-003 | `frontend-react/src/pages/PortfolioPage.jsx` exists; private `/portfolio` route is not wired in `App.jsx` | Unrouted page | Route inventory test should fail if private portfolio screen is claimed reachable |
| BH-004 | `frontend-react/src/pages/DashboardPage.jsx` navigates to `/mock-tests`; implemented route is `/prep/milestones` | Broken navigation | Browser test should click action and verify it lands on existing route |
| BH-005 | `frontend-react/src/pages/DashboardPage.jsx` contains navigation to `/companies`; implemented route is `/career/companies` | Broken navigation | Browser test should click action and verify no 404 |
| BH-006 | `core/urls.py` declares `interview/end/` and `interview/history/` twice | Duplicate URL patterns | URL inventory test should assert no duplicate route names/patterns |
| BH-007 | `core/services/judge_service.py` imports `execute_code_locally` from `core/views.py` | Service depends on view module | Unit import test should detect circular/inverted dependency risk |
| BH-008 | `core/models.py` `UserDraft.__str__` references `self.user.username`; custom user has no `username` field | Runtime failure when stringifying draft | Unit test should call `str(UserDraft(...))` and expose failure |
| BH-009 | `core/views.py` `PrepTopicAIChatView` returns disabled AI system notice | AI chat not integrated | API test should assert current disabled notice |
| BH-010 | `frontend-react/src/ai/AIAssistant.jsx` returns local canned responses | Mocked frontend assistant | UI test should classify as mocked, not backend AI |
| BH-011 | `frontend-react/src/components/CodeLab/AiMentorPane.jsx` is local UI around canned prompt actions | Partially integrated AI mentor | UI/API test should verify backend `/ai-mentor/` canned responses |
| BH-012 | `core/views.py` contest leaderboard uses mock rankings | Mocked leaderboard | API test should assert response shape but mark rankings mocked |
| BH-013 | `requirements.txt` lacks `groq`; `core/views.py` imports `groq` in `get_groq_client` | Dependency mismatch | Dependency test should import app with optional AI path |
| BH-014 | `requirements.txt` lacks `apscheduler`; `core/scheduler.py` imports it | Dependency mismatch | Dependency test should import scheduler |
| BH-015 | Local SQLite must be migrated before seeding; stale DB produced missing-column failures during audit work | Local environment failure | Setup test should run `manage.py migrate --check` before seed/screenshots |

## Known Failures

| ID | Failure | Source | Expected test result today |
|---|---|---|---|
| KF-001 | Password change form calls missing backend endpoint | `frontend-react/src/pages/SettingsPage.jsx`, `accounts/urls.py` | 404 |
| KF-002 | Practice page is implemented but unreachable from router | `frontend-react/src/pages/PracticePage.jsx`, `frontend-react/src/App.jsx` | Direct route absent |
| KF-003 | Private portfolio dashboard page is implemented but unreachable from router | `frontend-react/src/pages/PortfolioPage.jsx`, `frontend-react/src/App.jsx` | Direct route absent |
| KF-004 | Dashboard action navigates to `/mock-tests` | `frontend-react/src/pages/DashboardPage.jsx` | Browser lands on NotFound |
| KF-005 | Dashboard action navigates to `/companies` | `frontend-react/src/pages/DashboardPage.jsx` | Browser lands on NotFound |
| KF-006 | `UserDraft.__str__` can raise `AttributeError` | `core/models.py` | Unit test fails until fixed |
| KF-007 | AI topic chat returns disabled notice | `core/views.py` | API returns disabled notice, not generated answer |
| KF-008 | Code contest leaderboard rankings are mock generated | `core/views.py` | API returns mock rankings |
| KF-009 | Missing `groq` package in `requirements.txt` for AI client path | `requirements.txt`, `core/views.py` | Import or AI path fails unless package installed separately |
| KF-010 | Missing `apscheduler` package in `requirements.txt` for scheduler | `requirements.txt`, `core/scheduler.py` | Scheduler import fails unless package installed separately |

## Validation Rules

| Area | Rule | Source |
|---|---|---|
| Registration password | Minimum length 8 and Django password validators | `accounts/serializers.py` |
| Registration CGPA | CGPA must be between 0 and 10 | `accounts/serializers.py`, `accounts/models.py` |
| Login | Email and password are required | `accounts/views.py` |
| Settings | `weekly_goal_hours` must be between 1 and 80 | `accounts/serializers.py` |
| Goals | `goal_text` cannot be empty | `accounts/serializers.py` |
| Student dashboard | Staff/superuser users forbidden | `accounts/views.py` |
| Topic progress | `is_completed` must be boolean | `core/views.py` |
| Question submit | Answer must be `A`, `B`, `C`, or `D` | `core/views.py` |
| Test submit | Attempt must belong to authenticated user and not be completed | `core/views.py` |
| Company target | `readiness` parsed as integer and bounded 0-100 | `core/views.py` |
| Admin track create | Track name required | `core/views.py` |
| Admin topic create | Valid `track_id`; topic name required; order parsed as integer | `core/views.py` |
| Admin question create/update | Topic valid; question text and all four options required; correct answer A-D; difficulty easy/medium/hard | `core/views.py` |
| Admin test create/update | Test name required; duration numeric/min 1; topic/question IDs accepted | `core/views.py` |
| Code execution | Code required; language in `python`, `javascript`, `java`, `cpp`, `sql`; code size limited | `core/views.py` |
| Problem submit | Code cannot be empty | `core/views.py` |
| Interview question/end/submit | Active session must belong to user; answer cannot be empty | `core/views.py` |
| Resume | POST action must be `upload`, `rewrite`, or `branding` | `core/views.py` |
| Passport | POST action must be `verify`, `share`, or `copilot_checklist`; skill must exist for verify | `core/views.py` |
| Verification | POST action supports `issue_certificate`, `toggle_visibility` | `core/views.py` |
| Portfolio | POST action supports `generate_project`, `sync_to_resume`, `update_kanban`, `update_milestones_state`, `evaluate_project`, `update_template`, `toggle_visibility` | `core/views.py` |
| Topic drafts | `drafts` must be a dictionary | `core/views.py` |
| Topic quiz | `answers` must be a dictionary; quiz questions must exist | `core/views.py` |
| Public sharing | Passport/certificate/portfolio must be public | `core/views.py` |

## Security Tests

| ID | Security area | Source | Test case | Expected result |
|---|---|---|---|---|
| SEC-001 | JWT protection | `accounts/urls.py`, `core/urls.py` | Call each protected endpoint without token | DRF auth error |
| SEC-002 | Public endpoints | `core/urls.py`, `accounts/urls.py` | Call `landing`, `health`, shared passport/certificate/portfolio without token | Public endpoints respond according to visibility |
| SEC-003 | Admin permissions | `core/views.py` | Student calls `/api/admin/*` | Denied |
| SEC-004 | Student dashboard role restriction | `accounts/views.py` | Staff/superuser calls `/api/auth/dashboard/` | 403 |
| SEC-005 | Login throttle | `accounts/views.py` | More than 5 anonymous login attempts/minute | Throttled |
| SEC-006 | Token refresh | `frontend-react/src/api/client.js`, `accounts/views.py` | Expired access + valid refresh | New access token issued and request retried |
| SEC-007 | Invalid refresh | `accounts/views.py` | Invalid refresh token | 401 |
| SEC-008 | Logout blacklist | `accounts/views.py` | Logout with refresh token, then refresh again | Refresh rejected if blacklist app active |
| SEC-009 | Object ownership: goals | `accounts/views.py` | User updates another user's goal ID | 404 |
| SEC-010 | Object ownership: tests | `core/views.py` | User submits another user's attempt ID | 404 |
| SEC-011 | Object ownership: snippets | `core/views.py` | User deletes another user's snippet ID | Not found/denied |
| SEC-012 | Object ownership: interview | `core/views.py` | User submits/end another user's session ID | 404 |
| SEC-013 | Public passport privacy | `core/views.py` | Fetch private passport token | 403 |
| SEC-014 | Public certificate privacy | `core/views.py` | Fetch private certificate token | 403 |
| SEC-015 | Public portfolio privacy | `core/views.py` | Fetch private portfolio slug | 403 |
| SEC-016 | Code execution timeout | `core/views.py` | Infinite loop code | Timeout failure |
| SEC-017 | Code execution language allowlist | `core/views.py` | Unsupported language | 400 |
| SEC-018 | Code execution size limit | `core/views.py` | Oversized code payload | 400 |
| SEC-019 | Code execution filesystem/network access | `core/views.py` | Attempt file reads/network calls from submitted code | Current subprocess implementation should be treated as high-risk; test documents whether access is possible |
| SEC-020 | CORS configuration | `config/settings.py` | Browser request from allowed and disallowed origins | Allowed origins succeed; disallowed origins blocked by browser CORS |
| SEC-021 | Local token storage | `frontend-react/src/api/client.js`, `frontend-react/src/contexts/AuthContext.jsx` | XSS proof-of-risk test against token storage | Tokens are stored in `localStorage`; test should document exposure risk |
| SEC-022 | Rendered markdown/content | `frontend-react/src/pages/TopicStudyPage.jsx`, shared pages | Inject script-like content into markdown/text fields | UI must not execute injected scripts |

## Performance Tests

| ID | Area | Source | Dataset / load | Measurement |
|---|---|---|---|---|
| PERF-001 | Student dashboard aggregation | `accounts/views.py` | User with many answers, attempts, topic progress rows, company targets, activity events | Response time and query count |
| PERF-002 | Learning path aggregation | `core/views.py` | Many tracks/topics/questions/progress rows | Response time and query count |
| PERF-003 | Prep topic journey | `core/views.py` | Many topics with dependencies and progress rows | Response time; dependency lookup correctness |
| PERF-004 | Topic detail | `core/views.py` | Topic with many sections, visualizations, questions, problems | Response time and payload size |
| PERF-005 | Quiz submission | `core/views.py` | Topic quiz with many questions | DB write count and response time |
| PERF-006 | Test list | `core/views.py` | Many tests and attempts per user | Response time; latest/best attempt aggregation correctness |
| PERF-007 | Full analytics | `core/views.py` | High answer and attempt volume | Response time and chart payload size |
| PERF-008 | Admin overview | `core/views.py` | Many users, topics, questions, tests, company targets | Response time and query count |
| PERF-009 | Code execution timeout | `core/views.py` | Infinite loop and slow code | Enforces timeout under configured limit |
| PERF-010 | Problem submit evaluation | `core/services/judge_service.py` | Problem with many test cases | Total judge duration and per-case timing |
| PERF-011 | Problem list | `core/views.py` | Large `CodingProblem` table | Response time; pagination/search behavior |
| PERF-012 | Contest sync | `core/management/commands/sync_contests.py` | Mock API latency/failure | Command completes and fallback path works |
| PERF-013 | Frontend build | `frontend-react/package.json` | `npm run build` | Successful production build; bundle warnings recorded |
| PERF-014 | Frontend route rendering | `frontend-react/src/App.jsx` | Navigate every implemented route | Time to first rendered content per page |
| PERF-015 | API client retries | `frontend-react/src/api/client.js` | Mock 5xx/network failures | Retry count and backoff timing |
| PERF-016 | Charts rendering | `frontend-react/src/pages/AnalyticsPage.jsx`, `DashboardPage.jsx` | Large chart arrays | No UI lockup; chart remains readable |

## Automation Gaps

| Gap | Evidence | Recommended test layer |
|---|---|---|
| No Django unit tests | `accounts/tests.py`, `core/tests.py` contain only scaffold comments | Django `TestCase` / DRF `APITestCase` |
| No frontend unit test script | `frontend-react/package.json` has `dev`, `build`, `lint`, `preview`; no `test` script | Vitest/React Testing Library if added |
| Ad-hoc scripts are outside test runner | `test-artifacts/test_*.py` | Convert to pytest/Django tests or keep as manual utilities |
| No browser regression suite | Screenshot artifacts exist, no committed Playwright test suite | Playwright route smoke tests |
| No API contract suite | API inventory exists, no executable collection | DRF APITestCase or Postman/Newman collection |
