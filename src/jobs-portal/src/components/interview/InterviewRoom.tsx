"use client";

import { useCallback, useEffect, useState, useRef } from "react";
import {
  DailyProvider,
  useDaily,
  useLocalSessionId,
  useParticipantIds,
  useVideoTrack,
  useAudioTrack,
  useDailyEvent,
  useScreenShare,
} from "@daily-co/daily-react";
import DailyIframe, { DailyCall } from "@daily-co/daily-js";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import {
  Mic,
  MicOff,
  Video,
  VideoOff,
  PhoneOff,
  Loader2,
  Clock,
  ChevronRight,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface InterviewQuestion {
  id: string;
  question_text: string;
  question_type: string;
  category: string;
  order_num: number;
  max_duration_seconds: number;
  is_current: boolean;
}

interface InterviewRoomProps {
  roomUrl: string;
  roomToken: string;
  sessionId: string;
  questions: InterviewQuestion[];
  onInterviewComplete: () => void;
  onSubmitAnswer: (questionId: string, transcript: string, duration: number) => Promise<InterviewQuestion | null>;
}

function VideoTile({ sessionId, isLocal = false }: { sessionId: string; isLocal?: boolean }) {
  const videoTrack = useVideoTrack(sessionId);
  const audioTrack = useAudioTrack(sessionId);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoTrack?.track && videoRef.current) {
      videoRef.current.srcObject = new MediaStream([videoTrack.track]);
    }
  }, [videoTrack?.track]);

  return (
    <div className={cn(
      "relative rounded-lg overflow-hidden bg-gray-900",
      isLocal ? "w-48 h-36 absolute bottom-4 right-4 z-10" : "w-full h-full"
    )}>
      {videoTrack?.state === "playable" ? (
        <video
          ref={videoRef}
          autoPlay
          muted={isLocal}
          playsInline
          className="w-full h-full object-cover"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gray-800">
          <div className="w-20 h-20 rounded-full bg-gray-700 flex items-center justify-center">
            <span className="text-2xl text-white">
              {isLocal ? "You" : "AI"}
            </span>
          </div>
        </div>
      )}
      {!isLocal && audioTrack?.state !== "playable" && (
        <div className="absolute top-2 left-2">
          <MicOff className="w-4 h-4 text-red-500" />
        </div>
      )}
    </div>
  );
}

function InterviewControls({
  onLeave,
  isRecording = false,
}: {
  onLeave: () => void;
  isRecording?: boolean;
}) {
  const daily = useDaily();
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);

  const toggleMic = useCallback(() => {
    if (daily) {
      daily.setLocalAudio(!isMuted);
      setIsMuted(!isMuted);
    }
  }, [daily, isMuted]);

  const toggleVideo = useCallback(() => {
    if (daily) {
      daily.setLocalVideo(!isVideoOff);
      setIsVideoOff(!isVideoOff);
    }
  }, [daily, isVideoOff]);

  return (
    <div className="flex items-center justify-center gap-4 p-4 bg-gray-900 rounded-lg">
      <Button
        variant={isMuted ? "destructive" : "secondary"}
        size="icon"
        onClick={toggleMic}
        className="rounded-full w-12 h-12"
      >
        {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
      </Button>
      <Button
        variant={isVideoOff ? "destructive" : "secondary"}
        size="icon"
        onClick={toggleVideo}
        className="rounded-full w-12 h-12"
      >
        {isVideoOff ? <VideoOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
      </Button>
      <Button
        variant="destructive"
        size="icon"
        onClick={onLeave}
        className="rounded-full w-12 h-12"
      >
        <PhoneOff className="w-5 h-5" />
      </Button>
      {isRecording && (
        <Badge variant="destructive" className="animate-pulse">
          Recording
        </Badge>
      )}
    </div>
  );
}

function QuestionPanel({
  currentQuestion,
  questionIndex,
  totalQuestions,
  timeRemaining,
  onNextQuestion,
  isAnswering,
  transcript,
}: {
  currentQuestion: InterviewQuestion | null;
  questionIndex: number;
  totalQuestions: number;
  timeRemaining: number;
  onNextQuestion: () => void;
  isAnswering: boolean;
  transcript: string;
}) {
  const progress = ((questionIndex + 1) / totalQuestions) * 100;
  const timeProgress = currentQuestion
    ? (timeRemaining / currentQuestion.max_duration_seconds) * 100
    : 100;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Interview Progress</CardTitle>
          <Badge variant="outline">
            {questionIndex + 1} of {totalQuestions}
          </Badge>
        </div>
        <Progress value={progress} className="h-2" />
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4">
        {currentQuestion ? (
          <>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="secondary">{currentQuestion.category}</Badge>
              <Badge variant="outline">{currentQuestion.question_type}</Badge>
            </div>

            <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg flex-1">
              <p className="text-lg font-medium text-blue-900 dark:text-blue-100">
                {currentQuestion.question_text}
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  Time Remaining
                </span>
                <span className={cn(
                  "font-mono",
                  timeRemaining < 30 && "text-red-500 font-bold"
                )}>
                  {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, "0")}
                </span>
              </div>
              <Progress
                value={timeProgress}
                className={cn("h-2", timeRemaining < 30 && "bg-red-200")}
              />
            </div>

            {transcript && (
              <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg max-h-32 overflow-y-auto">
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium">Your answer: </span>
                  {transcript}
                </p>
              </div>
            )}

            <Button
              onClick={onNextQuestion}
              disabled={isAnswering}
              className="w-full"
            >
              {isAnswering ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : questionIndex < totalQuestions - 1 ? (
                <>
                  Next Question
                  <ChevronRight className="w-4 h-4 ml-2" />
                </>
              ) : (
                "Complete Interview"
              )}
            </Button>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Loading questions...</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function InterviewContent({
  sessionId,
  questions,
  onInterviewComplete,
  onSubmitAnswer,
  onLeave,
}: {
  sessionId: string;
  questions: InterviewQuestion[];
  onInterviewComplete: () => void;
  onSubmitAnswer: (questionId: string, transcript: string, duration: number) => Promise<InterviewQuestion | null>;
  onLeave: () => void;
}) {
  const daily = useDaily();
  const localSessionId = useLocalSessionId();
  const participantIds = useParticipantIds();

  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(180);
  const [isAnswering, setIsAnswering] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [answerStartTime, setAnswerStartTime] = useState<number>(Date.now());
  const [isRecording, setIsRecording] = useState(false);

  const currentQuestion = questions[currentQuestionIndex] || null;

  // Timer effect
  useEffect(() => {
    if (!currentQuestion) return;

    setTimeRemaining(currentQuestion.max_duration_seconds);
    setAnswerStartTime(Date.now());
    setTranscript("");

    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          // Auto-submit when time runs out
          handleNextQuestion();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [currentQuestionIndex, currentQuestion?.id]);

  // Speech recognition for transcript
  useEffect(() => {
    if (typeof window === "undefined" || !("webkitSpeechRecognition" in window)) {
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: any) => {
      let finalTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + " ";
        }
      }
      if (finalTranscript) {
        setTranscript((prev) => prev + finalTranscript);
      }
    };

    recognition.onerror = (event: any) => {
      console.error("Speech recognition error:", event.error);
    };

    try {
      recognition.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Failed to start speech recognition:", err);
    }

    return () => {
      try {
        recognition.stop();
        setIsRecording(false);
      } catch (err) {
        // Ignore
      }
    };
  }, [currentQuestionIndex]);

  const handleNextQuestion = async () => {
    if (!currentQuestion || isAnswering) return;

    setIsAnswering(true);
    const duration = Math.floor((Date.now() - answerStartTime) / 1000);

    try {
      const nextQuestion = await onSubmitAnswer(
        currentQuestion.id,
        transcript || "[No verbal response detected]",
        duration
      );

      if (nextQuestion) {
        setCurrentQuestionIndex((prev) => prev + 1);
      } else {
        // Interview complete
        onInterviewComplete();
      }
    } catch (error) {
      console.error("Failed to submit answer:", error);
    } finally {
      setIsAnswering(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-950">
      {/* Main content area */}
      <div className="flex-1 flex gap-4 p-4 overflow-hidden">
        {/* Video area */}
        <div className="flex-1 relative">
          {/* Main video (could be AI avatar or interview interface) */}
          <div className="w-full h-full bg-gray-900 rounded-lg flex items-center justify-center">
            <div className="text-center text-white">
              <div className="w-32 h-32 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-4xl">AI</span>
              </div>
              <h3 className="text-xl font-semibold">AI Interviewer</h3>
              <p className="text-gray-400 mt-2">Listening to your response...</p>
            </div>
          </div>

          {/* Local video preview */}
          {localSessionId && (
            <VideoTile sessionId={localSessionId} isLocal />
          )}
        </div>

        {/* Question panel */}
        <div className="w-96">
          <QuestionPanel
            currentQuestion={currentQuestion}
            questionIndex={currentQuestionIndex}
            totalQuestions={questions.length}
            timeRemaining={timeRemaining}
            onNextQuestion={handleNextQuestion}
            isAnswering={isAnswering}
            transcript={transcript}
          />
        </div>
      </div>

      {/* Controls */}
      <div className="p-4 border-t border-gray-800">
        <InterviewControls onLeave={onLeave} isRecording={isRecording} />
      </div>
    </div>
  );
}

export function InterviewRoom({
  roomUrl,
  roomToken,
  sessionId,
  questions,
  onInterviewComplete,
  onSubmitAnswer,
}: InterviewRoomProps) {
  const [callObject, setCallObject] = useState<DailyCall | null>(null);
  const [isJoining, setIsJoining] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const daily = DailyIframe.createCallObject({
      audioSource: true,
      videoSource: true,
    });

    setCallObject(daily);

    daily
      .join({ url: roomUrl, token: roomToken })
      .then(() => {
        setIsJoining(false);
      })
      .catch((err) => {
        console.error("Failed to join:", err);
        setError("Failed to join the interview room. Please try again.");
        setIsJoining(false);
      });

    return () => {
      daily.leave();
      daily.destroy();
    };
  }, [roomUrl, roomToken]);

  const handleLeave = useCallback(() => {
    if (callObject) {
      callObject.leave();
    }
    onInterviewComplete();
  }, [callObject, onInterviewComplete]);

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-950">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Connection Error</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={() => window.location.reload()}>
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isJoining || !callObject) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-950">
        <Card className="w-96">
          <CardContent className="pt-6">
            <div className="text-center">
              <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-500" />
              <h3 className="text-lg font-semibold mb-2">Joining Interview</h3>
              <p className="text-muted-foreground">
                Setting up your camera and microphone...
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <DailyProvider callObject={callObject}>
      <InterviewContent
        sessionId={sessionId}
        questions={questions}
        onInterviewComplete={onInterviewComplete}
        onSubmitAnswer={onSubmitAnswer}
        onLeave={handleLeave}
      />
    </DailyProvider>
  );
}

export default InterviewRoom;
