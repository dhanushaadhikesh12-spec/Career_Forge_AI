import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { TestStartResponse, Question } from '@/types';
import { LoadingSpinner, ErrorState, Badge } from '@/components/shared';
import FullscreenBlocker from '@/components/proctoring/FullscreenBlocker';
import { useFullscreen } from '@/hooks/useFullscreen';
import {
  Clock,
  Flag,
  CheckCircle2,
  AlertTriangle,
  Send,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  RotateCcw,
} from 'lucide-react';

interface StudentAnswerState {
  questionId: number;
  selectedOptionId: number | null;
  timeSpentSeconds: number;
  isFlagged: boolean;
}

export default function TestSessionPage() {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<TestStartResponse | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, StudentAnswerState>>({});
  const [secondsRemaining, setSecondsRemaining] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [error, setError] = useState('');

  // Proctoring warnings count
  const [warningCount, setWarningCount] = useState(0);
  const questionStartTimeRef = useRef<number>(Date.now());

  // Fullscreen enforcement — runs only once the test session is live
  const handleFullscreenExit = useCallback(() => {
    if (session?.attempt_id) {
      setWarningCount((prev) => prev + 1);
      api.logProctoringEvent(
        session.attempt_id,
        'fullscreen_exit',
        'HIGH',
        'Student exited fullscreen mode during proctored test',
        { timestamp: new Date().toISOString() },
      ).catch(console.error);
    }
  }, [session?.attempt_id]);

  const { isFullscreen, enterFullscreen, exitBlocked } = useFullscreen({
    onExit: handleFullscreenExit,
    enabled: !!session && !submitting,
  });

  useEffect(() => {
    if (testId) {
      startTestSession(parseInt(testId));
    }
  }, [testId]);

  const startTestSession = async (tId: number) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.startTest(tId);
      setSession(res);

      // Initialize answers state map
      const initialAnswers: Record<number, StudentAnswerState> = {};
      res.questions.forEach((q) => {
        initialAnswers[q.id] = {
          questionId: q.id,
          selectedOptionId: null,
          timeSpentSeconds: 0,
          isFlagged: false,
        };
      });
      setAnswers(initialAnswers);

      // Compute remaining time in seconds
      if (res.expires_at) {
        const remaining = Math.max(0, Math.floor((new Date(res.expires_at).getTime() - Date.now()) / 1000));
        setSecondsRemaining(remaining);
      } else {
        setSecondsRemaining(60 * 30); // Default 30 min
      }
      questionStartTimeRef.current = Date.now();
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to start test');
    } finally {
      setLoading(false);
    }
  };

  // Timer Countdown Effect
  useEffect(() => {
    if (secondsRemaining === null || secondsRemaining <= 0 || submitting) return;

    const timer = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev === null) return null;
        if (prev <= 1) {
          clearInterval(timer);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [secondsRemaining, submitting]);

  // Anti-Malpractice Listeners (Tab switch, Blur, Copy, Paste)
  useEffect(() => {
    if (!session?.attempt_id) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        triggerMalpracticeEvent('tab_switch', 'HIGH', 'Student switched browser tab');
      }
    };

    const handleBlur = () => {
      triggerMalpracticeEvent('window_blur', 'MEDIUM', 'Window lost focus');
    };

    const handleCopy = (e: ClipboardEvent) => {
      e.preventDefault();
      triggerMalpracticeEvent('copy_attempt', 'LOW', 'Clipboard copy blocked');
    };

    const handlePaste = (e: ClipboardEvent) => {
      e.preventDefault();
      triggerMalpracticeEvent('paste_attempt', 'LOW', 'Clipboard paste blocked');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleBlur);
    document.addEventListener('copy', handleCopy);
    document.addEventListener('paste', handlePaste);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleBlur);
      document.removeEventListener('copy', handleCopy);
      document.removeEventListener('paste', handlePaste);
    };
  }, [session?.attempt_id]);

  const triggerMalpracticeEvent = (eventType: string, severity: string, description: string) => {
    setWarningCount((prev) => prev + 1);
    if (session?.attempt_id) {
      api.logProctoringEvent(session.attempt_id, eventType, severity, description, {
        question_index: currentIndex,
        timestamp: new Date().toISOString(),
      }).catch(console.error);
    }
  };

  // Record time on question change
  const recordQuestionTime = () => {
    if (!currentQuestion) return;
    const elapsed = Math.max(1, Math.round((Date.now() - questionStartTimeRef.current) / 1000));
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: {
        ...prev[currentQuestion.id],
        timeSpentSeconds: (prev[currentQuestion.id]?.timeSpentSeconds || 0) + elapsed,
      },
    }));
    questionStartTimeRef.current = Date.now();
  };

  const handleSelectOption = (optionId: number) => {
    if (!currentQuestion) return;
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: {
        ...prev[currentQuestion.id],
        selectedOptionId: optionId,
      },
    }));
  };

  const handleClearSelection = () => {
    if (!currentQuestion) return;
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: {
        ...prev[currentQuestion.id],
        selectedOptionId: null,
      },
    }));
  };

  const handleToggleFlag = () => {
    if (!currentQuestion) return;
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: {
        ...prev[currentQuestion.id],
        isFlagged: !prev[currentQuestion.id]?.isFlagged,
      },
    }));
  };

  const handleNavigate = (newIndex: number) => {
    recordQuestionTime();
    setCurrentIndex(newIndex);
  };

  const handleAutoSubmit = () => {
    submitAll(true);
  };

  const submitAll = async (isTimeout = false) => {
    if (!session || submitting) return;
    setSubmitting(true);
    recordQuestionTime();

    try {
      const payloadAnswers = Object.values(answers)
        .filter((a) => a.selectedOptionId !== null)
        .map((a) => ({
          question_id: a.questionId,
          selected_option_id: a.selectedOptionId as number,
          time_taken_seconds: a.timeSpentSeconds,
        }));

      const res = await api.submitTest(session.attempt_id, payloadAnswers);
      navigate(`/student/tests/results/${res.id}`);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      alert(e?.response?.data?.detail || 'Error submitting test');
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[80vh]" />;
  if (error) return <ErrorState message={error} onRetry={() => testId && startTestSession(parseInt(testId))} />;
  if (!session || session.questions.length === 0) {
    return <ErrorState message="No questions available for this test." />;
  }

  const currentQuestion = session.questions[currentIndex];
  const currentAnswer = currentQuestion ? answers[currentQuestion.id] : null;

  // Format Time
  const mins = Math.floor((secondsRemaining || 0) / 60);
  const secs = (secondsRemaining || 0) % 60;
  const timeFormatted = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  const isTimeCritical = (secondsRemaining || 0) < 300; // < 5 mins

  // Question counts
  const totalQuestions = session.questions.length;
  const answeredCount = Object.values(answers).filter((a) => a.selectedOptionId !== null).length;
  const flaggedCount = Object.values(answers).filter((a) => a.isFlagged).length;

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Fullscreen blocking overlay — shown if student exits fullscreen */}
      {exitBlocked && (
        <FullscreenBlocker
          onReenter={enterFullscreen}
          warningNumber={warningCount}
        />
      )}
      {/* Top Test Header Bar */}
      <header className="sticky top-0 z-40 bg-card/90 backdrop-blur-md border-b border-border/60 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-base font-display gradient-text">CareerForge Test</span>
            <Badge variant="purple">LIVE</Badge>
          </div>
          {warningCount > 0 && (
            <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs font-semibold animate-pulse">
              <ShieldAlert size={14} />
              <span>{warningCount} Proctor Warnings</span>
            </div>
          )}
        </div>

        {/* Timer */}
        <div
          className={`px-4 py-1.5 rounded-xl border flex items-center gap-2 font-mono font-bold text-sm tracking-wider shadow-sm transition-all ${
            isTimeCritical
              ? 'bg-red-500/20 border-red-500/40 text-red-400 animate-pulse'
              : 'bg-white/5 border-border text-foreground'
          }`}
        >
          <Clock size={16} className={isTimeCritical ? 'text-red-400' : 'text-forge-400'} />
          <span>{timeFormatted}</span>
        </div>

        {/* Action: Finish test */}
        <button
          onClick={() => setShowSubmitModal(true)}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold text-xs glow-button flex items-center gap-1.5 shadow-md"
        >
          <Send size={14} />
          Submit Test
        </button>
      </header>

      {/* Main Container: Question Area & Navigation Palette */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Current Question Pane */}
        <div className="lg:col-span-8 flex flex-col justify-between glass-card p-8 border border-border/60 min-h-[580px]">
          <div>
            {/* Question meta header */}
            <div className="flex items-center justify-between border-b border-border/50 pb-4 mb-6">
              <div className="flex items-center gap-3">
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Question {currentIndex + 1} of {totalQuestions}
                </span>
                <Badge variant={currentQuestion.difficulty === 'EASY' ? 'success' : currentQuestion.difficulty === 'HARD' ? 'error' : 'warning'}>
                  {currentQuestion.difficulty}
                </Badge>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleToggleFlag}
                  className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-all flex items-center gap-1.5 ${
                    currentAnswer?.isFlagged
                      ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                      : 'bg-white/5 border-border text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <Flag size={14} className={currentAnswer?.isFlagged ? 'fill-amber-400 text-amber-400' : ''} />
                  {currentAnswer?.isFlagged ? 'Flagged' : 'Flag for Review'}
                </button>
              </div>
            </div>

            {/* Question Text */}
            <h2 className="text-lg font-semibold text-foreground leading-relaxed mb-8">
              {currentQuestion.text}
            </h2>

            {/* MCQ Options */}
            <div className="space-y-3.5">
              {currentQuestion.options.map((option, idx) => {
                const isSelected = currentAnswer?.selectedOptionId === option.id;
                const letter = String.fromCharCode(65 + idx);

                return (
                  <button
                    key={option.id}
                    onClick={() => handleSelectOption(option.id)}
                    className={`w-full text-left p-4 rounded-xl border transition-all flex items-center gap-4 ${
                      isSelected
                        ? 'bg-forge-600/20 border-forge-500 text-white font-semibold ring-1 ring-forge-500/50'
                        : 'bg-white/5 border-border/50 text-muted-foreground hover:bg-white/10 hover:text-foreground'
                    }`}
                  >
                    <span
                      className={`w-7 h-7 rounded-lg flex items-center justify-center font-mono font-bold text-xs shrink-0 transition-colors ${
                        isSelected
                          ? 'bg-forge-500 text-white'
                          : 'bg-white/10 text-muted-foreground'
                      }`}
                    >
                      {letter}
                    </span>
                    <span className="text-sm">{option.text}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Bottom Bar: Clear Answer + Prev / Next */}
          <div className="pt-6 border-t border-border/50 flex items-center justify-between mt-8">
            <button
              onClick={handleClearSelection}
              disabled={currentAnswer?.selectedOptionId === null}
              className="text-xs text-muted-foreground hover:text-red-400 transition-colors disabled:opacity-30 flex items-center gap-1.5"
            >
              <RotateCcw size={14} /> Clear Selection
            </button>

            <div className="flex items-center gap-3">
              <button
                onClick={() => handleNavigate(currentIndex - 1)}
                disabled={currentIndex === 0}
                className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-border text-xs font-semibold text-foreground transition-all disabled:opacity-30 flex items-center gap-1.5"
              >
                <ChevronLeft size={16} /> Previous
              </button>

              <button
                onClick={() => handleNavigate(currentIndex + 1)}
                disabled={currentIndex === totalQuestions - 1}
                className="px-5 py-2 rounded-xl bg-forge-600 hover:bg-forge-500 text-white text-xs font-semibold glow-button transition-all disabled:opacity-30 flex items-center gap-1.5"
              >
                Next <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>

        {/* Right: Question Palette & Test Summary */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass-card p-6 border border-border/60">
            <h3 className="font-bold text-sm text-foreground mb-4">Question Navigation Palette</h3>

            {/* Legend */}
            <div className="grid grid-cols-3 gap-2 mb-6 text-center">
              <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                <div className="text-xs font-bold text-emerald-400">{answeredCount}</div>
                <div className="text-[10px] text-muted-foreground uppercase">Answered</div>
              </div>
              <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
                <div className="text-xs font-bold text-amber-400">{flaggedCount}</div>
                <div className="text-[10px] text-muted-foreground uppercase">Flagged</div>
              </div>
              <div className="p-2 rounded-lg bg-white/5 border border-border/40">
                <div className="text-xs font-bold text-muted-foreground">{totalQuestions - answeredCount}</div>
                <div className="text-[10px] text-muted-foreground uppercase">Remaining</div>
              </div>
            </div>

            {/* Palette Buttons Grid */}
            <div className="grid grid-cols-5 gap-2.5 max-h-[300px] overflow-y-auto pr-1">
              {session.questions.map((q, idx) => {
                const ans = answers[q.id];
                const isCurrent = idx === currentIndex;
                const isAnswered = ans?.selectedOptionId !== null;
                const isFlagged = ans?.isFlagged;

                let btnStyle = 'bg-white/5 border-border/50 text-muted-foreground hover:bg-white/10';
                if (isFlagged) {
                  btnStyle = 'bg-amber-500/20 border-amber-500 text-amber-300 font-bold';
                } else if (isAnswered) {
                  btnStyle = 'bg-emerald-500/20 border-emerald-500 text-emerald-300 font-bold';
                }

                if (isCurrent) {
                  btnStyle += ' ring-2 ring-forge-400 ring-offset-2 ring-offset-background';
                }

                return (
                  <button
                    key={q.id}
                    onClick={() => handleNavigate(idx)}
                    className={`h-10 rounded-xl border text-xs font-mono transition-all flex items-center justify-center relative ${btnStyle}`}
                  >
                    {idx + 1}
                    {isFlagged && (
                      <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-amber-400" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Test Guidelines Reminder */}
          <div className="glass-card p-5 border border-border/60 text-xs text-muted-foreground space-y-2">
            <div className="font-semibold text-foreground flex items-center gap-1.5 text-xs">
              <ShieldAlert size={14} className="text-forge-400" /> Proctored Test Rules
            </div>
            <p>• Avoid switching tabs or opening external applications.</p>
            <p>• All tab blurs are automatically logged to the trainer audit trail.</p>
            <p>• Answers are auto-submitted when the countdown expires.</p>
          </div>
        </div>
      </main>

      {/* Confirmation Submit Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card p-6 border border-forge-500/30 max-w-md w-full space-y-5 animate-scale-in">
            <h3 className="text-lg font-bold text-foreground">Submit Assessment?</h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              You have answered <span className="font-bold text-foreground">{answeredCount}</span> of{' '}
              <span className="font-bold text-foreground">{totalQuestions}</span> questions.
              {totalQuestions - answeredCount > 0 && (
                <span className="text-amber-400 font-semibold block mt-1">
                  Warning: You have {totalQuestions - answeredCount} unanswered questions!
                </span>
              )}
            </p>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-border/50">
              <button
                onClick={() => setShowSubmitModal(false)}
                disabled={submitting}
                className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-border text-xs font-semibold text-foreground transition-colors"
              >
                Continue Test
              </button>
              <button
                onClick={() => submitAll(false)}
                disabled={submitting}
                className="px-5 py-2 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white text-xs font-semibold glow-button transition-all"
              >
                {submitting ? 'Submitting…' : 'Confirm Submission'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
