"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

// ============================================================================
// Stat Card Component
// ============================================================================

interface StatCardProps {
  title: string
  value: string | number
  description?: string
  icon?: React.ElementType
  trend?: {
    value: number
    label?: string
    type?: 'increase' | 'decrease' | 'neutral'
  }
  className?: string
  valueClassName?: string
}

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  className,
  valueClassName
}: StatCardProps) {
  const getTrendIcon = () => {
    if (!trend) return null

    const trendType = trend.type || (trend.value > 0 ? 'increase' : trend.value < 0 ? 'decrease' : 'neutral')

    const icons = {
      increase: TrendingUp,
      decrease: TrendingDown,
      neutral: Minus
    }

    const colors = {
      increase: 'text-green-500',
      decrease: 'text-red-500',
      neutral: 'text-muted-foreground'
    }

    const TrendIcon = icons[trendType]

    return (
      <div className={cn("flex items-center gap-1 text-sm", colors[trendType])}>
        <TrendIcon className="h-4 w-4" />
        <span>{Math.abs(trend.value)}%</span>
        {trend.label && (
          <span className="text-muted-foreground ml-1">{trend.label}</span>
        )}
      </div>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {Icon && (
          <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center">
            <Icon className="h-4 w-4 text-primary" />
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className={cn("text-2xl font-bold", valueClassName)}>
          {value}
        </div>
        <div className="flex items-center justify-between mt-1">
          {description && (
            <p className="text-xs text-muted-foreground">{description}</p>
          )}
          {getTrendIcon()}
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Stats Grid Component
// ============================================================================

interface StatsGridProps {
  stats: StatCardProps[]
  columns?: 2 | 3 | 4
  className?: string
}

export function StatsGrid({ stats, columns = 4, className }: StatsGridProps) {
  const gridCols = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
  }

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  )
}

export default StatCard
