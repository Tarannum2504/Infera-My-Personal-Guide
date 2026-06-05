import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Sidebar from '../components/Sidebar';
import api from '../services/api';
import { LogOut, ArrowUp, ArrowDown, TrendingUp, Target, Clock, CheckCircle, Circle, ArrowRight } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState<any>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const { data } = await api.get('/profile/dashboard-data');
        setDashboardData(data);
      } catch (e) {
        console.error(e);
      }
    };
    fetchDashboard();
  }, []);

  const handleProjectToggle = async (index: number) => {
    if (!dashboardData?.projects) return;
    const newProjects = [...dashboardData.projects];
    const p = newProjects[index];
    if (p.status === "not_started") p.status = "in_progress";
    else if (p.status === "in_progress") p.status = "completed";
    else if (p.status === "completed") p.status = "built";
    
    setDashboardData({ ...dashboardData, projects: newProjects });
    await api.put('/profile/projects', newProjects);
  };

  const skillData = [
    { subject: 'SQL', A: dashboardData?.skills?.SQL || 80, fullMark: 100 },
    { subject: 'Python', A: dashboardData?.skills?.Python || 65, fullMark: 100 },
    { subject: 'Power BI', A: dashboardData?.skills?.['Power BI'] || 20, fullMark: 100 },
    { subject: 'Azure', A: dashboardData?.skills?.Azure || 15, fullMark: 100 },
    { subject: 'Stats', A: dashboardData?.skills?.Statistics || 40, fullMark: 100 },
    { subject: 'DBMS', A: dashboardData?.skills?.DBMS || 70, fullMark: 100 },
    { subject: 'Comm', A: dashboardData?.skills?.Communication || 85, fullMark: 100 },
  ];

  const skillBars = [
    { name: 'SQL', score: dashboardData?.skills?.SQL || 80, status: '+5 this week', color: 'bg-success' },
    { name: 'Python', score: dashboardData?.skills?.Python || 65, status: 'stable', color: 'bg-accent' },
    { name: 'Power BI', score: dashboardData?.skills?.['Power BI'] || 20, status: 'CRITICAL', color: 'bg-danger' },
    { name: 'Statistics', score: dashboardData?.skills?.Statistics || 40, status: 'Gap', color: 'bg-warning' },
    { name: 'Azure', score: dashboardData?.skills?.Azure || 15, status: 'Gap', color: 'bg-warning' },
    { name: 'Databricks', score: dashboardData?.skills?.Databricks || 5, status: 'Not started', color: 'bg-borderC' },
  ];

  const sprint = dashboardData?.sprint || { week: 1, completion_pct: 33, days_remaining: 34, total_weeks: 12 };
  const projects = dashboardData?.projects || [];

  return (
    <div className="flex h-screen bg-bgPrimary overflow-hidden">
      <Sidebar sessions={[]} activeSession={null} onSelectSession={() => {}} onNewSession={() => {}} />
      
      <div className="flex-1 flex flex-col overflow-y-auto">
        <header className="h-16 border-b border-borderC bg-bgSurface flex items-center justify-between px-6 sticky top-0 z-10">
          <div className="font-bold text-xl tracking-wider text-accent">
            Infera <span className="text-xs text-textMuted ml-2 font-normal">DASHBOARD</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-textMain font-medium">{user?.full_name}</span>
            <button onClick={logout} className="text-textMuted hover:text-danger transition-colors">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </header>
        
        <div className="p-4 md:p-8 max-w-7xl mx-auto w-full space-y-8">
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm flex flex-col justify-between">
              <div className="text-textMuted text-sm font-semibold tracking-wider mb-2">OVERALL READINESS</div>
              <div className="flex items-end justify-between">
                <div className="text-4xl font-black text-white">72<span className="text-xl text-textMuted font-medium">/100</span></div>
                <div className="w-12 h-12 rounded-full border-4 border-success flex items-center justify-center">
                  <TrendingUp className="text-success w-5 h-5" />
                </div>
              </div>
            </div>

            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm flex flex-col justify-between">
              <div className="text-textMuted text-sm font-semibold tracking-wider mb-2">CELEBAL READINESS</div>
              <div className="flex items-end justify-between">
                <div className="text-4xl font-black text-white">70<span className="text-xl text-textMuted font-medium">/100</span></div>
                <div className="flex items-center text-success font-bold text-sm bg-success/20 px-2 py-1 rounded">
                  <ArrowUp className="w-4 h-4 mr-1" /> 5%
                </div>
              </div>
            </div>

            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm flex flex-col justify-between">
              <div className="text-textMuted text-sm font-semibold tracking-wider mb-2">TCS READINESS</div>
              <div className="flex items-end justify-between">
                <div className="text-4xl font-black text-white">82<span className="text-xl text-textMuted font-medium">/100</span></div>
                <div className="flex items-center text-success font-bold text-sm bg-success/20 px-2 py-1 rounded">
                  <ArrowUp className="w-4 h-4 mr-1" /> 2%
                </div>
              </div>
            </div>

            <div className="bg-bgSurface border border-danger/50 rounded-xl p-6 shadow-sm flex flex-col justify-between relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-danger"></div>
              <div className="text-textMuted text-sm font-semibold tracking-wider mb-2">OPTUM READINESS</div>
              <div className="flex items-end justify-between">
                <div className="text-4xl font-black text-danger">48<span className="text-xl text-textMuted font-medium">/100</span></div>
                <div className="flex items-center text-danger font-bold text-sm bg-danger/20 px-2 py-1 rounded">
                  <ArrowDown className="w-4 h-4 mr-1" /> 1%
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-bold text-white mb-6">Skill Radar</h3>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={skillData}>
                    <PolarGrid stroke="#374151" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#4B5563' }} />
                    <Radar name="Skills" dataKey="A" stroke="#6366F1" fill="#6366F1" fillOpacity={0.4} />
                    <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-bold text-white mb-6">Skill Breakdown</h3>
              <div className="space-y-5">
                {skillBars.map((skill, i) => (
                  <div key={i}>
                    <div className="flex justify-between items-end mb-1">
                      <span className="text-sm font-medium text-white">{skill.name}</span>
                      <div className="text-xs">
                        <span className="text-white font-mono mr-2">{skill.score}/100</span>
                        <span className={`${skill.status === 'CRITICAL' ? 'text-danger font-bold' : skill.status.includes('+') ? 'text-success' : 'text-textMuted'}`}>
                          [{skill.status}]
                        </span>
                      </div>
                    </div>
                    <div className="w-full h-2.5 bg-bgCard rounded-full overflow-hidden">
                      <div className={`h-full ${skill.color}`} style={{ width: `${skill.score}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-bold text-white">Sprint Progress</h3>
                <span className="bg-accent/20 text-accent text-xs px-2 py-1 rounded font-bold">Week {sprint.week} of {sprint.total_weeks}</span>
              </div>
              
              <div className="mb-6">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-textMuted">Overall Completion</span>
                  <span className="text-white font-bold">{sprint.completion_pct}%</span>
                </div>
                <div className="w-full h-3 bg-bgCard rounded-full overflow-hidden mb-2">
                  <div className="h-full bg-accent" style={{ width: `${sprint.completion_pct}%` }}></div>
                </div>
                <div className="text-xs text-textMuted text-right">{sprint.days_remaining} days remaining</div>
              </div>

              <div className="bg-bgCard p-4 rounded-lg border border-borderC">
                <h4 className="text-sm font-bold text-textMuted mb-3 uppercase tracking-wider">Projects Checklist</h4>
                <div className="space-y-3">
                  {projects.map((p: any, i: number) => (
                    <div key={i} className="flex items-center text-sm cursor-pointer hover:bg-bgSurface p-1 rounded" onClick={() => handleProjectToggle(i)}>
                      {p.status === "built" || p.status === "completed" ? (
                        <CheckCircle className="w-5 h-5 text-success mr-3" />
                      ) : p.status === "in_progress" ? (
                        <Clock className="w-5 h-5 text-warning mr-3" />
                      ) : (
                        <Circle className="w-5 h-5 text-borderC mr-3" />
                      )}
                      <span className={p.status === "built" || p.status === "completed" ? "text-textMuted line-through" : p.status === "in_progress" ? "text-white font-medium" : "text-textMuted"}>
                        {p.name} ({p.status.replace('_', ' ')})
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-bold text-white mb-6">Mock Interview Trend</h3>
              {!dashboardData?.has_mock_data ? (
                <div style={{textAlign:'center', color:'#9CA3AF', padding:'40px'}}>
                  <p>No mock interviews taken yet.</p>
                  <p>Go to Interviews → Start your first mock.</p>
                  <p>Your trend will appear here after completion.</p>
                </div>
              ) : (
                <div className="h-[250px] w-full mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={dashboardData.mock_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                      <XAxis dataKey="label" stroke="#9CA3AF" tick={{ fontSize: 12 }} />
                      <YAxis stroke="#9CA3AF" tick={{ fontSize: 12 }} />
                      <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
                      <Bar dataKey="score" fill="#6366F1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>

          <div className="bg-bgSurface border border-borderC rounded-xl p-6 shadow-sm">
            <div className="flex items-center mb-6">
              <Target className="text-accent w-6 h-6 mr-3" />
              <h3 className="text-xl font-bold text-white">This Week's Priority (60 min/day ROI)</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-bgCard border border-danger/30 rounded-lg p-5">
                <div className="flex justify-between items-start mb-3">
                  <span className="bg-danger/20 text-danger text-xs px-2 py-1 rounded font-bold border border-danger/30">CRITICAL PRIORITY</span>
                  <span className="text-textMuted text-sm"><Clock className="w-4 h-4 inline mr-1" />40m</span>
                </div>
                <h4 className="font-bold text-white mb-2">Build Power BI Sales Dashboard</h4>
                <p className="text-sm text-textMuted">Your Power BI score is holding you back from Optum and Celebal offers. Follow the MS Learn path and complete the primary dashboard.</p>
              </div>

              <div className="bg-bgCard border border-success/30 rounded-lg p-5">
                <div className="flex justify-between items-start mb-3">
                  <span className="bg-success/20 text-success text-xs px-2 py-1 rounded font-bold border border-success/30">HIGH ROI</span>
                  <span className="text-textMuted text-sm"><Clock className="w-4 h-4 inline mr-1" />10m</span>
                </div>
                <h4 className="font-bold text-white mb-2">Daily SQL Practice</h4>
                <p className="text-sm text-textMuted">Maintain your 80/100 score. Solve one medium-level JOIN or Window Function problem daily on LeetCode or HackerRank.</p>
              </div>

              <div className="bg-bgCard border border-borderC rounded-lg p-5">
                <div className="flex justify-between items-start mb-3">
                  <span className="bg-bgSurface text-textMuted text-xs px-2 py-1 rounded font-bold border border-borderC">MAINTENANCE</span>
                  <span className="text-textMuted text-sm"><Clock className="w-4 h-4 inline mr-1" />10m</span>
                </div>
                <h4 className="font-bold text-white mb-2">Review Python Concepts</h4>
                <p className="text-sm text-textMuted">Quickly review Object Oriented Programming concepts to ensure you are ready for technical rounds.</p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
