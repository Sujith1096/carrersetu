import React from 'react';
import { 
  LayoutDashboard, 
  FileSearch, 
  FileCheck2, 
  History, 
  Sparkles, 
  Download,
  BookOpen,
  HelpCircle,
  ExternalLink,
  Bot,
  Globe,
  Building2
} from 'lucide-react';
import { api } from '../services/api';

export default function Sidebar({ activePage, setActivePage, hasActiveReport, onOpenJarvis }) {
  const menuItems = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: LayoutDashboard },
    { id: 'jobs', label: 'Global Jobs Explorer', icon: Globe, badge: 'Live Feeds' },
    { id: 'companies', label: 'Companies Directory', icon: Building2 },
    { id: 'analyze', label: 'Job Description Matcher', icon: FileSearch, badge: 'ML Core' },
    { 
      id: 'report', 
      label: 'ATS Analysis Report', 
      icon: FileCheck2, 
      disabled: !hasActiveReport,
      badge: hasActiveReport ? 'Live' : null 
    },
    { id: 'history', label: 'Analysis History', icon: History },
    { id: 'landing', label: 'Platform Overview', icon: BookOpen },
  ];

  const handleDownloadSamplePdf = () => {
    window.open(api.getSamplePdfUrl(), '_blank');
  };

  return (
    <aside className="w-64 bg-forest-900 text-slate-100 flex flex-col justify-between border-r border-forest-800/80 shadow-xl shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-5">
        {/* J.A.R.V.I.S. Quick Launch */}
        <button
          type="button"
          onClick={onOpenJarvis}
          className="w-full flex items-center justify-between p-3 rounded-xl bg-gradient-to-r from-[#071329] to-[#0A1D3D] border border-cyan-500/40 hover:border-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.25)] text-left group transition-all cursor-pointer"
        >
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-cyan-950 flex items-center justify-center text-cyan-400 border border-cyan-500/50 shadow-[0_0_8px_rgba(6,182,212,0.5)]">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-bold text-cyan-300 flex items-center gap-1.5">
                <span>J.A.R.V.I.S.</span>
                <span className="text-[9px] px-1 py-0.2 rounded bg-cyan-900/80 text-cyan-300 border border-cyan-500/30">AI</span>
              </div>
              <div className="text-[10px] text-slate-400">Launch Assistant</div>
            </div>
          </div>
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
        </button>

        {/* Navigation list */}
        <div className="space-y-1">
          <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-forest-300/80 mb-2">
            Main Intelligence
          </p>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            const isDisabled = item.disabled;

            return (
              <button
                key={item.id}
                disabled={isDisabled}
                onClick={() => setActivePage(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-forest-800 text-white shadow-md border-l-4 border-gold-400 pl-2.5'
                    : isDisabled
                    ? 'text-forest-400/50 cursor-not-allowed'
                    : 'text-slate-300 hover:text-white hover:bg-forest-800/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-gold-400' : isDisabled ? 'text-forest-600' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${
                    item.badge === 'Live' 
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
                      : 'bg-gold-500/20 text-gold-300 border border-gold-500/30'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Action card: Download Sample Resume */}
        <div className="p-3.5 rounded-xl bg-forest-800/60 border border-forest-700/60 text-xs space-y-2.5">
          <div className="flex items-center gap-2 text-gold-400 font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Ready-to-Test Resume</span>
          </div>
          <p className="text-slate-300 text-[11px] leading-relaxed">
            Need an ATS-optimized PDF resume to test the parser and ML matcher right away?
          </p>
          <button
            onClick={handleDownloadSamplePdf}
            className="w-full flex items-center justify-center gap-1.5 py-1.5 px-2.5 rounded-lg bg-gold-500/20 hover:bg-gold-500/30 text-gold-300 hover:text-gold-200 border border-gold-500/30 font-medium transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Sample PDF</span>
          </button>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-forest-800/80 bg-forest-950/40 space-y-2">
        <div className="flex items-center justify-between text-[11px] text-slate-400">
          <span>TF-IDF & Cosine Sim</span>
          <span className="font-semibold text-emerald-400">v1.0 Ready</span>
        </div>
        <p className="text-[10px] text-slate-500 leading-tight">
          Designed with genuine NLP & SQLite persistence for portfolio presentation.
        </p>
      </div>
    </aside>
  );
}
