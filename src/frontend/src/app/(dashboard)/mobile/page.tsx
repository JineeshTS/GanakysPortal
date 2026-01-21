'use client';

import { useState, useEffect } from 'react';
import { Plus, Search, Smartphone, Bell, RefreshCw, Shield, CheckCircle, XCircle, Clock, MoreVertical, Loader2, Tablet, Wifi, WifiOff, Trash2, AlertTriangle } from 'lucide-react';
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

interface MobileDevice {
  id: string;
  device_name: string;
  device_type: string;
  platform: string;
  user_name: string;
  status: string;
  last_active: string;
  app_version: string;
}

interface PushNotification {
  id: string;
  title: string;
  notification_type: string;
  target_type: string;
  sent_count: number;
  delivered_count: number;
  status: string;
  sent_at: string;
}

interface OfflineAction {
  id: string;
  user_name: string;
  action_type: string;
  entity_type: string;
  status: string;
  created_at: string;
  synced_at: string | null;
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  online: 'bg-green-100 text-green-800',
  offline: 'bg-gray-100 text-gray-800',
  blocked: 'bg-red-100 text-red-800',
  sent: 'bg-blue-100 text-blue-800',
  delivered: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  pending: 'bg-yellow-100 text-yellow-800',
  synced: 'bg-green-100 text-green-800',
  conflict: 'bg-red-100 text-red-800',
};

const platformIcons: Record<string, React.ReactNode> = {
  ios: <Smartphone className="h-4 w-4" />,
  android: <Smartphone className="h-4 w-4" />,
  tablet: <Tablet className="h-4 w-4" />,
};

export default function MobilePage() {
  const [activeTab, setActiveTab] = useState('devices');
  const { showToast } = useToast();
  const deleteApi = useApi();
  const { data: devicesData, isLoading: devicesLoading, get: getDevices } = useApi<{ data: MobileDevice[] }>();
  const { data: notificationsData, isLoading: notificationsLoading, get: getNotifications } = useApi<{ data: PushNotification[] }>();
  const { data: offlineData, isLoading: offlineLoading, get: getOfflineActions } = useApi<{ data: OfflineAction[] }>();

  // Local state for data management
  const [localDevices, setLocalDevices] = useState<MobileDevice[]>([]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deviceToDelete, setDeviceToDelete] = useState<MobileDevice | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    getDevices('/mobile/devices');
    getNotifications('/mobile/notifications');
    getOfflineActions('/mobile/offline/actions');
  }, [getDevices, getNotifications, getOfflineActions]);

  useEffect(() => {
    if (devicesData?.data) {
      setLocalDevices(devicesData.data);
    }
  }, [devicesData]);

  const handleDeleteClick = (device: MobileDevice) => {
    setDeviceToDelete(device);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deviceToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/mobile/devices/${deviceToDelete.id}`);
      setLocalDevices(localDevices.filter(d => d.id !== deviceToDelete.id));
      setDeleteDialogOpen(false);
      setDeviceToDelete(null);
      showToast("success", "Device deleted successfully");
    } catch (error) {
      console.error("Failed to delete device:", error);
      showToast("error", "Failed to delete device");
    } finally {
      setIsDeleting(false);
    }
  };

  const devices = localDevices.length ? localDevices : devicesData?.data || [];
  const notifications = notificationsData?.data || [];
  const offlineActions = offlineData?.data || [];
  const isLoading = devicesLoading || notificationsLoading || offlineLoading;

  const stats = {
    registeredDevices: devices.length || 156,
    activeDevices: devices.filter(d => d.status === 'online').length || 89,
    notificationsSent: 1250,
    pendingSync: offlineActions.filter(a => a.status === 'pending').length || 12,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mobile App Management"
        description="Manage mobile devices, push notifications, and offline synchronization"
        actions={
          <Button>
            <Bell className="h-4 w-4 mr-2" />
            Send Notification
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading mobile data...</span>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Registered Devices"
          value={stats.registeredDevices}
          icon={Smartphone}
          description="Total enrolled"
        />
        <StatCard
          title="Active Now"
          value={stats.activeDevices}
          icon={Wifi}
          description="Currently online"
        />
        <StatCard
          title="Notifications Sent"
          value={stats.notificationsSent}
          icon={Bell}
          description="This month"
        />
        <StatCard
          title="Pending Sync"
          value={stats.pendingSync}
          icon={RefreshCw}
          description="Offline actions"
          className={stats.pendingSync > 0 ? "border-yellow-200 bg-yellow-50" : ""}
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="devices">Devices</TabsTrigger>
          <TabsTrigger value="notifications">Push Notifications</TabsTrigger>
          <TabsTrigger value="offline">Offline Sync</TabsTrigger>
          <TabsTrigger value="settings">App Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="devices" className="mt-4">
          <div className="flex gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search devices..."
                className="pl-9"
              />
            </div>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Device</th>
                  <th className="text-left p-4 font-medium">User</th>
                  <th className="text-left p-4 font-medium">Platform</th>
                  <th className="text-left p-4 font-medium">App Version</th>
                  <th className="text-left p-4 font-medium">Last Active</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(devices.length ? devices : [
                  { id: '1', device_name: 'iPhone 14 Pro', device_type: 'phone', platform: 'ios', user_name: 'Rahul Sharma', status: 'online', last_active: '2026-01-15 10:45', app_version: '2.5.0' },
                  { id: '2', device_name: 'Samsung Galaxy S23', device_type: 'phone', platform: 'android', user_name: 'Priya Patel', status: 'online', last_active: '2026-01-15 10:30', app_version: '2.5.0' },
                  { id: '3', device_name: 'iPad Pro', device_type: 'tablet', platform: 'ios', user_name: 'Amit Kumar', status: 'offline', last_active: '2026-01-14 18:00', app_version: '2.4.2' },
                  { id: '4', device_name: 'OnePlus 11', device_type: 'phone', platform: 'android', user_name: 'Neha Singh', status: 'blocked', last_active: '2026-01-10 12:00', app_version: '2.3.0' },
                ]).map((device) => (
                  <tr key={device.id} className="border-t hover:bg-muted/30">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {platformIcons[device.platform] || <Smartphone className="h-4 w-4" />}
                        <span className="font-medium">{device.device_name}</span>
                      </div>
                    </td>
                    <td className="p-4">{device.user_name}</td>
                    <td className="p-4">
                      <Badge variant="outline">{device.platform}</Badge>
                    </td>
                    <td className="p-4 text-muted-foreground">{device.app_version}</td>
                    <td className="p-4 text-muted-foreground text-sm">{device.last_active}</td>
                    <td className="p-4">
                      <Badge className={statusColors[device.status]}>
                        {device.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                        {device.status === 'blocked' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick(device)}
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

        <TabsContent value="notifications" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Title</th>
                  <th className="text-left p-4 font-medium">Type</th>
                  <th className="text-left p-4 font-medium">Target</th>
                  <th className="text-right p-4 font-medium">Sent</th>
                  <th className="text-right p-4 font-medium">Delivered</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Sent At</th>
                </tr>
              </thead>
              <tbody>
                {(notifications.length ? notifications : [
                  { id: '1', title: 'New Leave Request', notification_type: 'workflow', target_type: 'user', sent_count: 1, delivered_count: 1, status: 'delivered', sent_at: '2026-01-15 10:30' },
                  { id: '2', title: 'Monthly Report Available', notification_type: 'report', target_type: 'all', sent_count: 156, delivered_count: 142, status: 'delivered', sent_at: '2026-01-15 09:00' },
                  { id: '3', title: 'System Maintenance', notification_type: 'system', target_type: 'all', sent_count: 156, delivered_count: 0, status: 'pending', sent_at: '2026-01-15 11:00' },
                ]).map((notification) => (
                  <tr key={notification.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{notification.title}</td>
                    <td className="p-4">
                      <Badge variant="outline">{notification.notification_type}</Badge>
                    </td>
                    <td className="p-4">{notification.target_type}</td>
                    <td className="p-4 text-right">{notification.sent_count}</td>
                    <td className="p-4 text-right text-green-600">{notification.delivered_count}</td>
                    <td className="p-4">
                      <Badge className={statusColors[notification.status]}>
                        {notification.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-muted-foreground text-sm">{notification.sent_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="offline" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">User</th>
                  <th className="text-left p-4 font-medium">Action</th>
                  <th className="text-left p-4 font-medium">Entity</th>
                  <th className="text-left p-4 font-medium">Created</th>
                  <th className="text-left p-4 font-medium">Synced</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(offlineActions.length ? offlineActions : [
                  { id: '1', user_name: 'Rahul Sharma', action_type: 'create', entity_type: 'attendance', status: 'synced', created_at: '2026-01-15 08:00', synced_at: '2026-01-15 10:30' },
                  { id: '2', user_name: 'Priya Patel', action_type: 'update', entity_type: 'timesheet', status: 'pending', created_at: '2026-01-15 09:00', synced_at: null },
                  { id: '3', user_name: 'Amit Kumar', action_type: 'create', entity_type: 'expense', status: 'conflict', created_at: '2026-01-14 17:00', synced_at: null },
                ]).map((action) => (
                  <tr key={action.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{action.user_name}</td>
                    <td className="p-4">
                      <Badge variant="outline">{action.action_type}</Badge>
                    </td>
                    <td className="p-4">{action.entity_type}</td>
                    <td className="p-4 text-muted-foreground text-sm">{action.created_at}</td>
                    <td className="p-4 text-muted-foreground text-sm">{action.synced_at || '-'}</td>
                    <td className="p-4">
                      <Badge className={statusColors[action.status]}>
                        {action.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      {action.status === 'conflict' && (
                        <Button size="sm" variant="outline">Resolve</Button>
                      )}
                      {action.status === 'pending' && (
                        <Button size="sm" variant="outline">
                          <RefreshCw className="h-3 w-3 mr-1" />
                          Sync
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                App Configuration
              </CardTitle>
              <CardDescription>Configure mobile app settings and security policies</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { name: 'Minimum App Version', value: '2.4.0', description: 'Users below this version will be forced to update' },
                  { name: 'Session Timeout', value: '30 minutes', description: 'Auto-logout after inactivity' },
                  { name: 'Offline Mode', value: 'Enabled', description: 'Allow offline data access' },
                  { name: 'Biometric Auth', value: 'Optional', description: 'Fingerprint/Face ID login' },
                ].map((setting, i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">{setting.name}</p>
                      <p className="text-sm text-muted-foreground">{setting.description}</p>
                    </div>
                    <Badge variant="secondary">{setting.value}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Device Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Device
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{deviceToDelete?.device_name}</strong>?
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
