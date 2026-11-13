import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  X, 
  Send, 
  Trash2, 
  Volume2, 
  VolumeX, 
  Sparkles, 
  Bot, 
  User, 
  Key, 
  HelpCircle, 
  CheckCircle2, 
  AlertCircle,
  Briefcase,
  Layers,
  ArrowRight,
  RefreshCw,
  Terminal,
  Zap,
  Mic,
  Maximize2,
  Minimize2,
  Edit3,
  Check
} from 'lucide-react';
import JarvisVisualizer from './JarvisVisualizer';
import { api, jarvisSessionStore } from '../../services/api';

export default function JarvisChatPanel({ isOpen, onClose, contextReport, onUpdateCandidateName }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  // Status & Key Configuration State
  const [jarvisStatus, setJarvisStatus] = useState(null);
  const [showKeyConfig, setShowKeyConfig] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const [configMessage, setConfigMessage] = useState(null);

  // Name Editing State
  const [isEditingName, setIsEditingName] = useState(false);
  const [customNameInput, setCustomNameInput] = useState('');

  // Interview state
  const [interviewState, setInterviewState] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Load status and welcome message on open
  useEffect(() => {
    if (isOpen) {
      const storedKey = jarvisSessionStore.getKey();
      const storedProvider = jarvisSessionStore.getProvider();
      if (storedKey) {
        setApiKeyInput(storedKey);
        setSelectedProvider(storedProvider);
      }

      api.jarvisGetStatus()
        .then((st) => {
          if (storedKey) {
            setJarvisStatus({
              ...st,
              mode: 'live_api',
              provider: storedProvider.toUpperCase(),
              has_key: true,
              description: `Connected to ${storedProvider.toUpperCase()} cloud neural model (Browser Session).`
            });
          } else {
            setJarvisStatus(st);
          }
        })
        .catch((err) => console.error('Failed to get JARVIS status:', err));

      if (messages.length === 0) {
        initWelcomeMessage();
      }
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  const initWelcomeMessage = () => {
    const candidateName = contextReport?.candidate_name || 'Sir';
    const jobTitle = contextReport?.job_title || 'Target Role';
    const company = contextReport?.job_company || 'your target company';
    const score = contextReport?.overall_score ? Math.round(contextReport.overall_score) : null;

    let greeting = `Good to see you, **${candidateName}**. I am **J.A.R.V.I.S.**, your personal AI career strategist.\n\n`;
    if (score) {
      greeting += `I have actively ingested your CareerSetu profile for **${jobTitle}** at **${company}** (ATS Score: **${score}/100**).\n\n`;
    } else {
      greeting += `I am standing by to assist with resume optimization, technical interview practice, and skill roadmaps.\n\n`;
    }
    greeting += `What shall we focus on today?`;

    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: greeting,
        suggested_replies: [
          'Analyze my resume for this role',
          'What critical skills am I missing?',
          'Start an interactive mock interview',
          'Create a 30-day learning roadmap'
        ]
      }
    ]);
  };

  // Text-To-Speech handler
  const speakText = (text) => {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    try {
      window.speechSynthesis.cancel();
      // Clean markdown symbols for cleaner speech
      const clean = text.replace(/[*#`>_-]/g, ' ').replace(/\s+/g, ' ').trim();
      const utterance = new SpeechSynthesisUtterance(clean);
      utterance.rate = 1.05;
      utterance.pitch = 0.95;
      
      // Try to find a British or deep male English voice
      const voices = window.speechSynthesis.getVoices();
      const preferred = voices.find(v => v.lang.includes('en-GB') || v.name.includes('Daniel') || v.name.includes('George'));
      if (preferred) utterance.voice = preferred;

      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
    } catch (e) {
      setIsSpeaking(false);
    }
  };

  // Send message to JARVIS backend
  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;

    setInputMessage('');
    const userMsg = { id: Date.now().toString(), role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await api.jarvisChat({
        message: text,
        conversationHistory: messages.slice(-20).map((m) => ({ role: m.role, content: m.content })),
        context: contextReport,
        interviewState: interviewState,
      });

      const assistantMsg = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.reply,
        mode: res.mode,
        provider: res.provider,
        suggested_replies: res.suggested_replies || []
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setInterviewState(res.interview_state || null);

      if (res.updated_name && onUpdateCandidateName) {
        onUpdateCandidateName(res.updated_name);
      }

      if (voiceEnabled) {
        speakText(res.reply);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `⚠️ **Diagnostic Alert:** Connection error (${err.message}). Running in safe offline diagnostics mode.`,
          isError: true,
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartInterview = async () => {
    setIsLoading(true);
    try {
      const res = await api.jarvisStartInterview(contextReport);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: res.reply,
          mode: res.mode,
          provider: res.provider,
          suggested_replies: res.suggested_replies || []
        }
      ]);
      setInterviewState(res.interview_state);
      if (voiceEnabled) speakText(res.reply);
    } catch (err) {
      alert(`Interview session error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setInterviewState(null);
    setMessages([]);
    initWelcomeMessage();
  };

  const handleSaveApiKey = async (e) => {
    e.preventDefault();
    try {
      const res = await api.jarvisConfigureKey({
        provider: selectedProvider,
        apiKey: apiKeyInput,
      });
      setConfigMessage(res.message);
      if (apiKeyInput && apiKeyInput.trim()) {
        setJarvisStatus({
          mode: 'live_api',
          provider: selectedProvider.toUpperCase(),
          has_key: true,
          description: `Connected to ${selectedProvider.toUpperCase()} cloud neural model (Browser Session).`
        });
      } else {
        const updatedStatus = await api.jarvisGetStatus();
        setJarvisStatus(updatedStatus);
      }
      setTimeout(() => {
        setShowKeyConfig(false);
        setConfigMessage(null);
      }, 1500);
    } catch (err) {
      setConfigMessage(`Failed to set key: ${err.message}`);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end animate-fade-in pointer-events-auto">
      {/* Dark backdrop */}
      <div 
        onClick={onClose}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" 
      />

      {/* Main JARVIS Panel */}
      <div 
        className={`relative z-10 w-full bg-[#060B15]/95 backdrop-blur-2xl border-l border-cyan-500/30 shadow-[0_0_50px_rgba(6,182,212,0.25)] flex flex-col justify-between text-slate-100 transition-all duration-300 ${
          isExpanded ? 'max-w-4xl' : 'max-w-xl'
        }`}
      >
        {/* Holographic Top Accent Bar */}
        <div className="h-1 bg-gradient-to-r from-cyan-600 via-cyan-400 to-blue-500 shadow-[0_0_15px_#06b6d4]" />

        {/* Panel Header */}
        <div className="p-4 border-b border-cyan-500/20 bg-[#091224]/80 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <JarvisVisualizer size="sm" isTyping={isLoading} isSpeaking={isSpeaking} />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-serif font-bold text-base tracking-wide text-cyan-300">
                  J.A.R.V.I.S.
                </span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-500/40 uppercase tracking-widest">
                  AI Mentor
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                <span>
                  {jarvisStatus?.has_key 
                    ? `Live Cloud AI (${jarvisStatus?.provider})` 
                    : 'Local Intelligence Engine (Demo Mode)'}
                </span>
              </div>
            </div>
          </div>

          {/* Header Action Icons */}
          <div className="flex items-center gap-1.5 text-slate-400">
            {/* Voice Toggle */}
            <button
              onClick={() => {
                const next = !voiceEnabled;
                setVoiceEnabled(next);
                if (!next && window.speechSynthesis) window.speechSynthesis.cancel();
              }}
              className={`p-2 rounded-lg transition-colors ${
                voiceEnabled 
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' 
                  : 'hover:bg-slate-800 hover:text-slate-200'
              }`}
              title={voiceEnabled ? 'Mute Speech' : 'Enable Voice Output'}
            >
              {voiceEnabled ? <Volume2 className="w-4 h-4 text-cyan-400" /> : <VolumeX className="w-4 h-4" />}
            </button>

            {/* API Key Modal Toggle */}
            <button
              onClick={() => setShowKeyConfig(!showKeyConfig)}
              className="p-2 rounded-lg hover:bg-slate-800 hover:text-cyan-300 transition-colors"
              title="API Key Configuration"
            >
              <Key className="w-4 h-4" />
            </button>

            {/* Expand / Minimize */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 rounded-lg hover:bg-slate-800 hover:text-cyan-300 transition-colors hidden sm:block"
              title={isExpanded ? 'Standard View' : 'Expand View'}
            >
              {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>

            {/* Clear Chat */}
            <button
              onClick={handleClearChat}
              className="p-2 rounded-lg hover:bg-slate-800 hover:text-rose-400 transition-colors"
              title="Reset Conversation"
            >
              <Trash2 className="w-4 h-4" />
            </button>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
              title="Close Panel"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* API Key Settings Drawer (Collapsible) */}
        {showKeyConfig && (
          <div className="p-4 bg-[#0A162D] border-b border-cyan-500/30 text-xs space-y-3 animate-fade-in shrink-0">
            <div className="flex items-center justify-between">
              <span className="font-bold text-cyan-300 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5" />
                <span>Optional Cloud AI Key Setup</span>
              </span>
              <button 
                onClick={() => setShowKeyConfig(false)}
                className="text-slate-400 hover:text-white"
              >
                &times;
              </button>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              CareerSetu includes an autonomous local intelligence engine that analyzes real resume data. You can optionally connect your own Gemini, OpenAI, or Groq API key here.
            </p>
            <form onSubmit={handleSaveApiKey} className="space-y-2">
              <div className="flex gap-2">
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-200 outline-none focus:border-cyan-400"
                >
                  <option value="gemini">Google Gemini</option>
                  <option value="openai">OpenAI</option>
                  <option value="groq">Groq (Llama 3)</option>
                </select>
                <input
                  type="password"
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  placeholder="Paste API Key (or empty to reset)..."
                  className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 outline-none focus:border-cyan-400 font-mono"
                />
                <button
                  type="submit"
                  className="px-3 py-1.5 rounded-lg font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition-colors"
                >
                  Save
                </button>
              </div>
            </form>
            {configMessage && (
              <p className="text-[11px] font-semibold text-emerald-400">{configMessage}</p>
            )}
          </div>
        )}

        {/* Active Context Banner */}
        <div className="px-4 py-2 bg-[#09152C]/90 border-b border-cyan-500/10 flex items-center justify-between text-[11px] text-slate-400 shrink-0">
          <div className="flex items-center gap-2 truncate">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
            <div className="flex items-center gap-1.5 text-cyan-300 font-semibold truncate">
              <span>Candidate:</span>
              {isEditingName ? (
                <div className="flex items-center gap-1">
                  <input
                    type="text"
                    value={customNameInput}
                    onChange={(e) => setCustomNameInput(e.target.value)}
                    placeholder="Your Name..."
                    className="bg-slate-900 border border-cyan-400 rounded px-1.5 py-0.5 text-[11px] text-white outline-none font-bold w-28"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        if (customNameInput.trim()) {
                          if (onUpdateCandidateName) onUpdateCandidateName(customNameInput.trim());
                          setIsEditingName(false);
                          handleSendMessage(`I am ${customNameInput.trim()}`);
                        }
                      }
                    }}
                  />
                  <button
                    onClick={() => {
                      if (customNameInput.trim()) {
                        if (onUpdateCandidateName) onUpdateCandidateName(customNameInput.trim());
                        setIsEditingName(false);
                        handleSendMessage(`I am ${customNameInput.trim()}`);
                      }
                    }}
                    className="p-1 hover:text-emerald-400"
                    title="Confirm Name"
                  >
                    <Check className="w-3 h-3 text-emerald-400" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => {
                    setCustomNameInput(contextReport?.candidate_name || '');
                    setIsEditingName(true);
                  }}
                  className="flex items-center gap-1 hover:text-cyan-200 transition-colors group"
                  title="Click to change candidate name"
                >
                  <span className="underline decoration-cyan-500/50 underline-offset-2">
                    {contextReport?.candidate_name || 'Candidate'}
                  </span>
                  <Edit3 className="w-2.5 h-2.5 opacity-60 group-hover:opacity-100" />
                </button>
              )}
            </div>
            <span>&bull;</span>
            <span className="truncate">{contextReport?.job_title || 'Senior Full Stack'}</span>
          </div>
          {contextReport?.overall_score && (
            <span className="px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 font-bold border border-cyan-500/30 shrink-0">
              ATS: {Math.round(contextReport.overall_score)}/100
            </span>
          )}
        </div>

        {/* Interview Session Active HUD Banner */}
        {interviewState?.active && (
          <div className="p-3 bg-gradient-to-r from-cyan-950/80 via-blue-950/80 to-cyan-950/80 border-b border-cyan-500/40 flex items-center justify-between text-xs shrink-0">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span className="font-bold text-cyan-300">
                Mock Interview Mode: Question {interviewState.question_index} of {interviewState.total_questions || 4}
              </span>
              <span className="text-slate-400 hidden sm:inline">&bull; {interviewState.category}</span>
            </div>
            <button
              onClick={() => {
                setInterviewState(null);
                setMessages((prev) => [
                  ...prev,
                  {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: 'Interview session ended. Returning to regular career guidance.',
                  }
                ]);
              }}
              className="text-[10px] font-bold px-2 py-1 rounded bg-rose-950/80 text-rose-300 border border-rose-500/30 hover:bg-rose-900 transition-colors"
            >
              End Interview
            </button>
          </div>
        )}

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';

            return (
              <div 
                key={msg.id} 
                className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-xl bg-cyan-950 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shrink-0 shadow-[0_0_10px_rgba(6,182,212,0.3)] mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                  isUser 
                    ? 'bg-gradient-to-r from-forest-800 to-forest-900 text-white border border-forest-700 shadow-md rounded-tr-none' 
                    : msg.isError
                    ? 'bg-rose-950/60 border border-rose-500/40 text-rose-200'
                    : 'bg-[#0B172E]/90 border border-cyan-500/30 text-slate-200 shadow-[0_0_15px_rgba(6,182,212,0.1)] rounded-tl-none'
                }`}>
                  {/* Assistant Meta Tag */}
                  {!isUser && msg.provider && (
                    <div className="text-[10px] font-bold text-cyan-400/80 uppercase tracking-widest pb-1 border-b border-cyan-500/10 flex items-center justify-between">
                      <span>{msg.provider}</span>
                      {voiceEnabled && (
                        <button
                          onClick={() => speakText(msg.content)}
                          className="hover:text-cyan-200"
                          title="Replay Audio"
                        >
                          <Volume2 className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  )}

                  {/* Message Content rendered with ReactMarkdown */}
                  <div className="prose prose-invert prose-xs max-w-none prose-p:my-1.5 prose-headings:my-2 prose-headings:text-cyan-300 prose-ul:my-1.5 prose-li:my-0.5 prose-pre:bg-slate-950 prose-pre:border prose-pre:border-slate-800 prose-code:text-cyan-300">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>

                  {/* Suggested Follow-up chips */}
                  {!isUser && msg.suggested_replies && msg.suggested_replies.length > 0 && (
                    <div className="pt-3 border-t border-cyan-500/20 space-y-1.5">
                      <p className="text-[10px] font-bold uppercase tracking-wider text-cyan-400/70">
                        Suggested Inquiries:
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.suggested_replies.map((chip, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSendMessage(chip)}
                            className="text-[11px] px-2.5 py-1 rounded-lg bg-cyan-950/70 hover:bg-cyan-900/80 text-cyan-300 border border-cyan-500/30 transition-all hover:scale-[1.02] text-left"
                          >
                            {chip}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-xl bg-forest-800 border border-forest-600 flex items-center justify-center text-gold-300 shrink-0 mt-0.5">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}

          {/* Typing indicator */}
          {isLoading && (
            <div className="flex items-center gap-3 text-cyan-400 text-xs">
              <div className="w-8 h-8 rounded-xl bg-cyan-950 border border-cyan-500/40 flex items-center justify-center">
                <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
              </div>
              <div className="bg-[#0B172E] px-4 py-2.5 rounded-2xl rounded-tl-none border border-cyan-500/30 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                <span className="font-mono text-[11px] text-cyan-300">
                  J.A.R.V.I.S. is synthesizing tactical career intelligence...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Action Chips Bar */}
        <div className="px-4 py-2 border-t border-cyan-500/10 bg-[#081022]/90 flex items-center gap-2 overflow-x-auto shrink-0 scrollbar-none">
          <button
            onClick={handleStartInterview}
            className="shrink-0 text-[11px] font-bold px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-[0_0_10px_rgba(6,182,212,0.4)] flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Mock Interview</span>
          </button>

          <button
            onClick={() => handleSendMessage('How can I optimize my ATS score for this role?')}
            className="shrink-0 text-[11px] px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700"
          >
            ATS Score Diagnostic
          </button>

          <button
            onClick={() => handleSendMessage('Generate a personalized 30-day career roadmap')}
            className="shrink-0 text-[11px] px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700"
          >
            30-Day Roadmap
          </button>

          <button
            onClick={() => handleSendMessage('How do I explain my top project in an interview?')}
            className="shrink-0 text-[11px] px-2.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700"
          >
            Project Explanation Pitch
          </button>
        </div>

        {/* Input Command Line */}
        <div className="p-4 border-t border-cyan-500/20 bg-[#060D1A] shrink-0">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="relative flex items-center"
          >
            <div className="absolute left-3.5 text-cyan-500">
              <Terminal className="w-4 h-4" />
            </div>

            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder={
                interviewState?.active
                  ? "Type your interview answer here..."
                  : "Ask JARVIS about your resume, skills, code, or interview prep..."
              }
              className="w-full pl-10 pr-24 py-3 rounded-xl bg-[#0B152B] border border-cyan-500/40 text-xs text-slate-100 placeholder:text-slate-500 outline-none focus:border-cyan-400 focus:shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all font-sans"
            />

            <button
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              className="absolute right-2 px-3 py-1.5 rounded-lg font-bold text-xs bg-cyan-600 hover:bg-cyan-500 text-white disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_0_10px_rgba(6,182,212,0.4)] flex items-center gap-1.5 transition-all"
            >
              <span>Transmit</span>
              <Send className="w-3 h-3" />
            </button>
          </form>

          <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 px-1">
            <span>J.A.R.V.I.S. Career Intelligence Protocol v2.4</span>
            <span className="font-mono">Context-Aware Neural Engine</span>
          </div>
        </div>
      </div>
    </div>
  );
}
