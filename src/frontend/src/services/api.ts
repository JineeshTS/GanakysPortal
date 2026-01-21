/**
 * GanaPortal API Client
 * Handles all API communication with the backend
 *
 * Note: Authentication tokens are stored in httpOnly cookies for XSS protection.
 * All requests include credentials: 'include' to send cookies automatically.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: any
  headers?: Record<string, string>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async refreshToken(): Promise<boolean> {
    try {
      // Refresh token is sent via httpOnly cookie automatically
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include'  // Send/receive httpOnly cookies
      })

      if (!response.ok) return false

      // New tokens are set via httpOnly cookies by backend
      return true
    } catch {
      return false
    }
  }

  async request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {} } = options

    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    }

    const config: RequestInit = {
      method,
      headers: requestHeaders,
      credentials: 'include'  // Send httpOnly cookies with every request
    }

    if (body) {
      config.body = JSON.stringify(body)
    }

    let response = await fetch(`${this.baseUrl}${endpoint}`, config)

    // Handle token refresh on 401
    if (response.status === 401) {
      const refreshed = await this.refreshToken()
      if (refreshed) {
        // Retry with refreshed token (cookies updated automatically)
        response = await fetch(`${this.baseUrl}${endpoint}`, config)
      } else {
        // Redirect to login
        window.location.href = '/login'
        throw new Error('Session expired')
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || error.message || 'Request failed')
    }

    return response.json()
  }

  // Convenience methods
  get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  post<T>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body })
  }

  put<T>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body })
  }

  delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  patch<T>(endpoint: string, body?: any): Promise<T> {
    return this.request<T>(endpoint, { method: 'PATCH', body })
  }
}

export const api = new ApiClient(API_BASE_URL)
