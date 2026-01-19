"use client"

import { useState, useCallback } from 'react'
import { useAuthStore } from './use-auth'
import type { ApiResponse, PaginatedResponse, PaginationParams } from '@/types'

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

// ============================================================================
// API Hook
// ============================================================================

interface UseApiOptions {
  requireAuth?: boolean
}

interface UseApiState<T> {
  data: T | null
  error: string | null
  isLoading: boolean
}

export function useApi<T>(options: UseApiOptions = { requireAuth: true }) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    isLoading: false
  })

  const { logout } = useAuthStore()

  // Note: Authentication tokens are now stored in httpOnly cookies.
  // credentials: 'include' sends cookies automatically with each request.
  const getHeaders = useCallback((): HeadersInit => {
    return {
      'Content-Type': 'application/json'
    }
  }, [])

  const handleResponse = useCallback(async <R>(response: Response): Promise<R> => {
    if (response.status === 401) {
      logout()
      throw new Error('Session expired. Please login again.')
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || errorData.message || 'Request failed')
    }

    return response.json()
  }, [logout])

  const get = useCallback(async (endpoint: string): Promise<T | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'GET',
        headers: getHeaders(),
        credentials: 'include'
      })

      const data = await handleResponse<T>(response)
      setState({ data, error: null, isLoading: false })
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Request failed'
      setState(prev => ({ ...prev, error: message, isLoading: false }))
      return null
    }
  }, [getHeaders, handleResponse])

  const post = useCallback(async <D>(endpoint: string, body: D): Promise<T | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: getHeaders(),
        credentials: 'include',
        body: JSON.stringify(body)
      })

      const data = await handleResponse<T>(response)
      setState({ data, error: null, isLoading: false })
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Request failed'
      setState(prev => ({ ...prev, error: message, isLoading: false }))
      return null
    }
  }, [getHeaders, handleResponse])

  const put = useCallback(async <D>(endpoint: string, body: D): Promise<T | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'PUT',
        headers: getHeaders(),
        credentials: 'include',
        body: JSON.stringify(body)
      })

      const data = await handleResponse<T>(response)
      setState({ data, error: null, isLoading: false })
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Request failed'
      setState(prev => ({ ...prev, error: message, isLoading: false }))
      return null
    }
  }, [getHeaders, handleResponse])

  const patch = useCallback(async <D>(endpoint: string, body: D): Promise<T | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'PATCH',
        headers: getHeaders(),
        credentials: 'include',
        body: JSON.stringify(body)
      })

      const data = await handleResponse<T>(response)
      setState({ data, error: null, isLoading: false })
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Request failed'
      setState(prev => ({ ...prev, error: message, isLoading: false }))
      return null
    }
  }, [getHeaders, handleResponse])

  const del = useCallback(async (endpoint: string): Promise<boolean> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'DELETE',
        headers: getHeaders(),
        credentials: 'include'
      })

      if (response.status === 401) {
        logout()
        throw new Error('Session expired. Please login again.')
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Delete failed')
      }

      setState(prev => ({ ...prev, isLoading: false }))
      return true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Delete failed'
      setState(prev => ({ ...prev, error: message, isLoading: false }))
      return false
    }
  }, [getHeaders, logout])

  return {
    ...state,
    get,
    post,
    put,
    patch,
    delete: del,
    setData: (data: T | null) => setState(prev => ({ ...prev, data })),
    setError: (error: string | null) => setState(prev => ({ ...prev, error })),
    clearError: () => setState(prev => ({ ...prev, error: null }))
  }
}

// ============================================================================
// Paginated API Hook
// ============================================================================

interface UsePaginatedApiState<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
  error: string | null
  isLoading: boolean
}

export function usePaginatedApi<T>(baseEndpoint: string) {
  const [state, setState] = useState<UsePaginatedApiState<T>>({
    data: [],
    total: 0,
    page: 1,
    pageSize: 20,
    totalPages: 0,
    error: null,
    isLoading: false
  })

  const { logout } = useAuthStore()

  const fetch = useCallback(async (
    params: PaginationParams & Record<string, unknown> = { page: 1, page_size: 20 }
  ): Promise<void> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          searchParams.set(key, String(value))
        }
      })

      const url = `${API_BASE}${baseEndpoint}?${searchParams.toString()}`

      const response = await globalThis.fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      })

      if (response.status === 401) {
        logout()
        throw new Error('Session expired')
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Request failed')
      }

      const result: PaginatedResponse<T> = await response.json()

      setState({
        data: result.items,
        total: result.total,
        page: result.page,
        pageSize: result.page_size,
        totalPages: result.total_pages,
        error: null,
        isLoading: false
      })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Request failed'
      setState(prev => ({ ...prev, error: message, isLoading: false }))
    }
  }, [baseEndpoint, logout])

  const goToPage = useCallback((page: number) => {
    fetch({ page, page_size: state.pageSize })
  }, [fetch, state.pageSize])

  const setPageSize = useCallback((pageSize: number) => {
    fetch({ page: 1, page_size: pageSize })
  }, [fetch])

  return {
    ...state,
    fetch,
    goToPage,
    setPageSize,
    refresh: () => fetch({ page: state.page, page_size: state.pageSize })
  }
}

// ============================================================================
// Mutation Hook
// ============================================================================

interface MutationOptions<T, D> {
  onSuccess?: (data: T) => void
  onError?: (error: string) => void
}

export function useMutation<T, D = unknown>(
  endpoint: string,
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST',
  options: MutationOptions<T, D> = {}
) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { logout } = useAuthStore()

  const mutate = useCallback(async (data?: D): Promise<T | null> => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: data ? JSON.stringify(data) : undefined
      })

      if (response.status === 401) {
        logout()
        throw new Error('Session expired')
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Request failed')
      }

      const result: T = await response.json()
      options.onSuccess?.(result)
      return result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Request failed'
      setError(message)
      options.onError?.(message)
      return null
    } finally {
      setIsLoading(false)
    }
  }, [endpoint, logout, method, options])

  return { mutate, isLoading, error }
}
