const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiOptions extends RequestInit {
  token?: string;
}

class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: ApiOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers || {}),
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(
      data?.detail || 'An error occurred',
      response.status,
      data
    );
  }

  return data as T;
}

// Public endpoints (no auth required)
export const publicApi = {
  getJobs: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : '';
    return fetchApi<{ items: Job[]; total: number; page: number; page_size: number }>(
      `/api/v1/public/jobs${query}`
    );
  },

  getJob: (id: string) => {
    return fetchApi<Job>(`/api/v1/public/jobs/${id}`);
  },

  getCompany: (slug: string) => {
    return fetchApi<Company>(`/api/v1/public/companies/${slug}`);
  },
};

// Candidate auth endpoints
export const authApi = {
  register: (data: RegisterData) => {
    return fetchApi<AuthResponse>('/api/v1/candidates/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  login: (data: LoginData) => {
    return fetchApi<AuthResponse>('/api/v1/candidates/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  verifyEmail: (token: string) => {
    return fetchApi<{ message: string }>('/api/v1/candidates/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
  },

  forgotPassword: (email: string) => {
    return fetchApi<{ message: string }>('/api/v1/candidates/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  resetPassword: (data: { token: string; password: string }) => {
    return fetchApi<{ message: string }>('/api/v1/candidates/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  refresh: (refreshToken: string) => {
    return fetchApi<AuthResponse>('/api/v1/candidates/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  },
};

// Candidate profile endpoints (auth required)
export const candidateApi = {
  getProfile: (token: string) => {
    return fetchApi<CandidateProfile>('/api/v1/candidates/me', { token });
  },

  updateProfile: (token: string, data: Partial<CandidateProfile>) => {
    return fetchApi<CandidateProfile>('/api/v1/candidates/me', {
      token,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  uploadResume: async (token: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/v1/candidates/me/resume`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      throw new ApiError(
        data?.detail || 'Upload failed',
        response.status,
        data
      );
    }

    return response.json();
  },

  getResumes: (token: string) => {
    return fetchApi<Resume[]>('/api/v1/candidates/me/resumes', { token });
  },

  deleteResume: (token: string, id: string) => {
    return fetchApi<void>(`/api/v1/candidates/me/resumes/${id}`, {
      token,
      method: 'DELETE',
    });
  },
};

// Application endpoints (auth required)
export const applicationApi = {
  apply: (token: string, data: ApplicationData) => {
    return fetchApi<Application>('/api/v1/candidates/applications', {
      token,
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getApplications: (token: string) => {
    return fetchApi<Application[]>('/api/v1/candidates/applications', { token });
  },

  getApplication: (token: string, id: string) => {
    return fetchApi<Application>(`/api/v1/candidates/applications/${id}`, { token });
  },

  withdraw: (token: string, id: string) => {
    return fetchApi<void>(`/api/v1/candidates/applications/${id}/withdraw`, {
      token,
      method: 'POST',
    });
  },
};

// Interview endpoints (auth required)
export const interviewApi = {
  getInterviews: (token: string) => {
    return fetchApi<Interview[]>('/api/v1/candidates/interviews', { token });
  },

  getInterview: (token: string, id: string) => {
    return fetchApi<Interview>(`/api/v1/candidates/interviews/${id}`, { token });
  },

  joinInterview: (token: string, id: string) => {
    return fetchApi<{ room_url: string; token: string }>(
      `/api/v1/candidates/interviews/${id}/join`,
      { token }
    );
  },

  completeInterview: (token: string, id: string) => {
    return fetchApi<void>(`/api/v1/candidates/interviews/${id}/complete`, {
      token,
      method: 'POST',
    });
  },

  // AI Interview endpoints
  startSession: (token: string, applicationId: string) => {
    return fetchApi<AIInterviewSession>('/api/v1/ai-interview/sessions/start', {
      token,
      method: 'POST',
      body: JSON.stringify({ application_id: applicationId }),
    });
  },

  getSession: (sessionId: string) => {
    const token = getStoredToken();
    return fetchApi<AIInterviewSession>(`/api/v1/ai-interview/sessions/${sessionId}`, { token });
  },

  beginInterview: (sessionId: string) => {
    const token = getStoredToken();
    return fetchApi<{ status: string; message: string }>(
      `/api/v1/ai-interview/sessions/${sessionId}/begin`,
      { token, method: 'POST' }
    );
  },

  getQuestions: (sessionId: string) => {
    const token = getStoredToken();
    return fetchApi<AIInterviewQuestion[]>(
      `/api/v1/ai-interview/sessions/${sessionId}/questions`,
      { token }
    );
  },

  getCurrentQuestion: (sessionId: string) => {
    const token = getStoredToken();
    return fetchApi<AIInterviewQuestion>(
      `/api/v1/ai-interview/sessions/${sessionId}/current-question`,
      { token }
    );
  },

  submitAnswer: (
    sessionId: string,
    questionId: string,
    transcript: string,
    duration: number
  ) => {
    const token = getStoredToken();
    return fetchApi<AIAnswerSubmissionResponse>(
      `/api/v1/ai-interview/sessions/${sessionId}/submit-answer`,
      {
        token,
        method: 'POST',
        body: JSON.stringify({
          question_id: questionId,
          transcript,
          duration_seconds: duration,
        }),
      }
    );
  },

  getResults: (sessionId: string) => {
    const token = getStoredToken();
    return fetchApi<AIInterviewResult>(
      `/api/v1/ai-interview/sessions/${sessionId}/results`,
      { token }
    );
  },

  endInterview: (sessionId: string) => {
    const token = getStoredToken();
    return fetchApi<{ status: string; message: string }>(
      `/api/v1/ai-interview/sessions/${sessionId}/end`,
      { token, method: 'POST' }
    );
  },
};

// Helper to get token from storage (client-side only)
function getStoredToken(): string {
  if (typeof window === 'undefined') return '';
  try {
    const authData = localStorage.getItem('auth-storage');
    if (authData) {
      const parsed = JSON.parse(authData);
      return parsed?.state?.accessToken || '';
    }
  } catch {
    // Ignore parse errors
  }
  return '';
}

// Types
export interface Job {
  id: string;
  title: string;
  company_name?: string;
  department?: string;
  location?: string;
  job_type: string;
  description?: string;
  requirements?: string;
  responsibilities?: string;
  skills_required?: string;
  experience_min?: number;
  experience_max?: number;
  salary_min?: number;
  salary_max?: number;
  is_remote: boolean;
  posted_date?: string;
  closing_date?: string;
  status: string;
  slug?: string;
}

export interface Company {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  website?: string;
  location?: string;
  industry?: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
  };
}

export interface CandidateProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  headline?: string;
  summary?: string;
  avatar_url?: string;
  social_links?: {
    linkedin?: string;
    github?: string;
    twitter?: string;
    portfolio?: string;
  };
  preferences?: {
    job_types?: string[];
    locations?: string[];
    salary_range?: { min: number; max: number };
    remote_only?: boolean;
  };
  profile_completeness: number;
}

export interface Resume {
  id: string;
  file_url: string;
  file_name: string;
  file_type: string;
  is_primary: boolean;
  parsed_data?: unknown;
  parsing_status: string;
  created_at: string;
}

export interface ApplicationData {
  job_id: string;
  resume_id?: string;
  cover_letter?: string;
  expected_salary?: number;
  screening_questions_answers?: Record<string, string>;
}

export interface Application {
  id: string;
  job_id: string;
  job?: Job;
  status: string;
  stage: string;
  applied_date: string;
  cover_letter?: string;
  expected_salary?: number;
  ai_match_score?: number;
  interviews?: Interview[];
}

export interface Interview {
  id: string;
  application_id: string;
  session_type: string;
  status: string;
  scheduled_at?: string;
  started_at?: string;
  completed_at?: string;
  video_room_url?: string;
  overall_score?: number;
  ai_recommendation?: string;
}

// AI Interview Types
export interface AIInterviewSession {
  id: string;
  application_id: string;
  status: string;
  room_url: string | null;
  room_token: string | null;
  scheduled_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  current_question_index: number;
  total_questions: number;
}

export interface AIInterviewQuestion {
  id: string;
  question_text: string;
  question_type: string;
  category: string;
  order_num: number;
  max_duration_seconds: number;
  is_current: boolean;
}

export interface AIAnswerSubmissionResponse {
  success: boolean;
  message: string;
  next_question: AIInterviewQuestion | null;
  interview_complete: boolean;
}

export interface AIInterviewResult {
  session_id: string;
  status: string;
  overall_score: number | null;
  technical_score: number | null;
  communication_score: number | null;
  problem_solving_score: number | null;
  summary: string | null;
  strengths: string[];
  areas_for_improvement: string[];
}

export { ApiError };
