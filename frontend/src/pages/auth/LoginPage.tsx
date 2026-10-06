import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Eye, EyeOff, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('student@careerforge.ai');
  const [password, setPassword] = useState('Student@1234');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      const stored = localStorage.getItem('user');
      const user = stored ? JSON.parse(stored) : null;
      if (user?.role === 'TRAINER' || user?.role === 'ADMIN') {
        navigate('/trainer/dashboard');
      } else {
        navigate('/student/dashboard');
      }
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(e?.response?.data?.detail || e?.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const demoAccounts = [
    { label: 'Student', email: 'student@careerforge.ai', password: 'Student@1234' },
    { label: 'Trainer', email: 'trainer@careerforge.ai', password: 'Trainer@1234' },
  ];

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
            College Placement Preparation Workspace
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-7 sm:p-8 shadow-subtle space-y-5">
          <div>
            <h2 className="text-base font-bold text-white">Sign In</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Enter your credentials to access your preparation dashboard
            </p>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-950/30 border border-red-500/40 text-red-300 text-xs leading-relaxed">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold mb-1 text-slate-300">Email Address</label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-teal-500 transition-colors"
                placeholder="candidate@university.edu"
              />
            </div>

            <div>
              <label className="block font-semibold mb-1 text-slate-300">Password</label>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 pr-10 bg-slate-950 border border-slate-800 rounded-lg text-white text-xs placeholder:text-slate-500 focus:outline-none focus:border-teal-500 transition-colors"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button
              id="login-submit"
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-teal-700 hover:bg-teal-600 text-white font-semibold rounded-lg text-xs transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-subtle"
            >
              {loading ? <Loader2 size={16} className="animate-spin" /> : null}
              {loading ? 'Authenticating…' : 'Sign In to Workspace'}
            </button>
          </form>

          {/* Quick Demo Access */}
          <div className="pt-4 border-t border-slate-800">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 mb-2.5 text-center">
              Quick Demo Accounts
            </p>
            <div className="grid grid-cols-2 gap-2">
              {demoAccounts.map((acc) => (
                <button
                  key={acc.label}
                  type="button"
                  onClick={() => { setEmail(acc.email); setPassword(acc.password); }}
                  className="px-3 py-1.5 text-xs bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded-lg transition-colors font-medium text-center"
                >
                  Demo {acc.label}
                </button>
              ))}
            </div>
          </div>

          <p className="text-center text-xs text-slate-400 pt-1">
            New candidate?{' '}
            <Link to="/register" className="text-teal-400 hover:text-teal-300 font-semibold transition-colors">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
