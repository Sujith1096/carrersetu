import React from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  ShieldCheck, 
  Cpu, 
  FileCheck2, 
  Target, 
  BarChart3, 
  Layers, 
  Zap,
  CheckCircle2,
  FileText,
  Globe,
  Building2
} from 'lucide-react';
import { api } from '../services/api';

export default function LandingPage({ setActivePage, onLoadSample }) {
  const handleDownloadSamplePdf = () => {
    window.open(api.getSamplePdfUrl(), '_blank');
  };

  return (
    <div className="space-y-20 pb-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 sm:pt-20 sm:pb-28">
        {/* Subtle background ambient lights */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-forest-200/30 blur-[120px] rounded-full pointer-events-none -z-10" />
        <div className="absolute top-1/3 right-10 w-[300px] h-[200px] bg-gold-200/20 blur-[100px] rounded-full pointer-events-none -z-10" />

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-forest-50 border border-forest-200 text-forest-800 text-xs font-semibold shadow-xs">
            <Sparkles className="w-4 h-4 text-gold-600" />
            <span>Next-Gen Machine Learning ATS Intelligence</span>
          </div>

          {/* Heading */}
          <h1 className="font-serif text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-forest-950 leading-[1.15]">
            Bridge the Gap Between Your Resume and <span className="gold-gradient-text">Dream Career</span>.
          </h1>

          {/* Subtitle */}
          <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-600 leading-relaxed font-normal">
            CareerSetu analyzes your resume against any job description using genuine NLP, 
            TF-IDF vectorization, and cosine similarity. Get explainable ATS scores, instant skill gap analysis, and tailored recommendations.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <button
              onClick={() => setActivePage('analyze')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-xl text-base font-bold bg-forest-800 text-white hover:bg-forest-900 shadow-premium hover:shadow-xl transition-all duration-300 group"
            >
              <span>Analyze Resume Now</span>
              <ArrowRight className="w-5 h-5 text-gold-400 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={() => setActivePage('jobs')}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-4 rounded-xl text-base font-semibold bg-white text-forest-900 border border-forest-200 hover:bg-forest-50/60 shadow-xs hover:shadow transition-all"
            >
              <Globe className="w-4 h-4 text-forest-700" />
              <span>Explore Live Jobs</span>
            </button>

            <button
              onClick={() => {
                if (onLoadSample) onLoadSample();
                setActivePage('analyze');
              }}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-4 rounded-xl text-base font-medium bg-forest-50 text-forest-800 border border-forest-100 hover:bg-forest-100/60 transition-all"
            >
              <Zap className="w-4 h-4 text-gold-600" />
              <span>Try Pre-loaded Demo</span>
            </button>
          </div>

          {/* Proof points */}
          <div className="pt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500 font-medium">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>No random scores &bull; Real NLP</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>PyMuPDF Deep Parsing</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>SQLite Persistent History</span>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14 space-y-3">
          <p className="text-xs font-bold uppercase tracking-widest text-gold-700">Commercial-Grade Architecture</p>
          <h2 className="font-serif text-3xl sm:text-4xl font-bold text-forest-950">
            Engineered for Precision & Explainability
          </h2>
          <p className="text-sm text-slate-600">
            Unlike superficial keyword checkers, CareerSetu uses multi-dimensional machine learning to evaluate structural integrity and semantic relevance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1 */}
          <div className="glass-panel p-6 rounded-2xl border border-forest-100 hover:shadow-premium transition-all duration-300 space-y-4">
            <div className="w-12 h-12 rounded-xl bg-forest-50 text-forest-800 flex items-center justify-center font-bold">
              <Cpu className="w-6 h-6 text-forest-700" />
            </div>
            <h3 className="font-serif text-lg font-bold text-forest-950">
              TF-IDF & Cosine Similarity
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Computes n-gram sublinear term frequency vectors to measure deep semantic alignment between your experiences and the target role.
            </p>
          </div>

          {/* Card 2 */}
          <div className="glass-panel p-6 rounded-2xl border border-forest-100 hover:shadow-premium transition-all duration-300 space-y-4">
            <div className="w-12 h-12 rounded-xl bg-gold-50 text-gold-700 flex items-center justify-center font-bold">
              <Target className="w-6 h-6 text-gold-600" />
            </div>
            <h3 className="font-serif text-lg font-bold text-forest-950">
              Skill Gap Intelligence
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Extracts and categorizes matching, missing, and additional skills across 200+ canonical technical competencies.
            </p>
          </div>

          {/* Card 3 */}
          <div className="glass-panel p-6 rounded-2xl border border-forest-100 hover:shadow-premium transition-all duration-300 space-y-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-800 flex items-center justify-center font-bold">
              <FileCheck2 className="w-6 h-6 text-emerald-700" />
            </div>
            <h3 className="font-serif text-lg font-bold text-forest-950">
              PyMuPDF Text Extraction
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Extracts high-fidelity text streams from PDF resumes, validating section headers, contact links, and structural readability.
            </p>
          </div>

          {/* Card 4 */}
          <div className="glass-panel p-6 rounded-2xl border border-forest-100 hover:shadow-premium transition-all duration-300 space-y-4">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-800 flex items-center justify-center font-bold">
              <BarChart3 className="w-6 h-6 text-amber-700" />
            </div>
            <h3 className="font-serif text-lg font-bold text-forest-950">
              Explainable ATS Scoring
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Every score breakdown is 100% transparent: Skills (40%), Content Similarity (25%), Quantified Metrics (20%), and Sections (15%).
            </p>
          </div>
        </div>
      </section>

      {/* Interactive Teaser Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl forest-gradient-bg p-8 sm:p-12 text-white relative overflow-hidden shadow-2xl">
          <div className="relative z-10 max-w-2xl space-y-5">
            <span className="text-xs font-bold uppercase tracking-wider text-gold-400">
              Instant Demonstration
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold leading-tight">
              Test with our ATS-Optimized Sample Resume & Job Roles
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              Download our realistic sample resume PDF or load pre-curated Senior Full Stack, AI/ML, and DevOps roles to inspect real ML score outputs immediately.
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={() => {
                  if (onLoadSample) onLoadSample();
                  setActivePage('analyze');
                }}
                className="px-6 py-3 rounded-xl text-sm font-bold bg-gold-500 hover:bg-gold-400 text-forest-950 transition-colors shadow-md"
              >
                Load Sample Profile in Matcher
              </button>
              <button
                onClick={handleDownloadSamplePdf}
                className="px-5 py-3 rounded-xl text-sm font-semibold bg-forest-800 hover:bg-forest-700 border border-forest-700 text-white transition-colors"
              >
                Download Alex Rivera PDF
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
