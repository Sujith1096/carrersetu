import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import AnalyzePage from './pages/AnalyzePage';
import ResultPage from './pages/ResultPage';
import HistoryPage from './pages/HistoryPage';
import JobsExplorerPage from './pages/JobsExplorerPage';
import CompaniesExplorerPage from './pages/CompaniesExplorerPage';
import JarvisFloatingOrb from './components/Jarvis/JarvisFloatingOrb';
import JarvisChatPanel from './components/Jarvis/JarvisChatPanel';
import AuthModal from './components/AuthModal';
import { api, authStore } from './services/api';

const CURRENT_YEAR = new Date().getFullYear();

export default function App() {
  const [activePage, setActivePage] = useState('landing');
  const [activeReport, setActiveReport] = useState(null);
  const [isJarvisOpen, setIsJarvisOpen] = useState(false);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(() => authStore.getUser());
  
  // Stored sample data for quick load
  const [initialResumeText, setInitialResumeText] = useState('');
  const [initialJob, setInitialJob] = useState(null);
  const [selectedCompanyForJobs, setSelectedCompanyForJobs] = useState('all');

  // Verify auth session on mount
  useEffect(() => {
    if (authStore.getToken()) {
      api.getMe()
        .then((user) => setCurrentUser(user))
        .catch(() => {
          authStore.clear();
          setCurrentUser(null);
        });
    }
  }, []);

  // Automatically load the latest analysis as initial context if available
  useEffect(() => {
    api.getHistory()
      .then((historyList) => {
        if (historyList && historyList.length > 0) {
          return api.getHistoryDetail(historyList[0].id);
        }
      })
      .then((latestReport) => {
        if (latestReport) {
          setActiveReport(latestReport);
        }
      })
      .catch((err) => console.log('Notice: Initial report context loading:', err));
  }, []);

  const handleAnalysisComplete = (report) => {
    setActiveReport(report);
    setActivePage('report');
  };

  const handleUpdateCandidateName = (newName) => {
    setActiveReport((prev) => {
      if (!prev) return { candidate_name: newName };
      return { ...prev, candidate_name: newName };
    });
  };

  const handleLoadSample = async () => {
    try {
      const resumeData = await api.getSampleResume();
      const jobs = await api.getSampleJobs();
      setInitialResumeText(resumeData.resume_text);
      if (jobs && jobs.length > 0) {
        setInitialJob(jobs[0]);
      }
    } catch (err) {
      console.error('Error loading sample data:', err);
    }
  };

  const handleAnalyzeJob = (job) => {
    if (job) {
      setInitialJob({
        title: job.title || '',
        company: job.company || '',
        description: job.description || ''
      });
    }
    setActivePage('analyze');
  };

  const isAppView = activePage !== 'landing';

  return (
    <div className="min-h-screen flex flex-col bg-[#F8FAF8] text-slate-800 antialiased selection:bg-gold-500/20 selection:text-forest-900 relative">
      {/* Top Navigation */}
      <Navbar 
        activePage={activePage} 
        setActivePage={setActivePage} 
        onOpenJarvis={() => setIsJarvisOpen(true)}
        currentUser={currentUser}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={() => {
          authStore.clear();
          setCurrentUser(null);
          setActiveReport(null);
        }}
      />

      {/* Main Container */}
      <div className="flex-1 flex w-full">
        {/* Sidebar on App Pages */}
        {isAppView && (
          <div className="hidden md:block">
            <Sidebar 
              activePage={activePage} 
              setActivePage={setActivePage} 
              hasActiveReport={!!activeReport} 
              onOpenJarvis={() => setIsJarvisOpen(true)}
            />
          </div>
        )}

        {/* Content Area */}
        <main className={`flex-1 transition-all duration-300 ${isAppView ? 'p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full' : ''}`}>
          {activePage === 'landing' && (
            <LandingPage 
              setActivePage={setActivePage} 
              onLoadSample={handleLoadSample} 
            />
          )}

          {activePage === 'dashboard' && (
            <Dashboard 
              setActivePage={setActivePage} 
              onSelectReport={(report) => {
                setActiveReport(report);
                setActivePage('report');
              }} 
            />
          )}

          {activePage === 'jobs' && (
            <JobsExplorerPage 
              onAnalyzeJob={handleAnalyzeJob}
              onNavigateCompany={(companyId) => {
                setSelectedCompanyForJobs(companyId);
                setActivePage('jobs');
              }}
              initialCompanyFilter={selectedCompanyForJobs}
            />
          )}

          {activePage === 'companies' && (
            <CompaniesExplorerPage 
              onSelectCompanyJobs={(companyId) => {
                setSelectedCompanyForJobs(companyId);
                setActivePage('jobs');
              }}
              onAnalyzeJob={handleAnalyzeJob}
            />
          )}

          {activePage === 'analyze' && (
            <AnalyzePage 
              onAnalysisComplete={handleAnalysisComplete}
              initialResumeText={initialResumeText}
              initialJob={initialJob}
            />
          )}

          {activePage === 'report' && (
            <ResultPage 
              report={activeReport} 
              setActivePage={setActivePage} 
            />
          )}

          {activePage === 'history' && (
            <HistoryPage 
              onSelectReport={(report) => {
                setActiveReport(report);
                setActivePage('report');
              }}
              setActivePage={setActivePage}
            />
          )}
        </main>
      </div>

      {/* Floating J.A.R.V.I.S. Orb (Accessible on all pages) */}
      <JarvisFloatingOrb
        isOpen={isJarvisOpen}
        onClick={() => setIsJarvisOpen(!isJarvisOpen)}
        activeCandidate={activeReport?.candidate_name}
        atsScore={activeReport?.overall_score ? Math.round(activeReport.overall_score) : null}
      />

      {/* J.A.R.V.I.S. Interactive AI Chat & Interview Panel */}
      <JarvisChatPanel
        isOpen={isJarvisOpen}
        onClose={() => setIsJarvisOpen(false)}
        contextReport={activeReport}
        onUpdateCandidateName={handleUpdateCandidateName}
      />

      {/* Authentication Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={(user) => {
          setCurrentUser(user);
          // Reload history for this user
          api.getHistory()
            .then((list) => {
              if (list && list.length > 0) {
                return api.getHistoryDetail(list[0].id);
              }
            })
            .then((report) => {
              if (report) setActiveReport(report);
            })
            .catch(() => {});
        }}
      />

      {/* Footer */}
      <footer className="bg-forest-950 text-slate-400 py-8 border-t border-forest-900 print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-serif font-bold text-white text-sm">CareerSetu</span>
            <span>&bull;</span>
            <span>AI Career Intelligence & ATS Engine</span>
            <span>&bull;</span>
            <span className="text-cyan-400 font-semibold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              <span>J.A.R.V.I.S. Integrated</span>
            </span>
          </div>

          <div className="flex items-center gap-4 text-slate-400">
            <span>FastAPI Backend</span>
            <span>&bull;</span>
            <span>PyMuPDF Text Extractor</span>
            <span>&bull;</span>
            <span>Scikit-learn TF-IDF</span>
            <span>&bull;</span>
            <span>SQLite Database</span>
          </div>

          <div className="text-slate-500">
            Portfolio Project &copy; {CURRENT_YEAR}
          </div>
        </div>
      </footer>
    </div>
  );
}
