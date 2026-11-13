import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell, 
  CartesianGrid 
} from 'recharts';
import { 
  FileText, 
  Award, 
  TrendingUp, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  Sparkles,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import { api } from '../services/api';

export default function Dashboard({ setActivePage, onSelectReport, currentUser, onOpenAuth }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard statistics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [currentUser]);

  const handleViewReport = async (id) => {
    try {
      const report = await api.getHistoryDetail(id);
      if (onSelectReport) {
        onSelectReport(report);
        setActivePage('report');
      }
    } catch (err) {
      alert(`Could not open report: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-3">
        <RefreshCw className="w-8 h-8 text-forest-700 animate-spin" />
        <p className="text-sm text-slate-500 font-medium">Aggregating platform intelligence...</p>
      </div>
    );
  }

  // Format score distribution for chart
  const distributionData = [
    { range: '< 50', count: stats?.score_distribution?.['< 50'] || 0, label: 'Needs Opt.', color: '#F43F5E' },
    { range: '50-69', count: stats?.score_distribution?.['50-69'] || 0, label: 'Moderate', color: '#D4AF37' },
    { range: '70-84', count: stats?.score_distribution?.['70-84'] || 0, label: 'Strong', color: '#2A6650' },
    { range: '85-100', count: stats?.score_distribution?.['85-100'] || 0, label: 'Excellent', color: '#10B981' },
  ];

  const topSkillsData = (stats?.top_in_demand_skills || []).slice(0, 6);

  return (
    <div className="space-y-8 pb-16">
      {/* Top Welcome & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-3xl font-bold text-forest-950">
            Executive Intelligence Dashboard
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time telemetry across analyzed resumes, TF-IDF similarities, and skill frequency patterns.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchStats}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition-colors shadow-xs"
            title="Refresh Metrics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setActivePage('analyze')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm bg-forest-800 text-white hover:bg-forest-900 shadow-sm transition-all"
          >
            <Sparkles className="w-4 h-4 text-gold-400" />
            <span>New Match Analysis</span>
          </button>
        </div>
      </div>

      {/* Guest Mode Notice */}
      {!currentUser && (
        <div className="p-4 sm:p-5 rounded-2xl bg-white border border-gold-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start sm:items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gold-50 border border-gold-200 flex items-center justify-center text-gold-700 flex-shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-serif text-sm font-bold text-forest-950">
                Guest Telemetry — Private User Records Protected
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Sign in or use 1-Click Demo Login to save evaluations, track ATS score improvements, and view your private history.
              </p>
            </div>
          </div>
          {onOpenAuth && (
            <button
              onClick={onOpenAuth}
              className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-forest-800 text-white hover:bg-forest-900 border border-forest-700 shadow-xs transition-all whitespace-nowrap cursor-pointer flex-shrink-0"
            >
              Sign In / Demo Login
            </button>
          )}
        </div>
      )}

      {/* 4 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          icon={FileText}
          title="Total Resumes Evaluated"
          value={stats?.total_analyses || 0}
          subtitle="Processed & stored in SQLite"
          goldAccent={false}
        />
        <MetricCard
          icon={TrendingUp}
          title="Average ATS Score"
          value={`${stats?.average_score || 0}`}
          subtitle="Composite NLP weighted score"
          progress={stats?.average_score || 0}
          goldAccent={true}
        />
        <MetricCard
          icon={Award}
          title="Highest Match Score"
          value={`${stats?.highest_score || 0}`}
          subtitle="Peak candidate-job alignment"
          badge="Top Performer"
        />
        <MetricCard
          icon={CheckCircle2}
          title="Skills Bank Coverage"
          value="200+"
          subtitle="Tech & leadership taxonomies"
          badge="Active Engine"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Score Distribution */}
        <div className="glass-panel p-6 rounded-2xl border border-forest-100 shadow-premium space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-serif text-lg font-bold text-forest-950">
                ATS Score Distribution
              </h3>
              <p className="text-xs text-slate-500">Frequency of candidate scores across benchmark buckets</p>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-forest-50 text-forest-800 border border-forest-100">
              Evaluated
            </span>
          </div>

          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distributionData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="range" tick={{ fontSize: 12, fill: '#64748B' }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#64748B' }} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-white p-2.5 rounded-lg shadow-lg border border-slate-100 text-xs">
                          <p className="font-bold text-forest-950">{d.range} ({d.label})</p>
                          <p className="text-slate-600">{d.count} candidates</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Top Skills In-Demand */}
        <div className="glass-panel p-6 rounded-2xl border border-forest-100 shadow-premium space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-serif text-lg font-bold text-forest-950">
                Top In-Demand Skills Matched
              </h3>
              <p className="text-xs text-slate-500">Most frequent skills detected in analyzed job descriptions</p>
            </div>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-gold-50 text-gold-800 border border-gold-200">
              Skill Taxonomy
            </span>
          </div>

          {topSkillsData.length > 0 ? (
            <div className="h-64 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topSkillsData} layout="vertical" margin={{ top: 5, right: 30, left: 35, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fill: '#64748B' }} />
                  <YAxis type="category" dataKey="skill" tick={{ fontSize: 11, fill: '#334155' }} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const d = payload[0].payload;
                        return (
                          <div className="bg-white p-2.5 rounded-lg shadow-lg border border-slate-100 text-xs">
                            <p className="font-bold text-forest-950">{d.skill}</p>
                            <p className="text-slate-600">{d.count} matches ({d.percentage}%)</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="count" fill="#123C2E" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-xs space-y-2">
              <Sparkles className="w-6 h-6 text-slate-300" />
              <p>Analyze your first resume to view skills distribution.</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="glass-panel rounded-2xl border border-forest-100 shadow-premium overflow-hidden">
        <div className="p-6 border-b border-forest-100/60 flex items-center justify-between">
          <div>
            <h3 className="font-serif text-lg font-bold text-forest-950">
              Recent Analysis Activity
            </h3>
            <p className="text-xs text-slate-500">Historical records stored in SQLite database</p>
          </div>
          <button
            onClick={() => setActivePage('history')}
            className="text-xs font-semibold text-forest-700 hover:text-forest-900 flex items-center gap-1 group"
          >
            <span>View All History</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-forest-50/60 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-6 py-3.5">Candidate / File</th>
                <th className="px-6 py-3.5">Target Role & Company</th>
                <th className="px-6 py-3.5">ATS Score</th>
                <th className="px-6 py-3.5">Match Skills</th>
                <th className="px-6 py-3.5">Missing</th>
                <th className="px-6 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(stats?.recent_history || []).length > 0 ? (
                stats.recent_history.map((item) => (
                  <tr key={item.id} className="hover:bg-forest-50/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-forest-950">{item.candidate_name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{item.file_name}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-800">{item.job_title}</div>
                      <div className="text-[11px] text-slate-500">{item.job_company}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-sm text-forest-900">{Math.round(item.overall_score)}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                          item.overall_score >= 80 
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-200' 
                            : item.overall_score >= 65 
                            ? 'bg-forest-50 text-forest-800 border-forest-200' 
                            : 'bg-amber-50 text-amber-800 border-amber-200'
                        }`}>
                          {item.match_rating}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 font-semibold text-emerald-700">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{item.matching_skills_count} skills</span>
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 font-semibold text-rose-600">
                        <AlertCircle className="w-3.5 h-3.5" />
                        <span>{item.missing_skills_count} gaps</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleViewReport(item.id)}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-forest-200 hover:bg-forest-50 text-forest-800 transition-colors shadow-xs"
                      >
                        <span>Inspect</span>
                        <ExternalLink className="w-3 h-3 text-gold-600" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-400">
                    {!currentUser ? (
                      <div className="flex flex-col items-center justify-center space-y-2">
                        <p>No evaluations recorded in guest mode.</p>
                        {onOpenAuth && (
                          <button
                            onClick={onOpenAuth}
                            className="text-xs font-semibold text-forest-700 hover:text-forest-900 underline cursor-pointer"
                          >
                            Sign in or demo login to access your personal history
                          </button>
                        )}
                      </div>
                    ) : (
                      "No evaluations recorded yet. Run a job match to see historical activity."
                    )}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
