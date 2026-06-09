import React, { useEffect, useState } from 'react';
import api from '../services/api';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { Database, Search, Clock, ShieldCheck } from 'lucide-react';

export default function MemoryDebugPage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    api.get('/profile').then((res) => {
      setProfile(res.data);
    }).catch(console.error);
  }, []);

  return (
    <div className="flex h-screen bg-bgPrimary">
      <Sidebar sessions={[]} activeSession={null} onSelectSession={() => {}} onNewSession={() => {}} />
      
      <div className="flex-1 flex flex-col">
        <header className="h-16 border-b border-borderC bg-bgSurface flex items-center px-6">
          <Database className="w-6 h-6 text-accent mr-3" />
          <div className="font-bold text-xl tracking-wider text-white">
            MEMORY INSPECTOR <span className="text-xs text-danger ml-2 font-bold px-2 py-1 bg-danger/20 rounded">DEVELOPER TOOLS</span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto space-y-6">
            
            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <ShieldCheck className="w-5 h-5 text-success mr-2" />
                Session Info
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-bgCard p-4 rounded">
                  <div className="text-textMuted text-xs font-bold mb-1 uppercase">User ID</div>
                  <div className="text-white font-mono">{user?.id || 'Unknown'}</div>
                </div>
                <div className="bg-bgCard p-4 rounded">
                  <div className="text-textMuted text-xs font-bold mb-1 uppercase">Name</div>
                  <div className="text-white font-mono">{user?.full_name || 'Unknown'}</div>
                </div>
              </div>
            </div>

            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center">
                <Search className="w-5 h-5 text-accent mr-2" />
                Structured Memory Dump (JSON)
              </h2>
              
              {!profile ? (
                <div className="text-textMuted">Loading memory database...</div>
              ) : (
                <div className="space-y-4">
                  {Object.keys(profile.memory_notes || {}).length === 0 ? (
                    <div className="bg-bgCard p-4 rounded text-textMuted italic">
                      No verified memory facts stored for this user.
                    </div>
                  ) : (
                    Object.entries(profile.memory_notes).map(([key, value]) => (
                      <div key={key} className="bg-bgCard border border-borderC rounded p-4 flex flex-col md:flex-row md:items-center justify-between">
                        <div className="flex-1">
                          <span className="text-accent font-bold font-mono mr-3">{key}:</span>
                          <span className="text-white font-medium">{String(value)}</span>
                        </div>
                        <div className="text-xs text-textMuted mt-2 md:mt-0 flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          Source: Memory DB
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm">
              <h2 className="text-xl font-bold text-white mb-4">Raw Profile State</h2>
              <pre className="bg-bgCard p-4 rounded text-xs text-textMuted overflow-auto font-mono">
                {JSON.stringify(profile, null, 2)}
              </pre>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
