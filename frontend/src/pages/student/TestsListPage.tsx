import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { Test, TestHistoryItem } from '@/types';
import { PageHeader, LoadingSpinner, ErrorState, Badge } from '@/components/shared';
import {
  FileText,
  Clock,
  Award,
  PlayCircle,
  CheckCircle2,
  Calendar,
  AlertCircle,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

export default function TestsListPage() {
  const navigate = useNavigate();
  const [tests, setTests] = useState<Test[]>([]);
  const [history, setHistory] = useState<TestHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTestsAndHistory();
  }, []);

  const fetchTestsAndHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const [testsData, historyData] = await Promise.all([
        api.getAvailableTests(),
        api.getTestHistory(),
      ]);
      setTests(testsData);
      setHistory(historyData);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to load test catalog');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[60vh]" />;
  if (error) return <ErrorState message={error} onRetry={fetchTestsAndHistory} />;

  return (
    <div className="space-y-10 animate-fade-in">
      <PageHeader
        title="Placement Assessment Tests"
        subtitle="Timed aptitude and technical evaluation tests with AI-powered proctoring & analytics"
      />

      {/* Available Tests Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
          <FileText size={18} className="text-forge-400" />
          Available Scored Tests ({tests.length})
        </h2>

        {tests.length === 0 ? (
          <div className="text-center py-12 glass-card border border-dashed border-border">
            <AlertCircle size={36} className="text-muted-foreground/40 mx-auto mb-2" />
            <p className="text-sm font-medium text-foreground">No tests scheduled at this time.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {tests.map((test) => (
              <div
                key={test.id}
                className="glass-card p-6 border border-border/60 hover:border-forge-500/50 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <Badge variant={test.test_type === 'APTITUDE' ? 'info' : 'purple'}>
                      {test.test_type}
                    </Badge>
                    <span className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                      <Clock size={14} /> {test.duration_minutes} Minutes
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-foreground">{test.title}</h3>
                  <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                    {test.description || 'Standard placement aptitude assessment covering quantitative, logical, and verbal ability.'}
                  </p>

                  <div className="grid grid-cols-3 gap-2 mt-5 p-3 rounded-xl bg-white/5 border border-border/40 text-center">
                    <div>
                      <div className="text-[10px] uppercase font-semibold text-muted-foreground">Questions</div>
                      <div className="text-sm font-bold text-foreground mt-0.5">{test.question_count || 0}</div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase font-semibold text-muted-foreground">Total Marks</div>
                      <div className="text-sm font-bold text-foreground mt-0.5">{test.total_marks}</div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase font-semibold text-muted-foreground">Pass Marks</div>
                      <div className="text-sm font-bold text-emerald-400 mt-0.5">{test.passing_marks}</div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-border/40 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-[11px] text-amber-400 font-medium">
                    <ShieldAlert size={14} /> Proctoring Enabled
                  </div>

                  <button
                    onClick={() => {
                      if (test.test_type === 'CODING') {
                        navigate(`/student/coding/assessments/${test.id}`);
                      } else {
                        navigate(`/student/tests/session/${test.id}`);
                      }
                    }}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold text-xs glow-button transition-all flex items-center gap-2"
                  >
                    <PlayCircle size={15} />
                    Start Assessment
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Completed History Section */}
      <div className="space-y-4 pt-6 border-t border-border/60">
        <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
          <CheckCircle2 size={18} className="text-emerald-400" />
          Test History & Scorecards ({history.length})
        </h2>

        {history.length === 0 ? (
          <div className="text-center py-8 text-xs text-muted-foreground">
            No completed tests yet. Your scorecards will appear here after submission.
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((h) => {
              const pct = Math.round(h.percentage || 0);
              const isPass = pct >= 60;
              return (
                <div
                  key={h.attempt_id}
                  className="glass-card p-4 border border-border/60 flex items-center justify-between gap-4 hover:border-border transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-sm font-display ${
                        isPass
                          ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-400'
                          : 'bg-red-500/15 border border-red-500/30 text-red-400'
                      }`}
                    >
                      {pct}%
                    </div>
                    <div>
                      <div className="font-semibold text-sm text-foreground">{h.test_title}</div>
                      <div className="text-xs text-muted-foreground mt-0.5 flex items-center gap-3">
                        <span>Score: {h.score} / {h.max_score}</span>
                        <span>•</span>
                        <span>{h.submitted_at ? new Date(h.submitted_at).toLocaleString() : 'Recent'}</span>
                      </div>
                    </div>
                  </div>

                  <Link
                    to={`/student/tests/results/${h.attempt_id}`}
                    className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-border text-xs font-semibold text-foreground transition-colors flex items-center gap-1.5"
                  >
                    View Scorecard <ArrowRight size={14} />
                  </Link>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
