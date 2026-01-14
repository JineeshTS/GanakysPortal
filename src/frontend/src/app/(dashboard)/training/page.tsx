'use client'

import { useState } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  GraduationCap,
  Plus,
  BookOpen,
  Award,
  Clock,
  Users,
  Calendar,
  Play,
  CheckCircle,
  Star
} from 'lucide-react'

const courses = [
  { id: '1', title: 'India Labour Law Compliance', category: 'Compliance', duration: '4 hours', enrolled: 45, completed: 38, mandatory: true },
  { id: '2', title: 'GST Filing Masterclass', category: 'Finance', duration: '6 hours', enrolled: 28, completed: 22, mandatory: true },
  { id: '3', title: 'Leadership Skills', category: 'Soft Skills', duration: '8 hours', enrolled: 15, completed: 8, mandatory: false },
  { id: '4', title: 'Data Security & Privacy', category: 'IT', duration: '3 hours', enrolled: 52, completed: 48, mandatory: true },
  { id: '5', title: 'Effective Communication', category: 'Soft Skills', duration: '5 hours', enrolled: 32, completed: 20, mandatory: false },
  { id: '6', title: 'PF/ESI Regulations 2025', category: 'Compliance', duration: '2 hours', enrolled: 40, completed: 35, mandatory: true },
]

const certifications = [
  { id: '1', name: 'AWS Solutions Architect', employee: 'Rajesh Kumar', status: 'active', expiry: '2026-06-15', issuer: 'Amazon' },
  { id: '2', name: 'PMP Certified', employee: 'Priya Sharma', status: 'active', expiry: '2027-03-20', issuer: 'PMI' },
  { id: '3', name: 'Chartered Accountant', employee: 'Amit Patel', status: 'active', expiry: null, issuer: 'ICAI' },
  { id: '4', name: 'SHRM-CP', employee: 'Sneha Reddy', status: 'expiring', expiry: '2026-02-28', issuer: 'SHRM' },
  { id: '5', name: 'Google Cloud Professional', employee: 'Vikram Singh', status: 'expired', expiry: '2025-12-01', issuer: 'Google' },
]

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  expiring: 'bg-yellow-100 text-yellow-800',
  expired: 'bg-red-100 text-red-800',
}

export default function TrainingPage() {
  const [activeTab, setActiveTab] = useState('courses')

  const stats = {
    totalCourses: courses.length,
    mandatoryCourses: courses.filter(c => c.mandatory).length,
    avgCompletion: Math.round(courses.reduce((sum, c) => sum + (c.completed / c.enrolled * 100), 0) / courses.length),
    certifications: certifications.filter(c => c.status === 'active').length,
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Training & Development"
        description="Manage courses, certifications, and skill development"
        icon={<GraduationCap className="h-6 w-6" />}
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Course
          </Button>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BookOpen className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.totalCourses}</p>
                <p className="text-sm text-muted-foreground">Total Courses</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <Star className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.mandatoryCourses}</p>
                <p className="text-sm text-muted-foreground">Mandatory</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.avgCompletion}%</p>
                <p className="text-sm text-muted-foreground">Avg Completion</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Award className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.certifications}</p>
                <p className="text-sm text-muted-foreground">Active Certifications</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="courses">Courses</TabsTrigger>
          <TabsTrigger value="certifications">Certifications</TabsTrigger>
          <TabsTrigger value="skills">Skills Matrix</TabsTrigger>
        </TabsList>

        <TabsContent value="courses" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {courses.map((course) => (
              <Card key={course.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <Badge variant="outline">{course.category}</Badge>
                    {course.mandatory && <Badge variant="destructive">Mandatory</Badge>}
                  </div>
                  <CardTitle className="text-lg mt-2">{course.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" /> {course.duration}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="h-3 w-3" /> {course.enrolled} enrolled
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Completion</span>
                      <span>{Math.round(course.completed / course.enrolled * 100)}%</span>
                    </div>
                    <Progress value={course.completed / course.enrolled * 100} />
                  </div>
                  <Button className="w-full mt-4" variant="outline">
                    <Play className="h-4 w-4 mr-2" /> Start Course
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="certifications" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Employee Certifications</CardTitle>
              <CardDescription>Track professional certifications and expiry dates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-4 font-medium">Certification</th>
                      <th className="text-left p-4 font-medium">Employee</th>
                      <th className="text-left p-4 font-medium">Issuer</th>
                      <th className="text-center p-4 font-medium">Status</th>
                      <th className="text-left p-4 font-medium">Expiry</th>
                    </tr>
                  </thead>
                  <tbody>
                    {certifications.map((cert) => (
                      <tr key={cert.id} className="border-t hover:bg-muted/30">
                        <td className="p-4 font-medium">{cert.name}</td>
                        <td className="p-4">{cert.employee}</td>
                        <td className="p-4 text-muted-foreground">{cert.issuer}</td>
                        <td className="p-4 text-center">
                          <Badge className={statusColors[cert.status]}>{cert.status}</Badge>
                        </td>
                        <td className="p-4 text-muted-foreground">
                          {cert.expiry ? new Date(cert.expiry).toLocaleDateString('en-IN') : 'Never'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skills" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Skills Matrix</CardTitle>
              <CardDescription>Organization-wide skills assessment</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Skills matrix visualization coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
