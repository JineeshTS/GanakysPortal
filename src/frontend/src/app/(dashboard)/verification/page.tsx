'use client';

import { useState } from 'react';
import { CheckCircle2, XCircle, Clock, AlertTriangle, FileCheck, Download, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/page-header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const verificationItems = [
  {
    id: 1,
    type: 'Payroll',
    period: 'March 2024',
    submittedAt: '2024-04-05T10:30:00Z',
    status: 'pending',
    amount: 4500000,
    employees: 85,
    submittedBy: 'HR Manager',
  },
  {
    id: 2,
    type: 'GST Returns',
    period: 'March 2024 - GSTR-3B',
    submittedAt: '2024-04-10T14:20:00Z',
    status: 'approved',
    amount: 125000,
    verifiedBy: 'CA Sharma',
    verifiedAt: '2024-04-12T09:00:00Z',
  },
  {
    id: 3,
    type: 'TDS Returns',
    period: 'Q4 2023-24',
    submittedAt: '2024-04-08T11:00:00Z',
    status: 'pending',
    amount: 850000,
    submittedBy: 'Finance Manager',
  },
  {
    id: 4,
    type: 'PF Challan',
    period: 'March 2024',
    submittedAt: '2024-04-03T16:45:00Z',
    status: 'approved',
    amount: 520000,
    verifiedBy: 'CA Sharma',
    verifiedAt: '2024-04-05T10:00:00Z',
  },
  {
    id: 5,
    type: 'ESI Challan',
    period: 'March 2024',
    submittedAt: '2024-04-03T16:50:00Z',
    status: 'rejected',
    amount: 85000,
    rejectedBy: 'CA Sharma',
    rejectionReason: 'ESI calculation mismatch for 3 employees',
  },
];

const statusConfig: Record<string, { icon: any; color: string; bg: string }> = {
  pending: { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100' },
  approved: { icon: CheckCircle2, color: 'text-green-600', bg: 'bg-green-100' },
  rejected: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-100' },
};

export default function VerificationPage() {
  const [selectedTab, setSelectedTab] = useState('pending');

  const pendingCount = verificationItems.filter(i => i.status === 'pending').length;
  const approvedCount = verificationItems.filter(i => i.status === 'approved').length;
  const rejectedCount = verificationItems.filter(i => i.status === 'rejected').length;

  const filteredItems = selectedTab === 'all'
    ? verificationItems
    : verificationItems.filter(i => i.status === selectedTab);

  return (
    <div className="space-y-6">
      <PageHeader
        title="CA Verification"
        description="Review and verify financial documents for compliance"
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-yellow-100 rounded-full">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{pendingCount}</div>
                <div className="text-sm text-muted-foreground">Pending Review</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-full">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{approvedCount}</div>
                <div className="text-sm text-muted-foreground">Approved</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-red-100 rounded-full">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{rejectedCount}</div>
                <div className="text-sm text-muted-foreground">Rejected</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <FileCheck className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{verificationItems.length}</div>
                <div className="text-sm text-muted-foreground">Total This Month</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList>
          <TabsTrigger value="pending">
            Pending ({pendingCount})
          </TabsTrigger>
          <TabsTrigger value="approved">
            Approved ({approvedCount})
          </TabsTrigger>
          <TabsTrigger value="rejected">
            Rejected ({rejectedCount})
          </TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>

        <TabsContent value={selectedTab} className="mt-4 space-y-4">
          {filteredItems.map((item) => {
            const config = statusConfig[item.status];
            const StatusIcon = config.icon;

            return (
              <Card key={item.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`p-2 rounded-lg ${config.bg}`}>
                        <StatusIcon className={`h-5 w-5 ${config.color}`} />
                      </div>
                      <div>
                        <h3 className="font-semibold">{item.type}</h3>
                        <p className="text-sm text-muted-foreground">{item.period}</p>
                        <div className="flex items-center gap-4 mt-2 text-sm">
                          <span>Amount: <strong>₹{item.amount.toLocaleString('en-IN')}</strong></span>
                          <span>Submitted: {new Date(item.submittedAt).toLocaleDateString('en-IN')}</span>
                        </div>
                        {item.status === 'rejected' && item.rejectionReason && (
                          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                            <AlertTriangle className="h-4 w-4 inline mr-1" />
                            {item.rejectionReason}
                          </div>
                        )}
                        {item.status === 'approved' && (
                          <p className="text-sm text-green-600 mt-2">
                            Verified by {item.verifiedBy} on {new Date(item.verifiedAt!).toLocaleDateString('en-IN')}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={config.bg + ' ' + config.color}>
                        {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                      </Badge>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                      {item.status === 'pending' && (
                        <>
                          <Button variant="default" size="sm" className="bg-green-600 hover:bg-green-700">
                            Approve
                          </Button>
                          <Button variant="destructive" size="sm">
                            Reject
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </TabsContent>
      </Tabs>
    </div>
  );
}
