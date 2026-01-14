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
  Clock,
  Plus,
  Edit,
  Trash2,
  Save,
  Loader2,
  MapPin,
  Sunrise,
  Sunset,
  Moon,
  Timer,
  AlertCircle,
  CheckCircle
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

interface Shift {
  id: string
  code: string
  name: string
  startTime: string
  endTime: string
  breakDuration: number // in minutes
  workingHours: number
  graceInMinutes: number
  graceOutMinutes: number
  halfDayHours: number
  isDefault: boolean
  isActive: boolean
  applicableDays: number[]
  color: string
}

interface OvertimeRule {
  id: string
  name: string
  minHours: number
  multiplier: number
  requiresApproval: boolean
  maxHoursPerDay: number
  maxHoursPerWeek: number
  isActive: boolean
}

interface RegularizationRule {
  id: string
  name: string
  maxPerMonth: number
  requiresApproval: boolean
  autoApproveAfterDays: number
  allowFutureDating: boolean
  allowBackDating: boolean
  maxBackDays: number
  isActive: boolean
}

interface GeoFenceLocation {
  id: string
  name: string
  address: string
  latitude: number
  longitude: number
  radiusMeters: number
  isActive: boolean
  applicableBranches: string[]
}

interface AttendanceSettings {
  markingMethod: 'biometric' | 'web' | 'mobile' | 'all'
  allowMultipleCheckIn: boolean
  autoCheckoutEnabled: boolean
  autoCheckoutTime: string
  minWorkHoursForFullDay: number
  minWorkHoursForHalfDay: number
  lateMarkAfterMinutes: number
  earlyGoingBeforeMinutes: number
  absentAfterMissedDays: number
}

// ============================================================================
// Initial Data
// ============================================================================

const INITIAL_SHIFTS: Shift[] = [
  {
    id: 'shift-1',
    code: 'GEN',
    name: 'General Shift',
    startTime: '09:00',
    endTime: '18:00',
    breakDuration: 60,
    workingHours: 8,
    graceInMinutes: 15,
    graceOutMinutes: 15,
    halfDayHours: 4,
    isDefault: true,
    isActive: true,
    applicableDays: [1, 2, 3, 4, 5],
    color: '#3B82F6'
  },
  {
    id: 'shift-2',
    code: 'MRN',
    name: 'Morning Shift',
    startTime: '06:00',
    endTime: '14:00',
    breakDuration: 30,
    workingHours: 8,
    graceInMinutes: 10,
    graceOutMinutes: 10,
    halfDayHours: 4,
    isDefault: false,
    isActive: true,
    applicableDays: [1, 2, 3, 4, 5, 6],
    color: '#F59E0B'
  },
  {
    id: 'shift-3',
    code: 'EVE',
    name: 'Evening Shift',
    startTime: '14:00',
    endTime: '22:00',
    breakDuration: 30,
    workingHours: 8,
    graceInMinutes: 10,
    graceOutMinutes: 10,
    halfDayHours: 4,
    isDefault: false,
    isActive: true,
    applicableDays: [1, 2, 3, 4, 5, 6],
    color: '#8B5CF6'
  },
  {
    id: 'shift-4',
    code: 'NGT',
    name: 'Night Shift',
    startTime: '22:00',
    endTime: '06:00',
    breakDuration: 30,
    workingHours: 8,
    graceInMinutes: 10,
    graceOutMinutes: 10,
    halfDayHours: 4,
    isDefault: false,
    isActive: true,
    applicableDays: [1, 2, 3, 4, 5, 6],
    color: '#1F2937'
  },
  {
    id: 'shift-5',
    code: 'FLX',
    name: 'Flexible Hours',
    startTime: '08:00',
    endTime: '20:00',
    breakDuration: 60,
    workingHours: 8,
    graceInMinutes: 120,
    graceOutMinutes: 120,
    halfDayHours: 4,
    isDefault: false,
    isActive: true,
    applicableDays: [1, 2, 3, 4, 5],
    color: '#10B981'
  }
]

const INITIAL_OVERTIME_RULES: OvertimeRule[] = [
  {
    id: 'ot-1',
    name: 'Weekday Overtime',
    minHours: 1,
    multiplier: 1.5,
    requiresApproval: true,
    maxHoursPerDay: 4,
    maxHoursPerWeek: 20,
    isActive: true
  },
  {
    id: 'ot-2',
    name: 'Weekend Overtime',
    minHours: 4,
    multiplier: 2,
    requiresApproval: true,
    maxHoursPerDay: 8,
    maxHoursPerWeek: 16,
    isActive: true
  },
  {
    id: 'ot-3',
    name: 'Holiday Overtime',
    minHours: 4,
    multiplier: 2.5,
    requiresApproval: true,
    maxHoursPerDay: 8,
    maxHoursPerWeek: 8,
    isActive: true
  }
]

const INITIAL_REGULARIZATION_RULES: RegularizationRule[] = [
  {
    id: 'reg-1',
    name: 'Missed Check-in/out',
    maxPerMonth: 4,
    requiresApproval: true,
    autoApproveAfterDays: 0,
    allowFutureDating: false,
    allowBackDating: true,
    maxBackDays: 7,
    isActive: true
  },
  {
    id: 'reg-2',
    name: 'Work From Home',
    maxPerMonth: 8,
    requiresApproval: true,
    autoApproveAfterDays: 0,
    allowFutureDating: true,
    allowBackDating: true,
    maxBackDays: 3,
    isActive: true
  },
  {
    id: 'reg-3',
    name: 'On-Duty (Client Location)',
    maxPerMonth: 20,
    requiresApproval: true,
    autoApproveAfterDays: 0,
    allowFutureDating: true,
    allowBackDating: true,
    maxBackDays: 7,
    isActive: true
  }
]

const INITIAL_GEOFENCE_LOCATIONS: GeoFenceLocation[] = [
  {
    id: 'geo-1',
    name: 'Head Office - Bangalore',
    address: 'Electronic City Phase 1, Bangalore',
    latitude: 12.8399,
    longitude: 77.6770,
    radiusMeters: 200,
    isActive: true,
    applicableBranches: ['HO']
  },
  {
    id: 'geo-2',
    name: 'Mumbai Office',
    address: 'BKC, Mumbai',
    latitude: 19.0587,
    longitude: 72.8656,
    radiusMeters: 150,
    isActive: true,
    applicableBranches: ['MUM']
  }
]

const INITIAL_SETTINGS: AttendanceSettings = {
  markingMethod: 'all',
  allowMultipleCheckIn: true,
  autoCheckoutEnabled: true,
  autoCheckoutTime: '23:59',
  minWorkHoursForFullDay: 8,
  minWorkHoursForHalfDay: 4,
  lateMarkAfterMinutes: 15,
  earlyGoingBeforeMinutes: 30,
  absentAfterMissedDays: 3
}

const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// ============================================================================
// Attendance Settings Page
// ============================================================================

export default function AttendanceSettingsPage() {
  const searchParams = useSearchParams()
  const defaultTab = searchParams.get('tab') || 'shifts'

  const [shifts, setShifts] = React.useState<Shift[]>(INITIAL_SHIFTS)
  const [overtimeRules, setOvertimeRules] = React.useState<OvertimeRule[]>(INITIAL_OVERTIME_RULES)
  const [regularizationRules, setRegularizationRules] = React.useState<RegularizationRule[]>(INITIAL_REGULARIZATION_RULES)
  const [geoLocations, setGeoLocations] = React.useState<GeoFenceLocation[]>(INITIAL_GEOFENCE_LOCATIONS)
  const [settings, setSettings] = React.useState<AttendanceSettings>(INITIAL_SETTINGS)

  const [isLoading, setIsLoading] = React.useState(false)
  const [isDirty, setIsDirty] = React.useState(false)
  const [isShiftDialogOpen, setIsShiftDialogOpen] = React.useState(false)
  const [isGeoDialogOpen, setIsGeoDialogOpen] = React.useState(false)
  const [editingShift, setEditingShift] = React.useState<Shift | null>(null)
  const [editingGeo, setEditingGeo] = React.useState<GeoFenceLocation | null>(null)

  // New shift form state
  const [newShift, setNewShift] = React.useState<Partial<Shift>>({
    startTime: '09:00',
    endTime: '18:00',
    breakDuration: 60,
    workingHours: 8,
    graceInMinutes: 15,
    graceOutMinutes: 15,
    halfDayHours: 4,
    isDefault: false,
    isActive: true,
    applicableDays: [1, 2, 3, 4, 5],
    color: '#3B82F6'
  })

  // New geo location form state
  const [newGeo, setNewGeo] = React.useState<Partial<GeoFenceLocation>>({
    radiusMeters: 200,
    isActive: true,
    applicableBranches: []
  })

  // Shift actions
  const handleAddShift = () => {
    setEditingShift(null)
    setNewShift({
      startTime: '09:00',
      endTime: '18:00',
      breakDuration: 60,
      workingHours: 8,
      graceInMinutes: 15,
      graceOutMinutes: 15,
      halfDayHours: 4,
      isDefault: false,
      isActive: true,
      applicableDays: [1, 2, 3, 4, 5],
      color: '#3B82F6'
    })
    setIsShiftDialogOpen(true)
  }

  const handleEditShift = (shift: Shift) => {
    setEditingShift(shift)
    setNewShift(shift)
    setIsShiftDialogOpen(true)
  }

  const handleSaveShift = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 500))

    if (editingShift) {
      setShifts(prev => prev.map(s =>
        s.id === editingShift.id ? { ...s, ...newShift } as Shift : s
      ))
    } else {
      const shift: Shift = {
        id: `shift-${Date.now()}`,
        code: newShift.code || '',
        name: newShift.name || '',
        startTime: newShift.startTime || '09:00',
        endTime: newShift.endTime || '18:00',
        breakDuration: newShift.breakDuration || 60,
        workingHours: newShift.workingHours || 8,
        graceInMinutes: newShift.graceInMinutes || 15,
        graceOutMinutes: newShift.graceOutMinutes || 15,
        halfDayHours: newShift.halfDayHours || 4,
        isDefault: newShift.isDefault || false,
        isActive: newShift.isActive ?? true,
        applicableDays: newShift.applicableDays || [1, 2, 3, 4, 5],
        color: newShift.color || '#3B82F6'
      }
      setShifts(prev => [...prev, shift])
    }

    setIsLoading(false)
    setIsShiftDialogOpen(false)
    setIsDirty(true)
  }

  const handleDeleteShift = (id: string) => {
    setShifts(prev => prev.filter(s => s.id !== id))
    setIsDirty(true)
  }

  // Geo location actions
  const handleAddGeo = () => {
    setEditingGeo(null)
    setNewGeo({
      radiusMeters: 200,
      isActive: true,
      applicableBranches: []
    })
    setIsGeoDialogOpen(true)
  }

  const handleEditGeo = (geo: GeoFenceLocation) => {
    setEditingGeo(geo)
    setNewGeo(geo)
    setIsGeoDialogOpen(true)
  }

  const handleSaveGeo = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 500))

    if (editingGeo) {
      setGeoLocations(prev => prev.map(g =>
        g.id === editingGeo.id ? { ...g, ...newGeo } as GeoFenceLocation : g
      ))
    } else {
      const geo: GeoFenceLocation = {
        id: `geo-${Date.now()}`,
        name: newGeo.name || '',
        address: newGeo.address || '',
        latitude: newGeo.latitude || 0,
        longitude: newGeo.longitude || 0,
        radiusMeters: newGeo.radiusMeters || 200,
        isActive: newGeo.isActive ?? true,
        applicableBranches: newGeo.applicableBranches || []
      }
      setGeoLocations(prev => [...prev, geo])
    }

    setIsLoading(false)
    setIsGeoDialogOpen(false)
    setIsDirty(true)
  }

  const handleDeleteGeo = (id: string) => {
    setGeoLocations(prev => prev.filter(g => g.id !== id))
    setIsDirty(true)
  }

  // Settings change
  const handleSettingsChange = (field: keyof AttendanceSettings, value: string | number | boolean) => {
    setSettings(prev => ({ ...prev, [field]: value }))
    setIsDirty(true)
  }

  // Overtime rule toggle
  const handleOvertimeToggle = (id: string) => {
    setOvertimeRules(prev => prev.map(r =>
      r.id === id ? { ...r, isActive: !r.isActive } : r
    ))
    setIsDirty(true)
  }

  // Regularization rule toggle
  const handleRegularizationToggle = (id: string) => {
    setRegularizationRules(prev => prev.map(r =>
      r.id === id ? { ...r, isActive: !r.isActive } : r
    ))
    setIsDirty(true)
  }

  // Save all
  const handleSave = async () => {
    setIsLoading(true)
    await new Promise(resolve => setTimeout(resolve, 1500))
    setIsLoading(false)
    setIsDirty(false)
  }

  // Get shift icon
  const getShiftIcon = (shift: Shift) => {
    const hour = parseInt(shift.startTime.split(':')[0])
    if (hour >= 5 && hour < 12) return Sunrise
    if (hour >= 12 && hour < 17) return Clock
    if (hour >= 17 && hour < 21) return Sunset
    return Moon
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Attendance Settings"
        description="Configure shifts, overtime rules, and attendance policies"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings", href: "/settings" },
          { label: "Attendance Settings" }
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
          <TabsTrigger value="shifts">Shifts</TabsTrigger>
          <TabsTrigger value="grace">Grace Period</TabsTrigger>
          <TabsTrigger value="overtime">Overtime</TabsTrigger>
          <TabsTrigger value="regularization">Regularization</TabsTrigger>
          <TabsTrigger value="geofence">Geo-Fencing</TabsTrigger>
          <TabsTrigger value="general">General</TabsTrigger>
        </TabsList>

        {/* Shifts Tab */}
        <TabsContent value="shifts" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold">Shift Management</h3>
              <p className="text-sm text-muted-foreground">Configure work shifts for employees</p>
            </div>
            <Button onClick={handleAddShift}>
              <Plus className="mr-2 h-4 w-4" />
              Add Shift
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {shifts.map(shift => {
              const Icon = getShiftIcon(shift)
              return (
                <Card key={shift.id} className={!shift.isActive ? 'opacity-60' : ''}>
                  <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                    <div className="flex items-start gap-3">
                      <div
                        className="h-10 w-10 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: `${shift.color}20` }}
                      >
                        <Icon className="h-5 w-5" style={{ color: shift.color }} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <CardTitle className="text-base">{shift.name}</CardTitle>
                          <Badge variant="outline">{shift.code}</Badge>
                          {shift.isDefault && <Badge>Default</Badge>}
                        </div>
                        <CardDescription className="mt-1">
                          {shift.startTime} - {shift.endTime} ({shift.workingHours}h)
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="icon" onClick={() => handleEditShift(shift)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      {!shift.isDefault && (
                        <Button variant="ghost" size="icon" onClick={() => handleDeleteShift(shift.id)}>
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Break:</span>
                        <span className="ml-2 font-medium">{shift.breakDuration} min</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Half Day:</span>
                        <span className="ml-2 font-medium">{shift.halfDayHours}h</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Grace In:</span>
                        <span className="ml-2 font-medium">{shift.graceInMinutes} min</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Grace Out:</span>
                        <span className="ml-2 font-medium">{shift.graceOutMinutes} min</span>
                      </div>
                    </div>
                    <div className="flex gap-1 mt-3">
                      {[0, 1, 2, 3, 4, 5, 6].map(day => (
                        <Badge
                          key={day}
                          variant={shift.applicableDays.includes(day) ? 'default' : 'outline'}
                          className="text-xs"
                        >
                          {DAY_NAMES[day]}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </TabsContent>

        {/* Grace Period Tab */}
        <TabsContent value="grace" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Timer className="h-4 w-4" />
                Grace Period & Half-Day Settings
              </CardTitle>
              <CardDescription>Configure grace periods and work hour calculations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ConfigFormRow columns={2}>
                <div className="space-y-2">
                  <Label>Late Mark After (minutes)</Label>
                  <Input
                    type="number"
                    value={settings.lateMarkAfterMinutes}
                    onChange={(e) => handleSettingsChange('lateMarkAfterMinutes', parseInt(e.target.value))}
                  />
                  <p className="text-xs text-muted-foreground">
                    Employee marked late if check-in exceeds grace + this value
                  </p>
                </div>
                <div className="space-y-2">
                  <Label>Early Going Before (minutes)</Label>
                  <Input
                    type="number"
                    value={settings.earlyGoingBeforeMinutes}
                    onChange={(e) => handleSettingsChange('earlyGoingBeforeMinutes', parseInt(e.target.value))}
                  />
                  <p className="text-xs text-muted-foreground">
                    Early going marked if checkout before shift end - this value
                  </p>
                </div>
              </ConfigFormRow>

              <ConfigFormRow columns={2}>
                <div className="space-y-2">
                  <Label>Min Hours for Full Day</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={settings.minWorkHoursForFullDay}
                    onChange={(e) => handleSettingsChange('minWorkHoursForFullDay', parseFloat(e.target.value))}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Min Hours for Half Day</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={settings.minWorkHoursForHalfDay}
                    onChange={(e) => handleSettingsChange('minWorkHoursForHalfDay', parseFloat(e.target.value))}
                  />
                </div>
              </ConfigFormRow>

              <div className="space-y-2">
                <Label>Absent After Missed Days</Label>
                <Input
                  type="number"
                  value={settings.absentAfterMissedDays}
                  onChange={(e) => handleSettingsChange('absentAfterMissedDays', parseInt(e.target.value))}
                  className="max-w-xs"
                />
                <p className="text-xs text-muted-foreground">
                  Auto-mark absent after consecutive missed check-ins
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Overtime Tab */}
        <TabsContent value="overtime" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Overtime Rules
              </CardTitle>
              <CardDescription>Configure overtime calculation and approval rules</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {overtimeRules.map(rule => (
                  <div
                    key={rule.id}
                    className={`flex items-center justify-between p-4 rounded-lg border ${!rule.isActive ? 'opacity-60' : ''}`}
                  >
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <span className="text-lg font-bold text-primary">{rule.multiplier}x</span>
                      </div>
                      <div>
                        <div className="font-medium">{rule.name}</div>
                        <div className="text-sm text-muted-foreground">
                          Min {rule.minHours}h | Max {rule.maxHoursPerDay}h/day, {rule.maxHoursPerWeek}h/week
                          {rule.requiresApproval && ' | Approval Required'}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={rule.isActive ? 'default' : 'secondary'}>
                        {rule.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleOvertimeToggle(rule.id)}
                      >
                        {rule.isActive ? 'Disable' : 'Enable'}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Regularization Tab */}
        <TabsContent value="regularization" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <CheckCircle className="h-4 w-4" />
                Regularization Rules
              </CardTitle>
              <CardDescription>Configure attendance regularization policies</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {regularizationRules.map(rule => (
                  <div
                    key={rule.id}
                    className={`p-4 rounded-lg border ${!rule.isActive ? 'opacity-60' : ''}`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="font-medium">{rule.name}</div>
                      <div className="flex items-center gap-2">
                        <Badge variant={rule.isActive ? 'default' : 'secondary'}>
                          {rule.isActive ? 'Active' : 'Inactive'}
                        </Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRegularizationToggle(rule.id)}
                        >
                          {rule.isActive ? 'Disable' : 'Enable'}
                        </Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Max/Month:</span>
                        <span className="ml-2 font-medium">{rule.maxPerMonth}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Back Dating:</span>
                        <span className="ml-2 font-medium">
                          {rule.allowBackDating ? `${rule.maxBackDays} days` : 'No'}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Future Dating:</span>
                        <span className="ml-2 font-medium">{rule.allowFutureDating ? 'Yes' : 'No'}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Approval:</span>
                        <span className="ml-2 font-medium">{rule.requiresApproval ? 'Required' : 'Auto'}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Geo-Fencing Tab */}
        <TabsContent value="geofence" className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-semibold">Geo-Fence Locations</h3>
              <p className="text-sm text-muted-foreground">Configure location-based attendance marking</p>
            </div>
            <Button onClick={handleAddGeo}>
              <Plus className="mr-2 h-4 w-4" />
              Add Location
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {geoLocations.map(geo => (
              <Card key={geo.id} className={!geo.isActive ? 'opacity-60' : ''}>
                <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                  <div className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <MapPin className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{geo.name}</CardTitle>
                      <CardDescription className="mt-1">{geo.address}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button variant="ghost" size="icon" onClick={() => handleEditGeo(geo)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDeleteGeo(geo.id)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Radius:</span>
                      <span className="ml-2 font-medium">{geo.radiusMeters}m</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Status:</span>
                      <Badge variant={geo.isActive ? 'default' : 'secondary'} className="ml-2">
                        {geo.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <div className="col-span-2">
                      <span className="text-muted-foreground">Coordinates:</span>
                      <span className="ml-2 font-mono text-xs">
                        {geo.latitude.toFixed(4)}, {geo.longitude.toFixed(4)}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="p-4 bg-muted rounded-lg flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
            <div className="text-sm text-muted-foreground">
              <p className="font-medium text-foreground">How Geo-Fencing Works</p>
              <p className="mt-1">
                Employees can only mark attendance when their device location is within the specified radius
                of configured locations. This requires location permission on their mobile device.
              </p>
            </div>
          </div>
        </TabsContent>

        {/* General Tab */}
        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">General Settings</CardTitle>
              <CardDescription>Configure general attendance policies</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <FormSelect
                label="Attendance Marking Method"
                name="markingMethod"
                options={[
                  { value: 'all', label: 'All Methods (Biometric, Web, Mobile)' },
                  { value: 'biometric', label: 'Biometric Only' },
                  { value: 'web', label: 'Web Portal Only' },
                  { value: 'mobile', label: 'Mobile App Only' }
                ]}
                value={settings.markingMethod}
                onChange={(e) => handleSettingsChange('markingMethod', e.target.value)}
                containerClassName="max-w-md"
              />

              <ConfigToggle
                label="Allow Multiple Check-ins"
                description="Allow employees to check-in/out multiple times per day"
                checked={settings.allowMultipleCheckIn}
                onChange={(checked) => handleSettingsChange('allowMultipleCheckIn', checked)}
              />

              <ConfigToggle
                label="Auto Checkout"
                description="Automatically check out employees who forget to check out"
                checked={settings.autoCheckoutEnabled}
                onChange={(checked) => handleSettingsChange('autoCheckoutEnabled', checked)}
              />

              {settings.autoCheckoutEnabled && (
                <div className="ml-6 space-y-2">
                  <Label>Auto Checkout Time</Label>
                  <Input
                    type="time"
                    value={settings.autoCheckoutTime}
                    onChange={(e) => handleSettingsChange('autoCheckoutTime', e.target.value)}
                    className="max-w-xs"
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Shift Dialog */}
      <Dialog open={isShiftDialogOpen} onOpenChange={setIsShiftDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingShift ? 'Edit Shift' : 'Add Shift'}</DialogTitle>
            <DialogDescription>
              Configure shift timing and rules
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Code *</Label>
                <Input
                  value={newShift.code || ''}
                  onChange={(e) => setNewShift(prev => ({ ...prev, code: e.target.value.toUpperCase() }))}
                  placeholder="GEN"
                  maxLength={4}
                />
              </div>
              <div className="space-y-2">
                <Label>Name *</Label>
                <Input
                  value={newShift.name || ''}
                  onChange={(e) => setNewShift(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="General Shift"
                />
              </div>
            </ConfigFormRow>

            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Start Time *</Label>
                <Input
                  type="time"
                  value={newShift.startTime || '09:00'}
                  onChange={(e) => setNewShift(prev => ({ ...prev, startTime: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <Label>End Time *</Label>
                <Input
                  type="time"
                  value={newShift.endTime || '18:00'}
                  onChange={(e) => setNewShift(prev => ({ ...prev, endTime: e.target.value }))}
                />
              </div>
            </ConfigFormRow>

            <ConfigFormRow columns={3}>
              <div className="space-y-2">
                <Label>Break (min)</Label>
                <Input
                  type="number"
                  value={newShift.breakDuration || 60}
                  onChange={(e) => setNewShift(prev => ({ ...prev, breakDuration: parseInt(e.target.value) }))}
                />
              </div>
              <div className="space-y-2">
                <Label>Working Hours</Label>
                <Input
                  type="number"
                  step="0.5"
                  value={newShift.workingHours || 8}
                  onChange={(e) => setNewShift(prev => ({ ...prev, workingHours: parseFloat(e.target.value) }))}
                />
              </div>
              <div className="space-y-2">
                <Label>Half Day Hours</Label>
                <Input
                  type="number"
                  step="0.5"
                  value={newShift.halfDayHours || 4}
                  onChange={(e) => setNewShift(prev => ({ ...prev, halfDayHours: parseFloat(e.target.value) }))}
                />
              </div>
            </ConfigFormRow>

            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Grace In (min)</Label>
                <Input
                  type="number"
                  value={newShift.graceInMinutes || 15}
                  onChange={(e) => setNewShift(prev => ({ ...prev, graceInMinutes: parseInt(e.target.value) }))}
                />
              </div>
              <div className="space-y-2">
                <Label>Grace Out (min)</Label>
                <Input
                  type="number"
                  value={newShift.graceOutMinutes || 15}
                  onChange={(e) => setNewShift(prev => ({ ...prev, graceOutMinutes: parseInt(e.target.value) }))}
                />
              </div>
            </ConfigFormRow>

            <div className="space-y-2">
              <Label>Applicable Days</Label>
              <div className="flex gap-2">
                {[0, 1, 2, 3, 4, 5, 6].map(day => (
                  <Button
                    key={day}
                    type="button"
                    variant={(newShift.applicableDays || []).includes(day) ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => {
                      const current = newShift.applicableDays || []
                      const updated = current.includes(day)
                        ? current.filter(d => d !== day)
                        : [...current, day]
                      setNewShift(prev => ({ ...prev, applicableDays: updated }))
                    }}
                  >
                    {DAY_NAMES[day]}
                  </Button>
                ))}
              </div>
            </div>

            <ConfigToggle
              label="Set as Default Shift"
              checked={newShift.isDefault || false}
              onChange={(checked) => setNewShift(prev => ({ ...prev, isDefault: checked }))}
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsShiftDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveShift} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                editingShift ? 'Update Shift' : 'Add Shift'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Geo Location Dialog */}
      <Dialog open={isGeoDialogOpen} onOpenChange={setIsGeoDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editingGeo ? 'Edit Location' : 'Add Location'}</DialogTitle>
            <DialogDescription>
              Configure geo-fence location for attendance
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Location Name *</Label>
              <Input
                value={newGeo.name || ''}
                onChange={(e) => setNewGeo(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Head Office - Bangalore"
              />
            </div>

            <div className="space-y-2">
              <Label>Address *</Label>
              <Input
                value={newGeo.address || ''}
                onChange={(e) => setNewGeo(prev => ({ ...prev, address: e.target.value }))}
                placeholder="Full address"
              />
            </div>

            <ConfigFormRow columns={2}>
              <div className="space-y-2">
                <Label>Latitude *</Label>
                <Input
                  type="number"
                  step="0.0001"
                  value={newGeo.latitude || ''}
                  onChange={(e) => setNewGeo(prev => ({ ...prev, latitude: parseFloat(e.target.value) }))}
                  placeholder="12.8399"
                />
              </div>
              <div className="space-y-2">
                <Label>Longitude *</Label>
                <Input
                  type="number"
                  step="0.0001"
                  value={newGeo.longitude || ''}
                  onChange={(e) => setNewGeo(prev => ({ ...prev, longitude: parseFloat(e.target.value) }))}
                  placeholder="77.6770"
                />
              </div>
            </ConfigFormRow>

            <div className="space-y-2">
              <Label>Radius (meters)</Label>
              <Input
                type="number"
                value={newGeo.radiusMeters || 200}
                onChange={(e) => setNewGeo(prev => ({ ...prev, radiusMeters: parseInt(e.target.value) }))}
              />
              <p className="text-xs text-muted-foreground">
                Employees must be within this radius to mark attendance
              </p>
            </div>

            <ConfigToggle
              label="Active"
              checked={newGeo.isActive ?? true}
              onChange={(checked) => setNewGeo(prev => ({ ...prev, isActive: checked }))}
            />
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsGeoDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveGeo} disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                editingGeo ? 'Update Location' : 'Add Location'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
