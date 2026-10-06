import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Eye, EyeOff, Loader2, GraduationCap, Briefcase } from 'lucide-react';
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
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4 antialiased">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-navy-800 border border-teal-500/40 rounded-xl text-teal-400 font-bold text-lg shadow-subtle mb-1">
            CF
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-display">
            CAREERFORGE
          </h1>
          <p className="text-xs text-slate-400">
            Create your placement workspace account
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-7 sm:p-8 shadow-subtle space-y-5">
          <div>
            <h2 className="text-base font-bold text-white">Register Account</h2>
            <p className="text-xs text-slate-400 mt-0.5">Select role and enter your profile information</p>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-950/30 border border-red-500/40 text-red-300 text-xs leading-relaxed">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold mb-1.5 text-slate-300">Account Type</label>
              <div className="grid grid-cols-2 gap-2.5">
                <button
                  type="button"
                  onClick={() => setRole('STUDENT')}
                  className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg border text-xs font-semibold transition-colors ${
                    role === 'STUDENT'
                      ? 'bg-navy-800 border-teal-500/60 text-white shadow-subtle'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <GraduationCap size={15} className="text-teal-400" />
                  Student
                </button>
                <button
                  type="button"
                  onClick={() => setRole('TRAINER')}
                  className={`flex items-center justify-center gap-2 py-2 px-3 rounded-lg border text-xs font-semibold transition-colors ${
                    role === 'TRAINER'
                      ? 'bg-navy-800 border-amber-500/60 text-white shadow-subtle'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <Briefcase size={15} className="text-amber-400" />
                  Trainer
                </button>
              </div>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-300">Full Name</label>
              <input
                id="register-fullname"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-teal-500"
                placeholder="Candidate Full Name"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-300">Email Address</label>
              <input
                id="register-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-teal-500"
                placeholder="candidate@university.edu"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-300">Password</label>
              <div className="relative">
                <input
                  id="register-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={6}
                  className="w-full px-3.5 py-2.5 pr-10 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-teal-500"
                  placeholder="At least 6 characters"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button
              id="register-submit"
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-teal-700 hover:bg-teal-600 text-white font-semibold rounded-lg text-xs transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-subtle mt-2"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : null}
              {loading ? 'Creating Account…' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-xs text-slate-400 pt-2 border-t border-slate-800">
            Already registered?{' '}
            <Link to="/login" className="text-teal-400 hover:text-teal-300 font-semibold transition-colors">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
