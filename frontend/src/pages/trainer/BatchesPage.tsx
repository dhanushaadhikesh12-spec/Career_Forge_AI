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
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title="Student Placement Batches"
        subtitle="Organize student cohorts, track company-specific readiness, and assign evaluations"
        action={
          <button
            onClick={() => setShowModal(true)}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold text-xs glow-button flex items-center gap-2"
          >
            <Plus size={16} /> Create New Batch
          </button>
        }
      />

      {batches.length === 0 ? (
        <div className="text-center py-16 glass-card border border-dashed border-border rounded-2xl">
          <Users size={40} className="text-muted-foreground/40 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-foreground">No batches found</h3>
          <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
            Create your first student cohort to group students and schedule customized tests.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {batches.map((b) => (
            <div
              key={b.id}
              className="glass-card p-6 border border-border/60 hover:border-purple-500/50 transition-all space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-bold text-foreground">{b.name}</h3>
                  <div className="text-xs text-muted-foreground mt-1 flex items-center gap-1.5">
                    <Building2 size={13} />
                    <span>Campus Placement Cohort</span>
                  </div>
                </div>
                <Badge variant={b.is_active ? 'success' : 'warning'}>
                  {b.is_active ? 'ACTIVE' : 'ARCHIVED'}
                </Badge>
              </div>

              {b.description && (
                <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                  {b.description}
                </p>
              )}

              <div className="p-3 rounded-xl bg-white/5 border border-border/40 text-xs space-y-1.5">
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Created</span>
                  <span className="font-semibold text-foreground">
                    {new Date(b.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground">
                  <span>Enrolled Candidates</span>
                  <span className="font-semibold text-forge-400">
                    {b.member_count ?? 15} students
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal: Create Batch */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card p-6 border border-purple-500/30 max-w-md w-full space-y-5 animate-scale-in">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-foreground">Create Placement Cohort</h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreate} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium mb-1 text-muted-foreground">Cohort / Batch Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. 2025 Tier-1 FastTrack"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-border text-foreground text-xs focus:ring-1 focus:ring-purple-500"
                />
              </div>

              <div>
                <label className="block font-medium mb-1 text-muted-foreground">Description & Objectives</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Batch targets product companies: Amazon, Google, Microsoft, Atlassian"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-border text-foreground text-xs focus:ring-1 focus:ring-purple-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-border/50">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-border font-medium text-foreground transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold glow-button"
                >
                  {creating ? 'Creating…' : 'Create Cohort'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
