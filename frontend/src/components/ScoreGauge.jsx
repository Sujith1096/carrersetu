import React from 'react';

export default function ScoreGauge({ score = 0, matchRating = 'Analysis Pending', size = 180 }) {
  const radius = 64;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (Math.min(100, Math.max(0, score)) / 100) * circumference;

  let strokeColor = '#10B981'; // emerald-500
  let badgeBg = 'bg-emerald-50 text-emerald-800 border-emerald-200';

  if (score >= 85) {
    strokeColor = '#10B981'; // emerald
    badgeBg = 'bg-emerald-50 text-emerald-800 border-emerald-200';
  } else if (score >= 70) {
    strokeColor = '#2A6650'; // forest-500
    badgeBg = 'bg-forest-50 text-forest-800 border-forest-200';
  } else if (score >= 55) {
    strokeColor = '#D4AF37'; // gold
    badgeBg = 'bg-amber-50 text-amber-800 border-amber-200';
  } else {
    strokeColor = '#F43F5E'; // rose-500
    badgeBg = 'bg-rose-50 text-rose-800 border-rose-200';
  }

  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 160 160">
          {/* Background Track */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            className="text-slate-100"
            strokeWidth="12"
            stroke="currentColor"
            fill="transparent"
          />
          {/* Progress Arc */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            stroke={strokeColor}
            strokeWidth="12"
            strokeDasharray={circumference}
            style={{
              strokeDashoffset,
              transition: 'stroke-dashoffset 1.2s ease-in-out',
            }}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-extrabold text-forest-900 tracking-tight">
            {Math.round(score)}
          </span>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Out of 100
          </span>
        </div>
      </div>

      <div className="mt-3">
        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border shadow-sm ${badgeBg}`}>
          {matchRating}
        </span>
      </div>
    </div>
  );
}
