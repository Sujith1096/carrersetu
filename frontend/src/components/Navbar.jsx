import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export default function Navbar({ activePage, setActivePage, onOpenJarvis }) {
  const [isHealthy, setIsHealthy] = useState(null);

  useEffect(() => {
    api.checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));
  }, []);

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-forest-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div 
            onClick={() => setActivePage('landing')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl forest-gradient-bg flex items-center justify-center text-gold-400 shadow-md group-hover:shadow-gold-glow transition-all duration-300">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-serif text-xl font-bold tracking-tight text-forest-900">CareerSetu</span>
                <span className="text-[10px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded bg-gold-100 text-gold-800 border border-gold-300">AI</span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium">Career Intelligence Platform</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            <button
              onClick={() => setActivePage('landing')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activePage === 'landing'
                  ? 'bg-forest-50 text-forest-800 font-semibold'
                  : 'text-slate-600 hover:text-forest-800 hover:bg-forest-50/50'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActivePage('dashboard')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activePage === 'dashboard'
                  ? 'bg-forest-50 text-forest-800 font-semibold'
                  : 'text-slate-600 hover:text-forest-800 hover:bg-forest-50/50'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActivePage('jobs')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activePage === 'jobs'
                  ? 'bg-forest-50 text-forest-800 font-semibold'
                  : 'text-slate-600 hover:text-forest-800 hover:bg-forest-50/50'
              }`}
            >
              Jobs Explorer
            </button>
            <button
              onClick={() => setActivePage('companies')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activePage === 'companies'
                  ? 'bg-forest-50 text-forest-800 font-semibold'
                  : 'text-slate-600 hover:text-forest-800 hover:bg-forest-50/50'
              }`}
            >
              Companies
            </button>
            <button
              onClick={() => setActivePage('analyze')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activePage === 'analyze'
                  ? 'bg-forest-50 text-forest-800 font-semibold'
                  : 'text-slate-600 hover:text-forest-800 hover:bg-forest-50/50'
              }`}
            >
              Job Matcher
            </button>
            <button
              onClick={() => setActivePage('history')}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activePage === 'history'
                  ? 'bg-forest-50 text-forest-800 font-semibold'
                  : 'text-slate-600 hover:text-forest-800 hover:bg-forest-50/50'
              }`}
            >
              History
            </button>
          </nav>

          {/* Right Action & Status */}
          <div className="flex items-center gap-2.5">
            {/* JARVIS Button */}
            <button
              onClick={onOpenJarvis}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-[#081224] text-cyan-300 border border-cyan-500/40 hover:border-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.25)] hover:shadow-[0_0_16px_rgba(6,182,212,0.45)] transition-all cursor-pointer"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              <span>J.A.R.V.I.S.</span>
            </button>

            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-forest-50 border border-forest-100 text-forest-800">
              <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'}`} />
              <span>{isHealthy ? 'ML Engine Online' : 'Connecting API...'}</span>
            </div>

            <button
              onClick={() => setActivePage('analyze')}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold bg-forest-800 text-white hover:bg-forest-900 shadow-sm hover:shadow transition-all group"
            >
              <span>Analyze Resume</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform text-gold-400" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
