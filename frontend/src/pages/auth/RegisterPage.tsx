import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Zap, Eye, EyeOff, Loader2, GraduationCap, Briefcase } from 'lucide-react';
import type { UserRole } from '@/types';

export default function RegisterPage() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('STUDENT');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(email, password, fullName, role);
      if (role === 'TRAINER') {
        navigate('/trainer/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center relative overflow-hidden py-12">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-forge-600/20 rounded-full blur-3xl animate-pulse-glow" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md px-4">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-forge-500 to-purple-600 rounded-2xl shadow-xl shadow-forge-500/30 mb-3">
            <Zap size={26} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold font-display">
            Create an Account on <span className="gradient-text">CareerForge</span>
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">Join the next-gen placement prep platform</p>
        </div>

        <div className="glass-card neon-border p-8">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5 text-muted-foreground">I am a</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setRole('STUDENT')}
                  className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl border text-sm font-medium transition-all ${
                    role === 'STUDENT'
                      ? 'bg-forge-600/20 border-forge-500 text-forge-400 ring-1 ring-forge-500'
                      : 'bg-white/5 border-border text-muted-foreground hover:bg-white/10'
                  }`}
                >
                  <GraduationCap size={16} />
                  Student
                </button>
                <button
                  type="button"
                  onClick={() => setRole('TRAINER')}
                  className={`flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl border text-sm font-medium transition-all ${
                    role === 'TRAINER'
                      ? 'bg-purple-600/20 border-purple-500 text-purple-400 ring-1 ring-purple-500'
                      : 'bg-white/5 border-border text-muted-foreground hover:bg-white/10'
                  }`}
                >
                  <Briefcase size={16} />
                  Trainer
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5 text-muted-foreground">Full Name</label>
              <input
                id="register-fullname"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="w-full px-4 py-3 bg-white/5 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-forge-500/50"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5 text-muted-foreground">Email</label>
              <input
                id="register-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 bg-white/5 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-forge-500/50"
                placeholder="you@college.edu"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5 text-muted-foreground">Password</label>
              <div className="relative">
                <input
                  id="register-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-4 py-3 pr-12 bg-white/5 border border-border rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-forge-500/50"
                  placeholder="At least 6 characters"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              id="register-submit"
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-to-r from-forge-600 to-purple-600 hover:from-forge-500 hover:to-purple-500 text-white font-semibold rounded-xl glow-button transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : null}
              {loading ? 'Creating Account…' : 'Create Account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link to="/login" className="text-forge-400 hover:text-forge-300 font-medium transition-colors">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
