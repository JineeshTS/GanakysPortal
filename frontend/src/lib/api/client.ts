/**
 * API Client for GanaPortal Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

async function getAuthToken(): Promise<string | null> {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // Build URL with query params
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  // Get auth token
  const token = await getAuthToken();

  // Build headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  // Handle 401 - clear tokens and throw error
  // AuthContext handles redirect to login page
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    throw new ApiError('Unauthorized', 401);
  }

  // Parse response
  let data;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  // Handle errors
  if (!response.ok) {
    const message = typeof data === 'object' && data?.detail
      ? data.detail
      : 'An error occurred';
    throw new ApiError(message, response.status, data);
  }

  return data as T;
}

/**
 * Upload FormData with proper auth and error handling
 * Use this for file uploads that require multipart/form-data
 */
async function uploadFormData<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = await getAuthToken();

  const headers: HeadersInit = {};
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  // Don't set Content-Type header - browser will set it with boundary for FormData

  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: formData,
  });

  // Handle 401 - clear tokens and throw error
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    throw new ApiError('Unauthorized', 401);
  }

  // Parse response
  let data;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  // Handle errors
  if (!response.ok) {
    const message = typeof data === 'object' && data?.detail
      ? data.detail
      : 'An error occurred';
    throw new ApiError(message, response.status, data);
  }

  return data as T;
}

/**
 * Download blob (e.g., PDF, Excel files) with proper auth and error handling
 */
async function downloadBlob(endpoint: string): Promise<Blob> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = await getAuthToken();

  const headers: HeadersInit = {};
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, { headers });

  // Handle 401 - clear tokens and throw error
  if (response.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    throw new ApiError('Unauthorized', 401);
  }

  // Handle errors
  if (!response.ok) {
    // Try to parse error message
    let message = 'Failed to download file';
    try {
      const data = await response.json();
      message = data?.detail || message;
    } catch {
      // If not JSON, use default message
    }
    throw new ApiError(message, response.status);
  }

  return response.blob();
}

export const api = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  put: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body?: unknown, options?: RequestOptions) =>
    request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),

  // Special methods for file handling
  uploadFormData,
  downloadBlob,
};

export { ApiError };
export default api;
