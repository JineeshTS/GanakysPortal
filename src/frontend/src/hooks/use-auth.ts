"use client"

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { useRouter } from 'next/navigation'
import { useCallback } from 'react'
import type { User, LoginRequest, LoginResponse } from '@/types'

// ============================================================================
// Auth Store
// ============================================================================

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  setUser: (user: User | null) => void
  setTokens: (access: string | null, refresh: string | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setUser: (user) => set({
        user,
        isAuthenticated: !!user
      }),

      setTokens: (accessToken, refreshToken) => set({
        accessToken,
        refreshToken,
        isAuthenticated: !!accessToken
      }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      logout: () => set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        error: null
      })
    }),
    {
      name: 'ganaportal-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
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
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    setUser,
    setTokens,
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
        body: formData.toString()
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data: LoginResponse = await response.json()

      setTokens(data.access_token, data.refresh_token)
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
  }, [router, setTokens, setUser, setLoading, setError])

  const logout = useCallback(() => {
    storeLogout()
    router.push('/login')
  }, [router, storeLogout])

  const refreshAccessToken = useCallback(async (): Promise<boolean> => {
    const { refreshToken } = useAuthStore.getState()

    if (!refreshToken) {
      logout()
      return false
    }

    try {
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      })

      if (!response.ok) {
        throw new Error('Token refresh failed')
      }

      const data = await response.json()
      setTokens(data.access_token, data.refresh_token || refreshToken)
      return true
    } catch {
      logout()
      return false
    }
  }, [logout, setTokens])

  const fetchWithAuth = useCallback(async (
    url: string,
    options: RequestInit = {}
  ): Promise<Response> => {
    const { accessToken } = useAuthStore.getState()

    const headers = new Headers(options.headers)
    if (accessToken) {
      headers.set('Authorization', `Bearer ${accessToken}`)
    }

    let response = await fetch(url, { ...options, headers })

    // If 401, try to refresh token
    if (response.status === 401) {
      const refreshed = await refreshAccessToken()
      if (refreshed) {
        const newToken = useAuthStore.getState().accessToken
        headers.set('Authorization', `Bearer ${newToken}`)
        response = await fetch(url, { ...options, headers })
      }
    }

    return response
  }, [refreshAccessToken])

  return {
    user,
    accessToken,
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

  if (typeof window !== 'undefined' && !isLoading && !isAuthenticated) {
    router.push(redirectTo)
  }

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
