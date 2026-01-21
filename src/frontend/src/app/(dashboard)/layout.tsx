'use client'

import * as React from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'
import { useAuthStore } from '@/hooks'
import { LoadingSpinner } from '@/components/layout/loading-spinner'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated, user, _hasHydrated } = useAuthStore()
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(true)

  // Check authentication after hydration
  React.useEffect(() => {
    // Wait for Zustand to hydrate from localStorage
    if (!_hasHydrated) {
      return
    }

    const checkAuth = () => {
      // Check Zustand store (now hydrated from localStorage)
      if (isAuthenticated && user) {
        setIsLoading(false)
        return
      }

      // Not authenticated, redirect to login
      router.push('/login')
    }

    checkAuth()
  }, [_hasHydrated, isAuthenticated, user, router])

  // Close mobile sidebar on route change
  React.useEffect(() => {
    setMobileSidebarOpen(false)
  }, [pathname])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <LoadingSpinner size="lg" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Sidebar Overlay */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 lg:hidden ${
          mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar collapsed={false} />
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-40 lg:block">
        <Sidebar
          collapsed={sidebarCollapsed}
          onCollapsedChange={setSidebarCollapsed}
        />
      </div>

      {/* Main Content */}
      <div
        className={`flex flex-col min-h-screen transition-all duration-300 ${
          sidebarCollapsed ? 'lg:pl-16' : 'lg:pl-64'
        }`}
      >
        {/* Header */}
        <Header onMenuClick={() => setMobileSidebarOpen(true)} />

        {/* Page Content */}
        <main className="flex-1 p-4 lg:p-6">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t py-4 px-6 text-center text-sm text-muted-foreground">
          <p>GanaPortal ERP - India Compliance Ready</p>
          <p className="mt-1">
            PF/ESI/PT/TDS/GST | Built with Next.js 14 & FastAPI
          </p>
        </footer>
      </div>
    </div>
  )
}
