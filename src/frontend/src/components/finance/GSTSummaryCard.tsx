'use client'

import * as React from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatCurrency, formatDate } from '@/lib/format'
import {
  FileText,
  ArrowRight,
  CheckCircle,
  Clock,
  AlertCircle,
  Calendar,
  TrendingUp,
  TrendingDown
} from 'lucide-react'

export interface GSTReturnStatus {
  type: 'GSTR-1' | 'GSTR-3B' | 'GSTR-9' | 'GSTR-2A' | 'GSTR-2B'
  period: string
  status: 'filed' | 'pending' | 'draft' | 'overdue' | 'upcoming'
  dueDate: string
  filedDate?: string
  taxableValue?: number
  taxLiability?: number
  invoiceCount?: number
  link?: string
}

interface GSTSummaryCardProps {
  returnData: GSTReturnStatus
  className?: string
  compact?: boolean
}

export function GSTSummaryCard({ returnData, className, compact = false }: GSTSummaryCardProps) {
  const getStatusConfig = (status: string) => {
    const config: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
      filed: {
        label: 'Filed',
        className: 'bg-green-100 text-green-800',
        icon: <CheckCircle className="h-3 w-3" />
      },
      pending: {
        label: 'Pending',
        className: 'bg-yellow-100 text-yellow-800',
        icon: <Clock className="h-3 w-3" />
      },
      draft: {
        label: 'Draft',
        className: 'bg-gray-100 text-gray-800',
        icon: <FileText className="h-3 w-3" />
      },
      overdue: {
        label: 'Overdue',
        className: 'bg-red-100 text-red-800',
        icon: <AlertCircle className="h-3 w-3" />
      },
      upcoming: {
        label: 'Upcoming',
        className: 'bg-blue-100 text-blue-800',
        icon: <Calendar className="h-3 w-3" />
      }
    }
    return config[status] || config.pending
  }

  const statusConfig = getStatusConfig(returnData.status)

  const getReturnIcon = (type: string) => {
    switch (type) {
      case 'GSTR-1':
        return <TrendingUp className="h-5 w-5 text-blue-600" />
      case 'GSTR-3B':
        return <FileText className="h-5 w-5 text-purple-600" />
      case 'GSTR-9':
        return <Calendar className="h-5 w-5 text-orange-600" />
      case 'GSTR-2A':
      case 'GSTR-2B':
        return <TrendingDown className="h-5 w-5 text-green-600" />
      default:
        return <FileText className="h-5 w-5 text-gray-600" />
    }
  }

  const getReturnDescription = (type: string) => {
    switch (type) {
      case 'GSTR-1':
        return 'Outward Supplies'
      case 'GSTR-3B':
        return 'Summary Return'
      case 'GSTR-9':
        return 'Annual Return'
      case 'GSTR-2A':
        return 'Auto-drafted Inward Supplies'
      case 'GSTR-2B':
        return 'Static Inward Supplies'
      default:
        return 'GST Return'
    }
  }

  if (compact) {
    return (
      <div className={`flex items-center justify-between p-3 bg-muted/50 rounded-lg ${className}`}>
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-background flex items-center justify-center">
            {getReturnIcon(returnData.type)}
          </div>
          <div>
            <p className="font-medium text-sm">{returnData.type}</p>
            <p className="text-xs text-muted-foreground">{returnData.period}</p>
          </div>
        </div>
        <div className="text-right">
          <Badge className={`${statusConfig.className} flex items-center gap-1`}>
            {statusConfig.icon}
            {statusConfig.label}
          </Badge>
          <p className="text-xs text-muted-foreground mt-1">Due: {formatDate(returnData.dueDate)}</p>
        </div>
      </div>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-lg">{returnData.type}</CardTitle>
          <CardDescription>{getReturnDescription(returnData.type)}</CardDescription>
        </div>
        <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
          {getReturnIcon(returnData.type)}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Period</span>
          <span className="font-medium">{returnData.period}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Status</span>
          <Badge className={`${statusConfig.className} flex items-center gap-1`}>
            {statusConfig.icon}
            {statusConfig.label}
          </Badge>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Due Date</span>
          <span className={`font-medium ${returnData.status === 'overdue' ? 'text-red-600' : ''}`}>
            {formatDate(returnData.dueDate)}
          </span>
        </div>

        {returnData.filedDate && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Filed Date</span>
            <span className="font-medium text-green-600">{formatDate(returnData.filedDate)}</span>
          </div>
        )}

        {returnData.invoiceCount !== undefined && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Invoices</span>
            <span className="font-medium">{returnData.invoiceCount}</span>
          </div>
        )}

        {returnData.taxableValue !== undefined && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Taxable Value</span>
            <span className="font-medium">{formatCurrency(returnData.taxableValue)}</span>
          </div>
        )}

        {returnData.taxLiability !== undefined && (
          <div className="flex items-center justify-between pt-2 border-t">
            <span className="font-medium">Tax Liability</span>
            <span className="font-bold text-primary">{formatCurrency(returnData.taxLiability)}</span>
          </div>
        )}

        {returnData.link && (
          <Button className="w-full mt-4" variant="outline" asChild>
            <Link href={returnData.link}>
              View Details <ArrowRight className="h-4 w-4 ml-2" />
            </Link>
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

// Grid component for displaying multiple GST returns
interface GSTReturnsGridProps {
  returns: GSTReturnStatus[]
  columns?: 2 | 3 | 4
  compact?: boolean
}

export function GSTReturnsGrid({ returns, columns = 3, compact = false }: GSTReturnsGridProps) {
  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  }

  return (
    <div className={`grid gap-4 ${gridCols[columns]}`}>
      {returns.map((returnData, index) => (
        <GSTSummaryCard key={index} returnData={returnData} compact={compact} />
      ))}
    </div>
  )
}

// Summary statistics component
interface GSTDashboardStatsProps {
  outputTax: number
  inputTax: number
  netLiability: number
  cashBalance: number
  creditBalance: number
}

export function GSTDashboardStats({
  outputTax,
  inputTax,
  netLiability,
  cashBalance,
  creditBalance
}: GSTDashboardStatsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Output Tax</p>
              <p className="text-xl font-bold text-red-600">{formatCurrency(outputTax)}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-red-500" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Input Tax (ITC)</p>
              <p className="text-xl font-bold text-green-600">{formatCurrency(inputTax)}</p>
            </div>
            <TrendingDown className="h-8 w-8 text-green-500" />
          </div>
        </CardContent>
      </Card>

      <Card className="bg-primary/5 border-primary">
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Net Liability</p>
              <p className="text-xl font-bold text-primary">{formatCurrency(netLiability)}</p>
            </div>
            <FileText className="h-8 w-8 text-primary" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Cash Ledger</p>
              <p className="text-xl font-bold">{formatCurrency(cashBalance)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Credit Ledger</p>
              <p className="text-xl font-bold">{formatCurrency(creditBalance)}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default GSTSummaryCard
