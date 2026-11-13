import React from 'react';

export default function MetricCard({ 
  icon: Icon, 
  title, 
  value, 
  subtitle, 
  progress, 
  badge, 
  goldAccent = false,
  onClick
}) {
  return (
    <div 
      onClick={onClick}
      className={`glass-panel rounded-2xl p-5 border transition-all duration-300 relative overflow-hidden ${
        onClick ? 'cursor-pointer hover:shadow-premium hover:-translate-y-0.5' : 'shadow-premium'
      } ${
        goldAccent ? 'border-gold-300/80 bg-gradient-to-br from-white via-gold-50/20 to-white' : 'border-forest-100'
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
            {title}
          </p>
          <h3 className="text-2xl sm:text-3xl font-extrabold text-forest-900 tracking-tight">
            {value}
          </h3>
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-xl ${
            goldAccent 
              ? 'bg-gold-100 text-gold-700' 
              : 'bg-forest-50 text-forest-700'
          }`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      {subtitle && (
        <p className="mt-2 text-xs text-slate-600 line-clamp-1">
          {subtitle}
        </p>
      )}

      {typeof progress === 'number' && (
        <div className="mt-3">
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-700 ${
                goldAccent ? 'bg-gold-500' : 'bg-forest-600'
              }`}
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            />
          </div>
        </div>
      )}

      {badge && (
        <div className="mt-3">
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
            {badge}
          </span>
        </div>
      )}
    </div>
  );
}
