'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { publicApi } from '@/lib/api';
import { useIsAuthenticated } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import {
  ArrowLeft,
  MapPin,
  Briefcase,
  Clock,
  Building2,
  DollarSign,
  Calendar,
  Share2,
  Bookmark,
} from 'lucide-react';
import { formatDate, formatCurrency } from '@/lib/utils';

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const isAuthenticated = useIsAuthenticated();
  const jobId = params.id as string;

  const { data: job, isLoading, error } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => publicApi.getJob(jobId),
    enabled: !!jobId,
  });

  const handleApply = () => {
    if (isAuthenticated) {
      router.push(`/applications/new?job=${jobId}`);
    } else {
      router.push(`/login?redirect=/jobs/${jobId}`);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <Skeleton className="mb-4 h-8 w-48" />
          <Skeleton className="mb-8 h-12 w-2/3" />
          <div className="grid gap-8 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <Skeleton className="h-96 w-full" />
            </div>
            <div>
              <Skeleton className="h-48 w-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="rounded-lg border border-red-200 bg-red-50 p-8 text-center">
            <h2 className="mb-2 text-lg font-semibold text-red-600">Job Not Found</h2>
            <p className="mb-4 text-red-600">The job you&apos;re looking for doesn&apos;t exist or has been removed.</p>
            <Link href="/">
              <Button>Back to Jobs</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center space-x-2">
            <Building2 className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">GanaPortal Jobs</span>
          </Link>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <Link href="/dashboard">
                <Button variant="ghost">Dashboard</Button>
              </Link>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost">Sign In</Button>
                </Link>
                <Link href="/register">
                  <Button>Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Back Button */}
        <Link href="/" className="mb-6 inline-flex items-center text-sm text-gray-600 hover:text-gray-900">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Jobs
        </Link>

        {/* Job Header */}
        <div className="mb-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="mb-2 text-3xl font-bold">{job.title}</h1>
              <p className="flex items-center gap-2 text-lg text-gray-600">
                <Building2 className="h-5 w-5" />
                {job.company_name || 'Company'}
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="icon">
                <Share2 className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Bookmark className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Card>
              <CardContent className="p-6">
                {/* Job Highlights */}
                <div className="mb-6 flex flex-wrap gap-4">
                  {job.location && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <MapPin className="h-5 w-5" />
                      <span>{job.location}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-gray-600">
                    <Briefcase className="h-5 w-5" />
                    <span>
                      {job.job_type?.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase()) || 'Full Time'}
                    </span>
                  </div>
                  {(job.experience_min !== undefined || job.experience_max !== undefined) && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <Clock className="h-5 w-5" />
                      <span>{job.experience_min || 0} - {job.experience_max || '10+'} years</span>
                    </div>
                  )}
                  {job.is_remote && (
                    <Badge variant="secondary">Remote Available</Badge>
                  )}
                </div>

                <Separator className="my-6" />

                {/* Description */}
                {job.description && (
                  <div className="mb-6">
                    <h2 className="mb-3 text-xl font-semibold">Job Description</h2>
                    <div className="prose prose-gray max-w-none whitespace-pre-line">
                      {job.description}
                    </div>
                  </div>
                )}

                {/* Requirements */}
                {job.requirements && (
                  <div className="mb-6">
                    <h2 className="mb-3 text-xl font-semibold">Requirements</h2>
                    <div className="prose prose-gray max-w-none whitespace-pre-line">
                      {job.requirements}
                    </div>
                  </div>
                )}

                {/* Responsibilities */}
                {job.responsibilities && (
                  <div className="mb-6">
                    <h2 className="mb-3 text-xl font-semibold">Responsibilities</h2>
                    <div className="prose prose-gray max-w-none whitespace-pre-line">
                      {job.responsibilities}
                    </div>
                  </div>
                )}

                {/* Skills */}
                {job.skills_required && (
                  <div>
                    <h2 className="mb-3 text-xl font-semibold">Required Skills</h2>
                    <div className="flex flex-wrap gap-2">
                      {job.skills_required.split(',').map((skill, index) => (
                        <Badge key={index} variant="outline">
                          {skill.trim()}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Apply Card */}
            <Card>
              <CardHeader>
                <CardTitle>Apply for this job</CardTitle>
              </CardHeader>
              <CardContent>
                <Button onClick={handleApply} className="w-full" size="lg">
                  Apply Now
                </Button>
                {!isAuthenticated && (
                  <p className="mt-2 text-center text-sm text-gray-500">
                    You&apos;ll need to sign in first
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Job Details Card */}
            <Card>
              <CardHeader>
                <CardTitle>Job Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {(job.salary_min || job.salary_max) && (
                  <div className="flex items-start gap-3">
                    <DollarSign className="mt-0.5 h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">Salary Range</p>
                      <p className="text-sm text-gray-600">
                        {job.salary_min ? formatCurrency(job.salary_min) : ''}
                        {job.salary_min && job.salary_max ? ' - ' : ''}
                        {job.salary_max ? formatCurrency(job.salary_max) : ''}
                        <span className="text-gray-400"> / year</span>
                      </p>
                    </div>
                  </div>
                )}

                {job.department && (
                  <div className="flex items-start gap-3">
                    <Building2 className="mt-0.5 h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">Department</p>
                      <p className="text-sm text-gray-600">{job.department}</p>
                    </div>
                  </div>
                )}

                {job.posted_date && (
                  <div className="flex items-start gap-3">
                    <Calendar className="mt-0.5 h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">Posted On</p>
                      <p className="text-sm text-gray-600">{formatDate(job.posted_date)}</p>
                    </div>
                  </div>
                )}

                {job.closing_date && (
                  <div className="flex items-start gap-3">
                    <Calendar className="mt-0.5 h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">Application Deadline</p>
                      <p className="text-sm text-gray-600">{formatDate(job.closing_date)}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
