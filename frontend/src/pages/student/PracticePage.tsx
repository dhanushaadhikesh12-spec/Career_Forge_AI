import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { Question, PracticeAnswerResult } from '@/types';
import { LoadingSpinner, ErrorState, Badge } from '@/components/shared';
import {
  Brain,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RotateCcw,
  Sparkles,
  Award,
  ArrowLeft,
} from 'lucide-react';

const parseErrorMessage = (err: unknown): string => {
  const e = err as { response?: { data?: { detail?: unknown } }; message?: string };
  const detail = e?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
  }
  if (e?.message) return e.message;
  return 'Failed to start practice session. Please try again.';
};

export default function PracticePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const topicIdParam = searchParams.get('topic_id');
  const topicId = topicIdParam && !isNaN(parseInt(topicIdParam)) ? parseInt(topicIdParam) : undefined;

  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOptionId, setSelectedOptionId] = useState<number | null>(null);
  const [result, setResult] = useState<PracticeAnswerResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [scoreCount, setScoreCount] = useState({ correct: 0, total: 0 });
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [isFinished, setIsFinished] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      setLoading(true);
      setError('');
      setIsFinished(false);
      setCurrentIndex(0);
      setSelectedOptionId(null);
      setResult(null);
      setScoreCount({ correct: 0, total: 0 });
      try {
        const data = await api.startPracticeSession(topicId, undefined, 5);
        if (!cancelled) {
          setQuestions(data);
          setStartTime(Date.now());
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(parseErrorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    run();

    return () => {
      cancelled = true;
    };
  }, [topicId]);

  const startSession = async () => {
    setLoading(true);
    setError('');
    setIsFinished(false);
    setCurrentIndex(0);
    setSelectedOptionId(null);
    setResult(null);
    setScoreCount({ correct: 0, total: 0 });
    try {
      const data = await api.startPracticeSession(topicId, undefined, 5);
      setQuestions(data);
      setStartTime(Date.now());
    } catch (err: unknown) {
      setError(parseErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCheckAnswer = async () => {
    if (!selectedOptionId || !currentQuestion) return;
    setSubmitting(true);
    try {
      const timeTaken = Math.max(1, Math.round((Date.now() - startTime) / 1000));
      const res = await api.submitPracticeAnswer(currentQuestion.id, selectedOptionId, timeTaken);
      setResult(res);
      setScoreCount((prev) => ({
        correct: prev.correct + (res.is_correct ? 1 : 0),
        total: prev.total + 1,
      }));
    } catch (err: unknown) {
      const msg = parseErrorMessage(err);
      alert(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (currentIndex + 1 < questions.length) {
      setCurrentIndex((prev) => prev + 1);
      setSelectedOptionId(null);
      setResult(null);
      setStartTime(Date.now());
    } else {
      setIsFinished(true);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[60vh]" />;
  if (error) return <ErrorState message={error} onRetry={startSession} />;

  if (questions.length === 0 && !isFinished) {
    return (
      <div className="max-w-md mx-auto py-12 text-center space-y-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-subtle space-y-4">
          <Brain size={36} className="text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-white">No Practice Questions Available</h3>
          <p className="text-xs text-slate-400">
            {topicId ? 'No questions found for this topic.' : 'Explore topics in the Learning Hub to start practicing.'}
          </p>
          <div className="flex items-center justify-center gap-2 pt-2">
            <button
              onClick={() => navigate('/student/learn')}
              className="px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors"
            >
              Browse Curriculum
            </button>
            <button
              onClick={() => navigate('/student/dashboard')}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition-colors"
            >
              Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const progressPct = questions.length > 0 ? Math.round(((currentIndex + 1) / questions.length) * 100) : 0;

  if (isFinished) {
    const accuracy = scoreCount.total > 0 ? Math.round((scoreCount.correct / scoreCount.total) * 100) : 0;
    return (
      <div className="max-w-xl mx-auto py-10">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center space-y-6 shadow-subtle">
          <div className="w-14 h-14 rounded-xl bg-navy-800 border border-teal-500/40 flex items-center justify-center mx-auto text-teal-400">
            <Award size={30} />
          </div>

          <div>
            <h2 className="text-xl font-bold text-white font-display">Practice Session Completed</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              You answered {scoreCount.total} questions. Your Elo skill rating and topic accuracy have been recorded.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 max-w-xs mx-auto">
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Correct</div>
              <div className="text-xl font-bold text-emerald-400 mt-0.5">
                {scoreCount.correct} / {scoreCount.total}
              </div>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Accuracy</div>
              <div className="text-xl font-bold text-teal-400 mt-0.5">{accuracy}%</div>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-2.5 pt-2">
            <button
              onClick={startSession}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium text-xs transition-colors flex items-center gap-1.5"
            >
              <RotateCcw size={14} /> Practice Again
            </button>
            <button
              onClick={() => navigate('/student/dashboard')}
              className="px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-subtle"
            >
              Back to Dashboard <ArrowRight size={14} />
            </button>
            <button
              onClick={() => navigate('/student/learn')}
              className="px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 text-xs font-medium transition-colors"
            >
              Learning Hub
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-5">
      {/* Top Session Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <button
          onClick={() => navigate('/student/dashboard')}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft size={15} /> Exit Practice
        </button>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-medium text-slate-400">
            Question {currentIndex + 1} of {questions.length}
          </span>
          <Badge variant={currentQuestion?.difficulty === 'EASY' ? 'success' : currentQuestion?.difficulty === 'HARD' ? 'error' : 'warning'}>
            {currentQuestion?.difficulty || 'MEDIUM'}
          </Badge>
        </div>
      </div>

      {/* Progress Line */}
      <div className="w-full bg-slate-800 rounded-full h-1 overflow-hidden">
        <div
          className="bg-teal-500 h-full rounded-full transition-all duration-300"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* Question Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 sm:p-7 space-y-6 shadow-subtle">
        <div className="space-y-1.5">
          <div className="text-[10px] font-bold text-teal-400 uppercase tracking-wider">
            {topicId ? 'Topic Practice Question' : 'Adaptive Placement Question'}
          </div>
          <h2 className="text-base sm:text-lg font-semibold text-white leading-relaxed">
            {currentQuestion?.text}
          </h2>
        </div>

        {/* Options List */}
        <div className="space-y-2.5">
          {currentQuestion?.options.map((option, idx) => {
            const isSelected = selectedOptionId === option.id;
            const letter = String.fromCharCode(65 + idx);

            let optionStyle = 'bg-slate-950/70 border-slate-800 text-slate-300 hover:bg-slate-800/80 hover:text-white hover:border-slate-700';
            if (result) {
              if (option.id === result.correct_option_id) {
                optionStyle = 'bg-emerald-950/40 border-emerald-500/80 text-emerald-200 font-semibold ring-1 ring-emerald-500/40';
              } else if (isSelected && !result.is_correct) {
                optionStyle = 'bg-red-950/40 border-red-500/80 text-red-200 font-semibold ring-1 ring-red-500/40';
              } else {
                optionStyle = 'bg-slate-950/40 border-slate-900 text-slate-600 opacity-60';
              }
            } else if (isSelected) {
              optionStyle = 'bg-navy-800/90 border-teal-500/80 text-white font-medium ring-1 ring-teal-500/40';
            }

            return (
              <button
                key={option.id}
                disabled={!!result || submitting}
                onClick={() => setSelectedOptionId(option.id)}
                className={`w-full text-left p-3.5 rounded-lg border text-xs sm:text-sm transition-colors flex items-center justify-between gap-3 ${optionStyle}`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="w-6 h-6 rounded flex items-center justify-center font-mono font-bold text-xs shrink-0 bg-slate-800 text-slate-400 border border-slate-700">
                    {letter}
                  </span>
                  <span className="leading-snug">{option.text}</span>
                </div>

                {result && option.id === result.correct_option_id && (
                  <CheckCircle2 size={17} className="text-emerald-400 shrink-0" />
                )}
                {result && isSelected && !result.is_correct && (
                  <XCircle size={17} className="text-red-400 shrink-0" />
                )}
              </button>
            );
          })}
        </div>

        {/* Answer Feedback & Diagnostics */}
        {result && (
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="text-xs font-bold">
                {result.is_correct ? (
                  <span className="text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 size={15} /> Correct! +{result.points_earned} Points
                  </span>
                ) : (
                  <span className="text-red-400 flex items-center gap-1.5">
                    <XCircle size={15} /> Incorrect
                  </span>
                )}
              </div>

              {result.new_skill_rating && (
                <div className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
                  Elo: {Math.round(result.new_skill_rating)}{' '}
                  {result.skill_delta !== undefined && (
                    <span className={result.skill_delta >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                      ({result.skill_delta >= 0 ? `+${result.skill_delta}` : result.skill_delta})
                    </span>
                  )}
                </div>
              )}
            </div>

            {result.adaptive_message && (
              <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs text-slate-300 flex items-center gap-2">
                <Sparkles size={13} className="text-teal-400 shrink-0" />
                <span>{result.adaptive_message}</span>
              </div>
            )}

            {result.explanation && (
              <p className="text-xs text-slate-400 leading-relaxed pt-1 border-t border-slate-800/80">
                <strong className="text-slate-300">Explanation: </strong>
                {result.explanation}
              </p>
            )}
          </div>
        )}

        {/* Action Button */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            Points: <span className="font-semibold text-slate-300">{currentQuestion?.points || 1} mark</span>
          </div>

          {!result ? (
            <button
              onClick={handleCheckAnswer}
              disabled={!selectedOptionId || submitting}
              className="px-5 py-2 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors disabled:opacity-50 shadow-subtle"
            >
              {submitting ? 'Evaluating…' : 'Check Answer'}
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="px-5 py-2 rounded-lg bg-navy-700 hover:bg-navy-600 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-subtle"
            >
              {currentIndex + 1 < questions.length ? 'Next Question' : 'View Summary'}
              <ArrowRight size={14} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
