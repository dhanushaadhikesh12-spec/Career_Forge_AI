import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { TestStartResponse } from '@/types';
import { LoadingSpinner, ErrorState, Badge } from '@/components/shared';
import FullscreenBlocker from '@/components/proctoring/FullscreenBlocker';
import { useFullscreen } from '@/hooks/useFullscreen';
import {
  Clock,
  Flag,
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

  const { enterFullscreen, exitBlocked } = useFullscreen({
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

      if (res.expires_at) {
        const remaining = Math.max(0, Math.floor((new Date(res.expires_at).getTime() - Date.now()) / 1000));
        setSecondsRemaining(remaining);
      } else {
        setSecondsRemaining(60 * 30);
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

  // Anti-Malpractice Listeners
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
    if (!session?.attempt_id) return;
    setWarningCount((prev) => prev + 1);
    api.logProctoringEvent(
      session.attempt_id,
      eventType,
      severity,
      description,
      { timestamp: new Date().toISOString() },
    ).catch(console.error);
  };

  const handleSelectOption = (optionId: number) => {
    if (!session || !currentQuestion) return;
    const now = Date.now();
    const elapsed = Math.round((now - questionStartTimeRef.current) / 1000);
    questionStartTimeRef.current = now;

    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: {
        ...prev[currentQuestion.id],
        selectedOptionId: optionId,
        timeSpentSeconds: (prev[currentQuestion.id]?.timeSpentSeconds || 0) + elapsed,
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

  const handleNavigate = (newIdx: number) => {
    if (newIdx < 0 || !session || newIdx >= session.questions.length) return;
    const now = Date.now();
    const elapsed = Math.round((now - questionStartTimeRef.current) / 1000);
    questionStartTimeRef.current = now;

    if (currentQuestion) {
      setAnswers((prev) => ({
        ...prev,
        [currentQuestion.id]: {
          ...prev[currentQuestion.id],
          timeSpentSeconds: (prev[currentQuestion.id]?.timeSpentSeconds || 0) + elapsed,
        },
      }));
    }
    setCurrentIndex(newIdx);
  };

  const handleAutoSubmit = () => {
    submitAll(true);
  };

  const submitAll = async (isAuto = false) => {
    if (!session || submitting) return;
    setSubmitting(true);
    setShowSubmitModal(false);

    try {
      const payloadAnswers = Object.values(answers).map((a) => ({
        question_id: a.questionId,
        selected_option_id: a.selectedOptionId ?? 0,
        time_taken_seconds: a.timeSpentSeconds || 1,
      }));

      const res = await api.submitTest(session.attempt_id, payloadAnswers);
      navigate(`/student/tests/results/${res.id || session.attempt_id}`);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      alert(e?.response?.data?.detail || 'Failed to submit test. Please check connection.');
      setSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[70vh]" />;
  if (error) return <ErrorState message={error} onRetry={() => testId && startTestSession(parseInt(testId))} />;
  if (!session || session.questions.length === 0) {
    return <ErrorState message="No questions available for this test." />;
  }

  const currentQuestion = session.questions[currentIndex];
  const currentAnswer = currentQuestion ? answers[currentQuestion.id] : null;

  const mins = Math.floor((secondsRemaining || 0) / 60);
  const secs = (secondsRemaining || 0) % 60;
  const timeFormatted = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  const isTimeCritical = (secondsRemaining || 0) < 300;

  const totalQuestions = session.questions.length;
  const answeredCount = Object.values(answers).filter((a) => a.selectedOptionId !== null).length;
  const flaggedCount = Object.values(answers).filter((a) => a.isFlagged).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
      {exitBlocked && (
        <FullscreenBlocker
          onReenter={enterFullscreen}
          warningNumber={warningCount}
        />
      )}

      {/* Top Test Header Bar */}
      <header className="sticky top-0 z-40 bg-slate-900 border-b border-slate-800 px-6 py-3 flex items-center justify-between shadow-subtle">
        <div className="flex items-center gap-3">
          <div className="font-bold text-sm text-white font-display">
            CareerForge Examination Platform
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20">
            PROCTORED
          </span>
          {warningCount > 0 && (
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
              <ShieldAlert size={13} />
              <span>{warningCount} Warnings</span>
            </div>
          )}
        </div>

        {/* Timer */}
        <div
          className={`px-3.5 py-1 rounded-md border flex items-center gap-2 font-mono font-bold text-sm tracking-wider ${
            isTimeCritical
              ? 'bg-red-500/15 border-red-500/40 text-red-400 animate-pulse'
              : 'bg-slate-950 border-slate-800 text-slate-200'
          }`}
        >
          <Clock size={15} className={isTimeCritical ? 'text-red-400' : 'text-teal-400'} />
          <span>{timeFormatted}</span>
        </div>

        {/* Submit Action */}
        <button
          onClick={() => setShowSubmitModal(true)}
          className="px-4 py-1.5 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-subtle"
        >
          <Send size={13} />
          Submit Test
        </button>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Question Pane */}
        <div className="lg:col-span-8 flex flex-col justify-between bg-slate-900 border border-slate-800 rounded-xl p-6 sm:p-7 min-h-[560px] shadow-subtle">
          <div>
            <div className="flex items-center justify-between border-b border-slate-800 pb-3.5 mb-5">
              <div className="flex items-center gap-2.5">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Question {currentIndex + 1} of {totalQuestions}
                </span>
                <Badge variant={currentQuestion.difficulty === 'EASY' ? 'success' : currentQuestion.difficulty === 'HARD' ? 'error' : 'warning'}>
                  {currentQuestion.difficulty}
                </Badge>
              </div>

              <button
                onClick={handleToggleFlag}
                className={`px-2.5 py-1 rounded border text-xs font-medium transition-colors flex items-center gap-1.5 ${
                  currentAnswer?.isFlagged
                    ? 'bg-amber-500/15 border-amber-500/40 text-amber-300'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                <Flag size={13} className={currentAnswer?.isFlagged ? 'fill-amber-400 text-amber-400' : ''} />
                {currentAnswer?.isFlagged ? 'Flagged' : 'Flag for Review'}
              </button>
            </div>

            {/* Question Text */}
            <h2 className="text-base sm:text-lg font-semibold text-white leading-relaxed mb-6">
              {currentQuestion.text}
            </h2>

            {/* MCQ Options */}
            <div className="space-y-2.5">
              {currentQuestion.options.map((option, idx) => {
                const isSelected = currentAnswer?.selectedOptionId === option.id;
                const letter = String.fromCharCode(65 + idx);

                return (
                  <button
                    key={option.id}
                    onClick={() => handleSelectOption(option.id)}
                    className={`w-full text-left p-3.5 rounded-lg border transition-colors flex items-center gap-3.5 ${
                      isSelected
                        ? 'bg-navy-800 border-teal-500 text-white font-medium ring-1 ring-teal-500/40'
                        : 'bg-slate-950/70 border-slate-800 text-slate-300 hover:bg-slate-800/80 hover:text-white'
                    }`}
                  >
                    <span
                      className={`w-6 h-6 rounded flex items-center justify-center font-mono font-bold text-xs shrink-0 ${
                        isSelected
                          ? 'bg-teal-600 text-white'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {letter}
                    </span>
                    <span className="text-xs sm:text-sm">{option.text}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Navigation & Clear */}
          <div className="pt-5 border-t border-slate-800 flex items-center justify-between mt-6">
            <button
              onClick={handleClearSelection}
              disabled={currentAnswer?.selectedOptionId === null}
              className="text-xs text-slate-500 hover:text-red-400 transition-colors disabled:opacity-30 flex items-center gap-1"
            >
              <RotateCcw size={13} /> Clear Choice
            </button>

            <div className="flex items-center gap-2.5">
              <button
                onClick={() => handleNavigate(currentIndex - 1)}
                disabled={currentIndex === 0}
                className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition-colors disabled:opacity-30 flex items-center gap-1"
              >
                <ChevronLeft size={15} /> Previous
              </button>

              <button
                onClick={() => handleNavigate(currentIndex + 1)}
                disabled={currentIndex === totalQuestions - 1}
                className="px-4 py-1.5 rounded-lg bg-navy-700 hover:bg-navy-600 text-white text-xs font-semibold transition-colors disabled:opacity-30 flex items-center gap-1 border border-navy-600/60 shadow-subtle"
              >
                Next <ChevronRight size={15} />
              </button>
            </div>
          </div>
        </div>

        {/* Right: Question Palette */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-subtle">
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-300 mb-3">
              Question Navigator
            </h3>

            {/* Legend Stats */}
            <div className="grid grid-cols-3 gap-2 mb-4 text-center">
              <div className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20">
                <div className="text-xs font-bold text-emerald-400">{answeredCount}</div>
                <div className="text-[10px] text-slate-400 uppercase">Answered</div>
              </div>
              <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20">
                <div className="text-xs font-bold text-amber-400">{flaggedCount}</div>
                <div className="text-[10px] text-slate-400 uppercase">Flagged</div>
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800">
                <div className="text-xs font-bold text-slate-400">{totalQuestions - answeredCount}</div>
                <div className="text-[10px] text-slate-500 uppercase">Remaining</div>
              </div>
            </div>

            {/* Grid of question buttons */}
            <div className="grid grid-cols-5 gap-2 max-h-[300px] overflow-y-auto pr-1">
              {session.questions.map((q, idx) => {
                const ans = answers[q.id];
                const isCurrent = idx === currentIndex;
                const isAnswered = ans?.selectedOptionId !== null;
                const isFlagged = ans?.isFlagged;

                let btnStyle = 'bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-800 hover:text-slate-200';
                if (isFlagged) {
                  btnStyle = 'bg-amber-500/20 border-amber-500/50 text-amber-300 font-bold';
                } else if (isAnswered) {
                  btnStyle = 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 font-bold';
                }

                if (isCurrent) {
                  btnStyle += ' ring-2 ring-teal-400 ring-offset-2 ring-offset-slate-900 font-bold text-white';
                }

                return (
                  <button
                    key={q.id}
                    onClick={() => handleNavigate(idx)}
                    className={`h-9 rounded-lg border text-xs font-mono transition-colors flex items-center justify-center relative ${btnStyle}`}
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

          {/* Proctored Rules Note */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-[11px] text-slate-400 space-y-1.5 shadow-subtle">
            <div className="font-semibold text-slate-300 flex items-center gap-1.5 text-xs">
              <ShieldAlert size={13} className="text-teal-400" /> Proctored Test Rules
            </div>
            <p>• Avoid leaving fullscreen or switching browser tabs.</p>
            <p>• Proctor events are recorded in your attempt audit log.</p>
            <p>• Automatic submission triggers when timer reaches 00:00.</p>
          </div>
        </div>
      </main>

      {/* Confirmation Submit Modal */}
      {showSubmitModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-sm w-full space-y-4 shadow-elevated">
            <h3 className="text-base font-bold text-white">Submit Assessment?</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              You have completed <strong className="text-white">{answeredCount}</strong> of{' '}
              <strong className="text-white">{totalQuestions}</strong> questions.
              {totalQuestions - answeredCount > 0 && (
                <span className="text-amber-400 block mt-1 font-medium">
                  {totalQuestions - answeredCount} question(s) remain unanswered!
                </span>
              )}
            </p>

            <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
              <button
                onClick={() => setShowSubmitModal(false)}
                disabled={submitting}
                className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => submitAll(false)}
                disabled={submitting}
                className="px-4 py-1.5 rounded-lg bg-teal-700 hover:bg-teal-600 text-white text-xs font-semibold transition-colors"
              >
                {submitting ? 'Submitting…' : 'Confirm Submit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
