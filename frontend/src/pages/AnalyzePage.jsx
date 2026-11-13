import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  FileUp, 
  Briefcase, 
  Building, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Download, 
  ArrowRight,
  RotateCcw,
  Layers,
  Copy
} from 'lucide-react';
import LoadingModal from '../components/LoadingModal';
import { api } from '../services/api';

export default function AnalyzePage({ onAnalysisComplete, initialResumeText, initialJob }) {
  // Resume input mode: 'upload' or 'text'
  const [resumeMode, setResumeMode] = useState('upload');
  const [pdfFile, setPdfFile] = useState(null);
  const [resumeText, setResumeText] = useState(initialResumeText || '');
  
  // Job Description state
  const [jobTitle, setJobTitle] = useState(initialJob?.title || '');
  const [jobCompany, setJobCompany] = useState(initialJob?.company || '');
  const [jobDescription, setJobDescription] = useState(initialJob?.description || '');
  
  // Samples list
  const [sampleJobs, setSampleJobs] = useState([]);
  const [loadingSamples, setLoadingSamples] = useState(false);

  // Execution state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef(null);

  // Fetch sample jobs on mount
  useEffect(() => {
    setLoadingSamples(true);
    api.getSampleJobs()
      .then((jobs) => setSampleJobs(jobs))
      .catch((err) => console.error('Failed to load sample jobs:', err))
      .finally(() => setLoadingSamples(false));
  }, []);

  // Update if initial props change
  useEffect(() => {
    if (initialResumeText) {
      setResumeText(initialResumeText);
      setResumeMode('text');
    }
    if (initialJob) {
      setJobTitle(initialJob.title);
      setJobCompany(initialJob.company);
      setJobDescription(initialJob.description);
    }
  }, [initialResumeText, initialJob]);

  // Handle Drag & Drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file) => {
    setErrorMessage(null);
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setErrorMessage('Invalid file format. Please select a valid .pdf document.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage('File exceeds 10MB limit. Please upload a smaller PDF resume.');
      return;
    }
    if (file.size === 0) {
      setErrorMessage('Selected PDF file is empty (0 bytes).');
      return;
    }
    setPdfFile(file);
  };

  // Populate sample resume text
  const handleLoadSampleResume = async () => {
    try {
      const data = await api.getSampleResume();
      setResumeText(data.resume_text);
      setResumeMode('text');
    } catch (err) {
      setErrorMessage('Could not load sample resume: ' + err.message);
    }
  };

  // Populate sample job
  const handleSelectSampleJob = (job) => {
    setJobTitle(job.title);
    setJobCompany(job.company);
    setJobDescription(job.description);
  };

  // Run Match Analysis
  const handleAnalyze = async () => {
    setErrorMessage(null);

    // Validation
    if (resumeMode === 'upload' && !pdfFile) {
      setErrorMessage('Please upload a PDF resume or switch to paste resume text.');
      return;
    }
    if (resumeMode === 'text' && (!resumeText || resumeText.trim().length < 50)) {
      setErrorMessage('Resume text is too brief. Please paste at least 50 characters of resume content.');
      return;
    }
    if (!jobDescription || jobDescription.trim().length < 40) {
      setErrorMessage('Job description is missing or too short. Please provide the target job requirements.');
      return;
    }

    setIsAnalyzing(true);

    try {
      let result;
      if (resumeMode === 'upload') {
        result = await api.analyzeUpload({
          file: pdfFile,
          jobDescription: jobDescription.trim(),
          jobTitle: jobTitle.trim() || 'Target Role',
          jobCompany: jobCompany.trim() || 'Company',
        });
      } else {
        result = await api.analyzeText({
          resumeText: resumeText.trim(),
          jobDescription: jobDescription.trim(),
          jobTitle: jobTitle.trim() || 'Target Role',
          jobCompany: jobCompany.trim() || 'Company',
          fileName: 'Pasted_Candidate_Resume.txt',
        });
      }

      onAnalysisComplete(result);
    } catch (err) {
      setErrorMessage(err.message || 'Analysis failed. Please check inputs and try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-8 pb-20">
      <LoadingModal isOpen={isAnalyzing} />

      {/* Header */}
      <div>
        <h1 className="font-serif text-3xl font-bold text-forest-950">
          Job Description Matcher & ATS Scorer
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload your PDF resume or paste text, select or paste target job requirements, and run the ML matching engine.
        </p>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button 
            onClick={() => setErrorMessage(null)} 
            className="text-rose-600 hover:text-rose-800 font-bold ml-2"
          >
            &times;
          </button>
        </div>
      )}

      {/* Dual Input Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Resume Input */}
        <div className="glass-panel p-6 rounded-2xl border border-forest-100 shadow-premium space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-forest-50 text-forest-800 flex items-center justify-center font-bold">
                  <FileText className="w-4 h-4 text-forest-700" />
                </div>
                <h2 className="font-serif text-lg font-bold text-forest-950">
                  Step 1: Provide Resume
                </h2>
              </div>

              {/* Mode Toggle Tabs */}
              <div className="flex items-center p-1 rounded-xl bg-forest-50 border border-forest-100 text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setResumeMode('upload')}
                  className={`px-3 py-1.5 rounded-lg transition-all ${
                    resumeMode === 'upload'
                      ? 'bg-white text-forest-900 shadow-xs'
                      : 'text-slate-500 hover:text-forest-800'
                  }`}
                >
                  PDF Upload
                </button>
                <button
                  type="button"
                  onClick={() => setResumeMode('text')}
                  className={`px-3 py-1.5 rounded-lg transition-all ${
                    resumeMode === 'text'
                      ? 'bg-white text-forest-900 shadow-xs'
                      : 'text-slate-500 hover:text-forest-800'
                  }`}
                >
                  Paste Text
                </button>
              </div>
            </div>

            {/* Upload Area */}
            {resumeMode === 'upload' ? (
              <div className="space-y-3">
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${
                    isDragging
                      ? 'border-gold-500 bg-gold-50/40 scale-[1.01]'
                      : pdfFile
                      ? 'border-emerald-400 bg-emerald-50/20'
                      : 'border-slate-200 hover:border-forest-300 hover:bg-forest-50/30'
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,application/pdf"
                    onChange={handleFileChange}
                    className="hidden"
                  />

                  <div className="w-14 h-14 mx-auto mb-3 rounded-2xl bg-forest-50 text-forest-800 flex items-center justify-center shadow-xs">
                    {pdfFile ? (
                      <CheckCircle2 className="w-7 h-7 text-emerald-600" />
                    ) : (
                      <FileUp className="w-7 h-7 text-forest-700" />
                    )}
                  </div>

                  {pdfFile ? (
                    <div>
                      <p className="text-sm font-bold text-forest-900">{pdfFile.name}</p>
                      <p className="text-xs text-slate-500 mt-1">
                        {(pdfFile.size / 1024).toFixed(1)} KB &bull; Ready for PyMuPDF extraction
                      </p>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setPdfFile(null);
                        }}
                        className="mt-3 text-xs font-semibold text-rose-600 hover:underline"
                      >
                        Change File
                      </button>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm font-bold text-forest-950">
                        Drop your PDF resume here, or <span className="text-forest-700 underline">browse</span>
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        Supported: Standard PDF documents up to 10MB
                      </p>
                    </div>
                  )}
                </div>

                {/* Sample PDF quick action */}
                <div className="flex items-center justify-between text-xs text-slate-500 pt-1">
                  <span>No PDF on hand?</span>
                  <button
                    type="button"
                    onClick={handleLoadSampleResume}
                    className="text-forest-700 font-semibold hover:underline flex items-center gap-1"
                  >
                    <span>Use Pre-built Alex Rivera Resume</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ) : (
              /* Paste Text Mode */
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Paste complete resume contents below</span>
                  <span>{resumeText.split(/\s+/).filter(Boolean).length} words</span>
                </div>
                <textarea
                  rows={13}
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  placeholder="Paste your resume text here (Summary, Skills, Work Experience, Education, Projects)..."
                  className="w-full p-4 rounded-xl border border-slate-200 text-xs font-mono leading-relaxed focus:ring-2 focus:ring-forest-700 focus:border-transparent outline-none bg-slate-50/50 resize-y"
                />
                <div className="flex items-center justify-between text-xs">
                  <button
                    type="button"
                    onClick={handleLoadSampleResume}
                    className="text-gold-700 font-semibold hover:underline flex items-center gap-1"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-gold-600" />
                    <span>Load Sample Resume Text</span>
                  </button>
                  {resumeText && (
                    <button
                      type="button"
                      onClick={() => setResumeText('')}
                      className="text-slate-400 hover:text-rose-600"
                    >
                      Clear text
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-forest-100/60 text-[11px] text-slate-500 flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
            <span>PyMuPDF extracts text directly from PDF vector streams.</span>
          </div>
        </div>

        {/* Right Column: Job Description Input */}
        <div className="glass-panel p-6 rounded-2xl border border-forest-100 shadow-premium space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gold-50 text-gold-700 flex items-center justify-center font-bold">
                  <Briefcase className="w-4 h-4 text-gold-600" />
                </div>
                <h2 className="font-serif text-lg font-bold text-forest-950">
                  Step 2: Target Job Description
                </h2>
              </div>
            </div>

            {/* Quick Sample Job Role Presets */}
            <div>
              <p className="text-xs font-semibold text-slate-600 mb-2">
                Quick-Load Curated Job Descriptions:
              </p>
              <div className="flex flex-wrap gap-2">
                {sampleJobs.map((job) => (
                  <button
                    key={job.id}
                    type="button"
                    onClick={() => handleSelectSampleJob(job)}
                    className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-forest-50 hover:bg-forest-100 text-forest-800 border border-forest-100 transition-colors"
                  >
                    {job.title}
                  </button>
                ))}
              </div>
            </div>

            {/* Job Title and Company inputs */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold uppercase text-slate-500 mb-1">
                  Job Title
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g. Senior Full Stack Engineer"
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-forest-700 outline-none bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold uppercase text-slate-500 mb-1">
                  Company Name
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={jobCompany}
                    onChange={(e) => setJobCompany(e.target.value)}
                    placeholder="e.g. Nexus Technologies"
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-forest-700 outline-none bg-white"
                  />
                </div>
              </div>
            </div>

            {/* Job Description Textarea */}
            <div>
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                <span>Job Requirements & Responsibilities</span>
                <span>{jobDescription.split(/\s+/).filter(Boolean).length} words</span>
              </div>
              <textarea
                rows={9}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the full job posting requirements, required tech stack, responsibilities, and qualifications..."
                className="w-full p-4 rounded-xl border border-slate-200 text-xs font-mono leading-relaxed focus:ring-2 focus:ring-forest-700 focus:border-transparent outline-none bg-slate-50/50 resize-y"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-forest-100/60 text-[11px] text-slate-500 flex items-center justify-between">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>TF-IDF vectorizer extracts requirements in real-time.</span>
            </span>
            {jobDescription && (
              <button
                type="button"
                onClick={() => {
                  setJobTitle('');
                  setJobCompany('');
                  setJobDescription('');
                }}
                className="text-slate-400 hover:text-rose-600"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Action Bar */}
      <div className="glass-panel p-6 rounded-2xl border border-forest-100 shadow-premium flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="font-serif text-base font-bold text-forest-950">
            Ready to Run Career Intelligence?
          </h3>
          <p className="text-xs text-slate-500">
            Calculates 4-part explainable ATS score, identifies missing critical skills, and provides actionable recommendations.
          </p>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-4 rounded-xl text-sm font-bold bg-forest-800 text-white hover:bg-forest-900 shadow-premium hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          <Sparkles className="w-4 h-4 text-gold-400 group-hover:scale-110 transition-transform" />
          <span>Execute AI Match Analysis</span>
          <ArrowRight className="w-4 h-4 text-gold-400 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
}
