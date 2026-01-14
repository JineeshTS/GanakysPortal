"use client"

import * as React from "react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronRight } from "lucide-react"

// ============================================================================
// Settings Card Component
// ============================================================================

interface SettingsCardProps {
  title: string
  description?: string
  icon?: React.ElementType
  href?: string
  onClick?: () => void
  badge?: string
  badgeVariant?: 'default' | 'success' | 'warning' | 'error'
  children?: React.ReactNode
  className?: string
  disabled?: boolean
}

export function SettingsCard({
  title,
  description,
  icon: Icon,
  href,
  onClick,
  badge,
  badgeVariant = 'default',
  children,
  className,
  disabled = false
}: SettingsCardProps) {
  const badgeColors = {
    default: 'bg-muted text-muted-foreground',
    success: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    error: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
  }

  const CardWrapper = href ? Link : 'div'
  const cardProps = href ? { href } : { onClick }

  const cardContent = (
    <Card
      className={cn(
        "transition-all duration-200",
        (href || onClick) && !disabled && "cursor-pointer hover:shadow-md hover:border-primary/50",
        disabled && "opacity-50 cursor-not-allowed",
        className
      )}
    >
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div className="flex items-start gap-3">
          {Icon && (
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
              <Icon className="h-5 w-5 text-primary" />
            </div>
          )}
          <div className="space-y-1">
            <CardTitle className="text-base font-semibold">{title}</CardTitle>
            {description && (
              <CardDescription className="text-sm">{description}</CardDescription>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {badge && (
            <span className={cn("text-xs px-2 py-1 rounded-full font-medium", badgeColors[badgeVariant])}>
              {badge}
            </span>
          )}
          {(href || onClick) && !disabled && (
            <ChevronRight className="h-5 w-5 text-muted-foreground" />
          )}
        </div>
      </CardHeader>
      {children && (
        <CardContent className="pt-0">
          {children}
        </CardContent>
      )}
    </Card>
  )

  if (href && !disabled) {
    return <Link href={href}>{cardContent}</Link>
  }

  if (onClick && !disabled) {
    return <div onClick={onClick}>{cardContent}</div>
  }

  return cardContent
}

// ============================================================================
// Settings Category Grid Component
// ============================================================================

interface SettingsCategoryGridProps {
  children: React.ReactNode
  columns?: 2 | 3
  className?: string
}

export function SettingsCategoryGrid({ children, columns = 2, className }: SettingsCategoryGridProps) {
  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
  }

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {children}
    </div>
  )
}

// ============================================================================
// Settings Section Component
// ============================================================================

interface SettingsSectionProps {
  title: string
  description?: string
  children: React.ReactNode
  className?: string
  action?: React.ReactNode
}

export function SettingsSection({ title, description, children, className, action }: SettingsSectionProps) {
  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{title}</h2>
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
        {action && <div>{action}</div>}
      </div>
      {children}
    </div>
  )
}

export default SettingsCard
