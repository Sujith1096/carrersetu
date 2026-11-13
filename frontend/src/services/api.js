// Resolve API base URL: Use VITE_API_URL if configured, otherwise fallback to Vite development proxy '/api'
const resolveApiBase = () => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (!envUrl || !envUrl.trim()) {
    return '/api';
  }
  const clean = envUrl.trim().replace(/\/+$/, '');
  return clean.endsWith('/api') ? clean : `${clean}/api`;
};

export const API_BASE = resolveApiBase();

/**
 * Authentication Token and User Store
 */
export const authStore = {
  getToken: () => {
    try {
      return localStorage.getItem('careersetu_auth_token') || '';
    } catch {
      return '';
    }
  },
  getUser: () => {
    try {
      const u = localStorage.getItem('careersetu_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },
  setAuth: (token, user) => {
    try {
      if (token) localStorage.setItem('careersetu_auth_token', token);
      if (user) localStorage.setItem('careersetu_user', JSON.stringify(user));
    } catch {}
  },
  clear: () => {
    try {
      localStorage.removeItem('careersetu_auth_token');
      localStorage.removeItem('careersetu_user');
    } catch {}
  }
};

/**
 * Isolated Client Session Storage for J.A.R.V.I.S. API Keys.
 * Ensures user keys are stored only in their current browser session and never leak to other users.
 */
export const jarvisSessionStore = {
  getKey: () => {
    try {
      return sessionStorage.getItem('careersetu_jarvis_key') || '';
    } catch {
      return '';
    }
  },
  getProvider: () => {
    try {
      return sessionStorage.getItem('careersetu_jarvis_provider') || 'gemini';
    } catch {
      return 'gemini';
    }
  },
  setCredentials: (provider, key) => {
    try {
      sessionStorage.setItem('careersetu_jarvis_provider', provider || 'gemini');
      sessionStorage.setItem('careersetu_jarvis_key', key || '');
    } catch {}
  },
  clear: () => {
    try {
      sessionStorage.removeItem('careersetu_jarvis_key');
      sessionStorage.removeItem('careersetu_jarvis_provider');
    } catch {}
  }
};

export async function fetchJson(endpoint, options = {}) {
  const token = authStore.getToken();
  const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {};

  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Accept': 'application/json',
      ...authHeaders,
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
  // Authentication & Session
  register: ({ email, password, full_name }) =>
    fetchJson('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name }),
    }),
  login: ({ email, password }) =>
    fetchJson('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }),
  demoLogin: () =>
    fetchJson('/auth/demo-login', {
      method: 'POST',
    }),
  getMe: () => fetchJson('/auth/me'),

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

    const token = authStore.getToken();
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

    const res = await fetch(`${API_BASE}/analyze/upload`, {
      method: 'POST',
      headers,
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

  // J.A.R.V.I.S. AI Assistant (Session isolated)
  jarvisChat: ({ message, conversationHistory = [], context = null, interviewState = null }) => {
    const clientKey = jarvisSessionStore.getKey();
    const clientProvider = jarvisSessionStore.getProvider();
    return fetchJson('/jarvis/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        conversation_history: conversationHistory,
        context,
        interview_state: interviewState,
        client_provider: clientKey ? clientProvider : undefined,
        client_api_key: clientKey ? clientKey : undefined,
      }),
    });
  },

  jarvisStartInterview: (context = null) => {
    const clientKey = jarvisSessionStore.getKey();
    const clientProvider = jarvisSessionStore.getProvider();
    return fetchJson('/jarvis/interview/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        context: context || {},
        client_provider: clientKey ? clientProvider : undefined,
        client_api_key: clientKey ? clientKey : undefined,
      }),
    });
  },

  jarvisGetStatus: () => fetchJson('/jarvis/status'),

  jarvisConfigureKey: async ({ provider, apiKey }) => {
    if (!apiKey || !apiKey.trim()) {
      jarvisSessionStore.clear();
      return fetchJson('/jarvis/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, api_key: '' }),
      });
    }

    const res = await fetchJson('/jarvis/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, api_key: apiKey }),
    });

    jarvisSessionStore.setCredentials(provider, apiKey);
    return res;
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
