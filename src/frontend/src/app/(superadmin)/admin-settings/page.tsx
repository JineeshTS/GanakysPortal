'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import {
  Settings,
  Shield,
  Mail,
  CreditCard,
  Database,
  Bell,
  Globe,
  Lock,
  Server,
  Save,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react'

// Mock platform settings data
const mockSettings = {
  general: {
    platformName: 'Ganakys Codilla Apps',
    supportEmail: 'support@ganakys.com',
    salesEmail: 'sales@ganakys.com',
    defaultTimezone: 'Asia/Kolkata',
    defaultCurrency: 'INR',
    maintenanceMode: false,
    maintenanceMessage: '',
  },
  security: {
    minPasswordLength: 8,
    requireMfa: false,
    mfaGracePeriodDays: 7,
    sessionTimeoutMinutes: 60,
    maxLoginAttempts: 5,
    lockoutDurationMinutes: 30,
    passwordExpiryDays: 90,
    enforcePasswordHistory: 5,
  },
  billing: {
    defaultCurrency: 'INR',
    taxRate: 18,
    trialDays: 14,
    gracePeriodDays: 7,
    autoSuspendOnOverdue: true,
    razorpayKeyId: 'rzp_test_xxxxx',
    razorpayKeySecret: '********',
    invoicePrefix: 'INV',
    invoiceStartNumber: 1001,
  },
  email: {
    provider: 'smtp',
    smtpHost: 'smtp.example.com',
    smtpPort: 587,
    smtpUser: 'notifications@ganakys.com',
    smtpPassword: '********',
    fromName: 'Ganakys Codilla Apps',
    fromEmail: 'no-reply@ganakys.com',
  },
  storage: {
    provider: 's3',
    bucketName: 'ganakys-uploads',
    region: 'ap-south-1',
    maxFileSizeMb: 50,
    allowedFileTypes: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'],
  },
  notifications: {
    enableEmailNotifications: true,
    enableSmsNotifications: false,
    enablePushNotifications: false,
    digestFrequency: 'daily',
    criticalAlertsImmediate: true,
  },
  limits: {
    defaultStorageGb: 10,
    defaultApiCallsPerMonth: 10000,
    defaultAiQueriesPerMonth: 500,
    maxUsersPerTenant: 500,
    maxEmployeesPerTenant: 5000,
  },
}

export default function SettingsPage() {
  const [settings, setSettings] = useState(mockSettings)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState('general')

  const handleSave = async () => {
    setSaving(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    setSaving(false)
  }

  const updateSetting = (category: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category as keyof typeof prev],
        [key]: value,
      },
    }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Platform Settings</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Configure global platform settings and defaults
          </p>
        </div>
        <Button onClick={handleSave} disabled={saving}>
          {saving ? (
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Save className="h-4 w-4 mr-2" />
          )}
          Save Changes
        </Button>
      </div>

      {/* Settings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-7 w-full">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            <span className="hidden lg:inline">General</span>
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            <span className="hidden lg:inline">Security</span>
          </TabsTrigger>
          <TabsTrigger value="billing" className="flex items-center gap-2">
            <CreditCard className="h-4 w-4" />
            <span className="hidden lg:inline">Billing</span>
          </TabsTrigger>
          <TabsTrigger value="email" className="flex items-center gap-2">
            <Mail className="h-4 w-4" />
            <span className="hidden lg:inline">Email</span>
          </TabsTrigger>
          <TabsTrigger value="storage" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            <span className="hidden lg:inline">Storage</span>
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            <span className="hidden lg:inline">Notifications</span>
          </TabsTrigger>
          <TabsTrigger value="limits" className="flex items-center gap-2">
            <Server className="h-4 w-4" />
            <span className="hidden lg:inline">Limits</span>
          </TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                General Settings
              </CardTitle>
              <CardDescription>
                Basic platform configuration and branding
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="platformName">Platform Name</Label>
                  <Input
                    id="platformName"
                    value={settings.general.platformName}
                    onChange={(e) => updateSetting('general', 'platformName', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="supportEmail">Support Email</Label>
                  <Input
                    id="supportEmail"
                    type="email"
                    value={settings.general.supportEmail}
                    onChange={(e) => updateSetting('general', 'supportEmail', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="salesEmail">Sales Email</Label>
                  <Input
                    id="salesEmail"
                    type="email"
                    value={settings.general.salesEmail}
                    onChange={(e) => updateSetting('general', 'salesEmail', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="defaultTimezone">Default Timezone</Label>
                  <Select
                    value={settings.general.defaultTimezone}
                    onValueChange={(value) => updateSetting('general', 'defaultTimezone', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Asia/Kolkata">Asia/Kolkata (IST)</SelectItem>
                      <SelectItem value="UTC">UTC</SelectItem>
                      <SelectItem value="America/New_York">America/New_York (EST)</SelectItem>
                      <SelectItem value="Europe/London">Europe/London (GMT)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="defaultCurrency">Default Currency</Label>
                  <Select
                    value={settings.general.defaultCurrency}
                    onValueChange={(value) => updateSetting('general', 'defaultCurrency', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="INR">INR - Indian Rupee</SelectItem>
                      <SelectItem value="USD">USD - US Dollar</SelectItem>
                      <SelectItem value="EUR">EUR - Euro</SelectItem>
                      <SelectItem value="GBP">GBP - British Pound</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="border-t pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                      Maintenance Mode
                    </h4>
                    <p className="text-sm text-gray-500">
                      Enable to show maintenance message to all users
                    </p>
                  </div>
                  <Switch
                    checked={settings.general.maintenanceMode}
                    onCheckedChange={(checked) => updateSetting('general', 'maintenanceMode', checked)}
                  />
                </div>
                {settings.general.maintenanceMode && (
                  <div className="mt-4 space-y-2">
                    <Label htmlFor="maintenanceMessage">Maintenance Message</Label>
                    <Textarea
                      id="maintenanceMessage"
                      placeholder="We are currently performing scheduled maintenance..."
                      value={settings.general.maintenanceMessage}
                      onChange={(e) => updateSetting('general', 'maintenanceMessage', e.target.value)}
                    />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Settings */}
        <TabsContent value="security" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5" />
                Security Settings
              </CardTitle>
              <CardDescription>
                Configure authentication and security policies
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="minPasswordLength">Minimum Password Length</Label>
                  <Input
                    id="minPasswordLength"
                    type="number"
                    min={6}
                    max={32}
                    value={settings.security.minPasswordLength}
                    onChange={(e) => updateSetting('security', 'minPasswordLength', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sessionTimeout">Session Timeout (minutes)</Label>
                  <Input
                    id="sessionTimeout"
                    type="number"
                    min={5}
                    max={1440}
                    value={settings.security.sessionTimeoutMinutes}
                    onChange={(e) => updateSetting('security', 'sessionTimeoutMinutes', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxLoginAttempts">Max Login Attempts</Label>
                  <Input
                    id="maxLoginAttempts"
                    type="number"
                    min={3}
                    max={10}
                    value={settings.security.maxLoginAttempts}
                    onChange={(e) => updateSetting('security', 'maxLoginAttempts', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lockoutDuration">Lockout Duration (minutes)</Label>
                  <Input
                    id="lockoutDuration"
                    type="number"
                    min={5}
                    max={60}
                    value={settings.security.lockoutDurationMinutes}
                    onChange={(e) => updateSetting('security', 'lockoutDurationMinutes', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="passwordExpiry">Password Expiry (days)</Label>
                  <Input
                    id="passwordExpiry"
                    type="number"
                    min={0}
                    max={365}
                    value={settings.security.passwordExpiryDays}
                    onChange={(e) => updateSetting('security', 'passwordExpiryDays', parseInt(e.target.value))}
                  />
                  <p className="text-xs text-gray-500">Set to 0 for no expiry</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="passwordHistory">Password History Count</Label>
                  <Input
                    id="passwordHistory"
                    type="number"
                    min={0}
                    max={24}
                    value={settings.security.enforcePasswordHistory}
                    onChange={(e) => updateSetting('security', 'enforcePasswordHistory', parseInt(e.target.value))}
                  />
                  <p className="text-xs text-gray-500">Prevent reuse of last N passwords</p>
                </div>
              </div>

              <div className="border-t pt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Require MFA for All Users</h4>
                    <p className="text-sm text-gray-500">
                      Enforce multi-factor authentication for all tenant users
                    </p>
                  </div>
                  <Switch
                    checked={settings.security.requireMfa}
                    onCheckedChange={(checked) => updateSetting('security', 'requireMfa', checked)}
                  />
                </div>
                {settings.security.requireMfa && (
                  <div className="space-y-2">
                    <Label htmlFor="mfaGracePeriod">MFA Grace Period (days)</Label>
                    <Input
                      id="mfaGracePeriod"
                      type="number"
                      min={0}
                      max={30}
                      value={settings.security.mfaGracePeriodDays}
                      onChange={(e) => updateSetting('security', 'mfaGracePeriodDays', parseInt(e.target.value))}
                      className="w-32"
                    />
                    <p className="text-xs text-gray-500">Days users have to enable MFA after requirement is activated</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Billing Settings */}
        <TabsContent value="billing" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Billing Settings
              </CardTitle>
              <CardDescription>
                Configure payment processing and billing defaults
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="taxRate">Default Tax Rate (%)</Label>
                  <Input
                    id="taxRate"
                    type="number"
                    min={0}
                    max={30}
                    value={settings.billing.taxRate}
                    onChange={(e) => updateSetting('billing', 'taxRate', parseFloat(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="trialDays">Trial Period (days)</Label>
                  <Input
                    id="trialDays"
                    type="number"
                    min={0}
                    max={90}
                    value={settings.billing.trialDays}
                    onChange={(e) => updateSetting('billing', 'trialDays', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gracePeriod">Grace Period (days)</Label>
                  <Input
                    id="gracePeriod"
                    type="number"
                    min={0}
                    max={30}
                    value={settings.billing.gracePeriodDays}
                    onChange={(e) => updateSetting('billing', 'gracePeriodDays', parseInt(e.target.value))}
                  />
                  <p className="text-xs text-gray-500">Days after due date before suspension</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="invoicePrefix">Invoice Prefix</Label>
                  <Input
                    id="invoicePrefix"
                    value={settings.billing.invoicePrefix}
                    onChange={(e) => updateSetting('billing', 'invoicePrefix', e.target.value)}
                  />
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Razorpay Configuration</h4>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="razorpayKey">Razorpay Key ID</Label>
                    <Input
                      id="razorpayKey"
                      value={settings.billing.razorpayKeyId}
                      onChange={(e) => updateSetting('billing', 'razorpayKeyId', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="razorpaySecret">Razorpay Key Secret</Label>
                    <Input
                      id="razorpaySecret"
                      type="password"
                      value={settings.billing.razorpayKeySecret}
                      onChange={(e) => updateSetting('billing', 'razorpayKeySecret', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between border-t pt-6">
                <div>
                  <h4 className="font-medium">Auto-suspend on Overdue</h4>
                  <p className="text-sm text-gray-500">
                    Automatically suspend tenants with overdue payments
                  </p>
                </div>
                <Switch
                  checked={settings.billing.autoSuspendOnOverdue}
                  onCheckedChange={(checked) => updateSetting('billing', 'autoSuspendOnOverdue', checked)}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Email Settings */}
        <TabsContent value="email" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Email Configuration
              </CardTitle>
              <CardDescription>
                Configure email delivery settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Email Provider</Label>
                <Select
                  value={settings.email.provider}
                  onValueChange={(value) => updateSetting('email', 'provider', value)}
                >
                  <SelectTrigger className="w-64">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="smtp">SMTP</SelectItem>
                    <SelectItem value="sendgrid">SendGrid</SelectItem>
                    <SelectItem value="ses">Amazon SES</SelectItem>
                    <SelectItem value="mailgun">Mailgun</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {settings.email.provider === 'smtp' && (
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="smtpHost">SMTP Host</Label>
                    <Input
                      id="smtpHost"
                      value={settings.email.smtpHost}
                      onChange={(e) => updateSetting('email', 'smtpHost', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="smtpPort">SMTP Port</Label>
                    <Input
                      id="smtpPort"
                      type="number"
                      value={settings.email.smtpPort}
                      onChange={(e) => updateSetting('email', 'smtpPort', parseInt(e.target.value))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="smtpUser">SMTP Username</Label>
                    <Input
                      id="smtpUser"
                      value={settings.email.smtpUser}
                      onChange={(e) => updateSetting('email', 'smtpUser', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="smtpPassword">SMTP Password</Label>
                    <Input
                      id="smtpPassword"
                      type="password"
                      value={settings.email.smtpPassword}
                      onChange={(e) => updateSetting('email', 'smtpPassword', e.target.value)}
                    />
                  </div>
                </div>
              )}

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Sender Details</h4>
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="fromName">From Name</Label>
                    <Input
                      id="fromName"
                      value={settings.email.fromName}
                      onChange={(e) => updateSetting('email', 'fromName', e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="fromEmail">From Email</Label>
                    <Input
                      id="fromEmail"
                      type="email"
                      value={settings.email.fromEmail}
                      onChange={(e) => updateSetting('email', 'fromEmail', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button variant="outline">
                  <Mail className="h-4 w-4 mr-2" />
                  Send Test Email
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Storage Settings */}
        <TabsContent value="storage" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Storage Configuration
              </CardTitle>
              <CardDescription>
                Configure file storage settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Storage Provider</Label>
                <Select
                  value={settings.storage.provider}
                  onValueChange={(value) => updateSetting('storage', 'provider', value)}
                >
                  <SelectTrigger className="w-64">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="s3">Amazon S3</SelectItem>
                    <SelectItem value="gcs">Google Cloud Storage</SelectItem>
                    <SelectItem value="azure">Azure Blob Storage</SelectItem>
                    <SelectItem value="local">Local Storage</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="bucketName">Bucket Name</Label>
                  <Input
                    id="bucketName"
                    value={settings.storage.bucketName}
                    onChange={(e) => updateSetting('storage', 'bucketName', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="region">Region</Label>
                  <Select
                    value={settings.storage.region}
                    onValueChange={(value) => updateSetting('storage', 'region', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ap-south-1">Asia Pacific (Mumbai)</SelectItem>
                      <SelectItem value="us-east-1">US East (N. Virginia)</SelectItem>
                      <SelectItem value="eu-west-1">Europe (Ireland)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxFileSize">Max File Size (MB)</Label>
                  <Input
                    id="maxFileSize"
                    type="number"
                    min={1}
                    max={500}
                    value={settings.storage.maxFileSizeMb}
                    onChange={(e) => updateSetting('storage', 'maxFileSizeMb', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Allowed File Types</Label>
                <div className="flex flex-wrap gap-2">
                  {settings.storage.allowedFileTypes.map((type) => (
                    <Badge key={type} variant="secondary">
                      .{type}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notification Settings */}
        <TabsContent value="notifications" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Settings
              </CardTitle>
              <CardDescription>
                Configure notification delivery preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Email Notifications</h4>
                    <p className="text-sm text-gray-500">Send notifications via email</p>
                  </div>
                  <Switch
                    checked={settings.notifications.enableEmailNotifications}
                    onCheckedChange={(checked) => updateSetting('notifications', 'enableEmailNotifications', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">SMS Notifications</h4>
                    <p className="text-sm text-gray-500">Send notifications via SMS</p>
                  </div>
                  <Switch
                    checked={settings.notifications.enableSmsNotifications}
                    onCheckedChange={(checked) => updateSetting('notifications', 'enableSmsNotifications', checked)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Push Notifications</h4>
                    <p className="text-sm text-gray-500">Send browser push notifications</p>
                  </div>
                  <Switch
                    checked={settings.notifications.enablePushNotifications}
                    onCheckedChange={(checked) => updateSetting('notifications', 'enablePushNotifications', checked)}
                  />
                </div>
              </div>

              <div className="border-t pt-6">
                <div className="space-y-2">
                  <Label>Digest Frequency</Label>
                  <Select
                    value={settings.notifications.digestFrequency}
                    onValueChange={(value) => updateSetting('notifications', 'digestFrequency', value)}
                  >
                    <SelectTrigger className="w-64">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="realtime">Real-time</SelectItem>
                      <SelectItem value="hourly">Hourly</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center justify-between mt-4">
                  <div>
                    <h4 className="font-medium">Critical Alerts Immediate</h4>
                    <p className="text-sm text-gray-500">Always send critical alerts immediately</p>
                  </div>
                  <Switch
                    checked={settings.notifications.criticalAlertsImmediate}
                    onCheckedChange={(checked) => updateSetting('notifications', 'criticalAlertsImmediate', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Resource Limits */}
        <TabsContent value="limits" className="space-y-4 mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                Default Resource Limits
              </CardTitle>
              <CardDescription>
                Configure default limits for new tenants
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="defaultStorage">Default Storage (GB)</Label>
                  <Input
                    id="defaultStorage"
                    type="number"
                    min={1}
                    max={1000}
                    value={settings.limits.defaultStorageGb}
                    onChange={(e) => updateSetting('limits', 'defaultStorageGb', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="defaultApiCalls">Default API Calls/Month</Label>
                  <Input
                    id="defaultApiCalls"
                    type="number"
                    min={1000}
                    max={1000000}
                    value={settings.limits.defaultApiCallsPerMonth}
                    onChange={(e) => updateSetting('limits', 'defaultApiCallsPerMonth', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="defaultAiQueries">Default AI Queries/Month</Label>
                  <Input
                    id="defaultAiQueries"
                    type="number"
                    min={0}
                    max={10000}
                    value={settings.limits.defaultAiQueriesPerMonth}
                    onChange={(e) => updateSetting('limits', 'defaultAiQueriesPerMonth', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxUsers">Max Users per Tenant</Label>
                  <Input
                    id="maxUsers"
                    type="number"
                    min={1}
                    max={10000}
                    value={settings.limits.maxUsersPerTenant}
                    onChange={(e) => updateSetting('limits', 'maxUsersPerTenant', parseInt(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxEmployees">Max Employees per Tenant</Label>
                  <Input
                    id="maxEmployees"
                    type="number"
                    min={1}
                    max={100000}
                    value={settings.limits.maxEmployeesPerTenant}
                    onChange={(e) => updateSetting('limits', 'maxEmployeesPerTenant', parseInt(e.target.value))}
                  />
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900 dark:text-blue-100">Plan Overrides</h4>
                  <p className="text-sm text-blue-700 dark:text-blue-200">
                    These are default limits. Individual subscription plans can override these values.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
