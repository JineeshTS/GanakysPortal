'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { publicApi, type Job } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Search, MapPin, Briefcase, Clock, Building2, DollarSign } from 'lucide-react';
import { formatDate, formatCurrency } from '@/lib/utils';

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [location, setLocation] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['jobs', { search: searchQuery, location }],
    queryFn: () =>
      publicApi.getJobs({
        ...(searchQuery && { search: searchQuery }),
        ...(location && { location }),
        status: 'published',
      }),
  });

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center space-x-2">
            <Building2 className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">GanaPortal Jobs</span>
          </Link>
          <div className="flex items-center space-x-4">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 text-center">
        <div className="container mx-auto px-4">
          <h1 className="mb-4 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            Find Your Dream Job
          </h1>
          <p className="mb-8 text-lg text-gray-600">
            Discover opportunities that match your skills and aspirations
          </p>

          {/* Search Bar */}
          <div className="mx-auto flex max-w-3xl flex-col gap-4 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <Input
                type="text"
                placeholder="Job title, keywords, or company"
                className="h-12 pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="relative flex-1">
              <MapPin className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
              <Input
                type="text"
                placeholder="Location"
                className="h-12 pl-10"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
            <Button size="lg" className="h-12 px-8">
              Search Jobs
            </Button>
          </div>
        </div>
      </section>

      {/* Job Listings */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="mb-8 flex items-center justify-between">
            <h2 className="text-2xl font-bold">
              {data?.total ? `${data.total} Jobs Found` : 'Latest Opportunities'}
            </h2>
          </div>

          {isLoading && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="mb-2 h-4 w-full" />
                    <Skeleton className="h-4 w-2/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center text-red-600">
              Failed to load jobs. Please try again.
            </div>
          )}

          {data?.items && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {data.items.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          )}

          {data?.items?.length === 0 && (
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-8 text-center">
              <Briefcase className="mx-auto mb-4 h-12 w-12 text-gray-400" />
              <h3 className="mb-2 text-lg font-semibold">No jobs found</h3>
              <p className="text-gray-600">
                Try adjusting your search criteria or check back later for new opportunities.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-gray-50 py-8">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>&copy; {new Date().getFullYear()} GanaPortal. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function JobCard({ job }: { job: Job }) {
  return (
    <Link href={`/jobs/${job.id}`}>
      <Card className="h-full transition-shadow hover:shadow-lg">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-lg">{job.title}</CardTitle>
              <CardDescription className="flex items-center gap-1">
                <Building2 className="h-4 w-4" />
                {job.company_name || 'Company'}
              </CardDescription>
            </div>
            {job.is_remote && (
              <Badge variant="secondary">Remote</Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-gray-600">
            {job.location && (
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                {job.location}
              </div>
            )}
            <div className="flex items-center gap-2">
              <Briefcase className="h-4 w-4" />
              {job.job_type?.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase()) || 'Full Time'}
            </div>
            {(job.experience_min !== undefined || job.experience_max !== undefined) && (
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                {job.experience_min || 0} - {job.experience_max || '10+'} years
              </div>
            )}
            {(job.salary_min || job.salary_max) && (
              <div className="flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                {job.salary_min ? formatCurrency(job.salary_min) : ''}
                {job.salary_min && job.salary_max ? ' - ' : ''}
                {job.salary_max ? formatCurrency(job.salary_max) : ''}
              </div>
            )}
          </div>
          {job.posted_date && (
            <p className="mt-4 text-xs text-gray-400">
              Posted {formatDate(job.posted_date)}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
