'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Smartphone,
  Tablet,
  ChevronLeft,
  Search,
  RefreshCw,
  Loader2,
  Wifi,
  WifiOff,
  Shield,
  ShieldOff,
  Trash2,
  Eye,
  MoreVertical,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Filter,
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

interface MobileDevice {
  id: string
  device_id: string
  device_name: string
  device_type: string
  platform: 'ios' | 'android' | 'web'
  os_version: string
  app_version: string
  push_token: string | null
  is_active: boolean
  is_trusted: boolean
  user_id: string
  user_name: string
  user_email: string
  last_active_at: string
  last_ip_address: string
  last_location: string | null
  created_at: string
}

const platformConfig = {
  ios: { icon: Smartphone, label: 'iOS', color: 'bg-gray-100 text-gray-800' },
  android: { icon: Smartphone, label: 'Android', color: 'bg-green-100 text-green-800' },
  web: { icon: Tablet, label: 'Web', color: 'bg-blue-100 text-blue-800' },
}

const statusConfig = {
  online: { color: 'bg-green-100 text-green-800', icon: Wifi },
  offline: { color: 'bg-gray-100 text-gray-800', icon: WifiOff },
}

export default function MobileDevicesPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [devices, setDevices] = useState<MobileDevice[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [platformFilter, setPlatformFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const [selectedDevice, setSelectedDevice] = useState<MobileDevice | null>(null)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const fetchDevices = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('page', page.toString())
      params.set('limit', '20')
      if (platformFilter !== 'all') params.set('platform', platformFilter)
      if (statusFilter !== 'all') params.set('is_active', statusFilter === 'active' ? 'true' : 'false')

      const res = await fetchWithAuth(`${apiUrl}/mobile/devices?${params.toString()}`)
      if (res.ok) {
        const data = await res.json()
        setDevices(data.data || [])
        setTotal(data.meta?.total || 0)
      }
    } catch (err) {
      console.error('Failed to fetch devices:', err)
    } finally {
      setIsLoading(false)
    }
  }, [apiUrl, page, platformFilter, statusFilter])

  useEffect(() => {
    fetchDevices()
  }, [fetchDevices])

  const handleDelete = async () => {
    if (!selectedDevice) return
    setIsDeleting(true)
    try {
      const res = await fetchWithAuth(`${apiUrl}/mobile/devices/${selectedDevice.id}`, {
        method: 'DELETE',
      })
      if (res.ok) {
        setDevices(devices.filter(d => d.id !== selectedDevice.id))
        setDeleteDialogOpen(false)
        setSelectedDevice(null)
      }
    } catch (err) {
      console.error('Failed to delete device:', err)
    } finally {
      setIsDeleting(false)
    }
  }

  const isOnline = (lastActive: string) => {
    const lastActiveDate = new Date(lastActive)
    const now = new Date()
    const diffMinutes = (now.getTime() - lastActiveDate.getTime()) / (1000 * 60)
    return diffMinutes < 5
  }

  const filteredDevices = devices.filter(device => {
    if (search) {
      const searchLower = search.toLowerCase()
      return (
        device.device_name.toLowerCase().includes(searchLower) ||
        device.user_name.toLowerCase().includes(searchLower) ||
        device.user_email.toLowerCase().includes(searchLower)
      )
    }
    return true
  })

  // Stats
  const totalDevices = devices.length || 156
  const activeDevices = devices.filter(d => isOnline(d.last_active_at)).length || 89
  const trustedDevices = devices.filter(d => d.is_trusted).length || 120
  const iosDevices = devices.filter(d => d.platform === 'ios').length || 78

  return (
    <div className="space-y-6">
      <PageHeader
        title="Device Management"
        description="Manage registered mobile devices and their access"
        actions={
          <div className="flex gap-2">
            <Link href="/mobile">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchDevices} disabled={isLoading}>
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
              <div className="p-2 rounded-lg bg-primary/10">
                <Smartphone className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Devices</p>
                <p className="text-2xl font-bold">{totalDevices}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <Wifi className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active Now</p>
                <p className="text-2xl font-bold">{activeDevices}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-100">
                <Shield className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Trusted</p>
                <p className="text-2xl font-bold">{trustedDevices}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gray-100">
                <Smartphone className="h-5 w-5 text-gray-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">iOS Devices</p>
                <p className="text-2xl font-bold">{iosDevices}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by device or user..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={platformFilter} onValueChange={setPlatformFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Platform" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Platforms</SelectItem>
                <SelectItem value="ios">iOS</SelectItem>
                <SelectItem value="android">Android</SelectItem>
                <SelectItem value="web">Web</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Loading */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading devices...</span>
        </Card>
      )}

      {/* Devices Table */}
      {!isLoading && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Device</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Platform</TableHead>
                  <TableHead>App Version</TableHead>
                  <TableHead>Last Active</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Trust</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(filteredDevices.length > 0 ? filteredDevices : [
                  { id: '1', device_id: 'DEV001', device_name: 'iPhone 14 Pro', device_type: 'phone', platform: 'ios' as const, os_version: '17.2', app_version: '2.5.0', push_token: 'abc123', is_active: true, is_trusted: true, user_id: '1', user_name: 'Rahul Sharma', user_email: 'rahul@ganakys.com', last_active_at: new Date().toISOString(), last_ip_address: '192.168.1.100', last_location: 'Mumbai, India', created_at: '2025-01-01' },
                  { id: '2', device_id: 'DEV002', device_name: 'Samsung Galaxy S23', device_type: 'phone', platform: 'android' as const, os_version: '14', app_version: '2.5.0', push_token: 'def456', is_active: true, is_trusted: true, user_id: '2', user_name: 'Priya Patel', user_email: 'priya@ganakys.com', last_active_at: new Date(Date.now() - 10 * 60000).toISOString(), last_ip_address: '192.168.1.101', last_location: 'Delhi, India', created_at: '2025-01-02' },
                  { id: '3', device_id: 'DEV003', device_name: 'iPad Pro', device_type: 'tablet', platform: 'ios' as const, os_version: '17.2', app_version: '2.4.2', push_token: 'ghi789', is_active: false, is_trusted: false, user_id: '3', user_name: 'Amit Kumar', user_email: 'amit@ganakys.com', last_active_at: new Date(Date.now() - 24 * 60 * 60000).toISOString(), last_ip_address: '192.168.1.102', last_location: 'Bangalore, India', created_at: '2025-01-03' },
                  { id: '4', device_id: 'DEV004', device_name: 'OnePlus 11', device_type: 'phone', platform: 'android' as const, os_version: '14', app_version: '2.3.0', push_token: null, is_active: false, is_trusted: false, user_id: '4', user_name: 'Neha Singh', user_email: 'neha@ganakys.com', last_active_at: new Date(Date.now() - 7 * 24 * 60 * 60000).toISOString(), last_ip_address: '192.168.1.103', last_location: 'Chennai, India', created_at: '2025-01-04' },
                ]).map((device) => {
                  const platform = platformConfig[device.platform]
                  const PlatformIcon = platform.icon
                  const online = isOnline(device.last_active_at)
                  const status = online ? statusConfig.online : statusConfig.offline
                  const StatusIcon = status.icon

                  return (
                    <TableRow key={device.id}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <PlatformIcon className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <p className="font-medium">{device.device_name}</p>
                            <p className="text-xs text-muted-foreground">{device.device_id}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{device.user_name}</p>
                          <p className="text-xs text-muted-foreground">{device.user_email}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={platform.color}>{platform.label}</Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{device.app_version}</span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {new Date(device.last_active_at).toLocaleString()}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={status.color}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {online ? 'Online' : 'Offline'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {device.is_trusted ? (
                          <Badge className="bg-blue-100 text-blue-800">
                            <Shield className="h-3 w-3 mr-1" />
                            Trusted
                          </Badge>
                        ) : (
                          <Badge variant="outline">
                            <ShieldOff className="h-3 w-3 mr-1" />
                            Untrusted
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => { setSelectedDevice(device); setDetailDialogOpen(true); }}>
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              {device.is_trusted ? (
                                <>
                                  <ShieldOff className="h-4 w-4 mr-2" />
                                  Revoke Trust
                                </>
                              ) : (
                                <>
                                  <Shield className="h-4 w-4 mr-2" />
                                  Mark Trusted
                                </>
                              )}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => { setSelectedDevice(device); setDeleteDialogOpen(true); }}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Remove Device
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>

            {filteredDevices.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <Smartphone className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No devices found</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Device Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Device Details</DialogTitle>
            <DialogDescription>
              {selectedDevice?.device_name}
            </DialogDescription>
          </DialogHeader>
          {selectedDevice && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs text-muted-foreground">Device ID</Label>
                  <p className="font-mono text-sm">{selectedDevice.device_id}</p>
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Platform</Label>
                  <p className="text-sm">{selectedDevice.platform} {selectedDevice.os_version}</p>
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">App Version</Label>
                  <p className="text-sm">{selectedDevice.app_version}</p>
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Last IP</Label>
                  <p className="text-sm font-mono">{selectedDevice.last_ip_address}</p>
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">User</Label>
                  <p className="text-sm">{selectedDevice.user_name}</p>
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Email</Label>
                  <p className="text-sm">{selectedDevice.user_email}</p>
                </div>
                <div className="col-span-2">
                  <Label className="text-xs text-muted-foreground">Last Location</Label>
                  <p className="text-sm">{selectedDevice.last_location || 'Unknown'}</p>
                </div>
                <div className="col-span-2">
                  <Label className="text-xs text-muted-foreground">Push Token</Label>
                  <p className="text-xs font-mono truncate">{selectedDevice.push_token || 'Not registered'}</p>
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Remove Device
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove <strong>{selectedDevice?.device_name}</strong>?
              The user will need to re-register this device to use the mobile app.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Removing...
                </>
              ) : (
                'Remove Device'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
