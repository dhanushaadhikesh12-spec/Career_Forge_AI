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
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Sparkles size={20} />
            </div>
            <h1 className="text-2xl font-bold font-display gradient-text">
              Trainer AI Assistant
            </h1>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Gemma 12B Co-Pilot with tool calling & strict cohort authorization
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
              className="w-full py-2.5 px-3.5 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold text-xs transition flex items-center justify-center gap-2 shadow-sm"
            >
              <Plus size={15} />
              New Chat
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
                <div className="w-4 h-4 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                Loading conversation history...
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex gap-3.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0 mt-1">
                      <Bot size={16} />
                    </div>
                  )}

                  <div
                    className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed space-y-3 ${
                      msg.role === 'user'
                        ? 'bg-forge-600 text-white rounded-tr-none'
                        : msg.isError
                        ? 'bg-red-500/10 text-red-300 border border-red-500/20 rounded-tl-none'
                        : 'glass-card border border-border/60 text-foreground rounded-tl-none'
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
                          <span className="flex items-center gap-1 text-purple-400" title="Conversational response">
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
                <div className="w-8 h-8 rounded-xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0 animate-pulse">
                  <Bot size={16} />
                </div>
                <div className="glass-card border border-border/60 p-4 rounded-2xl rounded-tl-none text-xs text-muted-foreground flex items-center gap-3">
                  <div className="w-4 h-4 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
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
                className="absolute right-2 top-2 p-1.5 rounded-lg bg-gradient-to-r from-forge-500 to-purple-600 text-white disabled:opacity-40 hover:opacity-90 transition shadow-sm"
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
function StructuredDataRenderer({ data, tool }: { data: any; tool?: string }) {
  if (!data || typeof data !== 'object') return null;

  // Weak students card
  if (data.weak_students && Array.isArray(data.weak_students)) {
    return (
      <div className="p-3 rounded-xl bg-black/20 border border-border/40 space-y-2">
        <div className="font-semibold text-[11px] text-forge-300 flex items-center gap-1.5">
          <AlertTriangle size={13} className="text-amber-400" />
          Weak Students in {data.topic || 'Cohort'} ({data.count || data.weak_students.length}):
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {data.weak_students.slice(0, 6).map((s: any, idx: number) => (
            <div key={idx} className="p-2 rounded-lg bg-white/5 flex justify-between items-center text-[11px]">
              <div>
                <div className="font-semibold text-foreground">{s.student_name}</div>
                <div className="text-muted-foreground text-[10px]">Elo: {s.skill_rating} • {s.questions_attempted} attempts</div>
              </div>
              <strong className="text-red-400">{s.accuracy}%</strong>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Placement readiness card
  if (data.category_breakdown) {
    const cb = data.category_breakdown;
    return (
      <div className="p-3 rounded-xl bg-black/20 border border-border/40 space-y-2">
        <div className="font-semibold text-[11px] text-purple-300 flex items-center gap-1.5">
          <TrendingUp size={13} className="text-emerald-400" />
          XGBoost Placement Readiness Breakdown:
        </div>
        <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
          <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold">
            <div>{cb.PLACEMENT_READY || 0}</div>
            <div className="text-[9px] uppercase tracking-wider text-muted-foreground font-normal">Ready</div>
          </div>
          <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 font-bold">
            <div>{cb.DEVELOPING || 0}</div>
            <div className="text-[9px] uppercase tracking-wider text-muted-foreground font-normal">Developing</div>
          </div>
          <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 font-bold">
            <div>{cb.NEEDS_IMPROVEMENT || 0}</div>
            <div className="text-[9px] uppercase tracking-wider text-muted-foreground font-normal">Needs Work</div>
          </div>
        </div>
      </div>
    );
  }

  // Batch summary card
  if (data.total_students !== undefined && data.avg_aptitude_score !== undefined) {
    return (
      <div className="p-3 rounded-xl bg-black/20 border border-border/40 space-y-2">
        <div className="font-semibold text-[11px] text-blue-300 flex items-center gap-1.5">
          <Users size={13} className="text-blue-400" />
          Batch Performance Metrics ({data.batch_names?.join(', ') || 'Cohort'}):
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-[11px]">
          <div className="p-2 rounded-lg bg-white/5">
            <div className="font-bold text-foreground">{data.total_students}</div>
            <div className="text-[9px] text-muted-foreground uppercase">Students</div>
          </div>
          <div className="p-2 rounded-lg bg-purple-400">{data.avg_aptitude_score}%</div>
          <div className="p-2 rounded-lg bg-white/5">
            <div className="font-bold text-emerald-400">{data.avg_coding_score}%</div>
            <div className="text-[9px] text-muted-foreground uppercase">Avg Coding</div>
          </div>
          <div className="p-2 rounded-lg bg-white/5">
            <div className="font-bold text-red-400">{data.at_risk_students_count}</div>
            <div className="text-[9px] text-muted-foreground uppercase">At-Risk</div>
          </div>
        </div>
      </div>
    );
  }

  // Coding performance card
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
