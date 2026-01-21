'use client'

import { useEffect } from 'react'
import { useAuthStore, useApi } from '@/hooks'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import {
  UserCircle,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Building2,
  Briefcase,
  CreditCard,
  Users,
  Edit,
  Shield,
  AlertCircle
} from 'lucide-react'

interface EmployeeContact {
  personal_email?: string
  work_email?: string
  personal_phone?: string
  work_phone?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  emergency_contact_relation?: string
  current_address_line1?: string
  current_address_line2?: string
  current_city?: string
  current_state?: string
  current_pincode?: string
  permanent_address_line1?: string
  permanent_city?: string
  permanent_state?: string
  permanent_pincode?: string
}

interface EmployeeIdentity {
  pan?: string
  aadhaar_masked?: string
  uan?: string
  pf_number?: string
  esi_number?: string
  passport_number?: string
}

interface EmployeeBank {
  bank_name?: string
  branch_name?: string
  account_number_masked?: string
  ifsc_code?: string
  account_type?: string
}

interface EmployeeProfile {
  id: string
  employee_code: string
  first_name: string
  middle_name?: string
  last_name: string
  full_name: string
  date_of_birth?: string
  gender?: string
  marital_status?: string
  nationality?: string
  blood_group?: string
  profile_photo_url?: string
  department_id?: string
  department_name?: string
  designation_id?: string
  designation_name?: string
  reporting_to?: string
  reporting_to_name?: string
  employment_status: string
  employment_type: string
  date_of_joining: string
  date_of_leaving?: string
  probation_end_date?: string
  confirmation_date?: string
  notice_period_days?: number
  contact?: EmployeeContact
  identity?: EmployeeIdentity
  bank?: EmployeeBank
}

export default function MyProfilePage() {
  const { user } = useAuthStore()
  const { data: profile, isLoading, error, get } = useApi<EmployeeProfile>()

  useEffect(() => {
    get('/employees/me')
  }, [get])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="My Profile"
          description="View and manage your personal information"
          icon={UserCircle}
        />
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row items-start gap-6">
              <Skeleton className="w-24 h-24 rounded-full" />
              <div className="flex-1 space-y-4">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-6 w-32" />
                <div className="flex gap-4">
                  <Skeleton className="h-4 w-40" />
                  <Skeleton className="h-4 w-32" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="My Profile"
          description="View and manage your personal information"
          icon={UserCircle}
        />
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Unable to load profile</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={() => get('/employees/me')}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="My Profile"
          description="View and manage your personal information"
          icon={UserCircle}
        />
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <UserCircle className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Employee Profile Found</h3>
              <p className="text-muted-foreground">Your user account is not linked to an employee record. Please contact HR.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const formatEmploymentType = (type: string) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Profile"
        description="View and manage your personal information"
        icon={UserCircle}
        actions={
          <Button>
            <Edit className="h-4 w-4 mr-2" />
            Edit Profile
          </Button>
        }
      />

      {/* Profile Header */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-start gap-6">
            <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center">
              {profile.profile_photo_url ? (
                <img src={profile.profile_photo_url} alt={profile.full_name} className="w-24 h-24 rounded-full object-cover" />
              ) : (
                <span className="text-3xl font-bold text-primary">
                  {profile.full_name.split(' ').map(n => n[0]).join('')}
                </span>
              )}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl font-bold">{profile.full_name}</h2>
                <Badge>{formatEmploymentType(profile.employment_type)}</Badge>
                <Badge variant={profile.employment_status === 'active' ? 'default' : 'secondary'}>
                  {profile.employment_status}
                </Badge>
              </div>
              <p className="text-lg text-muted-foreground">{profile.designation_name || 'No designation'}</p>
              <div className="flex flex-wrap gap-4 mt-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Mail className="h-4 w-4" /> {profile.contact?.work_email || user?.email}
                </span>
                {profile.contact?.work_phone && (
                  <span className="flex items-center gap-1">
                    <Phone className="h-4 w-4" /> {profile.contact.work_phone}
                  </span>
                )}
                {profile.department_name && (
                  <span className="flex items-center gap-1">
                    <Building2 className="h-4 w-4" /> {profile.department_name}
                  </span>
                )}
                {profile.contact?.current_city && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" /> {profile.contact.current_city}, {profile.contact.current_state}
                  </span>
                )}
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Employee ID</p>
              <p className="text-xl font-bold">{profile.employee_code}</p>
              <p className="text-sm text-muted-foreground mt-2">Joined</p>
              <p className="font-medium">{new Date(profile.date_of_joining).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="personal">
        <TabsList>
          <TabsTrigger value="personal">Personal Info</TabsTrigger>
          <TabsTrigger value="employment">Employment</TabsTrigger>
          <TabsTrigger value="bank">Bank & Statutory</TabsTrigger>
          <TabsTrigger value="emergency">Emergency Contact</TabsTrigger>
        </TabsList>

        <TabsContent value="personal" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Date of Birth</span>
                  <span>{profile.date_of_birth ? new Date(profile.date_of_birth).toLocaleDateString('en-IN') : '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Gender</span>
                  <span>{profile.gender || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Blood Group</span>
                  <span>{profile.blood_group || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Marital Status</span>
                  <span>{profile.marital_status || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Nationality</span>
                  <span>{profile.nationality || 'Indian'}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Contact & Address</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Personal Email</span>
                  <span>{profile.contact?.personal_email || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Personal Phone</span>
                  <span>{profile.contact?.personal_phone || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Address</span>
                  <span className="text-right">
                    {profile.contact?.current_address_line1 || '-'}
                    {profile.contact?.current_address_line2 && <br />}
                    {profile.contact?.current_address_line2}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">City</span>
                  <span>{profile.contact?.current_city || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">State</span>
                  <span>{profile.contact?.current_state || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">PIN Code</span>
                  <span>{profile.contact?.current_pincode || '-'}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="employment" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Employment Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Employee ID</span>
                    <span className="font-medium">{profile.employee_code}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Department</span>
                    <span>{profile.department_name || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Designation</span>
                    <span>{profile.designation_name || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Employment Type</span>
                    <span>{formatEmploymentType(profile.employment_type)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Status</span>
                    <Badge variant={profile.employment_status === 'active' ? 'default' : 'secondary'}>
                      {profile.employment_status}
                    </Badge>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Reporting To</span>
                    <span>{profile.reporting_to_name || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Join Date</span>
                    <span>{new Date(profile.date_of_joining).toLocaleDateString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Probation End</span>
                    <span>{profile.probation_end_date ? new Date(profile.probation_end_date).toLocaleDateString('en-IN') : '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Confirmation Date</span>
                    <span>{profile.confirmation_date ? new Date(profile.confirmation_date).toLocaleDateString('en-IN') : '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Notice Period</span>
                    <span>{profile.notice_period_days || 30} days</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bank" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <CreditCard className="h-4 w-4" /> Bank Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Bank Name</span>
                  <span>{profile.bank?.bank_name || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Branch</span>
                  <span>{profile.bank?.branch_name || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Account Number</span>
                  <span>{profile.bank?.account_number_masked || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">IFSC Code</span>
                  <span>{profile.bank?.ifsc_code || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Account Type</span>
                  <span>{profile.bank?.account_type || '-'}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Shield className="h-4 w-4" /> Statutory Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">PAN</span>
                  <span>{profile.identity?.pan || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Aadhar</span>
                  <span>{profile.identity?.aadhaar_masked || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">UAN (PF)</span>
                  <span>{profile.identity?.uan || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">PF Number</span>
                  <span>{profile.identity?.pf_number || '-'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">ESI Number</span>
                  <span>{profile.identity?.esi_number || '-'}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="emergency" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Users className="h-4 w-4" /> Emergency Contact
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Name</span>
                <span>{profile.contact?.emergency_contact_name || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Relationship</span>
                <span>{profile.contact?.emergency_contact_relation || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Phone</span>
                <span>{profile.contact?.emergency_contact_phone || '-'}</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
