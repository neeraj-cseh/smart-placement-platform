# Frontend Architecture

## Overview
React SPA with decentralized state management.

## Routing
react-router-dom v7 with Nested Ecosystems.

vements**: "Streak Freeze" items.

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
* **Data