'use client'

import { useState, useEffect } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import {
  Shield,
  ChevronLeft,
  Clock,
  CheckCircle2,
  PlayCircle,
  XCircle,
  Loader2,
  RefreshCw,
  AlertTriangle,
  Target,
  Lock,
  Unlock,
  CheckCircle,
  User,
  Calendar,
} from 'lucide-react'

// Types
interface WBSQualityGate {
  id: string
  gate_code: string
  name: string
  description: string | null
  criteria: string[]
  is_blocking: boolean
  status: 'pending' | 'in_progress' | 'passed' | 'failed'
  verified_at: string | null
  verified_by: string | null
  created_at: string
  updated_at: string
}

// Status config
const statusConfig: Record<string, { color: string; bgColor: string; icon: React.ReactNode; label: string }> = {
  pending: {
    color: 'bg-slate-100 text-slate-700',
    bgColor: 'bg-slate-50 border-slate-200',
    icon: <Clock className="h-5 w-5" />,
    label: 'Pending'
  },
  in_progress: {
    color: 'bg-blue-100 text-blue-700',
    bgColor: 'bg-blue-50 border-blue-200',
    icon: <PlayCircle className="h-5 w-5" />,
    label: 'In Progress'
  },
  passed: {
    color: 'bg-green-100 text-green-700',
    bgColor: 'bg-green-50 border-green-200',
    icon: <CheckCircle2 className="h-5 w-5" />,
    label: 'Passed'
  },
  failed: {
    color: 'bg-red-100 text-red-700',
    bgColor: 'bg-red-50 border-red-200',
    icon: <XCircle className="h-5 w-5" />,
    label: 'Failed'
  },
}

// Quality Gate Card
function QualityGateCard({ gate }: { gate: WBSQualityGate }) {
  const status = statusConfig[gate.status] || statusConfig.pending

  return (
    <Card className={`border-2 ${status.bgColor}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-xl ${status.color}`}>
              {status.icon}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Badge variant="outline" className="text-xs font-mono">
                  {gate.gate_code}
                </Badge>
                {gate.is_blocking ? (
                  <Badge variant="destructive" className="text-xs">
                    <Lock className="h-3 w-3 mr-1" />
                    Blocking
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="text-xs">
                    <Unlock className="h-3 w-3 mr-1" />
                    Non-blocking
                  </Badge>
                )}
              </div>
              <CardTitle className="text-base">{gate.name}</CardTitle>
            </div>
          </div>
          <Badge className={`${status.color}`}>
            {status.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {gate.description && (
          <p className="text-sm text-muted-foreground">{gate.description}</p>
        )}

        {/* Criteria */}
        {gate.criteria.length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2">Criteria</p>
            <ul className="space-y-1">
              {gate.criteria.map((criterion, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <Target className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
                  <span>{criterion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Verification Info */}
        {gate.status === 'passed' && gate.verified_at && (
          <div className="pt-2 border-t space-y-1">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>Verified: {new Date(gate.verified_at).toLocaleString()}</span>
            </div>
            {gate.verified_by && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <User className="h-3 w-3" />
                <span>By: {gate.verified_by}</span>
              </div>
            )}
          </div>
        )}

        {/* Action Button */}
        {gate.status === 'pending' && (
          <Button variant="outline" className="w-full" disabled>
            <Clock className="h-4 w-4 mr-2" />
            Awaiting Prerequisites
          </Button>
        )}
        {gate.status === 'in_progress' && (
          <Button variant="default" className="w-full">
            <CheckCircle className="h-4 w-4 mr-2" />
            Verify Gate
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

// Gate Flow Diagram
function GateFlowDiagram({ gates }: { gates: WBSQualityGate[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Quality Gate Flow</CardTitle>
        <CardDescription>Sequential verification checkpoints</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between overflow-x-auto py-4">
          {gates.map((gate, index) => {
            const status = statusConfig[gate.status] || statusConfig.pending
            return (
              <div key={gate.id} className="flex items-center">
                <div className="flex flex-col items-center min-w-[80px]">
                  <div className={`p-2 rounded-full ${status.color}`}>
                    {status.icon}
                  </div>
                  <p className="text-xs font-medium mt-1">{gate.gate_code}</p>
                  <p className="text-xs text-muted-foreground text-center max-w-[80px] truncate">
                    {gate.name.split(' ')[0]}
                  </p>
                </div>
                {index < gates.length - 1 && (
                  <div className={`w-8 h-0.5 mx-1 ${gate.status === 'passed' ? 'bg-green-500' : 'bg-slate-200'}`} />
                )}
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

export default function WBSQualityGatesPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [gates, setGates] = useState<WBSQualityGate[]>([])

  const fetchGates = async () => {
    setIsLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const res = await fetch(`${apiUrl}/wbs/quality-gates`)
      if (res.ok) {
        const data = await res.json()
        setGates(data)
      }
    } catch (err) {
      console.error('Failed to fetch quality gates:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchGates()
  }, [])

  // Calculate stats
  const totalGates = gates.length
  const passedGates = gates.filter(g => g.status === 'passed').length
  const failedGates = gates.filter(g => g.status === 'failed').length
  const blockingGates = gates.filter(g => g.is_blocking).length

  return (
    <div className="space-y-6">
      <PageHeader
        title="Quality Gates"
        description="Phase verification checkpoints ensuring project quality"
        actions={
          <div className="flex gap-2">
            <Link href="/wbs-dashboard">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Dashboard
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchGates} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Gate Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Gates</p>
                <p className="text-2xl font-bold">{totalGates}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Passed</p>
                <p className="text-2xl font-bold">{passedGates}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-100">
                <XCircle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Failed</p>
                <p className="text-2xl font-bold">{failedGates}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-100">
                <Lock className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Blocking</p>
                <p className="text-2xl font-bold">{blockingGates}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Gate Flow */}
      {gates.length > 0 && <GateFlowDiagram gates={gates} />}

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading quality gates...</span>
        </Card>
      )}

      {/* Gate Cards */}
      {!isLoading && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {gates.map((gate) => (
            <QualityGateCard key={gate.id} gate={gate} />
          ))}
        </div>
      )}

      {!isLoading && gates.length === 0 && (
        <Card className="p-8 text-center">
          <Shield className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No quality gates found</p>
          <p className="text-sm text-muted-foreground mt-1">
            Run the WBS seed script to populate quality gates
          </p>
        </Card>
      )}

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            About Quality Gates
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            <strong>Blocking gates</strong> must be passed before proceeding to the next phase.
            They ensure critical quality and compliance requirements are met.
          </p>
          <p>
            <strong>Non-blocking gates</strong> are recommended checkpoints that don't prevent
            progress but should be addressed for optimal project quality.
          </p>
          <p>
            Each gate has specific criteria that must be verified. Use the verification
            process to mark gates as passed or failed with appropriate documentation.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
