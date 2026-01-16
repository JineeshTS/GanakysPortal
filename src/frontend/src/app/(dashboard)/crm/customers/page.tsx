'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { formatCurrency, formatDate, formatPhone } from '@/lib/format'
import { useApi } from '@/hooks'
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
  Plus,
  Search,
  Users,
  Building2,
  Mail,
  Phone,
  MapPin,
  IndianRupee,
  TrendingUp,
  Download,
  Eye,
  Edit,
  MoreHorizontal,
  Loader2,
  ArrowLeft,
  Trash2,
  AlertTriangle
} from 'lucide-react'
import type { Customer } from '@/types'

// Mock customers data
const mockCustomers: Customer[] = [
  {
    id: '1',
    company_id: 'comp-1',
    name: 'Tech Solutions Pvt Ltd',
    email: 'contact@techsolutions.in',
    phone: '9876543210',
    gstin: '27AABCT1234F1ZF',
    billing_address: '123 MG Road, Mumbai, Maharashtra 400001',
    credit_limit: 500000,
    credit_days: 30,
    is_active: true,
    created_at: '2025-06-15T10:00:00Z',
    updated_at: '2026-01-05T14:30:00Z'
  },
  {
    id: '2',
    company_id: 'comp-1',
    name: 'Global Mart India',
    email: 'accounts@globalmart.co.in',
    phone: '9988776655',
    gstin: '29AABCG5678H1ZK',
    billing_address: '456 Brigade Road, Bangalore, Karnataka 560001',
    credit_limit: 1000000,
    credit_days: 45,
    is_active: true,
    created_at: '2025-03-20T09:00:00Z',
    updated_at: '2026-01-08T11:00:00Z'
  },
  {
    id: '3',
    company_id: 'comp-1',
    name: 'Innovate Tech Systems',
    email: 'billing@innovatetech.com',
    phone: '8877665544',
    gstin: '33AABCI9012J1ZL',
    billing_address: '789 Anna Salai, Chennai, Tamil Nadu 600002',
    credit_limit: 750000,
    credit_days: 30,
    is_active: true,
    created_at: '2025-08-10T14:00:00Z',
    updated_at: '2026-01-06T16:00:00Z'
  },
  {
    id: '4',
    company_id: 'comp-1',
    name: 'Bharat Finance Ltd',
    email: 'procurement@bharatfinance.in',
    phone: '7766554433',
    gstin: '07AABCB3456K1ZM',
    billing_address: '321 Connaught Place, New Delhi 110001',
    credit_limit: 2000000,
    credit_days: 60,
    is_active: true,
    created_at: '2025-01-05T11:00:00Z',
    updated_at: '2026-01-10T09:00:00Z'
  },
  {
    id: '5',
    company_id: 'comp-1',
    name: 'Sunrise Industries',
    email: 'info@sunriseindustries.co.in',
    phone: '6655443322',
    gstin: '24AABCS7890L1ZN',
    billing_address: '654 SG Highway, Ahmedabad, Gujarat 380015',
    credit_limit: 300000,
    credit_days: 15,
    is_active: false,
    created_at: '2024-11-20T10:00:00Z',
    updated_at: '2025-12-15T14:00:00Z'
  },
]

// Customer stats
interface CustomerStats {
  totalCustomers: number
  activeCustomers: number
  totalRevenue: number
  avgCreditLimit: number
}

export default function CustomersPage() {
  const [customers, setCustomers] = React.useState<Customer[]>(mockCustomers)
  const [searchQuery, setSearchQuery] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<'all' | 'active' | 'inactive'>('all')
  const [isLoading, setIsLoading] = React.useState(true)
  const api = useApi()

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [customerToDelete, setCustomerToDelete] = React.useState<Customer | null>(null)
  const [isDeleting, setIsDeleting] = React.useState(false)
  const deleteApi = useApi()

  const handleDeleteClick = (customer: Customer) => {
    setCustomerToDelete(customer)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!customerToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/crm/customers/${customerToDelete.id}`)
      setCustomers(customers.filter(c => c.id !== customerToDelete.id))
      setDeleteDialogOpen(false)
      setCustomerToDelete(null)
    } catch (error) {
      console.error('Failed to delete customer:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  React.useEffect(() => {
    const fetchCustomers = async () => {
      setIsLoading(true)
      try {
        const result = await api.get('/crm/customers?limit=100')
        if (result?.data && Array.isArray(result.data)) {
          setCustomers(result.data.length > 0 ? result.data : mockCustomers)
        }
      } catch (error) {
        console.error('Failed to fetch customers:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchCustomers()
  }, [])

  const filteredCustomers = React.useMemo(() => {
    return customers.filter(customer => {
      const matchesSearch = !searchQuery ||
        customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        customer.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        customer.gstin?.toLowerCase().includes(searchQuery.toLowerCase())

      const matchesStatus = statusFilter === 'all' ||
        (statusFilter === 'active' && customer.is_active) ||
        (statusFilter === 'inactive' && !customer.is_active)

      return matchesSearch && matchesStatus
    })
  }, [customers, searchQuery, statusFilter])

  const stats: CustomerStats = React.useMemo(() => ({
    totalCustomers: customers.length,
    activeCustomers: customers.filter(c => c.is_active).length,
    totalRevenue: 12500000, // Mock
    avgCreditLimit: customers.reduce((sum, c) => sum + (c.credit_limit || 0), 0) / customers.length
  }), [customers])

  return (
    <div className="space-y-6">
      <PageHeader
        title="Customers"
        description="Manage your customer relationships"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'CRM', href: '/crm' },
          { label: 'Customers' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/crm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Pipeline
              </Link>
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Customer
            </Button>
          </div>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Customers</p>
                <p className="text-2xl font-bold">{stats.totalCustomers}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active Customers</p>
                <p className="text-2xl font-bold text-green-600">{stats.activeCustomers}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-full">
                <IndianRupee className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Revenue</p>
                <p className="text-2xl font-bold text-purple-600">{formatCurrency(stats.totalRevenue)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-100 rounded-full">
                <Building2 className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Avg Credit Limit</p>
                <p className="text-2xl font-bold text-orange-600">{formatCurrency(stats.avgCreditLimit)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search customers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              <Button
                variant={statusFilter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('all')}
              >
                All
              </Button>
              <Button
                variant={statusFilter === 'active' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('active')}
              >
                Active
              </Button>
              <Button
                variant={statusFilter === 'inactive' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('inactive')}
              >
                Inactive
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Customers Table */}
      <Card>
        <CardHeader>
          <CardTitle>Customer List</CardTitle>
          <CardDescription>
            {filteredCustomers.length} customers found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Customer</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Contact</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">GSTIN</th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">Credit Limit</th>
                    <th className="text-center py-3 px-4 font-medium text-muted-foreground">Credit Days</th>
                    <th className="text-center py-3 px-4 font-medium text-muted-foreground">Status</th>
                    <th className="text-center py-3 px-4 font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCustomers.map((customer) => (
                    <tr key={customer.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                            <Building2 className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium">{customer.name}</p>
                            <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                              {customer.billing_address}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="space-y-1 text-sm">
                          {customer.email && (
                            <div className="flex items-center gap-1 text-muted-foreground">
                              <Mail className="h-3 w-3" />
                              <span>{customer.email}</span>
                            </div>
                          )}
                          {customer.phone && (
                            <div className="flex items-center gap-1 text-muted-foreground">
                              <Phone className="h-3 w-3" />
                              <span>{formatPhone(customer.phone)}</span>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 font-mono text-sm">
                        {customer.gstin || '-'}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-sm">
                        {customer.credit_limit ? formatCurrency(customer.credit_limit) : '-'}
                      </td>
                      <td className="py-3 px-4 text-center text-sm">
                        {customer.credit_days ? `${customer.credit_days} days` : '-'}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge className={customer.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                          {customer.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          {!customer.is_active && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDeleteClick(customer)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                  {filteredCustomers.length === 0 && (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-muted-foreground">
                        No customers found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Customer
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{customerToDelete?.name}</strong>?
              This will remove all associated data. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
