'use client'

import * as React from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuthStore } from '@/hooks'
import {
  Bot,
  Send,
  Sparkles,
  MessageSquare,
  FileText,
  Calculator,
  TrendingUp,
  HelpCircle,
  Loader2,
  User
} from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

// Quick action suggestions
const quickActions = [
  { icon: Calculator, label: 'Calculate PF for employee', prompt: 'Calculate PF contribution for an employee with basic salary ₹50,000' },
  { icon: FileText, label: 'Generate payslip', prompt: 'Generate payslip for December 2025 for employee EMP001' },
  { icon: TrendingUp, label: 'Analyze expenses', prompt: 'Analyze our monthly expenses and identify cost savings' },
  { icon: HelpCircle, label: 'GST filing help', prompt: 'What are the due dates for GST filing this month?' }
]

export default function AIAssistantPage() {
  const { user } = useAuthStore()
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Hello ${user?.full_name || 'there'}! I'm your AI assistant for GanaPortal. I can help you with:\n\n• **Payroll calculations** - PF, ESI, TDS, and more\n• **Compliance queries** - GST, TDS filing deadlines\n• **Report generation** - Payslips, Form 16, ECR files\n• **Data analysis** - Expense trends, cash flow forecasts\n• **General HR queries** - Leave policies, attendance\n\nHow can I assist you today?`,
      timestamp: new Date()
    }
  ])
  const [input, setInput] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  React.useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    // Simulate AI response (would be actual API call)
    setTimeout(() => {
      const responses: Record<string, string> = {
        'pf': `**Provident Fund Calculation**\n\nFor an employee with Basic Salary ₹50,000:\n\n• **Employee PF (12%):** ₹6,000\n• **Employer EPS (8.33%):** ₹1,250 (capped at ₹15,000 wage)\n• **Employer EPF (3.67%):** ₹4,750\n• **Total PF:** ₹12,000\n\nNote: EPS contribution is capped at ₹1,250/month for employees with basic > ₹15,000.`,
        'gst': `**GST Filing Due Dates - January 2026**\n\n• **GSTR-1:** 11th January (Monthly filers)\n• **GSTR-3B:** 20th January\n• **GSTR-9:** 31st December 2025 (Annual return)\n• **GSTR-9C:** 31st December 2025 (Reconciliation)\n\nWould you like me to help prepare any of these returns?`,
        'payslip': `I can help generate the payslip. Please provide:\n\n1. Employee ID or code\n2. Month and year\n\nAlternatively, you can go to **Payroll → Payslips** to generate payslips in bulk for all employees.`,
        'default': `I understand you're asking about "${input}". Let me help you with that.\n\nBased on your query, I can:\n1. Provide calculations or explanations\n2. Guide you to the right module in GanaPortal\n3. Generate reports or documents\n\nCould you please provide more details about what specific information you need?`
      }

      const lowerInput = input.toLowerCase()
      let response = responses.default

      if (lowerInput.includes('pf') || lowerInput.includes('provident')) {
        response = responses.pf
      } else if (lowerInput.includes('gst') || lowerInput.includes('filing')) {
        response = responses.gst
      } else if (lowerInput.includes('payslip') || lowerInput.includes('salary slip')) {
        response = responses.payslip
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1500)
  }

  const handleQuickAction = (prompt: string) => {
    setInput(prompt)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Assistant"
        description="Your intelligent helper for payroll, compliance, and analytics"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'AI Assistant' }
        ]}
        actions={
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <Sparkles className="h-3 w-3 mr-1" />
            Powered by Claude
          </Badge>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Area */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-primary-foreground" />
                    </div>
                  )}
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm">
                      {message.content.split('\n').map((line, i) => {
                        // Handle bold text
                        const boldRegex = /\*\*(.*?)\*\*/g
                        const parts = line.split(boldRegex)

                        return (
                          <React.Fragment key={i}>
                            {parts.map((part, j) =>
                              j % 2 === 1 ? (
                                <strong key={j}>{part}</strong>
                              ) : (
                                part
                              )
                            )}
                            {i < message.content.split('\n').length - 1 && <br />}
                          </React.Fragment>
                        )
                      })}
                    </div>
                    <p className={`text-xs mt-1 ${
                      message.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'
                    }`}>
                      {message.timestamp.toLocaleTimeString('en-IN', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-primary-foreground" />
                  </div>
                  <div className="bg-muted rounded-lg p-3">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </CardContent>

            {/* Input Area */}
            <div className="border-t p-4">
              <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about payroll, compliance, reports..."
                  className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  disabled={isLoading}
                />
                <Button type="submit" disabled={!input.trim() || isLoading}>
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </form>
            </div>
          </Card>
        </div>

        {/* Quick Actions Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Quick Actions</CardTitle>
              <CardDescription>Common queries</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {quickActions.map((action, index) => {
                const Icon = action.icon
                return (
                  <Button
                    key={index}
                    variant="outline"
                    className="w-full justify-start text-left h-auto py-2"
                    onClick={() => handleQuickAction(action.prompt)}
                  >
                    <Icon className="h-4 w-4 mr-2 flex-shrink-0" />
                    <span className="text-sm">{action.label}</span>
                  </Button>
                )
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Usage Stats</CardTitle>
              <CardDescription>This month</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Queries</span>
                  <span className="font-medium">127</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Reports Generated</span>
                  <span className="font-medium">23</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Quota Remaining</span>
                  <span className="font-medium text-green-600">873</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">AI Capabilities</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <MessageSquare className="h-4 w-4 mt-0.5 text-primary" />
                  <span>Natural language queries</span>
                </li>
                <li className="flex items-start gap-2">
                  <Calculator className="h-4 w-4 mt-0.5 text-primary" />
                  <span>Tax & compliance calculations</span>
                </li>
                <li className="flex items-start gap-2">
                  <FileText className="h-4 w-4 mt-0.5 text-primary" />
                  <span>Document generation</span>
                </li>
                <li className="flex items-start gap-2">
                  <TrendingUp className="h-4 w-4 mt-0.5 text-primary" />
                  <span>Business insights</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
