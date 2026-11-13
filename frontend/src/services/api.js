const API_BASE = '/api';

export async function fetchJson(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Accept': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorDetail = `Request failed with status ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorDetail = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Health
  checkHealth: () => fetchJson('/health'),

  // Stats & Overview
  getStats: () => fetchJson('/stats'),

  // History
  getHistory: () => fetchJson('/history'),
  getHistoryDetail: (id) => fetchJson(`/history/${id}`),
  deleteHistoryRecord: (id) => fetchJson(`/history/${id}`, { method: 'DELETE' }),
  clearHistory: () => fetchJson('/history', { method: 'DELETE' }),

  // Samples
  getSampleJobs: () => fetchJson('/samples/jobs'),
  getSampleResume: () => fetchJson('/samples/resume'),
  seedDemo: () => fetchJson('/samples/seed', { method: 'POST' }),
  getSamplePdfUrl: () => `${API_BASE}/samples/resume-pdf`,

  // Analysis
  analyzeUpload: async ({ file, jobDescription, jobTitle = 'Target Role', jobCompany = 'Company' }) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);
    formData.append('job_title', jobTitle);
    formData.append('job_company', jobCompany);

    const res = await fetch(`${API_BASE}/analyze/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      let msg = `Upload failed with status ${res.status}`;
      try {
        const err = await res.json();
        if (err.detail) msg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      } catch {}
      throw new Error(msg);
    }
    return res.json();
  },

  analyzeText: ({ resumeText, jobDescription, jobTitle = 'Target Role', jobCompany = 'Company', fileName = 'Pasted_Resume.txt' }) => {
    return fetchJson('/analyze/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_text: resumeText,
        job_description: jobDescription,
        job_title: jobTitle,
        job_company: jobCompany,
        file_name: fileName,
      }),
    });
  },

  // J.A.R.V.I.S. AI Assistant
  jarvisChat: ({ message, conversationHistory = [], context = null, interviewState = null }) => {
    return fetchJson('/jarvis/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
        context,
        interview_state: interviewState,
      }),
    });
  },

  jarvisStartInterview: (context = null) => {
    return fetchJson('/jarvis/interview/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(context || {}),
    });
  },

  jarvisGetStatus: () => fetchJson('/jarvis/status'),

  jarvisConfigureKey: ({ provider, apiKey }) => {
    return fetchJson('/jarvis/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        provider,
        api_key: apiKey,
      }),
    });
  },

  // Global Jobs Explorer
  getJobs: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '' && val !== 'all') {
        query.append(key, val);
      }
    });
    const qs = query.toString();
    return fetchJson(`/jobs${qs ? `?${qs}` : ''}`);
  },

  getJobById: (id) => fetchJson(`/jobs/${id}`),

  syncLiveJobs: () => fetchJson('/jobs/sync', { method: 'POST' }),

  getJobFilterOptions: () => fetchJson('/jobs/filters/options'),

  // Companies Explorer
  getCompanies: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '' && val !== 'all') {
        query.append(key, val);
      }
    });
    const qs = query.toString();
    return fetchJson(`/companies${qs ? `?${qs}` : ''}`);
  },

  getCompanyById: (id) => fetchJson(`/companies/${id}`),
};
