# 🎓 Smart Placement Platform

The **Smart Placement Platform** is a feature-rich, full-stack placement preparation web application designed for students and college administrators. It helps candidates prepare systematically for technical, aptitude, and HR rounds with structured learning paths, mock test simulators, coding sandboxes, and AI-driven interview feedback.

The project features a **Django REST Framework (DRF)** backend and a **React 19 + Vite** frontend.

---

## 🚀 Key Modules & Features

1. **Dashboard & Streaks**:
   - High-level overview of daily goals, weekly study hour targets, and recent events.
   - Dynamic user streak system tracking active days and longest streak records.
   - Live activity events log documenting user actions (e.g., submission, mock test start).

2. **Structured Learning Paths**:
   - Curriculum divided into distinct **Tracks** (e.g., *Data Structures and Algorithms*, *Computer Science Fundamentals*, *SQL and Databases*, *Web Development and Projects*, *Aptitude and Reasoning*, etc.).
   - Each Track contains multiple **Topics** with descriptions, step-by-step progress updating, and checkmarks.

3. **Practice Workspace & Mock Tests**:
   - Topic-wise practice questions categorized by difficulty (Easy, Medium, Hard).
   - Mock Test Simulator with timers, auto-scoring, and complete summary dashboards.
   - Track-wise and Topic-wise performance analytics.

4. **Interactive Coding Workspace**:
   - Python code runner that executes submissions locally.
   - Capture `stdout` and `stderr` outputs, execution time, and memory usage.
   - Submission history and code workspace states.

5. **AI Interview Prep Simulator**:
   - Simulated interview rounds across technical and behavioral categories.
   - Sequential question delivery, text-based answers, and AI-driven evaluation.
   - Provides immediate scoring and constructive feedback on individual QA pairs.

6. **Full-Scale Analytics & Visual Charts**:
   - Recharts-driven graphs tracking preparation metrics.
   - Topic-wise accuracy radar/bar charts, daily active hours, and weak areas indicator.
   - Interview readiness dashboard showing scores in DSA, Aptitude, Projects, and Communication.

7. **Target Company Readiness**:
   - Customize list of target companies (e.g., TCS, Infosys, Accenture, Zoho).
   - Tracks preparation focus guidelines and estimated readiness percentages.

8. **Admin Operations Portal**:
   - Dedicated management view for staff and superusers.
   - Admin oversight of all users, curriculum content (tracks, topics, questions, mock tests), and company targets.

---

## 🛠️ Technology Stack

### Backend
- **Core**: Python 3.10+, Django 6.0.4
- **API Framework**: Django REST Framework (DRF) 3.17.1
- **Authentication**: `djangorestframework-simplejwt` (JWT-based token rotation)
- **Database**: MySQL (Production) / SQLite (Fallback for Local Development)
- **CORS**: `django-cors-headers`
- **Environment**: `python-dotenv`

### Frontend
- **Core**: React 19.2.5, Vite 8.0.10
- **Routing**: React Router DOM 7.14.2
- **Data Visualization**: Recharts 3.8.1
- **Icons**: Lucide React 1.14.0
- **Styling**: Vanilla CSS (Premium design system utilizing modern CSS custom variables, dark/light themes, animations, glassmorphism, responsive flex/grid layouts)

---

## 📁 Project Directory Structure

```
smart-placement-platform/
│
├── config/                  # Django project configuration
│   ├── settings.py          # App settings (JWT, CORS, logging, DB overrides)
│   ├── urls.py              # Root routing configuration
│   └── wsgi.py / asgi.py    # Production deployment interfaces
│
├── accounts/                # Django App: User accounts & streaks
│   ├── models.py            # User, UserProfile, DailyGoal, UserStreak
│   ├── serializers.py       # Serializers for profiles, login, and registration
│   ├── urls.py              # Auth-related routing (/api/auth/*)
│   └── views.py             # Auth controllers, session validation, registration
│
├── core/                    # Django App: Curriculum, Practice, Tests, and AI Engines
│   ├── bootstrap.py         # Mock data catalog & demo student seeding logic
│   ├── models.py            # Track, Topic, Question, Test, CompanyTarget, etc.
│   ├── serializers.py       # Serializers for practice questions, tests, submissions
│   ├── urls.py              # API routing (/api/*)
│   ├── views.py             # Viewsets for interactive learning, coding execution, and AI APIs
│   └── management/
│       └── commands/
│           └── seed_platform_data.py   # Seeding command
│
├── frontend-react/          # Vite + React Frontend Application
│   ├── src/
│   │   ├── api/             # API client configured with Axios/fetch helper
│   │   ├── components/      # UI components (Button, Card, Modal, Layout)
│   │   ├── contexts/        # React context (Auth, Theme)
│   │   ├── pages/           # Platform pages (Landing, Practice, CodeEditor, AIInterview, Admin)
│   │   ├── App.jsx          # Route declarations & protection middleware
│   │   └── main.jsx         # React mounting entry point
│   ├── package.json         # NPM manifest & script commands
│   └── vite.config.js       # Vite bundler configurations
│
├── db.sqlite3               # SQLite Database (for development)
├── manage.py                # Django CLI entry point
├── requirements.txt         # Backend Python dependencies
└── README.md                # Root project documentation (This file)
```

---

## 🔧 Installation & Local Setup

### Prerequisite
Ensure you have **Python 3.10+** and **Node.js 18+** installed.

### Backend Setup

1. **Navigate to the root directory**:
   ```bash
   cd smart-placement-platform
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory and add the following settings:
   ```env
   DEBUG=True
   SECRET_KEY=django-insecure-dev-only-smart-placement-platform-key-2026
   DB_ENGINE=sqlite
   ```
   *(Note: By default, if `DB_ENGINE=sqlite` is set or database configuration isn't provided, it will fallback to SQLite. Otherwise, configure your MySQL credentials).*

5. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Seed Database with Demo Data**:
   The platform includes a seeding command that populates the tracks, topics, practice questions, mock tests, and creates both a student and an admin account.
   ```bash
   python manage.py seed_platform_data
   ```
   This generates the following accounts:
   - **Student Account**:
     - **Email**: `student@prepsmart.dev`
     - **Password**: `PrepSmart@123`
   - **Admin Account**:
     - **Email**: `admin@prepsmart.dev`
     - **Password**: `Admin@12345`

7. **Start Backend Server**:
   ```bash
   python manage.py runserver
   ```
   The backend API will run at `http://127.0.0.1:8000/`.

---

### Frontend Setup

1. **Navigate to the frontend folder**:
   ```bash
   cd frontend-react
   ```

2. **Install Node Packages**:
   ```bash
   npm install
   ```

3. **Run Dev Server**:
   ```bash
   npm run dev
   ```
   The React application will run at `http://localhost:5173/`. Open it in your web browser.

---

## 📡 API Endpoints Overview

The backend exposes the following REST APIs:

### 🔐 Authentication (`/api/auth/`)
* `POST /api/auth/register/` - Register a new user profile
* `POST /api/auth/login/` - Login and receive JWT tokens (`access` & `refresh`)
* `GET /api/auth/session/` - Retrieve details of the current logged-in user
* `POST /api/auth/token/refresh/` - Rotate expired JWT access tokens
* `POST /api/auth/logout/` - Invalidate refresh token and logout
* `GET/POST /api/auth/profile/` - Fetch/update detailed student profile
* `GET/POST /api/auth/settings/` - Fetch/update settings (notifications, bio, timezone, etc.)
* `GET/POST /api/auth/goals/` - Fetch daily goals list / Create new goal
* `PATCH/DELETE /api/auth/goals/<id>/` - Toggle completion status or delete goals
* `GET /api/auth/streak/` - Get active and longest streak tracking stats
* `GET /api/auth/dashboard/` - Get composite dashboard metrics (hour counts, streaks, target companies, plan progress)

### 📚 Learning & Practice (`/api/`)
* `GET /api/tracks/` - List all tracks
* `GET /api/tracks/<id>/topics/` - List topics within a specific track
* `GET /api/tracks/<id>/progress/` - Retrieve user completion progress for a track
* `PATCH /api/topics/<id>/progress/` - Update progress percentage for a topic
* `POST /api/topics/<id>/complete/` - Mark a topic as completed
* `GET /api/topics/<id>/questions/` - Get practice questions under a topic
* `POST /api/questions/<id>/submit/` - Submit answer and check correctness

### 📝 Mock Tests (`/api/`)
* `GET /api/tests/` - List available mock tests
* `GET /api/tests/<id>/` - Retrieve details of a mock test
* `POST /api/tests/<id>/start/` - Start a test attempt
* `POST /api/tests/submit/` - Submit test solutions and record final scores

### 💻 Code Workspace & Execution (`/api/`)
* `POST /api/code/execute/` - Execute python code against custom stdin
* `GET /api/code/workspace/` - Fetch user's latest coding state
* `GET /api/code/submissions/` - List all previous code submission history

### 🤖 AI Interviews (`/api/`)
* `GET /api/interview/config/` - Retrieve available interview categories
* `POST /api/interview/start/` - Initialize a new mock interview session
* `GET /api/interview/question/` - Fetch the next interview question
* `POST /api/interview/submit/` - Submit an answer to the current question and receive AI evaluation
* `POST /api/interview/end/` - Complete the interview session and get final results
* `GET /api/interview/history/` - View past interview performance history

### 📊 Analytics & Companies (`/api/`)
* `GET /api/analytics/overall-performance/` - Get high-level correct answer ratios and activity metrics
* `GET /api/analytics/topic-accuracy/` - Get topic-wise accuracy analytics
* `GET /api/analytics/dashboard/` - Get complete dashboard analytics
* `GET /api/analytics/full/` - Fetch detailed visual data for all chart formats
* `GET /api/companies/` - Fetch target companies readiness overview
* `PATCH /api/companies/<company_name>/` - Edit readiness goals or toggle focus areas for a company
