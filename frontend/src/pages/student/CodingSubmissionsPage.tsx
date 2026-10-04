import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  History, ArrowLeft, CheckCircle2, XCircle, Clock,
  FileCode, Terminal, AlertCircle
} from 'lucide-react';
import { api } from '@/services/api';
import type { CodeSubmission } from '@/types';
import { Badge, LoadingSpinner } from '@/components/shared';

export default function CodingSubmissionsPage() {
  const navigate = useNavigate();
  const [submissions, setSubmissions] = useState<CodeSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSub, setSelectedSub] = useState<CodeSubmission | null>(null);

  useEffect(() => {
    loadSubmissions();
  }, []);

  async function loadSubmissions() {
    setIsLoading(true);
    try {
      const data = await api.getCodingSubmissions();
      setSubmissions(data);
    } catch (err) {
      console.error('Failed to load submissions:', err);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/student/coding')}
            className="inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground hover:text-white transition-colors mb-2"
          >
            <ArrowLeft size={16} />
            Back to Practice
          </button>
          <h1 className="text-2xl font-bold font-display text-white flex items-center gap-2">
            <History size={24} className="text-forge-400" />
            Coding Submission History
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Review all your past code solutions, evaluation verdicts, and compiler logs.
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : submissions.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-border/60 rounded-3xl glass-card">
          <FileCode size={40} className="text-muted-foreground/40 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-foreground">No submissions found</h3>
          <p className="text-xs text-muted-foreground mt-1">
            Solve your first challenge in the Coding Practice Hub to build your placement profile.
          </p>
        </div>
      ) : (
        <div className="glass-card rounded-2xl border border-border/60 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-white/5 border-b border-border/40 text-[11px] uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="py-3 px-4">Problem</th>
                  <th className="py-3 px-4">Language</th>
                  <th className="py-3 px-4">Verdict</th>
                  <th className="py-3 px-4">Score</th>
                  <th className="py-3 px-4">Tests Passed</th>
                  <th className="py-3 px-4">Submitted At</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {submissions.map((sub) => {
                  const isAccepted = sub.verdict === 'ACCEPTED';
                  const dateStr = new Date(sub.submitted_at).toLocaleString();

                  return (
                    <tr key={sub.id} className="hover:bg-white/5 transition-colors">
                      <td className="py-3 px-4 font-semibold text-foreground">
                        {sub.question_title || `Problem #${sub.coding_question_id}`}
                      </td>
                      <td className="py-3 px-4 uppercase text-muted-foreground font-mono">
                        {sub.language}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant={isAccepted ? 'success' : 'error'}>
                          {sub.verdict.replace(/_/g, ' ')}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 font-semibold text-forge-300">
                        {sub.score} pts
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">
                        {sub.test_cases_passed} / {sub.test_cases_total}
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">
                        {dateStr}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setSelectedSub(sub)}
                          className="px-3 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-foreground border border-border/40 text-xs font-medium transition-colors"
                        >
                          View Code
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Code Modal */}
      {selectedSub && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
          <div className="glass-card w-full max-w-3xl rounded-2xl border border-border/80 overflow-hidden shadow-2xl flex flex-col max-h-[85vh]">
            <div className="p-4 bg-black/40 border-b border-border/40 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-sm text-foreground">
                  {selectedSub.question_title} — Submission #{selectedSub.id}
                </h3>
                <div className="text-[11px] text-muted-foreground mt-0.5 flex items-center gap-2">
                  <span className="uppercase font-mono">{selectedSub.language}</span>
                  <span>•</span>
                  <span>Score: {selectedSub.score}</span>
                  <span>•</span>
                  <span>Verdict: {selectedSub.verdict}</span>
                </div>
              </div>

              <button
                onClick={() => setSelectedSub(null)}
                className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 text-white text-xs font-semibold"
              >
                Close
              </button>
            </div>

            <div className="p-4 overflow-y-auto space-y-4 text-xs">
              <div>
                <div className="text-[11px] uppercase tracking-wider font-semibold text-muted-foreground mb-1">
                  Submitted Code:
                </div>
                <pre className="font-mono text-xs p-4 rounded-xl bg-black/60 border border-border/40 text-slate-200 overflow-x-auto whitespace-pre">
                  {selectedSub.source_code}
                </pre>
              </div>

              {selectedSub.compile_output && (
                <div>
                  <div className="text-[11px] uppercase tracking-wider font-semibold text-red-400 mb-1">
                    Compiler Diagnostics:
                  </div>
                  <pre className="font-mono text-xs p-3 rounded-xl bg-red-950/20 border border-red-500/30 text-red-200 whitespace-pre-wrap">
                    {selectedSub.compile_output}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
