"use client"

import * as React from "react"
import { useSearchParams } from "next/navigation"
import { PageHeader } from "@/components/layout/page-header"
import { ConfigForm, ConfigFormField, ConfigFormRow, ConfigToggle } from "@/components/settings/ConfigForm"
import { SettingsSection } from "@/components/settings/SettingsCard"
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
import { FormSelect } from "@/components/forms/form-field"
import {
  Wallet,
  Plus,
  Edit,
  Trash2,
  TrendingUp,
  TrendingDown,
  IndianRupee,
  Calculator,
  Landmark,
  FileText,
  Save,
  Loader2,
  AlertCircle,
  Info
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

interface SalaryComponent {
  id: string
  code: string
  name: string
  type: 'earning' | 'deduction'
  calculationType: 'fixed' | 'percentage' | 'formula'
  percentageOf?: string
  percentage?: number
  isStatutory: boolean
  isTaxable: boolean
  affectsPF: boolean
  affectsESI: boolean
  isActive: boolean
  description?: string
}

interface PFSettings {
  employeeContribution: number
  employerContribution: number
  employerEPS: number
  adminCharges: number
  wageCeiling: number
  restrictToBasic: boolean
  includeDA: boolean
  includeSpecialAllowance: boolean
  optOutAllowed: boolean
  optOutWageLimit: number
}

interface ESISettings {
  employeeContribution: number
  employerContribution: number
  wageCeiling: number
  roundOff: 'nearest' | 'up' | 'down'
}

interface PTSettings {
  state: string
  slabs: { from: number; to: number; amount: number }[]
}

interface TDSSettings {
  defaultRegime: 'old' | 'new'
  allowEmployeeChoice: boolean
  standardDeduction: number
  cess: number
}

interface PaySchedule {
  payDay: number
  processingDay: number
  attendanceCutoff: number
  arrearProcessing: 'current' | 'next'
}

// ============================================================================
// Initial Data
// ============================================================================

const INITIAL_COMPONENTS: SalaryComponent[] = [
  {
    id: 'comp-1',
    code: 'BASIC',
    name: 'Basic Salary',
    type: 'earning',
    calculationType: 'percentage',
    percentageOf: 'CTC',
    percentage: 40,
    isStatutory: false,
    isTaxable: true,
    affectsPF: true,
    affectsESI: true,
    isActive: true,
    description: 'Base salary component, typically 40-50% of CTC'
  },
  {
    id: 'comp-2',
    code: 'HRA',
    name: 'House Rent Allowance',
    type: 'earning',
    calculationType: 'percentage',
    percentageOf: 'BASIC',
    percentage: 50,
    isStatutory: false,
    isTaxable: true,
    affectsPF: false,
    affectsESI: true,
    isActive: true,
    description: '40-50% of Basic, tax exempt under section 10(13A)'
  },
  {
    id: 'comp-3',
    code: 'DA',
    name: 'Dearness Allowance',
    type: 'earning',
    calculationType: 'percentage',
    percentageOf: 'BASIC',
    percentage: 0,
    isStatutory: false,
    isTaxable: true,
    affectsPF: true,
    affectsESI: true,
    isActive: false,
    description: 'Cost of living adjustment'
  },
  {
    id: 'comp-4',
    code: 'SPECIAL',
    name: 'Special Allowance',
    type: 'earning',
    calculationType: 'fixed',
    isStatutory: false,
    isTaxable: true,
    affectsPF: false,
    affectsESI: true,
    isActive: true,
    description: 'Flexible component to balance CTC'
  },
  {
    id: 'comp-5',
    code: 'CONVEYANCE',
    name: 'Conveyance Allowance',
    type: 'earning',
    calculationType: 'fixed',
    isStatutory: false,
    isTaxable: true,
    affectsPF: false,
    affectsESI: true,
    isActive: true,
    description: 'Transport allowance for commuting'
  },
  {
    id: 'comp-6',
    code: 'PF_EE',
    name: 'Provident Fund (Employee)',
    type: 'deduction',
    calculationType: 'percentage',
    percentageOf: 'PF_WAGES',
    percentage: 12,
    isStatutory: true,
    isTaxable: false,
    affectsPF: false,
    affectsESI: false,
    isActive: true,
    description: 'Employee contribution to EPF'
  },
  {
    id: 'comp-7',
    code: 'ESI_EE',
    name: 'ESI (Employee)',
    type: 'deduction',
    calculationType: 'percentage',
    percentageOf: 'GROSS',
    percentage: 0.75,
    isStatutory: true,
    isTaxable: false,
    affectsPF: false,
    affectsESI: false,
    isActive: true,
    description: 'Employee contribution to ESIC'
  },
  {
    id: 'comp-8',
    code: 'PT',
    name: 'Professional Tax',
    type: 'deduction',
    calculationType: 'formula',
    isStatutory: true,
    isTaxable: false,
    affectsPF: false,
    affectsESI: false,
    isActive: true,
    description: 'State-wise professional tax'
  },
  {
    id: 'comp-9',
    code: 'TDS',
    name: 'Tax Deducted at Source',
    type: 'deduction',
    calculationType: 'formula',
    isStatutory: true,
    isTaxable: false,
    affectsPF: false,
    affectsESI: false,
    isActive: true,
    description: 'Income tax deduction'
  }
]

const INITIAL_PF_SETTINGS: PFSettings = {
  employeeContribution: 12,
  employerContribution: 12,
  employerEPS: 8.33,
  adminCharges: 0.5,
  wageCeiling: 15000,
  restrictToBasic: false,
  includeDA: true,
  includeSpecialAllowance: false,
  optOutAllowed: true,
  optOutWageLimit: 15000
}

const INITIAL_ESI_SETTINGS: ESISettings = {
  employeeContribution: 0.75,
  employerContribution: 3.25,
  wageCeiling: 21000,
  roundOff: 'nearest'
}

const INITIAL_PT_SETTINGS: PTSettings = {
  state: 'KA',
  slabs: [
    { from: 0, to: 15000, amount: 0 },
    { from: 15001, to: 25000, amount: 200 }
  ]
}

const INITIAL_TDS_SETTINGS: TDSSettings = {
  defaultRegime: 'new',
  allowEmployeeChoice: true,
  standardDeduction: 50000,
  cess: 4
}

const INITIAL_PAY_SCHEDULE: PaySchedule = {
  payDay: 1,
  processingDay: 28,
  attendanceCutoff: 25,
  arrearProcessing: 'next'
}

const INDIAN_STATES_PT = [
  { value: 'AN', label: 'Andhra Pradesh' },
  { value: 'AS', label: 'Assam' },
  { value: 'BR', label: 'Bihar' },
  { value: 'GJ', label: 'Gujarat' },
  { value: 'KA', label: 'Karnataka' },
  { value: 'KL', label: 'Kerala' },
  { value: 'MP', label: 'Madhya Pradesh' },
  { value: 'MH', label: 'Maharashtra' },
  { value: 'MN', label: 'Manipur' },
  { value: 'ML', label: 'Meghalaya' },
  { value: 'MZ', label: 'Mizoram' },
  { value: 'OR', label: 'Odisha' },
  { value: 'PB', label: 'Punjab' },
  { value: 'SK', label: 'Sikkim' },
  { value: 'TN', label: 'Tamil Nadu' },
  { value: 'TG', label: 'Telangana' },
  { value: 'TR', label: 'Tripura' },
  { value: 'WB', label: 'West Bengal' }
]

// ============================================================================
// Payroll Configuration Page
// ============================================================================

export default function PayrollConfigPage() {
  const searchParams = useSearchParams()
  const defaultTab = searchParams.get('tab') || 'components'

  const [components, setComponents] = React.useState<SalaryComponent[]>(INITIAL_COMPONENTS)
  const [pfSettings, setPfSettings] = React.useState<PFSettings>(INITIAL_PF_SETTINGS)
  const [esiSettings, setEsiSettings] = React.useState<ESISettings>(INITIAL_ESI_SETTINGS)
  const [ptSettings, setPtSettings] = React.useState<PTSettings>(INITIAL_PT_SETTINGS)
  const [tdsSettings, setTdsSettings] = React.useState<TDSSettings>(INITIAL_TDS_SETTINGS)
  const [paySchedule, setPaySchedule] = React.useState<PaySchedule>(INITIAL_PAY_SCHEDULE)

  const [isLoading, setIsLoading] = React.useState(false)
  const [isDirty, setIsDirty] = React.useState(false)
  const [isComponentDialogOpen, setIsComponentDialogOpen] = React.useState(false)
  const [editingComponent, setEditingComponent] = React.useState<SalaryComponent | null>(null)

  // New component form state
  const [newComponent, setNewComponent] = React.useState<Partial<SalaryComponent>>({
    type: 'earning',
    calculationType: 'fixed',
    isStatutory: false,
    isTaxable: true,
    affectsPF: false,
    affectsESI: true,
    isActive: true
  })

  // Filter components by type
  const earnings = components.filter(c => c.type === 'earning')
  const deductions = components.filter(c => c.type === 'deduction')

  // Handle component actions
  const handleAddComponent = () => {
    setEditingComponent(null)
    setNewComponent({
      type: 'earning',
      calculationType: 'fixed',
      isStatutory: false,
      isTaxable: true,
      affectsPF: false,
      affectsESI: true,
      isActive: true
    })
    setIsComponentDialogOpen(true)
  }

  const handleEditComponent = (component: SalaryComponent) => {
    setEditingComponent(component)
    setNewComponent(component)
    setIsComponentDialogOpen(true)
  }

  const handleSaveComponent = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 500))

    if (editingComponent) {
      setComponents(prev => prev.map(c =>
        c.id === editingComponent.id ? { ...c, ...newComponent } as SalaryComponent : c
      ))
    } else {
      const component: SalaryComponent = {
        id: `comp-${Date.now()}`,
        code: newComponent.code || '',
        name: newComponent.name || '',
        type: newComponent.type || 'earning',
        calculationType: newComponent.calculationType || 'fixed',
        percentageOf: newComponent.percentageOf,
        percentage: newComponent.percentage,
        isStatutory: newComponent.isStatutory || false,
        isTaxable: newComponent.isTaxable || false,
        affectsPF: newComponent.affectsPF || false,
        affectsESI: newComponent.affectsESI || false,
        isActive: newComponent.isActive || true,
        description: newComponent.description
      }
      setComponents(prev => [...prev, component])
    }

    setIsLoading(false)
    setIsComponentDialogOpen(false)
    setIsDirty(true)
  }

  const handleDeleteComponent = (id: string) => {
    setComponents(prev => prev.filter(c => c.id !== id))
    setIsDirty(true)
  }

  const handleToggleComponent = (id: string) => {
    setComponents(prev => prev.map(c =>
      c.id === id ? { ...c, isActive: !c.isActive } : c
    ))
    setIsDirty(true)
  }

  // Save all settings
  const handleSave = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1500))
    setIsLoading(false)
    setIsDirty(false)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Payroll Configuration"
        description="Configure salary components and statutory compliance settings"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings", href: "/settings" },
          { label: "Payroll Configuration" }
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
                Save Changes
              </>
            )}
          </Button>
        }
      />

      <Tabs defaultValue={defaultTab} className="space-y-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="components">Salary Components</TabsTrigger>
          <TabsTrigger value="pf">PF Settings</TabsTrigger>
          <TabsTrigger value="esi">ESI Settings</TabsTrigger>
          <TabsTrigger value="pt">PT Settings</TabsTrigger>
          <TabsTrigger value="tds">TDS Settings</TabsTrigger>
          <TabsTrigger value="schedule">Pay Schedule</TabsTrigger>
        </TabsList>

        {/* Salary Components Tab */}
        <TabsContent value="components" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold">Salary Components</h3>
              <p className="text-sm text-muted-foreground">Manage earnings and deductions</p>
            </div>
            <Button onClick={handleAddComponent}>
              <Plus className="mr-2 h-4 w-4" />
              Add Component
            </Button>
          </div>

          {/* Earnings */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                Earnings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {earnings.map(component => (
                  <ComponentRow
                    key={component.id}
                    component={component}
                    onEdit={() => handleEditComponent(component)}
                    onDelete={() => handleDeleteComponent(component.id)}
                    onToggle={() => handleToggleComponent(component.id)}
                  />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Deductions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-red-600" />
                Deductions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {deductions.map(component => (
                  <ComponentRow
                    key={component.id}
                    component={component}
                    onEdit={() => handleEditComponent(component)}
                    onDelete={() => handleDeleteComponent(component.id)}
                    onToggle={() => handleToggleComponent(component.id)}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* PF Settings Tab */}
        <TabsContent value="pf" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Landmark className="h-4 w-4" />
                Provident Fund (EPF) Settings
              </CardTitle>
              <CardDescription>
                Configure EPF contribution rates and rules as per EPFO guidelines
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ConfigFormRow columns={3}>
                <div className="space-y-2">
                  <Label>Employee Contribution (%)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={pfSettings.employeeContribution}
                    onChange={(e) => {
                      setPfSettings(prev => ({ ...prev, employeeContribution: parseFloat(e.target.value) }))
                      setIsDirty(true)
                    }}
                  />
                  <p className="text-xs text-muted-foreground">Standard: 12%</p>
                </div>
                <div className="space-y-2">
                  <Label>Employer Contribution (%)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={pfSettings.employerContribution}
                    onChange={(e) => {
                      setPfSettings(prev => ({ ...prev, employerContribution: parseFloat(e.target.value) }))
                      setIsDirty(true)
                    }}
                  />
                  <p className="text-xs text-muted-foreground">Standard: 12% (3.67% EPF + 8.33% EPS)</p>
                </div>
                <div className="space-y-2">
                  <Label>Wage Ceiling (Rs.)</Label>
                  <Input
                    type="number"
                    value={pfSettings.wageCeiling}
                    onChange={(e) => {
                      setPfSettings(prev => ({ ...prev, wageCeiling: parseInt(e.target.value) }))
                      setIsDirty(true)
                    }}
                  />
                  <p className="text-xs text-muted-foreground">Current limit: Rs. 15,000</p>
                </div>
              </ConfigFormRow>

              <div className="border-t pt-4 space-y-4">
                <h4 className="font-medium">PF Wage Calculation</h4>
                <ConfigToggle
                  label="Include DA in PF Wages"
                  description="Dearness Allowance will be considered for PF calculation"
                  checked={pfSettings.includeDA}
                  onChange={(checked) => {
                    setPfSettings(prev => ({ ...prev, includeDA: checked }))
                    setIsDirty(true)
                  }}
                />
                <ConfigToggle
                  label="Include Special Allowance in PF Wages"
                  description="Special Allowance will be considered for PF calculation"
                  checked={pfSettings.includeSpecialAllowance}
                  onChange={(checked) => {
                    setPfSettings(prev => ({ ...prev, includeSpecialAllowance: checked }))
                    setIsDirty(true)
                  }}
                />
                <ConfigToggle
                  label="Restrict to Basic + DA Only"
                  description="PF will be calculated only on Basic + DA, ignoring other allowances"
                  checked={pfSettings.restrictToBasic}
                  onChange={(checked) => {
                    setPfSettings(prev => ({ ...prev, restrictToBasic: checked }))
                    setIsDirty(true)
                  }}
                />
              </div>

              <div className="border-t pt-4 space-y-4">
                <h4 className="font-medium">Opt-Out Rules</h4>
                <ConfigToggle
                  label="Allow Voluntary Opt-Out"
                  description="Employees earning above threshold can opt out of PF"
                  checked={pfSettings.optOutAllowed}
                  onChange={(checked) => {
                    setPfSettings(prev => ({ ...prev, optOutAllowed: checked }))
                    setIsDirty(true)
                  }}
                />
                {pfSettings.optOutAllowed && (
                  <div className="space-y-2 ml-6">
                    <Label>Opt-Out Wage Limit (Rs.)</Label>
                    <Input
                      type="number"
                      value={pfSettings.optOutWageLimit}
                      onChange={(e) => {
                        setPfSettings(prev => ({ ...prev, optOutWageLimit: parseInt(e.target.value) }))
                        setIsDirty(true)
                      }}
                      className="max-w-xs"
                    />
                    <p className="text-xs text-muted-foreground">
                      Employees with Basic + DA above this limit can opt out
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ESI Settings Tab */}
        <TabsContent value="esi" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Calculator className="h-4 w-4" />
                ESI Settings
              </CardTitle>
              <CardDescription>
                Configure ESIC contribution rates as per current regulations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ConfigFormRow columns={3}>
                <div className="space-y-2">
                  <Label>Employee Contribution (%)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={esiSettings.employeeContribution}
                    onChange={(e) => {
                      setEsiSettings(prev => ({ ...prev, employeeContribution: parseFloat(e.target.value) }))
                      setIsDirty(true)
                    }}
                  />
                  <p className="text-xs text-muted-foreground">Standard: 0.75%</p>
                </div>
                <div className="space-y-2">
                  <Label>Employer Contribution (%)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={esiSettings.employerContribution}
                    onChange={(e) => {
                      setEsiSettings(prev => ({ ...prev, employerContribution: parseFloat(e.target.value) }))
                      setIsDirty(true)
                    }}
                  />
                  <p className="text-xs text-muted-foreground">Standard: 3.25%</p>
                </div>
                <div className="space-y-2">
                  <Label>Wage Ceiling (Rs.)</Label>
                  <Input
                    type="number"
                    value={esiSettings.wageCeiling}
                    onChange={(e) => {
                      setEsiSettings(prev => ({ ...prev, wageCeiling: parseInt(e.target.value) }))
                      setIsDirty(true)
                    }}
                  />
                  <p className="text-xs text-muted-foreground">Current limit: Rs. 21,000</p>
                </div>
              </ConfigFormRow>

              <FormSelect
                label="Round Off"
                name="roundOff"
                options={[
                  { value: 'nearest', label: 'Round to Nearest' },
                  { value: 'up', label: 'Round Up' },
                  { value: 'down', label: 'Round Down' }
                ]}
                value={esiSettings.roundOff}
                onChange={(e) => {
                  setEsiSettings(prev => ({ ...prev, roundOff: e.target.value as ESISettings['roundOff'] }))
                  setIsDirty(true)
                }}
                containerClassName="max-w-xs"
              />

              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg flex items-start gap-3">
                <Info className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
                <div className="text-sm text-blue-800 dark:text-blue-200">
                  <p className="font-medium">ESI Applicability</p>
                  <p className="mt-1">ESI is applicable when gross salary is at or below Rs. {esiSettings.wageCeiling.toLocaleString('en-IN')} per month. Once applicable, ESI continues for the entire contribution period even if salary exceeds the ceiling.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* PT Settings Tab */}
        <TabsContent value="pt" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <IndianRupee className="h-4 w-4" />
                Professional Tax Settings
              </CardTitle>
              <CardDescription>
                Configure state-wise Professional Tax slabs
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <FormSelect
                label="State"
                name="state"
                options={INDIAN_STATES_PT}
                value={ptSettings.state}
                onChange={(e) => {
                  setPtSettings(prev => ({ ...prev, state: e.target.value }))
                  setIsDirty(true)
                }}
                containerClassName="max-w-xs"
                hint="Select the state for PT calculation"
              />

              <div className="border-t pt-4">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="font-medium">PT Slabs</h4>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const lastSlab = ptSettings.slabs[ptSettings.slabs.length - 1]
                      setPtSettings(prev => ({
                        ...prev,
                        slabs: [...prev.slabs, { from: lastSlab.to + 1, to: lastSlab.to + 10000, amount: 0 }]
                      }))
                      setIsDirty(true)
                    }}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add Slab
                  </Button>
                </div>

                <div className="space-y-3">
                  {ptSettings.slabs.map((slab, index) => (
                    <div key={index} className="flex items-center gap-4 p-3 bg-muted rounded-lg">
                      <div className="flex-1 grid grid-cols-3 gap-4">
                        <div className="space-y-1">
                          <Label className="text-xs">From (Rs.)</Label>
                          <Input
                            type="number"
                            value={slab.from}
                            onChange={(e) => {
                              const newSlabs = [...ptSettings.slabs]
                              newSlabs[index].from = parseInt(e.target.value)
                              setPtSettings(prev => ({ ...prev, slabs: newSlabs }))
                              setIsDirty(true)
                            }}
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs">To (Rs.)</Label>
                          <Input
                            type="number"
                            value={slab.to}
                            onChange={(e) => {
                              const newSlabs = [...ptSettings.slabs]
                              newSlabs[index].to = parseInt(e.target.value)
                              setPtSettings(prev => ({ ...prev, slabs: newSlabs }))
                              setIsDirty(true)
                            }}
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs">PT Amount (Rs.)</Label>
                          <Input
                            type="number"
                            value={slab.amount}
                            onChange={(e) => {
                              const newSlabs = [...ptSettings.slabs]
                              newSlabs[index].amount = parseInt(e.target.value)
                              setPtSettings(prev => ({ ...prev, slabs: newSlabs }))
                              setIsDirty(true)
                            }}
                          />
                        </div>
                      </div>
                      {ptSettings.slabs.length > 1 && (
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => {
                            setPtSettings(prev => ({
                              ...prev,
                              slabs: prev.slabs.filter((_, i) => i !== index)
                            }))
                            setIsDirty(true)
                          }}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-yellow-600 shrink-0 mt-0.5" />
                <div className="text-sm text-yellow-800 dark:text-yellow-200">
                  <p className="font-medium">State-specific Rules</p>
                  <p className="mt-1">PT rates vary by state. Please verify the current rates with the respective state government website. Maximum PT per month is Rs. 2,500 as per Constitutional limits.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* TDS Settings Tab */}
        <TabsContent value="tds" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="h-4 w-4" />
                TDS Settings
              </CardTitle>
              <CardDescription>
                Configure income tax deduction settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ConfigFormRow columns={2}>
                <FormSelect
                  label="Default Tax Regime"
                  name="defaultRegime"
                  options={[
                    { value: 'new', label: 'New Tax Regime (Default from FY 2023-24)' },
                    { value: 'old', label: 'Old Tax Regime' }
                  ]}
                  value={tdsSettings.defaultRegime}
                  onChange={(e) => {
                    setTdsSettings(prev => ({ ...prev, defaultRegime: e.target.value as 'old' | 'new' }))
                    setIsDirty(true)
                  }}
                  hint="New regime is default for employees not declaring"
                />
                <div className="space-y-2">
                  <Label>Standard Deduction (Rs.)</Label>
                  <Input
                    type="number"
                    value={tdsSettings.standardDeduction}
                    onChange={(e) => {
                      setTdsSettings(prev => ({ ...prev, standardDeduction: parseInt(e.target.value) }))
                      setIsDirty(true)
                    }}
                  />
                  <p className="text-xs text-muted-foreground">Rs. 50,000 for both regimes</p>
                </div>
              </ConfigFormRow>

              <ConfigToggle
                label="Allow Employee to Choose Regime"
                description="Employees can select their preferred tax regime during declaration"
                checked={tdsSettings.allowEmployeeChoice}
                onChange={(checked) => {
                  setTdsSettings(prev => ({ ...prev, allowEmployeeChoice: checked }))
                  setIsDirty(true)
                }}
              />

              <div className="space-y-2">
                <Label>Health & Education Cess (%)</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={tdsSettings.cess}
                  onChange={(e) => {
                    setTdsSettings(prev => ({ ...prev, cess: parseFloat(e.target.value) }))
                    setIsDirty(true)
                  }}
                  className="max-w-xs"
                />
                <p className="text-xs text-muted-foreground">Current: 4% on tax amount</p>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-3">Tax Slabs Reference (New Regime FY 2024-25)</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>Up to Rs. 3,00,000</div><div className="text-right">Nil</div>
                  <div>Rs. 3,00,001 - 7,00,000</div><div className="text-right">5%</div>
                  <div>Rs. 7,00,001 - 10,00,000</div><div className="text-right">10%</div>
                  <div>Rs. 10,00,001 - 12,00,000</div><div className="text-right">15%</div>
                  <div>Rs. 12,00,001 - 15,00,000</div><div className="text-right">20%</div>
                  <div>Above Rs. 15,00,000</div><div className="text-right">30%</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pay Schedule Tab */}
        <TabsContent value="schedule" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Pay Schedule</CardTitle>
              <CardDescription>
                Configure monthly payroll processing schedule
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ConfigFormRow columns={2}>
                <FormSelect
                  label="Pay Day"
                  name="payDay"
                  options={Array.from({ length: 28 }, (_, i) => ({
                    value: String(i + 1),
                    label: `${i + 1}${['st', 'nd', 'rd'][i] || 'th'} of every month`
                  }))}
                  value={String(paySchedule.payDay)}
                  onChange={(e) => {
                    setPaySchedule(prev => ({ ...prev, payDay: parseInt(e.target.value) }))
                    setIsDirty(true)
                  }}
                  hint="Day when salaries are credited"
                />
                <FormSelect
                  label="Processing Day"
                  name="processingDay"
                  options={Array.from({ length: 28 }, (_, i) => ({
                    value: String(i + 1),
                    label: `${i + 1}${['st', 'nd', 'rd'][i] || 'th'} of every month`
                  }))}
                  value={String(paySchedule.processingDay)}
                  onChange={(e) => {
                    setPaySchedule(prev => ({ ...prev, processingDay: parseInt(e.target.value) }))
                    setIsDirty(true)
                  }}
                  hint="Day when payroll is processed"
                />
              </ConfigFormRow>

              <ConfigFormRow columns={2}>
                <FormSelect
                  label="Attendance Cutoff"
                  name="attendanceCutoff"
                  options={Array.from({ length: 28 }, (_, i) => ({
                    value: String(i + 1),
                    label: `${i + 1}${['st', 'nd', 'rd'][i] || 'th'} of every month`
                  }))}
                  value={String(paySchedule.attendanceCutoff)}
                  onChange={(e) => {
                    setPaySchedule(prev => ({ ...prev, attendanceCutoff: parseInt(e.target.value) }))
                    setIsDirty(true)
                  }}
                  hint="Last day for attendance input"
                />
                <FormSelect
                  label="Arrear Processing"
                  name="arrearProcessing"
                  options={[
                    { value: 'current', label: 'Process in Current Month' },
                    { value: 'next', label: 'Process in Next Month' }
                  ]}
                  value={paySchedule.arrearProcessing}
                  onChange={(e) => {
                    setPaySchedule(prev => ({ ...prev, arrearProcessing: e.target.value as 'current' | 'next' }))
                    setIsDirty(true)
                  }}
                  hint="When to process salary arrears"
                />
              </ConfigFormRow>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Component Dialog */}
      <Dialog open={isComponentDialogOpen} onOpenChange={setIsComponentDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingComponent ? 'Edit Component' : 'Add Salary Component'}</DialogTitle>
            <DialogDescription>
              Configure the salary component details
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Code *</Label>
                <Input
                  value={newComponent.code || ''}
                  onChange={(e) => setNewComponent(prev => ({ ...prev, code: e.target.value.toUpperCase() }))}
                  placeholder="BASIC"
                />
              </div>
              <FormSelect
                label="Type *"
                name="type"
                options={[
                  { value: 'earning', label: 'Earning' },
                  { value: 'deduction', label: 'Deduction' }
                ]}
                value={newComponent.type || 'earning'}
                onChange={(e) => setNewComponent(prev => ({ ...prev, type: e.target.value as 'earning' | 'deduction' }))}
              />
            </ConfigFormRow>

            <div className="space-y-2">
              <Label>Name *</Label>
              <Input
                value={newComponent.name || ''}
                onChange={(e) => setNewComponent(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Basic Salary"
              />
            </div>

            <FormSelect
              label="Calculation Type"
              name="calculationType"
              options={[
                { value: 'fixed', label: 'Fixed Amount' },
                { value: 'percentage', label: 'Percentage of Component' },
                { value: 'formula', label: 'Custom Formula' }
              ]}
              value={newComponent.calculationType || 'fixed'}
              onChange={(e) => setNewComponent(prev => ({ ...prev, calculationType: e.target.value as SalaryComponent['calculationType'] }))}
            />

            {newComponent.calculationType === 'percentage' && (
              <ConfigFormRow columns={2}>
                <FormSelect
                  label="Percentage Of"
                  name="percentageOf"
                  options={[
                    { value: 'CTC', label: 'CTC' },
                    { value: 'GROSS', label: 'Gross Salary' },
                    { value: 'BASIC', label: 'Basic Salary' },
                    { value: 'PF_WAGES', label: 'PF Wages' }
                  ]}
                  value={newComponent.percentageOf || 'BASIC'}
                  onChange={(e) => setNewComponent(prev => ({ ...prev, percentageOf: e.target.value }))}
                />
                <div className="space-y-2">
                  <Label>Percentage (%)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={newComponent.percentage || 0}
                    onChange={(e) => setNewComponent(prev => ({ ...prev, percentage: parseFloat(e.target.value) }))}
                  />
                </div>
              </ConfigFormRow>
            )}

            <div className="space-y-3 border-t pt-4">
              <ConfigToggle
                label="Is Taxable"
                checked={newComponent.isTaxable || false}
                onChange={(checked) => setNewComponent(prev => ({ ...prev, isTaxable: checked }))}
              />
              <ConfigToggle
                label="Affects PF Calculation"
                checked={newComponent.affectsPF || false}
                onChange={(checked) => setNewComponent(prev => ({ ...prev, affectsPF: checked }))}
              />
              <ConfigToggle
                label="Affects ESI Calculation"
                checked={newComponent.affectsESI || false}
                onChange={(checked) => setNewComponent(prev => ({ ...prev, affectsESI: checked }))}
              />
              <ConfigToggle
                label="Is Statutory"
                description="Cannot be removed if statutory"
                checked={newComponent.isStatutory || false}
                onChange={(checked) => setNewComponent(prev => ({ ...prev, isStatutory: checked }))}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsComponentDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveComponent} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                editingComponent ? 'Update Component' : 'Add Component'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// ============================================================================
// Component Row
// ============================================================================

interface ComponentRowProps {
  component: SalaryComponent
  onEdit: () => void
  onDelete: () => void
  onToggle: () => void
}

function ComponentRow({ component, onEdit, onDelete, onToggle }: ComponentRowProps) {
  return (
    <div className={`flex items-center justify-between p-3 rounded-lg border ${!component.isActive ? 'opacity-50' : ''}`}>
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded bg-muted flex items-center justify-center font-mono text-xs">
          {component.code}
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-medium">{component.name}</span>
            {component.isStatutory && (
              <Badge variant="secondary">Statutory</Badge>
            )}
            {!component.isActive && (
              <Badge variant="outline">Disabled</Badge>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
            <span>{component.calculationType === 'percentage' ? `${component.percentage}% of ${component.percentageOf}` : component.calculationType}</span>
            {component.isTaxable && <span>| Taxable</span>}
            {component.affectsPF && <span>| PF</span>}
            {component.affectsESI && <span>| ESI</span>}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="icon" onClick={onToggle}>
          {component.isActive ? (
            <Badge variant="default" className="h-6">Active</Badge>
          ) : (
            <Badge variant="outline" className="h-6">Inactive</Badge>
          )}
        </Button>
        <Button variant="ghost" size="icon" onClick={onEdit}>
          <Edit className="h-4 w-4" />
        </Button>
        {!component.isStatutory && (
          <Button variant="ghost" size="icon" onClick={onDelete}>
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        )}
      </div>
    </div>
  )
}
