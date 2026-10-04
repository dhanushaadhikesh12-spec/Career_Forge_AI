import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { Subject, Topic } from '@/types';
import { PageHeader, LoadingSpinner, ErrorState } from '@/components/shared';
import { BookOpen, ChevronRight, Brain, Target, Sparkles, Layers } from 'lucide-react';

export default function LearnPage() {
  const navigate = useNavigate();
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loadingSubjects, setLoadingSubjects] = useState(true);
  const [loadingTopics, setLoadingTopics] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    setLoadingSubjects(true);
    setError('');
    try {
      const data = await api.getSubjects();
      setSubjects(data);
      if (data.length > 0) {
        setSelectedSubjectId(data[0].id);
        fetchTopics(data[0].id);
      }
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to load learning subjects');
    } finally {
      setLoadingSubjects(false);
    }
  };

  const fetchTopics = async (subjectId: number) => {
    setLoadingTopics(true);
    try {
      const data = await api.getTopics(subjectId);
      setTopics(data);
    } catch (err: unknown) {
      console.error(err);
    } finally {
      setLoadingTopics(false);
    }
  };

  const handleSelectSubject = (id: number) => {
    setSelectedSubjectId(id);
    fetchTopics(id);
  };

  if (loadingSubjects) return <LoadingSpinner size="lg" className="h-[60vh]" />;
  if (error) return <ErrorState message={error} onRetry={fetchSubjects} />;

  const activeSubject = subjects.find((s) => s.id === selectedSubjectId);

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title="Learning Hub"
        subtitle="Master placement aptitude & core computer science concepts with bite-sized lessons"
      />

      {/* Subject Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 border-b border-border/60">
        {subjects.map((sub) => {
          const isActive = sub.id === selectedSubjectId;
          return (
            <button
              key={sub.id}
              onClick={() => handleSelectSubject(sub.id)}
              className={`px-5 py-2.5 rounded-xl font-medium text-sm transition-all whitespace-nowrap flex items-center gap-2 ${
                isActive
                  ? 'bg-forge-600 text-white shadow-lg shadow-forge-600/30'
                  : 'bg-white/5 text-muted-foreground hover:bg-white/10 hover:text-foreground border border-border/40'
              }`}
            >
              <Layers size={16} />
              <span>{sub.name}</span>
            </button>
          );
        })}
      </div>

      {/* Selected Subject Intro */}
      {activeSubject && (
        <div className="glass-card p-6 border border-forge-500/20 bg-gradient-to-r from-forge-950/20 to-purple-950/20 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-foreground">{activeSubject.name}</h2>
            <p className="text-xs text-muted-foreground mt-1 max-w-xl">
              {activeSubject.description || 'Comprehensive curriculum aligned with top tech company campus hiring tests.'}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-forge-400">
            <Sparkles size={16} />
            <span>{topics.length} Targeted Topics</span>
          </div>
        </div>
      )}

      {/* Topics Grid */}
      {loadingTopics ? (
        <LoadingSpinner size="md" className="py-12" />
      ) : topics.length === 0 ? (
        <div className="text-center py-16 glass-card border border-dashed border-border">
          <BookOpen size={36} className="text-muted-foreground/40 mx-auto mb-2" />
          <p className="text-sm font-medium text-foreground">No topics found in this category.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topics.map((t) => (
            <div
              key={t.id}
              className="glass-card p-6 border border-border/60 hover:border-forge-500/50 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-forge-500/10 border border-forge-500/20 flex items-center justify-center text-forge-400 group-hover:scale-105 transition-transform">
                    <Brain size={20} />
                  </div>
                  <span className="text-[11px] px-2.5 py-1 rounded-full bg-white/5 border border-border font-medium text-muted-foreground">
                    {t.total_questions || 0} Questions
                  </span>
                </div>

                <h3 className="text-base font-bold text-foreground group-hover:text-forge-300 transition-colors">
                  {t.name}
                </h3>
                <p className="text-xs text-muted-foreground mt-2 line-clamp-2 leading-relaxed">
                  {t.description || 'Learn core concepts, formulas, shortcuts, and solve high-probability interview problems.'}
                </p>
              </div>

              <div className="mt-6 pt-4 border-t border-border/40 flex items-center justify-between gap-3">
                <button
                  onClick={() => navigate(`/student/topics/${t.id}`)}
                  className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-white/5 hover:bg-white/10 text-foreground border border-border transition-colors flex items-center gap-1.5"
                >
                  <BookOpen size={14} />
                  View Lessons ({t.total_lessons || 0})
                </button>

                <button
                  onClick={() => navigate(`/student/practice?topic_id=${t.id}`)}
                  className="px-3.5 py-2 text-xs font-semibold rounded-lg bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white glow-button transition-all flex items-center gap-1.5"
                >
                  <Target size={14} />
                  Practice
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
