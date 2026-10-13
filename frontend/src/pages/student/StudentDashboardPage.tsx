import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';
import type { StudentDashboard, AdaptiveInsights } from '@/types';
import {
  StatCard,
  LoadingSpinner,
  ErrorState,
  Badge,
} from '@/components/shared';
import {
  Trophy,
  Flame,
  Brain,
  Code2,
  BookOpen,
  ArrowRight,
  TrendingUp,
  AlertCircle,
  PlayCircle,
  CheckCircle2,
  Compass,
  FileCode,
  Target,
  Sparkles,
  RotateCcw
} from 'lucide-react';

export default function StudentDashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState<StudentDashboard | null>(null);
  const [insights, setInsights] = useState<AdaptiveInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    setError('');
    try {
      const [dashRes, insRes] = await Promise.all([
        api.getStudentDashboard(),
        api.getAdaptiveInsights().catch(() => null),
      ]);
      setData(dashRes);
      setInsights(insRes);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[60vh]" />;
  if (error) return <ErrorState message={error} onRetry={fetchDashboard} />;

  const student = data?.student;
  const recentTests = data?.recent_tests || [];
  const weakTopics = (data?.weak_topics && data.weak_topics.length > 0)
    ? data.weak_topics
    : (insights?.weak_topics || []);

  const readinessScore = Math.min(100, Math.round(student?.total_score || 0));

  return (
    <div className="space-y-6">
      {/* 1. Header Command Area */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 sm:p-7 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-subtle">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700/80 text-slate-300 text-xs font-medium mb-3">
            <Flame size={14} className="text-amber-500 fill-amber-500" />
            <span>{student?.streak_days || 1} Day Streak</span>
            <span className="text-slate-500">•</span>
            <span className="text-teal-400 font-semibold">Active Session</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-display">
            {getGreeting()}, {user?.full_name?.split(' ')[0] || 'Candidate'}
          </h1>
          <p className="text-slate-400 mt-1.5 text-xs sm:text-sm max-w-xl">
            Here's your placement preparation progress. Review your readiness indicators, target weak topics, and practice with timed assessments.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Link
            to="/student/coach"
            className="px-3.5 py-2 rounded-lg bg-teal-500/15 hover:bg-teal-500/25 text-teal-300 border border-teal-500/40 font-semibold text-xs transition-colors flex items-center gap-2 shadow-sm"
          >
            <Sparkles size={14} className="text-teal-400" />
            AI Coach
          </Link>
          <Link
            to="/student/learn"
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs transition-colors flex items-center gap-2 shadow-sm"
          >
            <BookOpen size={15} />
            Learning Hub
          </Link>
          <Link
            to="/student/practice"
            className="px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors flex items-center gap-2 shadow-subtle"
          >
            <Brain size={15} />
            Start Practice
          </Link>
          <Link
            to="/student/tests"
            className="px-4 py-2 rounded-lg bg-navy-700 hover:bg-navy-600 text-white font-semibold text-xs transition-colors flex items-center gap-2 border border-navy-600/60 shadow-subtle"
          >
            <PlayCircle size={15} />
            Assessments
          </Link>
        </div>
      </div>

      {/* 2. Compact Core Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Placement Readiness"
          value={`${readinessScore}%`}
          icon={<Target size={17} className="text-teal-400" />}
          trend="Calibrated ML projection"
          trendUp={readinessScore >= 60}
          color="teal"
        />
        <StatCard
          label="Aptitude Mastery"
          value={`${Math.round(student?.aptitude_score || 0)}%`}
          icon={<Brain size={17} className="text-sky-400" />}
          trend="Quantitative & Logical"
          trendUp={true}
          color="blue"
        />
        <StatCard
          label="Coding Score"
          value={`${Math.round(student?.coding_score || 0)}%`}
          icon={<Code2 size={17} className="text-emerald-400" />}
          trend="Algorithms & DS"
          trendUp={true}
          color="green"
        />
        <StatCard
          label="Completed Sessions"
          value={data?.practice_count || 0}
          icon={<Trophy size={17} className="text-amber-400" />}
          trend={`${data?.tests_taken || 0} Assessed Tests`}
          trendUp={true}
          color="orange"
        />
      </div>

      {/* 3. "What Should I Do Next?" Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 sm:p-6 shadow-subtle">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-4">
          <div className="flex items-center gap-2">
            <Compass size={18} className="text-teal-400" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Recommended Next Steps
            </h2>
          </div>
          <span className="text-[11px] text-slate-500 font-medium hidden sm:inline">
            Action items based on your recent performance
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {/* Priority 1: Weak Topic Drill */}
          <div className="p-4 rounded-lg bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                  Priority Focus
                </span>
                <span className="text-[11px] text-slate-500 font-medium">Aptitude</span>
              </div>
              <h3 className="text-sm font-semibold text-white">
                {weakTopics.length > 0 ? weakTopics[0].topic_name : 'Quantitative Aptitude'}
              </h3>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                {weakTopics.length > 0
                  ? `Accuracy currently at ${weakTopics[0].accuracy ?? 0}%. Complete a 10-question adaptive set to improve rating.`
                  : 'Maintain your current skill rating with a focused practice set.'}
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80">
              <button
                onClick={() => navigate(weakTopics.length > 0 ? `/student/practice?topic_id=${weakTopics[0].topic_id}` : '/student/practice')}
                className="w-full py-1.5 px-3 rounded-md bg-teal-700 hover:bg-teal-600 text-white font-medium text-xs transition-colors flex items-center justify-center gap-1.5"
              >
                Practice Topic <ArrowRight size={13} />
              </button>
            </div>
          </div>

          {/* Priority 2: Coding Practice */}
          <div className="p-4 rounded-lg bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Algorithm Practice
                </span>
                <span className="text-[11px] text-slate-500 font-medium">Technical</span>
              </div>
              <h3 className="text-sm font-semibold text-white">Data Structures & Logic</h3>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                Solve placement coding problems in Python, Java, or C++ on the code compiler.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80">
              <Link
                to="/student/coding"
                className="w-full py-1.5 px-3 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-xs transition-colors flex items-center justify-center gap-1.5"
              >
                Open Code Editor <FileCode size={13} />
              </Link>
            </div>
          </div>

          {/* Priority 3: Timed Mock Assessment */}
          <div className="p-4 rounded-lg bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                  Assessment
                </span>
                <span className="text-[11px] text-slate-500 font-medium">Evaluation</span>
              </div>
              <h3 className="text-sm font-semibold text-white">Timed Full Assessment</h3>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                Take a simulated college placement test with strict timing and instant scoring.
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80">
              <Link
                to="/student/tests"
                className="w-full py-1.5 px-3 rounded-md bg-navy-700 hover:bg-navy-600 text-white font-medium text-xs transition-colors flex items-center justify-center gap-1.5"
              >
                View Tests <PlayCircle size={13} />
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Two-Column Layout: Focus Areas & Recent Tests */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Focus Areas */}
        <div className="lg:col-span-1 space-y-5">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-subtle">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-4">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-1.5">
                  <AlertCircle size={16} className="text-amber-400" />
                  Focus Areas
                </h2>
                <p className="text-[11px] text-slate-400 mt-0.5">Topics requiring targeted revision</p>
              </div>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                &lt; 50% Acc
              </span>
            </div>

            {weakTopics.length === 0 ? (
              <div className="text-center py-6">
                <CheckCircle2 size={32} className="text-emerald-400 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-200">No Critical Weak Areas</p>
                <p className="text-[11px] text-slate-400 mt-1">All practiced topics have solid accuracy.</p>
                <Link
                  to="/student/learn"
                  className="mt-3 inline-flex items-center gap-1 text-xs text-teal-400 hover:text-teal-300 font-semibold"
                >
                  Explore curriculum <ArrowRight size={13} />
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {weakTopics.slice(0, 4).map((topic) => {
                  const acc = topic.accuracy ?? 0;
                  const isSevere = acc < 35;
                  return (
                    <div
                      key={topic.topic_id}
                      className="p-3 rounded-lg bg-slate-950/70 border border-slate-800/90 hover:border-slate-700 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs font-semibold text-slate-200 truncate">{topic.topic_name}</span>
                            {topic.category_label && (
                              <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                                {topic.category_label}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-1">
                            <span className={isSevere ? 'text-red-400 font-medium' : 'text-amber-400 font-medium'}>
                              {acc}% accuracy
                            </span>
                            {topic.questions_attempted !== undefined && topic.questions_attempted > 0 && (
                              <>
                                <span>•</span>
                                <span>{topic.questions_correct ?? 0}/{topic.questions_attempted} correct</span>
                              </>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-1.5 shrink-0">
                          <button
                            onClick={() => navigate(`/student/coach?prompt=How can I improve my performance in ${encodeURIComponent(topic.topic_name)}?`)}
                            className="px-2 py-1 text-[11px] rounded bg-teal-500/10 hover:bg-teal-500/20 text-teal-300 border border-teal-500/30 font-medium transition-colors flex items-center gap-1"
                            title="Ask AI Coach how to improve in this topic"
                          >
                            <Sparkles size={11} />
                            <span>Ask AI</span>
                          </button>
                          <button
                            onClick={() => navigate(`/student/practice?topic_id=${topic.topic_id}`)}
                            className="px-2.5 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 font-medium transition-colors"
                          >
                            Practice
                          </button>
                        </div>
                      </div>

                      {/* Accuracy bar */}
                      <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2.5 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${isSevere ? 'bg-red-500' : 'bg-amber-500'}`}
                          style={{ width: `${Math.min(100, Math.max(8, acc))}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Adaptive Engine Guidance */}
          {insights && insights.tips && insights.tips.length > 0 && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-subtle">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles size={14} className="text-teal-400" />
                  Study Tips
                </h3>
                <span className="text-[10px] text-slate-500">Item Response Theory</span>
              </div>
              <div className="space-y-2.5">
                {insights.tips.slice(0, 3).map((tip, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/70 text-xs">
                    <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${tip.type === 'WARNING' ? 'bg-amber-400' : 'bg-teal-400'}`} />
                      {tip.title}
                    </div>
                    <div className="text-slate-400 text-[11px] mt-0.5 pl-3 leading-relaxed">{tip.description}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Recent Test Results */}
        <div className="lg:col-span-2 space-y-5">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 sm:p-6 shadow-subtle">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-4">
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Recent Assessments
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Scored evaluation history and benchmark results</p>
              </div>
              <Link
                to="/student/tests"
                className="text-xs text-teal-400 hover:text-teal-300 font-semibold flex items-center gap-1"
              >
                All Tests <ArrowRight size={13} />
              </Link>
            </div>

            {recentTests.length === 0 ? (
              <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
                <PlayCircle size={36} className="text-slate-600 mx-auto mb-2.5" />
                <h3 className="text-sm font-semibold text-slate-200">No Assessment History</h3>
                <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                  Take a practice assessment to generate your placement readiness benchmark.
                </p>
                <Link
                  to="/student/tests"
                  className="mt-4 inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-teal-700 hover:bg-teal-600 text-white text-xs font-semibold"
                >
                  Start Assessment
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-slate-800/70">
                {recentTests.map((t) => {
                  const pct = Math.round(t.percentage || 0);
                  const isPass = pct >= 60;
                  return (
                    <div
                      key={t.attempt_id}
                      className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between gap-3"
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
                          <div className="font-semibold text-xs text-slate-200 truncate">{t.test_title}</div>
                          <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-2">
                            <span>Score: {t.score} pts</span>
                            <span>•</span>
                            <span>{t.submitted_at ? new Date(t.submitted_at).toLocaleDateString() : 'Recent'}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <Badge variant={isPass ? 'success' : 'error'}>
                          {isPass ? 'PASSED' : 'RETRY'}
                        </Badge>
                        <Link
                          to={`/student/tests/results/${t.attempt_id}`}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium transition-colors"
                        >
                          Scorecard
                        </Link>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
