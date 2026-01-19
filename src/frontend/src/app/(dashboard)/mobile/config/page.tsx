'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  ChevronLeft,
  RefreshCw,
  Save,
  Loader2,
  Settings,
  Bell,
  Shield,
  Wifi,
  Database,
  Palette,
  Clock,
  MapPin,
  Camera,
  Fingerprint,
  Lock,
  Smartphone,
  Globe,
  Battery,
  Download,
} from 'lucide-react'

interface AppConfig {
  id: string
  key: string
  value: string
  category: string
  description: string
  type: 'boolean' | 'number' | 'string' | 'select'
  options?: string[]
  updated_at: string
}

export default function MobileConfigPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [configs, setConfigs] = useState<AppConfig[]>([])
  const [hasChanges, setHasChanges] = useState(false)

  // Local state for all settings
  const [settings, setSettings] = useState({
    // General
    app_name: 'GanaPortal Mobile',
    default_language: 'en',
    session_timeout_minutes: 30,
    force_update_version: '1.0.0',
    maintenance_mode: false,

    // Sync
    auto_sync_enabled: true,
    sync_interval_minutes: 15,
    sync_on_wifi_only: false,
    max_offline_days: 7,
    sync_attachments: true,
    max_attachment_size_mb: 10,

    // Security
    require_biometric: false,
    require_pin: true,
    pin_length: 4,
    max_login_attempts: 5,
    lockout_duration_minutes: 15,
    allow_screenshot: true,
    encrypt_local_data: true,

    // Notifications
    push_enabled: true,
    sound_enabled: true,
    vibrate_enabled: true,
    quiet_hours_start: '22:00',
    quiet_hours_end: '07:00',
    badge_count_enabled: true,

    // Location
    location_tracking: true,
    location_accuracy: 'high',
    geofence_enabled: true,
    geofence_radius_meters: 100,

    // Camera & Media
    camera_enabled: true,
    photo_quality: 'high',
    max_photos_per_upload: 5,
    allow_gallery_access: true,

    // Data & Storage
    cache_size_mb: 100,
    auto_clear_cache: true,
    keep_login_sessions: true,
    data_compression: true,
  })

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const fetchConfigs = useCallback(async () => {
    setIsLoading(true)
    try {
      const res = await fetchWithAuth(`${apiUrl}/mobile/config`)
      if (res.ok) {
        const data = await res.json()
        setConfigs(data.data || [])
      }
    } catch (err) {
      console.error('Failed to fetch configs:', err)
    } finally {
      setIsLoading(false)
    }
  }, [apiUrl])

  useEffect(() => {
    fetchConfigs()
  }, [fetchConfigs])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const res = await fetchWithAuth(`${apiUrl}/mobile/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      })
      if (res.ok) {
        setHasChanges(false)
      }
    } catch (err) {
      console.error('Failed to save config:', err)
    } finally {
      setIsSaving(false)
    }
  }

  const updateSetting = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="App Configuration"
        description="Configure mobile application settings and policies"
        actions={
          <div className="flex gap-2">
            <Link href="/mobile">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <Button onClick={handleSave} disabled={isSaving || !hasChanges}>
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        }
      />

      {hasChanges && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="py-3 flex items-center gap-2">
            <Settings className="h-4 w-4 text-yellow-600" />
            <span className="text-sm text-yellow-800">You have unsaved changes</span>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading configuration...</span>
        </Card>
      ) : (
        <Tabs defaultValue="general" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="sync">Sync</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="location">Location</TabsTrigger>
            <TabsTrigger value="storage">Storage</TabsTrigger>
          </TabsList>

          {/* General Settings */}
          <TabsContent value="general">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Smartphone className="h-5 w-5" />
                  General Settings
                </CardTitle>
                <CardDescription>Basic app configuration and behavior</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>App Name</Label>
                    <Input
                      value={settings.app_name}
                      onChange={(e) => updateSetting('app_name', e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label>Default Language</Label>
                    <Select
                      value={settings.default_language}
                      onValueChange={(v) => updateSetting('default_language', v)}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="hi">Hindi</SelectItem>
                        <SelectItem value="ta">Tamil</SelectItem>
                        <SelectItem value="te">Telugu</SelectItem>
                        <SelectItem value="mr">Marathi</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>Session Timeout (minutes)</Label>
                    <div className="flex items-center gap-4 mt-1">
                      <Slider
                        value={[settings.session_timeout_minutes]}
                        min={5}
                        max={120}
                        step={5}
                        onValueChange={([v]) => updateSetting('session_timeout_minutes', v)}
                        className="flex-1"
                      />
                      <span className="text-sm font-medium w-12">{settings.session_timeout_minutes}m</span>
                    </div>
                  </div>
                  <div>
                    <Label>Force Update Version</Label>
                    <Input
                      value={settings.force_update_version}
                      onChange={(e) => updateSetting('force_update_version', e.target.value)}
                      className="mt-1"
                      placeholder="e.g., 1.2.0"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <Settings className="h-5 w-5 text-red-500" />
                    <div>
                      <p className="font-medium">Maintenance Mode</p>
                      <p className="text-sm text-muted-foreground">Disable app access for all users</p>
                    </div>
                  </div>
                  <Switch
                    checked={settings.maintenance_mode}
                    onCheckedChange={(v) => updateSetting('maintenance_mode', v)}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Sync Settings */}
          <TabsContent value="sync">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wifi className="h-5 w-5" />
                  Sync Settings
                </CardTitle>
                <CardDescription>Configure data synchronization behavior</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <RefreshCw className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Auto Sync</p>
                      <p className="text-sm text-muted-foreground">Automatically sync data in background</p>
                    </div>
                  </div>
                  <Switch
                    checked={settings.auto_sync_enabled}
                    onCheckedChange={(v) => updateSetting('auto_sync_enabled', v)}
                  />
                </div>

                <div>
                  <Label>Sync Interval (minutes)</Label>
                  <div className="flex items-center gap-4 mt-1">
                    <Slider
                      value={[settings.sync_interval_minutes]}
                      min={5}
                      max={60}
                      step={5}
                      onValueChange={([v]) => updateSetting('sync_interval_minutes', v)}
                      className="flex-1"
                    />
                    <span className="text-sm font-medium w-12">{settings.sync_interval_minutes}m</span>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">WiFi Only Sync</p>
                      <p className="text-sm text-muted-foreground">Only sync on WiFi</p>
                    </div>
                    <Switch
                      checked={settings.sync_on_wifi_only}
                      onCheckedChange={(v) => updateSetting('sync_on_wifi_only', v)}
                    />
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">Sync Attachments</p>
                      <p className="text-sm text-muted-foreground">Include files in sync</p>
                    </div>
                    <Switch
                      checked={settings.sync_attachments}
                      onCheckedChange={(v) => updateSetting('sync_attachments', v)}
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>Max Offline Days</Label>
                    <Input
                      type="number"
                      value={settings.max_offline_days}
                      onChange={(e) => updateSetting('max_offline_days', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label>Max Attachment Size (MB)</Label>
                    <Input
                      type="number"
                      value={settings.max_attachment_size_mb}
                      onChange={(e) => updateSetting('max_attachment_size_mb', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Settings */}
          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Security Settings
                </CardTitle>
                <CardDescription>Configure authentication and data protection</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                      <Fingerprint className="h-5 w-5 text-primary" />
                      <div>
                        <p className="font-medium">Biometric Auth</p>
                        <p className="text-sm text-muted-foreground">Face ID / Fingerprint</p>
                      </div>
                    </div>
                    <Switch
                      checked={settings.require_biometric}
                      onCheckedChange={(v) => updateSetting('require_biometric', v)}
                    />
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div className="flex items-center gap-3">
                      <Lock className="h-5 w-5 text-primary" />
                      <div>
                        <p className="font-medium">Require PIN</p>
                        <p className="text-sm text-muted-foreground">PIN on app launch</p>
                      </div>
                    </div>
                    <Switch
                      checked={settings.require_pin}
                      onCheckedChange={(v) => updateSetting('require_pin', v)}
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <Label>PIN Length</Label>
                    <Select
                      value={settings.pin_length.toString()}
                      onValueChange={(v) => updateSetting('pin_length', parseInt(v))}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="4">4 digits</SelectItem>
                        <SelectItem value="6">6 digits</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Max Login Attempts</Label>
                    <Input
                      type="number"
                      value={settings.max_login_attempts}
                      onChange={(e) => updateSetting('max_login_attempts', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label>Lockout Duration (min)</Label>
                    <Input
                      type="number"
                      value={settings.lockout_duration_minutes}
                      onChange={(e) => updateSetting('lockout_duration_minutes', parseInt(e.target.value))}
                      className="mt-1"
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">Allow Screenshots</p>
                      <p className="text-sm text-muted-foreground">Enable screen capture</p>
                    </div>
                    <Switch
                      checked={settings.allow_screenshot}
                      onCheckedChange={(v) => updateSetting('allow_screenshot', v)}
                    />
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">Encrypt Local Data</p>
                      <p className="text-sm text-muted-foreground">AES-256 encryption</p>
                    </div>
                    <Switch
                      checked={settings.encrypt_local_data}
                      onCheckedChange={(v) => updateSetting('encrypt_local_data', v)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notification Settings */}
          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Notification Settings
                </CardTitle>
                <CardDescription>Configure push notifications behavior</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <Bell className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Push Notifications</p>
                      <p className="text-sm text-muted-foreground">Enable push notifications</p>
                    </div>
                  </div>
                  <Switch
                    checked={settings.push_enabled}
                    onCheckedChange={(v) => updateSetting('push_enabled', v)}
                  />
                </div>

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">Sound</p>
                      <p className="text-sm text-muted-foreground">Play sounds</p>
                    </div>
                    <Switch
                      checked={settings.sound_enabled}
                      onCheckedChange={(v) => updateSetting('sound_enabled', v)}
                    />
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">Vibrate</p>
                      <p className="text-sm text-muted-foreground">Vibration alerts</p>
                    </div>
                    <Switch
                      checked={settings.vibrate_enabled}
                      onCheckedChange={(v) => updateSetting('vibrate_enabled', v)}
                    />
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">Badge Count</p>
                      <p className="text-sm text-muted-foreground">Show count on icon</p>
                    </div>
                    <Switch
                      checked={settings.badge_count_enabled}
                      onCheckedChange={(v) => updateSetting('badge_count_enabled', v)}
                    />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>Quiet Hours Start</Label>
                    <Input
                      type="time"
                      value={settings.quiet_hours_start}
                      onChange={(e) => updateSetting('quiet_hours_start', e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label>Quiet Hours End</Label>
                    <Input
                      type="time"
                      value={settings.quiet_hours_end}
                      onChange={(e) => updateSetting('quiet_hours_end', e.target.value)}
                      className="mt-1"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Location Settings */}
          <TabsContent value="location">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Location Settings
                </CardTitle>
                <CardDescription>Configure location tracking and geofencing</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <MapPin className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Location Tracking</p>
                      <p className="text-sm text-muted-foreground">Track user location for attendance</p>
                    </div>
                  </div>
                  <Switch
                    checked={settings.location_tracking}
                    onCheckedChange={(v) => updateSetting('location_tracking', v)}
                  />
                </div>

                <div>
                  <Label>Location Accuracy</Label>
                  <Select
                    value={settings.location_accuracy}
                    onValueChange={(v) => updateSetting('location_accuracy', v)}
                  >
                    <SelectTrigger className="mt-1 w-48">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low (Battery Saver)</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High (GPS)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <Globe className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Geofencing</p>
                      <p className="text-sm text-muted-foreground">Trigger actions based on location</p>
                    </div>
                  </div>
                  <Switch
                    checked={settings.geofence_enabled}
                    onCheckedChange={(v) => updateSetting('geofence_enabled', v)}
                  />
                </div>

                <div>
                  <Label>Geofence Radius (meters)</Label>
                  <div className="flex items-center gap-4 mt-1">
                    <Slider
                      value={[settings.geofence_radius_meters]}
                      min={50}
                      max={500}
                      step={25}
                      onValueChange={([v]) => updateSetting('geofence_radius_meters', v)}
                      className="flex-1"
                    />
                    <span className="text-sm font-medium w-16">{settings.geofence_radius_meters}m</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Storage Settings */}
          <TabsContent value="storage">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Storage Settings
                </CardTitle>
                <CardDescription>Configure local data storage and caching</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label>Cache Size Limit (MB)</Label>
                  <div className="flex items-center gap-4 mt-1">
                    <Slider
                      value={[settings.cache_size_mb]}
                      min={50}
                      max={500}
                      step={50}
                      onValueChange={([v]) => updateSetting('cache_size_mb', v)}
                      className="flex-1"
                    />
                    <span className="text-sm font-medium w-16">{settings.cache_size_mb} MB</span>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">Auto Clear Cache</p>
                      <p className="text-sm text-muted-foreground">Clear old cached data</p>
                    </div>
                    <Switch
                      checked={settings.auto_clear_cache}
                      onCheckedChange={(v) => updateSetting('auto_clear_cache', v)}
                    />
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-lg border">
                    <div>
                      <p className="font-medium">Keep Login Sessions</p>
                      <p className="text-sm text-muted-foreground">Remember login state</p>
                    </div>
                    <Switch
                      checked={settings.keep_login_sessions}
                      onCheckedChange={(v) => updateSetting('keep_login_sessions', v)}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg border">
                  <div className="flex items-center gap-3">
                    <Download className="h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">Data Compression</p>
                      <p className="text-sm text-muted-foreground">Compress data to save storage</p>
                    </div>
                  </div>
                  <Switch
                    checked={settings.data_compression}
                    onCheckedChange={(v) => updateSetting('data_compression', v)}
                  />
                </div>

                <div className="p-4 rounded-lg border bg-muted/50">
                  <div className="flex items-center gap-2 mb-2">
                    <Camera className="h-4 w-4" />
                    <span className="font-medium">Camera & Media</span>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2 mt-3">
                    <div>
                      <Label>Photo Quality</Label>
                      <Select
                        value={settings.photo_quality}
                        onValueChange={(v) => updateSetting('photo_quality', v)}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low (Faster Upload)</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High Quality</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Max Photos per Upload</Label>
                      <Input
                        type="number"
                        value={settings.max_photos_per_upload}
                        onChange={(e) => updateSetting('max_photos_per_upload', parseInt(e.target.value))}
                        className="mt-1"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
