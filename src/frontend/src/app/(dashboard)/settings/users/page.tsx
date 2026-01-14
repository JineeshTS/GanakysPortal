"use client"

import * as React from "react"
import { useSearchParams } from "next/navigation"
import { PageHeader } from "@/components/layout/page-header"
import { RolePermissions, RoleCard, DEFAULT_ROLES, DEFAULT_PERMISSION_MODULES, Role } from "@/components/settings/RolePermissions"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import { FormSelect } from "@/components/forms/form-field"
import { ConfigFormRow } from "@/components/settings/ConfigForm"
import {
  Users,
  UserPlus,
  Search,
  MoreVertical,
  Edit,
  Trash2,
  Shield,
  Mail,
  Phone,
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  KeyRound,
  History,
  Plus,
  Loader2
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

interface User {
  id: string
  name: string
  email: string
  phone: string
  role: string
  department: string
  employeeId: string
  status: 'active' | 'inactive' | 'pending'
  lastLogin?: Date | string
  createdAt: Date | string
}

interface ActivityLog {
  id: string
  userId: string
  userName: string
  action: string
  details: string
  ipAddress: string
  timestamp: Date | string
}

// ============================================================================
// Initial Data
// ============================================================================

const INITIAL_USERS: User[] = [
  {
    id: 'user-1',
    name: 'Rajesh Kumar',
    email: 'rajesh.kumar@ganaportal.in',
    phone: '+91 98765 43210',
    role: 'super_admin',
    department: 'IT',
    employeeId: 'GP001',
    status: 'active',
    lastLogin: new Date('2024-01-05T10:30:00'),
    createdAt: new Date('2023-01-15')
  },
  {
    id: 'user-2',
    name: 'Priya Sharma',
    email: 'priya.sharma@ganaportal.in',
    phone: '+91 98765 43211',
    role: 'hr_manager',
    department: 'HR',
    employeeId: 'GP002',
    status: 'active',
    lastLogin: new Date('2024-01-05T09:15:00'),
    createdAt: new Date('2023-02-20')
  },
  {
    id: 'user-3',
    name: 'Amit Patel',
    email: 'amit.patel@ganaportal.in',
    phone: '+91 98765 43212',
    role: 'payroll_manager',
    department: 'Finance',
    employeeId: 'GP003',
    status: 'active',
    lastLogin: new Date('2024-01-04T16:45:00'),
    createdAt: new Date('2023-03-10')
  },
  {
    id: 'user-4',
    name: 'Sneha Reddy',
    email: 'sneha.reddy@ganaportal.in',
    phone: '+91 98765 43213',
    role: 'team_lead',
    department: 'Engineering',
    employeeId: 'GP010',
    status: 'active',
    lastLogin: new Date('2024-01-05T11:00:00'),
    createdAt: new Date('2023-04-05')
  },
  {
    id: 'user-5',
    name: 'Vikram Singh',
    email: 'vikram.singh@ganaportal.in',
    phone: '+91 98765 43214',
    role: 'employee',
    department: 'Sales',
    employeeId: 'GP025',
    status: 'inactive',
    lastLogin: new Date('2023-12-20T14:30:00'),
    createdAt: new Date('2023-05-15')
  }
]

const ACTIVITY_LOGS: ActivityLog[] = [
  {
    id: 'log-1',
    userId: 'user-1',
    userName: 'Rajesh Kumar',
    action: 'Login',
    details: 'Successful login',
    ipAddress: '192.168.1.100',
    timestamp: new Date('2024-01-05T10:30:00')
  },
  {
    id: 'log-2',
    userId: 'user-2',
    userName: 'Priya Sharma',
    action: 'Update Employee',
    details: 'Updated employee GP050 salary details',
    ipAddress: '192.168.1.101',
    timestamp: new Date('2024-01-05T09:45:00')
  },
  {
    id: 'log-3',
    userId: 'user-3',
    userName: 'Amit Patel',
    action: 'Process Payroll',
    details: 'Initiated December 2024 payroll processing',
    ipAddress: '192.168.1.102',
    timestamp: new Date('2024-01-04T17:00:00')
  },
  {
    id: 'log-4',
    userId: 'user-1',
    userName: 'Rajesh Kumar',
    action: 'Create User',
    details: 'Created new user account for finance team',
    ipAddress: '192.168.1.100',
    timestamp: new Date('2024-01-04T14:20:00')
  },
  {
    id: 'log-5',
    userId: 'user-2',
    userName: 'Priya Sharma',
    action: 'Approve Leave',
    details: 'Approved leave request for GP045',
    ipAddress: '192.168.1.101',
    timestamp: new Date('2024-01-04T11:30:00')
  }
]

const DEPARTMENTS = [
  { value: 'IT', label: 'IT' },
  { value: 'HR', label: 'Human Resources' },
  { value: 'Finance', label: 'Finance' },
  { value: 'Engineering', label: 'Engineering' },
  { value: 'Sales', label: 'Sales' },
  { value: 'Marketing', label: 'Marketing' },
  { value: 'Operations', label: 'Operations' }
]

// ============================================================================
// User Management Page
// ============================================================================

export default function UserManagementPage() {
  const searchParams = useSearchParams()
  const defaultTab = searchParams.get('tab') || 'users'

  const [users, setUsers] = React.useState<User[]>(INITIAL_USERS)
  const [roles, setRoles] = React.useState<Role[]>(DEFAULT_ROLES)
  const [searchQuery, setSearchQuery] = React.useState('')
  const [selectedRole, setSelectedRole] = React.useState<string>('all')
  const [selectedUser, setSelectedUser] = React.useState<User | null>(null)
  const [isUserDialogOpen, setIsUserDialogOpen] = React.useState(false)
  const [isRoleDialogOpen, setIsRoleDialogOpen] = React.useState(false)
  const [editingRole, setEditingRole] = React.useState<Role | null>(null)
  const [isLoading, setIsLoading] = React.useState(false)

  // New user form state
  const [newUser, setNewUser] = React.useState({
    name: '',
    email: '',
    phone: '',
    role: '',
    department: '',
    employeeId: ''
  })

  // New role form state
  const [newRole, setNewRole] = React.useState({
    name: '',
    description: '',
    permissions: [] as string[]
  })

  // Filter users
  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.employeeId.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesRole = selectedRole === 'all' || user.role === selectedRole
    return matchesSearch && matchesRole
  })

  // Get role name by id
  const getRoleName = (roleId: string) => {
    return roles.find(r => r.id === roleId)?.name || roleId
  }

  // Handle user actions
  const handleAddUser = () => {
    setSelectedUser(null)
    setNewUser({
      name: '',
      email: '',
      phone: '',
      role: '',
      department: '',
      employeeId: ''
    })
    setIsUserDialogOpen(true)
  }

  const handleEditUser = (user: User) => {
    setSelectedUser(user)
    setNewUser({
      name: user.name,
      email: user.email,
      phone: user.phone,
      role: user.role,
      department: user.department,
      employeeId: user.employeeId
    })
    setIsUserDialogOpen(true)
  }

  const handleSaveUser = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1000))

    if (selectedUser) {
      // Update existing user
      setUsers(prev => prev.map(u =>
        u.id === selectedUser.id
          ? { ...u, ...newUser }
          : u
      ))
    } else {
      // Create new user
      const user: User = {
        id: `user-${Date.now()}`,
        ...newUser,
        status: 'pending',
        createdAt: new Date()
      }
      setUsers(prev => [...prev, user])
    }

    setIsLoading(false)
    setIsUserDialogOpen(false)
  }

  const handleDeleteUser = (userId: string) => {
    setUsers(prev => prev.filter(u => u.id !== userId))
  }

  const handleToggleUserStatus = (userId: string) => {
    setUsers(prev => prev.map(u =>
      u.id === userId
        ? { ...u, status: u.status === 'active' ? 'inactive' : 'active' }
        : u
    ))
  }

  // Handle role actions
  const handleAddRole = () => {
    setEditingRole(null)
    setNewRole({
      name: '',
      description: '',
      permissions: []
    })
    setIsRoleDialogOpen(true)
  }

  const handleEditRole = (role: Role) => {
    setEditingRole(role)
    setNewRole({
      name: role.name,
      description: role.description,
      permissions: role.permissions
    })
    setIsRoleDialogOpen(true)
  }

  const handleSaveRole = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1000))

    if (editingRole) {
      setRoles(prev => prev.map(r =>
        r.id === editingRole.id
          ? { ...r, ...newRole }
          : r
      ))
    } else {
      const role: Role = {
        id: `role-${Date.now()}`,
        ...newRole,
        userCount: 0
      }
      setRoles(prev => [...prev, role])
    }

    setIsLoading(false)
    setIsRoleDialogOpen(false)
  }

  const handleDeleteRole = (roleId: string) => {
    setRoles(prev => prev.filter(r => r.id !== roleId))
  }

  // Format date
  const formatDate = (date: Date | string | undefined) => {
    if (!date) return 'Never'
    return new Date(date).toLocaleString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="User Management"
        description="Manage users, roles, and access permissions"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings", href: "/settings" },
          { label: "User Management" }
        ]}
        actions={
          <Button onClick={handleAddUser}>
            <UserPlus className="mr-2 h-4 w-4" />
            Add User
          </Button>
        }
      />

      <Tabs defaultValue={defaultTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="roles">Roles & Permissions</TabsTrigger>
          <TabsTrigger value="activity">Activity Log</TabsTrigger>
        </TabsList>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="py-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by name, email, or employee ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <FormSelect
                  label=""
                  name="role-filter"
                  options={[
                    { value: 'all', label: 'All Roles' },
                    ...roles.map(r => ({ value: r.id, label: r.name }))
                  ]}
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  containerClassName="w-full sm:w-48"
                />
              </div>
            </CardContent>
          </Card>

          {/* User List */}
          <div className="space-y-3">
            {filteredUsers.map(user => (
              <Card key={user.id}>
                <CardContent className="py-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-start gap-4">
                      <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold">
                        {user.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{user.name}</h3>
                          <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>
                            {user.status}
                          </Badge>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground mt-1">
                          <span className="flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {user.email}
                          </span>
                          <span className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            {user.phone}
                          </span>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground mt-1">
                          <span className="flex items-center gap-1">
                            <Shield className="h-3 w-3" />
                            {getRoleName(user.role)}
                          </span>
                          <span>{user.department}</span>
                          <span>ID: {user.employeeId}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 sm:self-start">
                      <div className="text-sm text-muted-foreground mr-4 hidden lg:block">
                        <Clock className="h-3 w-3 inline mr-1" />
                        Last login: {formatDate(user.lastLogin)}
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEditUser(user)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleToggleUserStatus(user.id)}
                      >
                        {user.status === 'active' ? (
                          <XCircle className="h-4 w-4 text-destructive" />
                        ) : (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {filteredUsers.length === 0 && (
              <Card>
                <CardContent className="py-12 text-center">
                  <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="font-medium">No users found</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Try adjusting your search or filter
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Roles Tab */}
        <TabsContent value="roles" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold">Roles</h3>
              <p className="text-sm text-muted-foreground">Manage roles and their permissions</p>
            </div>
            <Button onClick={handleAddRole}>
              <Plus className="mr-2 h-4 w-4" />
              Create Role
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {roles.map(role => (
              <RoleCard
                key={role.id}
                role={{
                  ...role,
                  userCount: users.filter(u => u.role === role.id).length
                }}
                onEdit={() => handleEditRole(role)}
                onDelete={() => handleDeleteRole(role.id)}
              />
            ))}
          </div>
        </TabsContent>

        {/* Activity Log Tab */}
        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <History className="h-4 w-4" />
                Recent Activity
              </CardTitle>
              <CardDescription>
                Track user actions and system events
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {ACTIVITY_LOGS.map(log => (
                  <div key={log.id} className="flex items-start gap-4 pb-4 border-b last:border-b-0 last:pb-0">
                    <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                      <History className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{log.userName}</span>
                        <Badge variant="outline">{log.action}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mt-0.5">{log.details}</p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                        <span>{formatDate(log.timestamp)}</span>
                        <span>IP: {log.ipAddress}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* User Dialog */}
      <Dialog open={isUserDialogOpen} onOpenChange={setIsUserDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{selectedUser ? 'Edit User' : 'Add New User'}</DialogTitle>
            <DialogDescription>
              {selectedUser
                ? 'Update user details and permissions'
                : 'Create a new user account with role assignment'
              }
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Full Name *</Label>
                <Input
                  value={newUser.name}
                  onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Rajesh Kumar"
                />
              </div>
              <div className="space-y-2">
                <Label>Employee ID *</Label>
                <Input
                  value={newUser.employeeId}
                  onChange={(e) => setNewUser(prev => ({ ...prev, employeeId: e.target.value }))}
                  placeholder="GP001"
                />
              </div>
            </ConfigFormRow>

            <div className="space-y-2">
              <Label>Email *</Label>
              <Input
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                placeholder="user@company.com"
              />
            </div>

            <div className="space-y-2">
              <Label>Phone</Label>
              <Input
                value={newUser.phone}
                onChange={(e) => setNewUser(prev => ({ ...prev, phone: e.target.value }))}
                placeholder="+91 98765 43210"
              />
            </div>

            <ConfigFormRow columns={2}>
              <FormSelect
                label="Role *"
                name="role"
                options={roles.map(r => ({ value: r.id, label: r.name }))}
                value={newUser.role}
                onChange={(e) => setNewUser(prev => ({ ...prev, role: e.target.value }))}
                placeholder="Select role"
              />
              <FormSelect
                label="Department *"
                name="department"
                options={DEPARTMENTS}
                value={newUser.department}
                onChange={(e) => setNewUser(prev => ({ ...prev, department: e.target.value }))}
                placeholder="Select department"
              />
            </ConfigFormRow>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsUserDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveUser} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                selectedUser ? 'Update User' : 'Create User'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Role Dialog */}
      <Dialog open={isRoleDialogOpen} onOpenChange={setIsRoleDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingRole ? 'Edit Role' : 'Create New Role'}</DialogTitle>
            <DialogDescription>
              {editingRole
                ? 'Update role details and permissions'
                : 'Create a new role with specific permissions'
              }
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Role Name *</Label>
                <Input
                  value={newRole.name}
                  onChange={(e) => setNewRole(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Finance Manager"
                />
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Input
                  value={newRole.description}
                  onChange={(e) => setNewRole(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Brief description of role"
                />
              </div>
            </ConfigFormRow>

            <div>
              <Label className="mb-3 block">Permissions</Label>
              <RolePermissions
                selectedPermissions={newRole.permissions}
                onPermissionsChange={(permissions) => setNewRole(prev => ({ ...prev, permissions }))}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsRoleDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveRole} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                editingRole ? 'Update Role' : 'Create Role'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
