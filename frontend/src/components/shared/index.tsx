import { ReactNode, useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle2, ChevronRight, Info, XCircle } from 'lucide-react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  breadcrumb?: string;
  className?: string;
}

export function PageHeader({ title, subtitle, action, breadcrumb, className }: PageHeaderProps) {
  return (
    <div className={cn('flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 pb-4 border-b border-border/70', className)}>
      <div>
        {breadcrumb && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-1.5 font-medium">
            <span>Workspace</span>
            <ChevronRight size={12} className="text-slate-600" />
            <span className="text-slate-300">{breadcrumb}</span>
          </div>
        )}
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground">{title}</h1>
        {subtitle && <p className="mt-1 text-xs sm:text-sm text-muted-foreground max-w-2xl leading-relaxed">{subtitle}</p>}
      </div>
      {action && <div className="flex items-center gap-2.5 shrink-0">{action}</div>}
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  trend?: string;
  trendUp?: boolean;
  color?: 'blue' | 'purple' | 'green' | 'orange' | 'teal' | 'navy';
  className?: string;
}

const statColorMap = {
  navy: 'text-sky-400 bg-sky-950/40 border-sky-800/40',
  blue: 'text-sky-400 bg-sky-950/40 border-sky-800/40',
  teal: 'text-teal-400 bg-teal-950/40 border-teal-800/40',
  purple: 'text-indigo-400 bg-indigo-950/40 border-indigo-800/40',
  green: 'text-emerald-400 bg-emerald-950/40 border-emerald-800/40',
  orange: 'text-amber-400 bg-amber-950/40 border-amber-800/40',
};

export function StatCard({ label, value, icon, trend, trendUp, color = 'navy', className }: StatCardProps) {
  const iconStyle = statColorMap[color] || statColorMap.navy;
  return (
    <div className={cn('clean-card p-5 hover:border-slate-600/70 transition-all duration-150', className)}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-muted-foreground tracking-wide">{label}</span>
        <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center border', iconStyle)}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold tracking-tight text-foreground">{value}</div>
      {trend && (
        <div className="mt-2 flex items-center gap-1.5 text-xs">
          <span className={cn('font-semibold', trendUp ? 'text-emerald-400' : 'text-amber-400')}>
            {trendUp ? '↑' : '↓'}
          </span>
          <span className="text-muted-foreground truncate">{trend}</span>
        </div>
      )}
    </div>
  );
}

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  label?: string;
}

export function LoadingSpinner({ size = 'md', className, label }: LoadingSpinnerProps) {
  const sizeClass = { sm: 'w-4 h-4 border-2', md: 'w-6 h-6 border-2', lg: 'w-10 h-10 border-3' }[size];
  return (
    <div className={cn('flex flex-col items-center justify-center p-8 gap-3 text-muted-foreground text-xs', className)}>
      <div className={cn(sizeClass, 'border-slate-700 border-t-teal-500 rounded-full animate-spin')} />
      {label && <span>{label}</span>}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="clean-card p-5 space-y-3 animate-pulse">
      <div className="h-3 w-1/3 bg-slate-800/80 rounded" />
      <div className="h-7 w-1/2 bg-slate-800/90 rounded" />
      <div className="h-2.5 w-2/3 bg-slate-800/60 rounded" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="clean-card p-4 space-y-3 animate-pulse">
      <div className="h-5 bg-slate-800/80 rounded w-1/4 mb-4" />
      {Array.from({ length: rows }).map((_, idx) => (
        <div key={idx} className="flex gap-4 items-center">
          <div className="h-4 bg-slate-800/70 rounded w-1/3" />
          <div className="h-4 bg-slate-800/50 rounded w-1/4" />
          <div className="h-4 bg-slate-800/40 rounded w-1/4" />
          <div className="h-4 bg-slate-800/60 rounded w-16 ml-auto" />
        </div>
      ))}
    </div>
  );
}

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('clean-card p-10 flex flex-col items-center justify-center text-center', className)}>
      {icon && <div className="text-muted-foreground/60 mb-3">{icon}</div>}
      <h3 className="text-sm font-semibold text-foreground mb-1">{title}</h3>
      {description && <p className="text-xs text-muted-foreground max-w-sm leading-relaxed mb-4">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
}

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({ message, onRetry, className }: ErrorStateProps) {
  return (
    <div className={cn('clean-card border-red-500/30 bg-red-950/10 p-6 text-center max-w-md mx-auto my-6', className)}>
      <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
      <p className="text-xs font-semibold text-red-300 mb-1">Unable to Load Data</p>
      <p className="text-xs text-muted-foreground mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3.5 py-1.5 text-xs bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors border border-red-500/30 font-medium"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

interface BadgeProps {
  children: ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'purple' | 'teal' | 'neutral';
  className?: string;
}

export function Badge({ children, variant = 'neutral', className }: BadgeProps) {
  const variantClass = {
    success: 'badge-success',
    warning: 'badge-warning',
    error: 'badge-error',
    info: 'badge-info',
    purple: 'badge-teal',
    teal: 'badge-teal',
    neutral: 'badge-neutral',
  }[variant] || 'badge-neutral';

  return <span className={cn(variantClass, className)}>{children}</span>;
}

interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({ value, max = 100, color = 'bg-teal-500', showLabel = false, className }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, Math.round((value / max) * 100)));
  return (
    <div className={cn('w-full', className)}>
      <div className="progress-track h-1.5">
        <div className={cn('progress-fill h-full', color)} style={{ width: `${pct}%` }} />
      </div>
      {showLabel && <div className="text-[11px] text-muted-foreground mt-1 font-medium">{pct}%</div>}
    </div>
  );
}

interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

let toastCallback: ((t: ToastMessage) => void) | null = null;

export function useToast() {
  const toast = useCallback((type: 'success' | 'error' | 'info', message: string) => {
    toastCallback?.({ id: Date.now().toString(), type, message });
  }, []);
  return { toast };
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  toastCallback = (t) => {
    setToasts((prev) => [...prev, t]);
    setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== t.id)), 3500);
  };

  const typeConfig = {
    success: { bg: 'bg-slate-900 border-emerald-500/40 text-emerald-300', icon: <CheckCircle2 size={15} className="text-emerald-400" /> },
    error: { bg: 'bg-slate-900 border-red-500/40 text-red-300', icon: <XCircle size={15} className="text-red-400" /> },
    info: { bg: 'bg-slate-900 border-teal-500/40 text-teal-300', icon: <Info size={15} className="text-teal-400" /> },
  };

  return (
    <div className="fixed bottom-5 right-5 z-50 space-y-2 pointer-events-none">
      {toasts.map((t) => {
        const cfg = typeConfig[t.type];
        return (
          <div
            key={t.id}
            className={cn(
              'flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg border shadow-modal pointer-events-auto text-xs font-medium animate-fade-in',
              cfg.bg
            )}
          >
            <span>{cfg.icon}</span>
            <span>{t.message}</span>
          </div>
        );
      })}
    </div>
  );
}
