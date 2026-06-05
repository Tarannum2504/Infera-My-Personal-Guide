import React, { useState } from 'react';
import api from '../services/api';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { LogOut, CheckCircle } from 'lucide-react';

export default function QuizPage() {
  const { user, logout } = useAuth();
  
  const [topic, setTopic] = useState('SQL');
  const [session, setSession] = useState<any>(null);
  
  const [answer, setAnswer] = useState('');
  const [questionNum, setQuestionNum] = useState(1);
  const [currentQuestion, setCurrentQuestion] = useState('');
  
  const [lastResult, setLastResult] = useState<any>(null);
  const [isFinished, setIsFinished] = useState(false);

  const startQuiz = async () => {
    try {
      const res = await api.post('/quiz/start', { topic });
      setSession(res.data);
      setCurrentQuestion(res.data.question_1);
      setQuestionNum(1);
      setLastResult(null);
      setIsFinished(false);
    } catch (e) {
      console.error(e);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim() || !session) return;
    try {
      const res = await api.post('/quiz/answer', {
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
            INFERA <span className="text-xs text-textMuted ml-2 font-normal">QUIZ ENGINE</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-textMain font-medium">{user?.full_name}</span>
            <button onClick={logout} className="text-textMuted hover:text-danger"><LogOut className="w-5 h-5" /></button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto">
            {!session ? (
              <div className="bg-bgSurface p-8 rounded-lg shadow-xl border border-borderC">
                <h2 className="text-2xl font-bold mb-6">Start a Knowledge Quiz</h2>
                <div className="mb-6">
                  <label className="block text-sm text-textMuted mb-2">Topic</label>
                  <select 
                    value={topic} onChange={(e) => setTopic(e.target.value)}
                    className="w-full bg-bgCard border border-borderC rounded p-3 text-white focus:outline-none focus:border-accent"
                  >
                    <option>SQL</option>
                    <option>Python</option>
                    <option>Statistics</option>
                    <option>Power BI</option>
                    <option>Azure</option>
                    <option>Business Analytics</option>
                  </select>
                </div>
                <button 
                  onClick={startQuiz}
                  className="w-full bg-accent hover:bg-accent/90 text-white font-bold py-3 rounded transition-colors"
                >
                  START QUIZ
                </button>
              </div>
            ) : isFinished ? (
              <div className="text-center bg-bgSurface p-8 rounded-lg shadow-xl border border-borderC">
                <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
                <h2 className="text-3xl font-bold mb-2">Quiz Complete</h2>
                <p className="text-xl text-textMuted mb-6">{lastResult?.summary}</p>
                <button onClick={() => setSession(null)} className="bg-accent px-6 py-2 rounded font-bold">New Quiz</button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex justify-between items-center text-sm font-bold text-textMuted uppercase tracking-wider">
                  <span>Question {questionNum} of {session.total}</span>
                </div>
                
                <h2 className="text-2xl font-semibold text-white leading-relaxed">
                  {currentQuestion}
                </h2>
                
                <input
                  type="text"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your brief answer..."
                  className="w-full bg-bgSurface border border-borderC rounded p-4 text-white focus:outline-none focus:border-accent"
                  onKeyDown={(e) => e.key === 'Enter' && submitAnswer()}
                />
                
                <div className="flex justify-end">
                  <button 
                    onClick={submitAnswer}
                    disabled={!answer.trim()}
                    className="bg-accent hover:bg-accent/90 disabled:bg-borderC text-white font-bold py-2 px-8 rounded"
                  >
                    Submit Answer
                  </button>
                </div>

                {lastResult && (
                  <div className="mt-8 bg-bgSurface p-6 rounded border border-borderC">
                    <h3 className="font-bold text-accent mb-2">PREVIOUS ANSWER RESULT</h3>
                    <div className="mb-4">
                      <span className="font-bold text-white text-lg">{lastResult.score}/10 points</span>
                    </div>
                    <div className="bg-bgCard p-4 rounded text-sm text-textMuted">
                      <span className="text-success font-bold">Correct Answer: </span>
                      {lastResult.correct_answer}
                      <p className="mt-2 text-xs">{lastResult.explanation}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
