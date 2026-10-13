import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { AppLayout } from '@/components/layout/AppLayout';
import { ToastContainer, LoadingSpinner } from '@/components/shared';

// Auth Pages
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';

// Student Pages
import StudentDashboardPage from '@/pages/student/StudentDashboardPage';
import LearnPage from '@/pages/student/LearnPage';
import TopicDetailPage from '@/pages/student/TopicDetailPage';
import PracticePage from '@/pages/student/PracticePage';
import TestsListPage from '@/pages/student/TestsListPage';
import TestSessionPage from '@/pages/student/TestSessionPage';
import TestResultPage from '@/pages/student/TestResultPage';
import CodingPracticePage from '@/pages/student/CodingPracticePage';
import CodingProblemPage from '@/pages/student/CodingProblemPage';
import CodingSubmissionsPage from '@/pages/student/CodingSubmissionsPage';
import CodingAssessmentPage from '@/pages/student/CodingAssessmentPage';
import StudentAICoachPage from '@/pages/student/StudentAICoachPage';

// Trainer Pages
import TrainerDashboardPage from '@/pages/trainer/TrainerDashboardPage';
import BatchesPage from '@/pages/trainer/BatchesPage';
import TrainerAnalyticsPage from '@/pages/trainer/TrainerAnalyticsPage';
import TrainerStudentProfilePage from '@/pages/trainer/TrainerStudentProfilePage';
import TrainerAIAssistantPage from '@/pages/trainer/TrainerAIAssistantPage';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to their default dashboard if role not allowed
    if (user.role === 'TRAINER' || user.role === 'ADMIN') {
      return <Navigate to="/trainer/dashboard" replace />;
    }
    return <Navigate to="/student/dashboard" replace />;
  }

  return <>{children}</>;
}

function RootRedirect() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === 'TRAINER' || user.role === 'ADMIN') {
    return <Navigate to="/trainer/dashboard" replace />;
  }

  return <Navigate to="/student/dashboard" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <ToastContainer />
        <Routes>
          {/* Public Authentication */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<RootRedirect />} />

          {/* Proctored Assessment Sessions: Distraction-free full screen */}
          <Route
            path="/student/tests/session/:testId"
            element={
              <ProtectedRoute allowedRoles={['STUDENT', 'TRAINER', 'ADMIN']}>
                <TestSessionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/student/coding/assessments/:testId"
            element={
              <ProtectedRoute allowedRoles={['STUDENT', 'TRAINER', 'ADMIN']}>
                <CodingAssessmentPage />
              </ProtectedRoute>
            }
          />

          {/* Student Routes with AppLayout */}
          <Route
            path="/student/*"
            element={
              <ProtectedRoute allowedRoles={['STUDENT', 'TRAINER', 'ADMIN']}>
                <AppLayout>
                  <Routes>
                    <Route path="dashboard" element={<StudentDashboardPage />} />
                    <Route path="coach" element={<StudentAICoachPage />} />
                    <Route path="assistant" element={<StudentAICoachPage />} />
                    <Route path="learn" element={<LearnPage />} />
                    <Route path="topics/:topicId" element={<TopicDetailPage />} />
                    <Route path="practice" element={<PracticePage />} />
                    <Route path="coding" element={<CodingPracticePage />} />
                    <Route path="coding/submissions" element={<CodingSubmissionsPage />} />
                    <Route path="coding/:slug" element={<CodingProblemPage />} />
                    <Route path="tests" element={<TestsListPage />} />
                    <Route path="tests/results/:attemptId" element={<TestResultPage />} />
                    <Route path="*" element={<Navigate to="/student/dashboard" replace />} />
                  </Routes>
                </AppLayout>
              </ProtectedRoute>
            }
          />

          {/* Trainer Routes with AppLayout */}
          <Route
            path="/trainer/*"
            element={
              <ProtectedRoute allowedRoles={['TRAINER', 'ADMIN']}>
                <AppLayout>
                  <Routes>
                    <Route path="dashboard" element={<TrainerDashboardPage />} />
                    <Route path="assistant" element={<TrainerAIAssistantPage />} />
                    <Route path="batches" element={<BatchesPage />} />
                    <Route path="analytics" element={<TrainerAnalyticsPage />} />
                    <Route path="analytics/students/:studentId" element={<TrainerStudentProfilePage />} />
                    <Route path="students/:studentId" element={<TrainerStudentProfilePage />} />
                    <Route path="*" element={<Navigate to="/trainer/dashboard" replace />} />
                  </Routes>
                </AppLayout>
              </ProtectedRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
