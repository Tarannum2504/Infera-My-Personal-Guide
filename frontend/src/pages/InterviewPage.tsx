import React, { useState, useEffect } from 'react';
import api from '../services/api';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { LogOut, CheckCircle, Mic, MicOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function InterviewPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [company, setCompany] = useState('Celebal');
  const [round, setRound] = useState('Round 2');
  const [session, setSession] = useState<any>(null);
  
  const [answer, setAnswer] = useState('');
  const [questionNum, setQuestionNum] = useState(1);
  const [currentQuestion, setCurrentQuestion] = useState('');
  
  const [lastResult, setLastResult] = useState<any>(null);
  const [isFinished, setIsFinished] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [isRecording, setIsRecording] = useState(false);

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Your browser does not support Speech Recognition. Please try Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-IN';

    recognition.onstart = () => setIsRecording(true);
    
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('');
      setAnswer(transcript);
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event.error);
      setIsRecording(false);
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognition.start();
  };
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    if (session && !isFinished && timeLeft > 0) {
      timer = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
    }
    return () => clearInterval(timer);
  }, [session, isFinished, timeLeft]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const startInterview = async () => {
    try {
      const res = await api.post('/interview/start', { company, round });
      setSession(res.data);
      setCurrentQuestion(res.data.question_1);
      setQuestionNum(1);
      setLastResult(null);
      setIsFinished(false);
      setTimeLeft(res.data.timer_minutes * 60);
    } catch (e) {
      console.error(e);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim() || !session) return;
    try {
      const res = await api.post('/interview/answer', {
        session_id: session.session_id,
        question_num: questionNum,
        answer
      });
      
      setLastResult(res.data);
      setAnswer('');
      
      if (res.data.summary) {
        setIsFinished(true);
      } else {
        setQuestionNum(prev => prev + 1);
        setCurrentQuestion(res.data.next_question);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex h-screen bg-bgPrimary">
      <Sidebar sessions={[]} activeSession={null} onSelectSession={() => {}} onNewSession={() => {}} />
      
      <div className="flex-1 flex flex-col">
        <header className="h-16 border-b border-borderC bg-bgSurface flex items-center justify-between px-6">
          <div className="font-bold text-xl tracking-wider text-accent">
            INFERA <span className="text-xs text-textMuted ml-2 font-normal">INTERVIEW ENGINE</span>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => navigate('/interview/history')} className="text-sm text-textMuted hover:text-white">History</button>
            <span className="text-textMain font-medium">{user?.full_name}</span>
            <button onClick={logout} className="text-textMuted hover:text-danger"><LogOut className="w-5 h-5" /></button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto">
            {!session ? (
              <div className="bg-bgSurface p-8 rounded-lg shadow-xl border border-borderC">
                <h2 className="text-2xl font-bold mb-6">Start a Mock Interview</h2>
                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div>
                    <label className="block text-sm text-textMuted mb-2">Target Company</label>
                    <select 
                      value={company} onChange={(e) => setCompany(e.target.value)}
                      className="w-full bg-bgCard border border-borderC rounded p-3 text-white focus:outline-none focus:border-accent"
                    >
                      <option>Celebal</option>
                      <option>TCS</option>
                      <option>Optum</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-textMuted mb-2">Round</label>
                    <select 
                      value={round} onChange={(e) => setRound(e.target.value)}
                      className="w-full bg-bgCard border border-borderC rounded p-3 text-white focus:outline-none focus:border-accent"
                    >
                      <option>Round 1 SQL</option>
                      <option>Round 2</option>
                      <option>Technical</option>
                    </select>
                  </div>
                </div>
                <button 
                  onClick={startInterview}
                  className="w-full bg-accent hover:bg-accent/90 text-white font-bold py-3 rounded transition-colors"
                >
                  START INTERVIEW
                </button>
              </div>
            ) : isFinished ? (
              <div className="text-center bg-bgSurface p-10 rounded-xl shadow-2xl border border-borderC max-w-2xl mx-auto animate-in fade-in zoom-in duration-500">
                <div className="w-24 h-24 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle className="w-12 h-12 text-success" />
                </div>
                <h2 className="text-3xl font-black mb-2 tracking-tight text-white">Interview Complete</h2>
                <div className="bg-bgCard p-6 rounded-lg mb-8 border border-borderC text-left">
                  <h3 className="font-bold text-accent mb-4 border-b border-borderC pb-2">Final Evaluation</h3>
                  <p className="text-textMain leading-relaxed whitespace-pre-wrap">{lastResult?.summary}</p>
                </div>
                <button onClick={() => setSession(null)} className="bg-accent hover:bg-accent/90 px-8 py-3 rounded-full font-bold transition-all shadow-lg hover:shadow-accent/20">Start New Interview</button>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative">
                <div className="lg:col-span-2 space-y-6">
                  <div className="bg-bgSurface p-6 rounded-xl border border-borderC shadow-sm">
                    <div className="flex justify-between items-center mb-4">
                      <div className="flex items-center gap-4">
                        <span className="text-sm font-bold text-textMuted uppercase tracking-wider">
                          Question {questionNum} of {session.total_questions}
                        </span>
                      </div>
                      <div className={`font-mono text-xl font-bold flex items-center px-3 py-1 rounded ${timeLeft < 300 ? 'text-danger bg-danger/10 animate-pulse' : 'text-accent bg-accent/10'}`}>
                        {formatTime(timeLeft)}
                      </div>
                    </div>
                    
                    <div className="w-full h-1.5 bg-bgCard rounded-full overflow-hidden mb-6">
                      <div className="h-full bg-accent transition-all duration-500" style={{ width: `${(questionNum / session.total_questions) * 100}%` }}></div>
                    </div>
                    
                    <h2 className="text-2xl font-semibold text-white leading-relaxed mb-6">
                      {currentQuestion}
                    </h2>
                    
                    <textarea
                      value={answer}
                      onChange={(e) => setAnswer(e.target.value)}
                      placeholder="Type your answer here as if speaking to the interviewer..."
                      className="w-full h-48 bg-bgCard border border-borderC rounded-lg p-4 text-white focus:outline-none focus:border-accent resize-none shadow-inner"
                    />
                    
                    <div className="flex justify-between items-center mt-4">
                      <button
                        type="button"
                        onClick={toggleRecording}
                        disabled={!session}
                        className={`p-3 rounded-full flex items-center justify-center transition-colors ${isRecording ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-bgCard text-textMuted hover:text-accent border border-borderC'}`}
                        title="Voice Input"
                      >
                        {isRecording ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
                      </button>
                      <button 
                        onClick={submitAnswer}
                        disabled={!answer.trim()}
                        className="bg-accent hover:bg-accent/90 disabled:bg-borderC text-white font-bold py-3 px-8 rounded-full shadow-lg transition-all"
                      >
                        Submit Answer
                      </button>
                    </div>
                  </div>
                </div>

                <div className="lg:col-span-1">
                  {lastResult && (
                    <div className="bg-bgSurface p-6 rounded-xl border border-borderC shadow-sm animate-in slide-in-from-right-8 duration-500 sticky top-4">
                      <div className="flex items-center justify-between mb-4 pb-2 border-b border-borderC">
                        <h3 className="font-bold text-accent tracking-wider text-sm uppercase">Previous Feedback</h3>
                        <div className={`px-2 py-1 rounded font-bold text-lg ${lastResult.score >= 7 ? 'bg-success/20 text-success' : lastResult.score >= 5 ? 'bg-warning/20 text-warning' : 'bg-danger/20 text-danger'}`}>
                          {lastResult.score}/10
                        </div>
                      </div>
                      <div className="mb-4">
                        <p className="text-textMain text-sm leading-relaxed bg-bgCard p-3 rounded">{lastResult.feedback}</p>
                      </div>
                      <div className="bg-accent/10 border border-accent/20 p-4 rounded-lg text-sm">
                        <span className="text-accent font-bold flex items-center mb-2">
                          <CheckCircle className="w-4 h-4 mr-1" /> Ideal Approach
                        </span>
                        <div className="text-textMuted leading-relaxed">{lastResult.improved_answer}</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
