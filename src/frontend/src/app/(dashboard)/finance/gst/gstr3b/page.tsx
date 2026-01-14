'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
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
  Eye,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  Calculator,
  Printer,
  Send,
  CreditCard,
  Wallet,
  IndianRupee,
  ArrowRight,
  Info
} from 'lucide-react'

// Periods
const periods = [
  { value: '01-2026', label: 'January 2026' },
  { value: '12-2025', label: 'December 2025' },
  { value: '11-2025', label: 'November 2025' },
  { value: '10-2025', label: 'October 2025' },
]

// GSTR-3B Data (Following actual GSTR-3B structure)
const gstr3bData = {
  period: 'January 2026',
  status: 'draft',
  dueDate: '2026-02-20',

  // 3.1 - Details of Outward Supplies
  section3_1: {
    a: { // Outward taxable supplies (other than zero rated, nil rated and exempted)
      label: 'Outward taxable supplies (other than zero rated, nil rated and exempted)',
      totalTaxableValue: 1230500,
      integratedTax: 158610,
      centralTax: 55125,
      stateTax: 55125,
      cess: 0
    },
    b: { // Outward taxable supplies (zero rated)
      label: 'Outward taxable supplies (zero rated)',
      totalTaxableValue: 0,
      integratedTax: 0,
      centralTax: 0,
      stateTax: 0,
      cess: 0
    },
    c: { // Other outward supplies (nil rated, exempted)
      label: 'Other outward supplies (Nil rated, exempted)',
      totalTaxableValue: 45000,
      integratedTax: 0,
      centralTax: 0,
      stateTax: 0,
      cess: 0
    },
    d: { // Inward supplies (liable to reverse charge)
      label: 'Inward supplies (liable to reverse charge)',
      totalTaxableValue: 25000,
      integratedTax: 0,
      centralTax: 2250,
      stateTax: 2250,
      cess: 0
    },
    e: { // Non-GST outward supplies
      label: 'Non-GST outward supplies',
      totalTaxableValue: 0,
      integratedTax: 0,
      centralTax: 0,
      stateTax: 0,
      cess: 0
    }
  },

  // 3.2 - Inter-State supplies
  section3_2: {
    unreg: { // To unregistered persons
      label: 'Supplies to Unregistered Persons',
      placeOfSupply: [
        { state: '27-Maharashtra', taxableValue: 350000, igst: 63000 },
        { state: '33-Tamil Nadu', taxableValue: 125000, igst: 22500 },
      ]
    },
    comp: { // To composition taxable persons
      label: 'Supplies to Composition Taxable Persons',
      placeOfSupply: []
    },
    uin: { // To UIN holders
      label: 'Supplies to UIN Holders',
      placeOfSupply: []
    }
  },

  // 4. Eligible ITC
  section4: {
    a: { // ITC Available (whether in full or part)
      label: 'ITC Available (whether in full or part)',
      items: [
        {
          nature: '(1) Import of goods',
          integratedTax: 45000,
          centralTax: 0,
          stateTax: 0,
          cess: 0
        },
        {
          nature: '(2) Import of services',
          integratedTax: 12500,
          centralTax: 0,
          stateTax: 0,
          cess: 0
        },
        {
          nature: '(3) Inward supplies liable to reverse charge',
          integratedTax: 0,
          centralTax: 2250,
          stateTax: 2250,
          cess: 0
        },
        {
          nature: '(4) Inward supplies from ISD',
          integratedTax: 0,
          centralTax: 0,
          stateTax: 0,
          cess: 0
        },
        {
          nature: '(5) All other ITC',
          integratedTax: 98780,
          centralTax: 112500,
          stateTax: 112500,
          cess: 0
        }
      ]
    },
    b: { // ITC Reversed
      label: 'ITC Reversed',
      items: [
        {
          nature: '(1) As per rules 42 & 43 of CGST Rules',
          integratedTax: 3500,
          centralTax: 2100,
          stateTax: 2100,
          cess: 0
        },
        {
          nature: '(2) Others',
          integratedTax: 0,
          centralTax: 0,
          stateTax: 0,
          cess: 0
        }
      ]
    },
    c: { // Net ITC Available (A-B)
      label: 'Net ITC Available (A-B)',
      integratedTax: 152780,
      centralTax: 112650,
      stateTax: 112650,
      cess: 0
    },
    d: { // Ineligible ITC
      label: 'Ineligible ITC',
      items: [
        {
          nature: '(1) As per section 17(5)',
          integratedTax: 5600,
          centralTax: 3400,
          stateTax: 3400,
          cess: 0
        },
        {
          nature: '(2) Others',
          integratedTax: 0,
          centralTax: 0,
          stateTax: 0,
          cess: 0
        }
      ]
    }
  },

  // 5. Values of exempt, nil-rated and non-GST inward supplies
  section5: {
    interState: {
      label: 'From a supplier under composition scheme, Exempt and Nil rated supply',
      value: 25000
    },
    intraState: {
      label: 'Non-GST inward supplies',
      value: 15000
    }
  },

  // 6.1 - Tax Payable and Paid
  section6_1: {
    taxPayable: {
      integratedTax: 158610,
      centralTax: 57375,
      stateTax: 57375,
      cess: 0
    },
    paidFromITC: {
      integratedTax: {
        fromIGST: 152780,
        fromCGST: 0,
        fromSGST: 0
      },
      centralTax: {
        fromIGST: 5830,
        fromCGST: 51545,
        fromSGST: 0
      },
      stateTax: {
        fromIGST: 0,
        fromCGST: 0,
        fromSGST: 57375
      },
      cess: {
        fromCess: 0
      }
    },
    paidInCash: {
      integratedTax: 0,
      centralTax: 0,
      stateTax: 0,
      cess: 0
    },
    interestPayable: 0,
    lateFee: 0
  },

  // Ledger Balances
  ledgerBalances: {
    cash: {
      igst: 45000,
      cgst: 32500,
      sgst: 32500,
      cess: 0
    },
    credit: {
      igst: 152780,
      cgst: 112650,
      sgst: 112650,
      cess: 0
    }
  }
}

export default function GSTR3BPage() {
  const [selectedPeriod, setSelectedPeriod] = React.useState('01-2026')
  const [isEditing, setIsEditing] = React.useState(false)

  const getTotalFromItems = (items: Array<{integratedTax: number; centralTax: number; stateTax: number; cess: number}>) => {
    return items.reduce((acc, item) => ({
      integratedTax: acc.integratedTax + item.integratedTax,
      centralTax: acc.centralTax + item.centralTax,
      stateTax: acc.stateTax + item.stateTax,
      cess: acc.cess + item.cess
    }), { integratedTax: 0, centralTax: 0, stateTax: 0, cess: 0 })
  }

  const totalITCAvailable = getTotalFromItems(gstr3bData.section4.a.items)
  const totalITCReversed = getTotalFromItems(gstr3bData.section4.b.items)
  const totalIneligibleITC = getTotalFromItems(gstr3bData.section4.d.items)

  return (
    <div className="space-y-6">
      <PageHeader
        title="GSTR-3B - Summary Return"
        description="Monthly summary of outward supplies, ITC and tax payment"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/finance' },
          { label: 'GST', href: '/finance/gst' },
          { label: 'GSTR-3B' }
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
              Auto-populate
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button size="sm">
              <Send className="h-4 w-4 mr-2" />
              File GSTR-3B
            </Button>
          </div>
        }
      />

      {/* Status & Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200 mt-1">
                  <Clock className="h-3 w-3 mr-1" />
                  Draft
                </Badge>
              </div>
              <Clock className="h-8 w-8 text-yellow-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Due: {formatDate(gstr3bData.dueDate)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Tax Liability</p>
                <p className="text-xl font-bold text-red-600">
                  {formatCurrency(
                    gstr3bData.section6_1.taxPayable.integratedTax +
                    gstr3bData.section6_1.taxPayable.centralTax +
                    gstr3bData.section6_1.taxPayable.stateTax +
                    gstr3bData.section6_1.taxPayable.cess
                  )}
                </p>
              </div>
              <IndianRupee className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Available ITC</p>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(
                    gstr3bData.section4.c.integratedTax +
                    gstr3bData.section4.c.centralTax +
                    gstr3bData.section4.c.stateTax +
                    gstr3bData.section4.c.cess
                  )}
                </p>
              </div>
              <CreditCard className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-primary/5 border-primary">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Net Payable in Cash</p>
                <p className="text-xl font-bold text-primary">
                  {formatCurrency(0)}
                </p>
              </div>
              <Wallet className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Section 3.1 - Details of Outward Supplies */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">3.1 Details of Outward Supplies and Inward Supplies liable to Reverse Charge</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50%]">Nature of Supplies</TableHead>
                <TableHead className="text-right">Total Taxable Value</TableHead>
                <TableHead className="text-right">Integrated Tax</TableHead>
                <TableHead className="text-right">Central Tax</TableHead>
                <TableHead className="text-right">State/UT Tax</TableHead>
                <TableHead className="text-right">Cess</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {Object.entries(gstr3bData.section3_1).map(([key, data]) => (
                <TableRow key={key}>
                  <TableCell className="font-medium text-sm">({key}) {data.label}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.totalTaxableValue)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.integratedTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.centralTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.stateTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(data.cess)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Section 3.2 - Inter-State Supplies */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">3.2 Of the supplies shown in 3.1 (a), details of inter-state supplies made</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">Supplies to Unregistered Persons</h4>
              {gstr3bData.section3_2.unreg.placeOfSupply.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Place of Supply (State/UT)</TableHead>
                      <TableHead className="text-right">Total Taxable Value</TableHead>
                      <TableHead className="text-right">Integrated Tax</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {gstr3bData.section3_2.unreg.placeOfSupply.map((pos, index) => (
                      <TableRow key={index}>
                        <TableCell>{pos.state}</TableCell>
                        <TableCell className="text-right">{formatCurrency(pos.taxableValue)}</TableCell>
                        <TableCell className="text-right">{formatCurrency(pos.igst)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-sm text-muted-foreground">No inter-state supplies to unregistered persons</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Section 4 - Eligible ITC */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">4. Eligible ITC</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 4A - ITC Available */}
          <div>
            <h4 className="font-medium mb-3">(A) ITC Available (whether in full or part)</h4>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Details</TableHead>
                  <TableHead className="text-right">Integrated Tax</TableHead>
                  <TableHead className="text-right">Central Tax</TableHead>
                  <TableHead className="text-right">State/UT Tax</TableHead>
                  <TableHead className="text-right">Cess</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {gstr3bData.section4.a.items.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell className="text-sm">{item.nature}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.integratedTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.centralTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.stateTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.cess)}</TableCell>
                  </TableRow>
                ))}
                <TableRow className="bg-muted/50 font-semibold">
                  <TableCell>Total ITC Available</TableCell>
                  <TableCell className="text-right">{formatCurrency(totalITCAvailable.integratedTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(totalITCAvailable.centralTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(totalITCAvailable.stateTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(totalITCAvailable.cess)}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>

          {/* 4B - ITC Reversed */}
          <div>
            <h4 className="font-medium mb-3">(B) ITC Reversed</h4>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Details</TableHead>
                  <TableHead className="text-right">Integrated Tax</TableHead>
                  <TableHead className="text-right">Central Tax</TableHead>
                  <TableHead className="text-right">State/UT Tax</TableHead>
                  <TableHead className="text-right">Cess</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {gstr3bData.section4.b.items.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell className="text-sm">{item.nature}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.integratedTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.centralTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.stateTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.cess)}</TableCell>
                  </TableRow>
                ))}
                <TableRow className="bg-muted/50 font-semibold">
                  <TableCell>Total ITC Reversed</TableCell>
                  <TableCell className="text-right">{formatCurrency(totalITCReversed.integratedTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(totalITCReversed.centralTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(totalITCReversed.stateTax)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(totalITCReversed.cess)}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>

          {/* 4C - Net ITC */}
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium mb-3 text-green-800">(C) Net ITC Available (A - B)</h4>
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <p className="text-sm text-green-600">Integrated Tax</p>
                <p className="text-lg font-bold text-green-800">{formatCurrency(gstr3bData.section4.c.integratedTax)}</p>
              </div>
              <div>
                <p className="text-sm text-green-600">Central Tax</p>
                <p className="text-lg font-bold text-green-800">{formatCurrency(gstr3bData.section4.c.centralTax)}</p>
              </div>
              <div>
                <p className="text-sm text-green-600">State/UT Tax</p>
                <p className="text-lg font-bold text-green-800">{formatCurrency(gstr3bData.section4.c.stateTax)}</p>
              </div>
              <div>
                <p className="text-sm text-green-600">Cess</p>
                <p className="text-lg font-bold text-green-800">{formatCurrency(gstr3bData.section4.c.cess)}</p>
              </div>
            </div>
          </div>

          {/* 4D - Ineligible ITC */}
          <div>
            <h4 className="font-medium mb-3">(D) Ineligible ITC</h4>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Details</TableHead>
                  <TableHead className="text-right">Integrated Tax</TableHead>
                  <TableHead className="text-right">Central Tax</TableHead>
                  <TableHead className="text-right">State/UT Tax</TableHead>
                  <TableHead className="text-right">Cess</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {gstr3bData.section4.d.items.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell className="text-sm">{item.nature}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.integratedTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.centralTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.stateTax)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.cess)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Section 5 - Exempt Supplies */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">5. Values of Exempt, Nil-Rated and Non-GST Inward Supplies</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nature of Supplies</TableHead>
                <TableHead className="text-right">Inter-State Supplies</TableHead>
                <TableHead className="text-right">Intra-State Supplies</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>From a supplier under composition scheme, Exempt and Nil rated supply</TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section5.interState.value)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Non-GST inward supplies</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section5.intraState.value)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Section 6.1 - Payment of Tax */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">6.1 Payment of Tax</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Description</TableHead>
                <TableHead className="text-right">Tax Payable</TableHead>
                <TableHead className="text-right">Paid through ITC</TableHead>
                <TableHead className="text-right">Paid in Cash</TableHead>
                <TableHead className="text-right">Interest</TableHead>
                <TableHead className="text-right">Late Fee</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Integrated Tax</TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section6_1.taxPayable.integratedTax)}</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(gstr3bData.section6_1.paidFromITC.integratedTax.fromIGST)}
                </TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section6_1.paidInCash.integratedTax)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Central Tax</TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section6_1.taxPayable.centralTax)}</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(
                    gstr3bData.section6_1.paidFromITC.centralTax.fromIGST +
                    gstr3bData.section6_1.paidFromITC.centralTax.fromCGST
                  )}
                </TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section6_1.paidInCash.centralTax)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">State/UT Tax</TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section6_1.taxPayable.stateTax)}</TableCell>
                <TableCell className="text-right">
                  {formatCurrency(gstr3bData.section6_1.paidFromITC.stateTax.fromSGST)}
                </TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section6_1.paidInCash.stateTax)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Cess</TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section6_1.taxPayable.cess)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
                <TableCell className="text-right">{formatCurrency(gstr3bData.section6_1.paidInCash.cess)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
                <TableCell className="text-right">{formatCurrency(0)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>

          {/* ITC Utilization Details */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-start gap-2 mb-3">
              <Info className="h-4 w-4 text-blue-600 mt-0.5" />
              <h4 className="font-medium text-blue-800">ITC Utilization Order</h4>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-blue-600">IGST Utilized:</p>
                <ul className="mt-1 space-y-1">
                  <li>Against IGST: {formatCurrency(gstr3bData.section6_1.paidFromITC.integratedTax.fromIGST)}</li>
                  <li>Against CGST: {formatCurrency(gstr3bData.section6_1.paidFromITC.centralTax.fromIGST)}</li>
                  <li>Against SGST: {formatCurrency(0)}</li>
                </ul>
              </div>
              <div>
                <p className="text-blue-600">CGST Utilized:</p>
                <ul className="mt-1 space-y-1">
                  <li>Against CGST: {formatCurrency(gstr3bData.section6_1.paidFromITC.centralTax.fromCGST)}</li>
                </ul>
              </div>
              <div>
                <p className="text-blue-600">SGST Utilized:</p>
                <ul className="mt-1 space-y-1">
                  <li>Against SGST: {formatCurrency(gstr3bData.section6_1.paidFromITC.stateTax.fromSGST)}</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ledger Balances & Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Ledger Balances</CardTitle>
            <CardDescription>Available balance in electronic ledgers</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium mb-2">Cash Ledger</h4>
                <div className="grid grid-cols-4 gap-2 text-center">
                  <div className="p-2 bg-muted rounded">
                    <p className="text-xs text-muted-foreground">IGST</p>
                    <p className="font-medium">{formatCurrency(gstr3bData.ledgerBalances.cash.igst)}</p>
                  </div>
                  <div className="p-2 bg-muted rounded">
                    <p className="text-xs text-muted-foreground">CGST</p>
                    <p className="font-medium">{formatCurrency(gstr3bData.ledgerBalances.cash.cgst)}</p>
                  </div>
                  <div className="p-2 bg-muted rounded">
                    <p className="text-xs text-muted-foreground">SGST</p>
                    <p className="font-medium">{formatCurrency(gstr3bData.ledgerBalances.cash.sgst)}</p>
                  </div>
                  <div className="p-2 bg-muted rounded">
                    <p className="text-xs text-muted-foreground">Cess</p>
                    <p className="font-medium">{formatCurrency(gstr3bData.ledgerBalances.cash.cess)}</p>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium mb-2">Credit Ledger (After Utilization)</h4>
                <div className="grid grid-cols-4 gap-2 text-center">
                  <div className="p-2 bg-green-50 rounded">
                    <p className="text-xs text-green-600">IGST</p>
                    <p className="font-medium text-green-700">{formatCurrency(0)}</p>
                  </div>
                  <div className="p-2 bg-green-50 rounded">
                    <p className="text-xs text-green-600">CGST</p>
                    <p className="font-medium text-green-700">{formatCurrency(61105)}</p>
                  </div>
                  <div className="p-2 bg-green-50 rounded">
                    <p className="text-xs text-green-600">SGST</p>
                    <p className="font-medium text-green-700">{formatCurrency(55275)}</p>
                  </div>
                  <div className="p-2 bg-green-50 rounded">
                    <p className="text-xs text-green-600">Cess</p>
                    <p className="font-medium text-green-700">{formatCurrency(0)}</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filing Actions</CardTitle>
            <CardDescription>Generate and file your GSTR-3B</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button className="w-full justify-start" variant="outline">
                <Eye className="h-4 w-4 mr-2" />
                Preview GSTR-3B
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Download JSON
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Printer className="h-4 w-4 mr-2" />
                Print Summary
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Recalculate from Books
              </Button>
              <div className="pt-2 border-t">
                <Button className="w-full">
                  <Send className="h-4 w-4 mr-2" />
                  Proceed to File GSTR-3B
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
