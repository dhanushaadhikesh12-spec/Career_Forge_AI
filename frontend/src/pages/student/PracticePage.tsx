import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { Question, PracticeAnswerResult } from '@/types';
import { PageHeader, LoadingSpinner, ErrorState, Badge } from '@/components/shared';
import {
  Brain,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RotateCcw,
  Sparkles,
  HelpCircle,
  Award,
  ChevronRight,
  ArrowLeft,
} from 'lucide-react';

export default function PracticePage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const topicIdParam = searchParams.get('topic_id');
  const topicId = topicIdParam ? parseInt(topicIdParam) : 1;

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
    startSession();
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
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to start practice session');
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
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      alert(e?.response?.data?.detail || 'Failed to submit answer');
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

  const currentQuestion = questions[currentIndex];

  if (isFinished) {
    const accuracy = scoreCount.total > 0 ? Math.round((scoreCount.correct / scoreCount.total) * 100) : 0;
    return (
      <div className="max-w-2xl mx-auto py-12 animate-fade-in text-center">
        <div className="glass-card p-10 border border-forge-500/30 neon-border space-y-6">
          <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-forge-500 to-purple-600 flex items-center justify-center mx-auto shadow-xl shadow-forge-500/20">
            <Award size={36} className="text-white" />
          </div>

          <h2 className="text-3xl font-bold font-display text-white">Practice Complete!</h2>
          <p className="text-sm text-muted-foreground max-w-md mx-auto">
            You just completed {scoreCount.total} questions. Your IRT skill rating has been updated in real-time.
          </p>

          <div className="grid grid-cols-2 gap-4 max-w-sm mx-auto my-6">
            <div className="glass-card p-4 border border-border/60">
              <div className="text-xs text-muted-foreground uppercase font-semibold">Correct</div>
              <div className="text-2xl font-bold text-emerald-400 mt-1">
                {scoreCount.correct} / {scoreCount.total}
              </div>
            </div>
            <div className="glass-card p-4 border border-border/60">
              <div className="text-xs text-muted-foreground uppercase font-semibold">Accuracy</div>
              <div className="text-2xl font-bold text-forge-400 mt-1">{accuracy}%</div>
            </div>
          </div>

          <div className="flex items-center justify-center gap-4">
            <button
              onClick={startSession}
              className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white font-semibold text-xs transition-colors flex items-center gap-2"
            >
              <RotateCcw size={15} /> Practice Again
            </button>
            <button
              onClick={() => navigate('/student/learn')}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold text-xs glow-button flex items-center gap-2"
            >
              Back to Learn <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/student/learn')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft size={16} /> Exit Practice
        </button>

        <div className="flex items-center gap-3">
          <span className="text-xs font-mono font-medium text-muted-foreground">
            Question {currentIndex + 1} of {questions.length}
          </span>
          <Badge variant={currentQuestion?.difficulty === 'EASY' ? 'success' : currentQuestion?.difficulty === 'HARD' ? 'error' : 'warning'}>
            {currentQuestion?.difficulty || 'MEDIUM'}
          </Badge>
        </div>
      </div>

      {/* Question Card */}
      <div className="glass-card p-8 border border-border/60 space-y-6">
        <div className="space-y-2">
          <span className="text-xs font-bold text-forge-400 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles size={14} /> Multiple Choice Question
          </span>
          <h2 className="text-lg font-semibold text-foreground leading-relaxed">
            {currentQuestion?.text}
          </h2>
        </div>

        {/* Options List */}
        <div className="space-y-3 pt-2">
          {currentQuestion?.options.map((option, idx) => {
            const isSelected = selectedOptionId === option.id;
            const letter = String.fromCharCode(65 + idx);

            let optionStyle = 'bg-white/5 border-border/50 text-muted-foreground hover:bg-white/10 hover:text-foreground';
            if (result) {
              if (option.id === result.correct_option_id) {
                optionStyle = 'bg-emerald-500/20 border-emerald-500 text-emerald-300 font-semibold ring-1 ring-emerald-500';
              } else if (isSelected && !result.is_correct) {
                optionStyle = 'bg-red-500/20 border-red-500 text-red-300 font-semibold ring-1 ring-red-500';
              } else {
                optionStyle = 'bg-white/5 border-border/30 opacity-50';
              }
            } else if (isSelected) {
              optionStyle = 'bg-forge-600/20 border-forge-500 text-white font-semibold ring-1 ring-forge-500';
            }

            return (
              <button
                key={option.id}
                disabled={!!result || submitting}
                onClick={() => setSelectedOptionId(option.id)}
                className={`w-full text-left p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${optionStyle}`}
              >
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-lg bg-white/5 flex items-center justify-center font-mono font-bold text-xs shrink-0">
                    {letter}
                  </span>
                  <span className="text-sm font-medium">{option.text}</span>
                </div>

                {result && option.id === result.correct_option_id && (
                  <CheckCircle2 size={18} className="text-emerald-400 shrink-0" />
                )}
                {result && isSelected && !result.is_correct && (
                  <XCircle size={18} className="text-red-400 shrink-0" />
                )}
              </button>
            );
          })}
        </div>

        {/* Answer Explanation & Adaptive Diagnosis Box */}
        {result && (
          <div className="p-5 rounded-2xl bg-white/5 border border-border/60 space-y-3 animate-fade-in">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm font-bold">
                {result.is_correct ? (
                  <span className="text-emerald-400 flex items-center gap-1.5">
                    <CheckCircle2 size={16} /> Correct! +{result.points_earned} Points
                  </span>
                ) : (
                  <span className="text-red-400 flex items-center gap-1.5">
                    <XCircle size={16} /> Incorrect
                  </span>
                )}
              </div>

              {result.new_skill_rating && (
                <div className="text-xs font-mono font-semibold px-2.5 py-1 rounded-lg bg-forge-500/10 text-forge-300 border border-forge-500/20">
                  Elo: {Math.round(result.new_skill_rating)}{' '}
                  {result.skill_delta !== undefined && (
                    <span className={result.skill_delta >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                      ({result.skill_delta >= 0 ? `+${result.skill_delta}` : result.skill_delta})
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Adaptive diagnostic message banner */}
            {result.adaptive_message && (
              <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-xs font-medium text-purple-200 flex items-center gap-2">
                <Sparkles size={14} className="text-purple-400 shrink-0" />
                <span>{result.adaptive_message}</span>
              </div>
            )}

            {result.explanation && (
              <p className="text-xs text-muted-foreground leading-relaxed pt-1 border-t border-border/30">
                <span className="font-semibold text-foreground">Explanation: </span>
                {result.explanation}
              </p>
            )}
          </div>
        )}

        {/* Footer Actions */}
        <div className="pt-4 border-t border-border/60 flex items-center justify-between">
          <div className="text-xs text-muted-foreground">
            Points: <span className="font-bold text-foreground">{currentQuestion?.points || 1} mark</span>
          </div>

          {!result ? (
            <button
              onClick={handleCheckAnswer}
              disabled={!selectedOptionId || submitting}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold text-xs glow-button transition-all disabled:opacity-50 flex items-center gap-2"
            >
              {submitting ? 'Checking…' : 'Check Answer'}
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-xs glow-button transition-all flex items-center gap-2"
            >
              {currentIndex + 1 < questions.length ? 'Next Question' : 'View Summary'}
              <ArrowRight size={15} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
