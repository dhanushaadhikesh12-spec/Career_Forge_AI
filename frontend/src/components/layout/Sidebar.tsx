import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard, BookOpen, Brain, ClipboardList,
  BarChart3, Users, LogOut, Code2, Sparkles,
  GraduationCap, ShieldCheck
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const STUDENT_NAV: NavItem[] = [
  { to: '/student/dashboard', icon: <LayoutDashboard size={17} />, label: 'Dashboard' },
  { to: '/student/learn', icon: <BookOpen size={17} />, label: 'Learning Hub' },
  { to: '/student/practice', icon: <Brain size={17} />, label: 'Aptitude Practice' },
  { to: '/student/coding', icon: <Code2 size={17} />, label: 'Coding Practice' },
  { to: '/student/tests', icon: <ClipboardList size={17} />, label: 'Assessments' },
];

const TRAINER_NAV: NavItem[] = [
  { to: '/trainer/dashboard', icon: <LayoutDashboard size={17} />, label: 'Cohort Dashboard' },
  { to: '/trainer/assistant', icon: <Sparkles size={17} />, label: 'AI Trainer' },
  { to: '/trainer/batches', icon: <Users size={17} />, label: 'Batches' },
  { to: '/trainer/tests', icon: <ClipboardList size={17} />, label: 'Assessments' },
  { to: '/trainer/analytics', icon: <BarChart3 size={17} />, label: 'Analytics' },
];

interface SidebarProps {
  onCloseMobile?: () => void;
}

export function Sidebar({ onCloseMobile }: SidebarProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const isStudent = user?.role === 'STUDENT';
  const nav = isStudent ? STUDENT_NAV : TRAINER_NAV;

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside className="h-full w-64 bg-slate-950/90 border-r border-slate-800/80 flex flex-col z-40 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-navy-800 border border-teal-500/40 flex items-center justify-center text-teal-400 font-bold text-sm shadow-subtle">
            CF
          </div>
          <div className="min-w-0">
            <div className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5 font-display">
              CAREERFORGE
            </div>
            <div className="text-[11px] text-slate-400 font-normal truncate">
              Placement Preparation
            </div>
          </div>
        </div>
      </div>

      {/* Role & User Badge */}
      <div className="px-4 py-3 border-b border-slate-800/60 bg-slate-900/40">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-md bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-semibold text-slate-200 shrink-0">
            {user?.full_name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-medium text-slate-200 truncate leading-snug">
              {user?.full_name || 'User'}
            </div>
            <div className="text-[10px] text-slate-400 flex items-center gap-1">
              {isStudent ? (
                <>
                  <GraduationCap size={11} className="text-teal-400" />
                  <span>Student Workspace</span>
                </>
              ) : (
                <>
                  <ShieldCheck size={11} className="text-amber-400" />
                  <span>Trainer Portal</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Nav Section */}
      <div className="px-4 pt-3 pb-1">
        <span className="text-[10px] font-semibold tracking-wider uppercase text-slate-500">
          Navigation
        </span>
      </div>
      <nav className="flex-1 px-3 py-1 space-y-1 overflow-y-auto">
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onCloseMobile}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                isActive
                  ? 'bg-navy-800 text-white border border-slate-700/80 shadow-subtle font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/70'
              )
            }
          >
            <span className="shrink-0">{item.icon}</span>
            <span className="truncate">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer / Logout */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/60">
        <button
          onClick={handleLogout}
          className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-red-300 hover:bg-red-950/20 transition-colors"
        >
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
