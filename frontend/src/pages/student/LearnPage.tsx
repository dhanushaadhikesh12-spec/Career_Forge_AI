import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { Subject, Topic } from '@/types';
import { PageHeader, LoadingSpinner, ErrorState } from '@/components/shared';
import { BookOpen, Brain, Layers, ArrowRight, Target, CheckCircle2 } from 'lucide-react';

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
    <div className="space-y-6">
      <PageHeader
        title="Learning Hub"
        subtitle="Explore the structured placement curriculum across aptitude, programming, and technical problem solving."
      />

      {/* Subject Filter Pills */}
      <div className="flex gap-2 overflow-x-auto pb-2 border-b border-slate-800/80">
        {subjects.map((sub) => {
          const isActive = sub.id === selectedSubjectId;
          return (
            <button
              key={sub.id}
              onClick={() => handleSelectSubject(sub.id)}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap flex items-center gap-2 border ${
                isActive
                  ? 'bg-navy-800 text-white border-teal-500/50 shadow-subtle'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800 border-slate-800'
              }`}
            >
              <Layers size={14} className={isActive ? 'text-teal-400' : 'text-slate-500'} />
              <span>{sub.name}</span>
            </button>
          );
        })}
      </div>

      {/* Selected Subject Banner */}
      {activeSubject && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 sm:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-subtle">
          <div>
            <div className="text-[10px] uppercase font-bold tracking-wider text-teal-400 mb-1">
              Active Curriculum
            </div>
            <h2 className="text-xl font-bold text-white font-display">{activeSubject.name}</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              {activeSubject.description || 'Structured topic modules aligned with standard campus recruitment patterns.'}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 shrink-0">
            <span className="w-2 h-2 rounded-full bg-teal-500" />
            <span>{topics.length} Topics Available</span>
          </div>
        </div>
      )}

      {/* Topics Grid */}
      {loadingTopics ? (
        <LoadingSpinner size="md" className="py-12" />
      ) : topics.length === 0 ? (
        <div className="text-center py-16 bg-slate-900 border border-dashed border-slate-800 rounded-xl">
          <BookOpen size={36} className="text-slate-600 mx-auto mb-2" />
          <p className="text-xs font-medium text-slate-400">No topics found for this subject.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {topics.map((t) => (
            <div
              key={t.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-xl p-5 transition-colors flex flex-col justify-between shadow-subtle"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700/80 flex items-center justify-center text-teal-400">
                    <Brain size={16} />
                  </div>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-400 font-medium">
                    {t.total_questions || 0} Questions
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white">
                  {t.name}
                </h3>
                <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 leading-relaxed">
                  {t.description || 'Master core formulas, problem archetypes, and shortcut techniques.'}
                </p>
              </div>

              <div className="mt-5 pt-3.5 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <button
                  onClick={() => navigate(`/student/topics/${t.id}`)}
                  className="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors flex items-center gap-1.5"
                >
                  <BookOpen size={13} />
                  Lessons ({t.total_lessons || 0})
                </button>

                <button
                  onClick={() => navigate(`/student/practice?topic_id=${t.id}`)}
                  className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-teal-700 hover:bg-teal-600 text-white transition-colors flex items-center gap-1.5 shadow-subtle"
                >
                  <Target size={13} />
                  Practice Now
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
