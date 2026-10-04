import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart3, Users, Brain, Code2, AlertTriangle, ShieldAlert,
  Sparkles, CheckCircle2, XCircle, ArrowRight, Eye, RefreshCw, TrendingUp
} from 'lucide-react';
import { api } from '@/services/api';
import type {
  TrainerAnalyticsOverview, StudentClusterResult, PlagiarismReport, AnomalyReport, MalpracticeReport,
  BatchReadinessReport,
} from '@/types';
import { Badge, LoadingSpinner, StatCard } from '@/components/shared';

export default function TrainerAnalyticsPage() {
  const navigate = useNavigate();
  const [overview, setOverview] = useState<TrainerAnalyticsOverview | null>(null);
  const [clustering, setClustering] = useState<StudentClusterResult | null>(null);
  const [codingAnalytics, setCodingAnalytics] = useState<any>(null);
  const [topicAnalytics, setTopicAnalytics] = useState<any>(null);
  const [plagiarism, setPlagiarism] = useState<PlagiarismReport | null>(null);
  const [malpractice, setMalpractice] = useState<MalpracticeReport | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyReport | null>(null);
  const [readiness, setReadiness] = useState<BatchReadinessReport | null>(null);
  const [retraining, setRetraining] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const [activeTab, setActiveTab] = useState<'clusters' | 'topics' | 'coding' | 'malpractice' | 'plagiarism' | 'anomalies' | 'readiness'>('clusters');

  useEffect(() => {
    loadAllAnalytics();
  }, []);

  async function loadAllAnalytics() {
    setIsLoading(true);
    try {
      const [ov, cl, cd, tp, pl, rd] = await Promise.all([
        api.getTrainerAnalyticsOverview().catch(() => null),
        api.getTrainerClustering().catch(() => null),
        api.getTrainerCodingAnalytics().catch(() => null),
        api.getTrainerTopicsAnalytics().catch(() => null),
        api.getTrainerPlagiarismReport().catch(() => null),
        api.getBatchReadiness().catch(() => null),
      ]);
      setOverview(ov);
      setClustering(cl);
      setCodingAnalytics(cd);
      setTopicAnalytics(tp);
      setPlagiarism(pl);
      setReadiness(rd);

      // Load malpractice & anomalies for first test if available
      try {
        const tests = await api.getTrainerTests();
        if (tests && tests.length > 0) {
          const firstTestId = tests[0].id;
          const [mp, an] = await Promise.all([
            api.getTrainerMalpracticeReport(firstTestId).catch(() => null),
            api.getTrainerAnomaliesReport(firstTestId).catch(() => null),
          ]);
          setMalpractice(mp);
          setAnomalies(an);
        }
      } catch (err) {
        console.error('Failed to load test analytics:', err);
      }
    } catch (err) {
      console.error('Failed to load trainer analytics:', err);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRetrainReadiness() {
    setRetraining(true);
    try {
      await api.retrainReadinessModel();
      const updated = await api.getBatchReadiness().catch(() => null);
      setReadiness(updated);
    } catch (e) {
      console.error('Failed to retrain model:', e);
    } finally {
      setRetraining(false);
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Top Banner */}
      <div className="relative overflow-hidden rounded-3xl p-8 bg-gradient-to-r from-purple-900/40 via-blue-900/30 to-forge-900/40 border border-purple-500/20 backdrop-blur-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-semibold mb-3">
              <Sparkles size={14} className="text-purple-400" />
              <span>Trainer Intelligence Hub • Machine Learning & Analytics</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold font-display text-white">
              Cohort <span className="gradient-text">Analytics Engine</span>
            </h1>
            <p className="text-muted-foreground mt-2 max-w-xl text-sm leading-relaxed">
              Real-time multi-dimensional assessment metrics, K-Means student grouping, code similarity detection, and automated malpractice risk monitoring.
            </p>
          </div>

          <button
            onClick={loadAllAnalytics}
            className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white font-medium text-xs transition-colors flex items-center gap-2 self-start md:self-auto"
          >
            <RefreshCw size={15} />
            Refresh Analytics
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          label="Cohort Size"
          value={`${overview?.student_count || 0}`}
          icon={<Users size={18} className="text-blue-400" />}
          trend="Enrolled candidates"
          trendUp={true}
          color="blue"
        />
        <StatCard
          label="Avg Aptitude"
          value={`${overview?.avg_aptitude_score || 0}%`}
          icon={<Brain size={18} className="text-purple-400" />}
          trend="Mastery index"
          trendUp={true}
          color="purple"
        />
        <StatCard
          label="Avg Coding"
          value={`${overview?.avg_coding_score || 0}%`}
          icon={<Code2 size={18} className="text-emerald-400" />}
          trend="Test case pass rate"
          trendUp={true}
          color="green"
        />
        <StatCard
          label="Avg Test Score"
          value={`${overview?.avg_test_score || 0}%`}
          icon={<BarChart3 size={18} className="text-amber-400" />}
          trend="Graded assessments"
          trendUp={true}
          color="orange"
        />
        <StatCard
          label="At-Risk Students"
          value={`${overview?.at_risk_count || 0}`}
          icon={<AlertTriangle size={18} className="text-red-400" />}
          trend="Requires intervention"
          trendUp={false}
          color="orange"
        />
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-2 border-b border-border/40 pb-2 overflow-x-auto text-xs font-semibold">
        {[
          { key: 'clusters', label: 'K-Means Grouping', icon: Users },
          { key: 'readiness', label: 'Placement Readiness (XGBoost)', icon: TrendingUp },
          { key: 'topics', label: 'Topic Mastery', icon: Brain },
          { key: 'coding', label: 'Coding Analytics', icon: Code2 },
          { key: 'malpractice', label: 'Malpractice Reports', icon: ShieldAlert },
          { key: 'plagiarism', label: 'Plagiarism Review', icon: Sparkles },
          { key: 'anomalies', label: 'Behavioral Anomalies', icon: AlertTriangle },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-all shrink-0 ${
                isActive
                  ? 'bg-forge-600 text-white shadow-md shadow-forge-500/20'
                  : 'text-muted-foreground hover:bg-white/5'
              }`}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* TAB CONTENT: K-Means Student Grouping */}
      {activeTab === 'clusters' && (
        <div className="space-y-6">
          {clustering?.status === 'INSUFFICIENT_DATA' ? (
            <div className="glass-card p-8 rounded-2xl border border-border/60 text-center">
              <Users size={36} className="text-muted-foreground/40 mx-auto mb-2" />
              <h3 className="font-bold text-sm text-foreground">Insufficient Data for Clustering</h3>
              <p className="text-xs text-muted-foreground max-w-md mx-auto mt-1">
                {clustering.message || 'K-Means clustering requires at least 3 students with performance history.'}
              </p>
            </div>
          ) : (
            <>
              {/* Cluster Summaries */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {clustering?.clusters.map((c) => (
                  <div
                    key={c.cluster_id}
                    className="glass-card p-5 rounded-2xl border border-border/60 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-foreground">{c.label}</span>
                      <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-white/10 text-muted-foreground">
                        {c.student_count} Students
                      </span>
                    </div>

                    <div className="space-y-1.5 text-xs text-muted-foreground pt-2 border-t border-border/30">
                      <div className="flex justify-between">
                        <span>Avg Aptitude:</span>
                        <strong className="text-foreground">{c.avg_aptitude}%</strong>
                      </div>
                      <div className="flex justify-between">
                        <span>Avg Coding:</span>
                        <strong className="text-foreground">{c.avg_coding}%</strong>
                      </div>
                      <div className="flex justify-between">
                        <span>Avg Assessment:</span>
                        <strong className="text-foreground">{c.avg_test_score}%</strong>
                      </div>
                      <div className="flex justify-between">
                        <span>Avg Streak:</span>
                        <strong className="text-foreground">{c.avg_streak} days</strong>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Student Assignments Table */}
              <div className="glass-card rounded-2xl border border-border/60 overflow-hidden">
                <div className="p-4 bg-white/5 border-b border-border/40 font-bold text-xs text-foreground">
                  Individual Student Performance Groupings
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-white/5 border-b border-border/30 text-[11px] uppercase text-muted-foreground">
                      <tr>
                        <th className="py-3 px-4">Student</th>
                        <th className="py-3 px-4">Assigned Cluster</th>
                        <th className="py-3 px-4">Aptitude Score</th>
                        <th className="py-3 px-4">Coding Score</th>
                        <th className="py-3 px-4">Avg Assessment</th>
                        <th className="py-3 px-4 text-right">Profile</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/20">
                      {clustering?.students.map((st) => (
                        <tr key={st.student_id} className="hover:bg-white/5 transition-colors">
                          <td className="py-3 px-4 font-semibold text-foreground">
                            {st.full_name}
                            <div className="text-[11px] text-muted-foreground font-normal">{st.email}</div>
                          </td>
                          <td className="py-3 px-4">
                            <Badge
                              variant={
                                st.performance_group.includes('High') || st.performance_group.includes('Proficient')
                                  ? 'success'
                                  : st.performance_group.includes('Developing')
                                  ? 'info'
                                  : 'error'
                              }
                            >
                              {st.performance_group}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 font-medium text-foreground">{st.aptitude_score || 0}%</td>
                          <td className="py-3 px-4 font-medium text-foreground">{st.coding_score || 0}%</td>
                          <td className="py-3 px-4 font-medium text-foreground">{st.avg_test_score || 0}%</td>
                          <td className="py-3 px-4 text-right">
                            <button
                              onClick={() => navigate(`/trainer/analytics/students/${st.student_id}`)}
                              className="px-3 py-1 rounded-lg bg-forge-600/20 hover:bg-forge-600 text-forge-300 hover:text-white border border-forge-500/30 text-xs font-semibold transition-colors flex items-center gap-1 ml-auto"
                            >
                              <Eye size={12} /> View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* TAB CONTENT: Plagiarism Review */}
      {activeTab === 'plagiarism' && (
        <div className="glass-card rounded-2xl border border-border/60 overflow-hidden space-y-4">
          <div className="p-4 bg-white/5 border-b border-border/40 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-sm text-foreground">Code Similarity & Plagiarism Review</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                Submissions analyzed across token n-grams, identifier normalization, and whitespace stripping.
              </p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
              {plagiarism?.flagged_pairs_count || 0} Flagged Pairs
            </span>
          </div>

          {plagiarism?.flagged_pairs && plagiarism.flagged_pairs.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-white/5 border-b border-border/30 text-[11px] uppercase text-muted-foreground">
                  <tr>
                    <th className="py-3 px-4">Student A</th>
                    <th className="py-3 px-4">Student B</th>
                    <th className="py-3 px-4">Language</th>
                    <th className="py-3 px-4">Structural Similarity</th>
                    <th className="py-3 px-4">Risk Level</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/20">
                  {plagiarism.flagged_pairs.map((pair, idx) => (
                    <tr key={idx} className="hover:bg-white/5">
                      <td className="py-3 px-4 font-semibold text-foreground">
                        {pair.student_a_name} (ID: {pair.student_a_id})
                      </td>
                      <td className="py-3 px-4 font-semibold text-foreground">
                        {pair.student_b_name} (ID: {pair.student_b_id})
                      </td>
                      <td className="py-3 px-4 uppercase font-mono text-muted-foreground">
                        {pair.language}
                      </td>
                      <td className="py-3 px-4">
                        <strong className="text-red-400 font-bold text-sm">
                          {pair.similarity_score}%
                        </strong>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={pair.risk_level === 'HIGH' ? 'error' : 'warning'}>
                          {pair.risk_level} RISK
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-muted-foreground">
              <CheckCircle2 size={32} className="text-emerald-400 mx-auto mb-2 opacity-80" />
              No suspicious code similarity or copied submissions detected in current batch.
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: Malpractice Reports */}
      {activeTab === 'malpractice' && (
        <div className="glass-card rounded-2xl border border-border/60 overflow-hidden space-y-4">
          <div className="p-4 bg-white/5 border-b border-border/40 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-sm text-foreground">Proctoring Telemetry & Anti-Malpractice Audit</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                Tracks tab switches, window blur events, clipboard copy/paste, and fullscreen exit attempts.
              </p>
            </div>
            {malpractice && (
              <div className="flex items-center gap-2 text-xs">
                <span className="px-2 py-0.5 rounded-full bg-red-500/20 text-red-300 font-semibold border border-red-500/30">
                  {malpractice.high_risk_count} High Risk
                </span>
                <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/30">
                  {malpractice.medium_risk_count} Medium Risk
                </span>
              </div>
            )}
          </div>

          {malpractice?.student_reports && malpractice.student_reports.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-white/5 border-b border-border/30 text-[11px] uppercase text-muted-foreground">
                  <tr>
                    <th className="py-3 px-4">Candidate</th>
                    <th className="py-3 px-4">Risk Level</th>
                    <th className="py-3 px-4">Total Violations</th>
                    <th className="py-3 px-4">Tab Switches</th>
                    <th className="py-3 px-4">Window Blurs</th>
                    <th className="py-3 px-4">Fullscreen Exits</th>
                    <th className="py-3 px-4">Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/20">
                  {malpractice.student_reports.map((rep) => (
                    <tr key={rep.attempt_id} className="hover:bg-white/5">
                      <td className="py-3 px-4 font-semibold text-foreground">
                        {rep.student_name}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={rep.risk_level === 'HIGH' ? 'error' : rep.risk_level === 'MEDIUM' ? 'warning' : 'success'}>
                          {rep.risk_level}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 font-bold text-foreground">
                        {rep.total_violations}
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">
                        {rep.breakdown?.tab_switch || 0}
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">
                        {rep.breakdown?.window_blur || 0}
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">
                        {rep.breakdown?.fullscreen_exit || 0}
                      </td>
                      <td className="py-3 px-4 font-semibold text-foreground">
                        {rep.percentage !== undefined ? `${rep.percentage}%` : 'In Progress'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-muted-foreground">
              No malpractice events recorded for the selected assessment.
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: Behavioral Anomalies (Isolation Forest) */}
      {activeTab === 'anomalies' && (
        <div className="glass-card rounded-2xl border border-border/60 overflow-hidden space-y-4">
          <div className="p-4 bg-white/5 border-b border-border/40">
            <h3 className="font-bold text-sm text-foreground">Isolation Forest Behavioral Anomaly Detection</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Multivariate outlier detection combining completion velocity, score jumps, and violation spikes.
            </p>
          </div>

          {anomalies?.status === 'INSUFFICIENT_DATA' ? (
            <div className="p-8 text-center text-xs text-muted-foreground">
              {anomalies.message || 'At least 4 assessment attempts required for statistically meaningful Isolation Forest evaluation.'}
            </div>
          ) : anomalies?.anomalies && anomalies.anomalies.length > 0 ? (
            <div className="p-4 space-y-3">
              {anomalies.anomalies.map((an, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-white/5 border border-red-500/30 flex items-start justify-between gap-4">
                  <div>
                    <div className="font-bold text-xs text-foreground flex items-center gap-2">
                      <span>{an.student_name}</span>
                      <Badge variant={an.risk_level === 'HIGH' ? 'error' : 'warning'}>{an.risk_level} RISK</Badge>
                    </div>
                    <div className="text-[11px] text-muted-foreground mt-1 flex flex-wrap gap-2">
                      {an.detected_signals.map((sig, sidx) => (
                        <span key={sidx} className="px-2 py-0.5 rounded-md bg-red-500/10 text-red-300 border border-red-500/20">
                          {sig}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="text-right text-xs">
                    <div className="font-bold text-foreground">{an.score_percentage}% Score</div>
                    <div className="text-[11px] text-muted-foreground">{an.duration_seconds}s duration • {an.violation_count} violations</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-muted-foreground">
              <CheckCircle2 size={32} className="text-emerald-400 mx-auto mb-2 opacity-80" />
              No statistical anomalies detected by Isolation Forest.
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: Topic Mastery */}
      {activeTab === 'topics' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-4">
            <h3 className="font-bold text-sm text-foreground flex items-center gap-2">
              <AlertTriangle size={16} className="text-red-400" />
              Weakest Topics (Needs Attention)
            </h3>
            <div className="space-y-3">
              {topicAnalytics?.weakest?.map((t: any) => (
                <div key={t.topic_id} className="p-3 rounded-xl bg-white/5 border border-border/40 flex justify-between items-center text-xs">
                  <div>
                    <div className="font-semibold text-foreground">{t.topic_name}</div>
                    <div className="text-muted-foreground text-[11px]">{t.total_attempted} problems attempted</div>
                  </div>
                  <strong className="text-red-400">{t.accuracy}%</strong>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-4">
            <h3 className="font-bold text-sm text-foreground flex items-center gap-2">
              <CheckCircle2 size={16} className="text-emerald-400" />
              Strongest Topics (Mastered)
            </h3>
            <div className="space-y-3">
              {topicAnalytics?.strongest?.map((t: any) => (
                <div key={t.topic_id} className="p-3 rounded-xl bg-white/5 border border-border/40 flex justify-between items-center text-xs">
                  <div>
                    <div className="font-semibold text-foreground">{t.topic_name}</div>
                    <div className="text-muted-foreground text-[11px]">{t.total_attempted} problems attempted</div>
                  </div>
                  <strong className="text-emerald-400">{t.accuracy}%</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Coding Analytics */}
      {activeTab === 'coding' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-4">
            <h3 className="font-bold text-sm text-foreground">Language Distribution</h3>
            <div className="space-y-2 text-xs">
              {Object.entries(codingAnalytics?.language_breakdown || {}).map(([lang, count]: any) => (
                <div key={lang} className="p-3 rounded-xl bg-white/5 flex justify-between items-center">
                  <span className="uppercase font-mono font-semibold">{lang}</span>
                  <span className="font-bold text-forge-300">{count} submissions</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-4">
            <h3 className="font-bold text-sm text-foreground">Verdicts & Error Breakdown</h3>
            <div className="space-y-2 text-xs">
              {Object.entries(codingAnalytics?.verdict_breakdown || {}).map(([verdict, count]: any) => (
                <div key={verdict} className="p-3 rounded-xl bg-white/5 flex justify-between items-center">
                  <span className="font-semibold">{verdict.replace(/_/g, ' ')}</span>
                  <span className="font-bold text-foreground">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: Placement Readiness (XGBoost Multi-Class ML) */}
      {activeTab === 'readiness' && (
        <div className="space-y-6">
          {/* Readiness Summary Bar */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 p-5 rounded-2xl glass-card border border-border/60">
            <div>
              <h3 className="font-bold text-base text-foreground flex items-center gap-2">
                <TrendingUp size={18} className="text-emerald-400" />
                XGBoost Placement Readiness Intelligence
              </h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                Multi-dimensional tabular ML model evaluating aptitude accuracy, coding pass rates, and performance velocity.
              </p>
            </div>
            <button
              onClick={handleRetrainReadiness}
              disabled={retraining}
              className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-md disabled:opacity-50"
            >
              <RefreshCw size={14} className={retraining ? 'animate-spin' : ''} />
              {retraining ? 'Retraining ML Pipeline...' : 'Retrain Readiness Model'}
            </button>
          </div>

          {/* Three Tier KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="glass-card p-5 border border-emerald-500/30 bg-emerald-500/5 rounded-2xl">
              <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Placement Ready</div>
              <div className="text-3xl font-bold font-display mt-2 text-foreground">
                {readiness?.readiness_summary?.placement_ready_count || 0}
              </div>
              <div className="text-[11px] text-muted-foreground mt-1">High aptitude + strong coding pass rate</div>
            </div>

            <div className="glass-card p-5 border border-amber-500/30 bg-amber-500/5 rounded-2xl">
              <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Developing Candidates</div>
              <div className="text-3xl font-bold font-display mt-2 text-foreground">
                {readiness?.readiness_summary?.developing_count || 0}
              </div>
              <div className="text-[11px] text-muted-foreground mt-1">Solid foundations, requires targeted practice</div>
            </div>

            <div className="glass-card p-5 border border-red-500/30 bg-red-500/5 rounded-2xl">
              <div className="text-xs font-semibold text-red-400 uppercase tracking-wider">Needs Attention / Improvement</div>
              <div className="text-3xl font-bold font-display mt-2 text-foreground">
                {readiness?.readiness_summary?.needs_improvement_count || 0}
              </div>
              <div className="text-[11px] text-muted-foreground mt-1">Immediate intervention recommended</div>
            </div>
          </div>

          {/* Students Readiness Table */}
          <div className="glass-card rounded-2xl border border-border/60 overflow-hidden">
            <div className="p-4 border-b border-border/40 font-bold text-sm text-foreground">
              Candidate Readiness Profiles ({readiness?.students?.length || 0})
            </div>
            {readiness?.students && readiness.students.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead className="bg-white/5 text-muted-foreground font-semibold uppercase text-[10px] border-b border-border/40">
                    <tr>
                      <th className="p-4">Student</th>
                      <th className="p-4">Readiness Category</th>
                      <th className="p-4">Score</th>
                      <th className="p-4">Key Strengths</th>
                      <th className="p-4">Focus Areas</th>
                      <th className="p-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/30">
                    {readiness.students.map((st) => (
                      <tr key={st.student_id} className="hover:bg-white/5 transition">
                        <td className="p-4 font-semibold text-foreground">
                          {st.full_name}
                          <div className="text-[11px] text-muted-foreground font-normal">{st.email}</div>
                        </td>
                        <td className="p-4">
                          <Badge
                            variant={
                              st.readiness_category === 'PLACEMENT_READY'
                                ? 'success'
                                : st.readiness_category === 'DEVELOPING'
                                ? 'warning'
                                : 'error'
                            }
                          >
                            {st.readiness_category.replace(/_/g, ' ')}
                          </Badge>
                        </td>
                        <td className="p-4 font-bold text-sm">
                          {Math.round(st.readiness_score)}%
                        </td>
                        <td className="p-4">
                          <div className="space-y-1">
                            {st.contributing_factors?.strengths?.slice(0, 2).map((s: string, idx: number) => (
                              <div key={idx} className="text-[11px] text-emerald-400 flex items-center gap-1">
                                • {s}
                              </div>
                            )) || <span className="text-muted-foreground text-[11px]">—</span>}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="space-y-1">
                            {st.contributing_factors?.areas_for_improvement?.slice(0, 2).map((imp: string, idx: number) => (
                              <div key={idx} className="text-[11px] text-amber-400 flex items-center gap-1">
                                • {imp}
                              </div>
                            )) || <span className="text-muted-foreground text-[11px]">—</span>}
                          </div>
                        </td>
                        <td className="p-4 text-right">
                          <button
                            onClick={() => navigate(`/trainer/students/${st.student_id}`)}
                            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-forge-400 transition"
                            title="View Full Profile"
                          >
                            <Eye size={14} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-muted-foreground">
                No readiness records available for this cohort.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
