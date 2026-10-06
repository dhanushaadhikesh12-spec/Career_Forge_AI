import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  History, ArrowLeft, FileCode
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
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <button
            onClick={() => navigate('/student/coding')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors mb-2"
          >
            <ArrowLeft size={15} />
            Back to Coding Hub
          </button>
          <h1 className="text-xl sm:text-2xl font-bold font-display text-white flex items-center gap-2">
            <History size={20} className="text-teal-400" />
            Coding Submission History
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit history of your compiler submissions, execution scores, and test verdicts.
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      ) : submissions.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-slate-800 rounded-xl bg-slate-900">
          <FileCode size={36} className="text-slate-600 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-200">No submissions found</h3>
          <p className="text-xs text-slate-400 mt-1">
            Solve problems in the Coding Practice Hub to see your submissions logged here.
          </p>
        </div>
      ) : (
        <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-subtle">
          <div className="overflow-x-auto">
            <table className="cf-table">
              <thead>
                <tr>
                  <th>Problem</th>
                  <th>Language</th>
                  <th>Verdict</th>
                  <th>Score</th>
                  <th>Tests Passed</th>
                  <th>Submitted At</th>
                  <th className="text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {submissions.map((sub) => {
                  const isAccepted = sub.verdict === 'ACCEPTED';
                  const dateStr = new Date(sub.submitted_at).toLocaleString();

                  return (
                    <tr key={sub.id}>
                      <td className="font-semibold text-white">
                        {sub.question_title || `Problem #${sub.coding_question_id}`}
                      </td>
                      <td className="uppercase text-slate-400 font-mono">
                        {sub.language}
                      </td>
                      <td>
                        <Badge variant={isAccepted ? 'success' : 'error'}>
                          {sub.verdict.replace(/_/g, ' ')}
                        </Badge>
                      </td>
                      <td className="font-semibold text-slate-200">
                        {sub.score} pts
                      </td>
                      <td className="text-slate-400">
                        {sub.test_cases_passed} / {sub.test_cases_total}
                      </td>
                      <td className="text-slate-400">
                        {dateStr}
                      </td>
                      <td className="text-right">
                        <button
                          onClick={() => setSelectedSub(sub)}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-medium transition-colors"
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
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 w-full max-w-3xl rounded-xl border border-slate-800 overflow-hidden shadow-elevated flex flex-col max-h-[85vh]">
            <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-sm text-white">
                  {selectedSub.question_title} — Submission #{selectedSub.id}
                </h3>
                <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-2">
                  <span className="uppercase font-mono">{selectedSub.language}</span>
                  <span>•</span>
                  <span>Score: {selectedSub.score}</span>
                  <span>•</span>
                  <span>Verdict: {selectedSub.verdict}</span>
                </div>
              </div>

              <button
                onClick={() => setSelectedSub(null)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
              >
                Close
              </button>
            </div>

            <div className="p-4 overflow-y-auto space-y-4 text-xs">
              <div>
                <div className="text-[11px] uppercase tracking-wider font-semibold text-slate-400 mb-1">
                  Submitted Code
                </div>
                <pre className="font-mono text-xs p-4 rounded-lg bg-slate-950 border border-slate-800 text-emerald-400/90 overflow-x-auto whitespace-pre">
                  {selectedSub.source_code}
                </pre>
              </div>

              {selectedSub.compile_output && (
                <div>
                  <div className="text-[11px] uppercase tracking-wider font-semibold text-red-400 mb-1">
                    Compiler Diagnostics
                  </div>
                  <pre className="font-mono text-xs p-3 rounded-lg bg-red-950/20 border border-red-500/30 text-red-200 whitespace-pre-wrap">
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
