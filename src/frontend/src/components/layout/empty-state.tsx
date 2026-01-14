"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { FileQuestion, Plus, Search, Users, Receipt, Folder } from "lucide-react"

// ============================================================================
// Empty State Component
// ============================================================================

type EmptyStateType =
  | 'default'
  | 'search'
  | 'employees'
  | 'invoices'
  | 'projects'
  | 'custom'

interface EmptyStateProps {
  type?: EmptyStateType
  title?: string
  description?: string
  icon?: React.ElementType
  action?: {
    label: string
    onClick: () => void
    variant?: 'default' | 'secondary' | 'outline'
  }
  secondaryAction?: {
    label: string
    onClick: () => void
  }
  className?: string
}

const emptyStateDefaults: Record<EmptyStateType, {
  icon: React.ElementType
  title: string
  description: string
}> = {
  default: {
    icon: FileQuestion,
    title: "No data found",
    description: "There's nothing here yet. Get started by adding your first item."
  },
  search: {
    icon: Search,
    title: "No results found",
    description: "Try adjusting your search or filter criteria to find what you're looking for."
  },
  employees: {
    icon: Users,
    title: "No employees yet",
    description: "Start building your team by adding your first employee."
  },
  invoices: {
    icon: Receipt,
    title: "No invoices",
    description: "Create your first invoice to start tracking your sales."
  },
  projects: {
    icon: Folder,
    title: "No projects",
    description: "Create a project to start organizing your work."
  },
  custom: {
    icon: FileQuestion,
    title: "No data",
    description: "Nothing to display."
  }
}

export function EmptyState({
  type = 'default',
  title,
  description,
  icon,
  action,
  secondaryAction,
  className
}: EmptyStateProps) {
  const defaults = emptyStateDefaults[type]
  const Icon = icon || defaults.icon
  const displayTitle = title || defaults.title
  const displayDescription = description || defaults.description

  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-12 px-4 text-center",
      className
    )}>
      <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
        <Icon className="h-8 w-8 text-muted-foreground" />
      </div>

      <h3 className="text-lg font-semibold mb-2">{displayTitle}</h3>
      <p className="text-sm text-muted-foreground max-w-sm mb-6">
        {displayDescription}
      </p>

      <div className="flex items-center gap-3">
        {action && (
          <Button
            variant={action.variant || 'default'}
            onClick={action.onClick}
          >
            <Plus className="h-4 w-4 mr-2" />
            {action.label}
          </Button>
        )}

        {secondaryAction && (
          <Button
            variant="outline"
            onClick={secondaryAction.onClick}
          >
            {secondaryAction.label}
          </Button>
        )}
      </div>
    </div>
  )
}

export default EmptyState
