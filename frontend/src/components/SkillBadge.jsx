import React from 'react';
import { Check, AlertCircle, Plus } from 'lucide-react';

export default function SkillBadge({ name, type = 'matching', category }) {
  if (type === 'matching') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200/80 shadow-xs hover:border-emerald-300 transition-colors">
        <Check className="w-3.5 h-3.5 text-emerald-600" />
        <span>{name}</span>
        {category && <span className="text-[10px] text-emerald-600/70 font-normal">({category})</span>}
      </span>
    );
  }

  if (type === 'missing') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200/80 shadow-xs hover:border-rose-300 transition-colors">
        <AlertCircle className="w-3.5 h-3.5 text-rose-500" />
        <span>{name}</span>
        {category && <span className="text-[10px] text-rose-500/70 font-normal">({category})</span>}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-forest-50/70 text-forest-800 border border-forest-100 shadow-xs hover:border-forest-200 transition-colors">
      <Plus className="w-3 h-3 text-forest-500" />
      <span>{name}</span>
    </span>
  );
}
