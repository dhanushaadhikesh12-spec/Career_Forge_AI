import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Code2, Search, Sparkles, Filter, CheckCircle2,
  Clock, ArrowRight, History, Flame, Trophy
} from 'lucide-react';
import { api } from '@/services/api';
import type { CodingQuestionSummary } from '@/types';
import { Badge, LoadingSpinner } from '@/components/shared';

export default function CodingPracticePage() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<CodingQuestionSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadQuestions();
  }, [selectedDifficulty]);

  async function loadQuestions() {
    setIsLoading(true);
    try {
      const params: { difficulty?: string; search?: string } = {};
      if (selectedDifficulty !== 'ALL') {
        params.difficulty = selectedDifficulty;
      }
      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }
      const data = await api.getCodingQuestions(params);
      setQuestions(data);
    } catch (err) {
      console.error('Failed to load coding questions:', err);
    } finally {
      setIsLoading(false);
    }
  }

  const filteredQuestions = questions.filter((q) => {
    if (!searchQuery) return true;
    const term = searchQuery.toLowerCase();
    return (
      q.title.toLowerCase().includes(term) ||
      (q.topic_name && q.topic_name.toLowerCase().includes(term)) ||
      q.tags.some((t) => t.toLowerCase().includes(term))
    );
  });

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl p-8 bg-gradient-to-r from-blue-900/40 via-purple-900/30 to-forge-900/30 border border-blue-500/20 backdrop-blur-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-300 text-xs font-semibold mb-3">
              <Code2 size={14} className="text-blue-400" />
              <span>Technical Coding Playground • Judge0 Isolated Runtime</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold font-display text-white">
              Coding <span className="gradient-text">Practice Hub</span>
            </h1>
            <p className="text-muted-foreground mt-2 max-w-xl text-sm leading-relaxed">
              Master essential placement interview algorithms with Monaco Editor in Python, C++, Java, and JavaScript. All code executes inside isolated Judge0 sandboxes.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/student/coding/submissions"
              className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 border border-white/20 text-white font-medium text-xs transition-colors flex items-center gap-2 shadow-sm"
            >
              <History size={16} />
              My Submissions
            </Link>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-card p-4 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4 border border-border/60">
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {(['ALL', 'EASY', 'MEDIUM', 'HARD'] as const).map((diff) => (
            <button
              key={diff}
              onClick={() => setSelectedDifficulty(diff)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all shrink-0 ${
                selectedDifficulty === diff
                  ? 'bg-forge-600 text-white shadow-md shadow-forge-500/20 border border-forge-400/40'
                  : 'bg-white/5 hover:bg-white/10 text-muted-foreground border border-border/40'
              }`}
            >
              {diff}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-80">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search problems, topics, tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-white/5 border border-border/60 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-forge-500/60 transition-colors"
          />
        </div>
      </div>

      {/* Questions Grid */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredQuestions.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-border/60 rounded-3xl glass-card">
          <Code2 size={40} className="text-muted-foreground/40 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-foreground">No coding problems found</h3>
          <p className="text-xs text-muted-foreground mt-1">Try clearing your search query or choosing another difficulty level.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredQuestions.map((q) => {
            const diffColor =
              q.difficulty === 'EASY'
                ? 'emerald'
                : q.difficulty === 'MEDIUM'
                ? 'amber'
                : 'red';

            return (
              <div
                key={q.id}
                className="glass-card p-6 rounded-2xl border border-border/60 hover:border-forge-500/40 transition-all flex flex-col justify-between group hover:-translate-y-0.5 duration-200"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <Badge variant={diffColor as any}>{q.difficulty}</Badge>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-white/5 border border-border/40 text-muted-foreground">
                      {q.marks} Marks
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-foreground group-hover:text-forge-300 transition-colors">
                    {q.title}
                  </h3>

                  <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                    <span>{q.topic_name || 'Algorithms'}</span>
                    {q.acceptance_rate !== null && (
                      <>
                        <span>•</span>
                        <span>{q.acceptance_rate}% Acceptance</span>
                      </>
                    )}
                  </div>

                  {q.tags && q.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-4">
                      {q.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-[10px] px-2 py-0.5 rounded-md bg-white/5 text-muted-foreground border border-border/30"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mt-6 pt-4 border-t border-border/40 flex items-center justify-between">
                  <span className="text-[11px] text-muted-foreground">
                    {q.supported_languages.length} Languages
                  </span>

                  <button
                    onClick={() => navigate(`/student/coding/${q.slug}`)}
                    className="px-3.5 py-1.5 rounded-xl bg-forge-600/20 hover:bg-forge-600 text-forge-300 hover:text-white border border-forge-500/30 text-xs font-semibold transition-all flex items-center gap-1.5"
                  >
                    Solve Challenge <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
