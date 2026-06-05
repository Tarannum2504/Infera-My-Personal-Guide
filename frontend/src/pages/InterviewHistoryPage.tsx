import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function InterviewHistoryPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [history, setHistory] = useState<any[]>([]);

  const fetchHistory = async () => {
    try {
      const res: any = await api.get('/interview/history');
      setHistory(res.data);
    } catch (error) {
      console.error('Failed to fetch history', error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="flex h-screen bg-bgPrimary">
      <Sidebar sessions={[]} activeSession={null} onSelectSession={() => {}} onNewSession={() => {}} />
      
      <div className="flex-1 flex flex-col">
        <header className="h-16 border-b border-borderC bg-bgSurface flex items-center justify-between px-6">
          <div className="font-bold text-xl tracking-wider text-accent cursor-pointer" onClick={() => navigate('/interview')}>
            INFERA <span className="text-xs text-textMuted ml-2 font-normal">INTERVIEW HISTORY</span>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/interview')} className="text-sm text-textMuted hover:text-white">New Interview</button>
            <span className="text-textMain font-medium">{user?.full_name}</span>
            <button onClick={logout} className="text-textMuted hover:text-danger"><LogOut className="w-5 h-5" /></button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto space-y-4">
            <h2 className="text-2xl font-bold mb-6">Past Interviews</h2>
            
            {history.length === 0 ? (
              <p className="text-textMuted">No past interviews found.</p>
            ) : (
              history.map((mock: any) => (
                <div key={mock.id} className="bg-bgSurface p-6 rounded-lg border border-borderC shadow flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-bold text-white">{mock.company} - {mock.interview_round}</h3>
                    <p className="text-sm text-textMuted mt-1">
                      {new Date(mock.started_at).toLocaleString()} • {mock.status.replace('_', ' ')}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-accent">{mock.overall_score || '--'}/10</div>
                    <div className="text-xs text-textMuted">Overall Score</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
