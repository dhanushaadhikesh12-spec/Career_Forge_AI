import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';
import type { StudentDashboard, AdaptiveInsights } from '@/types';
import {
  PageHeader,
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
  Sparkles,
  Zap,
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

  if (loading) return <LoadingSpinner size="lg" className="h-[60vh]" />;
  if (error) return <ErrorState message={error} onRetry={fetchDashboard} />;

  const student = data?.student;
  const recentTests = data?.recent_tests || [];
  const weakTopics = data?.weak_topics || [];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Personalized Adaptive Recommendation Notification */}
      {insights?.recommendation_banner && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-purple-900/40 via-forge-900/30 to-card border border-purple-500/30 flex items-center justify-between gap-4 shadow-lg backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-300 shrink-0">
              <Sparkles size={18} />
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-wider font-bold text-purple-400">
                Personalized Adaptive Recommendation
              </div>
              <p className="text-xs font-medium text-foreground mt-0.5">
                {insights.recommendation_banner}
              </p>
            </div>
          </div>

          <button
            onClick={() => navigate(`/student/practice?topic_id=${insights.recommended_topic_id}`)}
            className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs transition-colors shrink-0 glow-button flex items-center gap-1.5"
          >
            Practice Now <ArrowRight size={14} />
          </button>
        </div>
      )}
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl p-8 bg-gradient-to-r from-forge-600/30 via-purple-600/20 to-blue-600/20 border border-forge-500/20 backdrop-blur-xl">
        <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-forge-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-forge-500/20 border border-forge-500/30 text-forge-300 text-xs font-semibold mb-3">
              <Flame size={14} className="text-orange-400 fill-orange-400 animate-pulse" />
              <span>{student?.streak_days || 1} Day Streak • Placement Ready</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold font-display text-white">
              Welcome back, <span className="gradient-text">{user?.full_name || 'Candidate'}</span>!
            </h1>
            <p className="text-muted-foreground mt-2 max-w-xl text-sm leading-relaxed">
              Track your aptitude mastery, coding readiness score, and practice targeted problem sets to ace your upcoming campus interviews.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/student/learn"
              className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white font-medium text-sm transition-all flex items-center gap-2 backdrop-blur-sm shadow-sm"
            >
              <BookOpen size={16} />
              Study Topics
            </Link>
            <Link
              to="/student/tests"
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-forge-500 to-purple-600 hover:from-forge-400 hover:to-purple-500 text-white font-semibold text-sm transition-all flex items-center gap-2 glow-button shadow-lg shadow-forge-500/20"
            >
              <PlayCircle size={16} />
              Take a Test
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          label="Overall Score"
          value={`${Math.round(student?.total_score || 0)}`}
          icon={<Trophy size={18} className="text-forge-400" />}
          trend="Cumulative performance"
          trendUp={true}
          color="blue"
        />
        <StatCard
          label="Aptitude Mastery"
          value={`${Math.round(student?.aptitude_score || 0)}%`}
          icon={<Brain size={18} className="text-purple-400" />}
          trend="Quantitative & Logical"
          trendUp={true}
          color="purple"
        />
        <StatCard
          label="Coding Score"
          value={`${Math.round(student?.coding_score || 0)}%`}
          icon={<Code2 size={18} className="text-emerald-400" />}
          trend="Algorithms & Data Structures"
          trendUp={true}
          color="green"
        />
        <StatCard
          label="Practice Sessions"
          value={data?.practice_count || 0}
          icon={<TrendingUp size={18} className="text-amber-400" />}
          trend={`${data?.tests_taken || 0} Tests Completed`}
          trendUp={true}
          color="orange"
        />
      </div>

      {/* Main Grid: Weak Areas & Recent Tests */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Weak Areas & Smart Recommendations */}
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-card p-6 border border-border/60">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold flex items-center gap-2">
                <AlertCircle size={18} className="text-amber-400" />
                Focus Areas
              </h2>
              <span className="text-xs text-muted-foreground">Accuracy &lt; 50%</span>
            </div>

            {weakTopics.length === 0 ? (
              <div className="text-center py-8">
                <CheckCircle2 size={36} className="text-emerald-400 mx-auto mb-2 opacity-80" />
                <p className="text-sm font-medium text-foreground">No critical weak spots detected!</p>
                <p className="text-xs text-muted-foreground mt-1">Keep practicing across all categories to maintain your edge.</p>
                <Link
                  to="/student/learn"
                  className="mt-4 inline-flex items-center gap-1.5 text-xs text-forge-400 hover:text-forge-300 font-semibold"
                >
                  Explore new subjects <ArrowRight size={14} />
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {weakTopics.map((topic) => (
                  <div
                    key={topic.topic_id}
                    className="p-3.5 rounded-xl bg-white/5 border border-border/50 hover:border-forge-500/40 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="text-sm font-semibold text-foreground">{topic.topic_name}</div>
                        <div className="text-xs text-red-400 font-medium mt-0.5">
                          {topic.accuracy}% accuracy
                        </div>
                      </div>
                      <button
                        onClick={() => navigate(`/student/practice?topic_id=${topic.topic_id}`)}
                        className="px-3 py-1.5 text-xs rounded-lg bg-forge-600/20 hover:bg-forge-600/30 text-forge-300 border border-forge-500/30 font-medium transition-colors"
                      >
                        Practice
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Adaptive Engine Personalization Coaching */}
          {insights && (
            <div className="glass-card p-6 border border-purple-500/30 bg-gradient-to-br from-purple-950/30 via-forge-950/20 to-card">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-sm text-foreground flex items-center gap-2">
                  <Sparkles size={16} className="text-purple-400" />
                  Adaptive Engine Insights
                </h3>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  Live IRT & Elo
                </span>
              </div>

              <div className="space-y-2 mb-4">
                {insights.weak_topics && insights.weak_topics.length > 0 && (
                  <div className="text-xs p-2.5 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 flex items-center justify-between">
                    <span><strong>Your weakest topic:</strong> {insights.weak_topics[0].topic_name} ({insights.weak_topics[0].accuracy ?? 0}%)</span>
                    <button
                      onClick={() => navigate(`/student/practice?topic_id=${insights.weak_topics[0].topic_id}`)}
                      className="text-[11px] underline font-semibold text-red-200 hover:text-white"
                    >
                      Fix Now
                    </button>
                  </div>
                )}
                {insights.recommended_topic_id && (
                  <div className="text-xs p-2.5 rounded-xl bg-forge-500/10 border border-forge-500/20 text-forge-300">
                    <strong>Recommended practice:</strong>{' '}
                    {insights.topic_analytics.find(t => t.topic_id === insights.recommended_topic_id)?.topic_name || 'Dynamic Diagnostic'}
                  </div>
                )}
              </div>

              {insights.tips && insights.tips.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-border/40">
                  <div className="text-[11px] uppercase tracking-wider font-semibold text-muted-foreground mb-1">
                    Calibrated Guidance:
                  </div>
                  {insights.tips.slice(0, 3).map((tip, idx) => (
                    <div key={idx} className="text-xs p-2 rounded-lg bg-white/5 border border-border/30">
                      <div className="font-semibold text-foreground flex items-center gap-1.5">
                        <span className={`w-1.5 h-1.5 rounded-full ${tip.type === 'WARNING' ? 'bg-red-400' : tip.type === 'SUCCESS' ? 'bg-emerald-400' : 'bg-blue-400'}`} />
                        {tip.title}
                      </div>
                      <div className="text-muted-foreground text-[11px] mt-0.5 pl-3">{tip.description}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Quick Study Launchpad */}
          <div className="glass-card p-6 border border-forge-500/20 bg-gradient-to-br from-forge-950/40 to-purple-950/30">
            <h3 className="font-semibold text-sm text-foreground mb-2 flex items-center gap-2">
              <Brain size={16} className="text-forge-400" />
              Aptitude Topic Library
            </h3>
            <p className="text-xs text-muted-foreground mb-4 leading-relaxed">
              Explore the full curriculum of Quantitative, Logical, and Verbal topics with real-time skill calibration.
            </p>
            <button
              onClick={() => navigate('/student/learn')}
              className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-xs font-semibold text-white transition-colors flex items-center justify-center gap-2"
            >
              Browse All Topics
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Right Column: Recent Tests & History */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6 border border-border/60">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-foreground">Recent Test Results</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Your official scored tests and performance reviews</p>
              </div>
              <Link
                to="/student/tests"
                className="text-xs text-forge-400 hover:text-forge-300 font-semibold flex items-center gap-1"
              >
                View all tests <ArrowRight size={14} />
              </Link>
            </div>

            {recentTests.length === 0 ? (
              <div className="text-center py-12 border border-dashed border-border/60 rounded-2xl">
                <PlayCircle size={40} className="text-muted-foreground/40 mx-auto mb-3" />
                <h3 className="text-base font-semibold text-foreground">No tests completed yet</h3>
                <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                  Take your first placement readiness test to establish your benchmark score.
                </p>
                <Link
                  to="/student/tests"
                  className="mt-5 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-forge-600 hover:bg-forge-500 text-white text-xs font-semibold glow-button"
                >
                  Start First Test
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {recentTests.map((t) => {
                  const pct = Math.round(t.percentage || 0);
                  const isPass = pct >= 60;
                  return (
                    <div
                      key={t.attempt_id}
                      className="p-4 rounded-xl bg-white/5 border border-border/50 hover:border-forge-500/40 transition-all flex items-center justify-between gap-4"
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
                          <div className="font-semibold text-sm text-foreground">{t.test_title}</div>
                          <div className="text-xs text-muted-foreground mt-1 flex items-center gap-3">
                            <span>Score: {t.score} marks</span>
                            <span>•</span>
                            <span>{t.submitted_at ? new Date(t.submitted_at).toLocaleDateString() : 'Recent'}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <Badge variant={isPass ? 'success' : 'error'}>
                          {isPass ? 'PASSED' : 'RETRY'}
                        </Badge>
                        <Link
                          to={`/student/tests/results/${t.attempt_id}`}
                          className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-border text-xs font-medium text-foreground transition-colors"
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
