'use client';

import { useState, useEffect } from 'react';
import { useApi } from '@/hooks';
import { Plus, Search, Filter, FileText, Send, Copy, MoreVertical, Loader2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { PageHeader } from '@/components/layout/page-header';
import { DataTable } from '@/components/layout/data-table';

// API Response interfaces
interface Quotation {
  id: string;
  customer: string;
  customer_id: string;
  amount: number;
  status: string;
  validUntil: string;
  valid_until: string;
  createdAt: string;
  created_at: string;
}

interface QuotationsListResponse {
  quotations: Quotation[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const sampleQuotations = [
  {
    id: 'QT-2024-001',
    customer: 'ABC Technologies Pvt Ltd',
    amount: 245000,
    status: 'sent',
    validUntil: '2024-04-15',
    createdAt: '2024-03-15',
  },
  {
    id: 'QT-2024-002',
    customer: 'XYZ Industries',
    amount: 180000,
    status: 'draft',
    validUntil: '2024-04-20',
    createdAt: '2024-03-18',
  },
  {
    id: 'QT-2024-003',
    customer: 'Global Solutions Ltd',
    amount: 520000,
    status: 'accepted',
    validUntil: '2024-04-10',
    createdAt: '2024-03-10',
  },
  {
    id: 'QT-2024-004',
    customer: 'Tech Innovators',
    amount: 95000,
    status: 'expired',
    validUntil: '2024-03-01',
    createdAt: '2024-02-15',
  },
];

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  sent: 'bg-blue-100 text-blue-800',
  accepted: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  expired: 'bg-yellow-100 text-yellow-800',
};

export default function QuotationsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: quotationsData, isLoading, error, get } = useApi<QuotationsListResponse>();

  // Fetch quotations on mount
  useEffect(() => {
    const params = new URLSearchParams();
    if (searchQuery) params.set('search', searchQuery);
    get(`/quotations?${params.toString()}`);
  }, [searchQuery, get]);

  const quotations = quotationsData?.quotations || sampleQuotations;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Quotations"
        description="Create and manage sales quotations"
      >
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Quotation
        </Button>
      </PageHeader>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading quotations...</span>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </Card>
      )}

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search quotations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          Filter
        </Button>
      </div>

      <div className="border rounded-lg">
        <table className="w-full">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left p-4 font-medium">Quotation #</th>
              <th className="text-left p-4 font-medium">Customer</th>
              <th className="text-right p-4 font-medium">Amount</th>
              <th className="text-left p-4 font-medium">Status</th>
              <th className="text-left p-4 font-medium">Valid Until</th>
              <th className="text-right p-4 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {quotations.map((quotation) => (
              <tr key={quotation.id} className="border-t hover:bg-muted/30">
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{quotation.id}</span>
                  </div>
                </td>
                <td className="p-4">{quotation.customer}</td>
                <td className="p-4 text-right font-medium">
                  ₹{quotation.amount.toLocaleString('en-IN')}
                </td>
                <td className="p-4">
                  <Badge className={statusColors[quotation.status] || statusColors.draft}>
                    {quotation.status.charAt(0).toUpperCase() + quotation.status.slice(1)}
                  </Badge>
                </td>
                <td className="p-4 text-muted-foreground">
                  {new Date(quotation.valid_until || quotation.validUntil).toLocaleDateString('en-IN')}
                </td>
                <td className="p-4 text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Button variant="ghost" size="icon">
                      <Send className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
