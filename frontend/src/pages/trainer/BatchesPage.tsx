import { useState, useEffect, FormEvent } from 'react';
import api from '@/services/api';
import type { Batch } from '@/types';
import { PageHeader, LoadingSpinner, ErrorState, Badge } from '@/components/shared';
import { Users, Plus, Calendar, Building2, X } from 'lucide-react';

export default function BatchesPage() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);

  // Form fields
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getTrainerBatches();
      setBatches(data);
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Failed to load batches');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.createBatch(name, description);
      setShowModal(false);
      setName('');
      setDescription('');
      fetchBatches();
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      alert(e?.response?.data?.detail || 'Failed to create batch');
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="h-[60vh]" />;
  if (error) return <ErrorState message={error} onRetry={fetchBatches} />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Student Placement Batches"
        subtitle="Organize student cohorts, track company-specific readiness, and assign evaluations."
        action={
          <button
            onClick={() => setShowModal(true)}
            className="px-3.5 py-2 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold text-xs flex items-center gap-1.5 shadow-subtle"
          >
            <Plus size={15} /> Create Batch
          </button>
        }
      />

      {batches.length === 0 ? (
        <div className="text-center py-16 bg-slate-900 border border-dashed border-slate-800 rounded-xl">
          <Users size={36} className="text-slate-600 mx-auto mb-2" />
          <h3 className="text-sm font-semibold text-slate-200">No batches found</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Create your first student cohort to group students and schedule tests.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {batches.map((b) => (
            <div
              key={b.id}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-5 space-y-3.5 shadow-subtle transition-colors"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-white">{b.name}</h3>
                  <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-1.5">
                    <Building2 size={13} />
                    <span>Campus Placement Cohort</span>
                  </div>
                </div>
                <Badge variant={b.is_active ? 'success' : 'warning'}>
                  {b.is_active ? 'ACTIVE' : 'ARCHIVED'}
                </Badge>
              </div>

              {b.description && (
                <p className="text-xs text-slate-400 leading-relaxed line-clamp-2">
                  {b.description}
                </p>
              )}

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Calendar size={13} />
                  <span>Created {new Date(b.created_at).toLocaleDateString()}</span>
                </span>
                <span className="font-semibold text-slate-300">Cohort #{b.id}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Batch Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 max-w-md w-full rounded-xl p-6 space-y-4 shadow-elevated">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="font-bold text-sm text-white">Create New Placement Batch</h3>
              <button
                onClick={() => setShowModal(false)}
                className="p-1 rounded text-slate-400 hover:text-white"
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="font-semibold text-slate-300 block mb-1">
                  Batch Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 2026 CS Placement Alpha"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white placeholder:text-slate-500 focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-300 block mb-1">
                  Description
                </label>
                <textarea
                  rows={3}
                  placeholder="Target companies, tier, preparation goals..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-white placeholder:text-slate-500 focus:outline-none focus:border-teal-500 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-1.5 rounded-lg bg-teal-700 hover:bg-teal-600 text-white font-semibold transition-colors disabled:opacity-50"
                >
                  {creating ? 'Creating…' : 'Create Batch'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
