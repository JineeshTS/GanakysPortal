'use client';

import { useState } from 'react';
import { Check, ChevronLeft, ChevronRight, Building2, Users, Wallet, FileText, Settings, Bell, Shield, Rocket } from 'lucide-react';
import { PageHeader } from '@/components/layout/page-header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface Step {
  id: number;
  title: string;
  description: string;
  icon: React.ElementType;
}

const steps: Step[] = [
  { id: 1, title: 'Company Setup', description: 'Basic company information', icon: Building2 },
  { id: 2, title: 'Departments', description: 'Create departments', icon: Users },
  { id: 3, title: 'Salary Components', description: 'Configure salary structure', icon: Wallet },
  { id: 4, title: 'Leave Policies', description: 'Setup leave types', icon: FileText },
  { id: 5, title: 'Statutory Settings', description: 'PF, ESI, TDS configuration', icon: Settings },
  { id: 6, title: 'Email Setup', description: 'Configure email notifications', icon: Bell },
  { id: 7, title: 'User Roles', description: 'Setup permissions', icon: Shield },
  { id: 8, title: 'Go Live', description: 'Review and launch', icon: Rocket },
];

// Step 1: Company Setup
function CompanySetupStep() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label>Company Name *</Label>
          <Input placeholder="Acme Corporation Pvt Ltd" className="mt-1.5" />
        </div>
        <div>
          <Label>Legal Name</Label>
          <Input placeholder="Acme Corporation Private Limited" className="mt-1.5" />
        </div>
        <div>
          <Label>CIN Number</Label>
          <Input placeholder="U12345MH2020PTC123456" className="mt-1.5" />
        </div>
        <div>
          <Label>GSTIN</Label>
          <Input placeholder="27AABCU9603R1ZM" className="mt-1.5" />
        </div>
        <div>
          <Label>PAN</Label>
          <Input placeholder="AABCU9603R" className="mt-1.5" />
        </div>
        <div>
          <Label>TAN</Label>
          <Input placeholder="MUMU12345A" className="mt-1.5" />
        </div>
        <div className="md:col-span-2">
          <Label>Registered Address *</Label>
          <Input placeholder="123 Business Park, Mumbai 400001" className="mt-1.5" />
        </div>
        <div>
          <Label>Contact Email *</Label>
          <Input type="email" placeholder="hr@acme.com" className="mt-1.5" />
        </div>
        <div>
          <Label>Contact Phone</Label>
          <Input placeholder="+91 22 1234 5678" className="mt-1.5" />
        </div>
      </div>
    </div>
  );
}

// Step 2: Departments
function DepartmentsStep() {
  const defaultDepts = ['HR', 'Finance', 'Engineering', 'Sales', 'Operations'];
  return (
    <div className="space-y-6">
      <p className="text-sm text-muted-foreground">
        Create departments for your organization. You can add more later.
      </p>
      <div className="space-y-3">
        {defaultDepts.map((dept, i) => (
          <div key={i} className="flex items-center gap-3">
            <Input defaultValue={dept} className="flex-1" />
            <Button variant="outline" size="icon">×</Button>
          </div>
        ))}
        <Button variant="outline" className="w-full">+ Add Department</Button>
      </div>
    </div>
  );
}

// Step 3: Salary Components
function SalaryComponentsStep() {
  return (
    <div className="space-y-6">
      <div>
        <h4 className="font-medium mb-3">Earnings</h4>
        <div className="space-y-2 bg-green-50 dark:bg-green-950/20 p-4 rounded-lg">
          {['Basic', 'HRA', 'Special Allowance', 'Conveyance', 'Medical'].map((comp, i) => (
            <div key={i} className="flex items-center justify-between p-2 bg-background rounded">
              <span>{comp}</span>
              <span className="text-sm text-muted-foreground">Enabled</span>
            </div>
          ))}
        </div>
      </div>
      <div>
        <h4 className="font-medium mb-3">Deductions</h4>
        <div className="space-y-2 bg-red-50 dark:bg-red-950/20 p-4 rounded-lg">
          {['PF (Employee)', 'ESI (Employee)', 'Professional Tax', 'TDS'].map((comp, i) => (
            <div key={i} className="flex items-center justify-between p-2 bg-background rounded">
              <span>{comp}</span>
              <span className="text-sm text-muted-foreground">Enabled</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Step 4: Leave Policies
function LeavePoliciesStep() {
  const leaveTypes = [
    { name: 'Casual Leave (CL)', days: 12, color: 'bg-green-500' },
    { name: 'Earned Leave (EL)', days: 15, color: 'bg-blue-500' },
    { name: 'Sick Leave (SL)', days: 12, color: 'bg-red-500' },
    { name: 'Maternity Leave (ML)', days: 182, color: 'bg-pink-500' },
  ];
  return (
    <div className="space-y-4">
      {leaveTypes.map((leave, i) => (
        <div key={i} className="flex items-center gap-4 p-4 border rounded-lg">
          <div className={cn('w-3 h-3 rounded-full', leave.color)} />
          <div className="flex-1">
            <div className="font-medium">{leave.name}</div>
          </div>
          <div className="flex items-center gap-2">
            <Input type="number" defaultValue={leave.days} className="w-20" />
            <span className="text-sm text-muted-foreground">days/year</span>
          </div>
        </div>
      ))}
    </div>
  );
}

// Step 5: Statutory Settings
function StatutorySettingsStep() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Provident Fund (PF)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span>PF Establishment Code</span>
            <Input placeholder="MHBAN12345" className="w-48" />
          </div>
          <div className="flex items-center justify-between">
            <span>Employer Contribution</span>
            <span className="font-medium">12%</span>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">ESI</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span>ESI Code</span>
            <Input placeholder="12345678901234567" className="w-48" />
          </div>
          <div className="flex items-center justify-between">
            <span>Wage Limit</span>
            <span className="font-medium">₹21,000</span>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Professional Tax</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <span>State</span>
            <span className="font-medium">Karnataka</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Step 6: Email Setup
function EmailSetupStep() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label>SMTP Host</Label>
          <Input placeholder="smtp.hostinger.com" className="mt-1.5" />
        </div>
        <div>
          <Label>SMTP Port</Label>
          <Input placeholder="587" className="mt-1.5" />
        </div>
        <div>
          <Label>Email Username</Label>
          <Input placeholder="noreply@yourcompany.com" className="mt-1.5" />
        </div>
        <div>
          <Label>Email Password</Label>
          <Input type="password" placeholder="••••••••" className="mt-1.5" />
        </div>
        <div className="md:col-span-2">
          <Label>From Name</Label>
          <Input placeholder="Acme HR System" className="mt-1.5" />
        </div>
      </div>
      <Button variant="outline">Send Test Email</Button>
    </div>
  );
}

// Step 7: User Roles
function UserRolesStep() {
  const roles = [
    { name: 'Super Admin', desc: 'Full access to all features', users: 1 },
    { name: 'HR Manager', desc: 'Manage employees, payroll, leave', users: 0 },
    { name: 'Finance Manager', desc: 'Manage accounting, invoices', users: 0 },
    { name: 'Employee', desc: 'Self-service portal access', users: 0 },
  ];
  return (
    <div className="space-y-4">
      {roles.map((role, i) => (
        <div key={i} className="flex items-center gap-4 p-4 border rounded-lg">
          <div className="flex-1">
            <div className="font-medium">{role.name}</div>
            <div className="text-sm text-muted-foreground">{role.desc}</div>
          </div>
          <div className="text-sm text-muted-foreground">{role.users} users</div>
          <Button variant="outline" size="sm">Configure</Button>
        </div>
      ))}
    </div>
  );
}

// Step 8: Go Live
function GoLiveStep() {
  const checkItems = [
    { name: 'Company information configured', done: true },
    { name: 'Departments created', done: true },
    { name: 'Salary structure defined', done: true },
    { name: 'Leave policies configured', done: true },
    { name: 'Statutory settings completed', done: true },
    { name: 'Email configured', done: false },
    { name: 'User roles defined', done: true },
  ];
  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <Rocket className="h-16 w-16 mx-auto text-primary mb-4" />
        <h3 className="text-xl font-semibold">Ready to Launch!</h3>
        <p className="text-muted-foreground">Review your setup before going live</p>
      </div>
      <div className="space-y-2">
        {checkItems.map((item, i) => (
          <div key={i} className="flex items-center gap-3 p-3 border rounded-lg">
            <div className={cn(
              'w-5 h-5 rounded-full flex items-center justify-center',
              item.done ? 'bg-green-500 text-white' : 'bg-yellow-500 text-white'
            )}>
              {item.done ? <Check className="h-3 w-3" /> : '!'}
            </div>
            <span className={item.done ? '' : 'text-yellow-600'}>{item.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function SetupWizardPage() {
  const [currentStep, setCurrentStep] = useState(1);

  const renderStep = () => {
    switch (currentStep) {
      case 1: return <CompanySetupStep />;
      case 2: return <DepartmentsStep />;
      case 3: return <SalaryComponentsStep />;
      case 4: return <LeavePoliciesStep />;
      case 5: return <StatutorySettingsStep />;
      case 6: return <EmailSetupStep />;
      case 7: return <UserRolesStep />;
      case 8: return <GoLiveStep />;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Initial Setup Wizard"
        description="Configure your HR & Finance system step by step"
        icon={<Settings className="h-6 w-6" />}
      />

      <div className="max-w-4xl mx-auto">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = step.id === currentStep;
              const isComplete = step.id < currentStep;
              return (
                <div key={step.id} className="flex flex-col items-center flex-1">
                  <div className="flex items-center w-full">
                    {index > 0 && (
                      <div className={cn(
                        'flex-1 h-1 mx-2',
                        isComplete ? 'bg-primary' : 'bg-muted'
                      )} />
                    )}
                    <button
                      onClick={() => setCurrentStep(step.id)}
                      className={cn(
                        'w-10 h-10 rounded-full flex items-center justify-center transition-colors',
                        isActive && 'bg-primary text-primary-foreground',
                        isComplete && 'bg-primary text-primary-foreground',
                        !isActive && !isComplete && 'bg-muted text-muted-foreground'
                      )}
                    >
                      {isComplete ? <Check className="h-5 w-5" /> : <Icon className="h-5 w-5" />}
                    </button>
                    {index < steps.length - 1 && (
                      <div className={cn(
                        'flex-1 h-1 mx-2',
                        step.id < currentStep ? 'bg-primary' : 'bg-muted'
                      )} />
                    )}
                  </div>
                  <span className={cn(
                    'text-xs mt-2 text-center hidden md:block',
                    isActive ? 'text-primary font-medium' : 'text-muted-foreground'
                  )}>
                    {step.title}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Step Content */}
        <Card>
          <CardHeader>
            <CardTitle>{steps[currentStep - 1].title}</CardTitle>
            <CardDescription>{steps[currentStep - 1].description}</CardDescription>
          </CardHeader>
          <CardContent>
            {renderStep()}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1}
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>
          {currentStep < 8 ? (
            <Button onClick={() => setCurrentStep(currentStep + 1)}>
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button className="bg-green-600 hover:bg-green-700">
              <Rocket className="h-4 w-4 mr-2" />
              Go Live
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
