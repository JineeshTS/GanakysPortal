'use client'

import * as React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatDate } from '@/lib/format'
import { QrCode } from 'lucide-react'
import type { Invoice, InvoiceItem } from '@/types'

interface InvoicePreviewProps {
  invoice: Invoice
  companyDetails: {
    name: string
    legalName: string
    gstin: string
    pan: string
    address: string
    state: string
    stateCode: string
    email: string
    phone: string
    logo?: string
  }
  bankDetails: {
    accountName: string
    accountNumber: string
    bankName: string
    branch: string
    ifsc: string
  }
  showQrCode?: boolean
}

export function InvoicePreview({
  invoice,
  companyDetails,
  bankDetails,
  showQrCode = true
}: InvoicePreviewProps) {
  const isInterState = invoice.supply_type === 'inter_state' || invoice.supply_type === 'export'

  // Number to words (Indian format)
  const numberToWords = (num: number): string => {
    const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
      'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

    if (num === 0) return 'Zero'

    const convertLessThanThousand = (n: number): string => {
      if (n === 0) return ''
      if (n < 20) return ones[n]
      if (n < 100) return tens[Math.floor(n / 10)] + (n % 10 ? ' ' + ones[n % 10] : '')
      return ones[Math.floor(n / 100)] + ' Hundred' + (n % 100 ? ' ' + convertLessThanThousand(n % 100) : '')
    }

    const convert = (n: number): string => {
      if (n < 1000) return convertLessThanThousand(n)
      if (n < 100000) return convertLessThanThousand(Math.floor(n / 1000)) + ' Thousand' + (n % 1000 ? ' ' + convertLessThanThousand(n % 1000) : '')
      if (n < 10000000) return convertLessThanThousand(Math.floor(n / 100000)) + ' Lakh' + (n % 100000 ? ' ' + convert(n % 100000) : '')
      return convertLessThanThousand(Math.floor(n / 10000000)) + ' Crore' + (n % 10000000 ? ' ' + convert(n % 10000000) : '')
    }

    const rupees = Math.floor(num)
    const paise = Math.round((num - rupees) * 100)

    let words = 'Rupees ' + convert(rupees)
    if (paise > 0) {
      words += ' and ' + convert(paise) + ' Paise'
    }
    return words + ' Only'
  }

  return (
    <Card className="max-w-4xl mx-auto print:shadow-none print:border-none">
      <CardContent className="p-8 print:p-4">
        {/* Header */}
        <div className="flex justify-between items-start border-b pb-4 mb-4">
          <div>
            {companyDetails.logo && (
              <img src={companyDetails.logo} alt="Company Logo" className="h-16 mb-2" />
            )}
            <h1 className="text-xl font-bold">{companyDetails.name}</h1>
            <p className="text-sm text-muted-foreground">{companyDetails.legalName}</p>
            <p className="text-sm mt-1">{companyDetails.address}</p>
            <div className="text-sm mt-2 space-y-1">
              <p>GSTIN: <span className="font-mono font-medium">{companyDetails.gstin}</span></p>
              <p>PAN: <span className="font-mono">{companyDetails.pan}</span></p>
              <p>State: {companyDetails.state} ({companyDetails.stateCode})</p>
            </div>
          </div>
          <div className="text-right">
            <h2 className="text-2xl font-bold text-primary">TAX INVOICE</h2>
            {invoice.irn && (
              <Badge className="bg-green-100 text-green-800 mt-2">E-Invoice Generated</Badge>
            )}
            <div className="mt-4 text-sm">
              <p><span className="text-muted-foreground">Invoice No:</span> <span className="font-mono font-medium">{invoice.invoice_number}</span></p>
              <p><span className="text-muted-foreground">Date:</span> {formatDate(invoice.invoice_date)}</p>
              <p><span className="text-muted-foreground">Due Date:</span> {formatDate(invoice.due_date)}</p>
            </div>
          </div>
        </div>

        {/* Customer & Supply Details */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="border rounded p-4">
            <h3 className="font-semibold text-sm text-muted-foreground mb-2">BILL TO</h3>
            <p className="font-medium">{invoice.customer_name}</p>
            {invoice.customer_gstin && (
              <p className="text-sm mt-1">GSTIN: <span className="font-mono">{invoice.customer_gstin}</span></p>
            )}
          </div>
          <div className="border rounded p-4">
            <h3 className="font-semibold text-sm text-muted-foreground mb-2">SUPPLY DETAILS</h3>
            <p className="text-sm">Place of Supply: <span className="font-medium">{invoice.place_of_supply}</span></p>
            <p className="text-sm">Supply Type: <span className="font-medium capitalize">{invoice.supply_type.replace('_', ' ')}</span></p>
            {isInterState ? (
              <Badge variant="outline" className="mt-2">Inter-State (IGST)</Badge>
            ) : (
              <Badge variant="outline" className="mt-2">Intra-State (CGST+SGST)</Badge>
            )}
          </div>
        </div>

        {/* Line Items Table */}
        <table className="w-full text-sm border mb-6">
          <thead>
            <tr className="bg-muted/50">
              <th className="border p-2 text-left">#</th>
              <th className="border p-2 text-left">Description</th>
              <th className="border p-2 text-center">HSN/SAC</th>
              <th className="border p-2 text-right">Qty</th>
              <th className="border p-2 text-right">Rate</th>
              <th className="border p-2 text-right">Taxable</th>
              {isInterState ? (
                <th className="border p-2 text-right">IGST</th>
              ) : (
                <>
                  <th className="border p-2 text-right">CGST</th>
                  <th className="border p-2 text-right">SGST</th>
                </>
              )}
              <th className="border p-2 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {invoice.items.map((item, index) => (
              <tr key={item.id}>
                <td className="border p-2">{index + 1}</td>
                <td className="border p-2">{item.description}</td>
                <td className="border p-2 text-center font-mono">{item.hsn_code}</td>
                <td className="border p-2 text-right">{item.quantity} {item.unit}</td>
                <td className="border p-2 text-right">{formatCurrency(item.rate)}</td>
                <td className="border p-2 text-right">{formatCurrency(item.taxable_amount)}</td>
                {isInterState ? (
                  <td className="border p-2 text-right">
                    {formatCurrency(item.igst)}
                    <br />
                    <span className="text-xs text-muted-foreground">@{item.gst_rate}%</span>
                  </td>
                ) : (
                  <>
                    <td className="border p-2 text-right">
                      {formatCurrency(item.cgst)}
                      <br />
                      <span className="text-xs text-muted-foreground">@{item.gst_rate / 2}%</span>
                    </td>
                    <td className="border p-2 text-right">
                      {formatCurrency(item.sgst)}
                      <br />
                      <span className="text-xs text-muted-foreground">@{item.gst_rate / 2}%</span>
                    </td>
                  </>
                )}
                <td className="border p-2 text-right font-medium">{formatCurrency(item.total)}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Summary */}
        <div className="flex justify-between mb-6">
          <div className="flex-1">
            {/* Tax Summary by Rate */}
            <table className="text-sm border">
              <thead>
                <tr className="bg-muted/50">
                  <th className="border p-2 text-left">Tax Rate</th>
                  <th className="border p-2 text-right">Taxable</th>
                  {isInterState ? (
                    <th className="border p-2 text-right">IGST</th>
                  ) : (
                    <>
                      <th className="border p-2 text-right">CGST</th>
                      <th className="border p-2 text-right">SGST</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {/* Group by GST rate */}
                {[5, 12, 18, 28].map(rate => {
                  const itemsAtRate = invoice.items.filter(item => item.gst_rate === rate)
                  if (itemsAtRate.length === 0) return null
                  const taxable = itemsAtRate.reduce((sum, item) => sum + item.taxable_amount, 0)
                  const cgst = itemsAtRate.reduce((sum, item) => sum + item.cgst, 0)
                  const sgst = itemsAtRate.reduce((sum, item) => sum + item.sgst, 0)
                  const igst = itemsAtRate.reduce((sum, item) => sum + item.igst, 0)
                  return (
                    <tr key={rate}>
                      <td className="border p-2">{rate}%</td>
                      <td className="border p-2 text-right">{formatCurrency(taxable)}</td>
                      {isInterState ? (
                        <td className="border p-2 text-right">{formatCurrency(igst)}</td>
                      ) : (
                        <>
                          <td className="border p-2 text-right">{formatCurrency(cgst)}</td>
                          <td className="border p-2 text-right">{formatCurrency(sgst)}</td>
                        </>
                      )}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <div className="w-64 ml-6">
            <table className="w-full text-sm">
              <tbody>
                <tr>
                  <td className="py-1 text-muted-foreground">Subtotal</td>
                  <td className="py-1 text-right">{formatCurrency(invoice.subtotal)}</td>
                </tr>
                {invoice.discount > 0 && (
                  <tr>
                    <td className="py-1 text-muted-foreground">Discount</td>
                    <td className="py-1 text-right text-red-600">-{formatCurrency(invoice.discount)}</td>
                  </tr>
                )}
                <tr className="border-t">
                  <td className="py-1 font-medium">Taxable Amount</td>
                  <td className="py-1 text-right font-medium">{formatCurrency(invoice.taxable_amount)}</td>
                </tr>
                {isInterState ? (
                  <tr>
                    <td className="py-1 text-muted-foreground">IGST</td>
                    <td className="py-1 text-right">{formatCurrency(invoice.igst)}</td>
                  </tr>
                ) : (
                  <>
                    <tr>
                      <td className="py-1 text-muted-foreground">CGST</td>
                      <td className="py-1 text-right">{formatCurrency(invoice.cgst)}</td>
                    </tr>
                    <tr>
                      <td className="py-1 text-muted-foreground">SGST</td>
                      <td className="py-1 text-right">{formatCurrency(invoice.sgst)}</td>
                    </tr>
                  </>
                )}
                {invoice.cess > 0 && (
                  <tr>
                    <td className="py-1 text-muted-foreground">Cess</td>
                    <td className="py-1 text-right">{formatCurrency(invoice.cess)}</td>
                  </tr>
                )}
                {invoice.round_off !== 0 && (
                  <tr>
                    <td className="py-1 text-muted-foreground">Round Off</td>
                    <td className="py-1 text-right">{formatCurrency(invoice.round_off)}</td>
                  </tr>
                )}
                <tr className="border-t-2 border-primary">
                  <td className="py-2 font-bold text-lg">Grand Total</td>
                  <td className="py-2 text-right font-bold text-lg text-primary">{formatCurrency(invoice.total)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Amount in Words */}
        <div className="border-t border-b py-2 mb-6">
          <p className="text-sm">
            <span className="text-muted-foreground">Amount in Words:</span>{' '}
            <span className="font-medium">{numberToWords(invoice.total)}</span>
          </p>
        </div>

        {/* Bank Details & E-Invoice Info */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="border rounded p-4">
            <h3 className="font-semibold text-sm text-muted-foreground mb-2">BANK DETAILS</h3>
            <div className="text-sm space-y-1">
              <p>Account Name: {bankDetails.accountName}</p>
              <p>Account No: <span className="font-mono">{bankDetails.accountNumber}</span></p>
              <p>Bank: {bankDetails.bankName}</p>
              <p>Branch: {bankDetails.branch}</p>
              <p>IFSC: <span className="font-mono">{bankDetails.ifsc}</span></p>
            </div>
          </div>
          {invoice.irn && (
            <div className="border rounded p-4">
              <h3 className="font-semibold text-sm text-muted-foreground mb-2">E-INVOICE DETAILS</h3>
              <div className="text-sm space-y-1">
                <p>IRN: <span className="font-mono text-xs break-all">{invoice.irn}</span></p>
                <p>Ack No: <span className="font-mono">{invoice.ack_number}</span></p>
                <p>Ack Date: {formatDate(invoice.ack_date || '')}</p>
              </div>
              {showQrCode && invoice.qr_code && (
                <div className="mt-2 flex justify-center">
                  <div className="w-24 h-24 bg-muted flex items-center justify-center">
                    <QrCode className="h-16 w-16 text-muted-foreground" />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Notes & Terms */}
        {(invoice.notes || invoice.terms) && (
          <div className="border-t pt-4 mb-6 text-sm">
            {invoice.notes && (
              <div className="mb-2">
                <p className="font-medium text-muted-foreground">Notes:</p>
                <p className="whitespace-pre-line">{invoice.notes}</p>
              </div>
            )}
            {invoice.terms && (
              <div>
                <p className="font-medium text-muted-foreground">Terms & Conditions:</p>
                <p className="whitespace-pre-line">{invoice.terms}</p>
              </div>
            )}
          </div>
        )}

        {/* Signature */}
        <div className="flex justify-end">
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-12">For {companyDetails.name}</p>
            <p className="border-t pt-2">Authorized Signatory</p>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t mt-6 pt-4 text-center text-xs text-muted-foreground">
          <p>This is a computer-generated invoice and does not require a physical signature.</p>
          <p className="mt-1">Email: {companyDetails.email} | Phone: {companyDetails.phone}</p>
        </div>
      </CardContent>
    </Card>
  )
}

export default InvoicePreview
