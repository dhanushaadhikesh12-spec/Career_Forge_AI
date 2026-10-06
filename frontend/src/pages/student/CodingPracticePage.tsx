import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Code2, Search, History
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
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 sm:p-7 flex flex-col md:flex-row md:items-center justify-between gap-5 shadow-subtle">
        <div>
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium mb-3">
            <Code2 size={14} className="text-teal-400" />
            <span>Judge0 Isolated Sandbox • Multilingual Compiler</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-display">
            Coding Practice Workspace
          </h1>
          <p className="text-slate-400 mt-1.5 text-xs sm:text-sm max-w-xl">
            Solve campus recruitment coding questions in Python, C++, Java, or JavaScript with real-time test case evaluation and memory/time benchmarking.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/student/coding/submissions"
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium text-xs transition-colors flex items-center gap-2 shadow-sm"
          >
            <History size={15} />
            My Submissions
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900 border border-slate-800 p-3.5 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-3 shadow-subtle">
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
          {(['ALL', 'EASY', 'MEDIUM', 'HARD'] as const).map((diff) => (
            <button
              key={diff}
              onClick={() => setSelectedDifficulty(diff)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors shrink-0 border ${
                selectedDifficulty === diff
                  ? 'bg-navy-800 text-white border-teal-500/60 shadow-subtle'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border-slate-800'
              }`}
            >
              {diff}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-72">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search problems, topics, tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3.5 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-teal-500 transition-colors"
          />
        </div>
      </div>

      {/* Questions Grid */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredQuestions.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-slate-800 rounded-xl bg-slate-900">
          <Code2 size={36} className="text-slate-600 mx-auto mb-2.5" />
          <h3 className="text-sm font-semibold text-slate-200">No coding problems found</h3>
          <p className="text-xs text-slate-400 mt-1">Try clearing your search query or choosing another difficulty level.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredQuestions.map((q) => {
            const diffColor =
              q.difficulty === 'EASY'
                ? 'success'
                : q.difficulty === 'MEDIUM'
                ? 'warning'
                : 'error';

            return (
              <div
                key={q.id}
                className="bg-slate-900 border border-slate-800 hover:border-slate-700/90 rounded-xl p-5 transition-colors flex flex-col justify-between shadow-subtle"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2.5">
                    <Badge variant={diffColor}>{q.difficulty}</Badge>
                    <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-400">
                      {q.marks} Marks
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-white">
                    {q.title}
                  </h3>

                  <div className="flex items-center gap-2 mt-1.5 text-xs text-slate-400">
                    <span>{q.topic_name || 'Algorithms'}</span>
                    {q.acceptance_rate !== null && (
                      <>
                        <span>•</span>
                        <span>{q.acceptance_rate}% Acceptance</span>
                      </>
                    )}
                  </div>

                  {q.tags && q.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3.5">
                      {q.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-[10px] px-2 py-0.2 rounded bg-slate-950 text-slate-400 border border-slate-800"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="mt-5 pt-3.5 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500">
                    {q.supported_languages.length} Languages
                  </span>

                  <button
                    onClick={() => navigate(`/student/coding/${q.slug}`)}
                    className="px-3.5 py-1.5 rounded-lg bg-teal-700 hover:bg-teal-600 text-white text-xs font-semibold transition-colors flex items-center gap-1.5 shadow-subtle"
                  >
                    Solve Problem
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
