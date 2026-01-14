'use client'

import * as React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
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
import { Plus, Trash2 } from 'lucide-react'

// Indian State Codes for Place of Supply
export const indianStates = [
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
export const gstRates = [
  { value: '0', label: '0%' },
  { value: '5', label: '5%' },
  { value: '12', label: '12%' },
  { value: '18', label: '18%' },
  { value: '28', label: '28%' },
]

// Common HSN/SAC codes
export const hsnSacCodes = [
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

export interface InvoiceLineItem {
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

export interface Customer {
  id: string
  name: string
  gstin?: string
  pan: string
  state: string
  stateCode: string
  address: string
}

interface InvoiceFormProps {
  companyStateCode: string
  customers: Customer[]
  onSubmit: (data: InvoiceFormData) => void
  initialData?: Partial<InvoiceFormData>
}

export interface InvoiceFormData {
  invoiceNumber: string
  invoiceDate: string
  dueDate: string
  customerId: string
  placeOfSupply: string
  supplyType: 'goods' | 'services'
  items: InvoiceLineItem[]
  notes: string
  terms: string
}

export function InvoiceForm({
  companyStateCode,
  customers,
  onSubmit,
  initialData
}: InvoiceFormProps) {
  const [selectedCustomer, setSelectedCustomer] = React.useState<Customer | null>(null)
  const [placeOfSupply, setPlaceOfSupply] = React.useState(initialData?.placeOfSupply || '')
  const [supplyType, setSupplyType] = React.useState<'goods' | 'services'>(
    initialData?.supplyType || 'services'
  )
  const [invoiceNumber, setInvoiceNumber] = React.useState(initialData?.invoiceNumber || '')
  const [invoiceDate, setInvoiceDate] = React.useState(
    initialData?.invoiceDate || new Date().toISOString().split('T')[0]
  )
  const [dueDate, setDueDate] = React.useState(initialData?.dueDate || '')
  const [notes, setNotes] = React.useState(initialData?.notes || '')
  const [terms, setTerms] = React.useState(
    initialData?.terms ||
    '1. Payment due within 30 days from invoice date.\n2. Interest @ 18% per annum will be charged on delayed payments.'
  )

  const [items, setItems] = React.useState<InvoiceLineItem[]>(
    initialData?.items || [createEmptyItem()]
  )

  function createEmptyItem(): InvoiceLineItem {
    return {
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
  }

  // Determine if intra-state or inter-state
  const isInterState = React.useMemo(() => {
    if (!placeOfSupply) return false
    const posStateCode = indianStates.find(s => s.name === placeOfSupply)?.code
    return posStateCode !== companyStateCode
  }, [placeOfSupply, companyStateCode])

  // Calculate line item totals
  const calculateItemTotals = (item: InvoiceLineItem): InvoiceLineItem => {
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

  const handleItemChange = (id: string, field: keyof InvoiceLineItem, value: string | number) => {
    setItems(prev => prev.map(item => {
      if (item.id === id) {
        const updated = { ...item, [field]: value }
        return calculateItemTotals(updated)
      }
      return item
    }))
  }

  const addItem = () => {
    setItems(prev => [...prev, createEmptyItem()])
  }

  const removeItem = (id: string) => {
    if (items.length > 1) {
      setItems(prev => prev.filter(item => item.id !== id))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      invoiceNumber,
      invoiceDate,
      dueDate,
      customerId: selectedCustomer?.id || '',
      placeOfSupply,
      supplyType,
      items: items.map(calculateItemTotals),
      notes,
      terms
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Invoice Header */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Invoice Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Invoice Number *</Label>
              <Input
                value={invoiceNumber}
                onChange={(e) => setInvoiceNumber(e.target.value)}
                placeholder="INV-2026-0001"
                required
              />
            </div>
            <div className="space-y-2">
              <Label>Invoice Date *</Label>
              <Input
                type="date"
                value={invoiceDate}
                onChange={(e) => setInvoiceDate(e.target.value)}
                required
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
          <CardTitle className="text-lg">Bill To</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Customer *</Label>
              <Select onValueChange={handleCustomerChange} required>
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
        </CardContent>
      </Card>

      {/* Place of Supply */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Supply Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Place of Supply *</Label>
              <Select value={placeOfSupply} onValueChange={setPlaceOfSupply} required>
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
        </CardContent>
      </Card>

      {/* Line Items */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">Line Items</CardTitle>
          <Button type="button" variant="outline" size="sm" onClick={addItem}>
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
                  <TableHead className="w-[100px] text-right">Rate</TableHead>
                  <TableHead className="w-[80px]">GST %</TableHead>
                  <TableHead className="w-[100px] text-right">Amount</TableHead>
                  <TableHead className="w-[40px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => {
                  const calculated = calculateItemTotals(item)
                  return (
                    <TableRow key={item.id}>
                      <TableCell>
                        <Input
                          value={item.description}
                          onChange={(e) => handleItemChange(item.id, 'description', e.target.value)}
                          placeholder="Item description"
                          required
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
                          required
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={item.rate}
                          onChange={(e) => handleItemChange(item.id, 'rate', parseFloat(e.target.value) || 0)}
                          className="text-right"
                          required
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
                      <TableCell className="text-right font-mono">
                        {formatCurrency(calculated.total)}
                      </TableCell>
                      <TableCell>
                        <Button
                          type="button"
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

          {/* Totals */}
          <div className="mt-6 flex justify-end">
            <div className="w-full max-w-xs space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal</span>
                <span>{formatCurrency(totals.subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Taxable Amount</span>
                <span>{formatCurrency(totals.taxableAmount)}</span>
              </div>
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
              {totals.roundOff !== 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Round Off</span>
                  <span>{formatCurrency(totals.roundOff)}</span>
                </div>
              )}
              <div className="flex justify-between text-lg font-bold border-t pt-2">
                <span>Grand Total</span>
                <span className="text-primary">{formatCurrency(totals.finalTotal)}</span>
              </div>
            </div>
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
    </form>
  )
}

export default InvoiceForm
