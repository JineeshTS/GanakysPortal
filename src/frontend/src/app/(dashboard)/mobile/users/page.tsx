'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  ChevronLeft,
  RefreshCw,
  Loader2,
  Users,
  User,
  Smartphone,
  Search,
  MoreHorizontal,
  CheckCircle,
  XCircle,
  Clock,
  Shield,
  Mail,
  Phone,
  Building,
  Calendar,
  Activity,
  Lock,
  Unlock,
  UserX,
  UserCheck,
} from 'lucide-react'

interface MobileUser {
  id: string
  employee_id: string
  employee_name: string
  employee_code: string
  email: string
  phone: string
  department: string
  designation: string
  status: 'active' | 'inactive' | 'suspended' | 'pending'
  devices_count: number
  last_active: string | null
  registered_at: string
  permissions: string[]
  two_factor_enabled: boolean
  biometric_enabled: boolean
}

const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  active: { color: 'bg-green-100 text-green-800', icon: <CheckCircle className="h-4 w-4" />, label: 'Active' },
  inactive: { color: 'bg-gray-100 text-gray-800', icon: <Clock className="h-4 w-4" />, label: 'Inactive' },
  suspended: { color: 'bg-red-100 text-red-800', icon: <XCircle className="h-4 w-4" />, label: 'Suspended' },
  pending: { color: 'bg-yellow-100 text-yellow-800', icon: <Clock className="h-4 w-4" />, label: 'Pending' },
}

export default function MobileUsersPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [users, setUsers] = useState<MobileUser[]>([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState<MobileUser | null>(null)

  const { fetchWithAuth } = useAuth()
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const fetchUsers = useCallback(async () => {
    setIsLoading(true)
    try {
      const res = await fetchWithAuth(`${apiUrl}/mobile/users`)
      if (res.ok) {
        const data = await res.json()
        setUsers(data.data || [])
      }
    } catch (err) {
      console.error('Failed to fetch users:', err)
    } finally {
      setIsLoading(false)
    }
  }, [apiUrl])

  useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

  // Mock data
  const mockUsers: MobileUser[] = [
    { id: '1', employee_id: 'e1', employee_name: 'Rahul Sharma', employee_code: 'EMP001', email: 'rahul.sharma@company.com', phone: '+91 98765 43210', department: 'Engineering', designation: 'Senior Developer', status: 'active', devices_count: 2, last_active: '2026-01-17T10:30:00Z', registered_at: '2025-06-15T09:00:00Z', permissions: ['attendance', 'leave', 'expenses', 'approvals'], two_factor_enabled: true, biometric_enabled: true },
    { id: '2', employee_id: 'e2', employee_name: 'Priya Patel', employee_code: 'EMP002', email: 'priya.patel@company.com', phone: '+91 98765 43211', department: 'Finance', designation: 'Finance Manager', status: 'active', devices_count: 1, last_active: '2026-01-17T09:45:00Z', registered_at: '2025-07-20T11:00:00Z', permissions: ['attendance', 'leave', 'expenses', 'approvals', 'reports'], two_factor_enabled: true, biometric_enabled: false },
    { id: '3', employee_id: 'e3', employee_name: 'Amit Kumar', employee_code: 'EMP003', email: 'amit.kumar@company.com', phone: '+91 98765 43212', department: 'HR', designation: 'HR Executive', status: 'inactive', devices_count: 1, last_active: '2026-01-10T14:00:00Z', registered_at: '2025-08-01T10:00:00Z', permissions: ['attendance', 'leave'], two_factor_enabled: false, biometric_enabled: true },
    { id: '4', employee_id: 'e4', employee_name: 'Neha Singh', employee_code: 'EMP004', email: 'neha.singh@company.com', phone: '+91 98765 43213', department: 'Sales', designation: 'Sales Manager', status: 'suspended', devices_count: 0, last_active: '2025-12-20T16:00:00Z', registered_at: '2025-05-10T09:00:00Z', permissions: ['attendance', 'leave', 'expenses'], two_factor_enabled: false, biometric_enabled: false },
    { id: '5', employee_id: 'e5', employee_name: 'Vikram Rao', employee_code: 'EMP005', email: 'vikram.rao@company.com', phone: '+91 98765 43214', department: 'Operations', designation: 'Operations Lead', status: 'active', devices_count: 3, last_active: '2026-01-17T11:00:00Z', registered_at: '2025-04-05T08:00:00Z', permissions: ['attendance', 'leave', 'expenses', 'approvals', 'inventory'], two_factor_enabled: true, biometric_enabled: true },
    { id: '6', employee_id: 'e6', employee_name: 'Sunita Gupta', employee_code: 'EMP006', email: 'sunita.gupta@company.com', phone: '+91 98765 43215', department: 'Marketing', designation: 'Marketing Executive', status: 'pending', devices_count: 0, last_active: null, registered_at: '2026-01-15T12:00:00Z', permissions: ['attendance', 'leave'], two_factor_enabled: false, biometric_enabled: false },
  ]

  const displayUsers = users.length > 0 ? users : mockUsers
  const filteredUsers = displayUsers.filter(u => {
    const matchesSearch = u.employee_name.toLowerCase().includes(search.toLowerCase()) ||
      u.employee_code.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = statusFilter === 'all' || u.status === statusFilter
    return matchesSearch && matchesStatus
  })

  // Stats
  const activeUsers = mockUsers.filter(u => u.status === 'active').length
  const totalDevices = mockUsers.reduce((sum, u) => sum + u.devices_count, 0)
  const twoFactorEnabled = mockUsers.filter(u => u.two_factor_enabled).length
  const biometricEnabled = mockUsers.filter(u => u.biometric_enabled).length

  const handleSuspendUser = async (userId: string) => {
    try {
      const res = await fetchWithAuth(`${apiUrl}/mobile/users/${userId}/suspend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      if (res.ok) {
        // Update local state
        setUsers(prev => prev.map(u =>
          u.id === userId ? { ...u, status: 'suspended' as const } : u
        ))
      } else {
        console.error('Failed to suspend user')
      }
    } catch (err) {
      console.error('Failed to suspend user:', err)
    }
  }

  const handleActivateUser = async (userId: string) => {
    try {
      const res = await fetchWithAuth(`${apiUrl}/mobile/users/${userId}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      if (res.ok) {
        // Update local state
        setUsers(prev => prev.map(u =>
          u.id === userId ? { ...u, status: 'active' as const } : u
        ))
      } else {
        console.error('Failed to activate user')
      }
    } catch (err) {
      console.error('Failed to activate user:', err)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mobile Users"
        description="Manage users with mobile app access"
        actions={
          <div className="flex gap-2">
            <Link href="/mobile">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <Button onClick={fetchUsers} disabled={isLoading}>
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
                <Users className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Users</p>
                <p className="text-2xl font-bold">{mockUsers.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <UserCheck className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active Users</p>
                <p className="text-2xl font-bold">{activeUsers}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-100">
                <Smartphone className="h-5 w-5 text-blue-600" />
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
              <div className="p-2 rounded-lg bg-purple-100">
                <Shield className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">2FA Enabled</p>
                <p className="text-2xl font-bold">{twoFactorEnabled}</p>
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
                  placeholder="Search users..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Loading */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading users...</span>
        </Card>
      )}

      {/* Users Table */}
      {!isLoading && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Devices</TableHead>
                  <TableHead>Security</TableHead>
                  <TableHead>Last Active</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => {
                  const status = statusConfig[user.status] || statusConfig.pending

                  return (
                    <TableRow
                      key={user.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => { setSelectedUser(user); setDetailDialogOpen(true); }}
                    >
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-9 w-9">
                            <AvatarFallback className="text-xs">
                              {user.employee_name.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{user.employee_name}</p>
                            <p className="text-xs text-muted-foreground">{user.employee_code} | {user.designation}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm">
                          <Building className="h-3 w-3 text-muted-foreground" />
                          {user.department}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm space-y-1">
                          <div className="flex items-center gap-1">
                            <Mail className="h-3 w-3 text-muted-foreground" />
                            <span className="truncate max-w-[150px]">{user.email}</span>
                          </div>
                          <div className="flex items-center gap-1 text-muted-foreground">
                            <Phone className="h-3 w-3" />
                            <span>{user.phone}</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Smartphone className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium">{user.devices_count}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {user.two_factor_enabled && (
                            <Badge variant="outline" className="text-xs">2FA</Badge>
                          )}
                          {user.biometric_enabled && (
                            <Badge variant="outline" className="text-xs">Bio</Badge>
                          )}
                          {!user.two_factor_enabled && !user.biometric_enabled && (
                            <span className="text-muted-foreground text-sm">Basic</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {user.last_active
                          ? new Date(user.last_active).toLocaleDateString()
                          : 'Never'}
                      </TableCell>
                      <TableCell>
                        <Badge className={status.color}>
                          {status.icon}
                          <span className="ml-1">{status.label}</span>
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={(e) => { e.stopPropagation(); setSelectedUser(user); setDetailDialogOpen(true); }}>
                              <User className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            {user.status === 'active' ? (
                              <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleSuspendUser(user.id); }} className="text-red-600">
                                <UserX className="h-4 w-4 mr-2" />
                                Suspend User
                              </DropdownMenuItem>
                            ) : (
                              <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleActivateUser(user.id); }} className="text-green-600">
                                <UserCheck className="h-4 w-4 mr-2" />
                                Activate User
                              </DropdownMenuItem>
                            )}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>

            {filteredUsers.length === 0 && (
              <div className="text-center py-12">
                <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No users found</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>User Details</DialogTitle>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-4 py-4">
              {/* User Info */}
              <div className="flex items-center gap-4 pb-4 border-b">
                <Avatar className="h-14 w-14">
                  <AvatarFallback className="text-lg">
                    {selectedUser.employee_name.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <p className="font-medium text-lg">{selectedUser.employee_name}</p>
                  <p className="text-sm text-muted-foreground">{selectedUser.designation}</p>
                  <Badge className={statusConfig[selectedUser.status]?.color + ' mt-1'}>
                    {statusConfig[selectedUser.status]?.label}
                  </Badge>
                </div>
              </div>

              {/* Contact */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span>{selectedUser.email}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span>{selectedUser.phone}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Building className="h-4 w-4 text-muted-foreground" />
                  <span>{selectedUser.department}</span>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                <div className="text-center">
                  <p className="text-2xl font-bold">{selectedUser.devices_count}</p>
                  <p className="text-xs text-muted-foreground">Devices</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold">{selectedUser.permissions.length}</p>
                  <p className="text-xs text-muted-foreground">Permissions</p>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium">
                    {selectedUser.last_active
                      ? new Date(selectedUser.last_active).toLocaleDateString()
                      : 'Never'}
                  </p>
                  <p className="text-xs text-muted-foreground">Last Active</p>
                </div>
              </div>

              {/* Security */}
              <div className="pt-4 border-t">
                <p className="text-sm font-medium mb-2">Security Features</p>
                <div className="flex gap-2">
                  <Badge variant={selectedUser.two_factor_enabled ? 'default' : 'outline'}>
                    {selectedUser.two_factor_enabled ? <Lock className="h-3 w-3 mr-1" /> : <Unlock className="h-3 w-3 mr-1" />}
                    Two-Factor Auth
                  </Badge>
                  <Badge variant={selectedUser.biometric_enabled ? 'default' : 'outline'}>
                    {selectedUser.biometric_enabled ? <Lock className="h-3 w-3 mr-1" /> : <Unlock className="h-3 w-3 mr-1" />}
                    Biometric
                  </Badge>
                </div>
              </div>

              {/* Permissions */}
              <div className="pt-4 border-t">
                <p className="text-sm font-medium mb-2">Permissions</p>
                <div className="flex flex-wrap gap-1">
                  {selectedUser.permissions.map((perm) => (
                    <Badge key={perm} variant="secondary" className="capitalize">
                      {perm}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Registered */}
              <div className="text-xs text-muted-foreground pt-2 border-t">
                Registered: {new Date(selectedUser.registered_at).toLocaleDateString()}
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
    </div>
  )
}
