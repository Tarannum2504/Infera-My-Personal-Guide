import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('ishara@infera.app');
  const [password, setPassword] = useState('InferaAI2026!');
  const { login } = useAuth();
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      if (isLogin) {
        const res = await api.post('/auth/login', { email, password });
        login(res.data.access_token);
      } else {
        const res = await api.post('/auth/register', { email, password, full_name: 'Ishara' });
        login(res.data.access_token);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bgPrimary">
      <div className="bg-bgSurface p-8 rounded-lg shadow-xl w-full max-w-md border border-borderC">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-accent mb-2">INFERA</h1>
          <p className="text-textMuted">Your AI Career System</p>
        </div>
        
        {error && <div className="bg-danger/20 text-danger p-3 rounded mb-4">{error}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-textMuted text-sm mb-1">Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-bgCard border border-borderC rounded p-2 text-textMain focus:border-accent focus:outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-textMuted text-sm mb-1">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-bgCard border border-borderC rounded p-2 text-textMain focus:border-accent focus:outline-none"
              required
            />
          </div>
          <button 
            type="submit" 
            className="w-full bg-accent hover:bg-accent/90 text-white font-bold py-2 px-4 rounded transition-colors"
          >
            {isLogin ? 'Login' : 'Initialize Profile'}
          </button>
        </form>
        
        <div className="mt-4 text-center">
          <button 
            onClick={() => setIsLogin(!isLogin)}
            className="text-textMuted hover:text-textMain text-sm"
          >
            {isLogin ? 'Need an account? Register' : 'Already have an account? Login'}
          </button>
        </div>
      </div>
    </div>
  );
}
