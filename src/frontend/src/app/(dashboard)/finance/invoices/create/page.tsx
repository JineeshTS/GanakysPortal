'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
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
import { formatCurrency } from '@/lib/format'
import {
  Plus,
  Trash2,
  Save,
  Send,
  Eye,
  Calculator,
  Search,
  FileText,
  Building2,
  MapPin,
  Banknote
} from 'lucide-react'

// Indian State Codes for Place of Supply
const indianStates = [
  { code: '01', name: 'Jammu and Kashmir' },
  { code: '02', name: 'Himachal Pradesh' },
  { code: '03', name: 'Punjab' },
  { code: '04', name: 'Chandigarh' },
  { code: '05', name: 'Uttarakhand' },
  { code: '06', name: 'Haryana' },
  { code: '07', name: 'Delhi' },
  { code: '08', name: 'Rajasthan' },
  { code: '09', name: 'Uttar Pradesh' },
  { code: '10', name: 'Bihar' },
  { code: '11', name: 'Sikkim' },
  { code: '12', name: 'Arunachal Pradesh' },
  { code: '13', name: 'Nagaland' },
  { code: '14', name: 'Manipur' },
  { code: '15', name: 'Mizoram' },
  { code: '16', name: 'Tripura' },
  { code: '17', name: 'Meghalaya' },
  { code: '18', name: 'Assam' },
  { code: '19', name: 'West Bengal' },
  { code: '20', name: 'Jharkhand' },
  { code: '21', name: 'Odisha' },
  { code: '22', name: 'Chhattisgarh' },
  { code: '23', name: 'Madhya Pradesh' },
  { code: '24', name: 'Gujarat' },
  { code: '27', name: 'Maharashtra' },
  { code: '29', name: 'Karnataka' },
  { code: '30', name: 'Goa' },
  { code: '32', name: 'Kerala' },
  { code: '33', name: 'Tamil Nadu' },
  { code: '36', name: 'Telangana' },
  { code: '37', name: 'Andhra Pradesh' },
]

// GST Rates
const gstRates = [
  { value: '0', label: '0%' },
  { value: '5', label: '5%' },
  { value: '12', label: '12%' },
  { value: '18', label: '18%' },
  { value: '28', label: '28%' },
]

// Common HSN/SAC codes for India
const hsnSacCodes = [
  { code: '998311', description: 'Management consulting services', type: 'SAC' },
  { code: '998312', description: 'Business consulting services', type: 'SAC' },
  { code: '998313', description: 'IT consulting services', type: 'SAC' },
  { code: '998314', description: 'IT design and development', type: 'SAC' },
  { code: '998315', description: 'Hosting and IT infrastructure', type: 'SAC' },
  { code: '998316', description: 'IT infrastructure management', type: 'SAC' },
  { code: '997331', description: 'Licensing of intellectual property', type: 'SAC' },
  { code: '8471', description: 'Computers and related equipment', type: 'HSN' },
  { code: '8473', description: 'Parts for computers', type: 'HSN' },
  { code: '8517', description: 'Telephone and communication equipment', type: 'HSN' },
]

// Mock customers
const customers = [
  {
    id: '1',
    name: 'ABC Technologies Pvt Ltd',
    gstin: '29AABCU9603R1ZM',
    pan: 'AABCU9603R',
    state: 'Karnataka',
    stateCode: '29',
    address: '123 Tech Park, Bangalore - 560001'
  },
  {
    id: '2',
    name: 'XYZ Solutions Ltd',
    gstin: '27AABCX1234D1ZP',
    pan: 'AABCX1234D',
    state: 'Maharashtra',
    stateCode: '27',
    address: '456 Business Tower, Mumbai - 400001'
  },
  {
    id: '3',
    name: 'PQR Industries',
    gstin: '29AABCP5678E1ZQ',
    pan: 'AABCP5678E',
    state: 'Karnataka',
    stateCode: '29',
    address: '789 Industrial Area, Bangalore - 560002'
  },
  {
    id: '4',
    name: 'Global Tech Solutions',
    gstin: '33AABCG9876F1ZR',
    pan: 'AABCG9876F',
    state: 'Tamil Nadu',
    stateCode: '33',
    address: '321 IT Corridor, Chennai - 600001'
  },
  {
    id: '5',
    name: 'LMN Enterprises',
    gstin: '',
    pan: 'AABCL2345G',
    state: 'Karnataka',
    stateCode: '29',
    address: '567 Commerce Street, Bangalore - 560003'
  }
]

// Company details (seller)
const companyDetails = {
  name: 'TechCorp Solutions Pvt Ltd',
  gstin: '29AATCT1234B1ZP',
  pan: 'AATCT1234B',
  state: 'Karnataka',
  stateCode: '29',
  address: '100 Innovation Hub, Whitefield, Bangalore - 560066',
  email: 'accounts@techcorp.in',
  phone: '+91 80 4567 8900'
}

// Bank details
const bankDetails = {
  accountName: 'TechCorp Solutions Pvt Ltd',
  accountNumber: '1234567890123456',
  bankName: 'HDFC Bank Ltd',
  branch: 'Whitefield Branch, Bangalore',
  ifsc: 'HDFC0001234',
  swift: 'HDFCINBB'
}

interface InvoiceItem {
  id: string
  description: string
  hsnSac: string
  quantity: number
  unit: string
  rate: number
  discount: number
  gstRate: number
  amount: number
  taxableAmount: number
  cgst: number
  sgst: number
  igst: number
  total: number
}

export default function CreateInvoicePage() {
  const router = useRouter()
  const [selectedCustomer, setSelectedCustomer] = React.useState<typeof customers[0] | null>(null)
  const [placeOfSupply, setPlaceOfSupply] = React.useState('')
  const [supplyType, setSupplyType] = React.useState<'goods' | 'services'>('services')
  const [invoiceDate, setInvoiceDate] = React.useState(new Date().toISOString().split('T')[0])
  const [dueDate, setDueDate] = React.useState('')
  const [invoiceNumber, setInvoiceNumber] = React.useState('INV-2026-0003')
  const [notes, setNotes] = React.useState('')
  const [terms, setTerms] = React.useState(
    '1. Payment due within 30 days from invoice date.\n2. Interest @ 18% per annum will be charged on delayed payments.\n3. Subject to Bangalore jurisdiction.'
  )

  const [items, setItems] = React.useState<InvoiceItem[]>([
    {
      id: '1',
      description: '',
      hsnSac: '',
      quantity: 1,
      unit: 'Nos',
      rate: 0,
      discount: 0,
      gstRate: 18,
      amount: 0,
      taxableAmount: 0,
      cgst: 0,
      sgst: 0,
      igst: 0,
      total: 0
    }
  ])

  // Determine if intra-state or inter-state
  const isInterState = React.useMemo(() => {
    if (!selectedCustomer || !placeOfSupply) return false
    const posStateCode = indianStates.find(s => s.name === placeOfSupply)?.code
    return posStateCode !== companyDetails.stateCode
  }, [selectedCustomer, placeOfSupply])

  // Calculate line item totals
  const calculateItemTotals = (item: InvoiceItem): InvoiceItem => {
    const amount = item.quantity * item.rate
    const discountAmount = (amount * item.discount) / 100
    const taxableAmount = amount - discountAmount
    const gstAmount = (taxableAmount * item.gstRate) / 100

    let cgst = 0, sgst = 0, igst = 0
    if (isInterState) {
      igst = gstAmount
    } else {
      cgst = gstAmount / 2
      sgst = gstAmount / 2
    }

    return {
      ...item,
      amount,
      taxableAmount,
      cgst,
      sgst,
      igst,
      total: taxableAmount + cgst + sgst + igst
    }
  }

  // Calculate totals
  const totals = React.useMemo(() => {
    const calculatedItems = items.map(calculateItemTotals)
    const subtotal = calculatedItems.reduce((sum, item) => sum + item.amount, 0)
    const totalDiscount = calculatedItems.reduce((sum, item) => sum + (item.amount - item.taxableAmount), 0)
    const taxableAmount = calculatedItems.reduce((sum, item) => sum + item.taxableAmount, 0)
    const totalCgst = calculatedItems.reduce((sum, item) => sum + item.cgst, 0)
    const totalSgst = calculatedItems.reduce((sum, item) => sum + item.sgst, 0)
    const totalIgst = calculatedItems.reduce((sum, item) => sum + item.igst, 0)
    const totalTax = totalCgst + totalSgst + totalIgst
    const grandTotal = taxableAmount + totalTax
    const roundOff = Math.round(grandTotal) - grandTotal
    const finalTotal = Math.round(grandTotal)

    return {
      subtotal,
      totalDiscount,
      taxableAmount,
      totalCgst,
      totalSgst,
      totalIgst,
      totalTax,
      grandTotal,
      roundOff,
      finalTotal
    }
  }, [items, isInterState])

  const handleCustomerChange = (customerId: string) => {
    const customer = customers.find(c => c.id === customerId)
    setSelectedCustomer(customer || null)
    if (customer) {
      setPlaceOfSupply(customer.state)
    }
  }

  const handleItemChange = (id: string, field: keyof InvoiceItem, value: string | number) => {
    setItems(prev => prev.map(item => {
      if (item.id === id) {
        const updated = { ...item, [field]: value }
        return calculateItemTotals(updated)
      }
      return item
    }))
  }

  const addItem = () => {
    const newItem: InvoiceItem = {
      id: Date.now().toString(),
      description: '',
      hsnSac: '',
      quantity: 1,
      unit: 'Nos',
      rate: 0,
      discount: 0,
      gstRate: 18,
      amount: 0,
      taxableAmount: 0,
      cgst: 0,
      sgst: 0,
      igst: 0,
      total: 0
    }
    setItems(prev => [...prev, newItem])
  }

  const removeItem = (id: string) => {
    if (items.length > 1) {
      setItems(prev => prev.filter(item => item.id !== id))
    }
  }

  const handleSaveDraft = () => {
    console.log('Saving draft...')
    // API call to save draft
  }

  const handleSaveAndSend = () => {
    console.log('Saving and sending...')
    // API call to save and send
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Create Invoice"
        description="Create a new GST-compliant tax invoice"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/finance' },
          { label: 'Invoices', href: '/finance/invoices' },
          { label: 'Create' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link href="/finance/invoices">Cancel</Link>
            </Button>
            <Button variant="outline" size="sm" onClick={handleSaveDraft}>
              <Save className="h-4 w-4 mr-2" />
              Save Draft
            </Button>
            <Button size="sm" onClick={handleSaveAndSend}>
              <Send className="h-4 w-4 mr-2" />
              Save & Send
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Invoice Header */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Invoice Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Invoice Number</Label>
                  <Input
                    value={invoiceNumber}
                    onChange={(e) => setInvoiceNumber(e.target.value)}
                    placeholder="INV-2026-0001"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Invoice Date</Label>
                  <Input
                    type="date"
                    value={invoiceDate}
                    onChange={(e) => setInvoiceDate(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Due Date</Label>
                  <Input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Customer Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Bill To
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Customer</Label>
                  <Select onValueChange={handleCustomerChange}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a customer" />
                    </SelectTrigger>
                    <SelectContent>
                      {customers.map(customer => (
                        <SelectItem key={customer.id} value={customer.id}>
                          {customer.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>GSTIN</Label>
                  <Input
                    value={selectedCustomer?.gstin || ''}
                    readOnly
                    placeholder="Customer GSTIN"
                    className="bg-muted"
                  />
                </div>
              </div>

              {selectedCustomer && (
                <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                  <p className="font-medium">{selectedCustomer.name}</p>
                  <p className="text-sm text-muted-foreground">{selectedCustomer.address}</p>
                  <div className="flex gap-4 mt-2 text-sm">
                    <span>GSTIN: <span className="font-mono">{selectedCustomer.gstin || 'N/A'}</span></span>
                    <span>PAN: <span className="font-mono">{selectedCustomer.pan}</span></span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Place of Supply */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Supply Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Place of Supply</Label>
                  <Select value={placeOfSupply} onValueChange={setPlaceOfSupply}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select state" />
                    </SelectTrigger>
                    <SelectContent>
                      {indianStates.map(state => (
                        <SelectItem key={state.code} value={state.name}>
                          {state.code} - {state.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Supply Type</Label>
                  <Select
                    value={supplyType}
                    onValueChange={(v) => setSupplyType(v as 'goods' | 'services')}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="goods">Goods</SelectItem>
                      <SelectItem value="services">Services</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {placeOfSupply && (
                <div className="mt-4 flex items-center gap-4">
                  <Badge variant={isInterState ? 'default' : 'secondary'}>
                    {isInterState ? 'Inter-State Supply' : 'Intra-State Supply'}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {isInterState
                      ? 'IGST will be applicable'
                      : 'CGST + SGST will be applicable'
                    }
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Line Items */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg">Line Items</CardTitle>
              <Button variant="outline" size="sm" onClick={addItem}>
                <Plus className="h-4 w-4 mr-2" />
                Add Item
              </Button>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="min-w-[200px]">Description</TableHead>
                      <TableHead className="w-[120px]">HSN/SAC</TableHead>
                      <TableHead className="w-[80px] text-right">Qty</TableHead>
                      <TableHead className="w-[80px]">Unit</TableHead>
                      <TableHead className="w-[100px] text-right">Rate</TableHead>
                      <TableHead className="w-[80px] text-right">Disc %</TableHead>
                      <TableHead className="w-[80px]">GST %</TableHead>
                      <TableHead className="w-[100px] text-right">GST Amt</TableHead>
                      <TableHead className="w-[100px] text-right">Total</TableHead>
                      <TableHead className="w-[40px]"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((item, index) => {
                      const calculated = calculateItemTotals(item)
                      return (
                        <TableRow key={item.id}>
                          <TableCell>
                            <Input
                              value={item.description}
                              onChange={(e) => handleItemChange(item.id, 'description', e.target.value)}
                              placeholder="Item description"
                            />
                          </TableCell>
                          <TableCell>
                            <Select
                              value={item.hsnSac}
                              onValueChange={(v) => handleItemChange(item.id, 'hsnSac', v)}
                            >
                              <SelectTrigger>
                                <SelectValue placeholder="Select" />
                              </SelectTrigger>
                              <SelectContent>
                                {hsnSacCodes.map(hsn => (
                                  <SelectItem key={hsn.code} value={hsn.code}>
                                    {hsn.code}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              value={item.quantity}
                              onChange={(e) => handleItemChange(item.id, 'quantity', parseFloat(e.target.value) || 0)}
                              className="text-right"
                            />
                          </TableCell>
                          <TableCell>
                            <Select
                              value={item.unit}
                              onValueChange={(v) => handleItemChange(item.id, 'unit', v)}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="Nos">Nos</SelectItem>
                                <SelectItem value="Hrs">Hrs</SelectItem>
                                <SelectItem value="Days">Days</SelectItem>
                                <SelectItem value="Months">Months</SelectItem>
                                <SelectItem value="Kgs">Kgs</SelectItem>
                                <SelectItem value="Ltrs">Ltrs</SelectItem>
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              value={item.rate}
                              onChange={(e) => handleItemChange(item.id, 'rate', parseFloat(e.target.value) || 0)}
                              className="text-right"
                            />
                          </TableCell>
                          <TableCell>
                            <Input
                              type="number"
                              value={item.discount}
                              onChange={(e) => handleItemChange(item.id, 'discount', parseFloat(e.target.value) || 0)}
                              className="text-right"
                            />
                          </TableCell>
                          <TableCell>
                            <Select
                              value={item.gstRate.toString()}
                              onValueChange={(v) => handleItemChange(item.id, 'gstRate', parseFloat(v))}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {gstRates.map(rate => (
                                  <SelectItem key={rate.value} value={rate.value}>
                                    {rate.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell className="text-right font-mono text-sm">
                            {formatCurrency(calculated.cgst + calculated.sgst + calculated.igst)}
                          </TableCell>
                          <TableCell className="text-right font-mono font-medium">
                            {formatCurrency(calculated.total)}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => removeItem(item.id)}
                              disabled={items.length === 1}
                            >
                              <Trash2 className="h-4 w-4 text-muted-foreground hover:text-red-500" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          {/* Notes & Terms */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Notes & Terms</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Notes</Label>
                <textarea
                  className="w-full min-h-[80px] px-3 py-2 text-sm border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Additional notes for the customer..."
                />
              </div>
              <div className="space-y-2">
                <Label>Terms & Conditions</Label>
                <textarea
                  className="w-full min-h-[100px] px-3 py-2 text-sm border rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-primary"
                  value={terms}
                  onChange={(e) => setTerms(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Summary Sidebar */}
        <div className="space-y-6">
          {/* Seller Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Bill From</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <p className="font-medium">{companyDetails.name}</p>
                <p className="text-muted-foreground">{companyDetails.address}</p>
                <p>GSTIN: <span className="font-mono">{companyDetails.gstin}</span></p>
                <p>State: {companyDetails.state} ({companyDetails.stateCode})</p>
              </div>
            </CardContent>
          </Card>

          {/* Amount Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                Amount Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Subtotal</span>
                  <span>{formatCurrency(totals.subtotal)}</span>
                </div>
                {totals.totalDiscount > 0 && (
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Discount</span>
                    <span className="text-red-600">-{formatCurrency(totals.totalDiscount)}</span>
                  </div>
                )}
                <div className="flex justify-between text-sm font-medium">
                  <span>Taxable Amount</span>
                  <span>{formatCurrency(totals.taxableAmount)}</span>
                </div>

                <div className="border-t pt-3 space-y-2">
                  {!isInterState ? (
                    <>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">CGST</span>
                        <span>{formatCurrency(totals.totalCgst)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">SGST</span>
                        <span>{formatCurrency(totals.totalSgst)}</span>
                      </div>
                    </>
                  ) : (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">IGST</span>
                      <span>{formatCurrency(totals.totalIgst)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-sm font-medium">
                    <span>Total Tax</span>
                    <span>{formatCurrency(totals.totalTax)}</span>
                  </div>
                </div>

                {totals.roundOff !== 0 && (
                  <div className="flex justify-between text-sm border-t pt-3">
                    <span className="text-muted-foreground">Round Off</span>
                    <span>{formatCurrency(totals.roundOff)}</span>
                  </div>
                )}

                <div className="flex justify-between text-lg font-bold border-t pt-3">
                  <span>Grand Total</span>
                  <span className="text-primary">{formatCurrency(totals.finalTotal)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tax Breakup */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Tax Breakup</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-xs">GST %</TableHead>
                    <TableHead className="text-xs text-right">Taxable</TableHead>
                    <TableHead className="text-xs text-right">Tax</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {[5, 12, 18, 28].map(rate => {
                    const itemsAtRate = items.filter(item => item.gstRate === rate)
                    if (itemsAtRate.length === 0) return null
                    const taxable = itemsAtRate.reduce((sum, item) => sum + calculateItemTotals(item).taxableAmount, 0)
                    const tax = (taxable * rate) / 100
                    if (taxable === 0) return null
                    return (
                      <TableRow key={rate}>
                        <TableCell className="text-xs">{rate}%</TableCell>
                        <TableCell className="text-xs text-right">{formatCurrency(taxable)}</TableCell>
                        <TableCell className="text-xs text-right">{formatCurrency(tax)}</TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Bank Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <Banknote className="h-4 w-4" />
                Bank Details for Payment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <p><span className="text-muted-foreground">Account Name:</span> {bankDetails.accountName}</p>
                <p><span className="text-muted-foreground">Account No:</span> <span className="font-mono">{bankDetails.accountNumber}</span></p>
                <p><span className="text-muted-foreground">Bank:</span> {bankDetails.bankName}</p>
                <p><span className="text-muted-foreground">Branch:</span> {bankDetails.branch}</p>
                <p><span className="text-muted-foreground">IFSC:</span> <span className="font-mono">{bankDetails.ifsc}</span></p>
              </div>
            </CardContent>
          </Card>

          {/* E-Invoice Info */}
          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="pt-4">
              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-blue-800">E-Invoice Generation</p>
                  <p className="text-blue-600 mt-1">
                    E-invoice (IRN) will be generated automatically upon saving if the invoice value exceeds Rs. 5 lakhs.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
