"use client"

import * as React from "react"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import {
  Mail,
  Edit,
  Save,
  Loader2,
  Eye,
  Send,
  Copy,
  FileText,
  UserPlus,
  Wallet,
  Calendar,
  KeyRound,
  CheckCircle,
  XCircle,
  AlertCircle,
  RefreshCw
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

interface EmailTemplate {
  id: string
  code: string
  name: string
  description: string
  subject: string
  body: string
  variables: string[]
  category: 'onboarding' | 'payroll' | 'leave' | 'attendance' | 'system'
  isActive: boolean
  lastModified: Date | string
}

// ============================================================================
// Initial Data
// ============================================================================

const TEMPLATE_VARIABLES = {
  employee: ['{{employee_name}}', '{{employee_email}}', '{{employee_id}}', '{{designation}}', '{{department}}', '{{joining_date}}'],
  company: ['{{company_name}}', '{{company_email}}', '{{company_phone}}', '{{company_address}}', '{{company_logo}}'],
  payroll: ['{{month}}', '{{year}}', '{{gross_salary}}', '{{net_salary}}', '{{basic}}', '{{hra}}', '{{pf_deduction}}', '{{tds_deduction}}', '{{total_earnings}}', '{{total_deductions}}'],
  leave: ['{{leave_type}}', '{{from_date}}', '{{to_date}}', '{{days}}', '{{reason}}', '{{approver_name}}', '{{leave_balance}}'],
  system: ['{{reset_link}}', '{{login_link}}', '{{otp}}', '{{expiry_time}}', '{{current_date}}', '{{current_year}}']
}

const INITIAL_TEMPLATES: EmailTemplate[] = [
  {
    id: 'tpl-1',
    code: 'WELCOME',
    name: 'Welcome Email',
    description: 'Sent to new employees upon account creation',
    category: 'onboarding',
    subject: 'Welcome to {{company_name}} - Your Account is Ready!',
    body: `Dear {{employee_name}},

Welcome to {{company_name}}! We are excited to have you join our team.

Your employee account has been created successfully. Here are your login details:

Employee ID: {{employee_id}}
Email: {{employee_email}}
Designation: {{designation}}
Department: {{department}}
Date of Joining: {{joining_date}}

Please click the link below to set up your password and access the employee portal:
{{reset_link}}

This link will expire in 24 hours.

If you have any questions, please contact HR at {{company_email}} or {{company_phone}}.

Best regards,
HR Team
{{company_name}}`,
    variables: ['employee_name', 'company_name', 'employee_id', 'employee_email', 'designation', 'department', 'joining_date', 'reset_link', 'company_email', 'company_phone'],
    isActive: true,
    lastModified: new Date('2024-01-01')
  },
  {
    id: 'tpl-2',
    code: 'PAYSLIP',
    name: 'Payslip Email',
    description: 'Monthly payslip notification with attachment',
    category: 'payroll',
    subject: 'Payslip for {{month}} {{year}} - {{company_name}}',
    body: `Dear {{employee_name}},

Your payslip for {{month}} {{year}} is now available.

Salary Summary:
--------------
Gross Salary: Rs. {{gross_salary}}
Total Deductions: Rs. {{total_deductions}}
Net Salary: Rs. {{net_salary}}

The detailed payslip is attached to this email.

Key Components:
- Basic: Rs. {{basic}}
- HRA: Rs. {{hra}}
- PF Deduction: Rs. {{pf_deduction}}
- TDS: Rs. {{tds_deduction}}

If you have any queries regarding your salary, please contact the payroll team.

Best regards,
Payroll Team
{{company_name}}`,
    variables: ['employee_name', 'month', 'year', 'company_name', 'gross_salary', 'total_deductions', 'net_salary', 'basic', 'hra', 'pf_deduction', 'tds_deduction'],
    isActive: true,
    lastModified: new Date('2024-01-01')
  },
  {
    id: 'tpl-3',
    code: 'LEAVE_APPROVED',
    name: 'Leave Approval Email',
    description: 'Sent when leave request is approved',
    category: 'leave',
    subject: 'Leave Request Approved - {{leave_type}}',
    body: `Dear {{employee_name}},

Your leave request has been approved.

Leave Details:
--------------
Leave Type: {{leave_type}}
From: {{from_date}}
To: {{to_date}}
Duration: {{days}} day(s)
Reason: {{reason}}
Approved By: {{approver_name}}

Remaining Leave Balance: {{leave_balance}} days

Please ensure proper handover of your responsibilities before going on leave.

Best regards,
HR Team
{{company_name}}`,
    variables: ['employee_name', 'leave_type', 'from_date', 'to_date', 'days', 'reason', 'approver_name', 'leave_balance', 'company_name'],
    isActive: true,
    lastModified: new Date('2024-01-01')
  },
  {
    id: 'tpl-4',
    code: 'LEAVE_REJECTED',
    name: 'Leave Rejection Email',
    description: 'Sent when leave request is rejected',
    category: 'leave',
    subject: 'Leave Request Declined - {{leave_type}}',
    body: `Dear {{employee_name}},

We regret to inform you that your leave request has been declined.

Leave Details:
--------------
Leave Type: {{leave_type}}
From: {{from_date}}
To: {{to_date}}
Duration: {{days}} day(s)
Reason: {{reason}}
Declined By: {{approver_name}}

Please contact your manager or HR for more information regarding this decision.

Best regards,
HR Team
{{company_name}}`,
    variables: ['employee_name', 'leave_type', 'from_date', 'to_date', 'days', 'reason', 'approver_name', 'company_name'],
    isActive: true,
    lastModified: new Date('2024-01-01')
  },
  {
    id: 'tpl-5',
    code: 'PASSWORD_RESET',
    name: 'Password Reset Email',
    description: 'Sent when user requests password reset',
    category: 'system',
    subject: 'Password Reset Request - {{company_name}}',
    body: `Dear {{employee_name}},

We received a request to reset your password for your {{company_name}} employee portal account.

Click the link below to reset your password:
{{reset_link}}

This link will expire in {{expiry_time}}.

If you did not request a password reset, please ignore this email or contact IT support immediately.

For security reasons, do not share this link with anyone.

Best regards,
IT Support
{{company_name}}`,
    variables: ['employee_name', 'company_name', 'reset_link', 'expiry_time'],
    isActive: true,
    lastModified: new Date('2024-01-01')
  },
  {
    id: 'tpl-6',
    code: 'LEAVE_PENDING',
    name: 'Leave Request Pending Approval',
    description: 'Sent to approver when new leave request is submitted',
    category: 'leave',
    subject: 'Leave Request Pending Approval - {{employee_name}}',
    body: `Dear {{approver_name}},

A new leave request requires your approval.

Employee: {{employee_name}}
Employee ID: {{employee_id}}
Department: {{department}}

Leave Details:
--------------
Leave Type: {{leave_type}}
From: {{from_date}}
To: {{to_date}}
Duration: {{days}} day(s)
Reason: {{reason}}

Please login to the portal to approve or reject this request:
{{login_link}}

Best regards,
HR System
{{company_name}}`,
    variables: ['approver_name', 'employee_name', 'employee_id', 'department', 'leave_type', 'from_date', 'to_date', 'days', 'reason', 'login_link', 'company_name'],
    isActive: true,
    lastModified: new Date('2024-01-01')
  },
  {
    id: 'tpl-7',
    code: 'ATTENDANCE_ANOMALY',
    name: 'Attendance Anomaly Alert',
    description: 'Sent when attendance irregularity is detected',
    category: 'attendance',
    subject: 'Attendance Alert - Action Required',
    body: `Dear {{employee_name}},

Our system has detected an attendance anomaly for your records.

Date: {{current_date}}
Issue: Missing check-in/check-out

Please regularize your attendance through the employee portal or contact HR.

Login to portal: {{login_link}}

Best regards,
HR Team
{{company_name}}`,
    variables: ['employee_name', 'current_date', 'login_link', 'company_name'],
    isActive: true,
    lastModified: new Date('2024-01-01')
  }
]

const CATEGORY_CONFIG = {
  onboarding: { icon: UserPlus, label: 'Onboarding', color: 'bg-green-500' },
  payroll: { icon: Wallet, label: 'Payroll', color: 'bg-blue-500' },
  leave: { icon: Calendar, label: 'Leave', color: 'bg-purple-500' },
  attendance: { icon: AlertCircle, label: 'Attendance', color: 'bg-yellow-500' },
  system: { icon: KeyRound, label: 'System', color: 'bg-gray-500' }
}

// ============================================================================
// Email Templates Page
// ============================================================================

export default function EmailTemplatesPage() {
  const [templates, setTemplates] = React.useState<EmailTemplate[]>(INITIAL_TEMPLATES)
  const [selectedTemplate, setSelectedTemplate] = React.useState<EmailTemplate | null>(null)
  const [isEditing, setIsEditing] = React.useState(false)
  const [isPreviewOpen, setIsPreviewOpen] = React.useState(false)
  const [isSendTestOpen, setIsSendTestOpen] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(false)
  const [testEmail, setTestEmail] = React.useState('')
  const [activeCategory, setActiveCategory] = React.useState<string>('all')

  // Editor state
  const [editSubject, setEditSubject] = React.useState('')
  const [editBody, setEditBody] = React.useState('')

  // Filter templates
  const filteredTemplates = activeCategory === 'all'
    ? templates
    : templates.filter(t => t.category === activeCategory)

  // Handle template selection
  const handleSelectTemplate = (template: EmailTemplate) => {
    setSelectedTemplate(template)
    setEditSubject(template.subject)
    setEditBody(template.body)
    setIsEditing(false)
  }

  // Handle save
  const handleSave = async () => {
    if (!selectedTemplate) return

    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1000))

    setTemplates(prev => prev.map(t =>
      t.id === selectedTemplate.id
        ? { ...t, subject: editSubject, body: editBody, lastModified: new Date() }
        : t
    ))
    setSelectedTemplate(prev => prev ? { ...prev, subject: editSubject, body: editBody } : null)

    setIsLoading(false)
    setIsEditing(false)
  }

  // Handle send test email
  const handleSendTest = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1500))
    setIsLoading(false)
    setIsSendTestOpen(false)
    setTestEmail('')
  }

  // Handle toggle active
  const handleToggleActive = (id: string) => {
    setTemplates(prev => prev.map(t =>
      t.id === id ? { ...t, isActive: !t.isActive } : t
    ))
  }

  // Copy variable to clipboard
  const handleCopyVariable = (variable: string) => {
    navigator.clipboard.writeText(variable)
  }

  // Format date
  const formatDate = (date: Date | string) => {
    return new Date(date).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Email Templates"
        description="Customize email notifications and templates"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings", href: "/settings" },
          { label: "Email Templates" }
        ]}
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Template List */}
        <div className="lg:col-span-1 space-y-4">
          {/* Category Filter */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant={activeCategory === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveCategory('all')}
            >
              All
            </Button>
            {Object.entries(CATEGORY_CONFIG).map(([key, config]) => (
              <Button
                key={key}
                variant={activeCategory === key ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveCategory(key)}
              >
                {config.label}
              </Button>
            ))}
          </div>

          {/* Template Cards */}
          <div className="space-y-2">
            {filteredTemplates.map(template => {
              const CategoryIcon = CATEGORY_CONFIG[template.category].icon
              return (
                <Card
                  key={template.id}
                  className={`cursor-pointer transition-all ${
                    selectedTemplate?.id === template.id
                      ? 'border-primary shadow-md'
                      : 'hover:border-primary/50'
                  } ${!template.isActive ? 'opacity-60' : ''}`}
                  onClick={() => handleSelectTemplate(template)}
                >
                  <CardContent className="py-3">
                    <div className="flex items-start gap-3">
                      <div className={`h-8 w-8 rounded flex items-center justify-center ${CATEGORY_CONFIG[template.category].color}/10`}>
                        <CategoryIcon className="h-4 w-4" style={{ color: CATEGORY_CONFIG[template.category].color.replace('bg-', 'text-') }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm truncate">{template.name}</span>
                          {!template.isActive && (
                            <Badge variant="secondary" className="text-xs">Disabled</Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground truncate">{template.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>

        {/* Template Editor */}
        <div className="lg:col-span-2">
          {selectedTemplate ? (
            <Card>
              <CardHeader className="flex flex-row items-start justify-between space-y-0">
                <div>
                  <div className="flex items-center gap-2">
                    <CardTitle>{selectedTemplate.name}</CardTitle>
                    <Badge variant="outline">{selectedTemplate.code}</Badge>
                  </div>
                  <CardDescription className="mt-1">
                    {selectedTemplate.description}
                  </CardDescription>
                  <p className="text-xs text-muted-foreground mt-2">
                    Last modified: {formatDate(selectedTemplate.lastModified)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleToggleActive(selectedTemplate.id)}
                  >
                    {selectedTemplate.isActive ? (
                      <>
                        <XCircle className="h-4 w-4 mr-1" />
                        Disable
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Enable
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Subject */}
                <div className="space-y-2">
                  <Label>Subject</Label>
                  {isEditing ? (
                    <Input
                      value={editSubject}
                      onChange={(e) => setEditSubject(e.target.value)}
                      placeholder="Email subject"
                    />
                  ) : (
                    <div className="p-2 bg-muted rounded text-sm">
                      {selectedTemplate.subject}
                    </div>
                  )}
                </div>

                {/* Body */}
                <div className="space-y-2">
                  <Label>Body</Label>
                  {isEditing ? (
                    <textarea
                      value={editBody}
                      onChange={(e) => setEditBody(e.target.value)}
                      className="w-full min-h-[300px] p-3 rounded-md border border-input bg-background text-sm font-mono resize-y"
                      placeholder="Email body"
                    />
                  ) : (
                    <pre className="p-3 bg-muted rounded text-sm whitespace-pre-wrap font-mono max-h-[400px] overflow-y-auto">
                      {selectedTemplate.body}
                    </pre>
                  )}
                </div>

                {/* Variables */}
                <div className="space-y-2">
                  <Label>Available Variables</Label>
                  <div className="flex flex-wrap gap-2 p-3 bg-muted rounded">
                    {selectedTemplate.variables.map(variable => (
                      <Button
                        key={variable}
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs font-mono"
                        onClick={() => handleCopyVariable(`{{${variable}}}`)}
                      >
                        <Copy className="h-3 w-3 mr-1" />
                        {`{{${variable}}}`}
                      </Button>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-4 border-t">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsPreviewOpen(true)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Preview
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsSendTestOpen(true)}
                    >
                      <Send className="h-4 w-4 mr-1" />
                      Send Test
                    </Button>
                  </div>
                  <div className="flex items-center gap-2">
                    {isEditing ? (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setEditSubject(selectedTemplate.subject)
                            setEditBody(selectedTemplate.body)
                            setIsEditing(false)
                          }}
                        >
                          Cancel
                        </Button>
                        <Button size="sm" onClick={handleSave} disabled={isLoading}>
                          {isLoading ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Saving...
                            </>
                          ) : (
                            <>
                              <Save className="mr-2 h-4 w-4" />
                              Save
                            </>
                          )}
                        </Button>
                      </>
                    ) : (
                      <Button size="sm" onClick={() => setIsEditing(true)}>
                        <Edit className="mr-2 h-4 w-4" />
                        Edit Template
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <Mail className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-medium">Select a Template</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Choose a template from the list to view and edit
                </p>
              </CardContent>
            </Card>
          )}

          {/* Variable Reference */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-base">Variable Reference</CardTitle>
              <CardDescription>Copy variables to use in your templates</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="employee">
                <TabsList className="flex-wrap">
                  <TabsTrigger value="employee">Employee</TabsTrigger>
                  <TabsTrigger value="company">Company</TabsTrigger>
                  <TabsTrigger value="payroll">Payroll</TabsTrigger>
                  <TabsTrigger value="leave">Leave</TabsTrigger>
                  <TabsTrigger value="system">System</TabsTrigger>
                </TabsList>
                {Object.entries(TEMPLATE_VARIABLES).map(([category, variables]) => (
                  <TabsContent key={category} value={category}>
                    <div className="flex flex-wrap gap-2">
                      {variables.map(variable => (
                        <Button
                          key={variable}
                          variant="outline"
                          size="sm"
                          className="h-7 text-xs font-mono"
                          onClick={() => handleCopyVariable(variable)}
                        >
                          <Copy className="h-3 w-3 mr-1" />
                          {variable}
                        </Button>
                      ))}
                    </div>
                  </TabsContent>
                ))}
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Preview Dialog */}
      <Dialog open={isPreviewOpen} onOpenChange={setIsPreviewOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Email Preview</DialogTitle>
            <DialogDescription>
              Preview with sample data
            </DialogDescription>
          </DialogHeader>

          {selectedTemplate && (
            <div className="space-y-4 py-4">
              <div className="p-4 border rounded-lg">
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                  <Mail className="h-4 w-4" />
                  <span>To: employee@example.com</span>
                </div>
                <div className="font-medium mb-4">
                  Subject: {selectedTemplate.subject
                    .replace(/\{\{company_name\}\}/g, 'GanaPortal Technologies')
                    .replace(/\{\{month\}\}/g, 'December')
                    .replace(/\{\{year\}\}/g, '2024')
                    .replace(/\{\{employee_name\}\}/g, 'Rajesh Kumar')
                    .replace(/\{\{leave_type\}\}/g, 'Casual Leave')
                  }
                </div>
                <div className="border-t pt-4">
                  <pre className="whitespace-pre-wrap text-sm font-sans">
                    {selectedTemplate.body
                      .replace(/\{\{employee_name\}\}/g, 'Rajesh Kumar')
                      .replace(/\{\{company_name\}\}/g, 'GanaPortal Technologies')
                      .replace(/\{\{employee_id\}\}/g, 'GP001')
                      .replace(/\{\{employee_email\}\}/g, 'rajesh.kumar@ganaportal.in')
                      .replace(/\{\{designation\}\}/g, 'Senior Developer')
                      .replace(/\{\{department\}\}/g, 'Engineering')
                      .replace(/\{\{joining_date\}\}/g, '15 Jan 2024')
                      .replace(/\{\{month\}\}/g, 'December')
                      .replace(/\{\{year\}\}/g, '2024')
                      .replace(/\{\{gross_salary\}\}/g, '1,00,000')
                      .replace(/\{\{net_salary\}\}/g, '75,000')
                      .replace(/\{\{total_deductions\}\}/g, '25,000')
                      .replace(/\{\{basic\}\}/g, '40,000')
                      .replace(/\{\{hra\}\}/g, '20,000')
                      .replace(/\{\{pf_deduction\}\}/g, '4,800')
                      .replace(/\{\{tds_deduction\}\}/g, '10,000')
                      .replace(/\{\{leave_type\}\}/g, 'Casual Leave')
                      .replace(/\{\{from_date\}\}/g, '10 Jan 2025')
                      .replace(/\{\{to_date\}\}/g, '12 Jan 2025')
                      .replace(/\{\{days\}\}/g, '3')
                      .replace(/\{\{reason\}\}/g, 'Personal work')
                      .replace(/\{\{approver_name\}\}/g, 'Priya Sharma')
                      .replace(/\{\{leave_balance\}\}/g, '9')
                      .replace(/\{\{reset_link\}\}/g, 'https://portal.ganaportal.in/reset/xxx')
                      .replace(/\{\{login_link\}\}/g, 'https://portal.ganaportal.in/login')
                      .replace(/\{\{expiry_time\}\}/g, '24 hours')
                      .replace(/\{\{current_date\}\}/g, '06 Jan 2025')
                      .replace(/\{\{company_email\}\}/g, 'hr@ganaportal.in')
                      .replace(/\{\{company_phone\}\}/g, '+91 80 4567 8901')
                    }
                  </pre>
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsPreviewOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Send Test Email Dialog */}
      <Dialog open={isSendTestOpen} onOpenChange={setIsSendTestOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Send Test Email</DialogTitle>
            <DialogDescription>
              Send a test email with sample data
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Recipient Email</Label>
              <Input
                type="email"
                value={testEmail}
                onChange={(e) => setTestEmail(e.target.value)}
                placeholder="test@example.com"
              />
            </div>
            <p className="text-sm text-muted-foreground">
              The email will be sent with sample data to help you verify the template.
            </p>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsSendTestOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSendTest} disabled={isLoading || !testEmail}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Send Test
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
