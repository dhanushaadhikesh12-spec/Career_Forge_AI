import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';
import type { TrainerDashboard } from '@/types';
import {
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
  ArrowRight,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

export default function TrainerDashboardPage() {
  const { user } = useAuth();
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
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 sm:p-7 flex flex-col md:flex-row md:items-center justify-between gap-5 shadow-subtle">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium mb-3">
            <ShieldCheck size={14} className="text-amber-400" />
            <span>Trainer Portal • Cohort Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-display">
            Welcome, {data?.trainer?.full_name || user?.full_name || 'Trainer'}
          </h1>
          <p className="text-slate-400 mt-1.5 text-xs sm:text-sm max-w-xl">
            Monitor college placement cohorts, review score distributions, inspect proctoring logs, and utilize AI diagnostic reports.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <Link
            to="/trainer/assistant"
            className="px-3.5 py-2 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors flex items-center gap-2 shadow-subtle"
          >
            <Sparkles size={14} />
            AI Trainer
          </Link>
          <Link
            to="/trainer/batches"
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium text-xs transition-colors flex items-center gap-2"
          >
            <Users size={14} />
            Manage Batches
          </Link>
        </div>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Active Cohorts"
          value={data?.batch_count || 0}
          icon={<GraduationCap size={17} className="text-teal-400" />}
          trend="Assigned student batches"
          trendUp={true}
          color="teal"
        />
        <StatCard
          label="Enrolled Students"
          value={data?.student_count || 0}
          icon={<Users size={17} className="text-sky-400" />}
          trend="Active candidates"
          trendUp={true}
          color="blue"
        />
        <StatCard
          label="Created Assessments"
          value={recentTests.length}
          icon={<FileCheck size={17} className="text-emerald-400" />}
          trend="Evaluations scheduled"
          trendUp={true}
          color="green"
        />
        <StatCard
          label="Cohort Average"
          value={
            batches.length > 0
              ? `${Math.round(batches.reduce((acc, b) => acc + (b.avg_score || 0), 0) / batches.length)}%`
              : '82%'
          }
          icon={<TrendingUp size={17} className="text-amber-400" />}
          trend="Benchmark performance"
          trendUp={true}
          color="orange"
        />
      </div>

      {/* Batches Overview & Recent Assessments */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Batches Overview Table */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 sm:p-6 space-y-4 shadow-subtle">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Cohort Performance by Batch</h2>
              <p className="text-xs text-slate-400 mt-0.5">Average scores and student headcount per batch</p>
            </div>
            <Link
              to="/trainer/batches"
              className="text-xs text-teal-400 hover:text-teal-300 font-semibold flex items-center gap-1"
            >
              All Batches <ArrowRight size={13} />
            </Link>
          </div>

          {batches.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-500">
              No batches with test submissions recorded yet.
            </div>
          ) : (
            <div className="space-y-2.5">
              {batches.map((b) => (
                <div
                  key={b.batch_id}
                  className="p-3.5 rounded-lg bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 transition-colors flex items-center justify-between gap-4"
                >
                  <div>
                    <div className="text-xs sm:text-sm font-bold text-white">{b.batch_name}</div>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      {b.student_count} Students enrolled
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-sm font-bold text-teal-400 font-display">
                        {Math.round(b.avg_score || 0)}%
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">
                        Average
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Assessments Sidebar */}
        <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-5 sm:p-6 space-y-4 shadow-subtle">
          <div className="pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Recent Assessments</h2>
            <p className="text-xs text-slate-400 mt-0.5">Test publishing status</p>
          </div>

          {recentTests.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-500">
              No assessments created yet.
            </div>
          ) : (
            <div className="space-y-2.5">
              {recentTests.map((t) => (
                <div key={t.id} className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80">
                  <div className="text-xs font-semibold text-slate-200 truncate">{t.title}</div>
                  <div className="flex items-center justify-between mt-2">
                    <Badge variant={t.status === 'PUBLISHED' ? 'success' : 'warning'}>
                      {t.status}
                    </Badge>
                    <span className="text-[11px] text-slate-500">
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
