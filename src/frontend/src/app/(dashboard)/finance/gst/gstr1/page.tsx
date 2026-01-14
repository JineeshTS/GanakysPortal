'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
import { formatCurrency, formatDate } from '@/lib/format'
import {
  FileText,
  Download,
  Upload,
  Eye,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  FileJson,
  Printer,
  Send
} from 'lucide-react'

// Periods (Monthly/Quarterly)
const periods = [
  { value: '01-2026', label: 'January 2026', type: 'monthly' },
  { value: '12-2025', label: 'December 2025', type: 'monthly' },
  { value: '11-2025', label: 'November 2025', type: 'monthly' },
  { value: 'Q3-2025', label: 'Oct-Dec 2025 (Q3)', type: 'quarterly' },
  { value: 'Q2-2025', label: 'Jul-Sep 2025 (Q2)', type: 'quarterly' },
]

// B2B Invoices (Registered Recipients)
const b2bInvoices = [
  {
    id: '1',
    invoiceNumber: 'INV-2026-0001',
    invoiceDate: '2026-01-05',
    gstin: '29AABCU9603R1ZM',
    customerName: 'ABC Technologies Pvt Ltd',
    placeOfSupply: '29-Karnataka',
    invoiceType: 'Regular',
    reverseCharge: 'N',
    taxableValue: 95000,
    igst: 0,
    cgst: 8550,
    sgst: 8550,
    cess: 0,
    invoiceValue: 112100,
    status: 'valid'
  },
  {
    id: '2',
    invoiceNumber: 'INV-2025-0147',
    invoiceDate: '2025-12-20',
    gstin: '27AABCX1234D1ZP',
    customerName: 'XYZ Solutions Ltd',
    placeOfSupply: '27-Maharashtra',
    invoiceType: 'Regular',
    reverseCharge: 'N',
    taxableValue: 75000,
    igst: 13500,
    cgst: 0,
    sgst: 0,
    cess: 0,
    invoiceValue: 88500,
    status: 'valid'
  },
  {
    id: '3',
    invoiceNumber: 'INV-2025-0145',
    invoiceDate: '2025-12-15',
    gstin: '29AABCP5678E1ZQ',
    customerName: 'PQR Industries',
    placeOfSupply: '29-Karnataka',
    invoiceType: 'Regular',
    reverseCharge: 'N',
    taxableValue: 237500,
    igst: 0,
    cgst: 21375,
    sgst: 21375,
    cess: 0,
    invoiceValue: 280250,
    status: 'valid'
  },
  {
    id: '4',
    invoiceNumber: 'INV-2025-0146',
    invoiceDate: '2025-12-18',
    gstin: '33AABCG9876F1ZR',
    customerName: 'Global Tech Solutions',
    placeOfSupply: '33-Tamil Nadu',
    invoiceType: 'Regular',
    reverseCharge: 'N',
    taxableValue: 171000,
    igst: 30780,
    cgst: 0,
    sgst: 0,
    cess: 0,
    invoiceValue: 201780,
    status: 'valid'
  }
]

// B2C Large (Unregistered with value > 2.5L inter-state)
const b2cLarge = [
  {
    id: '1',
    invoiceNumber: 'INV-2025-0140',
    invoiceDate: '2025-12-10',
    placeOfSupply: '27-Maharashtra',
    eCommerceGstin: '-',
    taxableValue: 350000,
    igst: 63000,
    cess: 0,
    invoiceValue: 413000
  }
]

// B2C Small Summary (By Rate)
const b2cSmall = [
  { rate: 5, taxableValue: 45000, cgst: 1125, sgst: 1125, cess: 0 },
  { rate: 12, taxableValue: 78000, cgst: 4680, sgst: 4680, cess: 0 },
  { rate: 18, taxableValue: 156000, cgst: 14040, sgst: 14040, cess: 0 },
  { rate: 28, taxableValue: 23000, cgst: 3220, sgst: 3220, cess: 0 }
]

// Credit/Debit Notes
const creditDebitNotes = [
  {
    id: '1',
    noteNumber: 'CN-2025-0012',
    noteDate: '2025-12-22',
    noteType: 'Credit Note',
    originalInvoice: 'INV-2025-0142',
    gstin: '29AABCP5678E1ZQ',
    customerName: 'PQR Industries',
    taxableValue: 10000,
    cgst: 900,
    sgst: 900,
    igst: 0,
    noteValue: 11800,
    reason: 'Quality issue - partial refund'
  }
]

// HSN Summary
const hsnSummary = [
  {
    hsnCode: '998314',
    description: 'IT design and development services',
    uqc: 'Nos',
    totalQuantity: 15,
    totalValue: 456000,
    taxableValue: 432000,
    igst: 44280,
    cgst: 16200,
    sgst: 16200,
    cess: 0
  },
  {
    hsnCode: '998313',
    description: 'IT consulting services',
    uqc: 'Hrs',
    totalQuantity: 120,
    totalValue: 234000,
    taxableValue: 220000,
    igst: 0,
    cgst: 19800,
    sgst: 19800,
    cess: 0
  },
  {
    hsnCode: '998311',
    description: 'Management consulting services',
    uqc: 'Nos',
    totalQuantity: 5,
    totalValue: 125000,
    taxableValue: 118500,
    igst: 21330,
    cgst: 0,
    sgst: 0,
    cess: 0
  }
]

// Summary Stats
const gstr1Summary = {
  period: 'January 2026',
  status: 'draft',
  dueDate: '2026-02-11',
  b2b: { invoices: 4, taxableValue: 578500, tax: 95605 },
  b2cLarge: { invoices: 1, taxableValue: 350000, tax: 63000 },
  b2cSmall: { taxableValue: 302000, tax: 46130 },
  creditNotes: { notes: 1, taxableValue: 10000, tax: 1800 },
  totalTaxableValue: 1220500,
  totalTax: 202935,
  totalInvoices: 18
}

export default function GSTR1Page() {
  const [selectedPeriod, setSelectedPeriod] = React.useState('01-2026')
  const [filingType, setFilingType] = React.useState<'monthly' | 'quarterly'>('monthly')

  const getStatusBadge = (status: string) => {
    const config: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
      valid: {
        label: 'Valid',
        className: 'bg-green-100 text-green-800',
        icon: <CheckCircle className="h-3 w-3" />
      },
      error: {
        label: 'Error',
        className: 'bg-red-100 text-red-800',
        icon: <AlertCircle className="h-3 w-3" />
      },
      draft: {
        label: 'Draft',
        className: 'bg-yellow-100 text-yellow-800',
        icon: <Clock className="h-3 w-3" />
      }
    }
    const c = config[status] || config.draft
    return (
      <Badge className={`${c.className} flex items-center gap-1`}>
        {c.icon}
        {c.label}
      </Badge>
    )
  }

  const b2bColumns: Column<typeof b2bInvoices[0]>[] = [
    {
      key: 'invoice',
      header: 'Invoice',
      accessor: (row) => (
        <div>
          <p className="font-mono font-medium">{row.invoiceNumber}</p>
          <p className="text-xs text-muted-foreground">{formatDate(row.invoiceDate)}</p>
        </div>
      )
    },
    {
      key: 'gstin',
      header: 'GSTIN / Customer',
      accessor: (row) => (
        <div>
          <p className="font-mono text-sm">{row.gstin}</p>
          <p className="text-xs text-muted-foreground">{row.customerName}</p>
        </div>
      )
    },
    {
      key: 'pos',
      header: 'Place of Supply',
      accessor: (row) => row.placeOfSupply
    },
    {
      key: 'taxable',
      header: 'Taxable Value',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.taxableValue)
    },
    {
      key: 'igst',
      header: 'IGST',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.igst)
    },
    {
      key: 'cgst',
      header: 'CGST',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.cgst)
    },
    {
      key: 'sgst',
      header: 'SGST',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.sgst)
    },
    {
      key: 'total',
      header: 'Invoice Value',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => <span className="font-medium">{formatCurrency(row.invoiceValue)}</span>
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    }
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="GSTR-1 - Outward Supplies"
        description="Statement of outward supplies of goods/services"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/finance' },
          { label: 'GST', href: '/finance/gst' },
          { label: 'GSTR-1' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {periods.map(period => (
                  <SelectItem key={period.value} value={period.value}>
                    {period.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Data
            </Button>
            <Button variant="outline" size="sm">
              <FileJson className="h-4 w-4 mr-2" />
              Download JSON
            </Button>
            <Button size="sm">
              <Send className="h-4 w-4 mr-2" />
              File GSTR-1
            </Button>
          </div>
        }
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">B2B Invoices</p>
                <p className="text-2xl font-bold">{gstr1Summary.b2b.invoices}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatCurrency(gstr1Summary.b2b.taxableValue)}
                </p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <FileText className="h-5 w-5 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">B2C Large</p>
                <p className="text-2xl font-bold">{gstr1Summary.b2cLarge.invoices}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatCurrency(gstr1Summary.b2cLarge.taxableValue)}
                </p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <FileText className="h-5 w-5 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">B2C Small</p>
                <p className="text-2xl font-bold">--</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatCurrency(gstr1Summary.b2cSmall.taxableValue)}
                </p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
                <FileText className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Credit/Debit Notes</p>
                <p className="text-2xl font-bold">{gstr1Summary.creditNotes.notes}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatCurrency(gstr1Summary.creditNotes.taxableValue)}
                </p>
              </div>
              <div className="h-10 w-10 rounded-lg bg-orange-100 flex items-center justify-center">
                <FileText className="h-5 w-5 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-primary/5 border-primary">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Tax Liability</p>
                <p className="text-2xl font-bold text-primary">{formatCurrency(gstr1Summary.totalTax)}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Taxable: {formatCurrency(gstr1Summary.totalTaxableValue)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filing Status */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                <Clock className="h-3 w-3 mr-1" />
                Draft
              </Badge>
              <div className="text-sm">
                <span className="text-muted-foreground">Period: </span>
                <span className="font-medium">{gstr1Summary.period}</span>
              </div>
              <div className="text-sm">
                <span className="text-muted-foreground">Due Date: </span>
                <span className="font-medium">{formatDate(gstr1Summary.dueDate)}</span>
              </div>
              <div className="text-sm">
                <span className="text-muted-foreground">Total Invoices: </span>
                <span className="font-medium">{gstr1Summary.totalInvoices}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </Button>
              <Button variant="outline" size="sm">
                <Printer className="h-4 w-4 mr-2" />
                Print
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabbed Content */}
      <Tabs defaultValue="b2b" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="b2b">B2B Invoices</TabsTrigger>
          <TabsTrigger value="b2cl">B2C Large</TabsTrigger>
          <TabsTrigger value="b2cs">B2C Small</TabsTrigger>
          <TabsTrigger value="cdnr">Credit/Debit Notes</TabsTrigger>
          <TabsTrigger value="hsn">HSN Summary</TabsTrigger>
          <TabsTrigger value="docs">Documents</TabsTrigger>
        </TabsList>

        {/* B2B Tab */}
        <TabsContent value="b2b" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">4A - B2B Invoices</CardTitle>
              <CardDescription>
                Taxable outward supplies to registered persons (excluding zero-rated, SEZ supplies)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                data={b2bInvoices}
                columns={b2bColumns}
                keyExtractor={(row) => row.id}
                emptyMessage="No B2B invoices for this period"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* B2C Large Tab */}
        <TabsContent value="b2cl" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">5A - B2C Large Invoices</CardTitle>
              <CardDescription>
                Taxable outward inter-state supplies to unregistered persons where invoice value is more than Rs.2.5 lakh
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Invoice</TableHead>
                    <TableHead>Place of Supply</TableHead>
                    <TableHead className="text-right">Taxable Value</TableHead>
                    <TableHead className="text-right">IGST</TableHead>
                    <TableHead className="text-right">Cess</TableHead>
                    <TableHead className="text-right">Invoice Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {b2cLarge.map(inv => (
                    <TableRow key={inv.id}>
                      <TableCell>
                        <p className="font-mono font-medium">{inv.invoiceNumber}</p>
                        <p className="text-xs text-muted-foreground">{formatDate(inv.invoiceDate)}</p>
                      </TableCell>
                      <TableCell>{inv.placeOfSupply}</TableCell>
                      <TableCell className="text-right">{formatCurrency(inv.taxableValue)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(inv.igst)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(inv.cess)}</TableCell>
                      <TableCell className="text-right font-medium">{formatCurrency(inv.invoiceValue)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* B2C Small Tab */}
        <TabsContent value="b2cs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">7 - B2C Small (Summary)</CardTitle>
              <CardDescription>
                Taxable outward supplies to consumers (B2C) - consolidated by rate
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>GST Rate</TableHead>
                    <TableHead className="text-right">Taxable Value</TableHead>
                    <TableHead className="text-right">CGST</TableHead>
                    <TableHead className="text-right">SGST</TableHead>
                    <TableHead className="text-right">Cess</TableHead>
                    <TableHead className="text-right">Total Tax</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {b2cSmall.map(item => (
                    <TableRow key={item.rate}>
                      <TableCell className="font-medium">{item.rate}%</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.taxableValue)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.cgst)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.sgst)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.cess)}</TableCell>
                      <TableCell className="text-right font-medium">{formatCurrency(item.cgst + item.sgst + item.cess)}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="bg-muted/50 font-semibold">
                    <TableCell>Total</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(b2cSmall.reduce((sum, i) => sum + i.taxableValue, 0))}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(b2cSmall.reduce((sum, i) => sum + i.cgst, 0))}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(b2cSmall.reduce((sum, i) => sum + i.sgst, 0))}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(b2cSmall.reduce((sum, i) => sum + i.cess, 0))}
                    </TableCell>
                    <TableCell className="text-right text-primary">
                      {formatCurrency(b2cSmall.reduce((sum, i) => sum + i.cgst + i.sgst + i.cess, 0))}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Credit/Debit Notes Tab */}
        <TabsContent value="cdnr" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">9B - Credit/Debit Notes (Registered)</CardTitle>
              <CardDescription>
                Credit/Debit notes issued to registered recipients
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Note Details</TableHead>
                    <TableHead>Original Invoice</TableHead>
                    <TableHead>GSTIN / Customer</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead className="text-right">Taxable Value</TableHead>
                    <TableHead className="text-right">Tax</TableHead>
                    <TableHead className="text-right">Note Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {creditDebitNotes.map(note => (
                    <TableRow key={note.id}>
                      <TableCell>
                        <div>
                          <Badge variant="outline" className="mb-1">{note.noteType}</Badge>
                          <p className="font-mono font-medium">{note.noteNumber}</p>
                          <p className="text-xs text-muted-foreground">{formatDate(note.noteDate)}</p>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono text-sm">{note.originalInvoice}</TableCell>
                      <TableCell>
                        <p className="font-mono text-sm">{note.gstin}</p>
                        <p className="text-xs text-muted-foreground">{note.customerName}</p>
                      </TableCell>
                      <TableCell className="text-sm">{note.reason}</TableCell>
                      <TableCell className="text-right">{formatCurrency(note.taxableValue)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(note.cgst + note.sgst + note.igst)}</TableCell>
                      <TableCell className="text-right font-medium">{formatCurrency(note.noteValue)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* HSN Summary Tab */}
        <TabsContent value="hsn" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">12 - HSN-wise Summary of Outward Supplies</CardTitle>
              <CardDescription>
                Summary of outward supplies by HSN/SAC code
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>HSN/SAC</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>UQC</TableHead>
                    <TableHead className="text-right">Qty</TableHead>
                    <TableHead className="text-right">Total Value</TableHead>
                    <TableHead className="text-right">Taxable Value</TableHead>
                    <TableHead className="text-right">IGST</TableHead>
                    <TableHead className="text-right">CGST</TableHead>
                    <TableHead className="text-right">SGST</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {hsnSummary.map(item => (
                    <TableRow key={item.hsnCode}>
                      <TableCell className="font-mono font-medium">{item.hsnCode}</TableCell>
                      <TableCell className="text-sm">{item.description}</TableCell>
                      <TableCell>{item.uqc}</TableCell>
                      <TableCell className="text-right">{item.totalQuantity}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.totalValue)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.taxableValue)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.igst)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.cgst)}</TableCell>
                      <TableCell className="text-right">{formatCurrency(item.sgst)}</TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="bg-muted/50 font-semibold">
                    <TableCell colSpan={4}>Total</TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(hsnSummary.reduce((sum, i) => sum + i.totalValue, 0))}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(hsnSummary.reduce((sum, i) => sum + i.taxableValue, 0))}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(hsnSummary.reduce((sum, i) => sum + i.igst, 0))}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(hsnSummary.reduce((sum, i) => sum + i.cgst, 0))}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatCurrency(hsnSummary.reduce((sum, i) => sum + i.sgst, 0))}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="docs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">13 - Document Summary</CardTitle>
              <CardDescription>
                Details of documents issued during the tax period
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document Type</TableHead>
                    <TableHead>Series From</TableHead>
                    <TableHead>Series To</TableHead>
                    <TableHead className="text-right">Total Issued</TableHead>
                    <TableHead className="text-right">Cancelled</TableHead>
                    <TableHead className="text-right">Net Issued</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell className="font-medium">Invoices for outward supply</TableCell>
                    <TableCell className="font-mono">INV-2026-0001</TableCell>
                    <TableCell className="font-mono">INV-2026-0015</TableCell>
                    <TableCell className="text-right">15</TableCell>
                    <TableCell className="text-right">0</TableCell>
                    <TableCell className="text-right font-medium">15</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium">Credit Notes</TableCell>
                    <TableCell className="font-mono">CN-2026-0001</TableCell>
                    <TableCell className="font-mono">CN-2026-0003</TableCell>
                    <TableCell className="text-right">3</TableCell>
                    <TableCell className="text-right">1</TableCell>
                    <TableCell className="text-right font-medium">2</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium">Debit Notes</TableCell>
                    <TableCell className="font-mono">DN-2026-0001</TableCell>
                    <TableCell className="font-mono">DN-2026-0001</TableCell>
                    <TableCell className="text-right">1</TableCell>
                    <TableCell className="text-right">0</TableCell>
                    <TableCell className="text-right font-medium">1</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
