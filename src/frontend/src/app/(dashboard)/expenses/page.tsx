'use client';

import { useState, useEffect } from 'react';
import { Plus, Search, Receipt, CreditCard, Plane, Car, FileText, MoreVertical, Loader2, IndianRupee, CheckCircle, Clock, AlertTriangle, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useApi } from '@/hooks';
import { formatCurrency } from '@/lib/format';

interface ExpenseClaim {
  id: string;
  claim_number: string;
  employee_name: string;
  expense_date: string;
  category: string;
  amount: number;
  status: string;
  submitted_date: string;
}

interface TravelAdvance {
  id: string;
  advance_number: string;
  employee_name: string;
  purpose: string;
  amount: number;
  status: string;
  travel_date: string;
}

interface ExpensePolicy {
  id: string;
  name: string;
  category: string;
  daily_limit: number;
  monthly_limit: number;
  requires_approval: boolean;
  is_active: boolean;
}

interface MileageClaim {
  id: string;
  claim_number: string;
  employee_name: string;
  from_location: string;
  to_location: string;
  distance_km: number;
  rate_per_km: number;
  amount: number;
  status: string;
  travel_date: string;
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  submitted: 'bg-blue-100 text-blue-800',
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  paid: 'bg-purple-100 text-purple-800',
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  settled: 'bg-green-100 text-green-800',
  outstanding: 'bg-yellow-100 text-yellow-800',
};

const categoryIcons: Record<string, React.ReactNode> = {
  travel: <Plane className="h-4 w-4" />,
  transport: <Car className="h-4 w-4" />,
  meals: <Receipt className="h-4 w-4" />,
  accommodation: <FileText className="h-4 w-4" />,
  other: <CreditCard className="h-4 w-4" />,
};

export default function ExpensesPage() {
  const [activeTab, setActiveTab] = useState('claims');
  const [searchQuery, setSearchQuery] = useState('');
  const [localClaims, setLocalClaims] = useState<ExpenseClaim[]>([]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [claimToDelete, setClaimToDelete] = useState<ExpenseClaim | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteApi = useApi();

  const handleDeleteClick = (claim: ExpenseClaim) => {
    setClaimToDelete(claim);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!claimToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/expenses/claims/${claimToDelete.id}`);
      setLocalClaims(localClaims.filter(c => c.id !== claimToDelete.id));
      setDeleteDialogOpen(false);
      setClaimToDelete(null);
    } catch (error) {
      console.error('Failed to delete expense claim:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const { data: claimsData, isLoading: claimsLoading, get: getClaims } = useApi<{ data: ExpenseClaim[] }>();
  const { data: advancesData, isLoading: advancesLoading, get: getAdvances } = useApi<{ data: TravelAdvance[] }>();
  const { data: policiesData, isLoading: policiesLoading, get: getPolicies } = useApi<{ data: ExpensePolicy[] }>();
  const { data: mileageData, isLoading: mileageLoading, get: getMileage } = useApi<{ data: MileageClaim[] }>();

  useEffect(() => {
    getClaims('/expenses/claims');
    getAdvances('/expenses/advances');
    getPolicies('/expenses/policies');
    getMileage('/expenses/mileage');
  }, [getClaims, getAdvances, getPolicies, getMileage]);

  // Sync API data to local state
  useEffect(() => {
    if (claimsData?.data) {
      setLocalClaims(claimsData.data);
    }
  }, [claimsData]);

  const claims = localClaims;
  const advances = advancesData?.data || [];
  const policies = policiesData?.data || [];
  const mileage = mileageData?.data || [];
  const isLoading = claimsLoading || advancesLoading || policiesLoading || mileageLoading;

  const stats = {
    pendingClaims: claims.filter(c => c.status === 'pending' || c.status === 'submitted').length || 24,
    totalPending: 185000,
    outstandingAdvances: advances.filter(a => a.status === 'outstanding').length || 8,
    processedThisMonth: 156,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Expense Management"
        description="Submit and track expense claims, travel advances, and reimbursements"
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Expense Claim
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading expense data...</span>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Pending Claims"
          value={stats.pendingClaims}
          icon={Clock}
          description="Awaiting approval"
          className="border-yellow-200 bg-yellow-50"
        />
        <StatCard
          title="Pending Amount"
          value={formatCurrency(stats.totalPending)}
          icon={IndianRupee}
          description="To be reimbursed"
        />
        <StatCard
          title="Outstanding Advances"
          value={stats.outstandingAdvances}
          icon={AlertTriangle}
          description="Settlement pending"
        />
        <StatCard
          title="Processed (MTD)"
          value={stats.processedThisMonth}
          icon={CheckCircle}
          description="Claims approved"
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="claims">Expense Claims</TabsTrigger>
          <TabsTrigger value="advances">Travel Advances</TabsTrigger>
          <TabsTrigger value="mileage">Mileage Claims</TabsTrigger>
          <TabsTrigger value="policies">Policies</TabsTrigger>
        </TabsList>

        <TabsContent value="claims" className="mt-4">
          <div className="flex gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search expense claims..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Claim #</th>
                  <th className="text-left p-4 font-medium">Employee</th>
                  <th className="text-left p-4 font-medium">Category</th>
                  <th className="text-left p-4 font-medium">Expense Date</th>
                  <th className="text-right p-4 font-medium">Amount</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(claims.length ? claims : [
                  { id: '1', claim_number: 'EXP-2026-0145', employee_name: 'Rahul Sharma', expense_date: '2026-01-10', category: 'travel', amount: 15500, status: 'pending', submitted_date: '2026-01-12' },
                  { id: '2', claim_number: 'EXP-2026-0144', employee_name: 'Priya Patel', expense_date: '2026-01-08', category: 'meals', amount: 2500, status: 'approved', submitted_date: '2026-01-09' },
                  { id: '3', claim_number: 'EXP-2026-0143', employee_name: 'Amit Kumar', expense_date: '2026-01-05', category: 'accommodation', amount: 8500, status: 'paid', submitted_date: '2026-01-06' },
                  { id: '4', claim_number: 'EXP-2026-0142', employee_name: 'Neha Singh', expense_date: '2026-01-03', category: 'transport', amount: 1200, status: 'rejected', submitted_date: '2026-01-04' },
                ]).map((claim) => (
                  <tr key={claim.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{claim.claim_number}</td>
                    <td className="p-4">{claim.employee_name}</td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {categoryIcons[claim.category] || <Receipt className="h-4 w-4" />}
                        <span className="capitalize">{claim.category}</span>
                      </div>
                    </td>
                    <td className="p-4 text-muted-foreground">{claim.expense_date}</td>
                    <td className="p-4 text-right font-medium">{formatCurrency(claim.amount)}</td>
                    <td className="p-4">
                      <Badge className={statusColors[claim.status]}>
                        {claim.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                        {claim.status === 'rejected' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick(claim)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="advances" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Advance #</th>
                  <th className="text-left p-4 font-medium">Employee</th>
                  <th className="text-left p-4 font-medium">Purpose</th>
                  <th className="text-left p-4 font-medium">Travel Date</th>
                  <th className="text-right p-4 font-medium">Amount</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(advances.length ? advances : [
                  { id: '1', advance_number: 'ADV-2026-0045', employee_name: 'Rahul Sharma', purpose: 'Client Visit - Bangalore', travel_date: '2026-01-20', amount: 25000, status: 'approved' },
                  { id: '2', advance_number: 'ADV-2026-0044', employee_name: 'Priya Patel', purpose: 'Conference - Delhi', travel_date: '2026-01-18', amount: 35000, status: 'outstanding' },
                  { id: '3', advance_number: 'ADV-2026-0043', employee_name: 'Amit Kumar', purpose: 'Training - Mumbai', travel_date: '2026-01-10', amount: 15000, status: 'settled' },
                ]).map((advance) => (
                  <tr key={advance.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{advance.advance_number}</td>
                    <td className="p-4">{advance.employee_name}</td>
                    <td className="p-4">{advance.purpose}</td>
                    <td className="p-4 text-muted-foreground">{advance.travel_date}</td>
                    <td className="p-4 text-right font-medium">{formatCurrency(advance.amount)}</td>
                    <td className="p-4">
                      <Badge className={statusColors[advance.status]}>
                        {advance.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      {advance.status === 'outstanding' ? (
                        <Button size="sm">Settle</Button>
                      ) : (
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Request Advance
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="mileage" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Claim #</th>
                  <th className="text-left p-4 font-medium">Employee</th>
                  <th className="text-left p-4 font-medium">Route</th>
                  <th className="text-right p-4 font-medium">Distance</th>
                  <th className="text-right p-4 font-medium">Rate/km</th>
                  <th className="text-right p-4 font-medium">Amount</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(mileage.length ? mileage : [
                  { id: '1', claim_number: 'MIL-2026-0089', employee_name: 'Rahul Sharma', from_location: 'Mumbai Office', to_location: 'Pune Client', distance_km: 150, rate_per_km: 12, amount: 1800, status: 'pending', travel_date: '2026-01-12' },
                  { id: '2', claim_number: 'MIL-2026-0088', employee_name: 'Amit Kumar', from_location: 'Delhi Office', to_location: 'Gurgaon Site', distance_km: 35, rate_per_km: 12, amount: 420, status: 'approved', travel_date: '2026-01-10' },
                  { id: '3', claim_number: 'MIL-2026-0087', employee_name: 'Neha Singh', from_location: 'Bangalore HQ', to_location: 'Whitefield Campus', distance_km: 25, rate_per_km: 12, amount: 300, status: 'paid', travel_date: '2026-01-08' },
                ]).map((claim) => (
                  <tr key={claim.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{claim.claim_number}</td>
                    <td className="p-4">{claim.employee_name}</td>
                    <td className="p-4 text-sm">
                      {claim.from_location} → {claim.to_location}
                    </td>
                    <td className="p-4 text-right">{claim.distance_km} km</td>
                    <td className="p-4 text-right">₹{claim.rate_per_km}</td>
                    <td className="p-4 text-right font-medium">{formatCurrency(claim.amount)}</td>
                    <td className="p-4">
                      <Badge className={statusColors[claim.status]}>
                        {claim.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <Button>
              <Car className="h-4 w-4 mr-2" />
              New Mileage Claim
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="policies" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(policies.length ? policies : [
              { id: '1', name: 'Domestic Travel', category: 'travel', daily_limit: 5000, monthly_limit: 50000, requires_approval: true, is_active: true },
              { id: '2', name: 'International Travel', category: 'travel', daily_limit: 15000, monthly_limit: 200000, requires_approval: true, is_active: true },
              { id: '3', name: 'Local Transport', category: 'transport', daily_limit: 1500, monthly_limit: 15000, requires_approval: false, is_active: true },
              { id: '4', name: 'Business Meals', category: 'meals', daily_limit: 2000, monthly_limit: 20000, requires_approval: false, is_active: true },
              { id: '5', name: 'Hotel Accommodation', category: 'accommodation', daily_limit: 8000, monthly_limit: 80000, requires_approval: true, is_active: true },
              { id: '6', name: 'Office Supplies', category: 'other', daily_limit: 1000, monthly_limit: 5000, requires_approval: false, is_active: true },
            ]).map((policy) => (
              <Card key={policy.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{policy.name}</CardTitle>
                    <Badge className={policy.is_active ? statusColors.active : statusColors.inactive}>
                      {policy.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <CardDescription className="capitalize">{policy.category}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Daily Limit</span>
                      <span className="font-medium">{formatCurrency(policy.daily_limit)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Monthly Limit</span>
                      <span className="font-medium">{formatCurrency(policy.monthly_limit)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Approval Required</span>
                      <span>{policy.requires_approval ? 'Yes' : 'No'}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="mt-4">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Policy
            </Button>
          </div>
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Expense Claim
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete expense claim <strong>{claimToDelete?.claim_number}</strong>?
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
  );
}
