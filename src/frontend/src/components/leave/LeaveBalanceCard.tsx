'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Sun,
  Heart,
  Umbrella,
  Baby,
  Briefcase,
  GraduationCap,
  Calendar,
  AlertCircle
} from 'lucide-react'
import type { LeaveBalance } from '@/types'

// ============================================================================
// Leave Type Icons & Colors
// ============================================================================

const leaveTypeConfig: Record<string, {
  icon: React.ElementType
  color: string
  bgColor: string
  borderColor: string
}> = {
  CL: {
    icon: Sun,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200'
  },
  SL: {
    icon: Heart,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200'
  },
  EL: {
    icon: Umbrella,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200'
  },
  PL: {
    icon: Umbrella,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
    borderColor: 'border-indigo-200'
  },
  ML: {
    icon: Baby,
    color: 'text-pink-600',
    bgColor: 'bg-pink-50',
    borderColor: 'border-pink-200'
  },
  PTL: {
    icon: Baby,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200'
  },
  COL: {
    icon: Briefcase,
    color: 'text-gray-600',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200'
  },
  SBL: {
    icon: GraduationCap,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200'
  },
  LWP: {
    icon: Calendar,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200'
  }
}

const defaultConfig = {
  icon: Calendar,
  color: 'text-primary',
  bgColor: 'bg-primary/5',
  borderColor: 'border-primary/20'
}

// ============================================================================
// Leave Balance Card Component
// ============================================================================

interface LeaveBalanceCardProps {
  balance: LeaveBalance
  compact?: boolean
  onClick?: () => void
  className?: string
}

export function LeaveBalanceCard({
  balance,
  compact = false,
  onClick,
  className
}: LeaveBalanceCardProps) {
  const config = leaveTypeConfig[balance.leave_type_code] || defaultConfig
  const Icon = config.icon

  const availablePercentage = balance.opening_balance > 0
    ? (balance.available / (balance.opening_balance + balance.credited)) * 100
    : 0

  if (compact) {
    return (
      <div
        className={cn(
          "flex items-center justify-between p-3 rounded-lg border",
          config.bgColor,
          config.borderColor,
          onClick && "cursor-pointer hover:shadow-sm transition-shadow",
          className
        )}
        onClick={onClick}
      >
        <div className="flex items-center gap-2">
          <Icon className={cn("h-4 w-4", config.color)} />
          <span className="text-sm font-medium">{balance.leave_type_code}</span>
        </div>
        <div className="text-right">
          <span className={cn("text-lg font-bold", config.color)}>
            {balance.available}
          </span>
          <span className="text-xs text-muted-foreground"> / {balance.opening_balance + balance.credited}</span>
        </div>
      </div>
    )
  }

  return (
    <Card
      className={cn(
        "overflow-hidden",
        onClick && "cursor-pointer hover:shadow-md transition-shadow",
        className
      )}
      onClick={onClick}
    >
      <CardHeader className={cn("pb-2", config.bgColor)}>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={cn("p-2 rounded-full bg-white", config.borderColor, "border")}>
              <Icon className={cn("h-4 w-4", config.color)} />
            </div>
            <div>
              <span className="text-sm font-medium">{balance.leave_type_name}</span>
              <p className="text-xs text-muted-foreground">{balance.leave_type_code}</p>
            </div>
          </div>
          <Badge variant="outline" className={cn(config.borderColor, config.color)}>
            {balance.leave_type_code}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4">
        {/* Available Balance */}
        <div className="text-center mb-4">
          <p className="text-4xl font-bold">{balance.available}</p>
          <p className="text-sm text-muted-foreground">days available</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all",
                availablePercentage > 50 ? "bg-green-500" :
                availablePercentage > 25 ? "bg-yellow-500" : "bg-red-500"
              )}
              style={{ width: `${Math.min(availablePercentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Balance Details */}
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Opening:</span>
            <span className="font-medium">{balance.opening_balance}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Credited:</span>
            <span className="font-medium text-green-600">+{balance.credited}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Used:</span>
            <span className="font-medium text-red-600">-{balance.used}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Lapsed:</span>
            <span className="font-medium text-orange-600">-{balance.lapsed}</span>
          </div>
        </div>

        {/* Pending Approval Warning */}
        {balance.pending_approval > 0 && (
          <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded-md flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-yellow-600" />
            <span className="text-xs text-yellow-800">
              {balance.pending_approval} day(s) pending approval
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Leave Balance Grid Component
// ============================================================================

interface LeaveBalanceGridProps {
  balances: LeaveBalance[]
  compact?: boolean
  columns?: 2 | 3 | 4
  onBalanceClick?: (balance: LeaveBalance) => void
  className?: string
}

export function LeaveBalanceGrid({
  balances,
  compact = false,
  columns = 3,
  onBalanceClick,
  className
}: LeaveBalanceGridProps) {
  const gridCols = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
  }

  if (compact) {
    return (
      <div className={cn("grid gap-2", gridCols[columns], className)}>
        {balances.map((balance) => (
          <LeaveBalanceCard
            key={`${balance.leave_type_code}-${balance.year}`}
            balance={balance}
            compact
            onClick={() => onBalanceClick?.(balance)}
          />
        ))}
      </div>
    )
  }

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {balances.map((balance) => (
        <LeaveBalanceCard
          key={`${balance.leave_type_code}-${balance.year}`}
          balance={balance}
          onClick={() => onBalanceClick?.(balance)}
        />
      ))}
    </div>
  )
}

// ============================================================================
// Leave Balance Summary Component (for quick view)
// ============================================================================

interface LeaveBalanceSummaryProps {
  balances: LeaveBalance[]
  className?: string
}

export function LeaveBalanceSummary({ balances, className }: LeaveBalanceSummaryProps) {
  const totalAvailable = balances.reduce((sum, b) => sum + b.available, 0)
  const totalUsed = balances.reduce((sum, b) => sum + b.used, 0)
  const totalPending = balances.reduce((sum, b) => sum + b.pending_approval, 0)

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">Leave Balance Summary</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between gap-4">
          <div className="text-center flex-1">
            <p className="text-2xl font-bold text-green-600">{totalAvailable}</p>
            <p className="text-xs text-muted-foreground">Available</p>
          </div>
          <div className="h-8 w-px bg-border" />
          <div className="text-center flex-1">
            <p className="text-2xl font-bold text-red-600">{totalUsed}</p>
            <p className="text-xs text-muted-foreground">Used</p>
          </div>
          <div className="h-8 w-px bg-border" />
          <div className="text-center flex-1">
            <p className="text-2xl font-bold text-yellow-600">{totalPending}</p>
            <p className="text-xs text-muted-foreground">Pending</p>
          </div>
        </div>

        {/* Quick leave type badges */}
        <div className="mt-4 flex flex-wrap gap-2">
          {balances.map((balance) => {
            const config = leaveTypeConfig[balance.leave_type_code] || defaultConfig
            return (
              <Badge
                key={balance.leave_type_code}
                variant="outline"
                className={cn(config.bgColor, config.borderColor)}
              >
                <span className={config.color}>{balance.leave_type_code}: {balance.available}</span>
              </Badge>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

export default LeaveBalanceCard
