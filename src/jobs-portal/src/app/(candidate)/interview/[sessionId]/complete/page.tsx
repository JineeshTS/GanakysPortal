"use client";

import { useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Loader2,
  CheckCircle2,
  Clock,
  TrendingUp,
  MessageSquare,
  Lightbulb,
  ArrowRight,
  Home,
} from "lucide-react";
import { interviewApi } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";

interface InterviewResult {
  session_id: string;
  status: string;
  overall_score: number | null;
  technical_score: number | null;
  communication_score: number | null;
  problem_solving_score: number | null;
  summary: string | null;
  strengths: string[];
  areas_for_improvement: string[];
}

function ScoreCard({
  label,
  score,
  icon: Icon,
  color,
}: {
  label: string;
  score: number | null;
  icon: React.ElementType;
  color: string;
}) {
  if (score === null) return null;

  const percentage = score * 10; // Convert 0-10 to 0-100

  return (
    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-5 h-5 ${color}`} />
        <span className="text-sm font-medium">{label}</span>
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold">{score.toFixed(1)}</span>
        <span className="text-sm text-muted-foreground mb-1">/10</span>
      </div>
      <Progress value={percentage} className="h-2 mt-2" />
    </div>
  );
}

export default function InterviewCompletePage() {
  const router = useRouter();
  const params = useParams();
  const sessionId = params.sessionId as string;
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();

  // Fetch results
  const {
    data: results,
    isLoading,
    error,
    refetch,
  } = useQuery<InterviewResult>({
    queryKey: ["interview-results", sessionId],
    queryFn: () => interviewApi.getResults(sessionId),
    enabled: isAuthenticated && !!sessionId,
    refetchInterval: (query) => {
      // Keep polling if evaluation is not complete
      const data = query.state.data;
      if (data?.status === "completed" || data?.status === "in_progress") {
        return 5000; // Poll every 5 seconds
      }
      return false;
    },
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push(`/login?redirect=/interview/${sessionId}/complete`);
    }
  }, [authLoading, isAuthenticated, router, sessionId]);

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-muted-foreground">Loading your results...</p>
        </div>
      </div>
    );
  }

  // Still evaluating
  if (results?.status === "completed" || results?.status === "in_progress") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="relative w-24 h-24 mx-auto mb-6">
                <div className="absolute inset-0 rounded-full border-4 border-blue-200 dark:border-blue-900" />
                <div className="absolute inset-0 rounded-full border-4 border-blue-500 border-t-transparent animate-spin" />
                <Clock className="absolute inset-0 m-auto w-10 h-10 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Evaluating Your Interview</h3>
              <p className="text-muted-foreground mb-6">
                Our AI is carefully reviewing your responses. This typically takes a few minutes.
              </p>
              <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing...</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Results ready
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-3xl mx-auto px-4">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
            <CheckCircle2 className="w-10 h-10 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-3xl font-bold mb-2">Interview Completed!</h1>
          <p className="text-muted-foreground">
            Thank you for completing your AI interview. Here are your results.
          </p>
        </div>

        {/* Overall Score */}
        {results && results.overall_score !== null && (
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-2">Overall Score</p>
                <div className="relative w-32 h-32 mx-auto">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="64"
                      cy="64"
                      r="56"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      className="text-gray-200 dark:text-gray-700"
                    />
                    <circle
                      cx="64"
                      cy="64"
                      r="56"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray={`${(results.overall_score / 10) * 352} 352`}
                      className="text-blue-500"
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-bold">
                      {results.overall_score.toFixed(1)}
                    </span>
                  </div>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">out of 10</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Score Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <ScoreCard
            label="Technical Skills"
            score={results?.technical_score ?? null}
            icon={TrendingUp}
            color="text-purple-500"
          />
          <ScoreCard
            label="Communication"
            score={results?.communication_score ?? null}
            icon={MessageSquare}
            color="text-blue-500"
          />
          <ScoreCard
            label="Problem Solving"
            score={results?.problem_solving_score ?? null}
            icon={Lightbulb}
            color="text-yellow-500"
          />
        </div>

        {/* Summary */}
        {results?.summary && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg">Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{results.summary}</p>
            </CardContent>
          </Card>
        )}

        {/* Strengths & Areas for Improvement */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {results?.strengths && results.strengths.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                  Strengths
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {results.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2" />
                      <span className="text-sm">{strength}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {results?.areas_for_improvement && results.areas_for_improvement.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-500" />
                  Areas for Growth
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {results.areas_for_improvement.map((area, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2" />
                      <span className="text-sm">{area}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Next Steps */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-lg">What&apos;s Next?</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Badge className="mt-0.5">1</Badge>
                <div>
                  <p className="font-medium">Review Process</p>
                  <p className="text-sm text-muted-foreground">
                    Our recruitment team will review your interview results along with your application.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Badge className="mt-0.5">2</Badge>
                <div>
                  <p className="font-medium">Next Round</p>
                  <p className="text-sm text-muted-foreground">
                    If selected, you&apos;ll be contacted for the next round of interviews with our team.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Badge className="mt-0.5">3</Badge>
                <div>
                  <p className="font-medium">Stay Updated</p>
                  <p className="text-sm text-muted-foreground">
                    Check your dashboard regularly for application status updates.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-center gap-4">
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            <Home className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          <Button onClick={() => router.push("/jobs")}>
            Browse More Jobs
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
}
