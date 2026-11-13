import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Search, 
  MapPin, 
  Globe, 
  ExternalLink, 
  Briefcase, 
  Users, 
  Calendar, 
  ArrowRight, 
  Sparkles, 
  CheckCircle2, 
  ChevronRight, 
  X,
  Layers,
  Filter
} from 'lucide-react';
import { api } from '../services/api';

export default function CompaniesExplorerPage({ onSelectCompanyJobs, onAnalyzeJob }) {
  const [companies, setCompanies] = useState([]);
  const [totalCompanies, setTotalCompanies] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  // Filters State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('all');

  // Selected company drawer/modal state
  const [selectedCompanyDetail, setSelectedCompanyDetail] = useState(null);
  const [companyJobs, setCompanyJobs] = useState([]);
  const [loadingCompanyJobs, setLoadingCompanyJobs] = useState(false);

  const industries = [
    { id: 'all', label: 'All Industries' },
    { id: 'Big Tech', label: 'Big Tech & Cloud' },
    { id: 'IT Services', label: 'IT Services & Consulting' },
    { id: 'E-Commerce', label: 'E-Commerce & Supply Chain' },
    { id: 'Semiconductors', label: 'AI & Semiconductors' },
    { id: 'Financial', label: 'FinTech & Payments' },
    { id: 'DevSecOps', label: 'DevSecOps & Edge Cloud' }
  ];

  // Fetch companies list
  const fetchCompanies = async (page = 1) => {
    setIsLoading(true);
    try {
      const res = await api.getCompanies({
        search: searchTerm,
        industry: selectedIndustry !== 'all' ? selectedIndustry : '',
        page: page,
        limit: 16
      });
      setCompanies(res.companies || []);
      setTotalCompanies(res.total || 0);
      setTotalPages(res.total_pages || 1);
      setCurrentPage(res.page || 1);
    } catch (err) {
      console.error('Failed to fetch companies:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCompanies(1);
    }, 250);
    return () => clearTimeout(timer);
  }, [searchTerm, selectedIndustry]);

  // Open company drawer & fetch company-specific jobs
  const handleOpenCompanyDetail = async (company) => {
    setSelectedCompanyDetail(company);
    setLoadingCompanyJobs(true);
    try {
      const res = await api.getCompanyById(company.id);
      setCompanyJobs(res.jobs || []);
    } catch (err) {
      console.error('Failed to load company detail jobs:', err);
      setCompanyJobs([]);
    } finally {
      setLoadingCompanyJobs(false);
    }
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl forest-gradient-bg p-6 sm:p-8 text-white shadow-xl border border-forest-700/50">
        <div className="relative z-10 max-w-4xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-gold-400/15 border border-gold-400/30 text-gold-300">
            <Building2 className="w-3.5 h-3.5" />
            <span>Global Companies & Hiring Organizations Directory</span>
          </div>

          <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-white leading-tight">
            Top Global & Indian Employers <br className="hidden sm:inline" />
            <span className="text-gold-300 font-normal italic">Hiring Across Engineering & Digital Technologies</span>
          </h1>

          <p className="text-sm text-forest-100 max-w-2xl leading-relaxed">
            Search verified enterprise tech giants, consulting leaders, and high-growth unicorns hiring in India and worldwide. Explore current openings and analyze roles directly.
          </p>

          {/* Search bar */}
          <div className="pt-2 max-w-xl relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search companies by name, industry, headquarters, or tech..."
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-white/95 text-slate-800 placeholder:text-slate-400 text-sm outline-none focus:ring-2 focus:ring-gold-400 border border-white/20 shadow-md font-sans"
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
        </div>

        {/* Decorative background glow */}
        <div className="absolute right-0 bottom-0 translate-x-12 translate-y-12 w-80 h-80 rounded-full bg-gold-500/10 blur-3xl pointer-events-none" />
      </div>

      {/* Industry Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {industries.map((ind) => (
          <button
            key={ind.id}
            onClick={() => setSelectedIndustry(ind.id)}
            className={`text-xs px-3.5 py-2 rounded-xl font-medium shrink-0 transition-all ${
              selectedIndustry === ind.id
                ? 'bg-forest-800 text-white font-bold shadow-xs'
                : 'bg-white hover:bg-forest-50 text-slate-700 border border-forest-100'
            }`}
          >
            {ind.label}
          </button>
        ))}
      </div>

      {/* Companies Grid Header */}
      <div className="flex items-center justify-between px-1">
        <p className="text-xs sm:text-sm text-slate-600">
          Showing <span className="font-bold text-forest-900">{companies.length}</span> of{' '}
          <span className="font-bold text-forest-900">{totalCompanies}</span> enterprise hiring employers
        </p>
      </div>

      {/* Loading Skeletons */}
      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
            <div key={n} className="p-5 rounded-2xl bg-white border border-forest-100 shadow-sm animate-pulse space-y-3">
              <div className="w-12 h-12 rounded-xl bg-slate-200" />
              <div className="h-4 bg-slate-200 rounded w-3/4" />
              <div className="h-3 bg-slate-200 rounded w-1/2" />
              <div className="h-10 bg-slate-100 rounded" />
            </div>
          ))}
        </div>
      )}

      {/* Companies Grid */}
      {!isLoading && companies.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {companies.map((comp) => (
            <div
              key={comp.id}
              className="p-5 rounded-2xl bg-white border border-forest-100 shadow-sm hover:shadow-md hover:border-forest-300 transition-all flex flex-col justify-between group"
            >
              <div>
                {/* Header: Logo & Openings Badge */}
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="w-12 h-12 rounded-xl bg-forest-50 border border-forest-200 flex items-center justify-center overflow-hidden shrink-0 shadow-xs">
                    {comp.logo ? (
                      <img 
                        src={comp.logo} 
                        alt={comp.name} 
                        className="w-7 h-7 object-contain"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'block';
                        }}
                      />
                    ) : null}
                    <span className="font-serif font-bold text-forest-800 text-base hidden">
                      {comp.name.slice(0, 1)}
                    </span>
                  </div>

                  {comp.openings_count > 0 ? (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 shrink-0">
                      {comp.openings_count} Openings
                    </span>
                  ) : (
                    <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-50 text-slate-500 border border-slate-200 shrink-0">
                      Hiring Active
                    </span>
                  )}
                </div>

                {/* Company Name & Industry */}
                <h3 className="font-serif text-base font-bold text-forest-950 group-hover:text-gold-600 transition-colors line-clamp-1 mb-1">
                  {comp.name}
                </h3>
                <p className="text-xs font-semibold text-slate-500 mb-2 line-clamp-1">
                  {comp.industry}
                </p>

                {/* HQ & Size */}
                <div className="space-y-1 text-[11px] text-slate-600 mb-3">
                  <div className="flex items-center gap-1.5 truncate">
                    <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span className="truncate">{comp.headquarters}</span>
                  </div>
                  <div className="flex items-center gap-1.5 truncate">
                    <Users className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span>{comp.size}</span>
                  </div>
                </div>

                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-4">
                  {comp.description}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="pt-3 border-t border-forest-100 flex items-center justify-between gap-2">
                <button
                  onClick={() => handleOpenCompanyDetail(comp)}
                  className="flex-1 py-1.5 px-2.5 rounded-xl text-xs font-bold bg-forest-800 hover:bg-forest-900 text-white shadow-xs transition-colors text-center"
                >
                  View Jobs ({comp.openings_count})
                </button>

                {comp.career_page && (
                  <a
                    href={comp.career_page}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-xl text-slate-500 hover:text-forest-800 hover:bg-forest-50 border border-forest-100 transition-colors"
                    title="Official Careers Page"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pt-6 flex items-center justify-between border-t border-forest-100 px-2">
          <button
            disabled={currentPage <= 1 || isLoading}
            onClick={() => fetchCompanies(currentPage - 1)}
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
            onClick={() => fetchCompanies(currentPage + 1)}
            className="px-3.5 py-1.5 rounded-xl text-xs font-bold border border-forest-200 bg-white text-forest-900 hover:bg-forest-50 disabled:opacity-40 transition-all"
          >
            Next Page
          </button>
        </div>
      )}

      {/* Company Detail Drawer / Modal with its Jobs */}
      {selectedCompanyDetail && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white w-full max-w-4xl max-h-[90vh] rounded-2xl shadow-2xl border border-forest-200 flex flex-col overflow-hidden animate-scale-up">
            {/* Header */}
            <div className="p-6 forest-gradient-bg text-white relative shrink-0">
              <button
                onClick={() => setSelectedCompanyDetail(null)}
                className="absolute right-4 top-4 w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>

              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-2xl bg-white p-2.5 flex items-center justify-center overflow-hidden shrink-0 shadow-md">
                  {selectedCompanyDetail.logo ? (
                    <img 
                      src={selectedCompanyDetail.logo} 
                      alt={selectedCompanyDetail.name} 
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <span className="font-serif font-bold text-forest-900 text-xl">
                      {selectedCompanyDetail.name.slice(0, 1)}
                    </span>
                  )}
                </div>

                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h2 className="font-serif text-xl sm:text-2xl font-bold">
                      {selectedCompanyDetail.name}
                    </h2>
                    <CheckCircle2 className="w-4 h-4 text-gold-400" />
                  </div>
                  <p className="text-xs text-forest-200">{selectedCompanyDetail.industry} &bull; {selectedCompanyDetail.size}</p>
                  <p className="text-xs text-forest-300">HQ: {selectedCompanyDetail.headquarters}</p>
                </div>
              </div>
            </div>

            {/* Content: Company Overview + Active Jobs List */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-800 text-sm">
              <div>
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Company Overview:
                </h4>
                <p className="text-xs sm:text-sm text-slate-700 leading-relaxed bg-forest-50/50 p-4 rounded-xl border border-forest-100">
                  {selectedCompanyDetail.description}
                </p>
              </div>

              {/* Active Jobs Section */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                    <Briefcase className="w-4 h-4 text-forest-800" />
                    <span>Current Openings ({companyJobs.length})</span>
                  </h4>

                  {onSelectCompanyJobs && (
                    <button
                      onClick={() => {
                        onSelectCompanyJobs(selectedCompanyDetail.id || selectedCompanyDetail.name);
                        setSelectedCompanyDetail(null);
                      }}
                      className="text-xs font-bold text-gold-600 hover:text-gold-700 hover:underline flex items-center gap-1"
                    >
                      <span>Open in Jobs Explorer</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                {loadingCompanyJobs && (
                  <div className="p-8 text-center text-xs text-slate-500 animate-pulse">
                    Loading active job listings for {selectedCompanyDetail.name}...
                  </div>
                )}

                {!loadingCompanyJobs && companyJobs.length === 0 && (
                  <div className="p-8 text-center rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-500 space-y-2">
                    <p>No active openings currently cached in our database for {selectedCompanyDetail.name}.</p>
                    <a
                      href={selectedCompanyDetail.career_page}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 font-bold text-forest-800 hover:underline"
                    >
                      <span>Check official career portal</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}

                {!loadingCompanyJobs && companyJobs.length > 0 && (
                  <div className="space-y-3">
                    {companyJobs.map((j) => (
                      <div
                        key={j.id}
                        className="p-4 rounded-xl bg-white border border-forest-100 shadow-xs hover:border-forest-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                      >
                        <div className="space-y-1">
                          <h5 className="font-bold text-forest-900 text-sm">{j.title}</h5>
                          <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                            <span className="flex items-center gap-1">
                              <MapPin className="w-3 h-3 text-slate-400" />
                              <span>{j.location}</span>
                            </span>
                            <span>&bull;</span>
                            <span className="px-1.5 py-0.5 rounded bg-forest-50 text-forest-800 font-medium">
                              {j.work_mode}
                            </span>
                            <span>&bull;</span>
                            <span>{j.experience_level}</span>
                            {j.salary_text && (
                              <>
                                <span>&bull;</span>
                                <span className="font-bold text-gold-800">{j.salary_text}</span>
                              </>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-2 shrink-0">
                          {j.url && (
                            <a
                              href={j.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-2 rounded-lg text-slate-500 hover:text-forest-800 hover:bg-forest-50 border border-slate-200 transition-colors"
                              title="Direct Apply"
                            >
                              <ExternalLink className="w-3.5 h-3.5" />
                            </a>
                          )}
                          <button
                            onClick={() => {
                              if (onAnalyzeJob) {
                                onAnalyzeJob({
                                  title: j.title,
                                  company: j.company,
                                  description: j.description
                                });
                              }
                              setSelectedCompanyDetail(null);
                            }}
                            className="px-3 py-1.5 rounded-xl text-xs font-bold bg-forest-800 hover:bg-forest-900 text-white shadow-xs flex items-center gap-1.5 transition-all"
                          >
                            <Sparkles className="w-3 h-3 text-gold-400" />
                            <span>Analyze with ATS</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Official career portal: <a href={selectedCompanyDetail.career_page} target="_blank" rel="noopener noreferrer" className="text-forest-800 font-semibold hover:underline">{selectedCompanyDetail.website}</a>
              </span>
              <button
                onClick={() => setSelectedCompanyDetail(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-200 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
