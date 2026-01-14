'use client'

import { useState } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Award,
  Plus,
  Target,
  TrendingUp,
  Star,
  Calendar,
  Users,
  CheckCircle,
  Clock,
  MessageSquare
} from 'lucide-react'

const reviews = [
  { id: '1', employee: 'Rajesh Kumar', department: 'Engineering', reviewer: 'Suresh Iyer', status: 'completed', rating: 4.5, period: 'Q4 2025' },
  { id: '2', employee: 'Priya Sharma', department: 'HR', reviewer: 'Neha Gupta', status: 'in_progress', rating: null, period: 'Q4 2025' },
  { id: '3', employee: 'Amit Patel', department: 'Finance', reviewer: 'Arjun Mehta', status: 'pending', rating: null, period: 'Q4 2025' },
  { id: '4', employee: 'Sneha Reddy', department: 'Sales', reviewer: 'Rohit Verma', status: 'completed', rating: 4.8, period: 'Q4 2025' },
  { id: '5', employee: 'Vikram Singh', department: 'Marketing', reviewer: 'Divya Krishnan', status: 'completed', rating: 4.2, period: 'Q4 2025' },
]

const goals = [
  { id: '1', title: 'Increase sales by 20%', employee: 'Sneha Reddy', progress: 85, dueDate: '2026-03-31', status: 'on_track' },
  { id: '2', title: 'Complete AWS certification', employee: 'Rajesh Kumar', progress: 60, dueDate: '2026-02-28', status: 'on_track' },
  { id: '3', title: 'Reduce employee turnover to 10%', employee: 'Priya Sharma', progress: 45, dueDate: '2026-03-31', status: 'at_risk' },
  { id: '4', title: 'Implement new accounting system', employee: 'Amit Patel', progress: 30, dueDate: '2026-01-31', status: 'behind' },
  { id: '5', title: 'Launch 3 marketing campaigns', employee: 'Vikram Singh', progress: 100, dueDate: '2025-12-31', status: 'completed' },
]

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  in_progress: 'bg-blue-100 text-blue-800',
  pending: 'bg-gray-100 text-gray-800',
  on_track: 'bg-green-100 text-green-800',
  at_risk: 'bg-yellow-100 text-yellow-800',
  behind: 'bg-red-100 text-red-800',
}

export default function PerformancePage() {
  const [activeTab, setActiveTab] = useState('reviews')

  const stats = {
    reviewsCompleted: reviews.filter(r => r.status === 'completed').length,
    reviewsPending: reviews.filter(r => r.status !== 'completed').length,
    avgRating: (reviews.filter(r => r.rating).reduce((sum, r) => sum + (r.rating || 0), 0) / reviews.filter(r => r.rating).length).toFixed(1),
    goalsOnTrack: goals.filter(g => g.status === 'on_track' || g.status === 'completed').length,
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Performance Management"
        description="Reviews, goals, and feedback"
        icon={<Award className="h-6 w-6" />}
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Start Review Cycle
          </Button>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.reviewsCompleted}</p>
                <p className="text-sm text-muted-foreground">Reviews Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.reviewsPending}</p>
                <p className="text-sm text-muted-foreground">Reviews Pending</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Star className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.avgRating}</p>
                <p className="text-sm text-muted-foreground">Avg Rating</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Target className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.goalsOnTrack}/{goals.length}</p>
                <p className="text-sm text-muted-foreground">Goals On Track</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="reviews">Performance Reviews</TabsTrigger>
          <TabsTrigger value="goals">Goals & OKRs</TabsTrigger>
          <TabsTrigger value="feedback">360° Feedback</TabsTrigger>
        </TabsList>

        <TabsContent value="reviews" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Q4 2025 Reviews</CardTitle>
              <CardDescription>Current review cycle status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-4 font-medium">Employee</th>
                      <th className="text-left p-4 font-medium">Department</th>
                      <th className="text-left p-4 font-medium">Reviewer</th>
                      <th className="text-center p-4 font-medium">Status</th>
                      <th className="text-center p-4 font-medium">Rating</th>
                      <th className="text-right p-4 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reviews.map((review) => (
                      <tr key={review.id} className="border-t hover:bg-muted/30">
                        <td className="p-4 font-medium">{review.employee}</td>
                        <td className="p-4 text-muted-foreground">{review.department}</td>
                        <td className="p-4">{review.reviewer}</td>
                        <td className="p-4 text-center">
                          <Badge className={statusColors[review.status]}>
                            {review.status.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="p-4 text-center">
                          {review.rating ? (
                            <span className="font-medium">{review.rating} <Star className="h-3 w-3 inline text-yellow-500" /></span>
                          ) : '-'}
                        </td>
                        <td className="p-4 text-right">
                          <Button variant="outline" size="sm">
                            {review.status === 'completed' ? 'View' : 'Continue'}
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="goals" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Goals & Objectives</CardTitle>
              <CardDescription>Track progress on individual and team goals</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {goals.map((goal) => (
                  <div key={goal.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-medium">{goal.title}</h4>
                        <p className="text-sm text-muted-foreground">{goal.employee}</p>
                      </div>
                      <Badge className={statusColors[goal.status]}>
                        {goal.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <Progress value={goal.progress} />
                      </div>
                      <span className="text-sm font-medium w-12">{goal.progress}%</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-2">
                      Due: {new Date(goal.dueDate).toLocaleDateString('en-IN')}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="feedback" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>360° Feedback</CardTitle>
              <CardDescription>Collect feedback from peers, managers, and direct reports</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No active feedback cycles</p>
                <Button className="mt-4">
                  <Plus className="h-4 w-4 mr-2" />
                  Start Feedback Cycle
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
