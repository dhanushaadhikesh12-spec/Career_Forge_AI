import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '@/services/api';
import { LoadingSpinner, ErrorState, Badge } from '@/components/shared';
import {
  Trophy,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowRight,
  RotateCcw,
  Sparkles,
  HelpCircle,
  Award,
  ChevronDown,
  Code2,
  FileCode,
  Check,
  Copy,
  AlertTriangle,
  Flame,
} from 'lucide-react';

interface ReviewQuestion {
  question_id: number;
  title?: string;
  text: string;
  points: number;
  difficulty?: string;
  selected_option_id?: number | null;
  correct_option_id?: number | null;
  is_correct: boolean;
  marks_awarded: number;
  verdict?: string;
  language?: string | null;
  source_code?: string | null;
  test_cases_passed?: number;
  test_cases_total?: number;
  constraints?: string | null;
  explanation?: string | null;
  options: Array<{ id: number; text: string }>;
}

interface TestReviewData {
  attempt_id: number;
  test_id: number;
  test_title: string;
  test_type: string;
  status: string;
  score: number;
  max_score: number;
  percentage: number;
  passed: boolean | null;
  passing_marks: number | null;
  started_at: string;
  submitted_at: string;
  total_questions: number;
  correct_answers: number;
  questions: ReviewQuestion[];
}

export default function TestResultPage() {
  const { attemptId } = useParams<{ attemptId: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<TestReviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [copiedId, setCopiedId] = useState<number | null>(null);

  useEffect(() => {
    if (attemptId) {
      fetchReview(parseInt(attemptId));
    }
  }, [attemptId]);

  const fetchReview = async (id: number) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.getTestAttemptReview(id);
      setData(res);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to load test results');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = (id: number, code: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[70vh]" />;
  if (error) return <ErrorState message={error} onRetry={() => attemptId && fetchReview(parseInt(attemptId))} />;
  if (!data) return <ErrorState message="Scorecard not found." />;

  const isCoding = data.test_type === 'CODING';
  const pct = Math.round(data.percentage || 0);
  const isPassed = data.passed ?? (pct >= 60);

  const getVerdictBadge = (verdict?: string) => {
    switch (verdict) {
      case 'ACCEPTED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 size={13} /> Accepted
          </span>
        );
      case 'WRONG_ANSWER':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-500/15 text-red-400 border border-red-500/30">
            <XCircle size={13} /> Wrong Answer
          </span>
        );
      case 'TIME_LIMIT_EXCEEDED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <Clock size={13} /> Time Limit Exceeded
          </span>
        );
      case 'COMPILATION_ERROR':
      case 'RUNTIME_ERROR':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <AlertTriangle size={13} /> {verdict === 'COMPILATION_ERROR' ? 'Compilation Error' : 'Runtime Error'}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-muted-foreground border border-border">
            <HelpCircle size={13} /> Not Attempted
          </span>
        );
    }
  };

  const getDifficultyBadge = (difficulty?: string) => {
    const diff = (difficulty || 'MEDIUM').toUpperCase();
    if (diff === 'EASY') {
      return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">EASY</span>;
    }
    if (diff === 'HARD') {
      return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">HARD</span>;
    }
    return <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">MEDIUM</span>;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in py-6">
      {/* Scorecard Hero Banner */}
      <div
        className={`glass-card p-8 rounded-3xl border relative overflow-hidden text-center space-y-6 ${
          isPassed
            ? 'border-emerald-500/30 bg-gradient-to-b from-emerald-950/20 via-card to-card'
            : 'border-red-500/30 bg-gradient-to-b from-red-950/20 via-card to-card'
        }`}
      >
        <div
          className={`w-20 h-20 rounded-3xl mx-auto flex items-center justify-center shadow-xl ${
            isPassed
              ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-emerald-500/20'
              : 'bg-gradient-to-br from-red-500 to-rose-600 text-white shadow-red-500/20'
          }`}
        >
          {isPassed ? <Trophy size={36} /> : <Award size={36} />}
        </div>

        <div>
          <Badge variant={isPassed ? 'success' : 'error'}>
            {isPassed ? 'ASSESSMENT PASSED' : 'BENCHMARK NOT MET'}
          </Badge>
          <h1 className="text-3xl font-bold font-display text-white mt-3">{data.test_title}</h1>
          <p className="text-xs text-muted-foreground mt-1">
            Submitted on {new Date(data.submitted_at).toLocaleString()}
          </p>
        </div>

        {/* Big Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-2xl mx-auto">
          <div className="glass-card p-4 border border-border/50">
            <div className="text-[11px] text-muted-foreground uppercase font-semibold">Score</div>
            <div className="text-2xl font-bold text-foreground mt-1">
              {Number(data.score).toFixed(1)} <span className="text-xs text-muted-foreground">/ {data.max_score}</span>
            </div>
          </div>

          <div className="glass-card p-4 border border-border/50">
            <div className="text-[11px] text-muted-foreground uppercase font-semibold">Percentage</div>
            <div
              className={`text-2xl font-bold mt-1 ${isPassed ? 'text-emerald-400' : 'text-red-400'}`}
            >
              {pct}%
            </div>
          </div>

          <div className="glass-card p-4 border border-border/50">
            <div className="text-[11px] text-muted-foreground uppercase font-semibold">Accuracy</div>
            <div className="text-2xl font-bold text-forge-400 mt-1">
              {data.total_questions > 0
                ? Math.round((data.correct_answers / data.total_questions) * 100)
                : 0}
              %
            </div>
          </div>

          <div className="glass-card p-4 border border-border/50">
            <div className="text-[11px] text-muted-foreground uppercase font-semibold">
              {isCoding ? 'Solved' : 'Correct'}
            </div>
            <div className="text-2xl font-bold text-emerald-400 mt-1">
              {data.correct_answers} / {data.total_questions}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <Link
            to="/student/dashboard"
            className="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-border text-xs font-semibold text-foreground transition-colors"
          >
            Back to Dashboard
          </Link>
          <Link
            to="/student/tests"
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold text-xs glow-button transition-all flex items-center gap-1.5"
          >
            Explore More Tests <ArrowRight size={14} />
          </Link>
        </div>
      </div>

      {/* Question by Question Detailed Review */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground">
            {isCoding ? 'Detailed Coding Problem Review' : 'Detailed Question Review'}
          </h2>
          <span className="text-xs text-muted-foreground">
            {data.correct_answers} {isCoding ? 'solved' : 'correct'} out of {data.total_questions} problems
          </span>
        </div>

        <div className="space-y-5">
          {data.questions.map((q, idx) => {
            if (isCoding) {
              // Dedicated Coding Problem Review Card
              return (
                <div
                  key={q.question_id}
                  className={`glass-card p-6 border rounded-2xl space-y-4 transition-all ${
                    q.is_correct
                      ? 'border-emerald-500/30 bg-emerald-950/5'
                      : q.verdict === 'NOT_ATTEMPTED'
                      ? 'border-border/40 bg-card/60'
                      : 'border-red-500/30 bg-red-950/5'
                  }`}
                >
                  {/* Top Bar: Problem #, Title, Difficulty, Verdict, Marks */}
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <span className="w-7 h-7 rounded-lg bg-forge-500/15 border border-forge-500/30 flex items-center justify-center text-xs font-mono font-bold text-forge-400">
                        {idx + 1}
                      </span>
                      <h3 className="text-base font-bold text-foreground">
                        {q.title || `Problem ${idx + 1}`}
                      </h3>
                      {getDifficultyBadge(q.difficulty)}
                    </div>

                    <div className="flex items-center gap-3">
                      {getVerdictBadge(q.verdict)}
                      <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-white/5 border border-border text-foreground">
                        {Number(q.marks_awarded || 0).toFixed(1)} / {Number(q.points || 5).toFixed(1)} pts
                      </span>
                    </div>
                  </div>

                  {/* Problem Statement */}
                  <div className="space-y-2">
                    <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                      Problem Statement
                    </div>
                    <p className="text-sm text-foreground/90 whitespace-pre-wrap leading-relaxed">
                      {q.text}
                    </p>
                  </div>

                  {/* Constraints if present */}
                  {q.constraints && (
                    <div className="p-3 rounded-xl bg-white/5 border border-border/40 space-y-1">
                      <div className="text-[11px] font-semibold text-muted-foreground uppercase">
                        Constraints
                      </div>
                      <p className="text-xs font-mono text-muted-foreground/90">{q.constraints}</p>
                    </div>
                  )}

                  {/* Test Cases Passed Summary */}
                  {q.verdict !== 'NOT_ATTEMPTED' && (
                    <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-border/40 text-xs">
                      <span className="text-muted-foreground">
                        Test Cases Evaluation:{' '}
                        <strong className="text-foreground">
                          {q.test_cases_passed || 0} / {q.test_cases_total || 0} passed
                        </strong>
                      </span>
                      <div className="w-36 h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            q.is_correct ? 'bg-emerald-500' : 'bg-red-500'
                          }`}
                          style={{
                            width: `${
                              q.test_cases_total
                                ? Math.min(100, Math.round(((q.test_cases_passed || 0) / q.test_cases_total) * 100))
                                : 0
                            }%`,
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Submitted Source Code */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
                        <Code2 size={14} className="text-forge-400" />
                        <span>Submitted Solution</span>
                        {q.language && (
                          <span className="text-[11px] px-2 py-0.5 rounded bg-white/10 text-muted-foreground font-mono">
                            {q.language}
                          </span>
                        )}
                      </div>

                      {q.source_code && (
                        <button
                          type="button"
                          onClick={() => handleCopyCode(q.question_id, q.source_code || '')}
                          className="text-[11px] text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors px-2 py-1 rounded bg-white/5"
                        >
                          {copiedId === q.question_id ? (
                            <>
                              <Check size={12} className="text-emerald-400" /> Copied
                            </>
                          ) : (
                            <>
                              <Copy size={12} /> Copy Code
                            </>
                          )}
                        </button>
                      )}
                    </div>

                    {q.source_code ? (
                      <pre className="p-4 rounded-xl bg-slate-950 border border-border/50 text-xs font-mono text-emerald-400/90 overflow-x-auto leading-relaxed max-h-80 select-all">
                        <code>{q.source_code}</code>
                      </pre>
                    ) : (
                      <div className="p-4 rounded-xl bg-white/5 border border-dashed border-border/40 text-xs text-muted-foreground flex items-center gap-2">
                        <FileCode size={16} />
                        No code was submitted for this problem during the assessment.
                      </div>
                    )}
                  </div>

                  {/* Explanation / Optimal Approach */}
                  {q.explanation && (
                    <div className="p-4 rounded-xl bg-forge-500/10 border border-forge-500/20 text-xs text-muted-foreground space-y-1">
                      <div className="font-semibold text-forge-300 flex items-center gap-1.5">
                        <Sparkles size={14} /> Optimal Approach / Explanation
                      </div>
                      <p className="leading-relaxed text-foreground/80">{q.explanation}</p>
                    </div>
                  )}
                </div>
              );
            }

            // Aptitude MCQ Review Card
            return (
              <div
                key={q.question_id}
                className={`glass-card p-6 border rounded-2xl space-y-4 transition-all ${
                  q.is_correct
                    ? 'border-emerald-500/30 bg-emerald-950/5'
                    : 'border-red-500/30 bg-red-950/5'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-lg bg-white/5 flex items-center justify-center text-xs font-mono font-bold text-muted-foreground">
                      {idx + 1}
                    </span>
                    <span className="text-xs font-semibold text-muted-foreground">
                      Worth {q.points} {q.points === 1 ? 'mark' : 'marks'}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {q.is_correct ? (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400">
                        <CheckCircle2 size={15} /> Correct (+{q.marks_awarded})
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-red-400">
                        <XCircle size={15} /> Incorrect (0)
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-sm font-semibold text-foreground leading-relaxed">{q.text}</p>

                {/* Options List */}
                <div className="space-y-2 pt-1">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = q.selected_option_id === opt.id;
                    const isCorrect = q.correct_option_id === opt.id;
                    const letter = String.fromCharCode(65 + optIdx);

                    let style = 'bg-white/5 border-border/40 text-muted-foreground';
                    if (isCorrect) {
                      style = 'bg-emerald-500/20 border-emerald-500 text-emerald-300 font-semibold ring-1 ring-emerald-500';
                    } else if (isSelected && !q.is_correct) {
                      style = 'bg-red-500/20 border-red-500 text-red-300 font-semibold ring-1 ring-red-500';
                    }

                    return (
                      <div
                        key={opt.id}
                        className={`p-3 rounded-xl border text-xs flex items-center justify-between gap-3 ${style}`}
                      >
                        <div className="flex items-center gap-3">
                          <span className="w-5 h-5 rounded flex items-center justify-center font-mono font-bold text-[11px] bg-white/10">
                            {letter}
                          </span>
                          <span>{opt.text}</span>
                        </div>

                        {isCorrect && (
                          <span className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 size={13} /> Correct Answer
                          </span>
                        )}
                        {isSelected && !isCorrect && (
                          <span className="text-[11px] font-semibold text-red-400 flex items-center gap-1">
                            <XCircle size={13} /> Your Choice
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Explanation */}
                {q.explanation && (
                  <div className="p-3.5 rounded-xl bg-white/5 border border-border/40 text-xs text-muted-foreground leading-relaxed">
                    <span className="font-semibold text-foreground">Explanation: </span>
                    {q.explanation}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
