"use client"

import * as React from "react"
import { useSearchParams } from "next/navigation"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useApi, useToast } from "@/hooks"
import { FormSelect } from "@/components/forms/form-field"
import { ConfigFormRow } from "@/components/settings/ConfigForm"
import {
  Users,
  UserPlus,
  Search,
  Edit,
  Trash2,
  Shield,
  Mail,
  Phone,
  Clock,
  CheckCircle,
  XCircle,
  History,
  Loader2,
  AlertTriangle,
  Building2,
  Briefcase,
  UserCheck,
  Send,
  Key,
  Globe,
  Building,
  Landmark
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

interface User {
  id: string
  email: string
  role: string
  category: string | null
  user_type: string | null
  company_id: string
  employee_id: string | null
  organization_name: string | null
  designation: string | null
  phone: string | null
  is_active: boolean
  is_verified: boolean
  expires_at: string | null
  last_login: string | null
  created_at: string
}

interface UserListResponse {
  success: boolean
  data: User[]
  meta: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

interface CategoryInfo {
  value: string
  label: string
  description: string
  types: { value: string; label: string }[]
}

interface CategoriesResponse {
  categories: CategoryInfo[]
}

interface Module {
  id: string
  code: string
  name: string
  category: string
  description: string | null
  icon: string | null
  route: string | null
  is_active: boolean
}

interface PermissionTemplate {
  id: string
  name: string
  code: string
  description: string | null
  category: string
  user_type: string | null
  is_default: boolean
}

interface ActivityLog {
  id: string
  user_id: string
  action: string
  entity_type: string
  entity_id: string
  old_values: string | null
  new_values: string | null
  ip_address: string
  user_agent: string
  created_at: string
}

// ============================================================================
// Constants
// ============================================================================

const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  INTERNAL: <Building2 className="h-4 w-4" />,
  EXTERNAL: <Globe className="h-4 w-4" />,
  GOVERNMENT: <Landmark className="h-4 w-4" />
}

const CATEGORY_COLORS: Record<string, string> = {
  INTERNAL: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  EXTERNAL: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  GOVERNMENT: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
}

const USER_TYPE_LABELS: Record<string, string> = {
  founder: "Founder",
  full_time_employee: "Full-time Employee",
  contract_employee: "Contractor",
  intern: "Intern",
  chartered_accountant: "Chartered Accountant",
  consultant: "Consultant",
  customer: "Customer",
  vendor: "Vendor",
  auditor: "Auditor",
  tax_official: "Tax Official",
  labor_official: "Labor Official",
  other_government: "Other Government"
}

const ROLE_OPTIONS = [
  { value: "admin", label: "Admin" },
  { value: "hr", label: "HR" },
  { value: "accountant", label: "Accountant" },
  { value: "employee", label: "Employee" },
  { value: "external_ca", label: "External CA" }
]

// ============================================================================
// User Management Page
// ============================================================================

export default function UserManagementPage() {
  const searchParams = useSearchParams()
  const defaultTab = searchParams.get('tab') || 'users'

  // API hooks
  const usersApi = useApi<UserListResponse>()
  const categoriesApi = useApi<CategoriesResponse>()
  const modulesApi = useApi<Module[]>()
  const templatesApi = useApi<PermissionTemplate[]>()
  const activityApi = useApi<ActivityLog[]>()
  const userActionApi = useApi()
  const { showToast } = useToast()

  // State
  const [users, setUsers] = React.useState<User[]>([])
  const [categories, setCategories] = React.useState<CategoryInfo[]>([])
  const [modules, setModules] = React.useState<Module[]>([])
  const [templates, setTemplates] = React.useState<PermissionTemplate[]>([])
  const [activityLogs, setActivityLogs] = React.useState<ActivityLog[]>([])
  const [meta, setMeta] = React.useState({ page: 1, limit: 20, total: 0, pages: 0 })

  // Filter state
  const [searchQuery, setSearchQuery] = React.useState('')
  const [selectedCategory, setSelectedCategory] = React.useState<string>('all')
  const [selectedUserType, setSelectedUserType] = React.useState<string>('all')
  const [selectedStatus, setSelectedStatus] = React.useState<string>('all')

  // Dialog state
  const [isUserDialogOpen, setIsUserDialogOpen] = React.useState(false)
  const [isInviteDialogOpen, setIsInviteDialogOpen] = React.useState(false)
  const [selectedUser, setSelectedUser] = React.useState<User | null>(null)
  const [isLoading, setIsLoading] = React.useState(false)

  // Delete state
  const [deleteUserDialogOpen, setDeleteUserDialogOpen] = React.useState(false)
  const [userToDelete, setUserToDelete] = React.useState<User | null>(null)
  const [isDeletingUser, setIsDeletingUser] = React.useState(false)

  // New user form state
  const [newUser, setNewUser] = React.useState({
    email: '',
    password: '',
    role: 'employee',
    category: 'INTERNAL',
    user_type: 'full_time_employee',
    organization_name: '',
    designation: '',
    phone: '',
    access_reason: '',
    template_id: ''
  })

  // Invite form state
  const [inviteData, setInviteData] = React.useState({
    email: '',
    category: 'EXTERNAL',
    user_type: 'chartered_accountant',
    organization_name: '',
    designation: '',
    access_reason: '',
    expires_in_days: 7,
    template_id: ''
  })

  // Fetch data on mount
  React.useEffect(() => {
    fetchUsers()
    fetchCategories()
    fetchModules()
    fetchTemplates()
    fetchActivityLogs()
  }, [])

  // Refetch when filters change
  React.useEffect(() => {
    fetchUsers()
  }, [selectedCategory, selectedUserType, selectedStatus, searchQuery])

  const fetchUsers = async () => {
    const params = new URLSearchParams()
    params.set('page', '1')
    params.set('limit', '50')
    if (selectedCategory !== 'all') params.set('category', selectedCategory)
    if (selectedUserType !== 'all') params.set('user_type', selectedUserType)
    if (selectedStatus !== 'all') params.set('is_active', selectedStatus === 'active' ? 'true' : 'false')
    if (searchQuery) params.set('search', searchQuery)

    const data = await usersApi.get(`/users?${params.toString()}`)
    if (data) {
      setUsers(data.data)
      setMeta(data.meta)
    }
  }

  const fetchCategories = async () => {
    const data = await categoriesApi.get('/users/categories')
    if (data) {
      setCategories(data.categories)
    }
  }

  const fetchModules = async () => {
    const data = await modulesApi.get('/users/modules/list')
    if (data) {
      setModules(data)
    }
  }

  const fetchTemplates = async () => {
    const data = await templatesApi.get('/users/templates/list')
    if (data) {
      setTemplates(data)
    }
  }

  const fetchActivityLogs = async () => {
    // Activity logs endpoint - using audit_logs
    // For now, we'll skip this as it requires a separate endpoint
  }

  // Get available user types for selected category
  const getAvailableUserTypes = (category: string) => {
    const cat = categories.find(c => c.value === category)
    return cat?.types || []
  }

  // Handle user actions
  const handleAddUser = () => {
    setSelectedUser(null)
    setNewUser({
      email: '',
      password: '',
      role: 'employee',
      category: 'INTERNAL',
      user_type: 'full_time_employee',
      organization_name: '',
      designation: '',
      phone: '',
      access_reason: '',
      template_id: ''
    })
    setIsUserDialogOpen(true)
  }

  const handleEditUser = (user: User) => {
    setSelectedUser(user)
    setNewUser({
      email: user.email,
      password: '',
      role: user.role,
      category: user.category || 'INTERNAL',
      user_type: user.user_type || 'full_time_employee',
      organization_name: user.organization_name || '',
      designation: user.designation || '',
      phone: user.phone || '',
      access_reason: '',
      template_id: ''
    })
    setIsUserDialogOpen(true)
  }

  const handleSaveUser = async () => {
    setIsLoading(true)
    try {
      if (selectedUser) {
        // Update existing user
        const result = await userActionApi.put(`/users/${selectedUser.id}`, {
          email: newUser.email,
          role: newUser.role,
          category: newUser.category,
          user_type: newUser.user_type,
          organization_name: newUser.organization_name || null,
          designation: newUser.designation || null,
          phone: newUser.phone || null
        })
        if (result) {
          showToast("success", "User updated successfully")
          fetchUsers()
        }
      } else {
        // Create new user
        const result = await userActionApi.post('/users', {
          email: newUser.email,
          password: newUser.password,
          role: newUser.role,
          category: newUser.category,
          user_type: newUser.user_type,
          organization_name: newUser.organization_name || null,
          designation: newUser.designation || null,
          phone: newUser.phone || null,
          template_id: newUser.template_id || null
        })
        if (result) {
          showToast("success", "User created successfully")
          fetchUsers()
        }
      }
      setIsUserDialogOpen(false)
    } catch (error) {
      showToast("error", "Failed to save user")
    } finally {
      setIsLoading(false)
    }
  }

  const handleInviteUser = () => {
    setInviteData({
      email: '',
      category: 'EXTERNAL',
      user_type: 'chartered_accountant',
      organization_name: '',
      designation: '',
      access_reason: '',
      expires_in_days: 7,
      template_id: ''
    })
    setIsInviteDialogOpen(true)
  }

  const handleSendInvite = async () => {
    setIsLoading(true)
    try {
      const result = await userActionApi.post('/users/invite', {
        email: inviteData.email,
        category: inviteData.category,
        user_type: inviteData.user_type,
        organization_name: inviteData.organization_name || null,
        designation: inviteData.designation || null,
        access_reason: inviteData.access_reason || null,
        expires_in_days: inviteData.expires_in_days,
        template_id: inviteData.template_id || null
      })
      if (result) {
        showToast("success", "Invitation sent successfully")
        setIsInviteDialogOpen(false)
      }
    } catch (error) {
      showToast("error", "Failed to send invitation")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteUserClick = (user: User) => {
    setUserToDelete(user)
    setDeleteUserDialogOpen(true)
  }

  const handleDeleteUserConfirm = async () => {
    if (!userToDelete) return
    setIsDeletingUser(true)
    try {
      await userActionApi.delete(`/users/${userToDelete.id}`)
      showToast("success", "User deactivated successfully")
      fetchUsers()
      setDeleteUserDialogOpen(false)
      setUserToDelete(null)
    } catch (error) {
      showToast("error", "Failed to delete user")
    } finally {
      setIsDeletingUser(false)
    }
  }

  const handleToggleUserStatus = async (user: User) => {
    try {
      await userActionApi.put(`/users/${user.id}`, {
        is_active: !user.is_active
      })
      showToast("success", `User ${user.is_active ? 'deactivated' : 'activated'} successfully`)
      fetchUsers()
    } catch (error) {
      showToast("error", "Failed to update user status")
    }
  }

  const handleResetPassword = async (user: User) => {
    try {
      await userActionApi.post(`/users/${user.id}/reset-password`, {})
      showToast("success", "Password reset email sent")
    } catch (error) {
      showToast("error", "Failed to send password reset")
    }
  }

  // Format date
  const formatDate = (date: string | null | undefined) => {
    if (!date) return 'Never'
    return new Date(date).toLocaleString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Get category badge
  const getCategoryBadge = (category: string | null) => {
    if (!category) return null
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${CATEGORY_COLORS[category] || 'bg-gray-100 text-gray-800'}`}>
        {CATEGORY_ICONS[category]}
        {category}
      </span>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="User Management"
        description="Manage users, categories, and access permissions"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings", href: "/settings" },
          { label: "User Management" }
        ]}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleInviteUser}>
              <Send className="mr-2 h-4 w-4" />
              Invite User
            </Button>
            <Button onClick={handleAddUser}>
              <UserPlus className="mr-2 h-4 w-4" />
              Add User
            </Button>
          </div>
        }
      />

      <Tabs defaultValue={defaultTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="users">Users ({meta.total})</TabsTrigger>
          <TabsTrigger value="templates">Permission Templates</TabsTrigger>
          <TabsTrigger value="modules">Modules</TabsTrigger>
          <TabsTrigger value="activity">Activity Log</TabsTrigger>
        </TabsList>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="py-4">
              <div className="flex flex-col lg:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by email or organization..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-full lg:w-40">
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    <SelectItem value="INTERNAL">Internal</SelectItem>
                    <SelectItem value="EXTERNAL">External</SelectItem>
                    <SelectItem value="GOVERNMENT">Government</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={selectedUserType} onValueChange={setSelectedUserType}>
                  <SelectTrigger className="w-full lg:w-44">
                    <SelectValue placeholder="User Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {Object.entries(USER_TYPE_LABELS).map(([value, label]) => (
                      <SelectItem key={value} value={value}>{label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                  <SelectTrigger className="w-full lg:w-32">
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

          {/* Category Summary Cards */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="border-l-4 border-l-blue-500">
              <CardContent className="py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Internal Users</p>
                    <p className="text-2xl font-bold">{users.filter(u => u.category === 'INTERNAL').length}</p>
                  </div>
                  <Building2 className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
            <Card className="border-l-4 border-l-green-500">
              <CardContent className="py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">External Users</p>
                    <p className="text-2xl font-bold">{users.filter(u => u.category === 'EXTERNAL').length}</p>
                  </div>
                  <Globe className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
            <Card className="border-l-4 border-l-purple-500">
              <CardContent className="py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Government Users</p>
                    <p className="text-2xl font-bold">{users.filter(u => u.category === 'GOVERNMENT').length}</p>
                  </div>
                  <Landmark className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* User List */}
          {usersApi.isLoading ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Loader2 className="h-8 w-8 mx-auto animate-spin text-muted-foreground" />
                <p className="text-sm text-muted-foreground mt-2">Loading users...</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {users.map(user => (
                <Card key={user.id}>
                  <CardContent className="py-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold">
                          {user.email.substring(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <h3 className="font-medium">{user.email}</h3>
                            <Badge variant={user.is_active ? 'default' : 'secondary'}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                            {getCategoryBadge(user.category)}
                          </div>
                          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground mt-1">
                            {user.phone && (
                              <span className="flex items-center gap-1">
                                <Phone className="h-3 w-3" />
                                {user.phone}
                              </span>
                            )}
                            <span className="flex items-center gap-1">
                              <Shield className="h-3 w-3" />
                              {user.role}
                            </span>
                            {user.user_type && (
                              <span className="flex items-center gap-1">
                                <Briefcase className="h-3 w-3" />
                                {USER_TYPE_LABELS[user.user_type] || user.user_type}
                              </span>
                            )}
                          </div>
                          {user.organization_name && (
                            <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                              <Building className="h-3 w-3" />
                              {user.organization_name}
                              {user.designation && ` - ${user.designation}`}
                            </div>
                          )}
                          {user.expires_at && (
                            <div className="flex items-center gap-1 text-sm text-orange-600 mt-1">
                              <Clock className="h-3 w-3" />
                              Expires: {formatDate(user.expires_at)}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 sm:self-start">
                        <div className="text-sm text-muted-foreground mr-4 hidden lg:block">
                          <Clock className="h-3 w-3 inline mr-1" />
                          Last login: {formatDate(user.last_login)}
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleResetPassword(user)}
                          title="Reset Password"
                        >
                          <Key className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEditUser(user)}
                          title="Edit User"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleToggleUserStatus(user)}
                          title={user.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {user.is_active ? (
                            <XCircle className="h-4 w-4 text-destructive" />
                          ) : (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteUserClick(user)}
                          title="Delete User"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {users.length === 0 && (
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
          )}
        </TabsContent>

        {/* Permission Templates Tab */}
        <TabsContent value="templates" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {templates.map(template => (
              <Card key={template.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base">{template.name}</CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                    </div>
                    {template.is_default && (
                      <Badge variant="secondary">Default</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {getCategoryBadge(template.category)}
                    {template.user_type && (
                      <Badge variant="outline">
                        {USER_TYPE_LABELS[template.user_type] || template.user_type}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}

            {templates.length === 0 && (
              <Card className="col-span-full">
                <CardContent className="py-12 text-center">
                  <Shield className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="font-medium">No templates found</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Permission templates will appear here
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Modules Tab */}
        <TabsContent value="modules" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {modules.map(module => (
              <Card key={module.id}>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    {module.name}
                    {module.is_active ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                  </CardTitle>
                  <CardDescription>{module.description || module.code}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Badge variant="outline">{module.category}</Badge>
                </CardContent>
              </Card>
            ))}

            {modules.length === 0 && (
              <Card className="col-span-full">
                <CardContent className="py-12 text-center">
                  <Loader2 className="h-8 w-8 mx-auto animate-spin text-muted-foreground" />
                  <p className="text-sm text-muted-foreground mt-2">Loading modules...</p>
                </CardContent>
              </Card>
            )}
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
              <div className="text-center py-8 text-muted-foreground">
                <History className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Activity logs will be displayed here</p>
                <p className="text-sm">This feature requires audit log endpoint integration</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add/Edit User Dialog */}
      <Dialog open={isUserDialogOpen} onOpenChange={setIsUserDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{selectedUser ? 'Edit User' : 'Add New User'}</DialogTitle>
            <DialogDescription>
              {selectedUser
                ? 'Update user details and category'
                : 'Create a new user account with category and permissions'
              }
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Email *</Label>
              <Input
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                placeholder="user@company.com"
                disabled={!!selectedUser}
              />
            </div>

            {!selectedUser && (
              <div className="space-y-2">
                <Label>Password *</Label>
                <Input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser(prev => ({ ...prev, password: e.target.value }))}
                  placeholder="Min 8 characters"
                />
              </div>
            )}

            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Category *</Label>
                <Select
                  value={newUser.category}
                  onValueChange={(value) => {
                    const types = getAvailableUserTypes(value)
                    setNewUser(prev => ({
                      ...prev,
                      category: value,
                      user_type: types[0]?.value || ''
                    }))
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(cat => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>User Type *</Label>
                <Select
                  value={newUser.user_type}
                  onValueChange={(value) => setNewUser(prev => ({ ...prev, user_type: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {getAvailableUserTypes(newUser.category).map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </ConfigFormRow>

            <div className="space-y-2">
              <Label>Role *</Label>
              <Select
                value={newUser.role}
                onValueChange={(value) => setNewUser(prev => ({ ...prev, role: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ROLE_OPTIONS.map(role => (
                    <SelectItem key={role.value} value={role.value}>
                      {role.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {(newUser.category === 'EXTERNAL' || newUser.category === 'GOVERNMENT') && (
              <>
                <ConfigFormRow columns={2}>
                  <div className="space-y-2">
                    <Label>Organization</Label>
                    <Input
                      value={newUser.organization_name}
                      onChange={(e) => setNewUser(prev => ({ ...prev, organization_name: e.target.value }))}
                      placeholder="Company/Org name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Designation</Label>
                    <Input
                      value={newUser.designation}
                      onChange={(e) => setNewUser(prev => ({ ...prev, designation: e.target.value }))}
                      placeholder="Job title"
                    />
                  </div>
                </ConfigFormRow>
              </>
            )}

            <div className="space-y-2">
              <Label>Phone</Label>
              <Input
                value={newUser.phone}
                onChange={(e) => setNewUser(prev => ({ ...prev, phone: e.target.value }))}
                placeholder="+91 98765 43210"
              />
            </div>

            {!selectedUser && templates.length > 0 && (
              <div className="space-y-2">
                <Label>Permission Template</Label>
                <Select
                  value={newUser.template_id}
                  onValueChange={(value) => setNewUser(prev => ({ ...prev, template_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select template (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    {templates
                      .filter(t => t.category === newUser.category)
                      .map(template => (
                        <SelectItem key={template.id} value={template.id}>
                          {template.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            )}
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

      {/* Invite User Dialog */}
      <Dialog open={isInviteDialogOpen} onOpenChange={setIsInviteDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Invite User</DialogTitle>
            <DialogDescription>
              Send an invitation email to an external user
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Email *</Label>
              <Input
                type="email"
                value={inviteData.email}
                onChange={(e) => setInviteData(prev => ({ ...prev, email: e.target.value }))}
                placeholder="user@external.com"
              />
            </div>

            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Category *</Label>
                <Select
                  value={inviteData.category}
                  onValueChange={(value) => {
                    const types = getAvailableUserTypes(value)
                    setInviteData(prev => ({
                      ...prev,
                      category: value,
                      user_type: types[0]?.value || ''
                    }))
                  }}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EXTERNAL">External</SelectItem>
                    <SelectItem value="GOVERNMENT">Government</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>User Type *</Label>
                <Select
                  value={inviteData.user_type}
                  onValueChange={(value) => setInviteData(prev => ({ ...prev, user_type: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {getAvailableUserTypes(inviteData.category).map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </ConfigFormRow>

            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Organization</Label>
                <Input
                  value={inviteData.organization_name}
                  onChange={(e) => setInviteData(prev => ({ ...prev, organization_name: e.target.value }))}
                  placeholder="Company name"
                />
              </div>
              <div className="space-y-2">
                <Label>Designation</Label>
                <Input
                  value={inviteData.designation}
                  onChange={(e) => setInviteData(prev => ({ ...prev, designation: e.target.value }))}
                  placeholder="Job title"
                />
              </div>
            </ConfigFormRow>

            <div className="space-y-2">
              <Label>Invitation Expires In</Label>
              <Select
                value={String(inviteData.expires_in_days)}
                onValueChange={(value) => setInviteData(prev => ({ ...prev, expires_in_days: Number(value) }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 day</SelectItem>
                  <SelectItem value="3">3 days</SelectItem>
                  <SelectItem value="7">7 days</SelectItem>
                  <SelectItem value="14">14 days</SelectItem>
                  <SelectItem value="30">30 days</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Access Reason</Label>
              <Textarea
                value={inviteData.access_reason}
                onChange={(e) => setInviteData(prev => ({ ...prev, access_reason: e.target.value }))}
                placeholder="Why is this user being granted access?"
                rows={3}
              />
            </div>

            {templates.length > 0 && (
              <div className="space-y-2">
                <Label>Permission Template</Label>
                <Select
                  value={inviteData.template_id}
                  onValueChange={(value) => setInviteData(prev => ({ ...prev, template_id: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select template (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    {templates
                      .filter(t => t.category === inviteData.category)
                      .map(template => (
                        <SelectItem key={template.id} value={template.id}>
                          {template.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsInviteDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSendInvite} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Send Invitation
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete User Confirmation Dialog */}
      <AlertDialog open={deleteUserDialogOpen} onOpenChange={setDeleteUserDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete User
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to deactivate <strong>{userToDelete?.email}</strong>?
              This will prevent them from accessing the system.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeletingUser}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteUserConfirm}
              disabled={isDeletingUser}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeletingUser ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
