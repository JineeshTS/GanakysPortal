'use client';

/**
 * Add New Employee Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
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
import employeesApi from '@/lib/api/employees';
import type { Department, Designation, EmploymentType, EmployeeCreateRequest } from '@/types/employee';

const employmentTypeLabels: Record<EmploymentType, string> = {
  full_time: 'Full Time',
  part_time: 'Part Time',
  contract: 'Contract',
  intern: 'Intern',
};

const genderOptions = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
];

export default function AddEmployeePage() {
  const router = useRouter();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Form state
  const [formData, setFormData] = useState<EmployeeCreateRequest>({
    email: '',
    first_name: '',
    middle_name: '',
    last_name: '',
    date_of_birth: '',
    gender: undefined,
    department_id: '',
    designation_id: '',
    reporting_manager_id: '',
    employment_type: 'full_time',
    date_of_joining: new Date().toISOString().split('T')[0],
  });

  const loadFilters = useCallback(async () => {
    try {
      const [depts, desigs] = await Promise.all([
        employeesApi.getDepartments(),
        employeesApi.getDesignations(),
      ]);
      setDepartments(depts);
      setDesignations(desigs);
    } catch (err) {
      console.error('Failed to load filters:', err);
    }
  }, []);

  useEffect(() => {
    loadFilters();
  }, [loadFilters]);

  const updateField = <K extends keyof EmployeeCreateRequest>(
    field: K,
    value: EmployeeCreateRequest[K]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError('');
  };

  const validateForm = (): string | null => {
    if (!formData.email?.trim()) {
      return 'Email is required';
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      return 'Please enter a valid email address';
    }
    if (!formData.first_name?.trim()) {
      return 'First name is required';
    }
    if (!formData.last_name?.trim()) {
      return 'Last name is required';
    }
    if (!formData.date_of_joining) {
      return 'Date of joining is required';
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Clean up optional fields
      const payload: EmployeeCreateRequest = {
        email: formData.email.trim(),
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        employment_type: formData.employment_type,
        date_of_joining: formData.date_of_joining,
      };

      if (formData.middle_name?.trim()) {
        payload.middle_name = formData.middle_name.trim();
      }
      if (formData.date_of_birth) {
        payload.date_of_birth = formData.date_of_birth;
      }
      if (formData.gender) {
        payload.gender = formData.gender;
      }
      if (formData.department_id) {
        payload.department_id = formData.department_id;
      }
      if (formData.designation_id) {
        payload.designation_id = formData.designation_id;
      }
      if (formData.reporting_manager_id) {
        payload.reporting_manager_id = formData.reporting_manager_id;
      }

      const employee = await employeesApi.createEmployee(payload);
      router.push(`/employees/${employee.id}`);
    } catch (err) {
      console.error('Failed to create employee:', err);
      setError(err instanceof Error ? err.message : 'Failed to create employee');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/employees')}>
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Add New Employee</h1>
            <p className="text-muted-foreground">
              Create a new employee record in the system
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Error Message */}
          {error && (
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
              <div className="flex items-center gap-2">
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                {error}
              </div>
            </div>
          )}

          {/* Account Information */}
          <Card>
            <CardHeader>
              <CardTitle>Account Information</CardTitle>
              <CardDescription>
                This will be used to create a user account for the employee
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">
                  Work Email <span className="text-destructive">*</span>
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="employee@company.com"
                  value={formData.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  disabled={isLoading}
                />
                <p className="text-xs text-muted-foreground">
                  A password reset link will be sent to this email
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Personal Information */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
              <CardDescription>Basic details about the employee</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">
                    First Name <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="first_name"
                    placeholder="John"
                    value={formData.first_name}
                    onChange={(e) => updateField('first_name', e.target.value)}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="middle_name">Middle Name</Label>
                  <Input
                    id="middle_name"
                    placeholder="William"
                    value={formData.middle_name}
                    onChange={(e) => updateField('middle_name', e.target.value)}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="last_name">
                    Last Name <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="last_name"
                    placeholder="Doe"
                    value={formData.last_name}
                    onChange={(e) => updateField('last_name', e.target.value)}
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="date_of_birth">Date of Birth</Label>
                  <Input
                    id="date_of_birth"
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => updateField('date_of_birth', e.target.value)}
                    disabled={isLoading}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="gender">Gender</Label>
                  <Select
                    value={formData.gender || ''}
                    onValueChange={(v) => updateField('gender', v as EmployeeCreateRequest['gender'])}
                    disabled={isLoading}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      {genderOptions.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Employment Details */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Employment Details</CardTitle>
              <CardDescription>Job role and organizational information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Select
                    value={formData.department_id || ''}
                    onValueChange={(v) => updateField('department_id', v)}
                    disabled={isLoading}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select department" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map((dept) => (
                        <SelectItem key={dept.id} value={dept.id}>
                          {dept.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="designation">Designation</Label>
                  <Select
                    value={formData.designation_id || ''}
                    onValueChange={(v) => updateField('designation_id', v)}
                    disabled={isLoading}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select designation" />
                    </SelectTrigger>
                    <SelectContent>
                      {designations.map((desig) => (
                        <SelectItem key={desig.id} value={desig.id}>
                          {desig.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="employment_type">
                    Employment Type <span className="text-destructive">*</span>
                  </Label>
                  <Select
                    value={formData.employment_type}
                    onValueChange={(v) => updateField('employment_type', v as EmploymentType)}
                    disabled={isLoading}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(employmentTypeLabels).map(([value, label]) => (
                        <SelectItem key={value} value={value}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="date_of_joining">
                    Date of Joining <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="date_of_joining"
                    type="date"
                    value={formData.date_of_joining}
                    onChange={(e) => updateField('date_of_joining', e.target.value)}
                    disabled={isLoading}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex justify-end gap-4 mt-6">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.push('/employees')}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                  Creating...
                </>
              ) : (
                <>
                  <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create Employee
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}
