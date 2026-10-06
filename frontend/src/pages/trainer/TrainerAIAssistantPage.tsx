import { useState, useEffect, useRef } from 'react';
import {
  Sparkles, Send, Bot, User as UserIcon, Zap, AlertTriangle,
  Brain, ShieldCheck, RefreshCw, CheckCircle2, TrendingUp,
  BarChart3, Code2, Users, MessageSquare, Plus, Trash2, Search,
  Clock
} from 'lucide-react';
import { api } from '@/services/api';
import { Badge } from '@/components/shared';
import type { ChatMessage, AIAssistantResponse, AIAssistantStatus, AIChatSessionSummary } from '@/types';

interface DisplayMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_called?: string;
  tool_arguments?: Record<string, any>;
  structured_data?: any;
  model_used?: string;
  isError?: boolean;
  intent?: string;
}

const isDataQueryIntent = (text: string): boolean => {
  const q = text.trim().toLowerCase();
  const dataKeywords = /\b(student|students|batch|cohort|candidate|candidates|learner|learners|performance|score|scores|accuracy|progress|improvement|trend|trends|rank|leaderboard|placement|readiness|weak|at-risk|struggling|failing|topic|subject|aptitude|test|tests|assessment|assessments|exam|coding|pass rate|fail rate|submission|submissions|attempt|attempts|malpractice|proctor|violation|violations|tab switch|cheating|suspicious|anomaly|anomalies|average|breakdown|summary|overview|report|analytics|insight|insights|statistics|who|which student|how many student|show me|list)\b/i;
  return dataKeywords.test(q);
};

const QUICK_PROMPTS = [
  'Which students are weak in reasoning?',
  'Who is placement ready?',
  "Summarize this cohort's performance",
  'Which students need urgent intervention?',
  'Show coding pass rate and language mix',
  'Audit assessment malpractice',
];

const WELCOME_MESSAGE: DisplayMessage = {
  id: 'welcome',
  role: 'assistant',
  content:
    'Hello! I am your **CareerForge AI Assistant** powered by **Gemma 12B**. I can query real student performance, topic mastery, placement readiness predictions, and anti-malpractice telemetry across your authorized cohorts. How can I help you today?',
  model_used: 'gemma4:12b-mlx',
  intent: 'conversational',
};

export default function TrainerAIAssistantPage() {
  const [sessions, setSessions] = useState<AIChatSessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [sessionSearch, setSessionSearch] = useState('');
  const [messages, setMessages] = useState<DisplayMessage[]>([WELCOME_MESSAGE]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Gemma 12B is formulating response...');
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [status, setStatus] = useState<AIAssistantStatus | null>(null);
  const [statusChecking, setStatusChecking] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkStatus();
    loadSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const checkStatus = async () => {
    setStatusChecking(true);
    try {
      const s = await api.getAIAssistantStatus();
      setStatus(s);
    } catch {
      setStatus({ available: false, provider: 'ollama', model: 'gemma4:12b-mlx' });
    } finally {
      setStatusChecking(false);
    }
  };

  const loadSessions = async () => {
    try {
      const sessList = await api.getTrainerChatSessions();
      setSessions(sessList);
    } catch (err) {
      console.error('Failed to load chat sessions:', err);
    }
  };

  const handleSelectSession = async (sessionId: number) => {
    if (activeSessionId === sessionId) return;
    setActiveSessionId(sessionId);
    setLoadingHistory(true);
    try {
      const detail = await api.getTrainerChatSession(sessionId);
      if (detail.messages && detail.messages.length > 0) {
        const loaded: DisplayMessage[] = detail.messages.map((m) => ({
          id: `m-${m.id}`,
          role: m.role as 'user' | 'assistant',
          content: m.content,
          tool_called: m.tool_name,
          structured_data: m.tool_result_metadata,
          model_used: m.role === 'assistant' ? 'gemma4:12b-mlx' : undefined,
          intent: m.tool_name ? 'data_query' : undefined,
        }));
        setMessages(loaded);
      } else {
        setMessages([WELCOME_MESSAGE]);
      }
    } catch (err) {
      console.error('Failed to load session detail:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([WELCOME_MESSAGE]);
    setInputValue('');
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: number) => {
    e.stopPropagation();
    try {
      await api.deleteTrainerChatSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        handleNewChat();
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || inputValue).trim();
    if (!textToSend || loading) return;

    const userMsg: DisplayMessage = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: textToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    const isData = isDataQueryIntent(textToSend);
    setLoadingMessage(
      isData
        ? 'Gemma 12B is analyzing database records & formulating response...'
        : 'Gemma 12B is formulating response...'
    );
    setLoading(true);

    try {
      // Build conversation history format for API (last few turns)
      const history: ChatMessage[] = messages
        .filter((m) => m.id !== 'welcome')
        .slice(-4)
        .map((m) => ({
          role: m.role,
          content: m.content,
        }));

      const res: AIAssistantResponse = await api.sendAIAssistantChat(
        textToSend,
        history,
        activeSessionId || undefined
      );

      // If backend created/assigned a session id, update active session
      if (res.session_id && res.session_id !== activeSessionId) {
        setActiveSessionId(res.session_id);
      }

      const assistantMsg: DisplayMessage = {
        id: `a-${Date.now()}`,
        role: 'assistant',
        content: res.reply || 'Analysis completed.',
        tool_called: res.tool_called,
        tool_arguments: res.tool_arguments,
        structured_data: res.structured_data,
        model_used: res.model_used || 'gemma4:12b-mlx',
        isError: res.status === 'ERROR',
        intent: res.intent || (isData ? 'data_query' : 'conversational'),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      // Refresh session list so new chat or title update appears
      loadSessions();
    } catch (err: any) {
      const errorMsg: DisplayMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content:
          err.response?.data?.detail ||
          'Failed to connect with Gemma 12B via Ollama. Please ensure `ollama serve` is active and the model `gemma4:12b-mlx` is loaded.',
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(sessionSearch.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto h-[calc(100vh-5.5rem)] flex flex-col space-y-4">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-border/40">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-navy-800 text-teal-400 border border-teal-500/30">
              <Sparkles size={18} />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold font-display text-white">
              AI Academic Assistant
            </h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Gemma AI Co-Pilot with real-time cohort analytics, IRT queries, and placement telemetry
          </p>
        </div>

        {/* Status Pill */}
        <div className="flex items-center gap-3">
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border ${
              status?.available
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                status?.available ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
            {statusChecking
              ? 'Checking Ollama...'
              : status?.available
              ? 'Gemma 12B (Ollama Online)'
              : 'Gemma 12B (Offline / Standby)'}
          </div>
          <button
            onClick={checkStatus}
            disabled={statusChecking}
            title="Refresh status"
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-muted-foreground transition"
          >
            <RefreshCw size={14} className={statusChecking ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Main Dual-Pane Container */}
      <div className="flex-1 flex gap-4 overflow-hidden min-h-0">
        {/* Left Sidebar: Recent Chats */}
        <div className="w-72 shrink-0 glass-card border border-border/50 rounded-2xl flex flex-col overflow-hidden">
          {/* Sidebar Top: New Chat button & Search */}
          <div className="p-3.5 border-b border-border/40 space-y-2.5">
            <button
              onClick={handleNewChat}
              className="w-full py-2 px-3 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition flex items-center justify-center gap-1.5 shadow-subtle"
            >
              <Plus size={14} />
              New Conversation
            </button>
            <div className="relative">
              <Search size={13} className="absolute left-3 top-2.5 text-muted-foreground" />
              <input
                type="text"
                value={sessionSearch}
                onChange={(e) => setSessionSearch(e.target.value)}
                placeholder="Search chats..."
                className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-white/5 border border-border/40 text-[11px] text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-forge-500 transition"
              />
            </div>
          </div>

          {/* Chat Sessions List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            <div className="px-2 py-1 text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
              Recent Conversations ({sessions.length})
            </div>

            {filteredSessions.length === 0 ? (
              <div className="p-4 text-center text-xs text-muted-foreground">
                {sessions.length === 0
                  ? 'No saved conversations yet. Start asking questions!'
                  : 'No matching chats found.'}
              </div>
            ) : (
              filteredSessions.map((sess) => {
                const isActive = sess.id === activeSessionId;
                const formattedDate = new Date(sess.updated_at || sess.created_at).toLocaleDateString(
                  undefined,
                  { month: 'short', day: 'numeric' }
                );

                return (
                  <div
                    key={sess.id}
                    onClick={() => handleSelectSession(sess.id)}
                    className={`group relative p-2.5 rounded-xl cursor-pointer transition flex items-start justify-between gap-2 text-xs ${
                      isActive
                        ? 'bg-forge-500/15 border border-forge-500/30 text-white'
                        : 'hover:bg-white/5 border border-transparent text-foreground/80'
                    }`}
                  >
                    <div className="flex items-start gap-2 min-w-0">
                      <MessageSquare
                        size={14}
                        className={`shrink-0 mt-0.5 ${isActive ? 'text-forge-400' : 'text-muted-foreground'}`}
                      />
                      <div className="min-w-0">
                        <div className="font-medium truncate">{sess.title}</div>
                        <div className="text-[10px] text-muted-foreground flex items-center gap-1.5 mt-0.5">
                          <Clock size={10} />
                          <span>{formattedDate}</span>
                          {sess.message_count !== undefined && (
                            <>
                              <span>•</span>
                              <span>{sess.message_count} msgs</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={(e) => handleDeleteSession(e, sess.id)}
                      title="Delete chat"
                      className="opacity-0 group-hover:opacity-100 p-1 rounded-md hover:bg-red-500/20 text-muted-foreground hover:text-red-400 transition shrink-0"
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Pane: Conversation & Input */}
        <div className="flex-1 flex flex-col glass-card border border-border/50 rounded-2xl overflow-hidden min-h-0">
          {/* Quick Prompts Bar */}
          <div className="p-2.5 border-b border-border/40 flex items-center gap-2 overflow-x-auto text-xs bg-black/10">
            <span className="text-muted-foreground font-semibold flex items-center gap-1 shrink-0 text-[11px]">
              <Zap size={13} className="text-forge-400" /> Prompts:
            </span>
            {QUICK_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt)}
                disabled={loading}
                className="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-foreground/80 hover:text-white border border-border/40 transition whitespace-nowrap text-[11px]"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Chat Messages Log */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {loadingHistory ? (
              <div className="h-full flex items-center justify-center text-xs text-muted-foreground gap-2">
                <div className="w-4 h-4 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
                Loading conversation history...
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-7 h-7 rounded-lg bg-navy-800 border border-teal-500/30 flex items-center justify-center text-teal-400 shrink-0 mt-0.5">
                      <Bot size={15} />
                    </div>
                  )}

                  <div
                    className={`max-w-2xl rounded-xl p-3.5 text-xs leading-relaxed space-y-2.5 ${
                      msg.role === 'user'
                        ? 'bg-navy-800 text-white border border-slate-700/80 rounded-tr-none'
                        : msg.isError
                        ? 'bg-red-950/20 text-red-300 border border-red-500/30 rounded-tl-none'
                        : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
                    }`}
                  >
                    {/* Tool Execution Badge */}
                    {msg.tool_called && (
                      <div className="flex items-center gap-1.5 p-2 rounded-lg bg-forge-500/10 border border-forge-500/20 text-[11px] text-forge-300">
                        <Zap size={12} className="text-forge-400" />
                        <span>
                          Executed Backend Tool:{' '}
                          <code className="font-mono font-bold">{msg.tool_called}</code>
                        </span>
                      </div>
                    )}

                    {/* Structured Visual Cards */}
                    {msg.structured_data && (
                      <StructuredDataRenderer data={msg.structured_data} tool={msg.tool_called} />
                    )}

                    {/* Markdown Content */}
                    <div className="whitespace-pre-line prose prose-invert prose-xs max-w-none">
                      {msg.content}
                    </div>

                    {msg.model_used && msg.role === 'assistant' && !msg.isError && (
                      <div className="text-[10px] text-muted-foreground pt-1 flex items-center justify-between border-t border-border/20">
                        <span>Engine: {msg.model_used}</span>
                        {msg.tool_called || msg.structured_data || msg.intent === 'data_query' ? (
                          <span className="flex items-center gap-1 text-emerald-400" title="Direct database analytics grounding">
                            <ShieldCheck size={11} /> Grounded on Database
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-teal-400" title="Conversational response">
                            <Sparkles size={11} /> Conversational Response
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-xl bg-forge-500/20 border border-forge-500/30 flex items-center justify-center text-forge-400 shrink-0 mt-1">
                      <UserIcon size={16} />
                    </div>
                  )}
                </div>
              ))
            )}

            {loading && (
              <div className="flex gap-3.5 justify-start">
                <div className="w-7 h-7 rounded-lg bg-navy-800 border border-teal-500/30 flex items-center justify-center text-teal-400 shrink-0">
                  <Bot size={15} />
                </div>
                <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl rounded-tl-none text-xs text-slate-400 flex items-center gap-3">
                  <div className="w-4 h-4 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
                  <span>{loadingMessage}</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Box */}
          <div className="p-3 border-t border-border/40 bg-black/20">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="relative"
            >
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask Gemma about weak topics, student performance, readiness predictions, or malpractice..."
                disabled={loading}
                className="w-full pl-4 pr-12 py-3 rounded-xl bg-secondary/60 border border-border/60 focus:border-forge-500 focus:outline-none text-xs text-foreground placeholder:text-muted-foreground transition shadow-md"
              />
              <button
                type="submit"
                disabled={loading || !inputValue.trim()}
                className="absolute right-2 top-2 p-1.5 rounded-lg bg-teal-700 hover:bg-teal-600 text-white disabled:opacity-40 transition shadow-subtle"
              >
                <Send size={14} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Renders structured backend JSON into rich UI cards alongside Gemma's explanation.
 */
function StructuredDataRenderer({ data }: { data: any; tool?: string }) {
  if (!data || typeof data !== 'object') return null;

  // 1. Single student performance profile
  if (data.student_name && data.readiness_score !== undefined && !data.batch_names && data.total_students === undefined) {
    return (
      <div className="p-3.5 rounded-xl bg-navy-900/90 border border-teal-500/30 space-y-3 text-xs">
        <div className="flex justify-between items-center border-b border-border/40 pb-2">
          <div>
            <div className="font-bold text-sm text-white flex items-center gap-2">
              <UserIcon size={14} className="text-teal-400" />
              {data.student_name}
            </div>
            {data.batch_name && (
              <div className="text-[10px] text-muted-foreground">{data.batch_name}</div>
            )}
          </div>
          <Badge variant={data.readiness_score >= 75 ? 'success' : data.readiness_score < 55 ? 'error' : 'warning'}>
            Readiness: {data.readiness_score}%
          </Badge>
        </div>

        <div className="grid grid-cols-2 gap-2 text-center text-[11px]">
          <div className="p-2 rounded-lg bg-white/5 border border-white/5">
            <div className="font-bold text-teal-400">{data.aptitude_score}%</div>
            <div className="text-[9px] text-muted-foreground uppercase">Aptitude</div>
          </div>
          <div className="p-2 rounded-lg bg-white/5 border border-white/5">
            <div className="font-bold text-emerald-400">{data.coding_score}%</div>
            <div className="text-[9px] text-muted-foreground uppercase">Coding</div>
          </div>
        </div>

        <div className="space-y-1.5 text-[11px]">
          {data.strong_areas && data.strong_areas.length > 0 && (
            <div className="flex items-start gap-1.5">
              <CheckCircle2 size={12} className="text-emerald-400 mt-0.5 shrink-0" />
              <span><strong className="text-slate-300">Strengths:</strong> {data.strong_areas.join(', ')}</span>
            </div>
          )}
          {data.weak_areas && data.weak_areas.length > 0 && (
            <div className="flex items-start gap-1.5">
              <AlertTriangle size={12} className="text-amber-400 mt-0.5 shrink-0" />
              <span><strong className="text-slate-300">Areas for Focus:</strong> {data.weak_areas.join(', ')}</span>
            </div>
          )}
          {data.recent_trend && (
            <div className="flex items-start gap-1.5">
              <TrendingUp size={12} className="text-blue-400 mt-0.5 shrink-0" />
              <span><strong className="text-slate-300">Trend:</strong> {data.recent_trend}</span>
            </div>
          )}
        </div>

        {data.recommended_action && (
          <div className="p-2 rounded-lg bg-teal-500/10 border border-teal-500/20 text-[11px] text-teal-300">
            <strong>Action:</strong> {data.recommended_action}
          </div>
        )}
      </div>
    );
  }

  // 2. Placement ready students
  if (data.placement_ready_students && Array.isArray(data.placement_ready_students)) {
    const ready = data.placement_ready_students;
    return (
      <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5">
        <div className="font-semibold text-[11px] text-teal-400 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <TrendingUp size={13} className="text-teal-400" />
            Placement-Ready Students ({data.placement_ready_count || ready.length}):
          </span>
          {data.category_breakdown && (
            <span className="text-[10px] text-muted-foreground font-normal">
              {data.category_breakdown.PLACEMENT_READY || ready.length} Ready • {data.category_breakdown.DEVELOPING || 0} Developing • {data.category_breakdown.NEEDS_IMPROVEMENT || 0} Needs Work
            </span>
          )}
        </div>

        {ready.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {ready.slice(0, 8).map((s: any, idx: number) => (
              <div key={idx} className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex justify-between items-center text-[11px]">
                <div className="min-w-0 pr-2">
                  <div className="font-semibold text-white truncate flex items-center gap-1.5">
                    <CheckCircle2 size={12} className="text-emerald-400 shrink-0" />
                    {s.student_name}
                  </div>
                  <div className="text-muted-foreground text-[10px] mt-0.5">
                    Apt: {s.aptitude_score}% • Cod: {s.coding_score}%
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <strong className="text-emerald-400 font-mono text-xs">{s.readiness_score}%</strong>
                  <div className="text-[9px] uppercase tracking-wider text-emerald-500 font-medium">Ready</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-muted-foreground italic p-2">
            No students currently meet the full placement-readiness cutoff.
          </div>
        )}
      </div>
    );
  }

  // 3. Weak students list
  if (data.weak_students && Array.isArray(data.weak_students)) {
    return (
      <div className="p-3 rounded-xl bg-black/20 border border-border/40 space-y-2">
        <div className="font-semibold text-[11px] text-forge-300 flex items-center gap-1.5">
          <AlertTriangle size={13} className="text-amber-400" />
          Students Needing Support in {data.topic || 'Cohort'} ({data.count || data.weak_students.length}):
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {data.weak_students.slice(0, 8).map((s: any, idx: number) => (
            <div key={idx} className="p-2.5 rounded-lg bg-white/5 flex justify-between items-center text-[11px]">
              <div className="min-w-0 pr-2">
                <div className="font-semibold text-foreground truncate">{s.student_name}</div>
                <div className="text-muted-foreground text-[10px] truncate">
                  {s.weak_topics && s.weak_topics.length > 0 ? `Weak: ${s.weak_topics.join(', ')}` : s.reason || 'Below benchmark'}
                </div>
              </div>
              <strong className="text-red-400 shrink-0 font-mono text-xs">
                {s.topic_accuracy !== undefined ? `${s.topic_accuracy}%` : `${s.accuracy}%`}
              </strong>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 4. At-risk students
  if (data.at_risk_students && Array.isArray(data.at_risk_students)) {
    return (
      <div className="p-3 rounded-xl bg-red-950/20 border border-red-500/30 space-y-2">
        <div className="font-semibold text-[11px] text-red-400 flex items-center gap-1.5">
          <AlertTriangle size={13} className="text-red-400" />
          At-Risk Students Requiring Intervention ({data.count || data.at_risk_students.length}):
        </div>
        <div className="space-y-1.5">
          {data.at_risk_students.slice(0, 6).map((s: any, idx: number) => (
            <div key={idx} className="p-2 rounded-lg bg-white/5 flex items-center justify-between text-[11px]">
              <div>
                <div className="font-semibold text-white flex items-center gap-2">
                  {s.student_name}
                  <Badge variant={s.risk_level === 'High Risk' ? 'error' : 'warning'}>
                    {s.risk_level || 'At Risk'}
                  </Badge>
                </div>
                <div className="text-[10px] text-muted-foreground mt-0.5">
                  {s.main_reason || `Apt: ${s.aptitude_score}% | Cod: ${s.coding_score}%`}
                </div>
              </div>
              <strong className="text-red-400 font-mono">{s.readiness_score}%</strong>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 5. Top students
  if (data.top_students && Array.isArray(data.top_students)) {
    return (
      <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
        <div className="font-semibold text-[11px] text-emerald-400 flex items-center gap-1.5">
          <TrendingUp size={13} className="text-emerald-400" />
          Top Performers ({data.ranking_metric || 'Cohort Rankings'}):
        </div>
        <div className="space-y-1.5">
          {data.top_students.slice(0, 6).map((s: any, idx: number) => (
            <div key={idx} className="p-2 rounded-lg bg-white/5 flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-2.5">
                <span className="w-5 h-5 rounded-full bg-teal-500/20 text-teal-400 font-bold text-[10px] flex items-center justify-center">
                  {s.rank || idx + 1}
                </span>
                <span className="font-semibold text-white">{s.student_name}</span>
              </div>
              <div className="flex items-center gap-2 font-mono">
                <span className="text-muted-foreground text-[10px]">Readiness: {s.readiness_score}%</span>
                <strong className="text-emerald-400">{s.ranking_score || s.score || s.readiness_score}%</strong>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 6. Batch summary card & student breakdown table
  if (data.total_students !== undefined && (data.avg_aptitude_score !== undefined || data.avg_readiness !== undefined)) {
    return (
      <div className="p-3.5 rounded-xl bg-black/20 border border-border/40 space-y-3 text-xs">
        <div className="font-semibold text-[11px] text-blue-300 flex items-center gap-1.5">
          <Users size={13} className="text-blue-400" />
          Batch Performance Metrics ({data.batch_names?.join(', ') || 'Cohort'}):
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-[11px]">
          <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <div className="font-bold text-white">{data.total_students}</div>
            <div className="text-[9px] text-slate-500 uppercase">Students</div>
          </div>
          <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <div className="font-bold text-teal-400">{data.avg_aptitude_score}%</div>
            <div className="text-[9px] text-slate-500 uppercase">Avg Aptitude</div>
          </div>
          <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <div className="font-bold text-emerald-400">{data.avg_coding_score}%</div>
            <div className="text-[9px] text-slate-500 uppercase">Avg Coding</div>
          </div>
          <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
            <div className="font-bold text-red-400">{data.at_risk_count ?? data.at_risk_students_count ?? 0}</div>
            <div className="text-[9px] text-slate-500 uppercase">At-Risk</div>
          </div>
        </div>

        {/* Student breakdown list */}
        {data.students && Array.isArray(data.students) && data.students.length > 0 && (
          <div className="mt-2 space-y-1.5 border-t border-border/30 pt-2">
            <div className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
              Enrolled Students:
            </div>
            <div className="max-h-40 overflow-y-auto space-y-1 pr-1">
              {data.students.map((s: any, idx: number) => (
                <div key={idx} className="p-1.5 rounded bg-white/5 flex items-center justify-between text-[11px]">
                  <span className="font-medium text-slate-200">{s.student_name}</span>
                  <div className="flex items-center gap-2 font-mono text-[10px]">
                    <span className="text-slate-400">R: {s.readiness}%</span>
                    <span className="text-teal-400">A: {s.aptitude}%</span>
                    <span className="text-emerald-400">C: {s.coding}%</span>
                    <Badge variant={s.status === 'Ready' ? 'success' : s.status === 'At Risk' ? 'error' : 'warning'}>
                      {s.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // 7. Coding performance card
  if (data.pass_rate !== undefined && data.total_submissions !== undefined) {
    return (
      <div className="p-3 rounded-xl bg-black/20 border border-border/40 space-y-2">
        <div className="font-semibold text-[11px] text-emerald-300 flex items-center gap-1.5">
          <Code2 size={13} className="text-emerald-400" />
          Coding Submissions Summary:
        </div>
        <div className="flex items-center gap-3 text-xs">
          <Badge variant={data.pass_rate >= 70 ? 'success' : 'warning'}>
            Pass Rate: {data.pass_rate}%
          </Badge>
          <span className="text-muted-foreground text-[11px]">
            {data.accepted} accepted of {data.total_submissions} total submissions
          </span>
        </div>
      </div>
    );
  }

  return null;
}
