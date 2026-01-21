"use client"

import * as React from "react"
import { useSearchParams } from "next/navigation"
import { PageHeader } from "@/components/layout/page-header"
import { ConfigFormRow, ConfigToggle } from "@/components/settings/ConfigForm"
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
  Calendar,
  Plus,
  Edit,
  Trash2,
  Save,
  Loader2,
  CalendarDays,
  Gift,
  Briefcase,
  Baby,
  Heart,
  Sun,
  Moon
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

interface LeaveType {
  id: string
  code: string
  name: string
  description: string
  color: string
  icon: 'calendar' | 'gift' | 'briefcase' | 'baby' | 'heart'
  entitlementPerYear: number
  entitlementUnit: 'days' | 'hours'
  accrualType: 'yearly' | 'monthly' | 'quarterly'
  carryForward: boolean
  maxCarryForward: number
  encashment: boolean
  maxEncashment: number
  encashmentOnSeparation: boolean
  minDays: number
  maxDays: number
  requiresApproval: boolean
  requiresDocument: boolean
  documentAfterDays: number
  applicableGender: 'all' | 'male' | 'female'
  probationApplicable: boolean
  isActive: boolean
  isPaid: boolean
}

interface Holiday {
  id: string
  date: string
  name: string
  type: 'national' | 'regional' | 'optional' | 'restricted'
  applicableStates: string[]
  isFloating: boolean
}

interface WeekOff {
  day: 0 | 1 | 2 | 3 | 4 | 5 | 6
  isOff: boolean
  isAlternate: boolean
  alternateWeeks: number[]
}

// ============================================================================
// Initial Data
// ============================================================================

const LEAVE_ICONS = {
  calendar: CalendarDays,
  gift: Gift,
  briefcase: Briefcase,
  baby: Baby,
  heart: Heart
}

const INITIAL_LEAVE_TYPES: LeaveType[] = [
  {
    id: 'lt-1',
    code: 'CL',
    name: 'Casual Leave',
    description: 'For personal work and emergencies',
    color: '#3B82F6',
    icon: 'calendar',
    entitlementPerYear: 12,
    entitlementUnit: 'days',
    accrualType: 'monthly',
    carryForward: false,
    maxCarryForward: 0,
    encashment: false,
    maxEncashment: 0,
    encashmentOnSeparation: false,
    minDays: 0.5,
    maxDays: 3,
    requiresApproval: true,
    requiresDocument: false,
    documentAfterDays: 0,
    applicableGender: 'all',
    probationApplicable: true,
    isActive: true,
    isPaid: true
  },
  {
    id: 'lt-2',
    code: 'EL',
    name: 'Earned Leave',
    description: 'Privilege leave earned based on service',
    color: '#10B981',
    icon: 'gift',
    entitlementPerYear: 15,
    entitlementUnit: 'days',
    accrualType: 'monthly',
    carryForward: true,
    maxCarryForward: 30,
    encashment: true,
    maxEncashment: 30,
    encashmentOnSeparation: true,
    minDays: 1,
    maxDays: 15,
    requiresApproval: true,
    requiresDocument: false,
    documentAfterDays: 0,
    applicableGender: 'all',
    probationApplicable: false,
    isActive: true,
    isPaid: true
  },
  {
    id: 'lt-3',
    code: 'SL',
    name: 'Sick Leave',
    description: 'For illness and medical treatment',
    color: '#EF4444',
    icon: 'heart',
    entitlementPerYear: 12,
    entitlementUnit: 'days',
    accrualType: 'yearly',
    carryForward: false,
    maxCarryForward: 0,
    encashment: false,
    maxEncashment: 0,
    encashmentOnSeparation: false,
    minDays: 0.5,
    maxDays: 12,
    requiresApproval: true,
    requiresDocument: true,
    documentAfterDays: 2,
    applicableGender: 'all',
    probationApplicable: true,
    isActive: true,
    isPaid: true
  },
  {
    id: 'lt-4',
    code: 'ML',
    name: 'Maternity Leave',
    description: 'Maternity leave as per Maternity Benefit Act',
    color: '#EC4899',
    icon: 'baby',
    entitlementPerYear: 182,
    entitlementUnit: 'days',
    accrualType: 'yearly',
    carryForward: false,
    maxCarryForward: 0,
    encashment: false,
    maxEncashment: 0,
    encashmentOnSeparation: false,
    minDays: 1,
    maxDays: 182,
    requiresApproval: true,
    requiresDocument: true,
    documentAfterDays: 0,
    applicableGender: 'female',
    probationApplicable: true,
    isActive: true,
    isPaid: true
  },
  {
    id: 'lt-5',
    code: 'PL',
    name: 'Paternity Leave',
    description: 'Leave for new fathers',
    color: '#6366F1',
    icon: 'baby',
    entitlementPerYear: 15,
    entitlementUnit: 'days',
    accrualType: 'yearly',
    carryForward: false,
    maxCarryForward: 0,
    encashment: false,
    maxEncashment: 0,
    encashmentOnSeparation: false,
    minDays: 1,
    maxDays: 15,
    requiresApproval: true,
    requiresDocument: true,
    documentAfterDays: 0,
    applicableGender: 'male',
    probationApplicable: false,
    isActive: true,
    isPaid: true
  },
  {
    id: 'lt-6',
    code: 'CO',
    name: 'Compensatory Off',
    description: 'For working on holidays/weekends',
    color: '#F59E0B',
    icon: 'briefcase',
    entitlementPerYear: 0,
    entitlementUnit: 'days',
    accrualType: 'yearly',
    carryForward: true,
    maxCarryForward: 5,
    encashment: false,
    maxEncashment: 0,
    encashmentOnSeparation: false,
    minDays: 0.5,
    maxDays: 2,
    requiresApproval: true,
    requiresDocument: false,
    documentAfterDays: 0,
    applicableGender: 'all',
    probationApplicable: true,
    isActive: true,
    isPaid: true
  },
  {
    id: 'lt-7',
    code: 'LWP',
    name: 'Leave Without Pay',
    description: 'Unpaid leave when balance exhausted',
    color: '#6B7280',
    icon: 'calendar',
    entitlementPerYear: 0,
    entitlementUnit: 'days',
    accrualType: 'yearly',
    carryForward: false,
    maxCarryForward: 0,
    encashment: false,
    maxEncashment: 0,
    encashmentOnSeparation: false,
    minDays: 0.5,
    maxDays: 30,
    requiresApproval: true,
    requiresDocument: false,
    documentAfterDays: 0,
    applicableGender: 'all',
    probationApplicable: true,
    isActive: true,
    isPaid: false
  }
]

const INITIAL_HOLIDAYS: Holiday[] = [
  { id: 'h-1', date: '2025-01-26', name: 'Republic Day', type: 'national', applicableStates: [], isFloating: false },
  { id: 'h-2', date: '2025-03-14', name: 'Holi', type: 'national', applicableStates: [], isFloating: false },
  { id: 'h-3', date: '2025-04-14', name: 'Dr. Ambedkar Jayanti', type: 'national', applicableStates: [], isFloating: false },
  { id: 'h-4', date: '2025-04-18', name: 'Good Friday', type: 'national', applicableStates: [], isFloating: false },
  { id: 'h-5', date: '2025-05-01', name: 'May Day', type: 'regional', applicableStates: ['KA', 'TN', 'KL', 'MH', 'GJ'], isFloating: false },
  { id: 'h-6', date: '2025-08-15', name: 'Independence Day', type: 'national', applicableStates: [], isFloating: false },
  { id: 'h-7', date: '2025-10-02', name: 'Gandhi Jayanti', type: 'national', applicableStates: [], isFloating: false },
  { id: 'h-8', date: '2025-10-20', name: 'Dussehra', type: 'national', applicableStates: [], isFloating: false },
  { id: 'h-9', date: '2025-11-01', name: 'Karnataka Rajyotsava', type: 'regional', applicableStates: ['KA'], isFloating: false },
  { id: 'h-10', date: '2025-11-12', name: 'Diwali', type: 'national', applicableStates: [], isFloating: false },
  { id: 'h-11', date: '2025-12-25', name: 'Christmas', type: 'national', applicableStates: [], isFloating: false }
]

const INITIAL_WEEK_OFFS: WeekOff[] = [
  { day: 0, isOff: true, isAlternate: false, alternateWeeks: [] }, // Sunday
  { day: 1, isOff: false, isAlternate: false, alternateWeeks: [] }, // Monday
  { day: 2, isOff: false, isAlternate: false, alternateWeeks: [] }, // Tuesday
  { day: 3, isOff: false, isAlternate: false, alternateWeeks: [] }, // Wednesday
  { day: 4, isOff: false, isAlternate: false, alternateWeeks: [] }, // Thursday
  { day: 5, isOff: false, isAlternate: false, alternateWeeks: [] }, // Friday
  { day: 6, isOff: true, isAlternate: true, alternateWeeks: [2, 4] } // Saturday
]

const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

// ============================================================================
// Leave Configuration Page
// ============================================================================

export default function LeaveConfigPage() {
  const searchParams = useSearchParams()
  const defaultTab = searchParams.get('tab') || 'types'

  const [leaveTypes, setLeaveTypes] = React.useState<LeaveType[]>(INITIAL_LEAVE_TYPES)
  const [holidays, setHolidays] = React.useState<Holiday[]>(INITIAL_HOLIDAYS)
  const [weekOffs, setWeekOffs] = React.useState<WeekOff[]>(INITIAL_WEEK_OFFS)

  const [isLoading, setIsLoading] = React.useState(false)
  const [isDirty, setIsDirty] = React.useState(false)
  const [isLeaveTypeDialogOpen, setIsLeaveTypeDialogOpen] = React.useState(false)
  const [isHolidayDialogOpen, setIsHolidayDialogOpen] = React.useState(false)
  const [editingLeaveType, setEditingLeaveType] = React.useState<LeaveType | null>(null)
  const [editingHoliday, setEditingHoliday] = React.useState<Holiday | null>(null)

  // New leave type form state
  const [newLeaveType, setNewLeaveType] = React.useState<Partial<LeaveType>>({
    icon: 'calendar',
    color: '#3B82F6',
    entitlementUnit: 'days',
    accrualType: 'yearly',
    applicableGender: 'all',
    isActive: true,
    isPaid: true,
    requiresApproval: true
  })

  // New holiday form state
  const [newHoliday, setNewHoliday] = React.useState<Partial<Holiday>>({
    type: 'national',
    applicableStates: [],
    isFloating: false
  })

  // Handle leave type actions
  const handleAddLeaveType = () => {
    setEditingLeaveType(null)
    setNewLeaveType({
      icon: 'calendar',
      color: '#3B82F6',
      entitlementUnit: 'days',
      accrualType: 'yearly',
      applicableGender: 'all',
      isActive: true,
      isPaid: true,
      requiresApproval: true
    })
    setIsLeaveTypeDialogOpen(true)
  }

  const handleEditLeaveType = (leaveType: LeaveType) => {
    setEditingLeaveType(leaveType)
    setNewLeaveType(leaveType)
    setIsLeaveTypeDialogOpen(true)
  }

  const handleSaveLeaveType = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 500))

    if (editingLeaveType) {
      setLeaveTypes(prev => prev.map(lt =>
        lt.id === editingLeaveType.id ? { ...lt, ...newLeaveType } as LeaveType : lt
      ))
    } else {
      const leaveType: LeaveType = {
        id: `lt-${Date.now()}`,
        code: newLeaveType.code || '',
        name: newLeaveType.name || '',
        description: newLeaveType.description || '',
        color: newLeaveType.color || '#3B82F6',
        icon: newLeaveType.icon || 'calendar',
        entitlementPerYear: newLeaveType.entitlementPerYear || 0,
        entitlementUnit: newLeaveType.entitlementUnit || 'days',
        accrualType: newLeaveType.accrualType || 'yearly',
        carryForward: newLeaveType.carryForward || false,
        maxCarryForward: newLeaveType.maxCarryForward || 0,
        encashment: newLeaveType.encashment || false,
        maxEncashment: newLeaveType.maxEncashment || 0,
        encashmentOnSeparation: newLeaveType.encashmentOnSeparation || false,
        minDays: newLeaveType.minDays || 0.5,
        maxDays: newLeaveType.maxDays || 30,
        requiresApproval: newLeaveType.requiresApproval ?? true,
        requiresDocument: newLeaveType.requiresDocument || false,
        documentAfterDays: newLeaveType.documentAfterDays || 0,
        applicableGender: newLeaveType.applicableGender || 'all',
        probationApplicable: newLeaveType.probationApplicable || false,
        isActive: newLeaveType.isActive ?? true,
        isPaid: newLeaveType.isPaid ?? true
      }
      setLeaveTypes(prev => [...prev, leaveType])
    }

    setIsLoading(false)
    setIsLeaveTypeDialogOpen(false)
    setIsDirty(true)
  }

  const handleDeleteLeaveType = (id: string) => {
    setLeaveTypes(prev => prev.filter(lt => lt.id !== id))
    setIsDirty(true)
  }

  // Handle holiday actions
  const handleAddHoliday = () => {
    setEditingHoliday(null)
    setNewHoliday({
      type: 'national',
      applicableStates: [],
      isFloating: false
    })
    setIsHolidayDialogOpen(true)
  }

  const handleEditHoliday = (holiday: Holiday) => {
    setEditingHoliday(holiday)
    setNewHoliday(holiday)
    setIsHolidayDialogOpen(true)
  }

  const handleSaveHoliday = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 500))

    if (editingHoliday) {
      setHolidays(prev => prev.map(h =>
        h.id === editingHoliday.id ? { ...h, ...newHoliday } as Holiday : h
      ))
    } else {
      const holiday: Holiday = {
        id: `h-${Date.now()}`,
        date: newHoliday.date || '',
        name: newHoliday.name || '',
        type: newHoliday.type || 'national',
        applicableStates: newHoliday.applicableStates || [],
        isFloating: newHoliday.isFloating || false
      }
      setHolidays(prev => [...prev, holiday])
    }

    setIsLoading(false)
    setIsHolidayDialogOpen(false)
    setIsDirty(true)
  }

  const handleDeleteHoliday = (id: string) => {
    setHolidays(prev => prev.filter(h => h.id !== id))
    setIsDirty(true)
  }

  // Handle week off changes
  const handleWeekOffChange = (day: number, field: keyof WeekOff, value: boolean | number[]) => {
    setWeekOffs(prev => prev.map(wo =>
      wo.day === day ? { ...wo, [field]: value } : wo
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
        title="Leave Configuration"
        description="Configure leave types, holidays, and week-off settings"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings", href: "/settings" },
          { label: "Leave Configuration" }
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
        <TabsList>
          <TabsTrigger value="types">Leave Types</TabsTrigger>
          <TabsTrigger value="holidays">Holiday Calendar</TabsTrigger>
          <TabsTrigger value="weekoffs">Week-Off Settings</TabsTrigger>
        </TabsList>

        {/* Leave Types Tab */}
        <TabsContent value="types" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold">Leave Types</h3>
              <p className="text-sm text-muted-foreground">Configure available leave types and their policies</p>
            </div>
            <Button onClick={handleAddLeaveType}>
              <Plus className="mr-2 h-4 w-4" />
              Add Leave Type
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {leaveTypes.map(leaveType => {
              const Icon = LEAVE_ICONS[leaveType.icon]
              return (
                <Card key={leaveType.id} className={!leaveType.isActive ? 'opacity-60' : ''}>
                  <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                    <div className="flex items-start gap-3">
                      <div
                        className="h-10 w-10 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: `${leaveType.color}20` }}
                      >
                        <Icon className="h-5 w-5" style={{ color: leaveType.color }} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-base">{leaveType.name}</CardTitle>
                          <Badge variant="outline" className="text-xs">{leaveType.code}</Badge>
                          {!leaveType.isPaid && <Badge variant="secondary">Unpaid</Badge>}
                        </div>
                        <CardDescription className="mt-1">{leaveType.description}</CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="icon" onClick={() => handleEditLeaveType(leaveType)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDeleteLeaveType(leaveType.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Entitlement:</span>
                        <span className="ml-2 font-medium">{leaveType.entitlementPerYear} {leaveType.entitlementUnit}/year</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Accrual:</span>
                        <span className="ml-2 font-medium capitalize">{leaveType.accrualType}</span>
                      </div>
                      {leaveType.carryForward && (
                        <div>
                          <span className="text-muted-foreground">Max Carry Forward:</span>
                          <span className="ml-2 font-medium">{leaveType.maxCarryForward} days</span>
                        </div>
                      )}
                      {leaveType.encashment && (
                        <div>
                          <span className="text-muted-foreground">Max Encashment:</span>
                          <span className="ml-2 font-medium">{leaveType.maxEncashment} days</span>
                        </div>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2 mt-3">
                      {leaveType.carryForward && <Badge variant="secondary">Carry Forward</Badge>}
                      {leaveType.encashment && <Badge variant="secondary">Encashable</Badge>}
                      {leaveType.requiresDocument && <Badge variant="secondary">Doc Required</Badge>}
                      {leaveType.applicableGender !== 'all' && (
                        <Badge variant="secondary" className="capitalize">{leaveType.applicableGender} Only</Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        {/* Holiday Calendar Tab */}
        <TabsContent value="holidays" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold">Holiday Calendar 2025</h3>
              <p className="text-sm text-muted-foreground">Manage public holidays and optional holidays</p>
            </div>
            <Button onClick={handleAddHoliday}>
              <Plus className="mr-2 h-4 w-4" />
              Add Holiday
            </Button>
          </div>

          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3">
                {holidays.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()).map(holiday => (
                  <div
                    key={holiday.id}
                    className="flex items-center justify-between p-3 rounded-lg border"
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-lg bg-muted flex flex-col items-center justify-center">
                        <span className="text-xs text-muted-foreground">
                          {new Date(holiday.date).toLocaleDateString('en-IN', { month: 'short' })}
                        </span>
                        <span className="text-lg font-bold">
                          {new Date(holiday.date).getDate()}
                        </span>
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{holiday.name}</span>
                          <Badge variant={
                            holiday.type === 'national' ? 'default' :
                            holiday.type === 'regional' ? 'secondary' :
                            'outline'
                          }>
                            {holiday.type}
                          </Badge>
                          {holiday.isFloating && <Badge variant="outline">Floating</Badge>}
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {new Date(holiday.date).toLocaleDateString('en-IN', {
                            weekday: 'long',
                            year: 'numeric'
                          })}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="icon" onClick={() => handleEditHoliday(holiday)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDeleteHoliday(holiday.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Badge>National</Badge>
              <span className="text-muted-foreground">Applicable to all</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">Regional</Badge>
              <span className="text-muted-foreground">State-specific</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">Optional</Badge>
              <span className="text-muted-foreground">Employee choice</span>
            </div>
          </div>
        </TabsContent>

        {/* Week-Off Settings Tab */}
        <TabsContent value="weekoffs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Week-Off Settings</CardTitle>
              <CardDescription>Configure weekly off days for the organization</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {weekOffs.map(weekOff => (
                  <div
                    key={weekOff.day}
                    className="flex items-center justify-between py-3 border-b last:border-b-0"
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
                        {weekOff.day === 0 || weekOff.day === 6 ? (
                          <Sun className="h-5 w-5 text-muted-foreground" />
                        ) : (
                          <Moon className="h-5 w-5 text-muted-foreground" />
                        )}
                      </div>
                      <div>
                        <span className="font-medium">{DAY_NAMES[weekOff.day]}</span>
                        {weekOff.isOff && weekOff.isAlternate && (
                          <div className="text-sm text-muted-foreground">
                            Off on {weekOff.alternateWeeks.map(w => `${w}${['st', 'nd', 'rd', 'th'][w - 1] || 'th'}`).join(' & ')} week
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <Label className="text-sm">Off</Label>
                        <input
                          type="checkbox"
                          checked={weekOff.isOff}
                          onChange={(e) => handleWeekOffChange(weekOff.day, 'isOff', e.target.checked)}
                          className="h-4 w-4 rounded border-input"
                        />
                      </div>
                      {weekOff.isOff && (
                        <div className="flex items-center gap-2">
                          <Label className="text-sm">Alternate</Label>
                          <input
                            type="checkbox"
                            checked={weekOff.isAlternate}
                            onChange={(e) => handleWeekOffChange(weekOff.day, 'isAlternate', e.target.checked)}
                            className="h-4 w-4 rounded border-input"
                          />
                        </div>
                      )}
                      {weekOff.isOff && weekOff.isAlternate && (
                        <FormSelect
                          label=""
                          name={`alternate-${weekOff.day}`}
                          options={[
                            { value: '2,4', label: '2nd & 4th week' },
                            { value: '1,3', label: '1st & 3rd week' },
                            { value: '2', label: '2nd week only' },
                            { value: '4', label: '4th week only' }
                          ]}
                          value={weekOff.alternateWeeks.join(',')}
                          onChange={(e) => handleWeekOffChange(
                            weekOff.day,
                            'alternateWeeks',
                            e.target.value.split(',').map(Number)
                          )}
                          containerClassName="w-40"
                        />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Leave Type Dialog */}
      <Dialog open={isLeaveTypeDialogOpen} onOpenChange={setIsLeaveTypeDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingLeaveType ? 'Edit Leave Type' : 'Add Leave Type'}</DialogTitle>
            <DialogDescription>
              Configure leave type settings and policies
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            <ConfigFormRow columns={3}>
              <div className="space-y-2">
                <Label>Code *</Label>
                <Input
                  value={newLeaveType.code || ''}
                  onChange={(e) => setNewLeaveType(prev => ({ ...prev, code: e.target.value.toUpperCase() }))}
                  placeholder="CL"
                  maxLength={5}
                />
              </div>
              <div className="col-span-2 space-y-2">
                <Label>Name *</Label>
                <Input
                  value={newLeaveType.name || ''}
                  onChange={(e) => setNewLeaveType(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Casual Leave"
                />
              </div>
            </ConfigFormRow>

            <div className="space-y-2">
              <Label>Description</Label>
              <Input
                value={newLeaveType.description || ''}
                onChange={(e) => setNewLeaveType(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Brief description of leave type"
              />
            </div>

            <ConfigFormRow columns={3}>
              <div className="space-y-2">
                <Label>Entitlement/Year</Label>
                <Input
                  type="number"
                  value={newLeaveType.entitlementPerYear || 0}
                  onChange={(e) => setNewLeaveType(prev => ({ ...prev, entitlementPerYear: parseInt(e.target.value) }))}
                />
              </div>
              <FormSelect
                label="Unit"
                name="unit"
                options={[
                  { value: 'days', label: 'Days' },
                  { value: 'hours', label: 'Hours' }
                ]}
                value={newLeaveType.entitlementUnit || 'days'}
                onChange={(e) => setNewLeaveType(prev => ({ ...prev, entitlementUnit: e.target.value as 'days' | 'hours' }))}
              />
              <FormSelect
                label="Accrual"
                name="accrual"
                options={[
                  { value: 'yearly', label: 'Yearly' },
                  { value: 'monthly', label: 'Monthly' },
                  { value: 'quarterly', label: 'Quarterly' }
                ]}
                value={newLeaveType.accrualType || 'yearly'}
                onChange={(e) => setNewLeaveType(prev => ({ ...prev, accrualType: e.target.value as 'yearly' | 'monthly' | 'quarterly' }))}
              />
            </ConfigFormRow>

            <div className="border-t pt-4 space-y-4">
              <h4 className="font-medium">Carry Forward & Encashment</h4>
              <ConfigToggle
                label="Allow Carry Forward"
                description="Unused leave can be carried to next year"
                checked={newLeaveType.carryForward || false}
                onChange={(checked) => setNewLeaveType(prev => ({ ...prev, carryForward: checked }))}
              />
              {newLeaveType.carryForward && (
                <div className="ml-6 space-y-2">
                  <Label>Max Carry Forward (days)</Label>
                  <Input
                    type="number"
                    value={newLeaveType.maxCarryForward || 0}
                    onChange={(e) => setNewLeaveType(prev => ({ ...prev, maxCarryForward: parseInt(e.target.value) }))}
                    className="max-w-xs"
                  />
                </div>
              )}
              <ConfigToggle
                label="Allow Encashment"
                description="Unused leave can be encashed"
                checked={newLeaveType.encashment || false}
                onChange={(checked) => setNewLeaveType(prev => ({ ...prev, encashment: checked }))}
              />
              {newLeaveType.encashment && (
                <>
                  <div className="ml-6 space-y-2">
                    <Label>Max Encashment (days)</Label>
                    <Input
                      type="number"
                      value={newLeaveType.maxEncashment || 0}
                      onChange={(e) => setNewLeaveType(prev => ({ ...prev, maxEncashment: parseInt(e.target.value) }))}
                      className="max-w-xs"
                    />
                  </div>
                  <div className="ml-6">
                    <ConfigToggle
                      label="Encashment on Separation"
                      description="Allow encashment when employee leaves"
                      checked={newLeaveType.encashmentOnSeparation || false}
                      onChange={(checked) => setNewLeaveType(prev => ({ ...prev, encashmentOnSeparation: checked }))}
                    />
                  </div>
                </>
              )}
            </div>

            <div className="border-t pt-4 space-y-4">
              <h4 className="font-medium">Rules & Restrictions</h4>
              <ConfigFormRow columns={2}>
                <div className="space-y-2">
                  <Label>Min Days per Application</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={newLeaveType.minDays || 0.5}
                    onChange={(e) => setNewLeaveType(prev => ({ ...prev, minDays: parseFloat(e.target.value) }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Max Days per Application</Label>
                  <Input
                    type="number"
                    value={newLeaveType.maxDays || 30}
                    onChange={(e) => setNewLeaveType(prev => ({ ...prev, maxDays: parseInt(e.target.value) }))}
                  />
                </div>
              </ConfigFormRow>
              <ConfigFormRow columns={2}>
                <FormSelect
                  label="Applicable Gender"
                  name="gender"
                  options={[
                    { value: 'all', label: 'All' },
                    { value: 'male', label: 'Male Only' },
                    { value: 'female', label: 'Female Only' }
                  ]}
                  value={newLeaveType.applicableGender || 'all'}
                  onChange={(e) => setNewLeaveType(prev => ({ ...prev, applicableGender: e.target.value as 'all' | 'male' | 'female' }))}
                />
                <div className="space-y-2">
                  <Label>Document Required After (days)</Label>
                  <Input
                    type="number"
                    value={newLeaveType.documentAfterDays || 0}
                    onChange={(e) => setNewLeaveType(prev => ({ ...prev, documentAfterDays: parseInt(e.target.value), requiresDocument: parseInt(e.target.value) > 0 }))}
                    placeholder="0 = no document required"
                  />
                </div>
              </ConfigFormRow>
              <ConfigToggle
                label="Available During Probation"
                checked={newLeaveType.probationApplicable || false}
                onChange={(checked) => setNewLeaveType(prev => ({ ...prev, probationApplicable: checked }))}
              />
              <ConfigToggle
                label="Paid Leave"
                checked={newLeaveType.isPaid ?? true}
                onChange={(checked) => setNewLeaveType(prev => ({ ...prev, isPaid: checked }))}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsLeaveTypeDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveLeaveType} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                editingLeaveType ? 'Update Leave Type' : 'Add Leave Type'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Holiday Dialog */}
      <Dialog open={isHolidayDialogOpen} onOpenChange={setIsHolidayDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingHoliday ? 'Edit Holiday' : 'Add Holiday'}</DialogTitle>
            <DialogDescription>
              Add a public or optional holiday
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Date *</Label>
              <Input
                type="date"
                value={newHoliday.date || ''}
                onChange={(e) => setNewHoliday(prev => ({ ...prev, date: e.target.value }))}
              />
            </div>

            <div className="space-y-2">
              <Label>Name *</Label>
              <Input
                value={newHoliday.name || ''}
                onChange={(e) => setNewHoliday(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Republic Day"
              />
            </div>

            <FormSelect
              label="Type"
              name="type"
              options={[
                { value: 'national', label: 'National Holiday' },
                { value: 'regional', label: 'Regional Holiday' },
                { value: 'optional', label: 'Optional Holiday' },
                { value: 'restricted', label: 'Restricted Holiday' }
              ]}
              value={newHoliday.type || 'national'}
              onChange={(e) => setNewHoliday(prev => ({ ...prev, type: e.target.value as Holiday['type'] }))}
            />

            <ConfigToggle
              label="Floating Holiday"
              description="Date varies each year"
              checked={newHoliday.isFloating || false}
              onChange={(checked) => setNewHoliday(prev => ({ ...prev, isFloating: checked }))}
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsHolidayDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveHoliday} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                editingHoliday ? 'Update Holiday' : 'Add Holiday'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
