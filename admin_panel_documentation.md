# Smart Placement Platform - Admin Console Documentation

The Admin Console is a comprehensive, production-grade interface designed to give platform administrators full control over the user base, curriculum, assessments, and corporate targets.

## Overview & Global Features
- **Deep-Dive Data Viewer (The "Eye" Icon)**: Every record across all tabs has an "Eye" action button. Clicking it opens a drawer rendering the entire raw backend JSON payload for that record. This allows admins to inspect hidden metadata without cluttering the main UI tables.
- **Global Error & Notice Banners**: Database constraints and server responses are elegantly handled via auto-clearing global animated toasts.
- **Responsive Slide-Over Drawer**: All creation, editing, and viewing actions utilize a modern slide-over drawer to preserve context, avoiding jarring page navigations.
- **Safe Deletions**: The backend enforces strict relational data integrity. If an admin attempts to delete a Topic or Question that a student has already interacted with, the system gracefully blocks the hard deletion to preserve student history, opting for soft-deletions (archiving) when applicable.

---

## 1. User Directory (Users Tab)
Manage all platform users, their roles, and their platform access.

**Features:**
- **Search & Filter**: Real-time filtering by user name or email address.
- **Role Management**: Instantly toggle a user's role between *Student* and *Staff Admin*. (*Superusers are protected and can only be modified via Django Admin*).
- **Access Control**: Suspend or Activate users with a single click. Suspended users receive a red badge and their access is revoked.
- **Data Display**: Shows avatar initials, role (Superuser/Staff/Student), status, and join date.

## 2. Curriculum Tracks (Tracks Tab)
The highest level of the educational hierarchy. Tracks represent broad subjects (e.g., "Frontend Engineering", "Data Structures").

**Features:**
- **Create & Edit**: Define Track names and descriptions.
- **Aggregated Analytics**: Displays the total number of Topics and Questions within the track, along with a platform-wide student completion percentage.
- **Safe Delete**: You cannot delete a track until its associated topics are deleted or reassigned.

## 3. Topics (Topics Tab)
Topics are specific sub-sections that belong to a Track (e.g., "React Hooks" under "Frontend Engineering").

**Features:**
- **Create & Edit**: Assign to a parent Track, define the Topic name, description, and the numerical order/sequence.
- **Data Display**: Shows the parent Track name as a badge, the sequence order, and the total questions associated with it.
- **Archiving Logic**: If a topic is deleted but students have already completed progress on it, it is safely "Archived" (soft-deleted) in the database rather than destroyed.

## 4. Question Bank (Questions Tab)
The global repository of multiple-choice questions used for mock tests and practice.

**Features:**
- **Create & Edit**: Link to a parent Topic. Define the question text, four options (A, B, C, D), select the correct answer, and assign a difficulty level (Easy, Medium, Hard).
- **Data Display**: The table truncates long question text cleanly and displays color-coded badges for difficulty. It explicitly shows the path `Track > Topic` to easily identify where the question belongs.
- **Safe Delete**: Questions with existing student answers cannot be deleted to prevent corrupting historical analytics.

## 5. Mock Tests (Tests Tab)
Assessments that group together topics for students to practice against a timer.

**Features:**
- **Create & Edit**: Define Test Name, Description, and Duration (in minutes).
- **Topic Assignment**: Multi-select interface to assign one or multiple Topics to the test. The backend automatically pools questions from these assigned topics.
- **Safe Delete**: Tests that have been attempted by students cannot be deleted.

## 6. Company Targets (Companies Tab)
Allows administrators to map and track specific corporate placement goals for individual users.

**Features:**
- **Create & Assign**: Assign a target company (e.g., "Google") to a specific user, and define their Preparation Focus Area (e.g., "System Design").
- **Readiness Scoring**: Admins can override the "Readiness Score" (0-100). The table renders a visual progress bar (Red < 50%, Amber 50-70%, Green > 70%).
- **Archiving UI**: When deleted, Company Targets are soft-deleted. They remain in the table but are visually faded out with a red **Archived** badge.

---

### Technical Notes for Developers
- **Endpoint**: `/admin/overview/` provides aggregated payloads for the initial load.
- **Routing**: Handled via `AdminPage.jsx` on the frontend and `admin_views.py` (via `core/urls.py`) on the Django backend.
- **Styling**: Relies entirely on `admin.css` utilizing CSS variables for seamless Light/Dark mode integration.
