import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';

const AuthPage = lazy(() => import('./pages/AuthPage'));
const LandingPage = lazy(() => import('./pages/LandingPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const LearningPathPage = lazy(() => import('./pages/LearningPathPage'));
const PracticePage = lazy(() => import('./pages/PracticePage'));
const MockTestsPage = lazy(() => import('./pages/MockTestsPage'));
const CodeEditorPage = lazy(() => import('./pages/CodeEditorPage'));
const AIInterviewPage = lazy(() => import('./pages/AIInterviewPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const CompaniesPage = lazy(() => import('./pages/CompaniesPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const AdminPage = lazy(() => import('./pages/AdminPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));

const routeFallback = (
  <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    Loading...
  </div>
);

function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth();

  if (loading) return routeFallback;

  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && !user.is_admin) return <Navigate to="/" replace />;

  return children;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return routeFallback;

  if (user) return <Navigate to="/" replace />;

  return children;
}

function HomeRoute() {
  const { user, loading } = useAuth();

  if (loading) return routeFallback;

  return user ? <DashboardPage /> : <LandingPage />;
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Suspense fallback={routeFallback}>
            <Routes>
              <Route path="/" element={<HomeRoute />} />
              <Route path="/landing" element={<LandingPage />} />
              <Route path="/login" element={<PublicRoute><AuthPage mode="login" /></PublicRoute>} />
              <Route path="/signup" element={<PublicRoute><AuthPage mode="signup" /></PublicRoute>} />
              <Route path="/learning-path" element={<ProtectedRoute><LearningPathPage /></ProtectedRoute>} />
              <Route path="/practice" element={<ProtectedRoute><PracticePage /></ProtectedRoute>} />
              <Route path="/mock-tests" element={<ProtectedRoute><MockTestsPage /></ProtectedRoute>} />
              <Route path="/code-editor" element={<ProtectedRoute><CodeEditorPage /></ProtectedRoute>} />
              <Route path="/ai-interview" element={<ProtectedRoute><AIInterviewPage /></ProtectedRoute>} />
              <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />
              <Route path="/companies" element={<ProtectedRoute><CompaniesPage /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
              <Route path="/admin" element={<ProtectedRoute adminOnly><AdminPage /></ProtectedRoute>} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
