'use client';

import { useState, useEffect } from 'react';
import { Plus, Search, Link2, Webhook, RefreshCw, Database, CheckCircle, XCircle, Clock, MoreVertical, Loader2, Settings, Activity, Trash2, AlertTriangle } from 'lucide-react';
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
import { useApi, useToast } from '@/hooks';

interface Connector {
  id: string;
  name: string;
  connector_type: string;
  provider: string;
  status: string;
  last_sync: string | null;
  sync_frequency: string;
}

interface WebhookConfig {
  id: string;
  name: string;
  url: string;
  event_type: string;
  status: string;
  last_triggered: string | null;
  success_count: number;
  failure_count: number;
}

interface SyncJob {
  id: string;
  connector_name: string;
  direction: string;
  status: string;
  records_processed: number;
  records_failed: number;
  started_at: string;
  completed_at: string | null;
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  connected: 'bg-green-100 text-green-800',
  disconnected: 'bg-red-100 text-red-800',
  running: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800',
};

const providerIcons: Record<string, string> = {
  salesforce: '☁️',
  quickbooks: '📊',
  zoho: '📈',
  tally: '💼',
  sap: '🏢',
  custom: '🔧',
};

export default function IntegrationPage() {
  const [activeTab, setActiveTab] = useState('connectors');
  const { showToast } = useToast();
  const deleteApi = useApi();
  const { data: connectorsData, isLoading: connectorsLoading, get: getConnectors } = useApi<{ data: Connector[] }>();
  const { data: webhooksData, isLoading: webhooksLoading, get: getWebhooks } = useApi<{ data: WebhookConfig[] }>();
  const { data: syncJobsData, isLoading: syncJobsLoading, get: getSyncJobs } = useApi<{ data: SyncJob[] }>();

  // Local state for data management
  const [localConnectors, setLocalConnectors] = useState<Connector[]>([]);
  const [localWebhooks, setLocalWebhooks] = useState<WebhookConfig[]>([]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<{ type: string; item: Connector | WebhookConfig } | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    getConnectors('/integration/connectors');
    getWebhooks('/integration/webhooks');
    getSyncJobs('/integration/sync/jobs');
  }, [getConnectors, getWebhooks, getSyncJobs]);

  useEffect(() => {
    if (connectorsData?.data) {
      setLocalConnectors(connectorsData.data);
    }
  }, [connectorsData]);

  useEffect(() => {
    if (webhooksData?.data) {
      setLocalWebhooks(webhooksData.data);
    }
  }, [webhooksData]);

  const handleDeleteClick = (type: string, item: Connector | WebhookConfig) => {
    setItemToDelete({ type, item });
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      const endpoint = itemToDelete.type === "connector"
        ? `/integration/connectors/${itemToDelete.item.id}`
        : `/integration/webhooks/${itemToDelete.item.id}`;

      await deleteApi.delete(endpoint);

      if (itemToDelete.type === "connector") {
        setLocalConnectors(localConnectors.filter(c => c.id !== itemToDelete.item.id));
      } else {
        setLocalWebhooks(localWebhooks.filter(w => w.id !== itemToDelete.item.id));
      }

      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast("success", `${itemToDelete.type === "connector" ? "Connector" : "Webhook"} deleted successfully`);
    } catch (error) {
      showToast("error", `Failed to delete ${itemToDelete.type}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const connectors = localConnectors.length ? localConnectors : connectorsData?.data || [];
  const webhooks = localWebhooks.length ? localWebhooks : webhooksData?.data || [];
  const syncJobs = syncJobsData?.data || [];
  const isLoading = connectorsLoading || webhooksLoading || syncJobsLoading;

  const stats = {
    activeConnectors: connectors.filter(c => c.status === 'connected').length || 5,
    activeWebhooks: webhooks.filter(w => w.status === 'active').length || 12,
    syncJobsToday: syncJobs.length || 45,
    failedSyncs: syncJobs.filter(s => s.status === 'failed').length || 2,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Integration Platform"
        description="Connect external systems, configure webhooks, and manage data synchronization"
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Connector
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading integration data...</span>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Active Connectors"
          value={stats.activeConnectors}
          icon={Link2}
          description="Connected systems"
        />
        <StatCard
          title="Active Webhooks"
          value={stats.activeWebhooks}
          icon={Webhook}
          description="Event listeners"
        />
        <StatCard
          title="Sync Jobs Today"
          value={stats.syncJobsToday}
          icon={RefreshCw}
          description="Data synchronizations"
        />
        <StatCard
          title="Failed Syncs"
          value={stats.failedSyncs}
          icon={XCircle}
          description="Requires attention"
          className={stats.failedSyncs > 0 ? "border-red-200 bg-red-50" : ""}
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="connectors">Connectors</TabsTrigger>
          <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
          <TabsTrigger value="sync-jobs">Sync Jobs</TabsTrigger>
          <TabsTrigger value="mappings">Data Mappings</TabsTrigger>
        </TabsList>

        <TabsContent value="connectors" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(connectors.length ? connectors : [
              { id: '1', name: 'Salesforce CRM', connector_type: 'crm', provider: 'salesforce', status: 'connected', last_sync: '2026-01-15 10:30', sync_frequency: 'every_hour' },
              { id: '2', name: 'QuickBooks Online', connector_type: 'accounting', provider: 'quickbooks', status: 'connected', last_sync: '2026-01-15 09:00', sync_frequency: 'daily' },
              { id: '3', name: 'Zoho Inventory', connector_type: 'inventory', provider: 'zoho', status: 'connected', last_sync: '2026-01-15 08:00', sync_frequency: 'every_6_hours' },
              { id: '4', name: 'Tally ERP', connector_type: 'accounting', provider: 'tally', status: 'disconnected', last_sync: '2026-01-10 12:00', sync_frequency: 'daily' },
            ]).map((connector) => (
              <Card key={connector.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{providerIcons[connector.provider] || '🔗'}</span>
                      <CardTitle className="text-base">{connector.name}</CardTitle>
                    </div>
                    <Badge className={statusColors[connector.status]}>
                      {connector.status}
                    </Badge>
                  </div>
                  <CardDescription>{connector.connector_type} • {connector.provider}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Last Sync</span>
                      <span>{connector.last_sync || 'Never'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Frequency</span>
                      <span>{connector.sync_frequency.replace('_', ' ')}</span>
                    </div>
                  </div>
                  <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <RefreshCw className="h-3 w-3 mr-1" />
                      Sync Now
                    </Button>
                    <Button size="sm" variant="ghost">
                      <Settings className="h-3 w-3" />
                    </Button>
                    {connector.status === 'disconnected' && (
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteClick('connector', connector);
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="webhooks" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Name</th>
                  <th className="text-left p-4 font-medium">Event Type</th>
                  <th className="text-left p-4 font-medium">URL</th>
                  <th className="text-center p-4 font-medium">Success</th>
                  <th className="text-center p-4 font-medium">Failed</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(webhooks.length ? webhooks : [
                  { id: '1', name: 'Order Created', event_type: 'order.created', url: 'https://api.example.com/webhooks/orders', status: 'active', last_triggered: '2026-01-15 10:45', success_count: 156, failure_count: 2 },
                  { id: '2', name: 'Invoice Paid', event_type: 'invoice.paid', url: 'https://api.example.com/webhooks/invoices', status: 'active', last_triggered: '2026-01-15 09:30', success_count: 89, failure_count: 0 },
                  { id: '3', name: 'Customer Updated', event_type: 'customer.updated', url: 'https://crm.example.com/hooks/customers', status: 'inactive', last_triggered: '2026-01-10 14:00', success_count: 45, failure_count: 5 },
                ]).map((webhook) => (
                  <tr key={webhook.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{webhook.name}</td>
                    <td className="p-4">
                      <Badge variant="outline">{webhook.event_type}</Badge>
                    </td>
                    <td className="p-4 text-muted-foreground text-sm truncate max-w-[200px]">{webhook.url}</td>
                    <td className="p-4 text-center text-green-600">{webhook.success_count}</td>
                    <td className="p-4 text-center text-red-600">{webhook.failure_count}</td>
                    <td className="p-4">
                      <Badge className={statusColors[webhook.status]}>
                        {webhook.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                        {webhook.status === 'inactive' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick('webhook', webhook)}
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

        <TabsContent value="sync-jobs" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Connector</th>
                  <th className="text-left p-4 font-medium">Direction</th>
                  <th className="text-right p-4 font-medium">Processed</th>
                  <th className="text-right p-4 font-medium">Failed</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Started</th>
                  <th className="text-left p-4 font-medium">Completed</th>
                </tr>
              </thead>
              <tbody>
                {(syncJobs.length ? syncJobs : [
                  { id: '1', connector_name: 'Salesforce CRM', direction: 'inbound', status: 'completed', records_processed: 150, records_failed: 0, started_at: '2026-01-15 10:30', completed_at: '2026-01-15 10:32' },
                  { id: '2', connector_name: 'QuickBooks Online', direction: 'outbound', status: 'running', records_processed: 45, records_failed: 0, started_at: '2026-01-15 10:45', completed_at: null },
                  { id: '3', connector_name: 'Zoho Inventory', direction: 'bidirectional', status: 'failed', records_processed: 89, records_failed: 3, started_at: '2026-01-15 08:00', completed_at: '2026-01-15 08:15' },
                ]).map((job) => (
                  <tr key={job.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{job.connector_name}</td>
                    <td className="p-4">
                      <Badge variant="outline">{job.direction}</Badge>
                    </td>
                    <td className="p-4 text-right">{job.records_processed}</td>
                    <td className="p-4 text-right text-red-600">{job.records_failed}</td>
                    <td className="p-4">
                      <Badge className={statusColors[job.status]}>
                        {job.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-muted-foreground text-sm">{job.started_at}</td>
                    <td className="p-4 text-muted-foreground text-sm">{job.completed_at || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="mappings" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Data Mappings
              </CardTitle>
              <CardDescription>Configure field mappings between systems</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {['Customer → Contact', 'Product → Item', 'Invoice → Bill', 'Order → Sales Order'].map((mapping, i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Activity className="h-4 w-4 text-primary" />
                      <span className="font-medium">{mapping}</span>
                    </div>
                    <Button variant="outline" size="sm">Configure</Button>
                  </div>
                ))}
              </div>
              <Button className="mt-4">
                <Plus className="h-4 w-4 mr-2" />
                Create Mapping
              </Button>
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
              Delete {itemToDelete?.type === 'connector' ? 'Connector' : 'Webhook'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{' '}
              <strong>{itemToDelete?.item.name}</strong>?
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
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
