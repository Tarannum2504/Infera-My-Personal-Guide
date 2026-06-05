import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import MessageBubble from '../components/MessageBubble';
import Sidebar from '../components/Sidebar';
import QuickActions from '../components/QuickActions';
import { useAuth } from '../context/AuthContext';
import { LogOut, Paperclip, Mic, MicOff } from 'lucide-react';

interface Message {
  id: number;
  role: 'user' | 'infera';
  content: string;
  imageUrl?: string;
}

interface Session {
  id: number;
  title: string;
  last_message_at: string;
}

export default function ChatPage() {
  const { user, logout } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSession, setActiveSession] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [attachmentFile, setAttachmentFile] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (activeSession) {
      fetchMessages(activeSession);
    } else {
      setMessages([]);
    }
  }, [activeSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchSessions = async () => {
    try {
      const res = await api.get('/chat/sessions');
      setSessions(res.data);
      if (res.data.length > 0 && !activeSession) {
        setActiveSession(res.data[0].id);
      }
    } catch (error) {
      console.error("Failed to fetch sessions", error);
    }
  };

  const fetchMessages = async (sessionId: number) => {
    try {
      const res = await api.get(`/chat/session/${sessionId}`);
      setMessages(res.data);
    } catch (error) {
      console.error("Failed to fetch messages", error);
    }
  };

  const handleSend = async (text: string = input) => {
    if (!text.trim() && !attachmentFile) return;
    
    let displayContent = text;
    let imageUrl: string | undefined;
    
    if (attachmentFile) {
      if (attachmentFile.type.startsWith('image/')) {
        imageUrl = URL.createObjectURL(attachmentFile);
      } else {
        displayContent = `<attachment name="${attachmentFile.name}"></attachment>\n\n` + text;
      }
    }
    
    const userMessage = { id: Date.now(), role: 'user' as const, content: displayContent.trim(), imageUrl };
    setMessages(prev => [...prev, userMessage]);
    
    setInput('');
    const fileToSend = attachmentFile;
    setAttachmentFile(null);
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('message', text || " ");
      if (activeSession) {
        formData.append('session_id', activeSession.toString());
      }
      if (fileToSend) {
        formData.append('file', fileToSend);
      }

      const res = await api.post('/chat/send', formData);
      
      const inferaMessage = { id: Date.now() + 1, role: 'infera' as const, content: res.data.infera_response };
      setMessages(prev => [...prev, inferaMessage]);
      
      if (!activeSession) {
        setActiveSession(res.data.session_id);
        fetchSessions();
      }
    } catch (error) {
      console.error("Failed to send message", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachmentFile(file);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

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
    recognition.lang = 'en-IN'; // Indian English, catches Hinglish well

    recognition.onstart = () => setIsRecording(true);
    
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('');
      
      // Update input as they speak, we can just set it directly or append
      // For simplicity, we just set the input to the current transcript if they are just starting,
      // or we could append. Let's just set it.
      setInput(transcript);
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

  return (
    <div className="flex h-screen bg-bgPrimary">
      <Sidebar 
        sessions={sessions} 
        activeSession={activeSession} 
        onSelectSession={setActiveSession}
        onNewSession={() => setActiveSession(null)}
      />
      
      <div className="flex-1 flex flex-col">
        <header className="h-16 border-b border-borderC bg-bgSurface flex items-center justify-between px-6">
          <div className="font-bold text-xl tracking-wider text-accent">
            INFERA <span className="text-xs text-textMuted ml-2 font-normal">v2.0</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-textMain font-medium">{user?.full_name}</span>
            <button onClick={logout} className="text-textMuted hover:text-danger transition-colors">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </header>
        
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto">
            {messages.length === 0 ? (
              <div className="text-center text-textMuted mt-20">
                <h2 className="text-2xl font-bold text-textMain mb-4">How can I help you today?</h2>
                <p>Select a quick action below to get started.</p>
              </div>
            ) : (
              messages.map(msg => <MessageBubble key={msg.id} msg={msg} />)
            )}
            {isLoading && (
              <div className="text-accent text-sm ml-4 mb-4 animate-pulse font-mono">
                Infera is computing...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        
        <div className="p-4 bg-bgSurface border-t border-borderC">
          <div className="max-w-3xl mx-auto">
            <QuickActions onActionClick={handleSend} />
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSend(); }}
              className="relative flex flex-col bg-bgCard border border-borderC rounded-lg p-1"
            >
              {attachmentFile && (
                <div className="flex flex-wrap gap-2 p-2 border-b border-borderC">
                  <div className="bg-bgSurface border border-borderC rounded flex items-center px-2 py-1 text-xs text-textMain">
                    <Paperclip className="w-3 h-3 mr-1 text-accent" />
                    <span className="truncate max-w-[150px]">{attachmentFile.name}</span>
                    <button 
                      type="button" 
                      onClick={() => setAttachmentFile(null)} 
                      className="ml-2 text-textMuted hover:text-danger"
                    >
                      ×
                    </button>
                  </div>
                </div>
              )}
              <div className="flex items-center w-full">
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileUpload} 
                  className="hidden" 
                  accept=".txt,.pdf,.docx,.doc,.jpg,.jpeg,.png,.webp"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  className="p-2 text-textMuted hover:text-accent disabled:opacity-50 transition-colors"
                  title="Attach Document or Image"
                >
                  <Paperclip className="w-5 h-5" />
                </button>
                
                <button
                  type="button"
                  onClick={toggleRecording}
                  disabled={isLoading}
                  className={`p-2 transition-colors ${isRecording ? 'text-red-500 animate-pulse' : 'text-textMuted hover:text-accent'} disabled:opacity-50`}
                  title="Voice Input"
                >
                  {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                </button>

                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask Infera or upload a file..."
                  className="flex-1 bg-transparent pl-2 pr-12 py-3 text-textMain focus:outline-none"
                  disabled={isLoading}
                />
                <button 
                  type="submit"
                  disabled={isLoading || (!input.trim() && !attachmentFile)}
                  className="absolute right-2 bottom-2 bg-accent hover:bg-accent/90 disabled:bg-borderC text-white rounded p-1.5 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
