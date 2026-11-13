import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import { 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Printer, 
  Copy, 
  ArrowLeft, 
  Briefcase, 
  Mail, 
  Phone, 
  Globe, 
  Link,
  Code2,
  BarChart3, 
  FileText, 
  Layers, 
  Zap,
  TrendingUp,
  Cpu,
  Bookmark
} from 'lucide-react';
import ScoreGauge from '../components/ScoreGauge';
import SkillBadge from '../components/SkillBadge';

export default function ResultPage({ report, setActivePage }) {
  const [skillFilter, setSkillFilter] = useState('all'); // 'all', 'matching', 'missing', 'additional'
  const [skillSearch, setSkillSearch] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Fire confetti for high scores!
    if (report && report.overall_score >= 75) {
      try {
        confetti({
          particleCount: 75,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch (e) {
        // ignore
      }
    }
  }, [report]);

  if (!report) {
    return (
      <div className="text-center py-20 space-y-4">
        <p className="text-slate-500 text-sm">No analysis report currently loaded.</p>
        <button
          onClick={() => setActivePage('analyze')}
          className="px-5 py-2.5 rounded-xl text-sm font-semibold bg-forest-800 text-white"
        >
          Run an Analysis
        </button>
      </div>
    );
  }

  const {
    candidate_name,
    candidate_email,
    candidate_phone,
    candidate_links = {},
    file_name,
    job_title,
    job_company,
    overall_score,
    match_rating,
    score_breakdown = {},
    matching_skills = [],
    missing_skills = [],
    additional_skills = [],
    parsed_sections = {},
    recommendations = [],
    word_count_resume,
    word_count_jd,
    quantified_metrics_count,
    action_verbs_found = [],
    created_at
  } = report;

  // Filter skills based on tab & search
  const filteredSkills = () => {
    let list = [];
    if (skillFilter === 'all' || skillFilter === 'matching') {
      list.push(...matching_skills.map((s) => ({ name: s, type: 'matching' })));
    }
    if (skillFilter === 'all' || skillFilter === 'missing') {
      list.push(...missing_skills.map((s) => ({ name: s, type: 'missing' })));
    }
    if (skillFilter === 'all' || skillFilter === 'additional') {
      list.push(...additional_skills.map((s) => ({ name: s, type: 'additional' })));
    }

    if (skillSearch.trim()) {
      const q = skillSearch.toLowerCase();
      list = list.filter((item) => item.name.toLowerCase().includes(q));
    }
    return list;
  };

  const handleCopySummary = () => {
    const summaryText = `CareerSetu ATS Analysis Report
Candidate: ${candidate_name}
Target Role: ${job_title} at ${job_company}
ATS Score: ${Math.round(overall_score)}/100 (${match_rating})
Matching Skills: ${matching_skills.length} (${matching_skills.slice(0, 5).join(', ')})
Missing Skills: ${missing_skills.length} (${missing_skills.slice(0, 5).join(', ')})
TF-IDF Similarity: ${score_breakdown.similarity_score}%
`;
    navigator.clipboard.writeText(summaryText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-8 pb-20 print:p-0">
      {/* Top Action Nav (Hidden in Print) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 print:hidden">
        <button
          onClick={() => setActivePage('analyze')}
          className="inline-flex items-center gap-2 text-xs font-semibold text-forest-800 hover:text-forest-900 group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
          <span>Back to Job Matcher</span>
        </button>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleCopySummary}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 transition-colors shadow-xs"
          >
            <Copy className="w-3.5 h-3.5" />
            <span>{copied ? 'Copied Summary!' : 'Copy Summary'}</span>
          </button>
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-forest-800 hover:bg-forest-900 text-white transition-colors shadow-xs"
          >
            <Printer className="w-3.5 h-3.5 text-gold-400" />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Hero Assessment Card */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-forest-100 shadow-premium relative overflow-hidden">
        <div className="flex flex-col lg:flex-row items-center justify-between gap-8">
          {/* Candidate & Job Meta */}
          <div className="space-y-4 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-forest-50 border border-forest-200 text-forest-800">
              <Sparkles className="w-3.5 h-3.5 text-gold-600" />
              <span>ATS Analysis Completed</span>
              {created_at && <span className="text-slate-400">&bull; {created_at}</span>}
            </div>

            <div>
              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-forest-950">
                {candidate_name}
              </h1>
              <p className="text-base text-slate-600 font-medium mt-1 flex items-center justify-center lg:justify-start gap-2">
                <Briefcase className="w-4 h-4 text-forest-700 shrink-0" />
                <span>{job_title}</span>
                <span className="text-slate-400">&bull;</span>
                <span className="text-forest-800 font-semibold">{job_company}</span>
              </p>
            </div>

            {/* Contact Pills */}
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-3 text-xs text-slate-500">
              {candidate_email && (
                <span className="flex items-center gap-1.5 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  <span>{candidate_email}</span>
                </span>
              )}
              {candidate_phone && (
                <span className="flex items-center gap-1.5 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                  <span>{candidate_phone}</span>
                </span>
              )}
              {candidate_links.linkedin && (
                <span className="flex items-center gap-1.5 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
                  <Link className="w-3.5 h-3.5 text-blue-600" />
                  <span>LinkedIn Linked</span>
                </span>
              )}
              {candidate_links.github && (
                <span className="flex items-center gap-1.5 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
                  <Code2 className="w-3.5 h-3.5 text-slate-800" />
                  <span>GitHub Linked</span>
                </span>
              )}
            </div>
          </div>

          {/* Central ATS Score Gauge */}
          <div className="shrink-0 bg-white/70 p-6 rounded-3xl border border-forest-100 shadow-sm flex flex-col items-center">
            <ScoreGauge score={overall_score} matchRating={match_rating} size={170} />
          </div>
        </div>
      </div>

      {/* Explainable Score Breakdown Grid */}
      <div>
        <div className="mb-4">
          <h2 className="font-serif text-xl font-bold text-forest-950">
            Explainable Score Breakdown
          </h2>
          <p className="text-xs text-slate-500">
            Weighted multi-factor ML evaluation based on skill frequency, vector similarity, and content metrics.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Skills Match */}
          <div className="glass-panel p-5 rounded-2xl border border-forest-100 shadow-premium space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold uppercase text-slate-500">Skills Overlap</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-forest-50 text-forest-800 border border-forest-100">
                40% Weight
              </span>
            </div>
            <div className="text-2xl font-extrabold text-forest-900">
              {score_breakdown.skills_score}%
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5">
              <div 
                className="bg-emerald-600 h-1.5 rounded-full" 
                style={{ width: `${score_breakdown.skills_score}%` }} 
              />
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              {score_breakdown.explanation?.skills || `Matched ${matching_skills.length} of ${matching_skills.length + missing_skills.length} required skills.`}
            </p>
          </div>

          {/* Card 2: TF-IDF Semantic Similarity */}
          <div className="glass-panel p-5 rounded-2xl border border-forest-100 shadow-premium space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold uppercase text-slate-500">TF-IDF Similarity</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-forest-50 text-forest-800 border border-forest-100">
                25% Weight
              </span>
            </div>
            <div className="text-2xl font-extrabold text-forest-900">
              {score_breakdown.similarity_score}%
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5">
              <div 
                className="bg-forest-700 h-1.5 rounded-full" 
                style={{ width: `${score_breakdown.similarity_score}%` }} 
              />
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              {score_breakdown.explanation?.similarity || 'Cosine similarity of unigram & bigram TF-IDF vectors.'}
            </p>
          </div>

          {/* Card 3: Metrics & Action Verbs */}
          <div className="glass-panel p-5 rounded-2xl border border-forest-100 shadow-premium space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold uppercase text-slate-500">Impact & Power Verbs</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-forest-50 text-forest-800 border border-forest-100">
                20% Weight
              </span>
            </div>
            <div className="text-2xl font-extrabold text-forest-900">
              {score_breakdown.metrics_score}%
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5">
              <div 
                className="bg-gold-500 h-1.5 rounded-full" 
                style={{ width: `${score_breakdown.metrics_score}%` }} 
              />
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              {score_breakdown.explanation?.metrics || `${quantified_metrics_count} quantified metrics detected.`}
            </p>
          </div>

          {/* Card 4: Section Completeness */}
          <div className="glass-panel p-5 rounded-2xl border border-forest-100 shadow-premium space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold uppercase text-slate-500">Section Integrity</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-forest-50 text-forest-800 border border-forest-100">
                15% Weight
              </span>
            </div>
            <div className="text-2xl font-extrabold text-forest-900">
              {score_breakdown.section_score}%
            </div>
            <div className="w-full bg-slate-100 rounded-full h-1.5">
              <div 
                className="bg-forest-600 h-1.5 rounded-full" 
                style={{ width: `${score_breakdown.section_score}%` }} 
              />
            </div>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              {score_breakdown.explanation?.sections || 'Evaluation of Experience, Education, Projects, and Skills.'}
            </p>
          </div>
        </div>
      </div>

      {/* Skill Gap Analysis Section */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-forest-100 shadow-premium space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="font-serif text-2xl font-bold text-forest-950">
              Skill Gap Analysis
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Comparison of resume skill taxonomy against job requirements.
            </p>
          </div>

          {/* Skill Filter Tabs */}
          <div className="flex items-center p-1 rounded-xl bg-forest-50/80 border border-forest-100 text-xs font-semibold">
            <button
              onClick={() => setSkillFilter('all')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                skillFilter === 'all' ? 'bg-white text-forest-950 shadow-xs' : 'text-slate-500'
              }`}
            >
              All ({matching_skills.length + missing_skills.length + additional_skills.length})
            </button>
            <button
              onClick={() => setSkillFilter('matching')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                skillFilter === 'matching' ? 'bg-white text-emerald-800 shadow-xs' : 'text-slate-500'
              }`}
            >
              Matching ({matching_skills.length})
            </button>
            <button
              onClick={() => setSkillFilter('missing')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                skillFilter === 'missing' ? 'bg-white text-rose-800 shadow-xs' : 'text-slate-500'
              }`}
            >
              Missing ({missing_skills.length})
            </button>
            <button
              onClick={() => setSkillFilter('additional')}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                skillFilter === 'additional' ? 'bg-white text-forest-800 shadow-xs' : 'text-slate-500'
              }`}
            >
              Additional ({additional_skills.length})
            </button>
          </div>
        </div>

        {/* Search Bar for Skills */}
        <div className="max-w-md">
          <input
            type="text"
            value={skillSearch}
            onChange={(e) => setSkillSearch(e.target.value)}
            placeholder="Search for a skill (e.g. Python, Docker, Redis)..."
            className="w-full px-4 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-forest-700 outline-none bg-white"
          />
        </div>

        {/* Skill Badges List */}
        <div className="flex flex-wrap gap-2 pt-2">
          {filteredSkills().length > 0 ? (
            filteredSkills().map((skill, idx) => (
              <SkillBadge
                key={`${skill.name}-${idx}`}
                name={skill.name}
                type={skill.type}
              />
            ))
          ) : (
            <p className="text-xs text-slate-400 py-4">No skills match the current filter.</p>
          )}
        </div>
      </div>

      {/* Actionable Recommendations Section */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-forest-100 shadow-premium space-y-6">
        <div>
          <h2 className="font-serif text-2xl font-bold text-forest-950">
            Targeted AI Recommendations
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Prioritized strategic adjustments to maximize recruiter callback rates.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec, idx) => {
            const isHigh = rec.priority === 'high';
            const isMedium = rec.priority === 'medium';

            return (
              <div 
                key={idx}
                className={`p-5 rounded-2xl border transition-all ${
                  isHigh 
                    ? 'bg-rose-50/40 border-rose-200/80' 
                    : isMedium 
                    ? 'bg-amber-50/40 border-amber-200/80' 
                    : 'bg-forest-50/30 border-forest-100'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                    isHigh 
                      ? 'bg-rose-100 text-rose-800 border-rose-300' 
                      : isMedium 
                      ? 'bg-amber-100 text-amber-800 border-amber-300' 
                      : 'bg-forest-100 text-forest-800 border-forest-200'
                  }`}>
                    {rec.priority} priority &bull; {rec.category}
                  </span>
                </div>
                <h3 className="font-serif text-base font-bold text-forest-950 mb-1">
                  {rec.title}
                </h3>
                <p className="text-xs text-slate-600 mb-3 leading-relaxed">
                  {rec.description}
                </p>
                <div className="p-3 rounded-xl bg-white/80 border border-slate-200 text-xs text-slate-800 font-medium leading-relaxed">
                  <span className="font-bold text-forest-900 block mb-0.5">Action:</span>
                  {rec.suggestion}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Structural Section Health */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-forest-100 shadow-premium space-y-4">
        <div>
          <h2 className="font-serif text-xl font-bold text-forest-950">
            Resume Section Health
          </h2>
          <p className="text-xs text-slate-500">
            Verification of standard section headings parsed by automated ATS systems.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {Object.entries(parsed_sections).map(([secKey, secVal]) => {
            const isPresent = secVal?.present;
            return (
              <div 
                key={secKey}
                className={`p-3 rounded-xl border text-center transition-all ${
                  isPresent 
                    ? 'bg-emerald-50/40 border-emerald-200' 
                    : 'bg-slate-50 border-slate-200 opacity-60'
                }`}
              >
                <div className="text-xs font-bold capitalize text-forest-950 mb-1">
                  {secKey}
                </div>
                <div className="flex items-center justify-center gap-1 text-[11px]">
                  {isPresent ? (
                    <span className="text-emerald-700 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Present
                    </span>
                  ) : (
                    <span className="text-slate-400">Missing</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Additional Telemetry Details */}
        <div className="pt-4 border-t border-forest-100/60 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500">
          <div>
            <span>Resume Word Count: </span>
            <strong className="text-forest-900">{word_count_resume} words</strong>
          </div>
          <div>
            <span>Job Description Word Count: </span>
            <strong className="text-forest-900">{word_count_jd} words</strong>
          </div>
          <div>
            <span>Action Verbs Detected: </span>
            <strong className="text-forest-900">{action_verbs_found.length} active verbs</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
