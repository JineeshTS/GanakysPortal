'use client';

/**
 * Dashboard Layout
 * Main layout wrapper for authenticated pages
 */

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Sidebar } from './sidebar';
import { Header } from './header';
import { ProtectedRoute } from '@/components/auth/protected-route';
import type { UserRole } from '@/types/auth';

interface DashboardLayoutProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
}

export function DashboardLayout({ children, allowedRoles }: DashboardLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <ProtectedRoute allowedRoles={allowedRoles}>
      <div className="min-h-screen bg-muted/30">
        <Sidebar isCollapsed={isSidebarCollapsed} />
        <div
          className={cn(
            'flex flex-col transition-all duration-300',
            isSidebarCollapsed ? 'ml-16' : 'ml-64'
          )}
        >
          <Header
            onToggleSidebar={toggleSidebar}
            isSidebarCollapsed={isSidebarCollapsed}
          />
          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </ProtectedRoute>
  );
}

export default DashboardLayout;
