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
  Award,
  Code2,
  FileCode,
  Check,
  Copy,
  AlertTriangle,
  HelpCircle,
  Sparkles,
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
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 size={13} /> Accepted
          </span>
        );
      case 'WRONG_ANSWER':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/30">
            <XCircle size={13} /> Wrong Answer
          </span>
        );
      case 'TIME_LIMIT_EXCEEDED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <Clock size={13} /> Time Limit Exceeded
          </span>
        );
      case 'COMPILATION_ERROR':
      case 'RUNTIME_ERROR':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/30">
            <AlertTriangle size={13} /> {verdict === 'COMPILATION_ERROR' ? 'Compilation Error' : 'Runtime Error'}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <HelpCircle size={13} /> Not Attempted
          </span>
        );
    }
  };

  const getDifficultyBadge = (difficulty?: string) => {
    const diff = (difficulty || 'MEDIUM').toUpperCase();
    if (diff === 'EASY') {
      return <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">EASY</span>;
    }
    if (diff === 'HARD') {
      return <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">HARD</span>;
    }
    return <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">MEDIUM</span>;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-2">
      {/* Scorecard Hero Banner */}
      <div
        className={`p-6 sm:p-8 rounded-xl border bg-slate-900 text-center space-y-5 shadow-subtle ${
          isPassed ? 'border-emerald-500/40' : 'border-slate-800'
        }`}
      >
        <div
          className={`w-14 h-14 rounded-xl mx-auto flex items-center justify-center border ${
            isPassed
              ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400'
              : 'bg-slate-800 border-slate-700 text-slate-300'
          }`}
        >
          {isPassed ? <Trophy size={28} /> : <Award size={28} />}
        </div>

        <div>
          <Badge variant={isPassed ? 'success' : 'error'}>
            {isPassed ? 'ASSESSMENT PASSED' : 'BENCHMARK NOT MET'}
          </Badge>
          <h1 className="text-xl sm:text-2xl font-bold text-white mt-2 font-display">{data.test_title}</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Submitted on {new Date(data.submitted_at).toLocaleString()}
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-xl mx-auto">
          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Score</div>
            <div className="text-xl font-bold text-white mt-0.5">
              {Number(data.score).toFixed(1)} <span className="text-xs text-slate-500">/ {data.max_score}</span>
            </div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Percentage</div>
            <div className={`text-xl font-bold mt-0.5 ${isPassed ? 'text-emerald-400' : 'text-red-400'}`}>
              {pct}%
            </div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Accuracy</div>
            <div className="text-xl font-bold text-teal-400 mt-0.5">
              {data.total_questions > 0
                ? Math.round((data.correct_answers / data.total_questions) * 100)
                : 0}
              %
            </div>
          </div>

          <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">
              {isCoding ? 'Solved' : 'Correct'}
            </div>
            <div className="text-xl font-bold text-emerald-400 mt-0.5">
              {data.correct_answers} / {data.total_questions}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-2.5 pt-1">
          <Link
            to="/student/dashboard"
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition-colors"
          >
            Back to Dashboard
          </Link>
          <Link
            to="/student/tests"
            className="px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-subtle"
          >
            Explore More Tests <ArrowRight size={13} />
          </Link>
        </div>
      </div>

      {/* Question Detailed Review */}
      <div className="space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            {isCoding ? 'Coding Problem Review' : 'Question Breakdown'}
          </h2>
          <span className="text-xs text-slate-400">
            {data.correct_answers} {isCoding ? 'solved' : 'correct'} of {data.total_questions} problems
          </span>
        </div>

        <div className="space-y-4">
          {data.questions.map((q, idx) => {
            if (isCoding) {
              return (
                <div
                  key={q.question_id}
                  className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 shadow-subtle"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2.5">
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-mono font-bold text-slate-300">
                        {idx + 1}
                      </span>
                      <h3 className="text-sm font-bold text-white">
                        {q.title || `Problem ${idx + 1}`}
                      </h3>
                      {getDifficultyBadge(q.difficulty)}
                    </div>

                    <div className="flex items-center gap-2.5">
                      {getVerdictBadge(q.verdict)}
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
                        {Number(q.marks_awarded || 0).toFixed(1)} / {Number(q.points || 5).toFixed(1)} pts
                      </span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">
                      Problem Description
                    </div>
                    <p className="text-xs sm:text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">
                      {q.text}
                    </p>
                  </div>

                  {q.constraints && (
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                      <div className="text-[10px] font-semibold text-slate-500 uppercase">Constraints</div>
                      <p className="text-xs font-mono text-slate-400 mt-0.5">{q.constraints}</p>
                    </div>
                  )}

                  {q.verdict !== 'NOT_ATTEMPTED' && (
                    <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                      <span className="text-slate-400">
                        Test Cases Evaluation:{' '}
                        <strong className="text-white">
                          {q.test_cases_passed || 0} / {q.test_cases_total || 0} passed
                        </strong>
                      </span>
                      <div className="w-32 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${q.is_correct ? 'bg-emerald-500' : 'bg-red-500'}`}
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

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400">
                        <Code2 size={13} className="text-teal-400" />
                        <span>Submitted Solution</span>
                        {q.language && (
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 font-mono">
                            {q.language}
                          </span>
                        )}
                      </div>

                      {q.source_code && (
                        <button
                          type="button"
                          onClick={() => handleCopyCode(q.question_id, q.source_code || '')}
                          className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 transition-colors"
                        >
                          {copiedId === q.question_id ? (
                            <>
                              <Check size={12} className="text-emerald-400" /> Copied
                            </>
                          ) : (
                            <>
                              <Copy size={12} /> Copy
                            </>
                          )}
                        </button>
                      )}
                    </div>

                    {q.source_code ? (
                      <pre className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-400/90 overflow-x-auto leading-relaxed max-h-72">
                        <code>{q.source_code}</code>
                      </pre>
                    ) : (
                      <div className="p-3 rounded-lg bg-slate-950 border border-dashed border-slate-800 text-xs text-slate-500 flex items-center gap-2">
                        <FileCode size={15} />
                        No code was submitted for this problem.
                      </div>
                    )}
                  </div>

                  {q.explanation && (
                    <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1">
                      <div className="font-semibold text-teal-400 flex items-center gap-1">
                        <Sparkles size={13} /> Explanation
                      </div>
                      <p className="text-slate-300 leading-relaxed">{q.explanation}</p>
                    </div>
                  )}
                </div>
              );
            }

            // Aptitude MCQ Review
            return (
              <div
                key={q.question_id}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3.5 shadow-subtle"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded bg-slate-800 flex items-center justify-center text-xs font-mono font-bold text-slate-400">
                      {idx + 1}
                    </span>
                    <span className="text-xs font-medium text-slate-400">
                      Worth {q.points} {q.points === 1 ? 'mark' : 'marks'}
                    </span>
                  </div>

                  <div>
                    {q.is_correct ? (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-400">
                        <CheckCircle2 size={14} /> Correct (+{q.marks_awarded})
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-semibold text-red-400">
                        <XCircle size={14} /> Incorrect (0)
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs sm:text-sm font-semibold text-white leading-relaxed">{q.text}</p>

                <div className="space-y-1.5 pt-1">
                  {q.options.map((opt, optIdx) => {
                    const isSelected = q.selected_option_id === opt.id;
                    const isCorrect = q.correct_option_id === opt.id;
                    const letter = String.fromCharCode(65 + optIdx);

                    let style = 'bg-slate-950 border-slate-800 text-slate-400';
                    if (isCorrect) {
                      style = 'bg-emerald-950/40 border-emerald-500/80 text-emerald-200 font-semibold ring-1 ring-emerald-500/30';
                    } else if (isSelected && !q.is_correct) {
                      style = 'bg-red-950/40 border-red-500/80 text-red-200 font-semibold ring-1 ring-red-500/30';
                    }

                    return (
                      <div
                        key={opt.id}
                        className={`p-2.5 rounded-lg border text-xs flex items-center justify-between gap-2.5 ${style}`}
                      >
                        <div className="flex items-center gap-2.5">
                          <span className="w-5 h-5 rounded flex items-center justify-center font-mono font-bold text-[10px] bg-slate-800 text-slate-300">
                            {letter}
                          </span>
                          <span>{opt.text}</span>
                        </div>

                        {isCorrect && (
                          <span className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
                            <CheckCircle2 size={12} /> Correct
                          </span>
                        )}
                        {isSelected && !isCorrect && (
                          <span className="text-[11px] font-semibold text-red-400 flex items-center gap-1">
                            <XCircle size={12} /> Your Choice
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                {q.explanation && (
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-400 leading-relaxed">
                    <strong className="text-slate-200">Explanation: </strong>
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
