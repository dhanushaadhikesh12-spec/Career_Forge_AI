import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  User, ArrowLeft, Brain, Code2, Trophy, Flame,
  ShieldAlert, Clock, CheckCircle2, XCircle, AlertTriangle, FileCode, TrendingUp
} from 'lucide-react';
import { api } from '@/services/api';
import type { TrainerStudentProfile } from '@/types';
import { Badge, LoadingSpinner, StatCard } from '@/components/shared';

export default function TrainerStudentProfilePage() {
  const { studentId } = useParams<{ studentId: string }>();
  const navigate = useNavigate();

  const [profile, setProfile] = useState<TrainerStudentProfile | null>(null);
  const [readiness, setReadiness] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (studentId) {
      loadProfile(parseInt(studentId));
    }
  }, [studentId]);

  async function loadProfile(id: number) {
    setIsLoading(true);
    try {
      const [data, rd] = await Promise.all([
        api.getTrainerStudentProfile(id),
        api.getStudentReadiness(id).catch(() => null),
      ]);
      setProfile(data);
      if (rd?.prediction) {
        setReadiness(rd.prediction);
      }
    } catch (err) {
      console.error('Failed to load student analytics profile:', err);
    } finally {
      setIsLoading(false);
    }
  }

  if (isLoading || !profile) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const { student, weak_topics, strong_topics, topic_metrics, test_history, coding_history } = profile;

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <button
          onClick={() => navigate('/trainer/analytics')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-white transition-colors"
        >
          <ArrowLeft size={16} />
          Back to Analytics
        </button>
      </div>

      {/* Candidate Card */}
      <div className="glass-card p-6 rounded-2xl border border-border/60 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-navy-800 border border-teal-500/40 flex items-center justify-center text-teal-300 font-bold text-lg shadow-sm">
            {student.full_name?.charAt(0) || 'S'}
          </div>
          <div>
            <h1 className="text-2xl font-bold font-display text-white">{student.full_name}</h1>
            <p className="text-xs text-muted-foreground mt-0.5">{student.email}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-forge-500/20 text-forge-300 font-semibold border border-forge-500/30 flex items-center gap-1">
                <Flame size={12} className="text-orange-400" />
                {student.streak_days} Day Streak
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="text-right">
            <div className="text-xs text-muted-foreground font-semibold">Placement Readiness</div>
            <div className="text-3xl font-black font-display gradient-text">
              {Math.round(student.total_score || 0)}%
            </div>
          </div>
        </div>
      </div>

      {/* Three Pillar KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <StatCard
          label="Overall Score"
          value={`${Math.round(student.total_score || 0)}`}
          icon={<Trophy size={18} className="text-forge-400" />}
          trend="Combined aptitude & coding"
          trendUp={true}
          color="blue"
        />
        <StatCard
          label="Aptitude Mastery"
          value={`${Math.round(student.aptitude_score || 0)}%`}
          icon={<Brain size={18} className="text-teal-400" />}
          trend="Calibrated IRT Elo"
          trendUp={true}
          color="teal"
        />
        <StatCard
          label="Coding Score"
          value={`${Math.round(student.coding_score || 0)}%`}
          icon={<Code2 size={18} className="text-emerald-400" />}
          trend="Algorithmic pass rate"
          trendUp={true}
          color="green"
        />
      </div>

      {/* XGBoost Placement Readiness Intelligence Card */}
      {readiness && (
        <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <div className="flex items-center gap-2">
                <TrendingUp size={18} className="text-emerald-400" />
                <h3 className="font-bold text-sm text-foreground">
                  XGBoost Placement Readiness Assessment
                </h3>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                Multi-dimensional tabular model evaluation across aptitude, coding velocity, and assessment history.
              </p>
            </div>
            <div className="flex items-center gap-2.5">
              <Badge
                variant={
                  readiness.readiness_category === 'PLACEMENT_READY'
                    ? 'success'
                    : readiness.readiness_category === 'DEVELOPING'
                    ? 'warning'
                    : 'error'
                }
              >
                {readiness.readiness_category?.replace(/_/g, ' ') || 'NEEDS IMPROVEMENT'}
              </Badge>
              <div className="text-xl font-bold font-display gradient-text">
                {Math.round(readiness.readiness_score || 0)}%
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-border/40 text-xs">
            <div className="space-y-1.5">
              <span className="font-semibold text-emerald-400 flex items-center gap-1">
                <CheckCircle2 size={13} /> Contributing Strengths:
              </span>
              {readiness.contributing_factors?.strengths?.map((s: string, idx: number) => (
                <div key={idx} className="p-2 rounded-lg bg-emerald-500/10 text-emerald-300 text-[11px]">
                  • {s}
                </div>
              )) || <div className="text-muted-foreground text-[11px]">—</div>}
            </div>

            <div className="space-y-1.5">
              <span className="font-semibold text-amber-400 flex items-center gap-1">
                <AlertTriangle size={13} /> Recommended Focus Areas:
              </span>
              {readiness.contributing_factors?.areas_for_improvement?.map((imp: string, idx: number) => (
                <div key={idx} className="p-2 rounded-lg bg-amber-500/10 text-amber-300 text-[11px]">
                  • {imp}
                </div>
              )) || <div className="text-muted-foreground text-[11px]">—</div>}
            </div>
          </div>
        </div>
      )}

      {/* Strengths & Weaknesses Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-3">
          <h3 className="font-bold text-sm text-foreground flex items-center gap-2">
            <AlertTriangle size={16} className="text-red-400" />
            Critical Focus Areas (Weakest Topics)
          </h3>
          {weak_topics.length > 0 ? (
            <div className="space-y-2 text-xs">
              {weak_topics.map((t) => (
                <div key={t.topic_id} className="p-3 rounded-xl bg-white/5 flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-foreground">{t.topic_name}</div>
                    <div className="text-muted-foreground text-[11px]">{t.attempted} attempts • Elo {t.skill_rating}</div>
                  </div>
                  <strong className="text-red-400">{t.accuracy}%</strong>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">No weak topics recorded.</p>
          )}
        </div>

        <div className="glass-card p-6 rounded-2xl border border-border/60 space-y-3">
          <h3 className="font-bold text-sm text-foreground flex items-center gap-2">
            <CheckCircle2 size={16} className="text-emerald-400" />
            Demonstrated Strengths (Mastered Topics)
          </h3>
          {strong_topics.length > 0 ? (
            <div className="space-y-2 text-xs">
              {strong_topics.map((t) => (
                <div key={t.topic_id} className="p-3 rounded-xl bg-white/5 flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-foreground">{t.topic_name}</div>
                    <div className="text-muted-foreground text-[11px]">{t.attempted} attempts • Elo {t.skill_rating}</div>
                  </div>
                  <strong className="text-emerald-400">{t.accuracy}%</strong>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">No strong topics recorded yet.</p>
          )}
        </div>
      </div>

      {/* Recent Coding Submissions */}
      <div className="glass-card rounded-2xl border border-border/60 overflow-hidden space-y-3">
        <div className="p-4 bg-white/5 border-b border-border/40 font-bold text-xs text-foreground flex items-center gap-2">
          <FileCode size={16} className="text-forge-400" />
          Recent Code Submissions
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-white/5 border-b border-border/20 text-[11px] uppercase text-muted-foreground">
              <tr>
                <th className="py-2.5 px-4">Problem</th>
                <th className="py-2.5 px-4">Language</th>
                <th className="py-2.5 px-4">Verdict</th>
                <th className="py-2.5 px-4">Score</th>
                <th className="py-2.5 px-4">Tests Passed</th>
                <th className="py-2.5 px-4">Submitted At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/20">
              {coding_history.map((s) => (
                <tr key={s.submission_id} className="hover:bg-white/5">
                  <td className="py-2.5 px-4 font-semibold text-foreground">{s.question_title}</td>
                  <td className="py-2.5 px-4 uppercase font-mono text-muted-foreground">{s.language}</td>
                  <td className="py-2.5 px-4">
                    <Badge variant={s.verdict === 'ACCEPTED' ? 'success' : 'error'}>
                      {s.verdict}
                    </Badge>
                  </td>
                  <td className="py-2.5 px-4 font-semibold text-forge-300">{s.score}</td>
                  <td className="py-2.5 px-4 text-muted-foreground">{s.passed_tests} / {s.total_tests}</td>
                  <td className="py-2.5 px-4 text-muted-foreground">{new Date(s.submitted_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Test Attempts & Malpractice */}
      <div className="glass-card rounded-2xl border border-border/60 overflow-hidden space-y-3">
        <div className="p-4 bg-white/5 border-b border-border/40 font-bold text-xs text-foreground flex items-center gap-2">
          <ShieldAlert size={16} className="text-amber-400" />
          Test Attempts & Proctoring History
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-white/5 border-b border-border/20 text-[11px] uppercase text-muted-foreground">
              <tr>
                <th className="py-2.5 px-4">Assessment</th>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Score</th>
                <th className="py-2.5 px-4">Percentage</th>
                <th className="py-2.5 px-4">Violations Recorded</th>
                <th className="py-2.5 px-4">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/20">
              {test_history.map((t) => (
                <tr key={t.attempt_id} className="hover:bg-white/5">
                  <td className="py-2.5 px-4 font-semibold text-foreground">{t.test_title}</td>
                  <td className="py-2.5 px-4">
                    <Badge variant={t.status === 'GRADED' ? 'success' : 'warning'}>{t.status}</Badge>
                  </td>
                  <td className="py-2.5 px-4">{t.score} / {t.max_score}</td>
                  <td className="py-2.5 px-4 font-semibold">{t.percentage || 0}%</td>
                  <td className="py-2.5 px-4">
                    {t.violations_count > 0 ? (
                      <span className="text-red-400 font-bold">{t.violations_count} Warnings</span>
                    ) : (
                      <span className="text-emerald-400">Clean</span>
                    )}
                  </td>
                  <td className="py-2.5 px-4 text-muted-foreground">{new Date(t.date).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
