import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { Lesson } from '@/types';
import { PageHeader, LoadingSpinner, ErrorState } from '@/components/shared';
import {
  BookOpen,
  CheckCircle2,
  ArrowLeft,
  Target,
  Sparkles,
  Clock,
  ChevronRight,
} from 'lucide-react';

export default function TopicDetailPage() {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);
  const [completedLessonIds, setCompletedLessonIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (topicId) {
      fetchLessons(parseInt(topicId));
    }
  }, [topicId]);

  const fetchLessons = async (tId: number) => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getLessons(tId);
      setLessons(data);
      if (data.length > 0) {
        setSelectedLesson(data[0]);
      }
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to load lessons');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async (lessonId: number) => {
    setCompleting(true);
    try {
      await api.completeLesson(lessonId, 120);
      setCompletedLessonIds((prev) => [...prev, lessonId]);
    } catch (err) {
      console.error(err);
    } finally {
      setCompleting(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[60vh]" />;
  if (error) return <ErrorState message={error} onRetry={() => topicId && fetchLessons(parseInt(topicId))} />;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/student/learn')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft size={16} /> Back to Learning Hub
        </button>

        <button
          onClick={() => navigate(`/student/practice?topic_id=${topicId}`)}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 text-white font-semibold text-xs glow-button flex items-center gap-2"
        >
          <Target size={16} />
          Practice Questions
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Lesson Directory */}
        <div className="lg:col-span-4 space-y-3">
          <div className="glass-card p-5 border border-border/60">
            <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground mb-4 flex items-center gap-2">
              <BookOpen size={16} className="text-forge-400" />
              Lesson Outline ({lessons.length})
            </h2>

            <div className="space-y-2">
              {lessons.map((lesson, idx) => {
                const isSelected = selectedLesson?.id === lesson.id;
                const isCompleted = completedLessonIds.includes(lesson.id);
                return (
                  <button
                    key={lesson.id}
                    onClick={() => setSelectedLesson(lesson)}
                    className={`w-full text-left p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${
                      isSelected
                        ? 'bg-forge-600/20 border-forge-500 text-white font-semibold ring-1 ring-forge-500/40'
                        : 'bg-white/5 border-border/50 text-muted-foreground hover:text-foreground hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 rounded-lg bg-white/5 flex items-center justify-center text-xs font-bold font-mono">
                        {idx + 1}
                      </span>
                      <span className="text-xs font-medium truncate max-w-[180px]">{lesson.title}</span>
                    </div>

                    {isCompleted ? (
                      <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                    ) : (
                      <ChevronRight size={14} className="opacity-50 shrink-0" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Selected Lesson Content */}
        <div className="lg:col-span-8">
          {selectedLesson ? (
            <div className="glass-card p-8 border border-border/60 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-border/60">
                <div>
                  <div className="text-xs font-semibold text-forge-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <Sparkles size={14} /> Lesson Concept
                  </div>
                  <h1 className="text-2xl font-bold font-display text-white">{selectedLesson.title}</h1>
                </div>

                <button
                  onClick={() => handleComplete(selectedLesson.id)}
                  disabled={completing || completedLessonIds.includes(selectedLesson.id)}
                  className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${
                    completedLessonIds.includes(selectedLesson.id)
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 cursor-default'
                      : 'bg-white/10 hover:bg-white/15 text-white border border-white/20'
                  }`}
                >
                  <CheckCircle2 size={15} />
                  {completedLessonIds.includes(selectedLesson.id) ? 'Completed' : 'Mark as Done'}
                </button>
              </div>

              {/* Rich Lesson Content Display */}
              <div className="prose prose-invert max-w-none text-sm leading-relaxed text-muted-foreground space-y-4">
                <div className="p-4 rounded-xl bg-white/5 border border-border/40 text-foreground font-mono text-xs whitespace-pre-wrap leading-relaxed">
                  {selectedLesson.content}
                </div>
              </div>

              {/* Action footer */}
              <div className="pt-6 border-t border-border/60 flex items-center justify-between">
                <div className="text-xs text-muted-foreground flex items-center gap-2">
                  <Clock size={14} /> Recommended reading time: ~5 mins
                </div>

                <button
                  onClick={() => navigate(`/student/practice?topic_id=${topicId}`)}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 text-white font-semibold text-xs glow-button flex items-center gap-2"
                >
                  <Target size={16} />
                  Solve Topic Practice Problems
                </button>
              </div>
            </div>
          ) : (
            <div className="glass-card p-12 text-center border border-dashed border-border">
              <BookOpen size={40} className="text-muted-foreground/30 mx-auto mb-3" />
              <p className="text-sm font-medium text-foreground">Select a lesson from the outline</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
