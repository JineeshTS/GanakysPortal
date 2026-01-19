'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  RefreshCw,
  ChevronLeft,
  Loader2,
  Cloud,
  CloudOff,
  Download,
  Upload,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Database,
  Smartphone,
  ArrowUpDown,
  Wifi,
  WifiOff,
} from 'lucide-react'

interface SyncRecord {
  id: string
  device_id: string
  device_name: string
  user_name: string
  sync_type: 'full' | 'incremental' | 'selective'
  direction: 'upload' | 'download' | 'bidirectional'
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'partial'
  entities_synced: number
  entities_total: number
  conflicts_count: number
  bytes_transferred: number
  started_at: string
  completed_at: string | null
  error_message: string | null
}

interface OfflineAction {
  id: string
  device_id: string
  action_type: 'create' | 'update' | 'delete'
  entity_type: string
  entity_id: string
  payload: Record<string, any>
  status: 'pending' | 'synced' | 'conflict' | 'failed'
  created_at: string
  synced_at: string | null
}

const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  pending: { color: 'bg-yellow-100 text-yellow-800', icon: <Clock className="h-4 w-4" />, label: 'Pending' },
  in_progress: { color: 'bg-blue-100 text-blue-800', icon: <RefreshCw className="h-4 w-4 animate-spin" />, label: 'In Progress' },
  completed: { color: 'bg-green-100 text-green-800', icon: <CheckCircle className="h-4 w-4" />, label: 'Completed' },
  failed: { color: 'bg-red-100 text-red-800', icon: <XCircle className="h-4 w-4" />, label: 'Failed' },
  partial: { color: 'bg-orange-100 text-orange-800', icon: <AlertTriangle className="h-4 w-4" />, label: 'Partial' },
  synced: { color: 'bg-green-100 text-green-800', icon: <CheckCircle className="h-4 w-4" />, label: 'Synced' },
  conflict: { color: 'bg-purple-100 text-purple-800', icon: <AlertTriangle className="h-4 w-4" />, label: 'Conflict' },
}

const directionConfig: Record<string, { icon: React.ReactNode; label: string }> = {
  upload: { icon: <Upload className="h-4 w-4" />, label: 'Upload' },
  download: { icon: <Download className="h-4 w-4" />, label: 'Download' },
  bidirectional: { icon: <ArrowUpDown className="h-4 w-4" />, label: 'Bidirectional' },
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export default function MobileSyncPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [syncRecords, setSyncRecords] = useState<SyncRecord[]>([])
  const [offlineActions, setOfflineActions] = useState<OfflineAction[]>([])
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [activeTab, setActiveTab] = useState<'sync' | 'offline'>('sync')
  const { fetchWithAuth } = useAuth()

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const [syncRes, actionsRes] = await Promise.all([
        fetchWithAuth(`${apiUrl}/mobile/sync-logs`),
        fetchWithAuth(`${apiUrl}/mobile/offline-actions`),
      ])

      if (syncRes.ok) {
        const data = await syncRes.json()
        setSyncRecords(data.data || [])
      }
      if (actionsRes.ok) {
        const data = await actionsRes.json()
        setOfflineActions(data.data || [])
      }
    } catch (err) {
      console.error('Failed to fetch sync data:', err)
    } finally {
      setIsLoading(false)
    }
  }, [apiUrl, fetchWithAuth])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Mock data for demo
  const mockSyncRecords: SyncRecord[] = [
    { id: '1', device_id: 'd1', device_name: 'iPhone 15 Pro', user_name: 'Rahul Sharma', sync_type: 'incremental', direction: 'bidirectional', status: 'completed', entities_synced: 45, entities_total: 45, conflicts_count: 0, bytes_transferred: 256000, started_at: '2026-01-17T10:30:00Z', completed_at: '2026-01-17T10:30:45Z', error_message: null },
    { id: '2', device_id: 'd2', device_name: 'Samsung Galaxy S24', user_name: 'Priya Patel', sync_type: 'full', direction: 'download', status: 'in_progress', entities_synced: 120, entities_total: 250, conflicts_count: 0, bytes_transferred: 1024000, started_at: '2026-01-17T10:35:00Z', completed_at: null, error_message: null },
    { id: '3', device_id: 'd3', device_name: 'iPad Pro', user_name: 'Amit Kumar', sync_type: 'selective', direction: 'upload', status: 'failed', entities_synced: 10, entities_total: 25, conflicts_count: 2, bytes_transferred: 50000, started_at: '2026-01-17T09:00:00Z', completed_at: '2026-01-17T09:01:00Z', error_message: 'Network timeout after 60 seconds' },
    { id: '4', device_id: 'd4', device_name: 'OnePlus 12', user_name: 'Neha Singh', sync_type: 'incremental', direction: 'bidirectional', status: 'partial', entities_synced: 30, entities_total: 35, conflicts_count: 5, bytes_transferred: 180000, started_at: '2026-01-17T08:30:00Z', completed_at: '2026-01-17T08:31:00Z', error_message: null },
    { id: '5', device_id: 'd5', device_name: 'Pixel 8 Pro', user_name: 'Vikram Rao', sync_type: 'full', direction: 'download', status: 'completed', entities_synced: 500, entities_total: 500, conflicts_count: 0, bytes_transferred: 5120000, started_at: '2026-01-16T18:00:00Z', completed_at: '2026-01-16T18:05:00Z', error_message: null },
  ]

  const mockOfflineActions: OfflineAction[] = [
    { id: '1', device_id: 'd1', action_type: 'create', entity_type: 'Expense', entity_id: 'new-1', payload: { amount: 1500, description: 'Cab fare' }, status: 'pending', created_at: '2026-01-17T10:00:00Z', synced_at: null },
    { id: '2', device_id: 'd1', action_type: 'update', entity_type: 'Attendance', entity_id: 'att-123', payload: { check_out: '18:30' }, status: 'synced', created_at: '2026-01-17T09:00:00Z', synced_at: '2026-01-17T10:30:00Z' },
    { id: '3', device_id: 'd3', action_type: 'create', entity_type: 'Leave', entity_id: 'new-2', payload: { type: 'sick', days: 1 }, status: 'conflict', created_at: '2026-01-17T08:00:00Z', synced_at: null },
    { id: '4', device_id: 'd4', action_type: 'update', entity_type: 'Task', entity_id: 'task-456', payload: { status: 'completed' }, status: 'pending', created_at: '2026-01-17T11:00:00Z', synced_at: null },
    { id: '5', device_id: 'd2', action_type: 'delete', entity_type: 'Draft', entity_id: 'draft-789', payload: {}, status: 'failed', created_at: '2026-01-17T07:00:00Z', synced_at: null },
  ]

  const displaySyncRecords = syncRecords.length > 0 ? syncRecords : mockSyncRecords
  const displayOfflineActions = offlineActions.length > 0 ? offlineActions : mockOfflineActions

  // Stats
  const completedSyncs = mockSyncRecords.filter(s => s.status === 'completed').length
  const failedSyncs = mockSyncRecords.filter(s => s.status === 'failed').length
  const pendingActions = mockOfflineActions.filter(a => a.status === 'pending').length
  const conflictActions = mockOfflineActions.filter(a => a.status === 'conflict').length

  return (
    <div className="space-y-6">
      <PageHeader
        title="Sync & Offline"
        description="Monitor device synchronization and manage offline actions"
        actions={
          <div className="flex gap-2">
            <Link href="/mobile">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <Button onClick={fetchData} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <Cloud className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Syncs Completed</p>
                <p className="text-2xl font-bold">{completedSyncs}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-100">
                <CloudOff className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Syncs Failed</p>
                <p className="text-2xl font-bold">{failedSyncs}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-yellow-100">
                <WifiOff className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Pending Actions</p>
                <p className="text-2xl font-bold">{pendingActions}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-100">
                <AlertTriangle className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Conflicts</p>
                <p className="text-2xl font-bold">{conflictActions}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tab Toggle */}
      <div className="flex gap-2">
        <Button
          variant={activeTab === 'sync' ? 'default' : 'outline'}
          onClick={() => setActiveTab('sync')}
        >
          <Cloud className="h-4 w-4 mr-2" />
          Sync History
        </Button>
        <Button
          variant={activeTab === 'offline' ? 'default' : 'outline'}
          onClick={() => setActiveTab('offline')}
        >
          <WifiOff className="h-4 w-4 mr-2" />
          Offline Actions
        </Button>
      </div>

      {/* Loading */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading sync data...</span>
        </Card>
      )}

      {/* Sync History Table */}
      {!isLoading && activeTab === 'sync' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Sync History</CardTitle>
            <CardDescription>Recent device synchronization records</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Device</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Direction</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead>Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {displaySyncRecords.map((record) => {
                  const status = statusConfig[record.status] || statusConfig.pending
                  const direction = directionConfig[record.direction] || directionConfig.bidirectional
                  const progress = record.entities_total > 0
                    ? Math.round((record.entities_synced / record.entities_total) * 100)
                    : 0

                  return (
                    <TableRow key={record.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Smartphone className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium">{record.device_name}</span>
                        </div>
                      </TableCell>
                      <TableCell>{record.user_name}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">{record.sync_type}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          {direction.icon}
                          <span className="text-sm">{direction.label}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="w-24">
                          <Progress value={progress} className="h-2" />
                          <p className="text-xs text-muted-foreground mt-1">
                            {record.entities_synced}/{record.entities_total}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={status.color}>
                          {status.icon}
                          <span className="ml-1">{status.label}</span>
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm">
                        {formatBytes(record.bytes_transferred)}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(record.started_at).toLocaleTimeString()}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* Offline Actions Table */}
      {!isLoading && activeTab === 'offline' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Offline Actions Queue</CardTitle>
            <CardDescription>Actions performed offline pending synchronization</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Action</TableHead>
                  <TableHead>Entity</TableHead>
                  <TableHead>Device</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Synced</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {displayOfflineActions.map((action) => {
                  const status = statusConfig[action.status] || statusConfig.pending

                  return (
                    <TableRow key={action.id}>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {action.action_type}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{action.entity_type}</p>
                          <p className="text-xs text-muted-foreground">{action.entity_id}</p>
                        </div>
                      </TableCell>
                      <TableCell className="text-sm">{action.device_id}</TableCell>
                      <TableCell>
                        <Badge className={status.color}>
                          {status.icon}
                          <span className="ml-1">{status.label}</span>
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(action.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {action.synced_at ? new Date(action.synced_at).toLocaleString() : '-'}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>

            {displayOfflineActions.length === 0 && (
              <div className="text-center py-12">
                <Wifi className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No offline actions in queue</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Database className="h-4 w-4 text-primary" />
            About Sync & Offline
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            <strong>Incremental Sync</strong> only transfers changes since the last sync,
            minimizing data usage and sync time.
          </p>
          <p>
            <strong>Offline Actions</strong> are queued when users work without connectivity
            and automatically synced when connection is restored.
          </p>
          <p>
            <strong>Conflicts</strong> occur when the same record is modified on multiple devices.
            These require manual resolution to ensure data integrity.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
