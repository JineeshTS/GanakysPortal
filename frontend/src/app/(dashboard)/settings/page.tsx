'use client';

/**
 * Settings Page
 */

import { useState, useEffect, useCallback } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import payrollApi from '@/lib/api/payroll';
import employeesApi from '@/lib/api/employees';
import type { PayrollComponent } from '@/types/payroll';
import type { Department, Designation } from '@/types/employee';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('payroll');
  const [components, setComponents] = useState<PayrollComponent[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [compData, deptData, desigData] = await Promise.all([
        payrollApi.getPayrollComponents(),
        employeesApi.getDepartments(),
        employeesApi.getDesignations(),
      ]);
      setComponents(compData);
      setDepartments(deptData);
      setDesignations(desigData);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const toggleComponent = async (id: string, isActive: boolean) => {
    try {
      await payrollApi.togglePayrollComponent(id, !isActive);
      loadData();
    } catch (error) {
      console.error('Failed to toggle component:', error);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Configure system settings and parameters
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="payroll">Payroll Components</TabsTrigger>
            <TabsTrigger value="organization">Organization</TabsTrigger>
            <TabsTrigger value="general">General</TabsTrigger>
          </TabsList>

          {/* Payroll Components */}
          <TabsContent value="payroll" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Salary Components</CardTitle>
                    <CardDescription>
                      Configure earnings and deduction components
                    </CardDescription>
                  </div>
                  <Button>
                    <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Add Component
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="py-8 text-center">
                    <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-green-600 mb-2">Earnings</h4>
                      <div className="space-y-2">
                        {components
                          .filter((c) => c.type === 'earning')
                          .map((comp) => (
                            <div
                              key={comp.id}
                              className="flex items-center justify-between py-2 px-3 rounded-lg border"
                            >
                              <div>
                                <div className="font-medium">{comp.name}</div>
                                <div className="text-sm text-muted-foreground">
                                  {comp.code} • {comp.calculation_type}
                                  {comp.is_taxable && ' • Taxable'}
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge
                                  variant={comp.is_active ? 'default' : 'secondary'}
                                  className="cursor-pointer"
                                  onClick={() => toggleComponent(comp.id, comp.is_active)}
                                >
                                  {comp.is_active ? 'Active' : 'Inactive'}
                                </Badge>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-red-600 mb-2">Deductions</h4>
                      <div className="space-y-2">
                        {components
                          .filter((c) => c.type === 'deduction')
                          .map((comp) => (
                            <div
                              key={comp.id}
                              className="flex items-center justify-between py-2 px-3 rounded-lg border"
                            >
                              <div>
                                <div className="font-medium">{comp.name}</div>
                                <div className="text-sm text-muted-foreground">
                                  {comp.code} • {comp.calculation_type}
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge
                                  variant={comp.is_active ? 'default' : 'secondary'}
                                  className="cursor-pointer"
                                  onClick={() => toggleComponent(comp.id, comp.is_active)}
                                >
                                  {comp.is_active ? 'Active' : 'Inactive'}
                                </Badge>
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Statutory Settings</CardTitle>
                <CardDescription>
                  Configure PF, ESI, and other statutory parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>PF Employee Contribution (%)</Label>
                    <Input type="number" defaultValue={12} />
                  </div>
                  <div className="space-y-2">
                    <Label>PF Employer Contribution (%)</Label>
                    <Input type="number" defaultValue={12} />
                  </div>
                  <div className="space-y-2">
                    <Label>ESI Employee Contribution (%)</Label>
                    <Input type="number" defaultValue={0.75} step={0.01} />
                  </div>
                  <div className="space-y-2">
                    <Label>ESI Employer Contribution (%)</Label>
                    <Input type="number" defaultValue={3.25} step={0.01} />
                  </div>
                  <div className="space-y-2">
                    <Label>ESI Wage Ceiling</Label>
                    <Input type="number" defaultValue={21000} />
                  </div>
                  <div className="space-y-2">
                    <Label>PF Wage Ceiling</Label>
                    <Input type="number" defaultValue={15000} />
                  </div>
                </div>
                <Button>Save Statutory Settings</Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Organization */}
          <TabsContent value="organization" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Departments</CardTitle>
                    <CardDescription>Manage organization departments</CardDescription>
                  </div>
                  <Button>Add Department</Button>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="py-8 text-center">
                    <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  </div>
                ) : departments.length === 0 ? (
                  <p className="text-muted-foreground">No departments configured</p>
                ) : (
                  <div className="space-y-2">
                    {departments.map((dept) => (
                      <div
                        key={dept.id}
                        className="flex items-center justify-between py-2 px-3 rounded-lg border"
                      >
                        <div>
                          <div className="font-medium">{dept.name}</div>
                          <div className="text-sm text-muted-foreground">{dept.code}</div>
                        </div>
                        <Badge variant={dept.is_active ? 'default' : 'secondary'}>
                          {dept.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Designations</CardTitle>
                    <CardDescription>Manage job titles and roles</CardDescription>
                  </div>
                  <Button>Add Designation</Button>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="py-8 text-center">
                    <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  </div>
                ) : designations.length === 0 ? (
                  <p className="text-muted-foreground">No designations configured</p>
                ) : (
                  <div className="space-y-2">
                    {designations.map((desig) => (
                      <div
                        key={desig.id}
                        className="flex items-center justify-between py-2 px-3 rounded-lg border"
                      >
                        <div>
                          <div className="font-medium">{desig.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {desig.code}
                            {desig.level && ` • Level ${desig.level}`}
                          </div>
                        </div>
                        <Badge variant={desig.is_active ? 'default' : 'secondary'}>
                          {desig.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* General Settings */}
          <TabsContent value="general" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Company Information</CardTitle>
                <CardDescription>
                  Basic company details used in reports and documents
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Company Name</Label>
                    <Input placeholder="Ganakys Codilla Apps" />
                  </div>
                  <div className="space-y-2">
                    <Label>Company Code</Label>
                    <Input placeholder="GCA" />
                  </div>
                  <div className="space-y-2">
                    <Label>PAN Number</Label>
                    <Input placeholder="AAAAA0000A" />
                  </div>
                  <div className="space-y-2">
                    <Label>TAN Number</Label>
                    <Input placeholder="AAAA00000A" />
                  </div>
                  <div className="space-y-2 col-span-2">
                    <Label>Registered Address</Label>
                    <Input placeholder="Company Address" />
                  </div>
                </div>
                <Button>Save Company Info</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Financial Year</CardTitle>
                <CardDescription>
                  Configure financial year settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Financial Year Start Month</Label>
                    <Select defaultValue="4">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">January</SelectItem>
                        <SelectItem value="4">April</SelectItem>
                        <SelectItem value="7">July</SelectItem>
                        <SelectItem value="10">October</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Default Currency</Label>
                    <Select defaultValue="INR">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="INR">INR - Indian Rupee</SelectItem>
                        <SelectItem value="USD">USD - US Dollar</SelectItem>
                        <SelectItem value="EUR">EUR - Euro</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button>Save Settings</Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
