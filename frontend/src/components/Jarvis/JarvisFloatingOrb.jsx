import React, { useState } from 'react';
import JarvisVisualizer from './JarvisVisualizer';

export default function JarvisFloatingOrb({ isOpen, onClick, activeCandidate, atsScore }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="fixed bottom-6 right-6 z-40 flex items-center gap-3">
      {/* Tooltip on hover */}
      {isHovered && !isOpen && (
        <div className="hidden sm:flex flex-col items-end animate-fade-in pointer-events-none">
          <div className="bg-[#0B132B]/95 backdrop-blur-md text-cyan-300 text-xs px-3 py-1.5 rounded-xl border border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.25)] flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
            <span>Consult J.A.R.V.I.S. AI Mentor</span>
          </div>
          {activeCandidate && (
            <span className="text-[10px] text-slate-400 pr-1 mt-0.5">
              Ingested: {activeCandidate} {atsScore ? `(${atsScore}/100)` : ''}
            </span>
          )}
        </div>
      )}

      {/* Floating Trigger Button */}
      <button
        type="button"
        onClick={onClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`relative group rounded-full p-2.5 transition-all duration-300 flex items-center justify-center ${
          isOpen
            ? 'bg-cyan-950/80 border-2 border-cyan-400 shadow-[0_0_25px_rgba(6,182,212,0.6)] scale-105'
            : 'bg-[#080E1C] border border-cyan-500/40 hover:border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.35)] hover:shadow-[0_0_30px_rgba(6,182,212,0.7)] hover:scale-110'
        }`}
        title="J.A.R.V.I.S. AI Assistant"
      >
        {/* Outer Pulsing Wave Ring */}
        <span className="absolute -inset-1 rounded-full bg-cyan-500/20 animate-ping opacity-60 pointer-events-none" />

        {/* Central Visualizer */}
        <JarvisVisualizer size="sm" isTyping={isOpen} />

        {/* Brand Text Badge on desktop */}
        <span className="hidden md:inline-flex items-center gap-1.5 pl-2 pr-2.5 text-xs font-bold tracking-widest text-cyan-300 uppercase">
          <span>JARVIS</span>
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
        </span>
      </button>
    </div>
  );
}
