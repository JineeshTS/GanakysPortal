"use client"

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { useRouter } from 'next/navigation'
import { useCallback, useEffect } from 'react'
import type { User, LoginRequest, LoginResponse } from '@/types'

// ============================================================================
// Auth Store
// ============================================================================
// Note: Tokens are now stored in httpOnly cookies for security (XSS protection).
// Only user data is persisted in localStorage.

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  setUser: (user: User | null) => void
  setAuthenticated: (authenticated: boolean) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setUser: (user) => set({
        user,
        isAuthenticated: !!user
      }),

      setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      logout: () => set({
        user: null,
        isAuthenticated: false,
        error: null
      })
    }),
    {
      name: 'ganaportal-auth',
      // Only persist user data, not tokens (tokens are in httpOnly cookies)
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)

// ============================================================================
// Auth Hook
// ============================================================================

// Always use relative path - nginx handles routing to backend
const API_BASE = '/api/v1'

export function useAuth() {
  const router = useRouter()
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    setUser,
    setLoading,
    setError,
    logout: storeLogout
  } = useAuthStore()

  const login = useCallback(async (credentials: LoginRequest): Promise<boolean> => {
    setLoading(true)
    setError(null)

    try {
      // Backend expects OAuth2PasswordRequestForm (form-urlencoded)
      const formData = new URLSearchParams()
      formData.append('username', credentials.email)
      formData.append('password', credentials.password)

      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
        credentials: 'include'  // Send/receive httpOnly cookies
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data: LoginResponse = await response.json()

      // Only store user data - tokens are in httpOnly cookies
      setUser(data.user)

      router.push('/dashboard')
      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed'
      setError(message)
      return false
    } finally {
      setLoading(false)
    }
  }, [router, setUser, setLoading, setError])

  const logout = useCallback(async () => {
    try {
      // Call backend to clear httpOnly cookies and blacklist tokens
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
    } catch {
      // Ignore errors, still clear local state
    }
    storeLogout()
    router.push('/login')
  }, [router, storeLogout])

  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    try {
      // Refresh token is sent via httpOnly cookie automatically
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      // New tokens are set via httpOnly cookies by backend
      return true
    } catch {
      logout()
      return false
    }
  }, [logout])

  const fetchWithAuth = useCallback(async (
    url: string,
    options: RequestInit = {}
  ): Promise<Response> => {
    // Include credentials to send httpOnly cookies
    let response = await fetch(url, {
      ...options,
      credentials: 'include'
    })

    // If 401, try to refresh token
    if (response.status === 401) {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        // Retry with refreshed token (cookies updated automatically)
        response = await fetch(url, {
          ...options,
          credentials: 'include'
        })
      }
    }

    return response
  }, [refreshAccessToken])

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    refreshAccessToken,
    fetchWithAuth
  }
}

// ============================================================================
// Auth Guard Hook
// ============================================================================

export function useRequireAuth(redirectTo: string = '/login') {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuthStore()

  useEffect(() => {
    // Only redirect after loading is complete and user is not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push(redirectTo)
    }
  }, [isLoading, isAuthenticated, router, redirectTo])

  return { isAuthenticated, isLoading }
}

// ============================================================================
// Role-based Access Hook
// ============================================================================

export function useHasRole(allowedRoles: string[]): boolean {
  const { user } = useAuthStore()

  if (!user) return false

  return allowedRoles.includes(user.role)
}

export function useHasPermission(permission: string): boolean {
  const { user } = useAuthStore()

  if (!user) return false

  // Role-based permission mapping
  const rolePermissions: Record<string, string[]> = {
    admin: ['*'],  // Full access for admin role
    super_admin: ['*'],
    company_admin: [
      'employees.*', 'payroll.*', 'leave.*', 'attendance.*',
      'finance.*', 'reports.*', 'settings.*'
    ],
    hr_manager: [
      'employees.*', 'payroll.view', 'payroll.process',
      'leave.*', 'attendance.*', 'reports.hr'
    ],
    hr_executive: [
      'employees.view', 'employees.create', 'employees.edit',
      'leave.view', 'leave.approve', 'attendance.view'
    ],
    finance_manager: [
      'payroll.*', 'finance.*', 'reports.finance', 'invoices.*', 'bills.*'
    ],
    accountant: [
      'payroll.view', 'finance.view', 'finance.create',
      'invoices.*', 'bills.*', 'reports.finance'
    ],
    employee: [
      'self.view', 'self.attendance', 'self.leave', 'self.payslip', 'self.documents'
    ],
    viewer: ['*.view']
  }

  const userPermissions = rolePermissions[user.role] || []

  // Check for wildcard
  if (userPermissions.includes('*')) return true

  // Check for exact match or wildcard patterns
  return userPermissions.some(p => {
    if (p === permission) return true
    if (p.endsWith('.*')) {
      const prefix = p.slice(0, -2)
      return permission.startsWith(prefix)
    }
    if (p.endsWith('.view') && permission === p) return true
    return false
  })
}
