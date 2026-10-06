import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr?: string): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  });
}

export function formatDateTime(dateStr?: string): string {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  });
}

export function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

export function formatScore(score?: number, max?: number): string {
  if (score === undefined || score === null) return '—';
  if (max !== undefined) return `${score}/${max}`;
  return `${Math.round(score)}`;
}

export function getGradeColor(percentage?: number): string {
  if (percentage === undefined) return 'text-muted-foreground';
  if (percentage >= 80) return 'text-emerald-400';
  if (percentage >= 60) return 'text-blue-400';
  if (percentage >= 40) return 'text-amber-400';
  return 'text-red-400';
}

export function getDifficultyColor(difficulty: string): string {
  switch (difficulty?.toUpperCase()) {
    case 'EASY': return 'badge-success';
    case 'MEDIUM': return 'badge-warning';
    case 'HARD': return 'badge-error';
    default: return 'badge-info';
  }
}

export function getStatusColor(status: string): string {
  switch (status?.toUpperCase()) {
    case 'GRADED': return 'badge-success';
    case 'IN_PROGRESS': return 'badge-info';
    case 'TIMED_OUT': return 'badge-error';
    case 'PUBLISHED': return 'badge-success';
    case 'DRAFT': return 'badge-warning';
    case 'ARCHIVED': return 'badge-neutral';
    default: return 'badge-info';
  }
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen) + '…';
}
