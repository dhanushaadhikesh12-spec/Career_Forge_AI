import { useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Menu, Bell, Shield, GraduationCap } from 'lucide-react';

interface TopbarProps {
  onToggleMobileMenu: () => void;
}

export function Topbar({ onToggleMobileMenu }: TopbarProps) {
  const { user } = useAuth();
  const location = useLocation();

  // Compute clean breadcrumb / title from path
  const getBreadcrumb = () => {
    const path = location.pathname;
    if (path.includes('/student/dashboard')) return 'Student Workspace / Dashboard';
    if (path.includes('/student/learn')) return 'Learning Hub / Curriculum Explorer';
    if (path.includes('/student/topics/')) return 'Learning Hub / Topic Deep Dive';
    if (path.includes('/student/practice')) return 'Aptitude / Adaptive Practice Session';
    if (path.includes('/student/coding/submissions')) return 'Coding / My Submissions';
    if (path.includes('/student/coding/assessments/')) return 'Assessments / Coding Assessment';
    if (path.includes('/student/coding/')) return 'Coding Practice / Problem Workspace';
    if (path.includes('/student/coding')) return 'Coding / Problem Explorer';
    if (path.includes('/student/tests/results/')) return 'Assessments / Test Scorecard';
    if (path.includes('/student/tests/session/')) return 'Assessments / Active Assessment';
    if (path.includes('/student/tests')) return 'Assessments / Standard Tests';
    if (path.includes('/trainer/dashboard')) return 'Trainer Portal / Cohort Overview';
    if (path.includes('/trainer/assistant')) return 'Trainer Portal / AI Academic Assistant';
    if (path.includes('/trainer/batches')) return 'Trainer Portal / Batches & Students';
    if (path.includes('/trainer/analytics')) return 'Trainer Portal / Cohort Performance Analytics';
    if (path.includes('/trainer/students/')) return 'Trainer Portal / Student Performance Profile';
    return 'CareerForge / Placement Preparation';
  };

  const isStudent = user?.role === 'STUDENT';

  return (
    <header className="h-14 bg-slate-950/80 border-b border-slate-800/80 sticky top-0 z-30 px-4 md:px-6 flex items-center justify-between backdrop-blur-sm select-none">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleMobileMenu}
          className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          aria-label="Toggle navigation"
        >
          <Menu size={20} />
        </button>
        <div className="text-xs font-medium text-slate-400 hidden sm:flex items-center gap-1.5">
          <span className="text-slate-500">Workspace</span>
          <span className="text-slate-600">/</span>
          <span className="text-slate-200 font-semibold">{getBreadcrumb()}</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[11px] text-slate-400">
          <span className="w-2 h-2 rounded-full bg-teal-500 animate-pulse" />
          <span>System Online</span>
        </div>

        <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
          <div className="w-7 h-7 rounded-full bg-navy-800 border border-teal-500/30 flex items-center justify-center text-xs font-semibold text-teal-300">
            {user?.full_name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-medium text-slate-200 leading-tight">
              {user?.full_name?.split(' ')[0] || 'User'}
            </div>
            <div className="text-[10px] text-slate-400 leading-tight">
              {isStudent ? 'Student' : 'Trainer'}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
