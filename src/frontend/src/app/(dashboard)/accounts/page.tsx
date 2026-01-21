'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatCurrency } from '@/lib/format'
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
import { useApi } from '@/hooks'
import {
  Plus,
  ChevronRight,
  ChevronDown,
  Building2,
  Wallet,
  CreditCard,
  TrendingUp,
  TrendingDown,
  Search,
  Download,
  Trash2,
  AlertTriangle,
  Loader2
} from 'lucide-react'
import type { Account, AccountType } from '@/types'

// Mock Chart of Accounts data
interface AccountNode extends Account {
  children?: AccountNode[]
  expanded?: boolean
}

const mockAccounts: AccountNode[] = [
  {
    id: '1',
    code: '1000',
    name: 'Assets',
    type: 'asset',
    balance: 4567890,
    is_active: true,
    is_system: true,
    gst_applicable: false,
    company_id: '1',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    children: [
      {
        id: '1-1',
        code: '1100',
        name: 'Current Assets',
        type: 'asset',
        parent_id: '1',
        balance: 3456780,
        is_active: true,
        is_system: true,
        gst_applicable: false,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        children: [
          {
            id: '1-1-1',
            code: '1110',
            name: 'Cash in Hand',
            type: 'cash',
            parent_id: '1-1',
            balance: 125000,
            is_active: true,
            is_system: true,
            gst_applicable: false,
            company_id: '1',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          },
          {
            id: '1-1-2',
            code: '1120',
            name: 'Bank Accounts',
            type: 'bank',
            parent_id: '1-1',
            balance: 2345780,
            is_active: true,
            is_system: true,
            gst_applicable: false,
            company_id: '1',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            children: [
              {
                id: '1-1-2-1',
                code: '1121',
                name: 'HDFC Bank - Current A/c',
                type: 'bank',
                parent_id: '1-1-2',
                balance: 1845780,
                is_active: true,
                is_system: false,
                gst_applicable: false,
                company_id: '1',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z'
              },
              {
                id: '1-1-2-2',
                code: '1122',
                name: 'ICICI Bank - Salary A/c',
                type: 'bank',
                parent_id: '1-1-2',
                balance: 500000,
                is_active: true,
                is_system: false,
                gst_applicable: false,
                company_id: '1',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z'
              }
            ]
          },
          {
            id: '1-1-3',
            code: '1130',
            name: 'Accounts Receivable',
            type: 'receivable',
            parent_id: '1-1',
            balance: 986000,
            is_active: true,
            is_system: true,
            gst_applicable: false,
            company_id: '1',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          }
        ]
      },
      {
        id: '1-2',
        code: '1200',
        name: 'Fixed Assets',
        type: 'asset',
        parent_id: '1',
        balance: 1111110,
        is_active: true,
        is_system: true,
        gst_applicable: false,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        children: [
          {
            id: '1-2-1',
            code: '1210',
            name: 'Furniture & Fixtures',
            type: 'asset',
            parent_id: '1-2',
            balance: 345000,
            is_active: true,
            is_system: false,
            gst_applicable: true,
            hsn_code: '9403',
            company_id: '1',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          },
          {
            id: '1-2-2',
            code: '1220',
            name: 'Computer Equipment',
            type: 'asset',
            parent_id: '1-2',
            balance: 766110,
            is_active: true,
            is_system: false,
            gst_applicable: true,
            hsn_code: '8471',
            company_id: '1',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          }
        ]
      }
    ]
  },
  {
    id: '2',
    code: '2000',
    name: 'Liabilities',
    type: 'liability',
    balance: 1234560,
    is_active: true,
    is_system: true,
    gst_applicable: false,
    company_id: '1',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    children: [
      {
        id: '2-1',
        code: '2100',
        name: 'Current Liabilities',
        type: 'liability',
        parent_id: '2',
        balance: 1234560,
        is_active: true,
        is_system: true,
        gst_applicable: false,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        children: [
          {
            id: '2-1-1',
            code: '2110',
            name: 'Accounts Payable',
            type: 'payable',
            parent_id: '2-1',
            balance: 567890,
            is_active: true,
            is_system: true,
            gst_applicable: false,
            company_id: '1',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          },
          {
            id: '2-1-2',
            code: '2120',
            name: 'Statutory Dues',
            type: 'liability',
            parent_id: '2-1',
            balance: 456670,
            is_active: true,
            is_system: true,
            gst_applicable: false,
            company_id: '1',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
            children: [
              {
                id: '2-1-2-1',
                code: '2121',
                name: 'GST Payable',
                type: 'liability',
                parent_id: '2-1-2',
                balance: 189000,
                is_active: true,
                is_system: true,
                gst_applicable: false,
                company_id: '1',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z'
              },
              {
                id: '2-1-2-2',
                code: '2122',
                name: 'TDS Payable',
                type: 'liability',
                parent_id: '2-1-2',
                balance: 156200,
                is_active: true,
                is_system: true,
                gst_applicable: false,
                company_id: '1',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z'
              },
              {
                id: '2-1-2-3',
                code: '2123',
                name: 'PF Payable',
                type: 'liability',
                parent_id: '2-1-2',
                balance: 111470,
                is_active: true,
                is_system: true,
                gst_applicable: false,
                company_id: '1',
                created_at: '2024-01-01T00:00:00Z',
                updated_at: '2024-01-01T00:00:00Z'
              }
            ]
          },
          {
            id: '2-1-3',
            code: '2130',
            name: 'Salary Payable',
            type: 'liability',
            parent_id: '2-1',
            balance: 210000,
            is_active: true,
            is_system: true,
            gst_applicable: false,
            company_id: '1',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          }
        ]
      }
    ]
  },
  {
    id: '3',
    code: '3000',
    name: 'Equity',
    type: 'equity',
    balance: 2500000,
    is_active: true,
    is_system: true,
    gst_applicable: false,
    company_id: '1',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    children: [
      {
        id: '3-1',
        code: '3100',
        name: 'Share Capital',
        type: 'equity',
        parent_id: '3',
        balance: 1000000,
        is_active: true,
        is_system: true,
        gst_applicable: false,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: '3-2',
        code: '3200',
        name: 'Retained Earnings',
        type: 'equity',
        parent_id: '3',
        balance: 1500000,
        is_active: true,
        is_system: true,
        gst_applicable: false,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    ]
  },
  {
    id: '4',
    code: '4000',
    name: 'Revenue',
    type: 'revenue',
    balance: 5678900,
    is_active: true,
    is_system: true,
    gst_applicable: false,
    company_id: '1',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    children: [
      {
        id: '4-1',
        code: '4100',
        name: 'Sales Revenue',
        type: 'revenue',
        parent_id: '4',
        balance: 5500000,
        is_active: true,
        is_system: true,
        gst_applicable: true,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: '4-2',
        code: '4200',
        name: 'Service Revenue',
        type: 'revenue',
        parent_id: '4',
        balance: 178900,
        is_active: true,
        is_system: true,
        gst_applicable: true,
        hsn_code: '998314',
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    ]
  },
  {
    id: '5',
    code: '5000',
    name: 'Expenses',
    type: 'expense',
    balance: 3456780,
    is_active: true,
    is_system: true,
    gst_applicable: false,
    company_id: '1',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    children: [
      {
        id: '5-1',
        code: '5100',
        name: 'Salary & Wages',
        type: 'expense',
        parent_id: '5',
        balance: 2100000,
        is_active: true,
        is_system: true,
        gst_applicable: false,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: '5-2',
        code: '5200',
        name: 'Rent Expense',
        type: 'expense',
        parent_id: '5',
        balance: 600000,
        is_active: true,
        is_system: false,
        gst_applicable: true,
        hsn_code: '997212',
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: '5-3',
        code: '5300',
        name: 'Utilities',
        type: 'expense',
        parent_id: '5',
        balance: 156780,
        is_active: true,
        is_system: false,
        gst_applicable: true,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: '5-4',
        code: '5400',
        name: 'Professional Fees',
        type: 'expense',
        parent_id: '5',
        balance: 300000,
        is_active: true,
        is_system: false,
        gst_applicable: true,
        hsn_code: '998231',
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: '5-5',
        code: '5500',
        name: 'Depreciation',
        type: 'expense',
        parent_id: '5',
        balance: 300000,
        is_active: true,
        is_system: true,
        gst_applicable: false,
        company_id: '1',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
    ]
  }
]

export default function ChartOfAccountsPage() {
  const router = useRouter()
  const [accounts, setAccounts] = React.useState(mockAccounts)
  const [expandedIds, setExpandedIds] = React.useState<Set<string>>(new Set(['1', '2', '3', '4', '5']))
  const [searchQuery, setSearchQuery] = React.useState('')

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [accountToDelete, setAccountToDelete] = React.useState<AccountNode | null>(null)
  const [isDeleting, setIsDeleting] = React.useState(false)
  const deleteApi = useApi()

  const handleDeleteClick = (account: AccountNode, e: React.MouseEvent) => {
    e.stopPropagation()
    setAccountToDelete(account)
    setDeleteDialogOpen(true)
  }

  // Recursively remove account from tree
  const removeAccountFromTree = (tree: AccountNode[], id: string): AccountNode[] => {
    return tree
      .filter(account => account.id !== id)
      .map(account => ({
        ...account,
        children: account.children ? removeAccountFromTree(account.children, id) : undefined
      }))
  }

  const handleDeleteConfirm = async () => {
    if (!accountToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/accounts/${accountToDelete.id}`)
      setAccounts(removeAccountFromTree(accounts, accountToDelete.id))
      setDeleteDialogOpen(false)
      setAccountToDelete(null)
    } catch (error) {
      console.error('Failed to delete account:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  const toggleExpand = (id: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const getTypeIcon = (type: AccountType) => {
    const icons: Record<string, React.ElementType> = {
      asset: TrendingUp,
      liability: TrendingDown,
      equity: Building2,
      revenue: Wallet,
      expense: CreditCard,
      bank: Building2,
      cash: Wallet,
      receivable: TrendingUp,
      payable: TrendingDown
    }
    return icons[type] || Building2
  }

  const getTypeColor = (type: AccountType) => {
    const colors: Record<string, string> = {
      asset: 'text-blue-600',
      liability: 'text-red-600',
      equity: 'text-purple-600',
      revenue: 'text-green-600',
      expense: 'text-orange-600',
      bank: 'text-blue-600',
      cash: 'text-green-600',
      receivable: 'text-blue-600',
      payable: 'text-red-600'
    }
    return colors[type] || 'text-gray-600'
  }

  const renderAccountRow = (account: AccountNode, level: number = 0): React.ReactNode => {
    const hasChildren = account.children && account.children.length > 0
    const isExpanded = expandedIds.has(account.id)
    const Icon = getTypeIcon(account.type)

    return (
      <React.Fragment key={account.id}>
        <tr
          className="hover:bg-muted/50 cursor-pointer"
          onClick={() => hasChildren && toggleExpand(account.id)}
        >
          <td className="py-3 px-4">
            <div className="flex items-center gap-2" style={{ paddingLeft: `${level * 24}px` }}>
              {hasChildren ? (
                <button className="p-0.5 hover:bg-muted rounded">
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </button>
              ) : (
                <span className="w-5" />
              )}
              <Icon className={`h-4 w-4 ${getTypeColor(account.type)}`} />
              <span className="font-mono text-sm text-muted-foreground">{account.code}</span>
            </div>
          </td>
          <td className="py-3 px-4">
            <div className="flex items-center gap-2">
              <span className={hasChildren ? 'font-medium' : ''}>{account.name}</span>
              {account.is_system && (
                <Badge variant="outline" className="text-xs">System</Badge>
              )}
              {account.gst_applicable && (
                <Badge variant="outline" className="text-xs bg-green-50 text-green-700">GST</Badge>
              )}
            </div>
          </td>
          <td className="py-3 px-4 capitalize">
            <Badge variant="outline" className={getTypeColor(account.type)}>
              {account.type}
            </Badge>
          </td>
          <td className="py-3 px-4 text-right font-mono">
            {formatCurrency(account.balance)}
          </td>
          <td className="py-3 px-4 text-center">
            {account.is_active ? (
              <Badge className="bg-green-100 text-green-800">Active</Badge>
            ) : (
              <Badge className="bg-gray-100 text-gray-800">Inactive</Badge>
            )}
          </td>
          <td className="py-3 px-4 text-center">
            {!account.is_system && !hasChildren && (
              <Button
                variant="ghost"
                size="icon"
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={(e) => handleDeleteClick(account, e)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </td>
        </tr>
        {hasChildren && isExpanded && account.children?.map(child => renderAccountRow(child, level + 1))}
      </React.Fragment>
    )
  }

  // Summary stats
  const summary = {
    totalAssets: mockAccounts.find(a => a.code === '1000')?.balance || 0,
    totalLiabilities: mockAccounts.find(a => a.code === '2000')?.balance || 0,
    totalEquity: mockAccounts.find(a => a.code === '3000')?.balance || 0,
    totalRevenue: mockAccounts.find(a => a.code === '4000')?.balance || 0,
    totalExpenses: mockAccounts.find(a => a.code === '5000')?.balance || 0
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Chart of Accounts"
        description="Manage your accounting structure"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/dashboard/accounts' },
          { label: 'Chart of Accounts' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Account
            </Button>
          </div>
        }
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Total Assets</p>
            <p className="text-xl font-bold text-blue-600">{formatCurrency(summary.totalAssets)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Total Liabilities</p>
            <p className="text-xl font-bold text-red-600">{formatCurrency(summary.totalLiabilities)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Total Equity</p>
            <p className="text-xl font-bold text-purple-600">{formatCurrency(summary.totalEquity)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Total Revenue</p>
            <p className="text-xl font-bold text-green-600">{formatCurrency(summary.totalRevenue)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Total Expenses</p>
            <p className="text-xl font-bold text-orange-600">{formatCurrency(summary.totalExpenses)}</p>
          </CardContent>
        </Card>
      </div>

      {/* Net Position */}
      <Card className="bg-primary/5 border-primary/20">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Net Position (Assets - Liabilities)</p>
              <p className="text-3xl font-bold text-primary">
                {formatCurrency(summary.totalAssets - summary.totalLiabilities)}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Net Profit (Revenue - Expenses)</p>
              <p className="text-3xl font-bold text-green-600">
                {formatCurrency(summary.totalRevenue - summary.totalExpenses)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Accounts Tree */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Accounts</CardTitle>
              <CardDescription>Hierarchical view of all accounts</CardDescription>
            </div>
            <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="search"
                placeholder="Search accounts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-md text-sm"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Code</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Account Name</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Type</th>
                  <th className="text-right py-3 px-4 font-medium text-muted-foreground">Balance</th>
                  <th className="text-center py-3 px-4 font-medium text-muted-foreground">Status</th>
                  <th className="text-center py-3 px-4 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {accounts.map(account => renderAccountRow(account))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Account
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the account <strong>{accountToDelete?.code} - {accountToDelete?.name}</strong>?
              This action cannot be undone.
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
