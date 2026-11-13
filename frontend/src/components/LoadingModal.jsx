import React, { useState, useEffect } from 'react';
import { Sparkles, CheckCircle2, Loader2, Cpu } from 'lucide-react';

export default function LoadingModal({ isOpen, stepMessage }) {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    'Parsing PDF text and structural sections via PyMuPDF...',
    'Generating TF-IDF vector representations & Cosine Similarity...',
    'Performing Skill Gap Analysis against 200+ competency taxonomies...',
    'Synthesizing explainable ATS score and tailored recommendations...'
  ];

  useEffect(() => {
    if (!isOpen) {
      setActiveStep(0);
      return;
    }
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 900);
    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-forest-950/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl border border-forest-100 text-center relative overflow-hidden">
        {/* Decorative Top Accent */}
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-forest-800 via-gold-500 to-forest-800" />

        {/* Central Animated Pulse */}
        <div className="relative mx-auto w-20 h-20 mb-6 flex items-center justify-center">
          <div className="absolute inset-0 rounded-2xl bg-forest-100 animate-ping opacity-30" />
          <div className="relative w-16 h-16 rounded-2xl forest-gradient-bg flex items-center justify-center text-gold-400 shadow-lg">
            <Cpu className="w-8 h-8 animate-spin" style={{ animationDuration: '6s' }} />
          </div>
        </div>

        <h3 className="font-serif text-2xl font-bold text-forest-950 mb-2">
          Analyzing Career Profile
        </h3>
        <p className="text-sm text-slate-500 mb-6">
          Our NLP algorithms and ATS scoring engine are comparing your resume against the target role.
        </p>

        {/* Multi-step progress list */}
        <div className="space-y-3 text-left bg-slate-50 p-4 rounded-2xl border border-slate-100 mb-6">
          {steps.map((st, idx) => {
            const isDone = idx < activeStep;
            const isCurrent = idx === activeStep;

            return (
              <div key={idx} className="flex items-start gap-3 text-xs">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-gold-600 animate-spin shrink-0 mt-0.5" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0 mt-0.5" />
                )}
                <span className={`leading-relaxed ${
                  isCurrent 
                    ? 'font-semibold text-forest-900' 
                    : isDone 
                    ? 'text-slate-500 line-through' 
                    : 'text-slate-400'
                }`}>
                  {st}
                </span>
              </div>
            );
          })}
        </div>

        <div className="text-[11px] text-slate-400 font-medium">
          Running Scikit-learn TF-IDF & Cosine Similarity
        </div>
      </div>
    </div>
  );
}
