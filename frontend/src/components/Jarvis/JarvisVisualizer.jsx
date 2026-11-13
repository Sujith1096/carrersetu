import React from 'react';

export default function JarvisVisualizer({ isSpeaking = false, isTyping = false, size = 'sm' }) {
  const isLarge = size === 'lg';
  const dimension = isLarge ? 'w-24 h-24' : 'w-10 h-10';

  return (
    <div className={`relative ${dimension} flex items-center justify-center shrink-0`}>
      {/* Outer Cyan Glow */}
      <div 
        className={`absolute inset-0 rounded-full bg-cyan-500/20 blur-md transition-all duration-700 ${
          isTyping || isSpeaking ? 'scale-125 opacity-80' : 'opacity-40 animate-pulse'
        }`} 
      />

      {/* Outer Rotating HUD Ring */}
      <svg 
        className={`absolute inset-0 w-full h-full text-cyan-400 ${
          isTyping ? 'animate-spin' : ''
        }`}
        style={{ animationDuration: '8s' }}
        viewBox="0 0 100 100"
      >
        <circle
          cx="50"
          cy="50"
          r="46"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeDasharray="12 8 4 8"
          fill="none"
          opacity="0.6"
        />
      </svg>

      {/* Inner Reverse-Rotating HUD Ring */}
      <svg 
        className="absolute inset-1 w-[calc(100%-8px)] h-[calc(100%-8px)] text-cyan-300"
        style={{ 
          animation: 'spin 12s linear infinite reverse',
        }}
        viewBox="0 0 100 100"
      >
        <circle
          cx="50"
          cy="50"
          r="40"
          stroke="currentColor"
          strokeWidth="2"
          strokeDasharray="20 15 5 10"
          fill="none"
          opacity="0.8"
        />
        {/* Cardinal Markers */}
        <line x1="50" y1="2" x2="50" y2="10" stroke="currentColor" strokeWidth="2" />
        <line x1="50" y1="90" x2="50" y2="98" stroke="currentColor" strokeWidth="2" />
        <line x1="2" y1="50" x2="10" y2="50" stroke="currentColor" strokeWidth="2" />
        <line x1="90" y1="50" x2="98" y2="50" stroke="currentColor" strokeWidth="2" />
      </svg>

      {/* Central Arc Reactor Core */}
      <div className={`relative rounded-full bg-gradient-to-tr from-cyan-600 via-cyan-400 to-blue-200 shadow-[0_0_15px_rgba(6,182,212,0.8)] flex items-center justify-center ${
        isLarge ? 'w-12 h-12' : 'w-5 h-5'
      }`}>
        <div className={`rounded-full bg-white transition-transform duration-300 ${
          isLarge ? 'w-4 h-4' : 'w-1.5 h-1.5'
        } ${isTyping || isSpeaking ? 'scale-125 shadow-[0_0_12px_#ffffff]' : 'scale-100 shadow-[0_0_6px_#ffffff]'}`} />
      </div>

      {/* Holographic Soundwave Frequency Bars (shown when speaking or typing) */}
      {(isSpeaking || isTyping) && isLarge && (
        <div className="absolute -bottom-5 flex items-center gap-0.5">
          {[40, 75, 100, 60, 90, 45, 80].map((h, i) => (
            <span
              key={i}
              className="w-1 bg-cyan-400 rounded-full animate-pulse"
              style={{
                height: `${h * 0.16}px`,
                animationDelay: `${i * 120}ms`,
                animationDuration: '600ms'
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
