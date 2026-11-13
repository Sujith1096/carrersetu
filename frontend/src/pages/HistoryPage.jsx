import React, { useState, useEffect } from 'react';
import { 
  History, 
  Trash2, 
  ExternalLink, 
  Search, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle2, 
  FileText,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';

export default function HistoryPage({ onSelectReport, setActivePage }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState(null);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getHistory();
      setHistoryItems(data);
    } catch (err) {
      setError(err.message || 'Failed to retrieve analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleInspect = async (id) => {
    try {
      const report = await api.getHistoryDetail(id);
      onSelectReport(report);
      setActivePage('report');
    } catch (err) {
      alert(`Could not load report #${id}: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to delete report #${id}?`)) return;
    try {
      await api.deleteHistoryRecord(id);
      setHistoryItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      alert(`Failed to delete report: ${err.message}`);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to delete all analysis reports in SQLite? This cannot be undone.')) return;
    try {
      await api.clearHistory();
      setHistoryItems([]);
    } catch (err) {
      alert(`Failed to clear history: ${err.message}`);
    }
  };

  const handleSeedDemo = async () => {
    try {
      await api.seedDemo();
      await loadHistory();
    } catch (err) {
      alert(`Failed to seed demo: ${err.message}`);
    }
  };

  const filteredItems = historyItems.filter((item) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      item.candidate_name.toLowerCase().includes(q) ||
      item.job_title.toLowerCase().includes(q) ||
      item.job_company.toLowerCase().includes(q) ||
      item.file_name.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-8 pb-20">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-3xl font-bold text-forest-950">
            Analysis History & Audit Log
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Complete database of prior candidate evaluations stored in SQLite.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={loadHistory}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-xs"
            title="Refresh list"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          {historyItems.length > 0 && (
            <button
              onClick={handleClearAll}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
          )}
        </div>
      </div>

      {/* Error alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Table Container */}
      <div className="glass-panel rounded-2xl border border-forest-100 shadow-premium overflow-hidden space-y-4">
        {/* Search Bar */}
        <div className="p-4 border-b border-forest-100/60 flex items-center justify-between gap-4">
          <div className="relative w-full max-w-sm">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by candidate, role, company..."
              className="w-full pl-9 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-forest-700 outline-none bg-white"
            />
          </div>
          <div className="text-xs text-slate-500 font-medium hidden sm:block">
            Showing {filteredItems.length} of {historyItems.length} entries
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-forest-50/70 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-6 py-3.5">ID</th>
                <th className="px-6 py-3.5">Candidate / File</th>
                <th className="px-6 py-3.5">Target Job</th>
                <th className="px-6 py-3.5">ATS Score</th>
                <th className="px-6 py-3.5">Skills Overlap</th>
                <th className="px-6 py-3.5">Date</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-forest-700" />
                    <span>Loading history...</span>
                  </td>
                </tr>
              ) : filteredItems.length > 0 ? (
                filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-forest-50/30 transition-colors">
                    <td className="px-6 py-4 font-mono text-slate-400 font-semibold">
                      #{item.id}
                    </td>
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
                      <div className="space-y-0.5">
                        <div className="text-emerald-700 font-semibold flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>{item.matching_skills_count} matching</span>
                        </div>
                        <div className="text-rose-600 flex items-center gap-1 text-[11px]">
                          <AlertCircle className="w-3 h-3" />
                          <span>{item.missing_skills_count} missing</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-[11px]">
                      {item.created_at}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="inline-flex items-center gap-2">
                        <button
                          onClick={() => handleInspect(item.id)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-forest-200 hover:bg-forest-50 text-forest-800 transition-colors shadow-xs"
                          title="Inspect detailed ATS report"
                        >
                          <span>Inspect</span>
                          <ExternalLink className="w-3 h-3 text-gold-600" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Delete report"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    <p className="mb-3">No analysis records found.</p>
                    <div className="flex items-center justify-center gap-3">
                      <button
                        onClick={handleSeedDemo}
                        className="px-4 py-2 rounded-xl text-xs font-semibold bg-forest-50 hover:bg-forest-100 text-forest-800 border border-forest-200"
                      >
                        Seed Demo Records
                      </button>
                      <button
                        onClick={() => setActivePage('analyze')}
                        className="px-4 py-2 rounded-xl text-xs font-semibold bg-forest-800 text-white"
                      >
                        Create New Analysis
                      </button>
                    </div>
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
