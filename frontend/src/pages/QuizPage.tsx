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
  const [nextQuestionText, setNextQuestionText] = useState('');
  
  const [lastResult, setLastResult] = useState<any>(null);
  const [isFinished, setIsFinished] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [lastUserAnswer, setLastUserAnswer] = useState('');
  const [quizReview, setQuizReview] = useState<any[]>([]);
  const [submitError, setSubmitError] = useState('');

  const startQuiz = async () => {
    try {
      const res = await api.post('/quiz/start', { topic });
      setSession(res.data);
      setCurrentQuestion(res.data.question_1);
      setQuestionNum(1);
      setLastResult(null);
      setIsFinished(false);
      setShowFeedback(false);
      setNextQuestionText('');
      setQuizReview([]);
      setSubmitError('');
    } catch (e) {
      console.error(e);
    }
  };

  const submitAnswer = async () => {
    if (!answer.trim() || !session) return;
    setSubmitError('');
    try {
      const res = await api.post('/quiz/answer', {
        session_id: session.session_id,
        question_num: questionNum,
        answer
      });
      
      setLastResult(res.data);
      setLastUserAnswer(answer);
      setAnswer('');
      setShowFeedback(true);
      
      // Override currentQuestion to precisely match the backend text just graded
      if (res.data.question_text) {
        setCurrentQuestion(res.data.question_text);
      }
      
      if (res.data.summary) {
        setIsFinished(true);
        if (res.data.quiz_review) {
          setQuizReview(res.data.quiz_review);
        }
      } else {
        setNextQuestionText(res.data.next_question);
      }
    } catch (e: any) {
      console.error(e);
      if (e.response && e.response.data && e.response.data.detail) {
        setSubmitError(e.response.data.detail);
      } else {
        setSubmitError("An error occurred while submitting.");
      }
    }
  };

  const nextQuestion = () => {
    setShowFeedback(false);
    if (!isFinished) {
      setCurrentQuestion(nextQuestionText);
      setQuestionNum(prev => prev + 1);
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
            ) : showFeedback ? (
              <div className="space-y-6 bg-bgSurface p-8 rounded-lg border border-borderC shadow-xl">
                <div className="flex justify-between items-center text-sm font-bold text-textMuted uppercase tracking-wider mb-2">
                  <span>Question {questionNum} of {session.total}</span>
                </div>
                <h2 className="text-xl font-semibold text-white leading-relaxed mb-6 pb-6 border-b border-borderC">
                  {currentQuestion}
                </h2>
                <h2 className="text-2xl font-bold text-white mb-2">Answer Feedback</h2>
                <div className="flex items-center gap-4 mb-6">
                  <span className="text-3xl font-black text-accent">{lastResult?.score ?? 0}<span className="text-xl text-textMuted font-medium">/10</span></span>
                  <span className="text-sm text-textMuted bg-bgCard px-3 py-1 rounded-full border border-borderC">
                    Score
                  </span>
                </div>
                
                <div className="space-y-4">
                  <div className="bg-danger/10 border border-danger/20 p-4 rounded-lg">
                    <h3 className="text-sm font-bold text-danger mb-1 uppercase">Your Answer:</h3>
                    <p className="text-white">{lastUserAnswer || <span className="italic">No answer provided.</span>}</p>
                  </div>
                  <div className="bg-success/10 border border-success/20 p-4 rounded-lg">
                    <h3 className="text-sm font-bold text-success mb-1 uppercase">Correct Answer:</h3>
                    <p className="text-white">{lastResult?.correct_answer}</p>
                  </div>
                  <div className="bg-bgCard border border-borderC p-4 rounded-lg">
                    <h3 className="text-sm font-bold text-accent mb-1 uppercase">Explanation:</h3>
                    <p className="text-textMuted text-sm whitespace-pre-wrap">{lastResult?.explanation}</p>
                  </div>
                </div>
                
                <div className="mt-8 flex justify-end">
                  {isFinished ? (
                    <button 
                      onClick={() => setShowFeedback(false)}
                      className="bg-accent hover:bg-accent/90 text-white font-bold py-3 px-8 rounded transition-colors"
                    >
                      View Final Results
                    </button>
                  ) : (
                    <button 
                      onClick={nextQuestion}
                      className="bg-accent hover:bg-accent/90 text-white font-bold py-3 px-8 rounded transition-colors"
                    >
                      Next Question
                    </button>
                  )}
                </div>
              </div>
            ) : isFinished ? (
              <div className="bg-bgSurface p-8 rounded-lg shadow-xl border border-borderC">
                <div className="text-center mb-8">
                  <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
                  <h2 className="text-3xl font-bold mb-2">Quiz Complete</h2>
                  <p className="text-xl text-textMuted whitespace-pre-wrap">{lastResult?.summary}</p>
                </div>
                
                {quizReview && quizReview.length > 0 && (
                  <div className="space-y-6 mt-8">
                    <h3 className="text-xl font-bold border-b border-borderC pb-2">Review Your Answers</h3>
                    {quizReview.map((item, idx) => (
                      <div key={idx} className="bg-bgCard p-4 rounded border border-borderC">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold">{idx + 1}. {item.question}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${item.score >= 7 ? 'bg-success/20 text-success' : item.score >= 4 ? 'bg-warning/20 text-warning' : 'bg-danger/20 text-danger'}`}>
                            {item.score}/10
                          </span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm mt-4">
                          <div className="bg-danger/10 p-3 rounded">
                            <span className="block text-danger font-bold mb-1">Your Answer:</span>
                            {item.user_answer || <span className="italic text-textMuted">No answer</span>}
                          </div>
                          <div className="bg-success/10 p-3 rounded">
                            <span className="block text-success font-bold mb-1">Correct Answer:</span>
                            {item.correct_answer}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="mt-8 text-center">
                  <button onClick={() => setSession(null)} className="bg-accent px-8 py-3 rounded font-bold hover:bg-accent/90">Start New Quiz</button>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex justify-between items-center text-sm font-bold text-textMuted uppercase tracking-wider">
                  <span>Question {questionNum} of {session.total}</span>
                </div>
                
                <h2 className="text-2xl font-semibold text-white leading-relaxed">
                  {currentQuestion}
                </h2>
                
                {submitError && (
                  <div className="bg-danger/20 border border-danger/50 text-danger px-4 py-2 rounded">
                    {submitError}
                  </div>
                )}
                
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your brief answer..."
                  className="w-full h-32 bg-bgSurface border border-borderC rounded p-4 text-white focus:outline-none focus:border-accent resize-none"
                />
                <div className="text-xs text-textMuted text-right">Click Submit Answer when done</div>
                
                <div className="flex justify-end">
                  <button 
                    onClick={submitAnswer}
                    disabled={!answer.trim()}
                    className="bg-accent hover:bg-accent/90 disabled:bg-borderC text-white font-bold py-2 px-8 rounded"
                  >
                    Submit Answer
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
