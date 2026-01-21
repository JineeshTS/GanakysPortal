'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useToken } from '@/lib/auth';
import { applicationApi, interviewApi, candidateApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import {
  FileText,
  Video,
  Search,
  Calendar,
  CheckCircle2,
  Clock,
  AlertCircle,
} from 'lucide-react';
import { formatDate } from '@/lib/utils';

export default function DashboardPage() {
  const token = useToken();

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['candidate-profile'],
    queryFn: () => candidateApi.getProfile(token!),
    enabled: !!token,
  });

  const { data: applications, isLoading: appsLoading } = useQuery({
    queryKey: ['candidate-applications'],
    queryFn: () => applicationApi.getApplications(token!),
    enabled: !!token,
  });

  const { data: interviews, isLoading: interviewsLoading } = useQuery({
    queryKey: ['candidate-interviews'],
    queryFn: () => interviewApi.getInterviews(token!),
    enabled: !!token,
  });

  const upcomingInterviews = interviews?.filter(
    (i) => i.status === 'scheduled' && i.scheduled_at
  );

  const activeApplications = applications?.filter(
    (a) => a.status !== 'rejected' && a.status !== 'withdrawn'
  );

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            Welcome back{profile?.first_name ? `, ${profile.first_name}` : ''}!
          </h1>
          <p className="text-gray-600">Track your job applications and interviews</p>
        </div>
        <Link href="/">
          <Button>
            <Search className="mr-2 h-4 w-4" />
            Browse Jobs
          </Button>
        </Link>
      </div>

      {/* Profile Completeness */}
      {profileLoading ? (
        <Skeleton className="h-24 w-full" />
      ) : (
        profile && profile.profile_completeness < 100 && (
          <Card className="border-yellow-200 bg-yellow-50">
            <CardContent className="py-4">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h3 className="font-medium">Complete your profile</h3>
                  <p className="text-sm text-gray-600">
                    A complete profile increases your chances of getting hired
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-32">
                    <Progress value={profile.profile_completeness} />
                  </div>
                  <span className="text-sm font-medium">
                    {profile.profile_completeness}%
                  </span>
                  <Link href="/profile">
                    <Button size="sm" variant="outline">
                      Complete Profile
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      )}

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 py-6">
            <div className="rounded-full bg-blue-100 p-3">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {appsLoading ? '-' : applications?.length || 0}
              </p>
              <p className="text-sm text-gray-600">Total Applications</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4 py-6">
            <div className="rounded-full bg-green-100 p-3">
              <CheckCircle2 className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {appsLoading ? '-' : activeApplications?.length || 0}
              </p>
              <p className="text-sm text-gray-600">Active Applications</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4 py-6">
            <div className="rounded-full bg-purple-100 p-3">
              <Video className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {interviewsLoading ? '-' : upcomingInterviews?.length || 0}
              </p>
              <p className="text-sm text-gray-600">Upcoming Interviews</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="flex items-center gap-4 py-6">
            <div className="rounded-full bg-orange-100 p-3">
              <Clock className="h-6 w-6 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {interviewsLoading
                  ? '-'
                  : interviews?.filter((i) => i.status === 'completed').length || 0}
              </p>
              <p className="text-sm text-gray-600">Completed Interviews</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Content Grid */}
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Recent Applications */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Applications</CardTitle>
            <CardDescription>Your latest job applications</CardDescription>
          </CardHeader>
          <CardContent>
            {appsLoading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : applications?.length === 0 ? (
              <div className="py-8 text-center">
                <FileText className="mx-auto mb-4 h-12 w-12 text-gray-300" />
                <p className="text-gray-500">No applications yet</p>
                <Link href="/">
                  <Button variant="link">Browse jobs to apply</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {applications?.slice(0, 5).map((app) => (
                  <Link
                    key={app.id}
                    href={`/applications/${app.id}`}
                    className="block"
                  >
                    <div className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-gray-50">
                      <div>
                        <h4 className="font-medium">{app.job?.title || 'Job'}</h4>
                        <p className="text-sm text-gray-500">
                          Applied {formatDate(app.applied_date)}
                        </p>
                      </div>
                      <ApplicationStatusBadge status={app.status} />
                    </div>
                  </Link>
                ))}
                {applications && applications.length > 5 && (
                  <Link href="/applications">
                    <Button variant="ghost" className="w-full">
                      View all applications
                    </Button>
                  </Link>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Upcoming Interviews */}
        <Card>
          <CardHeader>
            <CardTitle>Upcoming Interviews</CardTitle>
            <CardDescription>Your scheduled interviews</CardDescription>
          </CardHeader>
          <CardContent>
            {interviewsLoading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : upcomingInterviews?.length === 0 ? (
              <div className="py-8 text-center">
                <Video className="mx-auto mb-4 h-12 w-12 text-gray-300" />
                <p className="text-gray-500">No upcoming interviews</p>
              </div>
            ) : (
              <div className="space-y-4">
                {upcomingInterviews?.map((interview) => (
                  <Link
                    key={interview.id}
                    href={`/interviews/${interview.id}`}
                    className="block"
                  >
                    <div className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-gray-50">
                      <div>
                        <h4 className="font-medium capitalize">
                          {interview.session_type} Interview
                        </h4>
                        <p className="flex items-center gap-1 text-sm text-gray-500">
                          <Calendar className="h-4 w-4" />
                          {interview.scheduled_at
                            ? formatDate(interview.scheduled_at)
                            : 'TBD'}
                        </p>
                      </div>
                      <Badge>Scheduled</Badge>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function ApplicationStatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; label: string }> = {
    applied: { variant: 'outline', label: 'Applied' },
    screening: { variant: 'secondary', label: 'Screening' },
    interview: { variant: 'default', label: 'Interview' },
    offer: { variant: 'default', label: 'Offer' },
    hired: { variant: 'default', label: 'Hired' },
    rejected: { variant: 'destructive', label: 'Rejected' },
    withdrawn: { variant: 'outline', label: 'Withdrawn' },
  };

  const config = statusConfig[status] || { variant: 'outline' as const, label: status };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}
