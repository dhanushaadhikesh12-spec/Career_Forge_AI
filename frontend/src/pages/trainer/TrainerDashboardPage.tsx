import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';
import type { TrainerDashboard } from '@/types';
import {
  PageHeader,
  StatCard,
  LoadingSpinner,
  ErrorState,
  Badge,
} from '@/components/shared';
import {
  Users,
  GraduationCap,
  FileCheck,
  TrendingUp,
  Plus,
  ArrowRight,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

export default function TrainerDashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState<TrainerDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTrainerData();
  }, []);

  const fetchTrainerData = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.getTrainerDashboard();
      setData(res);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to load trainer dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[60vh]" />;
  if (error) return <ErrorState message={error} onRetry={fetchTrainerData} />;

  const batches = data?.batch_performance || [];
  const recentTests = data?.recent_tests || [];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Banner */}
      <div className="glass-card p-8 border border-purple-500/20 bg-gradient-to-r from-purple-950/30 via-card to-forge-950/20 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-semibold mb-3">
            <ShieldCheck size={14} className="text-purple-400" />
            <span>Trainer Portal • Batch Management Active</span>
          </div>
          <h1 className="text-3xl font-bold font-display text-white">
            Welcome, <span className="gradient-text">{data?.trainer?.full_name || user?.full_name || 'Trainer'}</span>
          </h1>
          <p className="text-xs text-muted-foreground mt-1 max-w-lg">
            Monitor student placement cohorts, schedule standardized aptitude tests, and track real-time score distributions.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            to="/trainer/batches"
            className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white font-semibold text-xs transition-colors flex items-center gap-2"
          >
            <Users size={15} />
            Manage Batches
          </Link>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          label="Active Batches"
          value={data?.batch_count || 0}
          icon={<GraduationCap size={18} className="text-purple-400" />}
          trend="Assigned cohorts"
          trendUp={true}
          color="purple"
        />
        <StatCard
          label="Total Students"
          value={data?.student_count || 0}
          icon={<Users size={18} className="text-forge-400" />}
          trend="Enrolled across batches"
          trendUp={true}
          color="blue"
        />
        <StatCard
          label="Tests Created"
          value={recentTests.length}
          icon={<FileCheck size={18} className="text-emerald-400" />}
          trend="Placement evaluations"
          trendUp={true}
          color="green"
        />
        <StatCard
          label="Avg Performance"
          value={
            batches.length > 0
              ? `${Math.round(batches.reduce((acc, b) => acc + (b.avg_score || 0), 0) / batches.length)}%`
              : '82%'
          }
          icon={<TrendingUp size={18} className="text-amber-400" />}
          trend="Cohort benchmark"
          trendUp={true}
          color="orange"
        />
      </div>

      {/* Batches Overview & Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-6 border border-border/60 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-foreground">Cohort Performance by Batch</h2>
            <Link
              to="/trainer/batches"
              className="text-xs text-forge-400 hover:text-forge-300 font-semibold flex items-center gap-1"
            >
              All Batches <ArrowRight size={14} />
            </Link>
          </div>

          {batches.length === 0 ? (
            <div className="text-center py-10 text-xs text-muted-foreground">
              No batches with test submissions yet.
            </div>
          ) : (
            <div className="space-y-3">
              {batches.map((b) => (
                <div
                  key={b.batch_id}
                  className="p-4 rounded-xl bg-white/5 border border-border/50 hover:border-purple-500/40 transition-colors flex items-center justify-between gap-4"
                >
                  <div>
                    <div className="text-sm font-bold text-foreground">{b.batch_name}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">
                      {b.student_count} Students enrolled
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-sm font-bold text-purple-400 font-display">
                        {Math.round(b.avg_score || 0)}%
                      </div>
                      <div className="text-[10px] text-muted-foreground uppercase font-semibold">
                        Average
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tests conducted sidebar */}
        <div className="lg:col-span-1 glass-card p-6 border border-border/60 space-y-4">
          <h2 className="text-base font-bold text-foreground">Recent Assessments</h2>

          {recentTests.length === 0 ? (
            <div className="text-center py-10 text-xs text-muted-foreground">
              No assessments created yet.
            </div>
          ) : (
            <div className="space-y-3">
              {recentTests.map((t) => (
                <div key={t.id} className="p-3.5 rounded-xl bg-white/5 border border-border/40">
                  <div className="text-xs font-semibold text-foreground truncate">{t.title}</div>
                  <div className="flex items-center justify-between mt-2">
                    <Badge variant={t.status === 'PUBLISHED' ? 'success' : 'warning'}>
                      {t.status}
                    </Badge>
                    <span className="text-[11px] text-muted-foreground">
                      {new Date(t.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
