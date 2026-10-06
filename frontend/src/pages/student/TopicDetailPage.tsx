import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '@/services/api';
import type { Lesson } from '@/types';
import { LoadingSpinner, ErrorState } from '@/components/shared';
import {
  BookOpen,
  CheckCircle2,
  ArrowLeft,
  Target,
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
    <div className="space-y-6">
      {/* Top Header & Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <button
          onClick={() => navigate('/student/learn')}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft size={15} /> Back to Learning Hub
        </button>

        <button
          onClick={() => navigate(`/student/practice?topic_id=${topicId}`)}
          className="px-3.5 py-1.5 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-subtle"
        >
          <Target size={14} />
          Practice Questions
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Lesson Directory */}
        <div className="lg:col-span-4 space-y-3">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-subtle">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
              <BookOpen size={14} className="text-teal-400" />
              Topic Lessons ({lessons.length})
            </h2>

            <div className="space-y-1.5">
              {lessons.map((lesson, idx) => {
                const isSelected = selectedLesson?.id === lesson.id;
                const isCompleted = completedLessonIds.includes(lesson.id);
                return (
                  <button
                    key={lesson.id}
                    onClick={() => setSelectedLesson(lesson)}
                    className={`w-full text-left p-3 rounded-lg border text-xs transition-colors flex items-center justify-between gap-3 ${
                      isSelected
                        ? 'bg-navy-800 border-teal-500/60 text-white font-semibold shadow-subtle'
                        : 'bg-slate-950/70 border-slate-850 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border-slate-800'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <span className="w-5 h-5 rounded bg-slate-800 flex items-center justify-center text-[10px] font-mono font-bold text-slate-300 shrink-0">
                        {idx + 1}
                      </span>
                      <span className="truncate">{lesson.title}</span>
                    </div>

                    {isCompleted ? (
                      <CheckCircle2 size={15} className="text-emerald-400 shrink-0" />
                    ) : (
                      <ChevronRight size={13} className="text-slate-600 shrink-0" />
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
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 sm:p-7 space-y-6 shadow-subtle">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-800">
                <div>
                  <div className="text-[10px] font-bold text-teal-400 uppercase tracking-wider mb-1">
                    Lesson Content
                  </div>
                  <h1 className="text-xl sm:text-2xl font-bold text-white font-display">
                    {selectedLesson.title}
                  </h1>
                </div>

                <button
                  onClick={() => handleComplete(selectedLesson.id)}
                  disabled={completing || completedLessonIds.includes(selectedLesson.id)}
                  className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                    completedLessonIds.includes(selectedLesson.id)
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 cursor-default'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700'
                  }`}
                >
                  <CheckCircle2 size={14} />
                  {completedLessonIds.includes(selectedLesson.id) ? 'Completed' : 'Mark as Completed'}
                </button>
              </div>

              {/* Lesson Text Container */}
              <div className="bg-slate-950/80 rounded-lg p-5 border border-slate-800/80 text-slate-300 text-xs sm:text-sm whitespace-pre-wrap leading-relaxed font-sans">
                {selectedLesson.content}
              </div>

              {/* Action footer */}
              <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="text-xs text-slate-500 flex items-center gap-1.5">
                  <Clock size={13} /> Estimated study time: ~5 mins
                </div>

                <button
                  onClick={() => navigate(`/student/practice?topic_id=${topicId}`)}
                  className="px-4 py-2 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs transition-colors flex items-center justify-center gap-1.5 shadow-subtle"
                >
                  <Target size={14} />
                  Practice Topic Questions
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-dashed border-slate-800 rounded-xl p-12 text-center">
              <BookOpen size={36} className="text-slate-600 mx-auto mb-2" />
              <p className="text-xs font-medium text-slate-400">Select a lesson from the outline</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
