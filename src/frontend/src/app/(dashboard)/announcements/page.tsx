'use client'

import { useState } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Megaphone,
  Plus,
  Pin,
  Calendar,
  Users,
  Eye,
  Bell,
  FileText,
  AlertTriangle,
  PartyPopper,
  Building2
} from 'lucide-react'

const announcements = [
  { 
    id: '1', 
    title: 'Republic Day Holiday', 
    content: 'Office will remain closed on 26th January 2026 for Republic Day. Wishing everyone a happy Republic Day!',
    category: 'holiday',
    author: 'HR Team',
    date: '2026-01-12',
    pinned: true,
    views: 156,
    audience: 'All Employees'
  },
  { 
    id: '2', 
    title: 'New PF Contribution Limits for FY 2025-26', 
    content: 'As per the latest government notification, the PF contribution ceiling has been revised. Please check the updated policy document.',
    category: 'policy',
    author: 'Finance Team',
    date: '2026-01-10',
    pinned: true,
    views: 89,
    audience: 'All Employees'
  },
  { 
    id: '3', 
    title: 'Q4 Town Hall Meeting', 
    content: 'Join us for the quarterly town hall meeting on January 20th, 2026 at 3:00 PM IST. Link will be shared via email.',
    category: 'event',
    author: 'CEO Office',
    date: '2026-01-08',
    pinned: false,
    views: 234,
    audience: 'All Employees'
  },
  { 
    id: '4', 
    title: 'IT System Maintenance', 
    content: 'Scheduled maintenance on January 15th from 2:00 AM to 6:00 AM IST. Some services may be unavailable.',
    category: 'alert',
    author: 'IT Team',
    date: '2026-01-07',
    pinned: false,
    views: 178,
    audience: 'All Employees'
  },
  { 
    id: '5', 
    title: 'Welcome New Joiners - January 2026', 
    content: 'Please join us in welcoming our new team members: Rahul Verma (Engineering), Ananya Singh (HR), and Karthik Reddy (Sales).',
    category: 'celebration',
    author: 'HR Team',
    date: '2026-01-06',
    pinned: false,
    views: 145,
    audience: 'All Employees'
  },
  { 
    id: '6', 
    title: 'Updated Travel Reimbursement Policy', 
    content: 'Please review the updated travel and reimbursement policy effective from January 2026. Key changes include revised per diem rates.',
    category: 'policy',
    author: 'Finance Team',
    date: '2026-01-05',
    pinned: false,
    views: 67,
    audience: 'All Employees'
  },
]

const policies = [
  { id: '1', title: 'Employee Handbook 2026', category: 'General', lastUpdated: '2026-01-01', downloads: 234 },
  { id: '2', title: 'Leave Policy', category: 'HR', lastUpdated: '2025-12-15', downloads: 189 },
  { id: '3', title: 'Travel & Expense Policy', category: 'Finance', lastUpdated: '2026-01-05', downloads: 156 },
  { id: '4', title: 'Code of Conduct', category: 'General', lastUpdated: '2025-11-01', downloads: 298 },
  { id: '5', title: 'IT Security Policy', category: 'IT', lastUpdated: '2025-10-15', downloads: 145 },
  { id: '6', title: 'Anti-Harassment Policy', category: 'HR', lastUpdated: '2025-09-01', downloads: 267 },
]

const categoryIcons: Record<string, React.ReactNode> = {
  holiday: <Calendar className="h-4 w-4" />,
  policy: <FileText className="h-4 w-4" />,
  event: <Users className="h-4 w-4" />,
  alert: <AlertTriangle className="h-4 w-4" />,
  celebration: <PartyPopper className="h-4 w-4" />,
}

const categoryColors: Record<string, string> = {
  holiday: 'bg-green-100 text-green-800',
  policy: 'bg-blue-100 text-blue-800',
  event: 'bg-purple-100 text-purple-800',
  alert: 'bg-red-100 text-red-800',
  celebration: 'bg-yellow-100 text-yellow-800',
}

export default function AnnouncementsPage() {
  const [activeTab, setActiveTab] = useState('announcements')

  return (
    <div className="space-y-6">
      <PageHeader
        title="Announcements & Policies"
        description="Company news, updates, and policy documents"
        icon={Megaphone}
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Announcement
          </Button>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Megaphone className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{announcements.length}</p>
                <p className="text-sm text-muted-foreground">Announcements</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Pin className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{announcements.filter(a => a.pinned).length}</p>
                <p className="text-sm text-muted-foreground">Pinned</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <FileText className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{policies.length}</p>
                <p className="text-sm text-muted-foreground">Policies</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Eye className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{announcements.reduce((sum, a) => sum + a.views, 0)}</p>
                <p className="text-sm text-muted-foreground">Total Views</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="announcements">Announcements</TabsTrigger>
          <TabsTrigger value="policies">Policies</TabsTrigger>
        </TabsList>

        <TabsContent value="announcements" className="mt-4">
          <div className="space-y-4">
            {announcements.map((announcement) => (
              <Card key={announcement.id} className={announcement.pinned ? 'border-primary' : ''}>
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {announcement.pinned && <Pin className="h-4 w-4 text-primary" />}
                      <Badge className={categoryColors[announcement.category]}>
                        <span className="flex items-center gap-1">
                          {categoryIcons[announcement.category]}
                          {announcement.category}
                        </span>
                      </Badge>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(announcement.date).toLocaleDateString('en-IN')}
                    </span>
                  </div>
                  <CardTitle className="text-lg">{announcement.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">{announcement.content}</p>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        <Building2 className="h-3 w-3" /> {announcement.author}
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="h-3 w-3" /> {announcement.audience}
                      </span>
                    </div>
                    <span className="flex items-center gap-1">
                      <Eye className="h-3 w-3" /> {announcement.views} views
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="policies" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Policy Documents</CardTitle>
              <CardDescription>Company policies and guidelines</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-4 font-medium">Document</th>
                      <th className="text-left p-4 font-medium">Category</th>
                      <th className="text-left p-4 font-medium">Last Updated</th>
                      <th className="text-center p-4 font-medium">Downloads</th>
                      <th className="text-right p-4 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {policies.map((policy) => (
                      <tr key={policy.id} className="border-t hover:bg-muted/30">
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">{policy.title}</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <Badge variant="outline">{policy.category}</Badge>
                        </td>
                        <td className="p-4 text-muted-foreground">
                          {new Date(policy.lastUpdated).toLocaleDateString('en-IN')}
                        </td>
                        <td className="p-4 text-center">{policy.downloads}</td>
                        <td className="p-4 text-right">
                          <Button variant="outline" size="sm">Download</Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
