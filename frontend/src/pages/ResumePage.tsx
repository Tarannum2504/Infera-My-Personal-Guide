import React, { useState } from 'react';
import api from '../services/api';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { LogOut, FileSearch } from 'lucide-react';

export default function ResumePage() {
  const { user, logout } = useAuth();
  
  const [resumeText, setResumeText] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [company, setCompany] = useState('Celebal');
  const [analysis, setAnalysis] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const analyzeResume = async () => {
    if (!resumeText.trim() && !resumeFile) return;
    setIsLoading(true);
    try {
      let res;
      if (resumeFile) {
        const formData = new FormData();
        formData.append('file', resumeFile);
        formData.append('company', company);
        res = await api.post('/resume/analyze_file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else {
        res = await api.post('/resume/analyze', { resume_text: resumeText, company });
      }
      
      if (res.data && res.data.error) {
        alert(res.data.error);
        setAnalysis(null);
      } else {
        setAnalysis(res.data);
      }
    } catch (e) {
      console.error(e);
      alert("An error occurred during analysis.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-bgPrimary">
      <Sidebar sessions={[]} activeSession={null} onSelectSession={() => {}} onNewSession={() => {}} />
      
      <div className="flex-1 flex flex-col">
        <header className="h-16 border-b border-borderC bg-bgSurface flex items-center justify-between px-6">
          <div className="font-bold text-xl tracking-wider text-accent">
            INFERA <span className="text-xs text-textMuted ml-2 font-normal">RESUME INTELLIGENCE</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-textMain font-medium">{user?.full_name}</span>
            <button onClick={logout} className="text-textMuted hover:text-danger"><LogOut className="w-5 h-5" /></button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Input Section */}
            <div className="bg-bgSurface p-6 rounded-lg shadow-xl border border-borderC flex flex-col h-[80vh]">
              <h2 className="text-xl font-bold mb-4">Resume Input</h2>
              <div className="mb-4">
                <label className="block text-sm text-textMuted mb-2">Target Company</label>
                <select 
                  value={company} onChange={(e) => setCompany(e.target.value)}
                  className="w-full bg-bgCard border border-borderC rounded p-3 text-white focus:outline-none focus:border-accent"
                >
                  <option>Celebal</option>
                  <option>TCS Digital</option>
                  <option>Optum</option>
                  <option>Deloitte</option>
                  <option>Publicis Sapient</option>
                  <option>Mediaocean</option>
                  <option>Data Analytics (General)</option>
                </select>
              </div>
              <div className="flex-1 flex flex-col mb-4">
                <label className="block text-sm text-textMuted mb-2">Resume Document (.pdf, .docx) or Plain Text</label>
                <input 
                  type="file" 
                  accept=".pdf,.docx,.txt"
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      setResumeFile(e.target.files[0]);
                      setResumeText('');
                    }
                  }}
                  className="mb-3 block w-full text-sm text-textMuted file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-accent file:text-white hover:file:bg-accent/90"
                />
                <div className="text-center text-xs text-textMuted mb-2">OR PASTE TEXT</div>
                <textarea
                  value={resumeText}
                  onChange={(e) => {
                    setResumeText(e.target.value);
                    setResumeFile(null);
                  }}
                  placeholder={resumeFile ? `Selected file: ${resumeFile.name}` : "Paste your plain text resume here..."}
                  disabled={!!resumeFile}
                  className="flex-1 w-full bg-bgCard border border-borderC rounded p-4 text-white focus:outline-none focus:border-accent font-mono text-sm resize-none"
                />
              </div>
              <button 
                onClick={analyzeResume}
                disabled={(!resumeText.trim() && !resumeFile) || isLoading}
                className="w-full bg-accent hover:bg-accent/90 disabled:bg-borderC text-white font-bold py-3 rounded transition-colors flex items-center justify-center"
              >
                {isLoading ? 'Analyzing...' : <><FileSearch className="w-5 h-5 mr-2" /> Analyze Resume</>}
              </button>
            </div>

            {/* Results Section */}
            <div className="bg-bgSurface p-6 rounded-lg shadow-xl border border-borderC overflow-y-auto h-[80vh]">
              <h2 className="text-xl font-bold mb-6 text-white tracking-wide">Analysis Results</h2>
              
              {!analysis ? (
                <div className="flex flex-col items-center justify-center h-full text-textMuted opacity-50">
                  <FileSearch className="w-16 h-16 mb-4" />
                  <p>Awaiting resume text...</p>
                </div>
              ) : (
                <div className="space-y-8 animate-in fade-in duration-500">
                  
                  {/* Top Scores */}
                  <div className="flex items-center justify-between bg-bgCard p-6 rounded-xl border border-borderC">
                    <div className="flex items-center gap-6">
                      <div className="relative w-32 h-32">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                          <circle cx="50" cy="50" r="45" fill="none" stroke="#374151" strokeWidth="8" />
                          <circle cx="50" cy="50" r="45" fill="none" stroke={analysis.ats_score > 70 ? '#10B981' : analysis.ats_score > 50 ? '#F59E0B' : '#EF4444'} strokeWidth="8" strokeDasharray={`${analysis.ats_score * 2.827} 282.7`} strokeLinecap="round" className="transition-all duration-1000 ease-out" />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          <span className="text-3xl font-black text-white">{analysis.ats_score}</span>
                          <span className="text-[10px] text-textMuted uppercase tracking-widest font-bold">Score</span>
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-textMuted font-bold uppercase tracking-widest mb-1">Current ATS Fit</div>
                        <div className="text-white font-medium">Based on 100-point scale</div>
                      </div>
                    </div>
                    
                    <div className="text-right bg-success/10 border border-success/30 p-4 rounded-xl">
                      <div className="text-sm font-bold text-success uppercase tracking-widest mb-1">If You Fix {analysis.issues.length} Things:</div>
                      <div className="text-4xl font-black text-success">{analysis.if_fixed_score}<span className="text-xl text-success/70">/100</span></div>
                    </div>
                  </div>

                  {/* Section Breakdown */}
                  <div>
                    <h3 className="text-sm font-bold text-textMuted uppercase tracking-widest mb-4">Score Breakdown</h3>
                    <div className="space-y-4">
                      {[
                        { label: 'Keywords', score: analysis.breakdown.keywords, max: 30 },
                        { label: 'Action Verbs', score: analysis.breakdown.action_verbs, max: 10 },
                        { label: 'Format', score: analysis.breakdown.format, max: 20 },
                        { label: 'Projects', score: analysis.breakdown.projects, max: 25 },
                        { label: 'Certifications', score: analysis.breakdown.certifications, max: 10 },
                        { label: 'GitHub', score: analysis.breakdown.github, max: 5 },
                      ].map(sec => (
                        <div key={sec.label}>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="text-white font-medium">{sec.label}</span>
                            <span className="text-textMuted font-mono">{sec.score}/{sec.max}</span>
                          </div>
                          <div className="w-full h-2 bg-bgCard rounded-full overflow-hidden">
                            <div className="h-full bg-accent" style={{ width: `${(sec.score / sec.max) * 100}%` }}></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Critical Issues */}
                  {analysis.issues.length > 0 && (
                    <div>
                      <h3 className="text-sm font-bold text-danger uppercase tracking-widest mb-4">Critical Issues Detected</h3>
                      <div className="space-y-3">
                        {analysis.issues.map((issue: string, i: number) => (
                          <div key={i} className="bg-danger/10 border-l-4 border-danger p-4 rounded-r-lg flex items-start">
                            <span className="text-danger font-black mr-3 text-lg leading-none">!</span>
                            <span className="text-danger font-medium text-sm">{issue}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Before / After */}
                  {analysis.before_after.length > 0 && (
                    <div>
                      <h3 className="text-sm font-bold text-success uppercase tracking-widest mb-4">Suggested Revisions</h3>
                      <div className="space-y-4">
                        {analysis.before_after.map((ex: any, i: number) => (
                          <div key={i} className="grid grid-cols-2 gap-4">
                            <div className="bg-danger/5 border border-danger/20 p-4 rounded-lg">
                              <div className="text-xs font-bold text-danger uppercase mb-2 border-b border-danger/20 pb-1">Current (Weak)</div>
                              <div className="text-sm text-textMuted line-through">{ex.before}</div>
                            </div>
                            <div className="bg-success/5 border border-success/20 p-4 rounded-lg">
                              <div className="text-xs font-bold text-success uppercase mb-2 border-b border-success/20 pb-1">Suggested (Strong)</div>
                              <div className="text-sm text-white font-medium">{ex.after}</div>
                            </div>
                            <div className="col-span-2 text-xs text-textMuted mt-1 mb-2 italic">
                              <span className="font-bold text-accent">Reasoning: </span>{ex.reason}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                </div>
              )}
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
