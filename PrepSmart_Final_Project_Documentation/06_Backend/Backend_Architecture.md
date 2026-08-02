# Backend Architecture

## Overview
Django monolith separated into `accounts` and `core` apps.

ecords all past attempts, allowing users to review their code evolution.

### AI Interview Prep Simulator
- **Dynamic Interviews**: AI generates sequential questions based on chosen categories (Technical, HR, System Design).
- **Real-Time Evaluation**: Users submit text-based answers; the AI analyzes the response for relevance, completeness, and clarity.
- **Constructive Feedback**: Provides an immediate score out of 20 and detailed actionable feedback for every single Q&A pair.

### Full-Scale Analytics & Visual Charts
- **Performance Radar**: Visualizes strengths and weaknesses across different domains.
- **Time Analytics**: Tracks daily active hours against weekly goals.
- **Topic Accuracy**: Bar charts displaying historical accuracy rates on practice questions.

### Target Company Readiness
- **Company Tracking**: Users select target companies (e.g., Google, TCS).
- **Readiness Scoring**: The platform calculates or allows admins to define a readiness percentage based on the user's performance in company-specific domains.

### Admin Operations Portal
- **User Management**: Toggle roles (Student/Staff), suspend/activate accounts.
- **Curriculum Management**: Full CRUD (Create, Read, Update, Delete) for Tracks, Topics, Questions, and Tests.
- **Safe Deletions**: Prevents deletion of historical data (e.g., a question already answered by a student) to maintain analytical integrity, employing soft-deletes/archiving instead.
- **Deep-Dive Viewer**: Allows admins to inspect raw JSON payloads for debugging.

---

## 3. Complete Module List

### `accounts` (Django App)
- **Responsibilities**: User authentication, profile management, goal tracking, and gamification (streaks).
- **Workflow**: Intercepts login/signup requests, issues JWTs, tracks daily logins to increment streaks.
- **Dependencies**: `djangorestframework-simplejwt`.
- **APIs**: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/profile/`, `/api/auth/streak/`.
- **Database Interactions**: Reads/Writes `Use