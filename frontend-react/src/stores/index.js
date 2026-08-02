/**
 * PrepSmart — Zustand Global Stores
 * Central state management for all UI & data domains.
 * Import individual stores — never import the whole file.
 *
 * Usage:
 *   import { useUIStore } from '@/stores';
 *   const { theme, setTheme } = useUIStore();
 */

import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';

/* ─────────────────────────────────────────────────────────────────
   1. UI STORE — theme, sidebar, toasts, modals
   ───────────────────────────────────────────────────────────────── */
export const useUIStore = create(
  persist(
    (set, get) => ({
      /* Theme */
      theme: 'dark',
      setTheme: (theme) => {
        set({ theme });
        document.documentElement.setAttribute('data-theme', theme);
      },
      toggleTheme: () => {
        const next = get().theme === 'dark' ? 'light' : 'dark';
        get().setTheme(next);
      },

      /* Sidebar */
      sidebarOpen:      false,
      sidebarCollapsed: false,
      setSidebarOpen:      (v) => set({ sidebarOpen: v }),
      setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

      /* Active route accent (company theme) */
      accentCompany: null,
      setAccentCompany: (company) => set({ accentCompany: company }),

      /* Toast notifications */
      toasts: [],
      addToast: (toast) => {
        const id = Date.now();
        set((s) => ({ toasts: [...s.toasts, { id, ...toast }] }));
        // Auto-dismiss after duration (default 4s)
        setTimeout(() => {
          set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
        }, toast.duration ?? 4000);
        return id;
      },
      removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
      clearToasts: () => set({ toasts: [] }),

      /* Active modal */
      activeModal: null,
      modalProps:  {},
      openModal:  (name, props = {}) => set({ activeModal: name, modalProps: props }),
      closeModal: () => set({ activeModal: null, modalProps: {} }),

      /* Command palette */
      commandOpen: false,
      setCommandOpen: (v) => set({ commandOpen: v }),
    }),
    {
      name: 'prepsmart-ui',
      partialize: (s) => ({ theme: s.theme, sidebarCollapsed: s.sidebarCollapsed }),
    }
  )
);

/* ─────────────────────────────────────────────────────────────────
   2. AI ASSISTANT STORE
   ───────────────────────────────────────────────────────────────── */
export const useAIStore = create(
  subscribeWithSelector((set) => ({
    /* Panel state */
    isOpen:     false,
    isMinimized:false,
    open:       () => set({ isOpen: true, isMinimized: false }),
    close:      () => set({ isOpen: false }),
    minimize:   () => set({ isMinimized: true }),
    restore:    () => set({ isMinimized: false }),
    toggle:     () => set((s) => ({ isOpen: !s.isOpen })),

    /* Conversation */
    messages: [],
    isTyping: false,
    context:  null,   /* Current module context: 'dashboard' | 'practice' | etc. */

    setContext: (ctx) => set({ context: ctx }),

    addMessage: (msg) =>
      set((s) => ({
        messages: [
          ...s.messages,
          { id: Date.now(), timestamp: new Date().toISOString(), ...msg },
        ],
      })),

    setTyping: (v) => set({ isTyping: v }),
    clearChat: () => set({ messages: [] }),

    /* Quick suggestions (context-aware) */
    suggestions: [
      '🎯 Generate a 7-day study plan',
      '📊 Analyze my weak areas',
      '🧩 Create a DP practice set',
      '💼 What should I focus on for Amazon?',
    ],
    setSuggestions: (s) => set({ suggestions: s }),

    /* Streaming state */
    streamActive:  false,
    streamContent: '',
    startStream:   () => set({ streamActive: true, streamContent: '' }),
    appendStream:  (chunk) => set((s) => ({ streamContent: s.streamContent + chunk })),
    endStream:     () => set({ streamActive: false }),
  }))
);

/* ─────────────────────────────────────────────────────────────────
   3. DASHBOARD STORE — widget layout, filters, preferences
   ───────────────────────────────────────────────────────────────── */
export const useDashboardStore = create(
  persist(
    (set) => ({
      /* Widget visibility toggles */
      widgetVisibility: {
        hero:         true,
        stats:        true,
        mission:      true,
        momentum:     true,
        companies:    true,
        skills:       true,
        activity:     true,
        recommendations: true,
        streak:       true,
        productivity: true,
        events:       true,
      },
      toggleWidget: (key) =>
        set((s) => ({
          widgetVisibility: {
            ...s.widgetVisibility,
            [key]: !s.widgetVisibility[key],
          },
        })),

      /* Time filter for analytics */
      timeRange: '7d',
      setTimeRange: (r) => set({ timeRange: r }),

      /* Target company for hero */
      focusCompany: null,
      setFocusCompany: (c) => set({ focusCompany: c }),

      /* Daily task completion (persisted) */
      completedTasks: {},
      toggleTask: (id) =>
        set((s) => ({
          completedTasks: { ...s.completedTasks, [id]: !s.completedTasks[id] },
        })),
      resetDailyTasks: () => set({ completedTasks: {} }),

      /* XP local state */
      sessionXP: 0,
      addXP: (amount) => set((s) => ({ sessionXP: s.sessionXP + amount })),
    }),
    {
      name: 'prepsmart-dashboard',
      partialize: (s) => ({
        widgetVisibility: s.widgetVisibility,
        timeRange:        s.timeRange,
        focusCompany:     s.focusCompany,
        completedTasks:   s.completedTasks,
      }),
    }
  )
);

/* ─────────────────────────────────────────────────────────────────
   4. NOTIFICATIONS STORE
   ───────────────────────────────────────────────────────────────── */
export const useNotificationStore = create(
  persist(
    (set) => ({
      notifications: [],
      unreadCount:   0,

      addNotification: (notif) =>
        set((s) => ({
          notifications: [
            { id: Date.now(), read: false, timestamp: new Date().toISOString(), ...notif },
            ...s.notifications,
          ],
          unreadCount: s.unreadCount + 1,
        })),

      markRead: (id) =>
        set((s) => ({
          notifications: s.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
          unreadCount: Math.max(0, s.unreadCount - 1),
        })),

      markAllRead: () =>
        set((s) => ({
          notifications: s.notifications.map((n) => ({ ...n, read: true })),
          unreadCount: 0,
        })),

      clearAll: () => set({ notifications: [], unreadCount: 0 }),
    }),
    { name: 'prepsmart-notifications', partialize: (s) => ({ notifications: s.notifications }) }
  )
);

/* ─────────────────────────────────────────────────────────────────
   5. PRACTICE STORE — active session, filters, streak
   ───────────────────────────────────────────────────────────────── */
export const usePracticeStore = create(
  persist(
    (set) => ({
      /* Filters */
      difficulty:  'all',
      topic:       'all',
      status:      'all',
      setFilter: (key, val) => set({ [key]: val }),
      resetFilters: () => set({ difficulty: 'all', topic: 'all', status: 'all' }),

      /* Active session */
      activeSession: null,
      sessionStart:  null,
      startSession:  (problem) => set({ activeSession: problem, sessionStart: Date.now() }),
      endSession:    () => set({ activeSession: null, sessionStart: null }),

      /* Solved history (local) */
      solvedProblems: [],
      markSolved: (id) =>
        set((s) => ({
          solvedProblems: s.solvedProblems.includes(id)
            ? s.solvedProblems
            : [...s.solvedProblems, id],
        })),
    }),
    {
      name: 'prepsmart-practice',
      partialize: (s) => ({ solvedProblems: s.solvedProblems }),
    }
  )
);

/* ─────────────────────────────────────────────────────────────────
   6. REALTIME STORE — websocket events, live activity
   ───────────────────────────────────────────────────────────────── */
export const useRealtimeStore = create((set) => ({
  connected:    false,
  liveActivity: [],
  liveEvents:   [],

  setConnected:    (v) => set({ connected: v }),
  pushActivity:    (item) => set((s) => ({ liveActivity: [item, ...s.liveActivity].slice(0, 20) })),
  pushEvent:       (evt)  => set((s) => ({ liveEvents:   [evt,  ...s.liveEvents  ].slice(0, 50) })),
  clearActivity:   () => set({ liveActivity: [] }),
}));
