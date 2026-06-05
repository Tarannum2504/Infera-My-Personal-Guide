import React, { useState } from 'react';
import { MessageSquare, List, FileText, Brain, LayoutDashboard, Search, Filter } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

interface Session {
  id: number;
  title: string;
  last_message_at: string;
}

interface SidebarProps {
  sessions: Session[];
  activeSession: number | null;
  onSelectSession: (id: number) => void;
  onNewSession: () => void;
}

export default function Sidebar({ sessions, activeSession, onSelectSession, onNewSession }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');

  const getIcon = (title: string) => {
    const t = title.toLowerCase();
    if (t.includes('mock') || t.includes('interview')) return <List className="w-4 h-4 text-warning" />;
    if (t.includes('quiz')) return <Brain className="w-4 h-4 text-accentLight" />;
    if (t.includes('resume')) return <FileText className="w-4 h-4 text-success" />;
    return <MessageSquare className="w-4 h-4 text-textMuted" />;
  };

  const filteredSessions = sessions.filter(s => {
    if (search && !s.title.toLowerCase().includes(search.toLowerCase())) return false;
    if (filter === 'All') return true;
    if (filter === 'Chat' && !s.title.toLowerCase().match(/(mock|quiz|resume|interview)/)) return true;
    if (filter === 'Mock' && s.title.toLowerCase().match(/(mock|interview)/)) return true;
    if (filter === 'Quiz' && s.title.toLowerCase().includes('quiz')) return true;
    if (filter === 'Resume' && s.title.toLowerCase().includes('resume')) return true;
    return false;
  });

  return (
    <div className="w-64 bg-bgSurface border-r border-borderC h-full flex flex-col hidden md:flex">
      <div className="p-4 border-b border-borderC space-y-2">
        <button 
          onClick={() => navigate('/dashboard')}
          className={`w-full font-semibold py-2 px-4 rounded transition-colors flex items-center ${location.pathname === '/dashboard' ? 'bg-accent text-white' : 'text-textMain hover:bg-bgCard'}`}
        >
          <LayoutDashboard className="w-4 h-4 mr-2" /> Dashboard
        </button>
        <button 
          onClick={() => navigate('/chat')}
          className={`w-full font-semibold py-2 px-4 rounded transition-colors flex items-center ${location.pathname === '/chat' ? 'bg-accent text-white' : 'text-textMain hover:bg-bgCard'}`}
        >
          <MessageSquare className="w-4 h-4 mr-2" /> Chat
        </button>
        <button 
          onClick={() => navigate('/interview')}
          className={`w-full font-semibold py-2 px-4 rounded transition-colors flex items-center ${location.pathname.includes('/interview') ? 'bg-accent text-white' : 'text-textMain hover:bg-bgCard'}`}
        >
          <List className="w-4 h-4 mr-2" /> Interviews
        </button>
        <button 
          onClick={() => navigate('/quiz')}
          className={`w-full font-semibold py-2 px-4 rounded transition-colors flex items-center ${location.pathname.includes('/quiz') ? 'bg-accent text-white' : 'text-textMain hover:bg-bgCard'}`}
        >
          <Brain className="w-4 h-4 mr-2" /> Quizzes
        </button>
        <button 
          onClick={() => navigate('/resume')}
          className={`w-full font-semibold py-2 px-4 rounded transition-colors flex items-center ${location.pathname.includes('/resume') ? 'bg-accent text-white' : 'text-textMain hover:bg-bgCard'}`}
        >
          <FileText className="w-4 h-4 mr-2" /> Resume Analyzer
        </button>
      </div>

      {location.pathname === '/chat' && (
        <div className="flex flex-col flex-1 overflow-hidden">
          <div className="p-4 border-b border-borderC space-y-3">
            <button 
              onClick={onNewSession}
              className="w-full bg-accent/10 hover:bg-accent/20 text-accent font-semibold py-2 px-4 rounded transition-colors flex items-center justify-center"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              New Chat
            </button>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-textMuted" />
              <input 
                type="text" 
                placeholder="Search history..." 
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-bgCard border border-borderC rounded-full pl-9 pr-4 py-1.5 text-sm text-textMain focus:outline-none focus:border-accent"
              />
            </div>
            <div className="flex gap-1 overflow-x-auto no-scrollbar pb-1">
              {['All', 'Chat', 'Mock', 'Quiz', 'Resume'].map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`text-[10px] px-2 py-1 rounded-full whitespace-nowrap ${filter === f ? 'bg-accent text-white' : 'bg-bgCard text-textMuted hover:text-white'}`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {filteredSessions.map(s => (
              <div 
                key={s.id}
                onClick={() => onSelectSession(s.id)}
                className={`p-3 cursor-pointer border-b border-borderC/50 hover:bg-bgCard transition-colors flex gap-3 ${
                  activeSession === s.id ? 'bg-bgCard border-l-2 border-l-accent' : ''
                }`}
              >
                <div className="mt-1">{getIcon(s.title)}</div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm text-textMain truncate font-medium">{s.title || 'New Chat'}</div>
                  <div className="text-xs text-textMuted mt-1">
                    {new Date(s.last_message_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
