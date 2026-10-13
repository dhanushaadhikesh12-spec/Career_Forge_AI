import { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Sparkles, Send, Bot, User as UserIcon, Zap, AlertTriangle,
  Brain, ShieldCheck, RefreshCw, CheckCircle2, TrendingUp,
  BarChart3, Code2, Users, MessageSquare, Plus, Trash2, Search,
  Clock, ArrowRight, Target, Calendar, Award, Check, FileQuestion,
  HelpCircle, ChevronRight, X
} from 'lucide-react';
import { api } from '@/services/api';
import { Badge, LoadingSpinner } from '@/components/shared';
import type {
  StudentCoachMessage,
  StudentCoachSessionSummary,
  StudentCoachResponse
} from '@/types';

interface DisplayMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_called?: string;
  structured_data?: any;
  model_used?: string;
  isError?: boolean;
  intent?: string;
  created_at?: string;
}

const QUICK_ACTIONS = [
  {
    icon: <BarChart3 size={16} className="text-teal-400" />,
    title: 'Analyze Performance',
    prompt: 'How am I performing? Give me an overall summary of my aptitude and coding scores.',
    badge: 'Overview',
  },
  {
    icon: <Target size={16} className="text-amber-400" />,
    title: 'Find Weak Topics',
    prompt: 'What are my weak topics? Where am I struggling the most?',
    badge: 'Diagnostics',
  },
  {
    icon: <Award size={16} className="text-emerald-400" />,
    title: 'Check Readiness',
    prompt: 'Am I placement ready? What is my ML placement readiness score and category?',
    badge: 'XGBoost ML',
  },
  {
    icon: <Calendar size={16} className="text-indigo-400" />,
    title: '7-Day Study Plan',
    prompt: 'Create a personalized 7-day placement preparation study plan targeting my weakest areas.',
    badge: 'Action Plan',
  },
  {
    icon: <Code2 size={16} className="text-cyan-400" />,
    title: 'Analyze Coding',
    prompt: 'How is my coding performance? Which algorithmic topics should I improve?',
    badge: 'Algorithms',
  },
  {
    icon: <Brain size={16} className="text-rose-400" />,
    title: 'Practice Weak Areas',
    prompt: 'Give me 5 adaptive practice questions on my weakest topics from the question bank.',
    badge: 'Adaptive IRT',
  },
];

const WELCOME_MESSAGE: DisplayMessage = {
  id: 'welcome',
  role: 'assistant',
  content:
    "Hello! I'm your **CareerForge AI Personal Placement Coach** powered by **Gemma 12B**.\n\n" +
    "I analyze your real practice history, test scores, and ML placement readiness to give you personalized guidance. " +
    "How would you like to prepare today?",
  model_used: 'gemma4:12b-mlx',
  intent: 'general_chat',
};

export default function StudentAICoachPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [sessions, setSessions] = useState<StudentCoachSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [sessionSearch, setSessionSearch] = useState('');
  const [messages, setMessages] = useState<DisplayMessage[]>([WELCOME_MESSAGE]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [status, setStatus] = useState<{ available: boolean; model: string } | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Question context passed via URL
  const [questionContext, setQuestionContext] = useState<{ question_id?: number; attempt_id?: number } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    checkStatus();
    loadSessions();

    // Check URL parameters for contextual prompts
    const promptParam = searchParams.get('prompt');
    const qIdParam = searchParams.get('questionId');
    const attIdParam = searchParams.get('attemptId');

    if (qIdParam) {
      setQuestionContext({
        question_id: parseInt(qIdParam),
        attempt_id: attIdParam ? parseInt(attIdParam) : undefined,
      });
    }

    if (promptParam) {
      // Auto-send or prefill prompt
      setInputValue(promptParam);
    }
  }, [searchParams]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const checkStatus = async () => {
    try {
      const s = await api.getStudentCoachStatus();
      setStatus({ available: s.available, model: s.model });
    } catch {
      setStatus({ available: false, model: 'gemma4:12b-mlx' });
    }
  };

  const loadSessions = async () => {
    try {
      const sessList = await api.getStudentCoachSessions();
      setSessions(sessList);
    } catch (err) {
      console.error('Failed to load coaching sessions:', err);
    }
  };

  const handleSelectSession = async (sessionId: number) => {
    if (activeSessionId === sessionId) return;
    setActiveSessionId(sessionId);
    setLoadingHistory(true);
    try {
      const detail = await api.getStudentCoachSession(sessionId);
      if (detail.messages && detail.messages.length > 0) {
        const loaded: DisplayMessage[] = detail.messages.map((m) => ({
          id: `m-${m.id}`,
          role: m.role as 'user' | 'assistant',
          content: m.content,
          tool_called: m.tool_name || undefined,
          structured_data: m.tool_result_metadata || undefined,
          created_at: m.created_at,
        }));
        setMessages(loaded);
      } else {
        setMessages([WELCOME_MESSAGE]);
      }
    } catch (err) {
      console.error('Failed to load session details:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleNewSession = async () => {
    setActiveSessionId(null);
    setMessages([WELCOME_MESSAGE]);
    setQuestionContext(null);
    if (inputRef.current) inputRef.current.focus();
  };

  const handleDeleteSession = async (sessionId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteStudentCoachSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        handleNewSession();
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend !== undefined ? textToSend : inputValue).trim();
    if (!text || loading) return;

    const userMsgId = `u-${Date.now()}`;
    const userMsg: DisplayMessage = {
      id: userMsgId,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setLoading(true);

    try {
      // Build conversation history for context
      const history = messages
        .filter((m) => m.id !== 'welcome')
        .slice(-6)
        .map((m) => ({ role: m.role, content: m.content }));

      const res: StudentCoachResponse = await api.sendStudentCoachChat({
        query: text,
        sessionId: activeSessionId || undefined,
        history,
        questionContext: questionContext || undefined,
      });

      if (res.session_id && activeSessionId !== res.session_id) {
        setActiveSessionId(res.session_id);
        loadSessions();
      }

      const assistantMsg: DisplayMessage = {
        id: `a-${Date.now()}`,
        role: 'assistant',
        content: res.reply,
        tool_called: res.tool_called,
        structured_data: res.structured_data,
        model_used: res.model_used,
        intent: res.intent,
        isError: res.status === 'ERROR',
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Failed to send coach chat:', err);
      const errorMsg: DisplayMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content:
          "I couldn't process your request right now. Please check your connection and try again.",
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(sessionSearch.toLowerCase())
  );

  return (
    <div className="flex h-[calc(100vh-5rem)] gap-4">
      {/* ── Sessions Drawer / Sidebar ───────────────────────────────────── */}
      <div
        className={`${
          sidebarOpen ? 'block' : 'hidden'
        } md:block w-72 shrink-0 bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden shadow-subtle`}
      >
        <div className="p-3.5 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-teal-400" />
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Coaching Chats
            </h2>
          </div>
          <button
            onClick={handleNewSession}
            className="p-1.5 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-400 border border-teal-500/30 text-xs font-medium transition-colors flex items-center gap-1"
            title="New Coaching Session"
          >
            <Plus size={14} />
            <span>New</span>
          </button>
        </div>

        {/* Search */}
        <div className="p-2.5 border-b border-slate-800/80">
          <div className="relative">
            <Search size={13} className="absolute left-2.5 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={sessionSearch}
              onChange={(e) => setSessionSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500/50"
            />
          </div>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {filteredSessions.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500">
              No conversations found.
            </div>
          ) : (
            filteredSessions.map((s) => (
              <div
                key={s.id}
                onClick={() => handleSelectSession(s.id)}
                className={`p-2.5 rounded-lg text-xs cursor-pointer group flex items-center justify-between transition-colors ${
                  activeSessionId === s.id
                    ? 'bg-teal-500/15 border border-teal-500/40 text-teal-200 font-medium'
                    : 'hover:bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-2 min-w-0 flex-1">
                  <MessageSquare size={13} className="shrink-0 text-slate-500 group-hover:text-teal-400" />
                  <span className="truncate">{s.title}</span>
                </div>
                <button
                  onClick={(e) => handleDeleteSession(s.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 transition-opacity ml-1"
                  title="Delete Session"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))
          )}
        </div>

        {/* AI Status Badge */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/40 flex items-center justify-between text-[11px]">
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                status?.available ? 'bg-emerald-400' : 'bg-amber-400'
              }`}
            />
            <span className="text-slate-400">
              {status?.available ? 'Gemma 12B Connected' : 'Gemma Local Engine'}
            </span>
          </div>
          <span className="text-slate-500 text-[10px]">Ollama</span>
        </div>
      </div>

      {/* ── Main Chat Area ──────────────────────────────────────────────── */}
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl flex flex-col overflow-hidden shadow-subtle min-w-0">
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 shadow-sm">
              <Sparkles size={17} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm sm:text-base font-bold text-white font-display">
                  AI Personal Placement Coach
                </h1>
                <Badge variant="success" className="text-[10px] px-1.5 py-0">
                  Student Mentor
                </Badge>
              </div>
              <p className="text-[11px] text-slate-400">
                Personalized guidance powered by your actual performance records
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden px-2.5 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-300 border border-slate-700"
            >
              Chats
            </button>
            <button
              onClick={handleNewSession}
              className="hidden sm:flex px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium items-center gap-1.5 transition-colors"
            >
              <Plus size={13} />
              <span>New Chat</span>
            </button>
          </div>
        </div>

        {/* Active Question Context Banner */}
        {questionContext?.question_id && (
          <div className="px-4 py-2 bg-indigo-950/40 border-b border-indigo-500/30 flex items-center justify-between text-xs text-indigo-200">
            <div className="flex items-center gap-2">
              <FileQuestion size={14} className="text-indigo-400" />
              <span>
                Active Question Context: <strong>Question #{questionContext.question_id}</strong>
                {questionContext.attempt_id && ` (Attempt #${questionContext.attempt_id})`}
              </span>
            </div>
            <button
              onClick={() => setQuestionContext(null)}
              className="text-indigo-400 hover:text-indigo-200 text-xs flex items-center gap-1"
            >
              <X size={13} />
              <span>Clear Context</span>
            </button>
          </div>
        )}

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
          {loadingHistory ? (
            <div className="h-full flex items-center justify-center">
              <LoadingSpinner size="md" />
            </div>
          ) : (
            <>
              {/* Quick Actions (only shown at start of session) */}
              {messages.length <= 1 && (
                <div className="mb-6 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Recommended Coaching Prompts
                    </span>
                    <span className="text-[11px] text-slate-500">Click any card to start</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                    {QUICK_ACTIONS.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(action.prompt)}
                        className="text-left p-3 rounded-xl bg-slate-950/80 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-700 transition-all group flex flex-col justify-between gap-2 shadow-subtle hover:scale-[1.01]"
                      >
                        <div className="flex items-center justify-between w-full">
                          <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 group-hover:border-slate-700">
                            {action.icon}
                          </div>
                          <span className="text-[10px] font-medium text-slate-400 bg-slate-900 px-2 py-0.5 rounded-full border border-slate-800">
                            {action.badge}
                          </span>
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-slate-200 group-hover:text-white flex items-center gap-1">
                            {action.title}
                            <ArrowRight size={11} className="opacity-0 group-hover:opacity-100 transition-opacity text-teal-400" />
                          </div>
                          <div className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">
                            {action.prompt}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Message Bubbles */}
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 max-w-4xl ${
                    msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`w-7 h-7 rounded-lg shrink-0 flex items-center justify-center text-xs font-bold ${
                      msg.role === 'user'
                        ? 'bg-slate-800 border border-slate-700 text-slate-300'
                        : 'bg-teal-500/10 border border-teal-500/30 text-teal-400 shadow-sm'
                    }`}
                  >
                    {msg.role === 'user' ? <UserIcon size={14} /> : <Sparkles size={14} />}
                  </div>

                  {/* Bubble Content */}
                  <div
                    className={`rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-teal-600 text-white rounded-tr-sm max-w-lg shadow-sm'
                        : msg.isError
                        ? 'bg-red-950/30 border border-red-500/40 text-red-200 rounded-tl-sm w-full'
                        : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-tl-sm w-full shadow-subtle'
                    }`}
                  >
                    {/* Tool Badge Indicator */}
                    {msg.tool_called && (
                      <div className="mb-2.5 inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[10px] font-mono text-teal-400">
                        <Zap size={10} />
                        <span>Data Grounding: {msg.tool_called}</span>
                      </div>
                    )}

                    {/* Main Text Content */}
                    <div className="prose prose-invert prose-sm max-w-none space-y-2 whitespace-pre-wrap">
                      {msg.content}
                    </div>

                    {/* Structured Result Display (Readiness) */}
                    {msg.structured_data?.readiness_score !== undefined && (
                      <div className="mt-4 p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                            <Award size={14} className="text-teal-400" />
                            XGBoost Placement Readiness
                          </span>
                          <span className="text-base font-bold text-teal-300 font-mono">
                            {msg.structured_data.readiness_score}%
                          </span>
                        </div>

                        {msg.structured_data.strengths && msg.structured_data.strengths.length > 0 && (
                          <div>
                            <span className="text-[11px] font-medium text-slate-400 block mb-1">
                              Strengths:
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {msg.structured_data.strengths.map((s: string, idx: number) => (
                                <span
                                  key={idx}
                                  className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-medium"
                                >
                                  {s}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {msg.structured_data.improvement_areas && msg.structured_data.improvement_areas.length > 0 && (
                          <div>
                            <span className="text-[11px] font-medium text-slate-400 block mb-1">
                              Areas to Improve:
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {msg.structured_data.improvement_areas.map((a: string, idx: number) => (
                                <span
                                  key={idx}
                                  className="px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] font-medium"
                                >
                                  {a}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Structured Result Display (Weak Topics) */}
                    {msg.structured_data?.topics && msg.structured_data.topics.length > 0 && (
                      <div className="mt-4 p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                        <span className="text-xs font-semibold text-slate-300 block">
                          Weak Topic Breakdown
                        </span>
                        <div className="space-y-1.5">
                          {msg.structured_data.topics.map((t: any, idx: number) => (
                            <div
                              key={idx}
                              className="p-2 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between text-xs"
                            >
                              <span className="font-medium text-slate-200">{t.topic}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-amber-400 font-mono font-semibold">
                                  {t.accuracy}%
                                </span>
                                <span className="text-[10px] text-slate-500">
                                  ({t.questions_attempted} attempts)
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Structured Result Display (Practice Questions) */}
                    {msg.structured_data?.questions && msg.structured_data.questions.length > 0 && (
                      <div className="mt-4 p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2.5">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold text-slate-300">
                            Selected Adaptive Questions ({msg.structured_data.questions.length})
                          </span>
                          <button
                            onClick={() => navigate('/student/practice')}
                            className="text-xs text-teal-400 hover:text-teal-300 flex items-center gap-1 font-medium"
                          >
                            Launch Full Practice Mode <ArrowRight size={12} />
                          </button>
                        </div>
                        <div className="space-y-2">
                          {msg.structured_data.questions.map((q: any, idx: number) => (
                            <div
                              key={idx}
                              className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 space-y-1 text-xs"
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-[10px] font-semibold text-teal-400 uppercase tracking-wider">
                                  Q{idx + 1} • {q.difficulty}
                                </span>
                                <span className="text-[10px] text-slate-500">{q.topic}</span>
                              </div>
                              <p className="text-slate-200 font-medium">{q.text}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Loading Indicator */}
              {loading && (
                <div className="flex gap-3 max-w-3xl">
                  <div className="w-7 h-7 rounded-lg shrink-0 flex items-center justify-center bg-teal-500/10 border border-teal-500/30 text-teal-400 shadow-sm animate-pulse">
                    <Sparkles size={14} />
                  </div>
                  <div className="rounded-2xl rounded-tl-sm p-4 bg-slate-950 border border-slate-800 text-xs text-slate-400 flex items-center gap-2.5">
                    <RefreshCw size={13} className="animate-spin text-teal-400" />
                    <span>Analyzing your CareerForge performance and formulating response...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90">
          <div className="relative rounded-xl bg-slate-950 border border-slate-800 focus-within:border-teal-500/50 transition-colors shadow-inner">
            <textarea
              ref={inputRef}
              rows={2}
              placeholder="Ask your coach anything about performance, readiness, weak topics, or CS concepts..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              className="w-full pl-3.5 pr-24 py-2.5 bg-transparent text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none resize-none leading-relaxed"
            />
            <div className="absolute right-2.5 bottom-2.5 flex items-center gap-1.5">
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || loading}
                className="p-2 rounded-lg bg-teal-500 hover:bg-teal-400 disabled:opacity-40 disabled:hover:bg-teal-500 text-slate-950 font-semibold transition-all shadow-sm"
                title="Send Message"
              >
                <Send size={14} />
              </button>
            </div>
          </div>

          <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 px-1">
            <span>Press Enter to send, Shift + Enter for new line</span>
            <span className="hidden sm:inline">Only your personal CareerForge data is accessible</span>
          </div>
        </div>
      </div>
    </div>
  );
}
