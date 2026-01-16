'use client';

import { useState, useEffect } from 'react';
import { Plus, Search, DollarSign, RefreshCw, TrendingUp, TrendingDown, Globe, MoreVertical, Loader2, Calculator, ArrowRightLeft, Trash2, AlertTriangle } from 'lucide-react';
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

interface Currency {
  id: string;
  code: string;
  name: string;
  symbol: string;
  exchange_rate: number;
  is_base: boolean;
  is_active: boolean;
  last_updated: string;
}

interface ExchangeRate {
  id: string;
  from_currency: string;
  to_currency: string;
  rate: number;
  rate_type: string;
  effective_date: string;
  source: string;
}

interface Revaluation {
  id: string;
  reference_number: string;
  revaluation_date: string;
  currency: string;
  accounts_affected: number;
  gain_loss: number;
  status: string;
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  draft: 'bg-yellow-100 text-yellow-800',
  posted: 'bg-green-100 text-green-800',
  reversed: 'bg-red-100 text-red-800',
};

export default function CurrencyPage() {
  const [activeTab, setActiveTab] = useState('currencies');
  const [localCurrencies, setLocalCurrencies] = useState<Currency[]>([]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [currencyToDelete, setCurrencyToDelete] = useState<Currency | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteApi = useApi();

  const handleDeleteClick = (currency: Currency) => {
    setCurrencyToDelete(currency);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!currencyToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/currency/currencies/${currencyToDelete.id}`);
      setLocalCurrencies(localCurrencies.filter(c => c.id !== currencyToDelete.id));
      setDeleteDialogOpen(false);
      setCurrencyToDelete(null);
    } catch (error) {
      console.error('Failed to delete currency:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const { data: currenciesData, isLoading: currenciesLoading, get: getCurrencies } = useApi<{ data: Currency[] }>();
  const { data: ratesData, isLoading: ratesLoading, get: getRates } = useApi<{ data: ExchangeRate[] }>();
  const { data: revaluationsData, isLoading: revaluationsLoading, get: getRevaluations } = useApi<{ data: Revaluation[] }>();

  useEffect(() => {
    getCurrencies('/currency/currencies');
    getRates('/currency/exchange-rates');
    getRevaluations('/currency/revaluations');
  }, [getCurrencies, getRates, getRevaluations]);

  // Sync API data to local state
  useEffect(() => {
    if (currenciesData?.data) {
      setLocalCurrencies(currenciesData.data);
    }
  }, [currenciesData]);

  const currencies = localCurrencies;
  const rates = ratesData?.data || [];
  const revaluations = revaluationsData?.data || [];
  const isLoading = currenciesLoading || ratesLoading || revaluationsLoading;

  const stats = {
    activeCurrencies: currencies.filter(c => c.is_active).length || 8,
    exchangeRates: rates.length || 24,
    pendingRevaluations: revaluations.filter(r => r.status === 'draft').length || 2,
    unrealizedGainLoss: 125000,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Multi-Currency Management"
        description="Manage currencies, exchange rates, and foreign currency revaluations"
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Currency
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading currency data...</span>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Active Currencies"
          value={stats.activeCurrencies}
          icon={Globe}
          description="Configured currencies"
        />
        <StatCard
          title="Exchange Rates"
          value={stats.exchangeRates}
          icon={ArrowRightLeft}
          description="Rate pairs"
        />
        <StatCard
          title="Pending Revaluations"
          value={stats.pendingRevaluations}
          icon={Calculator}
          description="Awaiting posting"
        />
        <StatCard
          title="Unrealized Gain/Loss"
          value={`₹${stats.unrealizedGainLoss.toLocaleString()}`}
          icon={TrendingUp}
          description="Current period"
          trend={{ value: 2.3, type: 'increase' }}
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="currencies">Currencies</TabsTrigger>
          <TabsTrigger value="exchange-rates">Exchange Rates</TabsTrigger>
          <TabsTrigger value="revaluations">Revaluations</TabsTrigger>
          <TabsTrigger value="converter">Converter</TabsTrigger>
        </TabsList>

        <TabsContent value="currencies" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {(currencies.length ? currencies : [
              { id: '1', code: 'INR', name: 'Indian Rupee', symbol: '₹', exchange_rate: 1, is_base: true, is_active: true, last_updated: '2026-01-15' },
              { id: '2', code: 'USD', name: 'US Dollar', symbol: '$', exchange_rate: 83.12, is_base: false, is_active: true, last_updated: '2026-01-15' },
              { id: '3', code: 'EUR', name: 'Euro', symbol: '€', exchange_rate: 90.45, is_base: false, is_active: true, last_updated: '2026-01-15' },
              { id: '4', code: 'GBP', name: 'British Pound', symbol: '£', exchange_rate: 105.23, is_base: false, is_active: true, last_updated: '2026-01-15' },
              { id: '5', code: 'AED', name: 'UAE Dirham', symbol: 'د.إ', exchange_rate: 22.63, is_base: false, is_active: true, last_updated: '2026-01-15' },
              { id: '6', code: 'SGD', name: 'Singapore Dollar', symbol: 'S$', exchange_rate: 61.85, is_base: false, is_active: true, last_updated: '2026-01-15' },
            ]).map((currency) => (
              <Card key={currency.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold">{currency.symbol}</span>
                      <CardTitle className="text-base">{currency.code}</CardTitle>
                    </div>
                    {currency.is_base ? (
                      <Badge className="bg-purple-100 text-purple-800">Base</Badge>
                    ) : (
                      <Badge className={currency.is_active ? statusColors.active : statusColors.inactive}>
                        {currency.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    )}
                  </div>
                  <CardDescription>{currency.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Rate (to INR)</span>
                      <span className="font-medium">{currency.exchange_rate.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Updated</span>
                      <span>{currency.last_updated}</span>
                    </div>
                    {!currency.is_base && !currency.is_active && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full mt-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => handleDeleteClick(currency)}
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="exchange-rates" className="mt-4">
          <div className="flex justify-between mb-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search rates..." className="pl-9" />
            </div>
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Update Rates
            </Button>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">From</th>
                  <th className="text-left p-4 font-medium">To</th>
                  <th className="text-right p-4 font-medium">Rate</th>
                  <th className="text-left p-4 font-medium">Type</th>
                  <th className="text-left p-4 font-medium">Effective Date</th>
                  <th className="text-left p-4 font-medium">Source</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(rates.length ? rates : [
                  { id: '1', from_currency: 'USD', to_currency: 'INR', rate: 83.12, rate_type: 'spot', effective_date: '2026-01-15', source: 'RBI' },
                  { id: '2', from_currency: 'EUR', to_currency: 'INR', rate: 90.45, rate_type: 'spot', effective_date: '2026-01-15', source: 'RBI' },
                  { id: '3', from_currency: 'GBP', to_currency: 'INR', rate: 105.23, rate_type: 'spot', effective_date: '2026-01-15', source: 'RBI' },
                  { id: '4', from_currency: 'USD', to_currency: 'INR', rate: 83.50, rate_type: 'budget', effective_date: '2026-01-01', source: 'Manual' },
                ]).map((rate) => (
                  <tr key={rate.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{rate.from_currency}</td>
                    <td className="p-4">{rate.to_currency}</td>
                    <td className="p-4 text-right font-mono">{rate.rate.toFixed(4)}</td>
                    <td className="p-4">
                      <Badge variant="outline">{rate.rate_type}</Badge>
                    </td>
                    <td className="p-4 text-muted-foreground">{rate.effective_date}</td>
                    <td className="p-4">{rate.source}</td>
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
        </TabsContent>

        <TabsContent value="revaluations" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Reference</th>
                  <th className="text-left p-4 font-medium">Date</th>
                  <th className="text-left p-4 font-medium">Currency</th>
                  <th className="text-right p-4 font-medium">Accounts</th>
                  <th className="text-right p-4 font-medium">Gain/Loss</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(revaluations.length ? revaluations : [
                  { id: '1', reference_number: 'REVAL-2026-001', revaluation_date: '2026-01-15', currency: 'USD', accounts_affected: 12, gain_loss: 45000, status: 'posted' },
                  { id: '2', reference_number: 'REVAL-2026-002', revaluation_date: '2026-01-15', currency: 'EUR', accounts_affected: 8, gain_loss: -12500, status: 'draft' },
                  { id: '3', reference_number: 'REVAL-2025-012', revaluation_date: '2025-12-31', currency: 'GBP', accounts_affected: 5, gain_loss: 28000, status: 'posted' },
                ]).map((reval) => (
                  <tr key={reval.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{reval.reference_number}</td>
                    <td className="p-4 text-muted-foreground">{reval.revaluation_date}</td>
                    <td className="p-4">{reval.currency}</td>
                    <td className="p-4 text-right">{reval.accounts_affected}</td>
                    <td className="p-4 text-right">
                      <span className={reval.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {reval.gain_loss >= 0 ? '+' : ''}₹{reval.gain_loss.toLocaleString()}
                      </span>
                    </td>
                    <td className="p-4">
                      <Badge className={statusColors[reval.status]}>
                        {reval.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      {reval.status === 'draft' ? (
                        <Button size="sm">Post</Button>
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
              <Calculator className="h-4 w-4 mr-2" />
              Run Revaluation
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="converter" className="mt-4">
          <Card className="max-w-md">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ArrowRightLeft className="h-5 w-5" />
                Currency Converter
              </CardTitle>
              <CardDescription>Convert amounts between currencies</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Amount</label>
                  <Input type="number" placeholder="Enter amount" className="mt-1" defaultValue="1000" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">From</label>
                    <select className="w-full mt-1 p-2 border rounded-md">
                      <option>USD</option>
                      <option>EUR</option>
                      <option>GBP</option>
                      <option>INR</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">To</label>
                    <select className="w-full mt-1 p-2 border rounded-md">
                      <option>INR</option>
                      <option>USD</option>
                      <option>EUR</option>
                      <option>GBP</option>
                    </select>
                  </div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground">Converted Amount</p>
                  <p className="text-2xl font-bold">₹83,120.00</p>
                  <p className="text-xs text-muted-foreground mt-1">Rate: 1 USD = 83.12 INR</p>
                </div>
                <Button className="w-full">Convert</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Currency
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{currencyToDelete?.code} - {currencyToDelete?.name}</strong>?
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
