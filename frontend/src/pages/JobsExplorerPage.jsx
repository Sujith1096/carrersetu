import React, { useState, useEffect, useCallback } from 'react';
import { 
  Search, 
  MapPin, 
  Briefcase, 
  Building2, 
  Filter, 
  Sparkles, 
  ExternalLink, 
  RefreshCw, 
  Clock, 
  DollarSign, 
  CheckCircle2, 
  ChevronRight, 
  Layers, 
  SlidersHorizontal, 
  X, 
  ArrowRight,
  Globe,
  Tag,
  Zap,
  Info
} from 'lucide-react';
import { api } from '../services/api';

export default function JobsExplorerPage({ onAnalyzeJob, onNavigateCompany, initialCompanyFilter }) {
  const [jobs, setJobs] = useState([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState(null);

  // Filters State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('all');
  const [selectedCompany, setSelectedCompany] = useState(initialCompanyFilter || 'all');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [selectedWorkMode, setSelectedWorkMode] = useState('all');
  const [selectedExpLevel, setSelectedExpLevel] = useState('all');
  const [selectedJobType, setSelectedJobType] = useState('all');
  const [selectedSkill, setSelectedSkill] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [showMobileFilters, setShowMobileFilters] = useState(false);

  // Filter options from backend
  const [filterOptions, setFilterOptions] = useState({
    roles: [],
    companies: [],
    locations: [],
    experience_levels: [],
    work_modes: [],
    employment_types: [],
    popular_skills: []
  });

  // Selected job for detail modal
  const [selectedJobDetail, setSelectedJobDetail] = useState(null);

  // Load filter options on mount
  useEffect(() => {
    api.getJobFilterOptions()
      .then((opts) => setFilterOptions(opts))
      .catch((err) => console.error('Failed to load filter options:', err));
  }, []);

  // Update selected company if prop changes
  useEffect(() => {
    if (initialCompanyFilter) {
      setSelectedCompany(initialCompanyFilter);
      setCurrentPage(1);
    }
  }, [initialCompanyFilter]);

  // Fetch jobs with active filters
  const fetchJobs = useCallback(async (page = 1) => {
    setIsLoading(true);
    try {
      const res = await api.getJobs({
        search: searchTerm,
        role: selectedRole !== 'all' ? selectedRole : '',
        company: selectedCompany !== 'all' ? selectedCompany : '',
        location: selectedLocation !== 'all' ? selectedLocation : '',
        work_mode: selectedWorkMode !== 'all' ? selectedWorkMode : '',
        experience_level: selectedExpLevel !== 'all' ? selectedExpLevel : '',
        job_type: selectedJobType !== 'all' ? selectedJobType : '',
        skills: selectedSkill,
        sort_by: sortBy,
        page: page,
        limit: 12
      });
      setJobs(res.jobs || []);
      setTotalJobs(res.total || 0);
      setTotalPages(res.total_pages || 1);
      setCurrentPage(res.page || 1);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setIsLoading(false);
    }
  }, [searchTerm, selectedRole, selectedCompany, selectedLocation, selectedWorkMode, selectedExpLevel, selectedJobType, selectedSkill, sortBy]);

  // Debounced search trigger
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchJobs(1);
    }, 250);
    return () => clearTimeout(timer);
  }, [fetchJobs]);

  // Live Sync handler
  const handleSyncLive = async () => {
    setIsSyncing(true);
    setSyncMessage(null);
    try {
      const res = await api.syncLiveJobs();
      setSyncMessage({
        type: 'success',
        text: `Live Sync Complete: Fetched ${res.fetched} listings across feeds. Added ${res.added} new active jobs!`
      });
      fetchJobs(1);
    } catch (err) {
      setSyncMessage({
        type: 'error',
        text: `Live Sync Notice: ${err.message}`
      });
    } finally {
      setIsSyncing(false);
      setTimeout(() => setSyncMessage(null), 7000);
    }
  };

  const handleResetFilters = () => {
    setSearchTerm('');
    setSelectedRole('all');
    setSelectedCompany('all');
    setSelectedLocation('all');
    setSelectedWorkMode('all');
    setSelectedExpLevel('all');
    setSelectedJobType('all');
    setSelectedSkill('');
    setSortBy('recent');
    setCurrentPage(1);
  };

  const hasActiveFilters = searchTerm || selectedRole !== 'all' || selectedCompany !== 'all' || selectedLocation !== 'all' || selectedWorkMode !== 'all' || selectedExpLevel !== 'all' || selectedJobType !== 'all' || selectedSkill;

  return (
    <div className="space-y-6 pb-16">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl forest-gradient-bg p-6 sm:p-8 text-white shadow-xl border border-forest-700/50">
        <div className="relative z-10 max-w-4xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-gold-400/15 border border-gold-400/30 text-gold-300">
            <Globe className="w-3.5 h-3.5" />
            <span>Global Career Intelligence & Live Feeds</span>
          </div>

          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-white leading-tight">
            Explore High-Impact Jobs <br className="hidden sm:inline" />
            <span className="text-gold-300 font-normal italic">Across India & International Tech Hubs</span>
          </h1>

          <p className="text-sm text-forest-100 max-w-2xl leading-relaxed">
            Real live job listings from top companies and verified career feeds. Filter by level, technology, and location, then analyze any role directly with our ATS Matcher.
          </p>

          {/* Global Search Inputs Bar */}
          <div className="pt-2 flex flex-col sm:flex-row gap-2.5 max-w-3xl">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Job title, role, company, or tech keyword (e.g. Python, React, AI, AWS)..."
                className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/95 text-slate-800 placeholder:text-slate-400 text-sm outline-none focus:ring-2 focus:ring-gold-400 border border-white/20 shadow-md transition-all font-sans"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            <button
              onClick={handleSyncLive}
              disabled={isSyncing}
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl font-bold text-xs sm:text-sm bg-gradient-to-r from-gold-500 to-amber-500 hover:from-gold-400 hover:to-amber-400 text-forest-950 shadow-md hover:shadow-gold-glow transition-all shrink-0 disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
              <span>{isSyncing ? 'Syncing Live Feeds...' : 'Sync Live Jobs'}</span>
            </button>
          </div>

          {/* Sync notification message */}
          {syncMessage && (
            <div className={`p-3 rounded-xl text-xs flex items-center gap-2 ${
              syncMessage.type === 'success' ? 'bg-emerald-950/80 border border-emerald-500/40 text-emerald-200' : 'bg-rose-950/80 border border-rose-500/40 text-rose-200'
            }`}>
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-400" />
              <span>{syncMessage.text}</span>
            </div>
          )}
        </div>

        {/* Decorative background glow */}
        <div className="absolute right-0 bottom-0 translate-x-12 translate-y-12 w-80 h-80 rounded-full bg-gold-500/10 blur-3xl pointer-events-none" />
      </div>

      {/* Main Content Layout (Sidebar Filters + Job Cards Grid) */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
        {/* Filter Panel (Desktop & Mobile Drawer) */}
        <div className="lg:col-span-1 space-y-4">
          {/* Mobile Filter Toggle */}
          <div className="lg:hidden flex items-center justify-between p-3.5 rounded-xl bg-white border border-forest-100 shadow-sm">
            <div className="flex items-center gap-2 text-sm font-bold text-forest-900">
              <SlidersHorizontal className="w-4 h-4 text-gold-500" />
              <span>Filters & Criteria</span>
              {hasActiveFilters && (
                <span className="w-2 h-2 rounded-full bg-gold-500" />
              )}
            </div>
            <button
              onClick={() => setShowMobileFilters(!showMobileFilters)}
              className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-forest-50 text-forest-800 border border-forest-200"
            >
              {showMobileFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
          </div>

          <div className={`space-y-5 bg-white p-5 rounded-2xl border border-forest-100 shadow-sm ${
            showMobileFilters ? 'block' : 'hidden lg:block'
          }`}>
            <div className="flex items-center justify-between pb-3 border-b border-forest-100">
              <div className="flex items-center gap-2 text-forest-900 font-bold text-sm">
                <SlidersHorizontal className="w-4 h-4 text-gold-500" />
                <span>Search Filters</span>
              </div>
              {hasActiveFilters && (
                <button
                  onClick={handleResetFilters}
                  className="text-[11px] font-semibold text-rose-600 hover:text-rose-700 hover:underline"
                >
                  Reset All
                </button>
              )}
            </div>

            {/* Role Category Filter */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Role Category
              </label>
              <select
                value={selectedRole}
                onChange={(e) => {
                  setSelectedRole(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full px-3 py-2 text-xs rounded-xl bg-forest-50/50 border border-forest-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-gold-400 font-sans"
              >
                <option value="all">All Roles & Disciplines</option>
                {filterOptions.roles.map((r, i) => (
                  <option key={i} value={r}>{r}</option>
                ))}
              </select>
            </div>

            {/* Experience Level */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Experience Level
              </label>
              <div className="grid grid-cols-2 gap-1.5">
                {['all', 'Internship', 'Fresher / Entry', 'Junior', 'Mid-level', 'Senior', 'Lead / Principal'].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => {
                      setSelectedExpLevel(lvl);
                      setCurrentPage(1);
                    }}
                    className={`text-[11px] px-2 py-1.5 rounded-lg border text-center transition-all ${
                      selectedExpLevel === lvl
                        ? 'bg-forest-800 text-white border-forest-900 font-bold shadow-xs'
                        : 'bg-forest-50/40 text-slate-600 border-forest-100 hover:bg-forest-50'
                    }`}
                  >
                    {lvl === 'all' ? 'All Levels' : lvl}
                  </button>
                ))}
              </div>
            </div>

            {/* Work Mode (Remote / Hybrid / Onsite) */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Work Mode
              </label>
              <div className="flex rounded-xl bg-forest-50/80 p-1 border border-forest-100">
                {[
                  { id: 'all', label: 'All' },
                  { id: 'Remote', label: 'Remote' },
                  { id: 'Hybrid', label: 'Hybrid' },
                  { id: 'On-site', label: 'On-site' }
                ].map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => {
                      setSelectedWorkMode(mode.id);
                      setCurrentPage(1);
                    }}
                    className={`flex-1 text-[11px] py-1.5 rounded-lg text-center font-medium transition-all ${
                      selectedWorkMode === mode.id
                        ? 'bg-white text-forest-900 font-bold shadow-xs border border-forest-200'
                        : 'text-slate-600 hover:text-forest-800'
                    }`}
                  >
                    {mode.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Location / Geography */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Hub & Location
              </label>
              <select
                value={selectedLocation}
                onChange={(e) => {
                  setSelectedLocation(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full px-3 py-2 text-xs rounded-xl bg-forest-50/50 border border-forest-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-gold-400 font-sans"
              >
                <option value="all">Global (All Locations)</option>
                {filterOptions.locations.map((loc, i) => (
                  <option key={i} value={loc}>{loc}</option>
                ))}
              </select>
            </div>

            {/* Company Select */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Company
              </label>
              <select
                value={selectedCompany}
                onChange={(e) => {
                  setSelectedCompany(e.target.value);
                  setCurrentPage(1);
                }}
                className="w-full px-3 py-2 text-xs rounded-xl bg-forest-50/50 border border-forest-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-gold-400 font-sans"
              >
                <option value="all">All Employers ({filterOptions.companies.length})</option>
                {filterOptions.companies.map((c, i) => (
                  <option key={i} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* Popular Technology Skills tags */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center justify-between">
                <span>Filter by Tech Stack</span>
                {selectedSkill && (
                  <button onClick={() => setSelectedSkill('')} className="text-[10px] text-rose-500 font-medium">Clear</button>
                )}
              </label>
              <div className="flex flex-wrap gap-1">
                {filterOptions.popular_skills.slice(0, 16).map((sk) => (
                  <button
                    key={sk}
                    onClick={() => {
                      setSelectedSkill(selectedSkill === sk ? '' : sk);
                      setCurrentPage(1);
                    }}
                    className={`text-[10px] px-2 py-1 rounded-md transition-all ${
                      selectedSkill === sk
                        ? 'bg-gold-500 text-forest-950 font-bold border border-gold-600 shadow-xs'
                        : 'bg-forest-50 hover:bg-forest-100 text-slate-700 border border-forest-200'
                    }`}
                  >
                    {sk}
                  </button>
                ))}
              </div>
            </div>

            {/* Sort Order */}
            <div className="space-y-1.5 pt-2 border-t border-forest-100">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Sort Order
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 text-xs rounded-xl bg-forest-50/50 border border-forest-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-gold-400 font-sans"
              >
                <option value="recent">Most Recently Posted</option>
                <option value="salary">Highest Compensation Band</option>
              </select>
            </div>
          </div>
        </div>

        {/* Job Listings Grid */}
        <div className="lg:col-span-3 space-y-4">
          {/* Header Bar with count and reset */}
          <div className="flex flex-wrap items-center justify-between gap-3 px-1">
            <div className="text-xs sm:text-sm text-slate-600">
              Showing <span className="font-bold text-forest-900">{jobs.length}</span> of{' '}
              <span className="font-bold text-forest-900">{totalJobs}</span> active global opportunities
            </div>

            {hasActiveFilters && (
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-500">Filtered view</span>
                <button
                  onClick={handleResetFilters}
                  className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-forest-100 hover:bg-forest-200 text-forest-800 transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            )}
          </div>

          {/* Loading Skeletons */}
          {isLoading && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4, 5, 6].map((n) => (
                <div key={n} className="p-5 rounded-2xl bg-white border border-forest-100 shadow-sm animate-pulse space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-slate-200" />
                    <div className="space-y-1.5 flex-1">
                      <div className="h-4 bg-slate-200 rounded w-3/4" />
                      <div className="h-3 bg-slate-200 rounded w-1/2" />
                    </div>
                  </div>
                  <div className="h-12 bg-slate-100 rounded" />
                  <div className="flex gap-2">
                    <div className="h-6 bg-slate-200 rounded w-16" />
                    <div className="h-6 bg-slate-200 rounded w-20" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isLoading && jobs.length === 0 && (
            <div className="p-12 text-center rounded-2xl bg-white border border-forest-100 shadow-sm space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-forest-50 border border-forest-200 flex items-center justify-center text-forest-700 mx-auto">
                <Search className="w-7 h-7 text-gold-500" />
              </div>
              <h3 className="font-serif text-lg font-bold text-forest-900">No Job Listings Match Criteria</h3>
              <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
                We couldn't find active jobs matching your selected filters. Try broadening your location, clearing specific skill tags, or syncing fresh listings.
              </p>
              <div className="flex justify-center gap-3 pt-2">
                <button
                  onClick={handleResetFilters}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-forest-800 text-white hover:bg-forest-900 shadow-sm transition-all"
                >
                  Reset All Filters
                </button>
                <button
                  onClick={handleSyncLive}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-gold-100 border border-gold-300 text-gold-800 hover:bg-gold-200 transition-all flex items-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>Sync Live Feeds</span>
                </button>
              </div>
            </div>
          )}

          {/* Job Cards Grid */}
          {!isLoading && jobs.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {jobs.map((job) => {
                return (
                  <div
                    key={job.id}
                    className="p-5 rounded-2xl bg-white border border-forest-100/80 shadow-sm hover:shadow-md hover:border-forest-300/80 transition-all flex flex-col justify-between group relative"
                  >
                    <div>
                      {/* Top Header: Company Logo, Name, Location */}
                      <div className="flex items-start justify-between gap-3 mb-2.5">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center overflow-hidden shrink-0 shadow-xs">
                            {job.company_logo ? (
                              <img 
                                src={job.company_logo} 
                                alt={job.company} 
                                className="w-6 h-6 object-contain"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  e.target.nextSibling.style.display = 'block';
                                }}
                              />
                            ) : null}
                            <span className="font-serif font-bold text-forest-800 text-sm hidden">
                              {job.company.slice(0, 1)}
                            </span>
                          </div>

                          <div>
                            <button
                              onClick={() => onNavigateCompany && onNavigateCompany(job.company_id || job.company)}
                              className="text-xs font-bold text-forest-900 hover:text-gold-600 transition-colors text-left flex items-center gap-1"
                            >
                              <span>{job.company}</span>
                              <CheckCircle2 className="w-3 h-3 text-emerald-500 inline shrink-0" />
                            </button>
                            <div className="flex items-center gap-1.5 text-[11px] text-slate-500 font-medium">
                              <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                              <span className="truncate max-w-[180px]">{job.location}</span>
                            </div>
                          </div>
                        </div>

                        {/* Work Mode Badge */}
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border shrink-0 ${
                          job.work_mode === 'Remote'
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                            : job.work_mode === 'Hybrid'
                            ? 'bg-amber-50 text-amber-800 border-amber-200'
                            : 'bg-blue-50 text-blue-800 border-blue-200'
                        }`}>
                          {job.work_mode}
                        </span>
                      </div>

                      {/* Job Title */}
                      <h3 
                        onClick={() => setSelectedJobDetail(job)}
                        className="font-serif text-base font-bold text-forest-950 group-hover:text-forest-800 transition-colors line-clamp-2 cursor-pointer mb-2"
                      >
                        {job.title}
                      </h3>

                      {/* Pill Badges: Level, Type, Salary */}
                      <div className="flex flex-wrap items-center gap-1.5 mb-3">
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-forest-50 text-forest-800 border border-forest-100">
                          {job.experience_level}
                        </span>
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-forest-50 text-slate-700 border border-forest-100">
                          {job.employment_type}
                        </span>
                        {job.salary_text && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-gold-50 text-gold-900 border border-gold-200 flex items-center gap-0.5">
                            <DollarSign className="w-2.5 h-2.5" />
                            <span>{job.salary_text}</span>
                          </span>
                        )}
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 font-mono">
                          via {job.source}
                        </span>
                      </div>

                      {/* Skill Tags preview */}
                      {job.skills && job.skills.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-4">
                          {job.skills.slice(0, 4).map((sk, idx) => (
                            <span 
                              key={idx}
                              className="text-[10px] px-2 py-0.5 rounded-md bg-slate-50 text-slate-600 border border-slate-200 font-medium"
                            >
                              {sk}
                            </span>
                          ))}
                          {job.skills.length > 4 && (
                            <span className="text-[10px] px-1.5 py-0.5 text-slate-400">
                              +{job.skills.length - 4}
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Bottom Action Bar */}
                    <div className="pt-3 border-t border-forest-100/60 flex items-center justify-between gap-2">
                      <button
                        onClick={() => setSelectedJobDetail(job)}
                        className="text-xs font-semibold text-forest-800 hover:text-forest-950 transition-colors flex items-center gap-1 py-1"
                      >
                        <span>View Details</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>

                      <div className="flex items-center gap-1.5">
                        {/* Direct External Apply */}
                        {job.url && (
                          <a
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 rounded-lg text-slate-500 hover:text-forest-800 hover:bg-forest-50 border border-forest-100 transition-colors"
                            title="Open Official Application Portal"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        )}

                        {/* Analyze with ATS (Primary Flow) */}
                        <button
                          onClick={() => {
                            if (onAnalyzeJob) {
                              onAnalyzeJob({
                                title: job.title,
                                company: job.company,
                                description: job.description
                              });
                            }
                          }}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-forest-800 hover:bg-forest-900 text-white shadow-xs hover:shadow transition-all group"
                          title="Transfer directly to ATS Resume Matcher"
                        >
                          <Sparkles className="w-3 h-3 text-gold-400 group-hover:scale-110 transition-transform" />
                          <span>Analyze with ATS</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="pt-6 flex items-center justify-between border-t border-forest-100 px-2">
              <button
                disabled={currentPage <= 1 || isLoading}
                onClick={() => fetchJobs(currentPage - 1)}
                className="px-3.5 py-1.5 rounded-xl text-xs font-bold border border-forest-200 bg-white text-forest-900 hover:bg-forest-50 disabled:opacity-40 transition-all"
              >
                Previous Page
              </button>

              <div className="text-xs font-medium text-slate-600">
                Page <span className="font-bold text-forest-900">{currentPage}</span> of{' '}
                <span className="font-bold text-forest-900">{totalPages}</span>
              </div>

              <button
                disabled={currentPage >= totalPages || isLoading}
                onClick={() => fetchJobs(currentPage + 1)}
                className="px-3.5 py-1.5 rounded-xl text-xs font-bold border border-forest-200 bg-white text-forest-900 hover:bg-forest-50 disabled:opacity-40 transition-all"
              >
                Next Page
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Job Details Slide-Over Modal */}
      {selectedJobDetail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white w-full max-w-3xl max-h-[90vh] rounded-2xl shadow-2xl border border-forest-200 flex flex-col overflow-hidden animate-scale-up">
            {/* Modal Header */}
            <div className="p-6 forest-gradient-bg text-white relative shrink-0">
              <button
                onClick={() => setSelectedJobDetail(null)}
                className="absolute right-4 top-4 w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>

              <div className="flex items-center gap-3 mb-2">
                <span className="text-xs font-bold text-gold-300 uppercase tracking-widest">
                  {selectedJobDetail.company}
                </span>
                <span className="w-1 h-1 rounded-full bg-white/40" />
                <span className="text-xs text-forest-200">{selectedJobDetail.location}</span>
                <span className="w-1 h-1 rounded-full bg-white/40" />
                <span className="text-xs text-gold-300 font-mono">Source: {selectedJobDetail.source}</span>
              </div>

              <h2 className="font-serif text-xl sm:text-2xl font-bold leading-tight mb-3">
                {selectedJobDetail.title}
              </h2>

              <div className="flex flex-wrap gap-2 text-xs">
                <span className="px-2.5 py-1 rounded-lg bg-white/10 text-white font-semibold border border-white/20">
                  {selectedJobDetail.role_category}
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-white/10 text-white font-semibold border border-white/20">
                  {selectedJobDetail.experience_level}
                </span>
                <span className="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30">
                  {selectedJobDetail.work_mode}
                </span>
                {selectedJobDetail.salary_text && (
                  <span className="px-2.5 py-1 rounded-lg bg-gold-400/20 text-gold-300 font-bold border border-gold-400/30">
                    {selectedJobDetail.salary_text}
                  </span>
                )}
              </div>
            </div>

            {/* Modal Body: Skills & Description */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-800 text-sm">
              {/* Highlight Banner: 1-Click ATS Analysis */}
              <div className="p-4 rounded-xl bg-forest-50 border border-forest-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-0.5">
                  <div className="font-bold text-forest-900 text-sm flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-gold-500" />
                    <span>Instant ATS Resume Alignment</span>
                  </div>
                  <p className="text-xs text-slate-600">
                    Transfer this role's description into CareerSetu's TF-IDF engine to test your resume match score.
                  </p>
                </div>
                <button
                  onClick={() => {
                    if (onAnalyzeJob) {
                      onAnalyzeJob({
                        title: selectedJobDetail.title,
                        company: selectedJobDetail.company,
                        description: selectedJobDetail.description
                      });
                    }
                  }}
                  className="px-4 py-2 rounded-xl font-bold text-xs bg-forest-800 hover:bg-forest-900 text-white shadow-sm flex items-center justify-center gap-1.5 shrink-0 transition-all"
                >
                  <Sparkles className="w-3.5 h-3.5 text-gold-400" />
                  <span>Analyze This Job</span>
                </button>
              </div>

              {/* Skills required */}
              {selectedJobDetail.skills && selectedJobDetail.skills.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Key Required Competencies:
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedJobDetail.skills.map((sk, idx) => (
                      <span key={idx} className="text-xs px-2.5 py-1 rounded-lg bg-forest-50 border border-forest-200 text-forest-800 font-semibold">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Full Description */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Full Job Description:
                </h4>
                <div className="whitespace-pre-line text-slate-700 leading-relaxed font-sans bg-slate-50 p-4 rounded-xl border border-slate-200">
                  {selectedJobDetail.description}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-3 shrink-0">
              <span className="text-xs text-slate-500">
                Posted via <strong className="text-slate-700">{selectedJobDetail.source}</strong> &bull; {selectedJobDetail.posted_date}
              </span>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedJobDetail(null)}
                  className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-200 transition-colors"
                >
                  Close
                </button>
                {selectedJobDetail.url && (
                  <a
                    href={selectedJobDetail.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-white border border-forest-300 text-forest-900 hover:bg-forest-50 shadow-xs flex items-center gap-1.5 transition-all"
                  >
                    <span>Apply on Portal</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
                <button
                  onClick={() => {
                    if (onAnalyzeJob) {
                      onAnalyzeJob({
                        title: selectedJobDetail.title,
                        company: selectedJobDetail.company,
                        description: selectedJobDetail.description
                      });
                    }
                  }}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-forest-800 hover:bg-forest-900 text-white shadow-sm flex items-center gap-1.5 transition-all"
                >
                  <Sparkles className="w-3.5 h-3.5 text-gold-400" />
                  <span>Analyze with ATS</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
