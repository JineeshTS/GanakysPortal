'use client';

/**
 * Salary Management Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import payrollApi from '@/lib/api/payroll';
import employeesApi from '@/lib/api/employees';
import type { SalaryStructure, TaxRegime } from '@/types/payroll';
import type { Employee } from '@/types/employee';

export default function SalaryManagementPage() {
  const router = useRouter();
  const [salaries, setSalaries] = useState<SalaryStructure[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Form dialog
  const [formDialogOpen, setFormDialogOpen] = useState(false);
  const [selectedSalary, setSelectedSalary] = useState<SalaryStructure | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    employee_id: '',
    effective_from: new Date().toISOString().split('T')[0],
    basic_salary: 0,
    hra_percentage: 40,
    special_allowance: 0,
    pf_applicable: true,
    esi_applicable: false,
    tax_regime: 'new' as TaxRegime,
  });

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [salariesData, employeesData] = await Promise.all([
        payrollApi.getSalaryStructures(),
        employeesApi.getEmployees({ limit: 1000 }),
      ]);
      setSalaries(salariesData);
      setEmployees(employeesData.items);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const openEditDialog = (salary: SalaryStructure) => {
    setSelectedSalary(salary);
    setFormData({
      employee_id: salary.employee_id,
      effective_from: salary.effective_from,
      basic_salary: salary.basic_salary,
      hra_percentage: salary.hra_percentage,
      special_allowance: salary.special_allowance,
      pf_applicable: salary.pf_applicable,
      esi_applicable: salary.esi_applicable,
      tax_regime: salary.tax_regime,
    });
    setFormDialogOpen(true);
  };

  const openCreateDialog = () => {
    setSelectedSalary(null);
    setFormData({
      employee_id: '',
      effective_from: new Date().toISOString().split('T')[0],
      basic_salary: 0,
      hra_percentage: 40,
      special_allowance: 0,
      pf_applicable: true,
      esi_applicable: false,
      tax_regime: 'new',
    });
    setFormDialogOpen(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      if (selectedSalary) {
        await payrollApi.updateSalaryStructure(selectedSalary.id, formData);
      } else {
        await payrollApi.createSalaryStructure(formData);
      }
      setFormDialogOpen(false);
      loadData();
    } catch (error) {
      console.error('Failed to save salary structure:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const calculateCTC = (salary: SalaryStructure) => {
    const hra = salary.basic_salary * (salary.hra_percentage / 100);
    const pfEmployer = salary.pf_applicable ? Math.min(salary.basic_salary * 0.12, 1800) : 0;
    return salary.basic_salary + hra + salary.special_allowance + pfEmployer;
  };

  const filteredSalaries = salaries.filter((s) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      s.employee_name?.toLowerCase().includes(query) ||
      s.employee_code?.toLowerCase().includes(query)
    );
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/payroll')}>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Salary Management</h1>
              <p className="text-muted-foreground">
                Manage employee salary structures
              </p>
            </div>
          </div>
          <Button onClick={openCreateDialog}>
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Salary Structure
          </Button>
        </div>

        {/* Search */}
        <div className="flex gap-4">
          <Input
            placeholder="Search by employee name or code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-sm"
          />
        </div>

        {/* Table */}
        <div className="rounded-lg border bg-card">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-2 text-muted-foreground">Loading salary structures...</p>
            </div>
          ) : filteredSalaries.length === 0 ? (
            <div className="p-8 text-center">
              <svg
                className="mx-auto h-12 w-12 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="mt-2 font-medium">No salary structures found</h3>
              <p className="text-sm text-muted-foreground">
                {searchQuery ? 'Try adjusting your search' : 'Get started by adding a salary structure'}
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Basic</TableHead>
                  <TableHead>HRA</TableHead>
                  <TableHead>Special</TableHead>
                  <TableHead>CTC</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Effective From</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSalaries.map((salary) => (
                  <TableRow key={salary.id}>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarFallback>
                            {getInitials(salary.employee_name || 'NA')}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium">{salary.employee_name}</div>
                          <div className="text-sm text-muted-foreground">
                            {salary.employee_code}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{formatCurrency(salary.basic_salary)}</TableCell>
                    <TableCell>{salary.hra_percentage}%</TableCell>
                    <TableCell>{formatCurrency(salary.special_allowance)}</TableCell>
                    <TableCell className="font-semibold">{formatCurrency(calculateCTC(salary))}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {salary.pf_applicable && (
                          <Badge variant="outline" className="text-xs">PF</Badge>
                        )}
                        {salary.esi_applicable && (
                          <Badge variant="outline" className="text-xs">ESI</Badge>
                        )}
                        <Badge variant="secondary" className="text-xs">
                          {salary.tax_regime.toUpperCase()}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>
                      {new Date(salary.effective_from).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditDialog(salary)}
                      >
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </div>

      {/* Form Dialog */}
      <Dialog open={formDialogOpen} onOpenChange={setFormDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {selectedSalary ? 'Edit Salary Structure' : 'New Salary Structure'}
            </DialogTitle>
            <DialogDescription>
              Define the salary components for the employee
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 max-h-[60vh] overflow-auto">
            {!selectedSalary && (
              <div className="space-y-2">
                <Label>Employee</Label>
                <Select
                  value={formData.employee_id}
                  onValueChange={(v) => setFormData({ ...formData, employee_id: v })}
                  disabled={isSaving}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select employee" />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((emp) => (
                      <SelectItem key={emp.id} value={emp.id}>
                        {emp.first_name} {emp.last_name} ({emp.employee_code})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="space-y-2">
              <Label>Effective From</Label>
              <Input
                type="date"
                value={formData.effective_from}
                onChange={(e) => setFormData({ ...formData, effective_from: e.target.value })}
                disabled={isSaving}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Basic Salary</Label>
                <Input
                  type="number"
                  value={formData.basic_salary}
                  onChange={(e) => setFormData({ ...formData, basic_salary: parseInt(e.target.value) || 0 })}
                  disabled={isSaving}
                />
              </div>
              <div className="space-y-2">
                <Label>HRA Percentage</Label>
                <Input
                  type="number"
                  value={formData.hra_percentage}
                  onChange={(e) => setFormData({ ...formData, hra_percentage: parseInt(e.target.value) || 0 })}
                  disabled={isSaving}
                  max={50}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Special Allowance</Label>
              <Input
                type="number"
                value={formData.special_allowance}
                onChange={(e) => setFormData({ ...formData, special_allowance: parseInt(e.target.value) || 0 })}
                disabled={isSaving}
              />
            </div>

            <div className="space-y-2">
              <Label>Tax Regime</Label>
              <Select
                value={formData.tax_regime}
                onValueChange={(v) => setFormData({ ...formData, tax_regime: v as TaxRegime })}
                disabled={isSaving}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">New Regime</SelectItem>
                  <SelectItem value="old">Old Regime</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex gap-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="pf_applicable"
                  checked={formData.pf_applicable}
                  onChange={(e) => setFormData({ ...formData, pf_applicable: e.target.checked })}
                  disabled={isSaving}
                  className="h-4 w-4"
                />
                <Label htmlFor="pf_applicable" className="font-normal">
                  PF Applicable
                </Label>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="esi_applicable"
                  checked={formData.esi_applicable}
                  onChange={(e) => setFormData({ ...formData, esi_applicable: e.target.checked })}
                  disabled={isSaving}
                  className="h-4 w-4"
                />
                <Label htmlFor="esi_applicable" className="font-normal">
                  ESI Applicable
                </Label>
              </div>
            </div>

            {/* CTC Preview */}
            <div className="rounded-lg bg-muted p-4">
              <div className="text-sm text-muted-foreground mb-2">Estimated CTC</div>
              <div className="text-2xl font-bold">
                {formatCurrency(
                  formData.basic_salary +
                  (formData.basic_salary * formData.hra_percentage / 100) +
                  formData.special_allowance +
                  (formData.pf_applicable ? Math.min(formData.basic_salary * 0.12, 1800) : 0)
                )}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setFormDialogOpen(false)}
              disabled={isSaving}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={isSaving || (!selectedSalary && !formData.employee_id)}
            >
              {isSaving ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
