import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import ChatPage from './pages/ChatPage';
import DashboardPage from './pages/DashboardPage';
import InterviewPage from './pages/InterviewPage';
import InterviewHistoryPage from './pages/InterviewHistoryPage';
import QuizPage from './pages/QuizPage';
import ResumePage from './pages/ResumePage';
import MemoryDebugPage from './pages/MemoryDebugPage';
import { useAuth } from './context/AuthContext';

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/chat" />} />
        
        {/* Protected Routes */}
        <Route path="/chat" element={isAuthenticated ? <ChatPage /> : <Navigate to="/login" />} />
        <Route path="/dashboard" element={isAuthenticated ? <DashboardPage /> : <Navigate to="/login" />} />
        <Route path="/interview" element={isAuthenticated ? <InterviewPage /> : <Navigate to="/login" />} />
        <Route path="/interview/history" element={isAuthenticated ? <InterviewHistoryPage /> : <Navigate to="/login" />} />
        <Route path="/quiz" element={isAuthenticated ? <QuizPage /> : <Navigate to="/login" />} />
        <Route path="/resume" element={isAuthenticated ? <ResumePage /> : <Navigate to="/login" />} />
        <Route path="/memory-debug" element={isAuthenticated ? <MemoryDebugPage /> : <Navigate to="/login" />} />
        
        <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
