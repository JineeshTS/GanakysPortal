'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatCurrency, formatDate } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  Plus,
  Download,
  Upload,
  RefreshCw,
  Building2,
  CreditCard,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownLeft,
  CheckCircle,
  Clock,
  AlertCircle,
  Eye,
  Loader2
} from 'lucide-react'

// API Response interfaces
interface BankAccountsResponse {
  accounts: BankAccount[]
  total_balance: number
}

interface TransactionsResponse {
  transactions: BankTransaction[]
  total: number
  page: number
  page_size: number
}

// Bank Account type
interface BankAccount {
  id: string
  account_name: string
  account_number: string
  bank_name: string
  branch: string
  ifsc: string
  account_type: 'current' | 'savings' | 'overdraft'
  balance: number
  is_primary: boolean
  last_synced?: string
}

// Bank Transaction type
interface BankTransaction {
  id: string
  date: string
  type: 'credit' | 'debit'
  description: string
  reference: string
  amount: number
  balance: number
  status: 'reconciled' | 'unreconciled' | 'matched'
  matched_with?: string
}

// Mock bank accounts
const mockBankAccounts: BankAccount[] = [
  {
    id: '1',
    account_name: 'HDFC Bank - Current A/c',
    account_number: '50200012345678',
    bank_name: 'HDFC Bank',
    branch: 'MG Road, Bangalore',
    ifsc: 'HDFC0001234',
    account_type: 'current',
    balance: 1845780,
    is_primary: true,
    last_synced: '2026-01-06T10:30:00Z'
  },
  {
    id: '2',
    account_name: 'ICICI Bank - Salary A/c',
    account_number: '123456789012',
    bank_name: 'ICICI Bank',
    branch: 'Indiranagar, Bangalore',
    ifsc: 'ICIC0004567',
    account_type: 'current',
    balance: 500000,
    is_primary: false,
    last_synced: '2026-01-06T09:00:00Z'
  },
  {
    id: '3',
    account_name: 'SBI - Tax Account',
    account_number: '30987654321',
    bank_name: 'State Bank of India',
    branch: 'Koramangala, Bangalore',
    ifsc: 'SBIN0007890',
    account_type: 'savings',
    balance: 125000,
    is_primary: false
  }
]

// Mock transactions for HDFC account
const mockTransactions: BankTransaction[] = [
  {
    id: '1',
    date: '2026-01-06',
    type: 'credit',
    description: 'NEFT-XYZ SOLUTIONS LTD',
    reference: 'NEFT123456789',
    amount: 88500,
    balance: 1845780,
    status: 'reconciled',
    matched_with: 'PAY-IN-2026-0001'
  },
  {
    id: '2',
    date: '2026-01-05',
    type: 'debit',
    description: 'RTGS-CLOUD SERVICES INC',
    reference: 'RTGS987654321',
    amount: 162000,
    balance: 1757280,
    status: 'reconciled',
    matched_with: 'PAY-OUT-2026-0001'
  },
  {
    id: '3',
    date: '2026-01-04',
    type: 'credit',
    description: 'CHQ DEP-456789',
    reference: 'CHQ-456789',
    amount: 100000,
    balance: 1919280,
    status: 'unreconciled'
  },
  {
    id: '4',
    date: '2026-01-03',
    type: 'debit',
    description: 'NEFT-PREMIUM OFFICE SPACE',
    reference: 'NEFT111222333',
    amount: 50000,
    balance: 1819280,
    status: 'matched',
    matched_with: 'PAY-OUT-2026-0002'
  },
  {
    id: '5',
    date: '2026-01-02',
    type: 'debit',
    description: 'SALARY-DEC2025',
    reference: 'SAL/DEC/2025',
    amount: 1405200,
    balance: 1869280,
    status: 'reconciled',
    matched_with: 'PAYROLL-2025-12'
  },
  {
    id: '6',
    date: '2026-01-01',
    type: 'credit',
    description: 'UPI-LMN ENTERPRISES',
    reference: 'UPI/123456/001',
    amount: 25000,
    balance: 3274480,
    status: 'unreconciled'
  }
]

export default function BankingPage() {
  const [selectedAccount, setSelectedAccount] = React.useState<BankAccount | null>(null)

  const { data: accountsData, isLoading: accountsLoading, error: accountsError, get: getAccounts } = useApi<BankAccountsResponse>()
  const { data: transactionsData, isLoading: transactionsLoading, get: getTransactions } = useApi<TransactionsResponse>()

  // Fetch bank accounts on mount
  React.useEffect(() => {
    getAccounts('/banking/accounts')
  }, [getAccounts])

  // Fetch transactions when selected account changes
  React.useEffect(() => {
    if (selectedAccount) {
      getTransactions(`/banking/accounts/${selectedAccount.id}/transactions`)
    }
  }, [selectedAccount, getTransactions])

  const accounts = accountsData?.accounts || mockBankAccounts
  const transactions = transactionsData?.transactions || mockTransactions
  const isLoading = accountsLoading || transactionsLoading

  // Set default selected account when accounts load
  React.useEffect(() => {
    if (accounts.length > 0 && !selectedAccount) {
      setSelectedAccount(accounts[0])
    }
  }, [accounts, selectedAccount])

  const totalBalance = accountsData?.total_balance || accounts.reduce((sum, acc) => sum + acc.balance, 0)

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; className: string; icon: React.ElementType }> = {
      reconciled: { label: 'Reconciled', className: 'bg-green-100 text-green-800', icon: CheckCircle },
      unreconciled: { label: 'Unreconciled', className: 'bg-yellow-100 text-yellow-800', icon: Clock },
      matched: { label: 'Matched', className: 'bg-blue-100 text-blue-800', icon: RefreshCw }
    }

    const config = statusConfig[status] || statusConfig.unreconciled
    const Icon = config.icon

    return (
      <Badge className={config.className}>
        <Icon className="h-3 w-3 mr-1" />
        {config.label}
      </Badge>
    )
  }

  const columns: Column<BankTransaction>[] = [
    {
      key: 'date',
      header: 'Date',
      accessor: (row) => formatDate(row.date)
    },
    {
      key: 'type',
      header: 'Type',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          {row.type === 'credit' ? (
            <ArrowDownLeft className="h-4 w-4 text-green-600" />
          ) : (
            <ArrowUpRight className="h-4 w-4 text-red-600" />
          )}
          <span className="capitalize">{row.type}</span>
        </div>
      )
    },
    {
      key: 'description',
      header: 'Description',
      accessor: (row) => (
        <div>
          <p className="font-medium">{row.description}</p>
          <p className="text-xs text-muted-foreground font-mono">{row.reference}</p>
        </div>
      )
    },
    {
      key: 'amount',
      header: 'Amount',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <span className={`font-semibold ${row.type === 'credit' ? 'text-green-600' : 'text-red-600'}`}>
          {row.type === 'credit' ? '+' : '-'}{formatCurrency(row.amount)}
        </span>
      )
    },
    {
      key: 'balance',
      header: 'Balance',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.balance)
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => (
        <div className="space-y-1">
          {getStatusBadge(row.status)}
          {row.matched_with && (
            <p className="text-xs text-muted-foreground">{row.matched_with}</p>
          )}
        </div>
      )
    }
  ]

  // Reconciliation stats
  const reconStats = {
    total: transactions.length,
    reconciled: transactions.filter(t => t.status === 'reconciled').length,
    unreconciled: transactions.filter(t => t.status === 'unreconciled').length,
    matched: transactions.filter(t => t.status === 'matched').length
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Banking"
        description="Manage bank accounts and reconciliation"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/dashboard/accounts' },
          { label: 'Banking' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Import Statement
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Reconcile
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Bank Account
            </Button>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading banking data...</span>
        </Card>
      )}

      {/* Error State */}
      {accountsError && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{accountsError}</span>
          </div>
        </Card>
      )}

      {/* Bank Accounts Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Total Balance Card */}
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Building2 className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Bank Balance</p>
                <p className="text-2xl font-bold">{formatCurrency(totalBalance)}</p>
                <p className="text-xs text-muted-foreground">{accounts.length} accounts</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bank Account Cards */}
        {accounts.map((account) => (
          <Card
            key={account.id}
            className={`cursor-pointer transition-colors ${
              selectedAccount?.id === account.id ? 'border-primary' : 'hover:border-muted-foreground/50'
            }`}
            onClick={() => setSelectedAccount(account)}
          >
            <CardContent className="pt-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{account.bank_name}</span>
                </div>
                {account.is_primary && (
                  <Badge variant="outline" className="text-xs">Primary</Badge>
                )}
              </div>
              <p className="text-xs text-muted-foreground mb-1">{account.account_name}</p>
              <p className="text-xs font-mono text-muted-foreground mb-2">
                A/c: ****{account.account_number.slice(-4)}
              </p>
              <p className="text-lg font-bold">{formatCurrency(account.balance)}</p>
              {account.last_synced && (
                <p className="text-xs text-muted-foreground mt-1">
                  Synced: {formatDate(account.last_synced, { showTime: true })}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tabs for Transactions and Details */}
      <Tabs defaultValue="transactions">
        <TabsList>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
          <TabsTrigger value="reconciliation">Reconciliation</TabsTrigger>
          <TabsTrigger value="details">Account Details</TabsTrigger>
        </TabsList>

        <TabsContent value="transactions" className="space-y-4">
          {/* Reconciliation Status */}
          <div className="grid grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-4">
                <p className="text-sm text-muted-foreground">Total Transactions</p>
                <p className="text-xl font-bold">{reconStats.total}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4">
                <p className="text-sm text-muted-foreground">Reconciled</p>
                <p className="text-xl font-bold text-green-600">{reconStats.reconciled}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4">
                <p className="text-sm text-muted-foreground">Unreconciled</p>
                <p className="text-xl font-bold text-yellow-600">{reconStats.unreconciled}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-4">
                <p className="text-sm text-muted-foreground">Auto-Matched</p>
                <p className="text-xl font-bold text-blue-600">{reconStats.matched}</p>
              </CardContent>
            </Card>
          </div>

          {/* Transactions Table */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">{selectedAccount?.account_name} - Recent Transactions</CardTitle>
              <CardDescription>January 2026</CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                data={transactions}
                columns={columns}
                keyExtractor={(row) => row.id}
                emptyMessage="No transactions found"
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reconciliation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Bank Reconciliation</CardTitle>
              <CardDescription>Match bank transactions with your records</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-4">Bank Statement</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Opening Balance (01 Jan)</span>
                      <span className="font-medium">{formatCurrency(3274480)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Total Credits</span>
                      <span className="font-medium text-green-600">+{formatCurrency(213500)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Total Debits</span>
                      <span className="font-medium text-red-600">-{formatCurrency(1617200)}</span>
                    </div>
                    <div className="flex justify-between py-2 font-semibold">
                      <span>Closing Balance (06 Jan)</span>
                      <span>{formatCurrency(1845780)}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-4">Book Balance</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Opening Balance (01 Jan)</span>
                      <span className="font-medium">{formatCurrency(3274480)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Receipts Recorded</span>
                      <span className="font-medium text-green-600">+{formatCurrency(213500)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Payments Recorded</span>
                      <span className="font-medium text-red-600">-{formatCurrency(1617200)}</span>
                    </div>
                    <div className="flex justify-between py-2 font-semibold">
                      <span>Book Balance (06 Jan)</span>
                      <span>{formatCurrency(1845780)}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-green-50 rounded-lg">
                <div className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-medium">Reconciled</span>
                </div>
                <p className="text-sm text-green-600 mt-1">
                  Bank balance and book balance match. No discrepancies found.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="details" className="space-y-4">
          {selectedAccount && (
            <Card>
              <CardHeader>
                <CardTitle>{selectedAccount.account_name}</CardTitle>
                <CardDescription>Account Details</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Bank Name</p>
                      <p className="font-medium">{selectedAccount.bank_name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Branch</p>
                      <p className="font-medium">{selectedAccount.branch}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Account Number</p>
                      <p className="font-medium font-mono">{selectedAccount.account_number}</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-muted-foreground">IFSC Code</p>
                      <p className="font-medium font-mono">{selectedAccount.ifsc}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Account Type</p>
                      <p className="font-medium capitalize">{selectedAccount.account_type}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Current Balance</p>
                      <p className="font-medium text-lg">{formatCurrency(selectedAccount.balance)}</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex gap-2">
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-2" />
                    View Statement
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
