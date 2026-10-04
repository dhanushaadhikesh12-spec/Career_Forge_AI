import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
}

export function PageHeader({ title, subtitle, action, className }: PageHeaderProps) {
  return (
    <div className={cn('flex items-start justify-between mb-8', className)}>
      <div>
        <h1 className="text-2xl font-bold font-display gradient-text">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string | number;
  icon: ReactNode;
  trend?: string;
  trendUp?: boolean;
  color?: 'blue' | 'purple' | 'green' | 'orange';
}

const colorMap = {
  blue: 'from-forge-500/20 to-blue-500/10 border-forge-500/30 text-forge-400',
  purple: 'from-purple-500/20 to-violet-500/10 border-purple-500/30 text-purple-400',
  green: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-400',
  orange: 'from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-400',
};

export function StatCard({ label, value, icon, trend, trendUp, color = 'blue' }: StatCardProps) {
  const colors = colorMap[color];
  return (
    <div className={`glass-card p-5 bg-gradient-to-br ${colors} border`}>
      <div className="flex items-center justify-between mb-3">
        <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</div>
        <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${colors} flex items-center justify-center`}>
          {icon}
        </div>
      </div>
      <div className="text-3xl font-bold font-display">{value}</div>
      {trend && (
        <div className={`mt-1.5 text-xs font-medium ${trendUp ? 'text-emerald-400' : 'text-red-400'}`}>
          {trendUp ? '↑' : '↓'} {trend}
        </div>
      )}
    </div>
  );
}

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  const sizeClass = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }[size];
  return (
    <div className={cn('flex items-center justify-center p-8', className)}>
      <div className={cn(sizeClass, 'border-2 border-forge-500/30 border-t-forge-500 rounded-full animate-spin')} />
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="glass-card p-5 space-y-3">
      <div className="skeleton h-4 w-2/3" />
      <div className="skeleton h-8 w-1/3" />
      <div className="skeleton h-3 w-1/2" />
    </div>
  );
}

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="text-muted-foreground/50 mb-4 text-5xl">{icon}</div>}
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      {description && <p className="text-sm text-muted-foreground max-w-sm">{description}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="glass-card border-red-500/30 p-8 text-center">
      <div className="text-red-400 text-4xl mb-3">⚠️</div>
      <p className="text-red-300 text-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-4 py-2 text-sm bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}

interface BadgeProps {
  children: ReactNode;
  variant?: 'success' | 'warning' | 'error' | 'info' | 'purple';
}

export function Badge({ children, variant = 'info' }: BadgeProps) {
  const cls = `badge-${variant}`;
  return <span className={cls}>{children}</span>;
}

interface ProgressBarProps {
  value: number;
  max?: number;
  color?: string;
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({ value, max = 100, color = 'bg-forge-500', showLabel = false, className }: ProgressBarProps) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <div className={cn('', className)}>
      <div className="progress-track h-2">
        <div className={cn('progress-fill h-full', color)} style={{ width: `${pct}%` }} />
      </div>
      {showLabel && <div className="text-xs text-muted-foreground mt-1">{pct}%</div>}
    </div>
  );
}

interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
}

// Simple toast hook
import { useState, useCallback } from 'react';

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
    success: { bg: 'bg-emerald-500/20 border-emerald-500/40', text: 'text-emerald-300', icon: '✓' },
    error: { bg: 'bg-red-500/20 border-red-500/40', text: 'text-red-300', icon: '✕' },
    info: { bg: 'bg-forge-500/20 border-forge-500/40', text: 'text-forge-300', icon: 'ℹ' },
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 space-y-2 pointer-events-none">
      {toasts.map((t) => {
        const cfg = typeConfig[t.type];
        return (
          <div
            key={t.id}
            className={cn(
              'flex items-center gap-3 px-4 py-3 rounded-xl border backdrop-blur-md',
              'animate-fade-in shadow-lg pointer-events-auto',
              cfg.bg
            )}
          >
            <span className={cn('text-sm font-bold', cfg.text)}>{cfg.icon}</span>
            <span className={cn('text-sm', cfg.text)}>{t.message}</span>
          </div>
        );
      })}
    </div>
  );
}
