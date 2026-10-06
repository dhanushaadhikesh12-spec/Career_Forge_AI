import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { Test, TestHistoryItem } from '@/types';
import { PageHeader, LoadingSpinner, ErrorState, Badge } from '@/components/shared';
import {
  FileText,
  Clock,
  PlayCircle,
  CheckCircle2,
  AlertCircle,
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
    <div className="space-y-8">
      <PageHeader
        title="Placement Assessment Tests"
        subtitle="Timed aptitude and coding evaluation tests with proctoring enforcement and detailed scorecards."
      />

      {/* Available Tests Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <FileText size={16} className="text-teal-400" />
            Scheduled Assessments ({tests.length})
          </h2>
          <span className="text-xs text-slate-500">Official Evaluation</span>
        </div>

        {tests.length === 0 ? (
          <div className="text-center py-12 bg-slate-900 border border-dashed border-slate-800 rounded-xl">
            <AlertCircle size={32} className="text-slate-600 mx-auto mb-2" />
            <p className="text-xs font-medium text-slate-400">No assessments scheduled at this time.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {tests.map((test) => (
              <div
                key={test.id}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors flex flex-col justify-between shadow-subtle"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2.5">
                    <Badge variant={test.test_type === 'APTITUDE' ? 'info' : 'teal'}>
                      {test.test_type}
                    </Badge>
                    <span className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
                      <Clock size={13} /> {test.duration_minutes} Mins
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white">{test.title}</h3>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                    {test.description || 'Standard placement evaluation covering quantitative, logical, or programming skill sets.'}
                  </p>

                  <div className="grid grid-cols-3 gap-2 mt-4 p-3 rounded-lg bg-slate-950 border border-slate-800 text-center">
                    <div>
                      <div className="text-[10px] uppercase font-semibold text-slate-500">Questions</div>
                      <div className="text-xs font-bold text-slate-200 mt-0.5">{test.question_count || 0}</div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase font-semibold text-slate-500">Total Marks</div>
                      <div className="text-xs font-bold text-slate-200 mt-0.5">{test.total_marks}</div>
                    </div>
                    <div>
                      <div className="text-[10px] uppercase font-semibold text-slate-500">Passing</div>
                      <div className="text-xs font-bold text-emerald-400 mt-0.5">{test.passing_marks}</div>
                    </div>
                  </div>
                </div>

                <div className="mt-5 pt-3.5 border-t border-slate-800 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-[11px] text-amber-400 font-medium">
                    <ShieldAlert size={13} /> Proctoring Monitored
                  </div>

                  <button
                    onClick={() => {
                      if (test.test_type === 'CODING') {
                        navigate(`/student/coding/assessments/${test.id}`);
                      } else {
                        navigate(`/student/tests/session/${test.id}`);
                      }
                    }}
                    className="px-4 py-2 rounded-lg bg-navy-700 hover:bg-navy-600 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-subtle border border-navy-600/60"
                  >
                    <PlayCircle size={14} />
                    Start Assessment
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Completed History Section */}
      <div className="space-y-4 pt-4 border-t border-slate-800">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 size={16} className="text-emerald-400" />
            Completed Assessment History ({history.length})
          </h2>
        </div>

        {history.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">
            No completed tests yet. Completed scorecards will be archived here.
          </div>
        ) : (
          <div className="space-y-2.5">
            {history.map((h) => {
              const pct = Math.round(h.percentage || 0);
              const isPass = pct >= 60;
              return (
                <div
                  key={h.attempt_id}
                  className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4 shadow-subtle"
                >
                  <div className="flex items-center gap-3.5 min-w-0">
                    <div
                      className={`w-11 h-11 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 border ${
                        isPass
                          ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                          : 'bg-red-500/10 border-red-500/30 text-red-400'
                      }`}
                    >
                      {pct}%
                    </div>
                    <div className="min-w-0">
                      <div className="font-semibold text-xs text-slate-200 truncate">{h.test_title}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-2">
                        <span>Score: {h.score} pts</span>
                        <span>•</span>
                        <span>{h.submitted_at ? new Date(h.submitted_at).toLocaleDateString() : 'Recent'}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <Badge variant={isPass ? 'success' : 'error'}>
                      {isPass ? 'PASSED' : 'FAILED'}
                    </Badge>
                    <button
                      onClick={() => navigate(`/student/tests/results/${h.attempt_id}`)}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition-colors"
                    >
                      View Scorecard
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
