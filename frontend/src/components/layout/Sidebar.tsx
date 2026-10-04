import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  LayoutDashboard, BookOpen, Brain, ClipboardList,
  BarChart3, Users, Settings, LogOut, Zap, ChevronRight,
  GraduationCap, Code2, Trophy, Sparkles,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const STUDENT_NAV: NavItem[] = [
  { to: '/student/dashboard', icon: <LayoutDashboard size={18} />, label: 'Dashboard' },
  { to: '/student/learn', icon: <BookOpen size={18} />, label: 'Learning Hub' },
  { to: '/student/practice', icon: <Brain size={18} />, label: 'Aptitude Practice' },
  { to: '/student/coding', icon: <Code2 size={18} />, label: 'Coding Practice' },
  { to: '/student/tests', icon: <ClipboardList size={18} />, label: 'Assessments' },
];

const TRAINER_NAV: NavItem[] = [
  { to: '/trainer/dashboard', icon: <LayoutDashboard size={18} />, label: 'Dashboard' },
  { to: '/trainer/assistant', icon: <Sparkles size={18} />, label: 'AI Assistant' },
  { to: '/trainer/batches', icon: <Users size={18} />, label: 'Batches' },
  { to: '/trainer/tests', icon: <ClipboardList size={18} />, label: 'Tests' },
  { to: '/trainer/analytics', icon: <BarChart3 size={18} />, label: 'Analytics' },
];

export function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const isStudent = user?.role === 'STUDENT';
  const nav = isStudent ? STUDENT_NAV : TRAINER_NAV;

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-card/80 backdrop-blur-xl border-r border-border flex flex-col z-40">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-gradient-to-br from-forge-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-forge-500/30">
            <Zap size={18} className="text-white" />
          </div>
          <div>
            <div className="font-bold text-sm font-display tracking-tight">CareerForge</div>
            <div className="text-xs text-muted-foreground">AI Platform</div>
          </div>
        </div>
      </div>

      {/* User info */}
      <div className="px-4 py-4 border-b border-border">
        <div className="flex items-center gap-3 p-3 glass-card rounded-xl">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-forge-500/30 to-purple-500/30 flex items-center justify-center text-sm font-bold text-forge-300">
            {user?.full_name?.charAt(0) ?? '?'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">{user?.full_name}</div>
            <div className={cn('text-xs', isStudent ? 'text-forge-400' : 'text-purple-400')}>
              {isStudent ? (
                <span className="flex items-center gap-1"><GraduationCap size={10} /> Student</span>
              ) : (
                <span className="flex items-center gap-1"><Trophy size={10} /> Trainer</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn('nav-item', isActive && 'active')
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom actions */}
      <div className="p-3 border-t border-border space-y-1">
        <button
          onClick={handleLogout}
          className="nav-item w-full text-red-400 hover:text-red-300 hover:bg-red-500/10"
        >
          <LogOut size={18} />
          <span>Log Out</span>
        </button>
      </div>
    </aside>
  );
}
