import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import { AIAssistant } from './ai/AIAssistant';

// Ecosystem Layouts
import { 
  PrepLayout, 
  CodeLabLayout, 
  AICoachLayout, 
  CareerLayout, 
  ProfileLayout 
} from './components/ecosystems/EcosystemLayouts';

// Lazy load pages
const AuthPage = lazy(() => import('./pages/AuthPage'));
const LandingPage = lazy(() => import('./pages/LandingPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const LearningPathPage = lazy(() => import('./pages/LearningPathPage'));
const PrepPage = lazy(() => import('./pages/PrepPage'));
const MockTestsPage = lazy(() => import('./pages/MockTestsPage'));
const TopicStudyPage = lazy(() => import('./pages/TopicStudyPage'));

const CodingWorkspacePage = lazy(() => import('./pages/CodingWorkspacePage'));
const ProblemArenaPage = lazy(() => import('./pages/ProblemArenaPage'));
const ProblemSolvingPage = lazy(() => import('./pages/ProblemSolvingPage'));
const ContestHubPage = lazy(() => import('./pages/ContestHubPage'));
const AIInterviewPage = lazy(() => import('./pages/AIInterviewPage'));
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));
const CompaniesPage = lazy(() => import('./pages/CompaniesPage'));
const CompanyDetailPage = lazy(() => import('./pages/CompanyDetailPage'));
const PassportPage = lazy(() => import('./pages/PassportPage'));
const SharedPassportPage = lazy(() => import('./pages/SharedPassportPage'));
const PortfolioPage = lazy(() => import('./pages/PortfolioPage'));
const SharedPortfolioPage = lazy(() => import('./pages/SharedPortfolioPage'));
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

  if (user) return <Navigate to={user.is_admin ? '/admin' : '/'} replace />;

  return children;
}

function HomeRoute() {
  const { user, loading } = useAuth();

  if (loading) return routeFallback;

  if (!user) return <LandingPage />;
  return user.is_admin ? <AdminPage /> : <DashboardPage />;
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <BrowserRouter>
            <Suspense fallback={routeFallback}>
              <Routes>
                {/* Global Entry */}
                <Route path="/" element={<HomeRoute />} />
                <Route path="/landing" element={<LandingPage />} />
                <Route path="/login" element={<PublicRoute><AuthPage mode="login" /></PublicRoute>} />
                <Route path="/signup" element={<PublicRoute><AuthPage mode="signup" /></PublicRoute>} />
                
                {/* Legacy Standalone redirects to Dashboard (temporarily mapping old analytics) */}
                <Route path="/analytics" element={<ProtectedRoute><AnalyticsPage /></ProtectedRoute>} />

                {/* 2. Prep Ecosystem */}
                <Route path="/prep" element={<ProtectedRoute><PrepLayout /></ProtectedRoute>}>
                  <Route index element={<Navigate to="journey" replace />} />
                  <Route path="journey" element={<PrepPage />} />
                  <Route path="roadmaps" element={<LearningPathPage />} />
                  <Route path="milestones" element={<MockTestsPage />} />
                  <Route path="topic/:slug" element={<TopicStudyPage />} />
                </Route>

                {/* 3. Code Lab Ecosystem */}
                <Route path="/code-lab" element={<ProtectedRoute><CodeLabLayout /></ProtectedRoute>}>
                  <Route index element={<Navigate to="arena" replace />} />
                  <Route path="arena" element={<ProblemArenaPage />} />
                  <Route path="arena/:slug" element={<ProblemSolvingPage />} />
                  <Route path="workspace" element={<CodingWorkspacePage />} />
                  <Route path="contests" element={<ContestHubPage />} />
                </Route>

                {/* 4. AI Coach Ecosystem */}
                <Route path="/ai" element={<ProtectedRoute><AICoachLayout /></ProtectedRoute>}>
                  <Route index element={<Navigate to="interview" replace />} />
                  <Route path="interview" element={<AIInterviewPage />} />
                </Route>

                {/* 5. Career Ecosystem */}
                <Route path="/career" element={<ProtectedRoute><CareerLayout /></ProtectedRoute>}>
                  <Route index element={<Navigate to="companies" replace />} />
                  <Route path="companies" element={<CompaniesPage />} />
                  <Route path="companies/:name" element={<CompanyDetailPage />} />
                </Route>
                {/* Public Shared Career Routes */}
                <Route path="/portfolio/shared/:slug" element={<SharedPortfolioPage />} />

                <Route path="/profile" element={<ProtectedRoute><ProfileLayout /></ProtectedRoute>}>
                  <Route index element={<Navigate to="passport" replace />} />
                  <Route path="passport" element={<PassportPage />} />
                  <Route path="me" element={<ProfilePage />} />
                </Route>
                {/* Public Shared Profile Routes */}
                <Route path="/passport/shared/:token" element={<SharedPassportPage />} />

                {/* Global Settings & Admin */}
                <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />
                <Route path="/admin" element={<ProtectedRoute adminOnly><AdminPage /></ProtectedRoute>} />
                
                {/* Fallback */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Suspense>
            {/* Global AI Assistant */}
            <AIAssistant />
          </BrowserRouter>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
