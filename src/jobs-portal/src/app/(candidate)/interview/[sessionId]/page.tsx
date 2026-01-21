"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import dynamic from "next/dynamic";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import {
  Loader2,
  Video,
  Mic,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";
import { interviewApi } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";

// Dynamically import InterviewRoom to avoid SSR issues with Daily.co
const InterviewRoom = dynamic(
  () => import("@/components/interview/InterviewRoom"),
  { ssr: false }
);

interface InterviewSession {
  id: string;
  application_id: string;
  status: string;
  room_url: string | null;
  room_token: string | null;
  scheduled_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  current_question_index: number;
  total_questions: number;
}

interface InterviewQuestion {
  id: string;
  question_text: string;
  question_type: string;
  category: string;
  order_num: number;
  max_duration_seconds: number;
  is_current: boolean;
}

export default function InterviewPage() {
  const router = useRouter();
  const params = useParams();
  const sessionId = params.sessionId as string;
  const { isAuthenticated, isLoading: authLoading } = useAuthStore();

  const [hasStarted, setHasStarted] = useState(false);
  const [devicePermissions, setDevicePermissions] = useState({
    camera: false,
    microphone: false,
  });
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [checkingPermissions, setCheckingPermissions] = useState(true);

  // Fetch session details
  const {
    data: session,
    isLoading: sessionLoading,
    error: sessionError,
    refetch: refetchSession,
  } = useQuery<InterviewSession>({
    queryKey: ["interview-session", sessionId],
    queryFn: () => interviewApi.getSession(sessionId),
    enabled: isAuthenticated && !!sessionId,
  });

  // Fetch questions
  const { data: questions, isLoading: questionsLoading } = useQuery<InterviewQuestion[]>({
    queryKey: ["interview-questions", sessionId],
    queryFn: () => interviewApi.getQuestions(sessionId),
    enabled: isAuthenticated && !!sessionId && session?.status !== "completed",
  });

  // Begin interview mutation
  const beginMutation = useMutation({
    mutationFn: () => interviewApi.beginInterview(sessionId),
    onSuccess: () => {
      setHasStarted(true);
      refetchSession();
    },
  });

  // Submit answer mutation
  const submitAnswerMutation = useMutation({
    mutationFn: (data: { questionId: string; transcript: string; duration: number }) =>
      interviewApi.submitAnswer(sessionId, data.questionId, data.transcript, data.duration),
  });

  // Check device permissions
  useEffect(() => {
    async function checkPermissions() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });

        setDevicePermissions({
          camera: true,
          microphone: true,
        });

        // Stop tracks after checking
        stream.getTracks().forEach((track) => track.stop());
      } catch (err) {
        console.error("Permission error:", err);
        // Check individual permissions
        try {
          const videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
          setDevicePermissions((prev) => ({ ...prev, camera: true }));
          videoStream.getTracks().forEach((track) => track.stop());
        } catch {
          // No camera permission
        }

        try {
          const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
          setDevicePermissions((prev) => ({ ...prev, microphone: true }));
          audioStream.getTracks().forEach((track) => track.stop());
        } catch {
          // No microphone permission
        }
      } finally {
        setCheckingPermissions(false);
      }
    }

    checkPermissions();
  }, []);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push(`/login?redirect=/interview/${sessionId}`);
    }
  }, [authLoading, isAuthenticated, router, sessionId]);

  const handleSubmitAnswer = async (
    questionId: string,
    transcript: string,
    duration: number
  ): Promise<InterviewQuestion | null> => {
    const result = await submitAnswerMutation.mutateAsync({
      questionId,
      transcript,
      duration,
    });

    return result.next_question || null;
  };

  const handleInterviewComplete = () => {
    router.push(`/interview/${sessionId}/complete`);
  };

  const handleStartInterview = () => {
    beginMutation.mutate();
  };

  if (authLoading || sessionLoading || checkingPermissions) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-500" />
          <p className="text-muted-foreground">Loading interview...</p>
        </div>
      </div>
    );
  }

  if (sessionError) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Session Not Found</h3>
              <p className="text-muted-foreground mb-4">
                This interview session doesn&apos;t exist or you don&apos;t have access to it.
              </p>
              <Button onClick={() => router.push("/dashboard")}>
                Back to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (session?.status === "completed" || session?.status === "evaluated") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircle2 className="w-12 h-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Interview Completed</h3>
              <p className="text-muted-foreground mb-4">
                Your interview has been completed. View your results below.
              </p>
              <Button onClick={() => router.push(`/interview/${sessionId}/complete`)}>
                View Results
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // If interview has started, show the interview room
  if (hasStarted && session?.room_url && session?.room_token && questions) {
    return (
      <InterviewRoom
        roomUrl={session.room_url}
        roomToken={session.room_token}
        sessionId={sessionId}
        questions={questions}
        onInterviewComplete={handleInterviewComplete}
        onSubmitAnswer={handleSubmitAnswer}
      />
    );
  }

  // Pre-interview screen
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="max-w-2xl mx-auto px-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">AI Interview</CardTitle>
            <CardDescription>
              Complete your AI-powered interview for this position
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Interview Info */}
            <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Interview Details</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Questions:</span>
                  <span className="ml-2 font-medium">{session?.total_questions || 8}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Duration:</span>
                  <span className="ml-2 font-medium">~25-30 minutes</span>
                </div>
              </div>
            </div>

            {/* Device Permissions */}
            <div>
              <h3 className="font-semibold mb-3">Device Check</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      devicePermissions.camera
                        ? "bg-green-100 text-green-600"
                        : "bg-red-100 text-red-600"
                    }`}
                  >
                    <Video className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-medium">Camera</p>
                    <p className="text-sm text-muted-foreground">
                      {devicePermissions.camera
                        ? "Camera access granted"
                        : "Please enable camera access"}
                    </p>
                  </div>
                  {devicePermissions.camera && (
                    <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      devicePermissions.microphone
                        ? "bg-green-100 text-green-600"
                        : "bg-red-100 text-red-600"
                    }`}
                  >
                    <Mic className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-medium">Microphone</p>
                    <p className="text-sm text-muted-foreground">
                      {devicePermissions.microphone
                        ? "Microphone access granted"
                        : "Please enable microphone access"}
                    </p>
                  </div>
                  {devicePermissions.microphone && (
                    <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
                  )}
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div>
              <h3 className="font-semibold mb-3">Instructions</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <Clock className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  Each question has a time limit. Answer within the allotted time.
                </li>
                <li className="flex items-start gap-2">
                  <Video className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  Your video and audio will be recorded for evaluation.
                </li>
                <li className="flex items-start gap-2">
                  <Mic className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  Speak clearly and at a moderate pace.
                </li>
              </ul>
            </div>

            {/* Terms Agreement */}
            <div className="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <Checkbox
                id="terms"
                checked={agreedToTerms}
                onCheckedChange={(checked) => setAgreedToTerms(checked as boolean)}
              />
              <Label htmlFor="terms" className="text-sm leading-relaxed cursor-pointer">
                I understand that this interview will be recorded and my responses will
                be evaluated using AI technology. I agree to participate honestly and
                authentically.
              </Label>
            </div>

            {/* Start Button */}
            <Button
              size="lg"
              className="w-full"
              disabled={
                !devicePermissions.camera ||
                !devicePermissions.microphone ||
                !agreedToTerms ||
                beginMutation.isPending
              }
              onClick={handleStartInterview}
            >
              {beginMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  Start Interview
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>

            {(!devicePermissions.camera || !devicePermissions.microphone) && (
              <p className="text-sm text-red-500 text-center">
                Please grant camera and microphone permissions to continue.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
