"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  ArrowLeft,
  Save,
  Lock,
  Shield,
  Key,
  Clock,
  Globe,
  Bell,
  FileText,
  Users,
  AlertTriangle,
  CheckCircle,
  Info,
} from "lucide-react";

export default function SecuritySettingsPage() {
  const [activeTab, setActiveTab] = useState("password");
  const [hasChanges, setHasChanges] = useState(false);

  // Password policy state
  const [passwordPolicy, setPasswordPolicy] = useState({
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecial: true,
    maxAgeDays: 90,
    historyCount: 5,
    lockoutAttempts: 5,
    lockoutDuration: 30,
  });

  // Session policy state
  const [sessionPolicy, setSessionPolicy] = useState({
    timeoutMinutes: 480,
    maxConcurrent: 5,
    requireReauthHours: 24,
    idleTimeoutMinutes: 30,
  });

  // MFA policy state
  const [mfaPolicy, setMfaPolicy] = useState({
    required: false,
    requiredForAdmins: true,
    methodsAllowed: ["totp", "email"],
    rememberDeviceDays: 30,
  });

  // IP restrictions state
  const [ipRestrictions, setIpRestrictions] = useState({
    whitelistEnabled: false,
    whitelist: "",
    blacklistEnabled: false,
    blacklist: "",
    geoRestrictionsEnabled: false,
    allowedCountries: ["IN"],
  });

  // Alert settings state
  const [alertSettings, setAlertSettings] = useState({
    suspiciousLogin: true,
    newDevice: true,
    permissionChange: true,
    bulkDataAccess: true,
    emailRecipients: "security@company.com",
  });

  // Data security state
  const [dataSecurity, setDataSecurity] = useState({
    retentionDays: 2555,
    auditLogRetentionDays: 730,
    encryptSensitiveData: true,
    maskSensitiveFields: true,
  });

  const handleSave = () => {
    // Save settings
    setHasChanges(false);
    // Show success toast
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/security">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Security Settings</h1>
            <p className="text-muted-foreground">
              Configure security policies for your organization
            </p>
          </div>
        </div>
        <Button onClick={handleSave} disabled={!hasChanges}>
          <Save className="mr-2 h-4 w-4" />
          Save Changes
        </Button>
      </div>

      {/* Settings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="password">
            <Lock className="mr-2 h-4 w-4" />
            Password
          </TabsTrigger>
          <TabsTrigger value="session">
            <Clock className="mr-2 h-4 w-4" />
            Session
          </TabsTrigger>
          <TabsTrigger value="mfa">
            <Key className="mr-2 h-4 w-4" />
            MFA
          </TabsTrigger>
          <TabsTrigger value="ip">
            <Globe className="mr-2 h-4 w-4" />
            IP & Geo
          </TabsTrigger>
          <TabsTrigger value="alerts">
            <Bell className="mr-2 h-4 w-4" />
            Alerts
          </TabsTrigger>
          <TabsTrigger value="data">
            <FileText className="mr-2 h-4 w-4" />
            Data
          </TabsTrigger>
        </TabsList>

        {/* Password Policy */}
        <TabsContent value="password">
          <Card>
            <CardHeader>
              <CardTitle>Password Policy</CardTitle>
              <CardDescription>
                Configure password requirements for all users
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="minLength">Minimum Length</Label>
                  <Input
                    id="minLength"
                    type="number"
                    min={6}
                    max={32}
                    value={passwordPolicy.minLength}
                    onChange={(e) => {
                      setPasswordPolicy({ ...passwordPolicy, minLength: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    Minimum 6 characters, maximum 32
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="maxAge">Password Expiry (Days)</Label>
                  <Input
                    id="maxAge"
                    type="number"
                    min={0}
                    max={365}
                    value={passwordPolicy.maxAgeDays}
                    onChange={(e) => {
                      setPasswordPolicy({ ...passwordPolicy, maxAgeDays: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    0 = never expires
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="historyCount">Password History</Label>
                  <Input
                    id="historyCount"
                    type="number"
                    min={0}
                    max={24}
                    value={passwordPolicy.historyCount}
                    onChange={(e) => {
                      setPasswordPolicy({ ...passwordPolicy, historyCount: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    Number of previous passwords to prevent reuse
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="lockoutAttempts">Lockout After (Attempts)</Label>
                  <Input
                    id="lockoutAttempts"
                    type="number"
                    min={3}
                    max={10}
                    value={passwordPolicy.lockoutAttempts}
                    onChange={(e) => {
                      setPasswordPolicy({ ...passwordPolicy, lockoutAttempts: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="text-sm font-medium">Character Requirements</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="requireUppercase">Require uppercase letter</Label>
                    <Switch
                      id="requireUppercase"
                      checked={passwordPolicy.requireUppercase}
                      onCheckedChange={(checked) => {
                        setPasswordPolicy({ ...passwordPolicy, requireUppercase: checked });
                        setHasChanges(true);
                      }}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="requireLowercase">Require lowercase letter</Label>
                    <Switch
                      id="requireLowercase"
                      checked={passwordPolicy.requireLowercase}
                      onCheckedChange={(checked) => {
                        setPasswordPolicy({ ...passwordPolicy, requireLowercase: checked });
                        setHasChanges(true);
                      }}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="requireNumbers">Require number</Label>
                    <Switch
                      id="requireNumbers"
                      checked={passwordPolicy.requireNumbers}
                      onCheckedChange={(checked) => {
                        setPasswordPolicy({ ...passwordPolicy, requireNumbers: checked });
                        setHasChanges(true);
                      }}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label htmlFor="requireSpecial">Require special character</Label>
                    <Switch
                      id="requireSpecial"
                      checked={passwordPolicy.requireSpecial}
                      onCheckedChange={(checked) => {
                        setPasswordPolicy({ ...passwordPolicy, requireSpecial: checked });
                        setHasChanges(true);
                      }}
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Session Policy */}
        <TabsContent value="session">
          <Card>
            <CardHeader>
              <CardTitle>Session Policy</CardTitle>
              <CardDescription>
                Configure session timeout and management settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="sessionTimeout">Session Timeout (Minutes)</Label>
                  <Input
                    id="sessionTimeout"
                    type="number"
                    min={15}
                    max={1440}
                    value={sessionPolicy.timeoutMinutes}
                    onChange={(e) => {
                      setSessionPolicy({ ...sessionPolicy, timeoutMinutes: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    Maximum session duration (15 mins to 24 hours)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="idleTimeout">Idle Timeout (Minutes)</Label>
                  <Input
                    id="idleTimeout"
                    type="number"
                    min={5}
                    max={120}
                    value={sessionPolicy.idleTimeoutMinutes}
                    onChange={(e) => {
                      setSessionPolicy({ ...sessionPolicy, idleTimeoutMinutes: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    Timeout after inactivity
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="maxConcurrent">Max Concurrent Sessions</Label>
                  <Input
                    id="maxConcurrent"
                    type="number"
                    min={1}
                    max={10}
                    value={sessionPolicy.maxConcurrent}
                    onChange={(e) => {
                      setSessionPolicy({ ...sessionPolicy, maxConcurrent: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    Maximum active sessions per user
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="requireReauth">Require Re-auth (Hours)</Label>
                  <Input
                    id="requireReauth"
                    type="number"
                    min={1}
                    max={168}
                    value={sessionPolicy.requireReauthHours}
                    onChange={(e) => {
                      setSessionPolicy({ ...sessionPolicy, requireReauthHours: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    Force re-authentication after this period
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* MFA Policy */}
        <TabsContent value="mfa">
          <Card>
            <CardHeader>
              <CardTitle>Multi-Factor Authentication</CardTitle>
              <CardDescription>
                Configure MFA requirements and allowed methods
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <Label className="text-base">Require MFA for all users</Label>
                    <p className="text-sm text-muted-foreground">
                      All users must set up MFA before accessing the system
                    </p>
                  </div>
                  <Switch
                    checked={mfaPolicy.required}
                    onCheckedChange={(checked) => {
                      setMfaPolicy({ ...mfaPolicy, required: checked });
                      setHasChanges(true);
                    }}
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <Label className="text-base">Require MFA for administrators</Label>
                    <p className="text-sm text-muted-foreground">
                      Admin users must always use MFA
                    </p>
                  </div>
                  <Switch
                    checked={mfaPolicy.requiredForAdmins}
                    onCheckedChange={(checked) => {
                      setMfaPolicy({ ...mfaPolicy, requiredForAdmins: checked });
                      setHasChanges(true);
                    }}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="text-sm font-medium">Allowed MFA Methods</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Shield className="h-5 w-5 text-blue-600" />
                      <div>
                        <div className="font-medium">TOTP Authenticator</div>
                        <div className="text-xs text-muted-foreground">
                          Google Authenticator, Authy, etc.
                        </div>
                      </div>
                    </div>
                    <Switch
                      checked={mfaPolicy.methodsAllowed.includes("totp")}
                      onCheckedChange={(checked) => {
                        const methods = checked
                          ? [...mfaPolicy.methodsAllowed, "totp"]
                          : mfaPolicy.methodsAllowed.filter((m) => m !== "totp");
                        setMfaPolicy({ ...mfaPolicy, methodsAllowed: methods });
                        setHasChanges(true);
                      }}
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Bell className="h-5 w-5 text-purple-600" />
                      <div>
                        <div className="font-medium">Email OTP</div>
                        <div className="text-xs text-muted-foreground">
                          One-time password via email
                        </div>
                      </div>
                    </div>
                    <Switch
                      checked={mfaPolicy.methodsAllowed.includes("email")}
                      onCheckedChange={(checked) => {
                        const methods = checked
                          ? [...mfaPolicy.methodsAllowed, "email"]
                          : mfaPolicy.methodsAllowed.filter((m) => m !== "email");
                        setMfaPolicy({ ...mfaPolicy, methodsAllowed: methods });
                        setHasChanges(true);
                      }}
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Users className="h-5 w-5 text-green-600" />
                      <div>
                        <div className="font-medium">SMS OTP</div>
                        <div className="text-xs text-muted-foreground">
                          One-time password via SMS
                        </div>
                      </div>
                    </div>
                    <Switch
                      checked={mfaPolicy.methodsAllowed.includes("sms")}
                      onCheckedChange={(checked) => {
                        const methods = checked
                          ? [...mfaPolicy.methodsAllowed, "sms"]
                          : mfaPolicy.methodsAllowed.filter((m) => m !== "sms");
                        setMfaPolicy({ ...mfaPolicy, methodsAllowed: methods });
                        setHasChanges(true);
                      }}
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Key className="h-5 w-5 text-orange-600" />
                      <div>
                        <div className="font-medium">Hardware Key</div>
                        <div className="text-xs text-muted-foreground">
                          YubiKey, security keys
                        </div>
                      </div>
                    </div>
                    <Switch
                      checked={mfaPolicy.methodsAllowed.includes("hardware_key")}
                      onCheckedChange={(checked) => {
                        const methods = checked
                          ? [...mfaPolicy.methodsAllowed, "hardware_key"]
                          : mfaPolicy.methodsAllowed.filter((m) => m !== "hardware_key");
                        setMfaPolicy({ ...mfaPolicy, methodsAllowed: methods });
                        setHasChanges(true);
                      }}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Remember Device Duration (Days)</Label>
                <Input
                  type="number"
                  min={0}
                  max={90}
                  value={mfaPolicy.rememberDeviceDays}
                  onChange={(e) => {
                    setMfaPolicy({ ...mfaPolicy, rememberDeviceDays: parseInt(e.target.value) });
                    setHasChanges(true);
                  }}
                />
                <p className="text-xs text-muted-foreground">
                  How long to remember trusted devices (0 = always require MFA)
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* IP & Geo Restrictions */}
        <TabsContent value="ip">
          <Card>
            <CardHeader>
              <CardTitle>IP & Geographic Restrictions</CardTitle>
              <CardDescription>
                Control access based on IP addresses and locations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <Label className="text-base">Enable IP Whitelist</Label>
                  <p className="text-sm text-muted-foreground">
                    Only allow access from specified IP addresses
                  </p>
                </div>
                <Switch
                  checked={ipRestrictions.whitelistEnabled}
                  onCheckedChange={(checked) => {
                    setIpRestrictions({ ...ipRestrictions, whitelistEnabled: checked });
                    setHasChanges(true);
                  }}
                />
              </div>

              {ipRestrictions.whitelistEnabled && (
                <div className="space-y-2">
                  <Label>Allowed IP Addresses</Label>
                  <Input
                    placeholder="e.g., 192.168.1.0/24, 10.0.0.1"
                    value={ipRestrictions.whitelist}
                    onChange={(e) => {
                      setIpRestrictions({ ...ipRestrictions, whitelist: e.target.value });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    Comma-separated list of IP addresses or CIDR ranges
                  </p>
                </div>
              )}

              <Separator />

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <Label className="text-base">Enable Geographic Restrictions</Label>
                  <p className="text-sm text-muted-foreground">
                    Only allow access from specific countries
                  </p>
                </div>
                <Switch
                  checked={ipRestrictions.geoRestrictionsEnabled}
                  onCheckedChange={(checked) => {
                    setIpRestrictions({ ...ipRestrictions, geoRestrictionsEnabled: checked });
                    setHasChanges(true);
                  }}
                />
              </div>

              {ipRestrictions.geoRestrictionsEnabled && (
                <div className="space-y-2">
                  <Label>Allowed Countries</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select countries" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="IN">India</SelectItem>
                      <SelectItem value="US">United States</SelectItem>
                      <SelectItem value="GB">United Kingdom</SelectItem>
                      <SelectItem value="SG">Singapore</SelectItem>
                      <SelectItem value="AE">UAE</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex gap-2 mt-2">
                    <Badge>India</Badge>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Alert Settings */}
        <TabsContent value="alerts">
          <Card>
            <CardHeader>
              <CardTitle>Security Alerts</CardTitle>
              <CardDescription>
                Configure when and how to receive security notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <Label className="text-base">Suspicious Login Attempts</Label>
                    <p className="text-sm text-muted-foreground">
                      Alert on unusual login patterns or locations
                    </p>
                  </div>
                  <Switch
                    checked={alertSettings.suspiciousLogin}
                    onCheckedChange={(checked) => {
                      setAlertSettings({ ...alertSettings, suspiciousLogin: checked });
                      setHasChanges(true);
                    }}
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <Label className="text-base">New Device Login</Label>
                    <p className="text-sm text-muted-foreground">
                      Alert when users log in from new devices
                    </p>
                  </div>
                  <Switch
                    checked={alertSettings.newDevice}
                    onCheckedChange={(checked) => {
                      setAlertSettings({ ...alertSettings, newDevice: checked });
                      setHasChanges(true);
                    }}
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <Label className="text-base">Permission Changes</Label>
                    <p className="text-sm text-muted-foreground">
                      Alert on role or permission modifications
                    </p>
                  </div>
                  <Switch
                    checked={alertSettings.permissionChange}
                    onCheckedChange={(checked) => {
                      setAlertSettings({ ...alertSettings, permissionChange: checked });
                      setHasChanges(true);
                    }}
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <Label className="text-base">Bulk Data Access</Label>
                    <p className="text-sm text-muted-foreground">
                      Alert on large data exports or unusual access patterns
                    </p>
                  </div>
                  <Switch
                    checked={alertSettings.bulkDataAccess}
                    onCheckedChange={(checked) => {
                      setAlertSettings({ ...alertSettings, bulkDataAccess: checked });
                      setHasChanges(true);
                    }}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Alert Recipients</Label>
                <Input
                  type="email"
                  placeholder="security@company.com, admin@company.com"
                  value={alertSettings.emailRecipients}
                  onChange={(e) => {
                    setAlertSettings({ ...alertSettings, emailRecipients: e.target.value });
                    setHasChanges(true);
                  }}
                />
                <p className="text-xs text-muted-foreground">
                  Comma-separated email addresses
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Security */}
        <TabsContent value="data">
          <Card>
            <CardHeader>
              <CardTitle>Data Security & Retention</CardTitle>
              <CardDescription>
                Configure data protection and retention policies
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label>Data Retention (Days)</Label>
                  <Input
                    type="number"
                    min={365}
                    max={3650}
                    value={dataSecurity.retentionDays}
                    onChange={(e) => {
                      setDataSecurity({ ...dataSecurity, retentionDays: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    How long to retain business data (min 1 year)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Audit Log Retention (Days)</Label>
                  <Input
                    type="number"
                    min={90}
                    max={1825}
                    value={dataSecurity.auditLogRetentionDays}
                    onChange={(e) => {
                      setDataSecurity({ ...dataSecurity, auditLogRetentionDays: parseInt(e.target.value) });
                      setHasChanges(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    How long to retain security audit logs
                  </p>
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="text-sm font-medium">Data Protection</h4>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <Label className="text-base">Encrypt Sensitive Data</Label>
                    <p className="text-sm text-muted-foreground">
                      Encrypt PII and sensitive fields at rest
                    </p>
                  </div>
                  <Switch
                    checked={dataSecurity.encryptSensitiveData}
                    onCheckedChange={(checked) => {
                      setDataSecurity({ ...dataSecurity, encryptSensitiveData: checked });
                      setHasChanges(true);
                    }}
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <Label className="text-base">Mask Sensitive Fields</Label>
                    <p className="text-sm text-muted-foreground">
                      Partially hide sensitive data in UI (e.g., ****1234)
                    </p>
                  </div>
                  <Switch
                    checked={dataSecurity.maskSensitiveFields}
                    onCheckedChange={(checked) => {
                      setDataSecurity({ ...dataSecurity, maskSensitiveFields: checked });
                      setHasChanges(true);
                    }}
                  />
                </div>
              </div>

              <Separator />

              <div className="p-4 bg-blue-50 rounded-lg flex items-start gap-3">
                <Info className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900">Compliance Information</h4>
                  <p className="text-sm text-blue-800">
                    These settings help ensure compliance with data protection regulations
                    including GDPR, SOC 2, and ISO 27001. Contact your legal team for
                    specific compliance requirements.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
