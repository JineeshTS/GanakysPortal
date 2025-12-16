'use client';

/**
 * Employee Profile Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
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
import employeesApi from '@/lib/api/employees';
import type {
  Employee,
  EmployeeDocument,
  Department,
  Designation,
  EmploymentStatus,
  EmploymentType,
} from '@/types/employee';

const statusColors: Record<EmploymentStatus, string> = {
  active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  probation: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  notice_period: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
  resigned: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
  terminated: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
};

const statusLabels: Record<EmploymentStatus, string> = {
  active: 'Active',
  probation: 'Probation',
  notice_period: 'Notice Period',
  resigned: 'Resigned',
  terminated: 'Terminated',
};

const employmentTypeLabels: Record<EmploymentType, string> = {
  full_time: 'Full Time',
  part_time: 'Part Time',
  contract: 'Contract',
  intern: 'Intern',
};

const documentTypes = [
  { value: 'id_proof', label: 'ID Proof' },
  { value: 'address_proof', label: 'Address Proof' },
  { value: 'education', label: 'Education Certificate' },
  { value: 'experience', label: 'Experience Letter' },
  { value: 'offer_letter', label: 'Offer Letter' },
  { value: 'contract', label: 'Contract' },
  { value: 'other', label: 'Other' },
];

export default function EmployeeProfilePage() {
  const params = useParams();
  const router = useRouter();
  const employeeId = params.id as string;

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [documents, setDocuments] = useState<EmployeeDocument[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('personal');

  // Edit states
  const [editMode, setEditMode] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, unknown>>({});

  // Document upload
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [uploadDocType, setUploadDocType] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadDescription, setUploadDescription] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const loadEmployee = useCallback(async () => {
    try {
      const data = await employeesApi.getEmployee(employeeId);
      setEmployee(data);
    } catch (error) {
      console.error('Failed to load employee:', error);
      router.push('/employees');
    }
  }, [employeeId, router]);

  const loadDocuments = useCallback(async () => {
    try {
      const data = await employeesApi.getDocuments(employeeId);
      setDocuments(data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  }, [employeeId]);

  const loadFilters = useCallback(async () => {
    try {
      const [depts, desigs] = await Promise.all([
        employeesApi.getDepartments(),
        employeesApi.getDesignations(),
      ]);
      setDepartments(depts);
      setDesignations(desigs);
    } catch (error) {
      console.error('Failed to load filters:', error);
    }
  }, []);

  useEffect(() => {
    const loadAll = async () => {
      setIsLoading(true);
      await Promise.all([loadEmployee(), loadDocuments(), loadFilters()]);
      setIsLoading(false);
    };
    loadAll();
  }, [loadEmployee, loadDocuments, loadFilters]);

  const startEdit = (section: string) => {
    if (!employee) return;

    switch (section) {
      case 'personal':
        setFormData({
          first_name: employee.first_name,
          middle_name: employee.middle_name || '',
          last_name: employee.last_name,
          date_of_birth: employee.date_of_birth || '',
          gender: employee.gender || '',
          blood_group: employee.blood_group || '',
          marital_status: employee.marital_status || '',
          nationality: employee.nationality || '',
        });
        break;
      case 'contact':
        setFormData({
          personal_email: employee.contact?.personal_email || '',
          personal_phone: employee.contact?.personal_phone || '',
          emergency_contact_name: employee.contact?.emergency_contact_name || '',
          emergency_contact_phone: employee.contact?.emergency_contact_phone || '',
          emergency_contact_relation: employee.contact?.emergency_contact_relation || '',
          current_address: employee.contact?.current_address || '',
          permanent_address: employee.contact?.permanent_address || '',
        });
        break;
      case 'identity':
        setFormData({
          pan_number: employee.identity?.pan_number || '',
          aadhaar_number: employee.identity?.aadhaar_number || '',
          passport_number: employee.identity?.passport_number || '',
          passport_expiry: employee.identity?.passport_expiry || '',
          driving_license: employee.identity?.driving_license || '',
          voter_id: employee.identity?.voter_id || '',
        });
        break;
      case 'bank':
        setFormData({
          bank_name: employee.bank?.bank_name || '',
          branch_name: employee.bank?.branch_name || '',
          account_number: employee.bank?.account_number || '',
          ifsc_code: employee.bank?.ifsc_code || '',
          account_type: employee.bank?.account_type || '',
        });
        break;
      case 'employment':
        setFormData({
          department_id: employee.employment?.department_id || '',
          designation_id: employee.employment?.designation_id || '',
          reporting_manager_id: employee.employment?.reporting_manager_id || '',
          employment_type: employee.employment?.employment_type || '',
          date_of_joining: employee.employment?.date_of_joining || '',
          probation_end_date: employee.employment?.probation_end_date || '',
          confirmation_date: employee.employment?.confirmation_date || '',
          notice_period_days: employee.employment?.notice_period_days || 30,
          current_status: employee.employment?.current_status || 'active',
        });
        break;
    }
    setEditMode(section);
  };

  const cancelEdit = () => {
    setEditMode(null);
    setFormData({});
  };

  const saveChanges = async () => {
    if (!editMode || !employee) return;

    setIsSaving(true);
    try {
      switch (editMode) {
        case 'personal':
          await employeesApi.updateEmployee(employeeId, formData as Partial<Employee>);
          break;
        case 'contact':
          await employeesApi.updateContact(employeeId, formData);
          break;
        case 'identity':
          await employeesApi.updateIdentity(employeeId, formData);
          break;
        case 'bank':
          await employeesApi.updateBank(employeeId, formData);
          break;
        case 'employment':
          await employeesApi.updateEmployment(employeeId, formData);
          break;
      }
      await loadEmployee();
      setEditMode(null);
      setFormData({});
    } catch (error) {
      console.error('Failed to save:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleUploadDocument = async () => {
    if (!uploadFile || !uploadDocType) return;

    setIsUploading(true);
    try {
      await employeesApi.uploadDocument(
        employeeId,
        uploadDocType,
        uploadFile,
        uploadDescription || undefined
      );
      await loadDocuments();
      setUploadDialogOpen(false);
      setUploadDocType('');
      setUploadFile(null);
      setUploadDescription('');
    } catch (error) {
      console.error('Failed to upload:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await employeesApi.deleteDocument(employeeId, docId);
      await loadDocuments();
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const handleVerifyDocument = async (docId: string) => {
    try {
      await employeesApi.verifyDocument(employeeId, docId);
      await loadDocuments();
    } catch (error) {
      console.error('Failed to verify:', error);
    }
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center">
            <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <p className="mt-2 text-muted-foreground">Loading employee...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!employee) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-lg font-medium">Employee not found</h2>
          <Button className="mt-4" onClick={() => router.push('/employees')}>
            Back to Employees
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/employees')}>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
            <Avatar className="h-16 w-16">
              <AvatarImage src={employee.profile_photo_path} />
              <AvatarFallback className="text-xl">
                {getInitials(employee.first_name, employee.last_name)}
              </AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-2xl font-bold">
                {employee.first_name} {employee.middle_name} {employee.last_name}
              </h1>
              <div className="flex items-center gap-3 text-muted-foreground">
                <span className="font-mono">{employee.employee_code}</span>
                <span>•</span>
                <span>{employee.employment?.designation_name || 'No Designation'}</span>
                {employee.employment?.current_status && (
                  <>
                    <span>•</span>
                    <Badge
                      variant="secondary"
                      className={statusColors[employee.employment.current_status]}
                    >
                      {statusLabels[employee.employment.current_status]}
                    </Badge>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="personal">Personal Info</TabsTrigger>
            <TabsTrigger value="employment">Employment</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
          </TabsList>

          {/* Personal Info Tab */}
          <TabsContent value="personal" className="space-y-6">
            {/* Basic Info */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Basic Information</CardTitle>
                  <CardDescription>Personal details and demographics</CardDescription>
                </div>
                {editMode !== 'personal' ? (
                  <Button variant="outline" size="sm" onClick={() => startEdit('personal')}>
                    Edit
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={cancelEdit} disabled={isSaving}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={saveChanges} disabled={isSaving}>
                      {isSaving ? 'Saving...' : 'Save'}
                    </Button>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                {editMode === 'personal' ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>First Name</Label>
                      <Input
                        value={formData.first_name as string}
                        onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Middle Name</Label>
                      <Input
                        value={formData.middle_name as string}
                        onChange={(e) => setFormData({ ...formData, middle_name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Last Name</Label>
                      <Input
                        value={formData.last_name as string}
                        onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Date of Birth</Label>
                      <Input
                        type="date"
                        value={formData.date_of_birth as string}
                        onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Gender</Label>
                      <Select
                        value={formData.gender as string}
                        onValueChange={(v) => setFormData({ ...formData, gender: v })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select gender" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Blood Group</Label>
                      <Input
                        value={formData.blood_group as string}
                        onChange={(e) => setFormData({ ...formData, blood_group: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Marital Status</Label>
                      <Select
                        value={formData.marital_status as string}
                        onValueChange={(v) => setFormData({ ...formData, marital_status: v })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="single">Single</SelectItem>
                          <SelectItem value="married">Married</SelectItem>
                          <SelectItem value="divorced">Divorced</SelectItem>
                          <SelectItem value="widowed">Widowed</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Nationality</Label>
                      <Input
                        value={formData.nationality as string}
                        onChange={(e) => setFormData({ ...formData, nationality: e.target.value })}
                      />
                    </div>
                  </div>
                ) : (
                  <dl className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm text-muted-foreground">Full Name</dt>
                      <dd className="font-medium">
                        {employee.first_name} {employee.middle_name} {employee.last_name}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Date of Birth</dt>
                      <dd className="font-medium">
                        {employee.date_of_birth
                          ? new Date(employee.date_of_birth).toLocaleDateString()
                          : '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Gender</dt>
                      <dd className="font-medium capitalize">{employee.gender || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Blood Group</dt>
                      <dd className="font-medium">{employee.blood_group || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Marital Status</dt>
                      <dd className="font-medium capitalize">{employee.marital_status || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Nationality</dt>
                      <dd className="font-medium">{employee.nationality || '—'}</dd>
                    </div>
                  </dl>
                )}
              </CardContent>
            </Card>

            {/* Contact Info */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Contact Information</CardTitle>
                  <CardDescription>Contact details and emergency contacts</CardDescription>
                </div>
                {editMode !== 'contact' ? (
                  <Button variant="outline" size="sm" onClick={() => startEdit('contact')}>
                    Edit
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={cancelEdit} disabled={isSaving}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={saveChanges} disabled={isSaving}>
                      {isSaving ? 'Saving...' : 'Save'}
                    </Button>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                {editMode === 'contact' ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Personal Email</Label>
                        <Input
                          type="email"
                          value={formData.personal_email as string}
                          onChange={(e) => setFormData({ ...formData, personal_email: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Personal Phone</Label>
                        <Input
                          value={formData.personal_phone as string}
                          onChange={(e) => setFormData({ ...formData, personal_phone: e.target.value })}
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label>Emergency Contact Name</Label>
                        <Input
                          value={formData.emergency_contact_name as string}
                          onChange={(e) => setFormData({ ...formData, emergency_contact_name: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Emergency Contact Phone</Label>
                        <Input
                          value={formData.emergency_contact_phone as string}
                          onChange={(e) => setFormData({ ...formData, emergency_contact_phone: e.target.value })}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Relation</Label>
                        <Input
                          value={formData.emergency_contact_relation as string}
                          onChange={(e) => setFormData({ ...formData, emergency_contact_relation: e.target.value })}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <Label>Current Address</Label>
                      <Textarea
                        value={formData.current_address as string}
                        onChange={(e) => setFormData({ ...formData, current_address: e.target.value })}
                        rows={2}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Permanent Address</Label>
                      <Textarea
                        value={formData.permanent_address as string}
                        onChange={(e) => setFormData({ ...formData, permanent_address: e.target.value })}
                        rows={2}
                      />
                    </div>
                  </div>
                ) : (
                  <dl className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <dt className="text-sm text-muted-foreground">Personal Email</dt>
                        <dd className="font-medium">{employee.contact?.personal_email || '—'}</dd>
                      </div>
                      <div>
                        <dt className="text-sm text-muted-foreground">Personal Phone</dt>
                        <dd className="font-medium">{employee.contact?.personal_phone || '—'}</dd>
                      </div>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Emergency Contact</dt>
                      <dd className="font-medium">
                        {employee.contact?.emergency_contact_name
                          ? `${employee.contact.emergency_contact_name} (${employee.contact.emergency_contact_relation || 'N/A'}) - ${employee.contact.emergency_contact_phone || 'N/A'}`
                          : '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Current Address</dt>
                      <dd className="font-medium">{employee.contact?.current_address || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Permanent Address</dt>
                      <dd className="font-medium">{employee.contact?.permanent_address || '—'}</dd>
                    </div>
                  </dl>
                )}
              </CardContent>
            </Card>

            {/* Identity Documents */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Identity Documents</CardTitle>
                  <CardDescription>Government-issued ID numbers</CardDescription>
                </div>
                {editMode !== 'identity' ? (
                  <Button variant="outline" size="sm" onClick={() => startEdit('identity')}>
                    Edit
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={cancelEdit} disabled={isSaving}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={saveChanges} disabled={isSaving}>
                      {isSaving ? 'Saving...' : 'Save'}
                    </Button>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                {editMode === 'identity' ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>PAN Number</Label>
                      <Input
                        value={formData.pan_number as string}
                        onChange={(e) => setFormData({ ...formData, pan_number: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Aadhaar Number</Label>
                      <Input
                        value={formData.aadhaar_number as string}
                        onChange={(e) => setFormData({ ...formData, aadhaar_number: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Passport Number</Label>
                      <Input
                        value={formData.passport_number as string}
                        onChange={(e) => setFormData({ ...formData, passport_number: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Passport Expiry</Label>
                      <Input
                        type="date"
                        value={formData.passport_expiry as string}
                        onChange={(e) => setFormData({ ...formData, passport_expiry: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Driving License</Label>
                      <Input
                        value={formData.driving_license as string}
                        onChange={(e) => setFormData({ ...formData, driving_license: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Voter ID</Label>
                      <Input
                        value={formData.voter_id as string}
                        onChange={(e) => setFormData({ ...formData, voter_id: e.target.value })}
                      />
                    </div>
                  </div>
                ) : (
                  <dl className="grid grid-cols-3 gap-4">
                    <div>
                      <dt className="text-sm text-muted-foreground">PAN Number</dt>
                      <dd className="font-mono font-medium">{employee.identity?.pan_number || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Aadhaar Number</dt>
                      <dd className="font-mono font-medium">{employee.identity?.aadhaar_number || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Passport</dt>
                      <dd className="font-mono font-medium">
                        {employee.identity?.passport_number || '—'}
                        {employee.identity?.passport_expiry && (
                          <span className="ml-1 text-xs text-muted-foreground">
                            (exp: {new Date(employee.identity.passport_expiry).toLocaleDateString()})
                          </span>
                        )}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Driving License</dt>
                      <dd className="font-mono font-medium">{employee.identity?.driving_license || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Voter ID</dt>
                      <dd className="font-mono font-medium">{employee.identity?.voter_id || '—'}</dd>
                    </div>
                  </dl>
                )}
              </CardContent>
            </Card>

            {/* Bank Details */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Bank Details</CardTitle>
                  <CardDescription>Salary account information</CardDescription>
                </div>
                {editMode !== 'bank' ? (
                  <Button variant="outline" size="sm" onClick={() => startEdit('bank')}>
                    Edit
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={cancelEdit} disabled={isSaving}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={saveChanges} disabled={isSaving}>
                      {isSaving ? 'Saving...' : 'Save'}
                    </Button>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                {editMode === 'bank' ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Bank Name</Label>
                      <Input
                        value={formData.bank_name as string}
                        onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Branch Name</Label>
                      <Input
                        value={formData.branch_name as string}
                        onChange={(e) => setFormData({ ...formData, branch_name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Account Number</Label>
                      <Input
                        value={formData.account_number as string}
                        onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>IFSC Code</Label>
                      <Input
                        value={formData.ifsc_code as string}
                        onChange={(e) => setFormData({ ...formData, ifsc_code: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Account Type</Label>
                      <Select
                        value={formData.account_type as string}
                        onValueChange={(v) => setFormData({ ...formData, account_type: v })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="savings">Savings</SelectItem>
                          <SelectItem value="current">Current</SelectItem>
                          <SelectItem value="salary">Salary</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                ) : (
                  <dl className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm text-muted-foreground">Bank Name</dt>
                      <dd className="font-medium">{employee.bank?.bank_name || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Branch</dt>
                      <dd className="font-medium">{employee.bank?.branch_name || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Account Number</dt>
                      <dd className="font-mono font-medium">{employee.bank?.account_number || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">IFSC Code</dt>
                      <dd className="font-mono font-medium">{employee.bank?.ifsc_code || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Account Type</dt>
                      <dd className="font-medium capitalize">{employee.bank?.account_type || '—'}</dd>
                    </div>
                  </dl>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Employment Tab */}
          <TabsContent value="employment" className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Employment Details</CardTitle>
                  <CardDescription>Job role and organizational information</CardDescription>
                </div>
                {editMode !== 'employment' ? (
                  <Button variant="outline" size="sm" onClick={() => startEdit('employment')}>
                    Edit
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={cancelEdit} disabled={isSaving}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={saveChanges} disabled={isSaving}>
                      {isSaving ? 'Saving...' : 'Save'}
                    </Button>
                  </div>
                )}
              </CardHeader>
              <CardContent>
                {editMode === 'employment' ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Department</Label>
                      <Select
                        value={formData.department_id as string}
                        onValueChange={(v) => setFormData({ ...formData, department_id: v })}
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
                      <Label>Designation</Label>
                      <Select
                        value={formData.designation_id as string}
                        onValueChange={(v) => setFormData({ ...formData, designation_id: v })}
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
                    <div className="space-y-2">
                      <Label>Employment Type</Label>
                      <Select
                        value={formData.employment_type as string}
                        onValueChange={(v) => setFormData({ ...formData, employment_type: v })}
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
                      <Label>Status</Label>
                      <Select
                        value={formData.current_status as string}
                        onValueChange={(v) => setFormData({ ...formData, current_status: v })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(statusLabels).map(([value, label]) => (
                            <SelectItem key={value} value={value}>
                              {label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Date of Joining</Label>
                      <Input
                        type="date"
                        value={formData.date_of_joining as string}
                        onChange={(e) => setFormData({ ...formData, date_of_joining: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Probation End Date</Label>
                      <Input
                        type="date"
                        value={formData.probation_end_date as string}
                        onChange={(e) => setFormData({ ...formData, probation_end_date: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Confirmation Date</Label>
                      <Input
                        type="date"
                        value={formData.confirmation_date as string}
                        onChange={(e) => setFormData({ ...formData, confirmation_date: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Notice Period (days)</Label>
                      <Input
                        type="number"
                        value={formData.notice_period_days as number}
                        onChange={(e) => setFormData({ ...formData, notice_period_days: parseInt(e.target.value) })}
                      />
                    </div>
                  </div>
                ) : (
                  <dl className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm text-muted-foreground">Department</dt>
                      <dd className="font-medium">{employee.employment?.department_name || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Designation</dt>
                      <dd className="font-medium">{employee.employment?.designation_name || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Reporting Manager</dt>
                      <dd className="font-medium">{employee.employment?.reporting_manager_name || '—'}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Employment Type</dt>
                      <dd className="font-medium">
                        {employee.employment?.employment_type
                          ? employmentTypeLabels[employee.employment.employment_type]
                          : '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Date of Joining</dt>
                      <dd className="font-medium">
                        {employee.employment?.date_of_joining
                          ? new Date(employee.employment.date_of_joining).toLocaleDateString()
                          : '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Probation End</dt>
                      <dd className="font-medium">
                        {employee.employment?.probation_end_date
                          ? new Date(employee.employment.probation_end_date).toLocaleDateString()
                          : '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Confirmation Date</dt>
                      <dd className="font-medium">
                        {employee.employment?.confirmation_date
                          ? new Date(employee.employment.confirmation_date).toLocaleDateString()
                          : '—'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Notice Period</dt>
                      <dd className="font-medium">{employee.employment?.notice_period_days || 30} days</dd>
                    </div>
                  </dl>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Documents Tab */}
          <TabsContent value="documents" className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Employee Documents</CardTitle>
                  <CardDescription>Uploaded documents and certificates</CardDescription>
                </div>
                <Button onClick={() => setUploadDialogOpen(true)}>
                  <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  Upload Document
                </Button>
              </CardHeader>
              <CardContent>
                {documents.length === 0 ? (
                  <div className="py-8 text-center text-muted-foreground">
                    <svg
                      className="mx-auto h-12 w-12"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    <p className="mt-2">No documents uploaded yet</p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Document</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Size</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Uploaded</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {documents.map((doc) => (
                        <TableRow key={doc.id}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <svg className="h-5 w-5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              <div>
                                <p className="font-medium">{doc.file_name}</p>
                                {doc.description && (
                                  <p className="text-xs text-muted-foreground">{doc.description}</p>
                                )}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="capitalize">
                            {doc.document_type.replace(/_/g, ' ')}
                          </TableCell>
                          <TableCell>{formatFileSize(doc.file_size)}</TableCell>
                          <TableCell>
                            {doc.is_verified ? (
                              <Badge variant="secondary" className="bg-green-100 text-green-800">
                                Verified
                              </Badge>
                            ) : (
                              <Badge variant="secondary">Pending</Badge>
                            )}
                          </TableCell>
                          <TableCell>
                            {new Date(doc.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              {!doc.is_verified && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleVerifyDocument(doc.id)}
                                  title="Verify"
                                >
                                  <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                  </svg>
                                </Button>
                              )}
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleDeleteDocument(doc.id)}
                                title="Delete"
                              >
                                <svg className="h-4 w-4 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Upload Document Dialog */}
      <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
            <DialogDescription>
              Upload a document for {employee.first_name} {employee.last_name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Document Type</Label>
              <Select value={uploadDocType} onValueChange={setUploadDocType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select document type" />
                </SelectTrigger>
                <SelectContent>
                  {documentTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>File</Label>
              <Input
                type="file"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                disabled={isUploading}
              />
            </div>
            <div className="space-y-2">
              <Label>Description (optional)</Label>
              <Input
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
                placeholder="Add a description"
                disabled={isUploading}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setUploadDialogOpen(false)}
              disabled={isUploading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUploadDocument}
              disabled={!uploadFile || !uploadDocType || isUploading}
            >
              {isUploading ? 'Uploading...' : 'Upload'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
