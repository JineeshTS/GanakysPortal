"use client"

import * as React from "react"
import { PageHeader } from "@/components/layout/page-header"
import { ConfigForm, ConfigFormField, ConfigFormRow, ConfigToggle, INDIA_VALIDATION_PATTERNS, getIndiaFieldError } from "@/components/settings/ConfigForm"
import { SettingsSection } from "@/components/settings/SettingsCard"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FormSelect, FormTextarea } from "@/components/forms/form-field"
import {
  Building2,
  Upload,
  Plus,
  Trash2,
  MapPin,
  Calendar,
  Save,
  Loader2
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

interface CompanyDetails {
  name: string
  legalName: string
  gstin: string
  pan: string
  tan: string
  cin: string
  website: string
  email: string
  phone: string
  logoUrl: string
}

interface Address {
  id: string
  type: 'registered' | 'corporate' | 'branch'
  name: string
  line1: string
  line2: string
  city: string
  state: string
  pincode: string
  country: string
}

interface FinancialYear {
  startMonth: number
  startDay: number
  currentYear: string
}

interface Branch {
  id: string
  code: string
  name: string
  gstin: string
  pfCode: string
  esiCode: string
  ptState: string
  address: string
  isActive: boolean
}

// ============================================================================
// Initial Data
// ============================================================================

const INDIAN_STATES = [
  { value: 'AN', label: 'Andaman and Nicobar Islands' },
  { value: 'AP', label: 'Andhra Pradesh' },
  { value: 'AR', label: 'Arunachal Pradesh' },
  { value: 'AS', label: 'Assam' },
  { value: 'BR', label: 'Bihar' },
  { value: 'CH', label: 'Chandigarh' },
  { value: 'CT', label: 'Chhattisgarh' },
  { value: 'DL', label: 'Delhi' },
  { value: 'GA', label: 'Goa' },
  { value: 'GJ', label: 'Gujarat' },
  { value: 'HR', label: 'Haryana' },
  { value: 'HP', label: 'Himachal Pradesh' },
  { value: 'JK', label: 'Jammu and Kashmir' },
  { value: 'JH', label: 'Jharkhand' },
  { value: 'KA', label: 'Karnataka' },
  { value: 'KL', label: 'Kerala' },
  { value: 'LA', label: 'Ladakh' },
  { value: 'MP', label: 'Madhya Pradesh' },
  { value: 'MH', label: 'Maharashtra' },
  { value: 'MN', label: 'Manipur' },
  { value: 'ML', label: 'Meghalaya' },
  { value: 'MZ', label: 'Mizoram' },
  { value: 'NL', label: 'Nagaland' },
  { value: 'OR', label: 'Odisha' },
  { value: 'PY', label: 'Puducherry' },
  { value: 'PB', label: 'Punjab' },
  { value: 'RJ', label: 'Rajasthan' },
  { value: 'SK', label: 'Sikkim' },
  { value: 'TN', label: 'Tamil Nadu' },
  { value: 'TG', label: 'Telangana' },
  { value: 'TR', label: 'Tripura' },
  { value: 'UP', label: 'Uttar Pradesh' },
  { value: 'UK', label: 'Uttarakhand' },
  { value: 'WB', label: 'West Bengal' }
]

const INITIAL_COMPANY: CompanyDetails = {
  name: 'GanaPortal Technologies',
  legalName: 'GanaPortal Technologies Private Limited',
  gstin: '29AABCG1234M1Z5',
  pan: 'AABCG1234M',
  tan: 'BLRG12345A',
  cin: 'U72200KA2020PTC123456',
  website: 'https://ganaportal.in',
  email: 'contact@ganaportal.in',
  phone: '+91 80 4567 8901',
  logoUrl: ''
}

const INITIAL_ADDRESS: Address = {
  id: 'addr-1',
  type: 'registered',
  name: 'Registered Office',
  line1: '123, 4th Floor, Tech Park',
  line2: 'Electronic City Phase 1',
  city: 'Bangalore',
  state: 'KA',
  pincode: '560100',
  country: 'India'
}

const INITIAL_BRANCHES: Branch[] = [
  {
    id: 'branch-1',
    code: 'HO',
    name: 'Head Office - Bangalore',
    gstin: '29AABCG1234M1Z5',
    pfCode: 'KA/BLR/1234567/000/0000001',
    esiCode: '12345678901234567',
    ptState: 'KA',
    address: 'Electronic City, Bangalore',
    isActive: true
  },
  {
    id: 'branch-2',
    code: 'MUM',
    name: 'Mumbai Office',
    gstin: '27AABCG1234M1Z5',
    pfCode: 'MH/MUM/1234567/000/0000002',
    esiCode: '12345678901234568',
    ptState: 'MH',
    address: 'BKC, Mumbai',
    isActive: true
  }
]

// ============================================================================
// Company Settings Page
// ============================================================================

export default function CompanySettingsPage() {
  const [company, setCompany] = React.useState<CompanyDetails>(INITIAL_COMPANY)
  const [addresses, setAddresses] = React.useState<Address[]>([INITIAL_ADDRESS])
  const [branches, setBranches] = React.useState<Branch[]>(INITIAL_BRANCHES)
  const [financialYear, setFinancialYear] = React.useState<FinancialYear>({
    startMonth: 4, // April
    startDay: 1,
    currentYear: '2024-25'
  })

  const [isLoading, setIsLoading] = React.useState(false)
  const [isDirty, setIsDirty] = React.useState(false)
  const [errors, setErrors] = React.useState<Record<string, string>>({})

  // Handle company field change
  const handleCompanyChange = (field: keyof CompanyDetails, value: string) => {
    setCompany(prev => ({ ...prev, [field]: value }))
    setIsDirty(true)

    // Validate India-specific fields
    if (field === 'gstin' && value) {
      const error = getIndiaFieldError('GSTIN', value)
      setErrors(prev => ({ ...prev, gstin: error || '' }))
    }
    if (field === 'pan' && value) {
      const error = getIndiaFieldError('PAN', value)
      setErrors(prev => ({ ...prev, pan: error || '' }))
    }
    if (field === 'tan' && value) {
      const error = getIndiaFieldError('TAN', value)
      setErrors(prev => ({ ...prev, tan: error || '' }))
    }
  }

  // Handle logo upload
  const handleLogoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setCompany(prev => ({ ...prev, logoUrl: reader.result as string }))
        setIsDirty(true)
      }
      reader.readAsDataURL(file)
    }
  }

  // Handle address change
  const handleAddressChange = (id: string, field: keyof Address, value: string) => {
    setAddresses(prev => prev.map(addr =>
      addr.id === id ? { ...addr, [field]: value } : addr
    ))
    setIsDirty(true)
  }

  // Add new branch
  const handleAddBranch = () => {
    const newBranch: Branch = {
      id: `branch-${Date.now()}`,
      code: '',
      name: '',
      gstin: '',
      pfCode: '',
      esiCode: '',
      ptState: '',
      address: '',
      isActive: true
    }
    setBranches(prev => [...prev, newBranch])
    setIsDirty(true)
  }

  // Handle branch change
  const handleBranchChange = (id: string, field: keyof Branch, value: string | boolean) => {
    setBranches(prev => prev.map(branch =>
      branch.id === id ? { ...branch, [field]: value } : branch
    ))
    setIsDirty(true)
  }

  // Delete branch
  const handleDeleteBranch = (id: string) => {
    if (branches.length <= 1) return
    setBranches(prev => prev.filter(b => b.id !== id))
    setIsDirty(true)
  }

  // Save all settings
  const handleSave = async () => {
    setIsLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    setIsLoading(false)
    setIsDirty(false)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Company Settings"
        description="Manage your company details, addresses, and branches"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings", href: "/settings" },
          { label: "Company Settings" }
        ]}
        actions={
          <Button onClick={handleSave} disabled={isLoading || !isDirty}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save All Changes
              </>
            )}
          </Button>
        }
      />

      <Tabs defaultValue="details" className="space-y-6">
        <TabsList>
          <TabsTrigger value="details">Company Details</TabsTrigger>
          <TabsTrigger value="addresses">Addresses</TabsTrigger>
          <TabsTrigger value="branches">Branches</TabsTrigger>
          <TabsTrigger value="financial">Financial Year</TabsTrigger>
        </TabsList>

        {/* Company Details Tab */}
        <TabsContent value="details" className="space-y-6">
          {/* Logo Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Company Logo</CardTitle>
              <CardDescription>Upload your company logo for invoices and payslips</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6">
                <div className="h-24 w-24 rounded-lg border-2 border-dashed border-muted-foreground/25 flex items-center justify-center overflow-hidden bg-muted">
                  {company.logoUrl ? (
                    <img src={company.logoUrl} alt="Company Logo" className="h-full w-full object-contain" />
                  ) : (
                    <Building2 className="h-8 w-8 text-muted-foreground" />
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="logo-upload" className="cursor-pointer">
                    <div className="flex items-center gap-2 text-sm text-primary hover:underline">
                      <Upload className="h-4 w-4" />
                      Upload Logo
                    </div>
                  </Label>
                  <input
                    id="logo-upload"
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleLogoUpload}
                  />
                  <p className="text-xs text-muted-foreground">PNG, JPG up to 2MB. Recommended: 200x200px</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Basic Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <ConfigFormRow columns={2}>
                <div className="space-y-2">
                  <Label htmlFor="name">Company Name *</Label>
                  <Input
                    id="name"
                    value={company.name}
                    onChange={(e) => handleCompanyChange('name', e.target.value)}
                    placeholder="Display name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="legalName">Legal Name *</Label>
                  <Input
                    id="legalName"
                    value={company.legalName}
                    onChange={(e) => handleCompanyChange('legalName', e.target.value)}
                    placeholder="As per registration"
                  />
                </div>
              </ConfigFormRow>

              <ConfigFormRow columns={2}>
                <div className="space-y-2">
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={company.email}
                    onChange={(e) => handleCompanyChange('email', e.target.value)}
                    placeholder="contact@company.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone *</Label>
                  <Input
                    id="phone"
                    value={company.phone}
                    onChange={(e) => handleCompanyChange('phone', e.target.value)}
                    placeholder="+91 80 1234 5678"
                  />
                </div>
              </ConfigFormRow>

              <div className="space-y-2">
                <Label htmlFor="website">Website</Label>
                <Input
                  id="website"
                  value={company.website}
                  onChange={(e) => handleCompanyChange('website', e.target.value)}
                  placeholder="https://company.com"
                />
              </div>
            </CardContent>
          </Card>

          {/* Statutory Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Statutory Details</CardTitle>
              <CardDescription>Tax and registration identifiers</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ConfigFormRow columns={2}>
                <ConfigFormField
                  label="GSTIN"
                  name="gstin"
                  value={company.gstin}
                  onChange={(e) => handleCompanyChange('gstin', e.target.value.toUpperCase())}
                  indiaValidation="GSTIN"
                  error={errors.gstin}
                  placeholder="29AABCG1234M1Z5"
                  hint="15-character GST Identification Number"
                  required
                />
                <ConfigFormField
                  label="PAN"
                  name="pan"
                  value={company.pan}
                  onChange={(e) => handleCompanyChange('pan', e.target.value.toUpperCase())}
                  indiaValidation="PAN"
                  error={errors.pan}
                  placeholder="AABCG1234M"
                  hint="10-character Permanent Account Number"
                  required
                />
              </ConfigFormRow>

              <ConfigFormRow columns={2}>
                <ConfigFormField
                  label="TAN"
                  name="tan"
                  value={company.tan}
                  onChange={(e) => handleCompanyChange('tan', e.target.value.toUpperCase())}
                  indiaValidation="TAN"
                  error={errors.tan}
                  placeholder="BLRG12345A"
                  hint="10-character Tax Deduction Account Number"
                  required
                />
                <div className="space-y-2">
                  <Label htmlFor="cin">CIN</Label>
                  <Input
                    id="cin"
                    value={company.cin}
                    onChange={(e) => handleCompanyChange('cin', e.target.value.toUpperCase())}
                    placeholder="U72200KA2020PTC123456"
                  />
                  <p className="text-sm text-muted-foreground">Corporate Identification Number</p>
                </div>
              </ConfigFormRow>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Addresses Tab */}
        <TabsContent value="addresses" className="space-y-6">
          {addresses.map((address) => (
            <Card key={address.id}>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  {address.name}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <ConfigFormRow columns={2}>
                  <div className="space-y-2">
                    <Label>Address Line 1 *</Label>
                    <Input
                      value={address.line1}
                      onChange={(e) => handleAddressChange(address.id, 'line1', e.target.value)}
                      placeholder="Building, Street"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Address Line 2</Label>
                    <Input
                      value={address.line2}
                      onChange={(e) => handleAddressChange(address.id, 'line2', e.target.value)}
                      placeholder="Area, Landmark"
                    />
                  </div>
                </ConfigFormRow>

                <ConfigFormRow columns={4}>
                  <div className="space-y-2">
                    <Label>City *</Label>
                    <Input
                      value={address.city}
                      onChange={(e) => handleAddressChange(address.id, 'city', e.target.value)}
                    />
                  </div>
                  <FormSelect
                    label="State *"
                    name="state"
                    options={INDIAN_STATES}
                    value={address.state}
                    onChange={(e) => handleAddressChange(address.id, 'state', e.target.value)}
                  />
                  <div className="space-y-2">
                    <Label>PIN Code *</Label>
                    <Input
                      value={address.pincode}
                      onChange={(e) => handleAddressChange(address.id, 'pincode', e.target.value)}
                      maxLength={6}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Country</Label>
                    <Input value="India" disabled />
                  </div>
                </ConfigFormRow>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Branches Tab */}
        <TabsContent value="branches" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold">Branch Offices</h3>
              <p className="text-sm text-muted-foreground">Manage multiple office locations with separate compliance codes</p>
            </div>
            <Button onClick={handleAddBranch}>
              <Plus className="mr-2 h-4 w-4" />
              Add Branch
            </Button>
          </div>

          {branches.map((branch, index) => (
            <Card key={branch.id}>
              <CardHeader className="flex flex-row items-start justify-between space-y-0">
                <div>
                  <CardTitle className="text-base">
                    {branch.name || `Branch ${index + 1}`}
                  </CardTitle>
                  <CardDescription>{branch.code || 'No code assigned'}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <ConfigToggle
                    label=""
                    checked={branch.isActive}
                    onChange={(checked) => handleBranchChange(branch.id, 'isActive', checked)}
                  />
                  {branches.length > 1 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteBranch(branch.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <ConfigFormRow columns={3}>
                  <div className="space-y-2">
                    <Label>Branch Code *</Label>
                    <Input
                      value={branch.code}
                      onChange={(e) => handleBranchChange(branch.id, 'code', e.target.value.toUpperCase())}
                      placeholder="HO, MUM, DEL"
                      maxLength={5}
                    />
                  </div>
                  <div className="col-span-2 space-y-2">
                    <Label>Branch Name *</Label>
                    <Input
                      value={branch.name}
                      onChange={(e) => handleBranchChange(branch.id, 'name', e.target.value)}
                      placeholder="Head Office - Bangalore"
                    />
                  </div>
                </ConfigFormRow>

                <ConfigFormRow columns={2}>
                  <ConfigFormField
                    label="GSTIN"
                    name={`gstin-${branch.id}`}
                    value={branch.gstin}
                    onChange={(e) => handleBranchChange(branch.id, 'gstin', e.target.value.toUpperCase())}
                    indiaValidation="GSTIN"
                    placeholder="State-specific GSTIN"
                  />
                  <FormSelect
                    label="PT State"
                    name={`ptState-${branch.id}`}
                    options={INDIAN_STATES}
                    value={branch.ptState}
                    onChange={(e) => handleBranchChange(branch.id, 'ptState', e.target.value)}
                    placeholder="Select state"
                  />
                </ConfigFormRow>

                <ConfigFormRow columns={2}>
                  <div className="space-y-2">
                    <Label>PF Establishment Code</Label>
                    <Input
                      value={branch.pfCode}
                      onChange={(e) => handleBranchChange(branch.id, 'pfCode', e.target.value.toUpperCase())}
                      placeholder="KA/BLR/1234567/000/0000001"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>ESIC Code</Label>
                    <Input
                      value={branch.esiCode}
                      onChange={(e) => handleBranchChange(branch.id, 'esiCode', e.target.value)}
                      placeholder="17-digit ESIC number"
                      maxLength={17}
                    />
                  </div>
                </ConfigFormRow>

                <div className="space-y-2">
                  <Label>Address</Label>
                  <Input
                    value={branch.address}
                    onChange={(e) => handleBranchChange(branch.id, 'address', e.target.value)}
                    placeholder="Full address"
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Financial Year Tab */}
        <TabsContent value="financial" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Financial Year Settings
              </CardTitle>
              <CardDescription>
                Configure your organization's financial year for payroll and compliance
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ConfigFormRow columns={3}>
                <FormSelect
                  label="Start Month"
                  name="startMonth"
                  options={[
                    { value: '1', label: 'January' },
                    { value: '2', label: 'February' },
                    { value: '3', label: 'March' },
                    { value: '4', label: 'April' },
                    { value: '5', label: 'May' },
                    { value: '6', label: 'June' },
                    { value: '7', label: 'July' },
                    { value: '8', label: 'August' },
                    { value: '9', label: 'September' },
                    { value: '10', label: 'October' },
                    { value: '11', label: 'November' },
                    { value: '12', label: 'December' }
                  ]}
                  value={String(financialYear.startMonth)}
                  onChange={(e) => {
                    setFinancialYear(prev => ({ ...prev, startMonth: parseInt(e.target.value) }))
                    setIsDirty(true)
                  }}
                  hint="Standard Indian FY starts in April"
                />
                <div className="space-y-2">
                  <Label>Start Day</Label>
                  <Input
                    type="number"
                    min={1}
                    max={28}
                    value={financialYear.startDay}
                    onChange={(e) => {
                      setFinancialYear(prev => ({ ...prev, startDay: parseInt(e.target.value) }))
                      setIsDirty(true)
                    }}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Current Financial Year</Label>
                  <Input value={financialYear.currentYear} disabled />
                  <p className="text-sm text-muted-foreground">Auto-calculated based on settings</p>
                </div>
              </ConfigFormRow>

              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">Important Notes</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>- Standard Indian Financial Year: April 1 to March 31</li>
                  <li>- This setting affects Form 16, PF returns, and other compliance reports</li>
                  <li>- Changing the financial year mid-year may affect existing calculations</li>
                  <li>- Contact support before making changes to an active financial year</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
