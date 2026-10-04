import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import {
  Clock, ShieldAlert, AlertTriangle, Send, Play, CheckCircle2,
  XCircle, ChevronRight, ChevronLeft, FileCode, Check,
  Code2, Sparkles, Shield, ArrowRight, CheckSquare, Layers, RotateCcw
} from 'lucide-react';
import { api } from '@/services/api';
import type { CodingAssessmentDetail, CodeRunResponse, CodeSubmission } from '@/types';
import { Badge, LoadingSpinner, useToast } from '@/components/shared';
import FullscreenBlocker from '@/components/proctoring/FullscreenBlocker';
import { useFullscreen } from '@/hooks/useFullscreen';

interface LanguageOption {
  id: string;
  name: string;
  version: string;
  badge: string;
  starterSnippet: (title: string) => string;
}

const SUPPORTED_LANGUAGES: LanguageOption[] = [
  {
    id: 'python',
    name: 'Python 3',
    version: 'v3.10+',
    badge: 'Popular for DSA & Fast Prototyping',
    starterSnippet: (_title) =>
      `import sys\n\ndef solve():\n    # Read input from standard input\n    input_data = sys.stdin.read().split()\n    if not input_data:\n        return\n    \n    # Write your solution logic here\n    pass\n\nif __name__ == '__main__':\n    solve()\n`,
  },
  {
    id: 'java',
    name: 'Java 17',
    version: 'OpenJDK 17',
    badge: 'Strong Typings & Strict Object-Oriented',
    starterSnippet: (_title) =>
      `import java.util.*;\nimport java.io.*;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner scanner = new Scanner(System.in);\n        // Write your solution logic here\n        \n    }\n}\n`,
  },
  {
    id: 'cpp',
    name: 'C++ 17',
    version: 'GCC 17',
    badge: 'Ultra High Performance & STL Algorithms',
    starterSnippet: (_title) =>
      `#include <iostream>\n#include <vector>\n#include <string>\n#include <algorithm>\n#include <unordered_map>\nusing namespace std;\n\nint main() {\n    ios_base::sync_with_stdio(false);\n    cin.tie(NULL);\n    // Write your solution logic here\n    \n    return 0;\n}\n`,
  },
  {
    id: 'javascript',
    name: 'JavaScript',
    version: 'Node.js v18+',
    badge: 'Modern ES6+ Runtime Environment',
    starterSnippet: (_title) =>
      `const fs = require('fs');\n\nfunction solve() {\n    const input = fs.readFileSync(0, 'utf-8').trim();\n    if (!input) return;\n    // Write your solution logic here\n    \n}\n\nsolve();\n`,
  },
];

export default function CodingAssessmentPage() {
  const { testId } = useParams<{ testId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();

  const [assessment, setAssessment] = useState<CodingAssessmentDetail | null>(null);
  const [activeQuestionIndex, setActiveQuestionIndex] = useState(0);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('python');
  const [codeMap, setCodeMap] = useState<Record<number, string>>({});
  const [remainingSeconds, setRemainingSeconds] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);

  // Pre-test flow state
  const [hasStarted, setHasStarted] = useState(false);
  const [agreedToRules, setAgreedToRules] = useState(true);

  // Execution states
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmittingProblem, setIsSubmittingProblem] = useState(false);
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [runResult, setRunResult] = useState<CodeRunResponse | null>(null);
  const [activeSubmission, setActiveSubmission] = useState<CodeSubmission | null>(null);

  // Proctoring telemetry states
  const [violationCount, setViolationCount] = useState<number>(0);
  const [lastViolationMsg, setLastViolationMsg] = useState<string | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Fullscreen enforcement: enabled ONLY when assessment is active and NOT finalizing
  const handleFullscreenExitHook = useCallback(() => {
    if (assessment?.attempt_id && hasStarted && !isFinalizing) {
      logViolation(assessment.attempt_id, 'fullscreen_exit', 'HIGH', 'Student exited fullscreen mode during coding assessment');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [assessment?.attempt_id, hasStarted, isFinalizing]);

  const { enterFullscreen, exitBlocked } = useFullscreen({
    onExit: handleFullscreenExitHook,
    enabled: hasStarted && !!assessment && !isFinalizing,
  });

  useEffect(() => {
    if (testId) {
      checkExistingSession(parseInt(testId));
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [testId]);

  // Anti-Malpractice Proctoring Event Listeners
  useEffect(() => {
    if (!assessment || !hasStarted) return;
    const attemptId = assessment.attempt_id;

    function handleVisibilityChange() {
      if (document.hidden) {
        logViolation(attemptId, 'tab_switch', 'HIGH', 'Student switched browser tabs during assessment');
      }
    }

    function handleWindowBlur() {
      logViolation(attemptId, 'window_blur', 'MEDIUM', 'Assessment window lost focus');
    }

    function handleCopy(e: ClipboardEvent) {
      logViolation(attemptId, 'clipboard_copy', 'MEDIUM', 'Clipboard copy attempt detected');
    }

    function handlePaste(e: ClipboardEvent) {
      logViolation(attemptId, 'clipboard_paste', 'MEDIUM', 'Clipboard paste attempt detected');
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleWindowBlur);
    document.addEventListener('copy', handleCopy);
    document.addEventListener('paste', handlePaste);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleWindowBlur);
      document.removeEventListener('copy', handleCopy);
      document.removeEventListener('paste', handlePaste);
    };
  }, [assessment, hasStarted]);

  async function logViolation(attemptId: number, eventType: string, severity: 'LOW' | 'MEDIUM' | 'HIGH', desc: string) {
    setViolationCount((prev) => prev + 1);
    setLastViolationMsg(`Warning: ${desc}`);
    toast('error', `Proctoring Alert: ${desc}`);

    try {
      await api.logProctoringEvent(attemptId, eventType, severity, desc);
    } catch (err) {
      console.error('Failed to log proctoring event:', err);
    }
  }

  /**
   * Check if the student already has an active ongoing attempt.
   * If yes, resume immediately without setup screen.
   */
  async function checkExistingSession(id: number) {
    setIsLoading(true);
    try {
      const sync = await api.getCodingAssessmentTime(id);
      if (sync && !sync.is_expired && sync.remaining_seconds > 0) {
        // Active attempt found: resume directly
        await startAssessmentSession(id, selectedLanguage);
      } else {
        // No active attempt: show pre-test setup and language options
        setIsLoading(false);
      }
    } catch {
      // If error or 404, show setup screen
      setIsLoading(false);
    }
  }

  async function handleBeginAssessment() {
    if (!agreedToRules) {
      toast('info', 'Please accept the proctoring rules before beginning.');
      return;
    }
    if (!testId) return;
    await startAssessmentSession(parseInt(testId), selectedLanguage);
  }

  async function startAssessmentSession(id: number, initialLang: string) {
    setIsLoading(true);
    try {
      const data = await api.startCodingAssessment(id);
      setAssessment(data);
      setRemainingSeconds(data.remaining_seconds);
      setSelectedLanguage(initialLang);

      // Initialize code templates for all questions using the selected language
      const langConfig = SUPPORTED_LANGUAGES.find((l) => l.id === initialLang) || SUPPORTED_LANGUAGES[0];
      const initialMap: Record<number, string> = {};
      data.questions.forEach((q) => {
        initialMap[q.id] = q.user_submission?.source_code || langConfig.starterSnippet(q.title);
      });
      setCodeMap(initialMap);

      setHasStarted(true);
      startTimer(id);

      // Trigger fullscreen safely
      setTimeout(() => {
        enterFullscreen().catch(() => {});
      }, 200);
    } catch (err: any) {
      toast('error', err.response?.data?.detail || 'Failed to start assessment');
      navigate('/student/tests');
    } finally {
      setIsLoading(false);
    }
  }

  function startTimer(assessmentId: number) {
    if (timerRef.current) clearInterval(timerRef.current);

    timerRef.current = setInterval(async () => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }

  async function handleAutoSubmit() {
    toast('info', 'Assessment time expired! Automatically submitting solutions...');
    if (assessment) {
      await finalizeAssessment();
    }
  }

  async function handleRunCode() {
    if (!assessment) return;
    const currentQ = assessment.questions[activeQuestionIndex];
    if (!currentQ) return;

    setIsRunning(true);
    setRunResult(null);
    try {
      const currentCode = codeMap[currentQ.id] || '';
      const result = await api.runCode(currentQ.id, currentCode, selectedLanguage);
      setRunResult(result);
      if (result.verdict === 'ACCEPTED') {
        toast('success', 'Sample test cases passed!');
      } else {
        toast('info', `Result: ${result.verdict}`);
      }
    } catch (err: any) {
      toast('error', err.response?.data?.detail || 'Code execution failed');
    } finally {
      setIsRunning(false);
    }
  }

  /**
   * CRITICAL FIX:
   * Uses isSubmittingProblem instead of toggling fullscreen state.
   * Fullscreen stays 100% active and stable throughout problem submissions!
   */
  async function handleSubmitCurrentProblem() {
    if (!assessment) return;
    const currentQ = assessment.questions[activeQuestionIndex];
    if (!currentQ) return;

    setIsSubmittingProblem(true);
    try {
      const currentCode = codeMap[currentQ.id] || '';
      const sub = await api.submitCode(currentQ.id, currentCode, selectedLanguage, assessment.attempt_id);
      setActiveSubmission(sub);

      // Update question in assessment state with user submission to reflect score immediately
      setAssessment((prev) => {
        if (!prev) return prev;
        const updatedQuestions = [...prev.questions];
        updatedQuestions[activeQuestionIndex] = {
          ...updatedQuestions[activeQuestionIndex],
          user_submission: sub,
        };
        return { ...prev, questions: updatedQuestions };
      });

      toast(
        sub.verdict === 'ACCEPTED' ? 'success' : 'info',
        `Submitted ${currentQ.title}: ${sub.verdict} (${sub.score} marks)`
      );
    } catch (err: any) {
      toast('error', err.response?.data?.detail || 'Submission failed');
    } finally {
      setIsSubmittingProblem(false);
    }
  }

  async function finalizeAssessment() {
    if (!assessment) return;
    setIsFinalizing(true);
    try {
      await api.finalizeCodingAssessment(assessment.test_id);
      toast('success', 'Assessment finalized and submitted successfully!');
      navigate(`/student/tests/results/${assessment.attempt_id}`);
    } catch (err: any) {
      toast('error', err.response?.data?.detail || 'Failed to finalize assessment');
      setIsFinalizing(false);
    }
  }

  function handleLanguageSwitch(newLang: string) {
    setSelectedLanguage(newLang);
    if (!currentQuestion) return;
    const existingCode = codeMap[currentQuestion.id] || '';
    const currentSnippet = SUPPORTED_LANGUAGES.find((l) => l.id === selectedLanguage)?.starterSnippet(currentQuestion.title) || '';

    // If existing code is unmodified starter code, replace it with new language starter code
    if (!existingCode || existingCode === currentSnippet) {
      const newConfig = SUPPORTED_LANGUAGES.find((l) => l.id === newLang);
      if (newConfig) {
        setCodeMap((prev) => ({
          ...prev,
          [currentQuestion.id]: newConfig.starterSnippet(currentQuestion.title),
        }));
      }
    }
  }

  function handleResetCode() {
    if (!currentQuestion) return;
    const config = SUPPORTED_LANGUAGES.find((l) => l.id === selectedLanguage) || SUPPORTED_LANGUAGES[0];
    setCodeMap((prev) => ({
      ...prev,
      [currentQuestion.id]: config.starterSnippet(currentQuestion.title),
    }));
    toast('info', 'Code reset to clean starter template.');
  }

  function formatTime(secs: number): string {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center space-y-4">
        <LoadingSpinner size="lg" />
        <p className="text-xs text-muted-foreground animate-pulse">Initializing Placement Coding Assessment...</p>
      </div>
    );
  }

  // ────────────────────────────── PRE-TEST LANGUAGE & SETUP SCREEN ──────────────────────────────
  if (!hasStarted) {
    const activeLangConfig = SUPPORTED_LANGUAGES.find((l) => l.id === selectedLanguage) || SUPPORTED_LANGUAGES[0];

    return (
      <div className="min-h-screen bg-gradient-to-b from-background via-black to-background text-foreground flex flex-col items-center justify-center p-6 animate-fade-in">
        <div className="max-w-4xl w-full glass-card p-8 md:p-10 rounded-3xl border border-forge-500/30 neon-border shadow-2xl space-y-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/40 pb-6">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-forge-400 uppercase tracking-wider">
                <Sparkles size={14} /> Placement Coding Assessment 1
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-white font-display">
                Assessment Setup & Language Selection
              </h1>
              <p className="text-xs text-muted-foreground">
                Select your preferred programming language. You will solve 20 algorithmic challenges under timed proctoring.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="px-4 py-2 rounded-2xl bg-white/5 border border-border/60 text-center">
                <div className="text-[10px] uppercase font-bold text-muted-foreground">Questions</div>
                <div className="text-lg font-extrabold text-forge-400">20 Problems</div>
              </div>
              <div className="px-4 py-2 rounded-2xl bg-white/5 border border-border/60 text-center">
                <div className="text-[10px] uppercase font-bold text-muted-foreground">Time Limit</div>
                <div className="text-lg font-extrabold text-amber-400">90 Mins</div>
              </div>
              <div className="px-4 py-2 rounded-2xl bg-white/5 border border-border/60 text-center">
                <div className="text-[10px] uppercase font-bold text-muted-foreground">Total Marks</div>
                <div className="text-lg font-extrabold text-emerald-400">100 Marks</div>
              </div>
            </div>
          </div>

          {/* Section 1: Language Options */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Code2 size={16} className="text-forge-400" />
                Select Preferred Programming Language
              </h2>
              <span className="text-[11px] text-muted-foreground">You can also switch per-problem in the editor</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {SUPPORTED_LANGUAGES.map((lang) => {
                const isSelected = selectedLanguage === lang.id;
                return (
                  <button
                    key={lang.id}
                    type="button"
                    onClick={() => setSelectedLanguage(lang.id)}
                    className={`p-4 rounded-2xl border text-left transition-all relative flex flex-col justify-between ${
                      isSelected
                        ? 'bg-forge-500/15 border-forge-500 shadow-lg shadow-forge-500/20 ring-1 ring-forge-500'
                        : 'bg-white/5 hover:bg-white/10 border-border/60 hover:border-border'
                    }`}
                  >
                    {isSelected && (
                      <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-forge-500 text-white flex items-center justify-center">
                        <Check size={12} strokeWidth={3} />
                      </div>
                    )}
                    <div>
                      <div className="text-base font-bold text-white">{lang.name}</div>
                      <div className="text-[11px] text-muted-foreground mt-0.5">{lang.version}</div>
                    </div>
                    <div className="mt-4 pt-3 border-t border-border/40 text-[10px] text-forge-300 font-medium">
                      {lang.badge}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Template preview */}
            <div className="p-4 rounded-2xl bg-black/50 border border-border/50 space-y-2">
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span className="font-semibold text-slate-300">Default Starter Code Preview ({activeLangConfig.name}):</span>
                <span>Judge0 Execution Engine</span>
              </div>
              <pre className="font-mono text-xs text-forge-200/90 overflow-x-auto max-h-32 p-3 bg-black/60 rounded-xl border border-white/5">
                {activeLangConfig.starterSnippet('Sample Problem')}
              </pre>
            </div>
          </div>

          {/* Section 2: Proctoring & Rules Confirmation */}
          <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-amber-300">
              <Shield size={16} /> Anti-Malpractice & Test Rules
            </div>
            <ul className="text-xs text-amber-200/80 space-y-1.5 list-disc pl-5">
              <li>Fullscreen mode will be engaged automatically upon entry.</li>
              <li>Exiting fullscreen or switching browser tabs generates proctoring violation alerts.</li>
              <li>Each of the 20 problems is evaluated against private hidden edge-case test suites.</li>
              <li>You may navigate between all 20 questions freely and submit multiple attempts per problem.</li>
            </ul>

            <label className="flex items-center gap-2 pt-2 text-xs text-white font-medium cursor-pointer">
              <input
                type="checkbox"
                checked={agreedToRules}
                onChange={(e) => setAgreedToRules(e.target.checked)}
                className="w-4 h-4 rounded border-border text-forge-600 focus:ring-forge-500"
              />
              <span>I understand the test regulations and am ready to begin in {activeLangConfig.name}</span>
            </label>
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-end gap-4 pt-4 border-t border-border/40">
            <button
              onClick={() => navigate('/student/tests')}
              className="px-5 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-muted-foreground text-xs font-semibold transition-colors"
            >
              Cancel & Back to Tests
            </button>

            <button
              onClick={handleBeginAssessment}
              disabled={!agreedToRules}
              className="px-7 py-3 rounded-xl bg-gradient-to-r from-forge-600 via-purple-600 to-forge-500 hover:from-forge-500 hover:to-purple-500 text-white font-bold text-xs glow-button flex items-center gap-2 transition-all disabled:opacity-50"
            >
              Start 20-Question Assessment ({activeLangConfig.name}) <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ────────────────────────────── ACTIVE ASSESSMENT WORKSPACE ──────────────────────────────
  const currentQuestion = assessment?.questions[activeQuestionIndex];
  const currentCode = currentQuestion ? codeMap[currentQuestion.id] || '' : '';
  const totalQuestions = assessment?.questions.length || 20;

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Fullscreen blocking overlay if student escapes */}
      {exitBlocked && (
        <FullscreenBlocker
          onReenter={enterFullscreen}
          warningNumber={violationCount}
        />
      )}

      {/* Top Authoritative Assessment Bar */}
      <header className="px-6 py-3 bg-black/70 border-b border-border/60 backdrop-blur-md flex items-center justify-between gap-4 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-forge-500 to-purple-600 flex items-center justify-center text-white font-extrabold text-xs shadow-md">
            20Q
          </div>
          <div>
            <h1 className="text-sm font-bold text-white flex items-center gap-2">
              {assessment?.title || 'Placement Coding Assessment 1'}
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-forge-500/20 text-forge-300 font-mono">
                {selectedLanguage.toUpperCase()}
              </span>
            </h1>
            <div className="text-[11px] text-muted-foreground flex items-center gap-2">
              <span>{assessment?.total_marks} Marks</span>
              <span>•</span>
              <span>20 Challenges</span>
              <span>•</span>
              <span className="flex items-center gap-1 text-amber-400 font-medium">
                <ShieldAlert size={12} /> Proctoring Monitored
              </span>
            </div>
          </div>
        </div>

        {/* Server Clock Timer & Finalize Button */}
        <div className="flex items-center gap-4">
          <div
            className={`px-4 py-1.5 rounded-xl font-mono text-sm font-bold flex items-center gap-2 border ${
              remainingSeconds < 300
                ? 'bg-red-500/20 text-red-300 border-red-500/40 animate-pulse'
                : 'bg-white/5 text-foreground border-border/60'
            }`}
          >
            <Clock size={16} />
            <span>{formatTime(remainingSeconds)}</span>
          </div>

          <button
            onClick={finalizeAssessment}
            disabled={isFinalizing}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 glow-button disabled:opacity-50"
          >
            {isFinalizing ? <LoadingSpinner size="sm" /> : <Check size={14} />}
            Finalize Test
          </button>
        </div>
      </header>

      {/* Proctoring Warning Banner if violations detected */}
      {violationCount > 0 && (
        <div className="px-6 py-2 bg-amber-950/40 border-b border-amber-500/30 text-amber-300 text-xs flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <AlertTriangle size={14} className="text-amber-400 shrink-0" />
            <span>{lastViolationMsg || 'Proctoring violation recorded.'} (Total warnings: {violationCount})</span>
          </div>
          <span className="text-[10px] uppercase font-bold text-amber-400/80">Proctoring Telemetry Active</span>
        </div>
      )}

      {/* 20-Question Horizontal Carousel Navigation Bar */}
      <div className="px-4 py-2 bg-black/40 border-b border-border/40 flex items-center gap-2 overflow-x-auto no-scrollbar">
        {assessment?.questions.map((q, idx) => {
          const isCurrent = activeQuestionIndex === idx;
          const isAnswered = !!q.user_submission;
          const isPassed = q.user_submission?.verdict === 'ACCEPTED';

          return (
            <button
              key={q.id}
              onClick={() => {
                setActiveQuestionIndex(idx);
                setRunResult(null);
                setActiveSubmission(q.user_submission || null);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 shrink-0 transition-all ${
                isCurrent
                  ? 'bg-forge-600 text-white shadow-md shadow-forge-500/30 ring-1 ring-forge-400'
                  : isAnswered
                  ? isPassed
                    ? 'bg-emerald-500/15 border border-emerald-500/40 text-emerald-300'
                    : 'bg-amber-500/15 border border-amber-500/40 text-amber-300'
                  : 'bg-white/5 hover:bg-white/10 text-muted-foreground border border-border/40'
              }`}
            >
              <span>Q{idx + 1}</span>
              {isAnswered && (
                <span className="text-[10px]">
                  {isPassed ? '✓' : '•'}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Main Workspace */}
      <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Pane: Question Description & Constraints */}
        <div className="lg:col-span-5 glass-card p-6 rounded-2xl border border-border/60 max-h-[76vh] overflow-y-auto space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="text-[11px] font-bold text-forge-400 uppercase tracking-wider">
                Question {activeQuestionIndex + 1} of {totalQuestions}
              </div>
              <h2 className="text-xl font-bold text-white mt-0.5">{currentQuestion?.title}</h2>
              <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                <span>{currentQuestion?.marks} Marks</span>
                <span>•</span>
                <span>Time Limit: {currentQuestion?.time_limit_ms || 2000}ms</span>
              </div>
            </div>
            <Badge
              variant={
                currentQuestion?.difficulty === 'EASY'
                  ? 'success'
                  : currentQuestion?.difficulty === 'HARD'
                  ? 'error'
                  : 'warning'
              }
            >
              {currentQuestion?.difficulty}
            </Badge>
          </div>

          <div className="space-y-4 text-xs text-muted-foreground leading-relaxed border-t border-border/40 pt-4">
            <div>
              <h4 className="font-semibold text-white uppercase text-[11px] mb-1">Problem Statement</h4>
              <p className="whitespace-pre-line text-foreground/90">{currentQuestion?.problem_statement}</p>
            </div>

            {currentQuestion?.constraints && (
              <div>
                <h4 className="font-semibold text-white uppercase text-[11px] mb-1">Constraints</h4>
                <pre className="p-2.5 rounded-xl bg-white/5 font-mono text-[11px] text-muted-foreground whitespace-pre-line border border-border/40">
                  {currentQuestion.constraints}
                </pre>
              </div>
            )}

            {currentQuestion?.input_format && (
              <div>
                <h4 className="font-semibold text-white uppercase text-[11px] mb-1">Input Format</h4>
                <p className="whitespace-pre-line text-foreground/80">{currentQuestion.input_format}</p>
              </div>
            )}

            {currentQuestion?.output_format && (
              <div>
                <h4 className="font-semibold text-white uppercase text-[11px] mb-1">Output Format</h4>
                <p className="whitespace-pre-line text-foreground/80">{currentQuestion.output_format}</p>
              </div>
            )}

            {currentQuestion?.examples && currentQuestion.examples.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-semibold text-white uppercase text-[11px]">Sample Examples</h4>
                {currentQuestion.examples.map((ex, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-black/40 border border-border/40 space-y-1.5">
                    <div className="text-[10px] font-bold text-forge-400">Example {idx + 1}:</div>
                    <div className="font-mono text-xs text-slate-200">Input: {ex.input}</div>
                    <div className="font-mono text-xs text-slate-200">Output: {ex.output}</div>
                    {ex.explanation && (
                      <div className="text-[11px] text-muted-foreground pt-1 border-t border-border/30">
                        {ex.explanation}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Pane: Monaco Code Editor */}
        <div className="lg:col-span-7 space-y-4">
          <div className="glass-card rounded-2xl border border-border/60 overflow-hidden shadow-xl">
            {/* Editor Toolbar */}
            <div className="p-3 bg-black/50 border-b border-border/40 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCode size={15} className="text-forge-400" />
                <span className="text-xs font-semibold text-white">Language:</span>
                <select
                  value={selectedLanguage}
                  onChange={(e) => handleLanguageSwitch(e.target.value)}
                  className="px-3 py-1 rounded-xl bg-white/10 border border-border/60 text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-forge-500"
                >
                  <option value="python" className="bg-card">Python 3</option>
                  <option value="java" className="bg-card">Java 17</option>
                  <option value="cpp" className="bg-card">C++ 17</option>
                  <option value="javascript" className="bg-card">JavaScript</option>
                </select>

                <button
                  type="button"
                  onClick={handleResetCode}
                  title="Reset code to clean starter template"
                  className="px-2.5 py-1 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors border border-border/40"
                >
                  <RotateCcw size={13} /> Reset Code
                </button>
              </div>

              {/* Navigation Arrows for the 20 problems */}
              <div className="flex items-center gap-2">
                <button
                  disabled={activeQuestionIndex === 0}
                  onClick={() => {
                    setActiveQuestionIndex((prev) => Math.max(0, prev - 1));
                    setRunResult(null);
                  }}
                  className="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-muted-foreground disabled:opacity-30 flex items-center gap-1"
                >
                  <ChevronLeft size={14} /> Prev
                </button>
                <span className="text-xs font-mono text-muted-foreground">
                  {activeQuestionIndex + 1}/{totalQuestions}
                </span>
                <button
                  disabled={activeQuestionIndex === totalQuestions - 1}
                  onClick={() => {
                    setActiveQuestionIndex((prev) => Math.min(totalQuestions - 1, prev + 1));
                    setRunResult(null);
                  }}
                  className="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-xs text-muted-foreground disabled:opacity-30 flex items-center gap-1"
                >
                  Next <ChevronRight size={14} />
                </button>
              </div>
            </div>

            {/* Monaco Editor */}
            <div className="h-[430px]">
              <Editor
                height="100%"
                language={
                  selectedLanguage === 'cpp'
                    ? 'cpp'
                    : selectedLanguage === 'javascript'
                    ? 'javascript'
                    : selectedLanguage === 'java'
                    ? 'java'
                    : 'python'
                }
                value={currentCode}
                onChange={(val) => {
                  if (currentQuestion) {
                    setCodeMap({ ...codeMap, [currentQuestion.id]: val || '' });
                  }
                }}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  fontFamily: 'JetBrains Mono, Menlo, monospace',
                  lineNumbers: 'on',
                  automaticLayout: true,
                  tabSize: 4,
                  padding: { top: 12, bottom: 12 },
                }}
              />
            </div>

            {/* Actions Bar */}
            <div className="p-3 bg-black/40 border-t border-border/40 flex items-center justify-between">
              <div className="text-[11px] text-muted-foreground flex items-center gap-1.5">
                <Layers size={13} className="text-forge-400" />
                Judge0 Isolated Runtime ({selectedLanguage})
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleRunCode}
                  disabled={isRunning || isSubmittingProblem}
                  className="px-3.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/15 text-white font-semibold text-xs flex items-center gap-1.5 disabled:opacity-50 transition-colors"
                >
                  {isRunning ? <LoadingSpinner size="sm" /> : <Play size={13} />}
                  Run Tests
                </button>

                <button
                  onClick={handleSubmitCurrentProblem}
                  disabled={isRunning || isSubmittingProblem}
                  className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold text-xs flex items-center gap-1.5 glow-button disabled:opacity-50 transition-all"
                >
                  {isSubmittingProblem ? <LoadingSpinner size="sm" /> : <Send size={13} />}
                  Submit Q{activeQuestionIndex + 1}
                </button>
              </div>
            </div>
          </div>

          {/* Test / Run Output */}
          {(runResult || activeSubmission) && (
            <div className="glass-card p-4 rounded-2xl border border-border/60 text-xs animate-fade-in space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white">Execution Verdict:</span>
                  <Badge
                    variant={
                      (runResult?.verdict || activeSubmission?.verdict) === 'ACCEPTED'
                        ? 'success'
                        : 'error'
                    }
                  >
                    {runResult?.verdict || activeSubmission?.verdict}
                  </Badge>
                  {activeSubmission?.score !== undefined && (
                    <span className="text-emerald-400 font-bold ml-2">
                      Score: {activeSubmission.score} / {currentQuestion?.marks} marks
                    </span>
                  )}
                </div>
                <div className="text-muted-foreground text-[11px]">
                  Passed: {runResult?.passed_tests || activeSubmission?.test_cases_passed || 0} /{' '}
                  {runResult?.total_tests || activeSubmission?.test_cases_total || 0} test cases
                </div>
              </div>

              {/* Sample test cases details if runResult */}
              {runResult?.test_results && runResult.test_results.length > 0 && (
                <div className="space-y-1.5 pt-2 border-t border-border/40">
                  {runResult.test_results.map((tr, idx) => (
                    <div
                      key={idx}
                      className={`p-2 rounded-xl text-[11px] font-mono flex items-center justify-between ${
                        tr.passed ? 'bg-emerald-500/10 text-emerald-300' : 'bg-red-500/10 text-red-300'
                      }`}
                    >
                      <span>Case {idx + 1}: {tr.passed ? 'PASSED' : tr.status}</span>
                      <span>{tr.runtime_ms ? `${tr.runtime_ms}ms` : ''}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
