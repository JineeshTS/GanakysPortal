"use client"

import * as React from "react"
import Link from "next/link"
import { useAuthStore } from "@/hooks"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Menu,
  Bell,
  Search,
  Sun,
  Moon,
  User,
  Settings,
  LogOut,
  HelpCircle
} from "lucide-react"

// ============================================================================
// Header Component
// ============================================================================

interface HeaderProps {
  onMenuClick?: () => void
  className?: string
}

export function Header({ onMenuClick, className }: HeaderProps) {
  const { user, logout } = useAuthStore()
  const [isDark, setIsDark] = React.useState(false)
  const [showUserMenu, setShowUserMenu] = React.useState(false)
  const [showNotifications, setShowNotifications] = React.useState(false)
  const [showSearch, setShowSearch] = React.useState(false)

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
  }

  // Mock notifications
  const notifications = [
    { id: 1, title: "Leave request approved", time: "2 min ago", read: false },
    { id: 2, title: "Payroll processed for December", time: "1 hour ago", read: false },
    { id: 3, title: "New employee onboarded", time: "3 hours ago", read: true }
  ]

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <header className={cn(
      "sticky top-0 z-40 flex h-16 items-center gap-4 border-b bg-background px-4 lg:px-6",
      className
    )}>
      {/* Menu Toggle */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
      >
        <Menu className="h-5 w-5" />
        <span className="sr-only">Toggle menu</span>
      </Button>

      {/* Search */}
      <div className="flex-1 max-w-xl">
        {showSearch ? (
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search employees, invoices, projects..."
              className="w-full pl-10 pr-4 py-2 bg-muted rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              autoFocus
              onBlur={() => setShowSearch(false)}
            />
          </div>
        ) : (
          <Button
            variant="ghost"
            className="w-full justify-start text-muted-foreground hidden sm:flex"
            onClick={() => setShowSearch(true)}
          >
            <Search className="mr-2 h-4 w-4" />
            <span>Search...</span>
            <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              <span className="text-xs">⌘</span>K
            </kbd>
          </Button>
        )}
      </div>

      <div className="flex items-center gap-2">
        {/* Theme Toggle */}
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {isDark ? (
            <Sun className="h-5 w-5" />
          ) : (
            <Moon className="h-5 w-5" />
          )}
          <span className="sr-only">Toggle theme</span>
        </Button>

        {/* Notifications */}
        <div className="relative">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setShowNotifications(!showNotifications)}
          >
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 h-4 w-4 rounded-full bg-destructive text-[10px] font-medium text-destructive-foreground flex items-center justify-center">
                {unreadCount}
              </span>
            )}
            <span className="sr-only">Notifications</span>
          </Button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-popover border rounded-lg shadow-lg z-50">
              <div className="p-3 border-b">
                <h3 className="font-semibold">Notifications</h3>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {notifications.map(notification => (
                  <div
                    key={notification.id}
                    className={cn(
                      "p-3 border-b last:border-0 hover:bg-muted cursor-pointer",
                      !notification.read && "bg-primary/5"
                    )}
                  >
                    <p className="text-sm font-medium">{notification.title}</p>
                    <p className="text-xs text-muted-foreground mt-1">{notification.time}</p>
                  </div>
                ))}
              </div>
              <div className="p-2 border-t">
                <Link
                  href="/dashboard/notifications"
                  className="block text-center text-sm text-primary hover:underline"
                  onClick={() => setShowNotifications(false)}
                >
                  View all notifications
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative">
          <Button
            variant="ghost"
            className="flex items-center gap-2"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
              <span className="text-sm font-medium">
                {user?.full_name?.charAt(0).toUpperCase()}
              </span>
            </div>
            <span className="hidden md:inline-block text-sm font-medium">
              {user?.full_name}
            </span>
          </Button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-56 bg-popover border rounded-lg shadow-lg z-50">
              <div className="p-3 border-b">
                <p className="font-medium">{user?.full_name}</p>
                <p className="text-sm text-muted-foreground">{user?.email}</p>
              </div>
              <div className="p-1">
                <Link
                  href="/dashboard/profile"
                  className="flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-muted"
                  onClick={() => setShowUserMenu(false)}
                >
                  <User className="h-4 w-4" />
                  Profile
                </Link>
                <Link
                  href="/dashboard/settings"
                  className="flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-muted"
                  onClick={() => setShowUserMenu(false)}
                >
                  <Settings className="h-4 w-4" />
                  Settings
                </Link>
                <Link
                  href="/help"
                  className="flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-muted"
                  onClick={() => setShowUserMenu(false)}
                >
                  <HelpCircle className="h-4 w-4" />
                  Help & Support
                </Link>
              </div>
              <div className="p-1 border-t">
                <button
                  onClick={() => {
                    setShowUserMenu(false)
                    logout()
                  }}
                  className="flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-muted w-full text-destructive"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
