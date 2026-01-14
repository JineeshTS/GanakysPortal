"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2,
  RefreshCw,
  ExternalLink,
  Settings,
  Key,
  Unplug,
  Link2
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

export type IntegrationStatus = 'connected' | 'disconnected' | 'error' | 'pending' | 'not_configured'

export interface Integration {
  id: string
  name: string
  description: string
  icon?: React.ElementType
  status: IntegrationStatus
  lastSync?: Date | string
  errorMessage?: string
  configUrl?: string
  externalUrl?: string
}

// ============================================================================
// Status Indicator Component
// ============================================================================

interface StatusIndicatorProps {
  status: IntegrationStatus
  size?: 'sm' | 'md'
  showLabel?: boolean
}

export function StatusIndicator({ status, size = 'md', showLabel = true }: StatusIndicatorProps) {
  const statusConfig = {
    connected: {
      icon: CheckCircle,
      label: 'Connected',
      color: 'text-green-500',
      bgColor: 'bg-green-100 dark:bg-green-900',
      textColor: 'text-green-700 dark:text-green-300'
    },
    disconnected: {
      icon: XCircle,
      label: 'Disconnected',
      color: 'text-muted-foreground',
      bgColor: 'bg-muted',
      textColor: 'text-muted-foreground'
    },
    error: {
      icon: AlertCircle,
      label: 'Error',
      color: 'text-red-500',
      bgColor: 'bg-red-100 dark:bg-red-900',
      textColor: 'text-red-700 dark:text-red-300'
    },
    pending: {
      icon: Loader2,
      label: 'Connecting...',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-100 dark:bg-yellow-900',
      textColor: 'text-yellow-700 dark:text-yellow-300'
    },
    not_configured: {
      icon: Unplug,
      label: 'Not Configured',
      color: 'text-muted-foreground',
      bgColor: 'bg-muted',
      textColor: 'text-muted-foreground'
    }
  }

  const config = statusConfig[status]
  const Icon = config.icon
  const iconSize = size === 'sm' ? 'h-3 w-3' : 'h-4 w-4'

  if (showLabel) {
    return (
      <Badge variant="secondary" className={cn("gap-1", config.bgColor, config.textColor)}>
        <Icon className={cn(iconSize, status === 'pending' && 'animate-spin')} />
        {config.label}
      </Badge>
    )
  }

  return (
    <Icon className={cn(iconSize, config.color, status === 'pending' && 'animate-spin')} />
  )
}

// ============================================================================
// Integration Card Component
// ============================================================================

interface IntegrationCardProps {
  integration: Integration
  onConnect?: () => void
  onDisconnect?: () => void
  onConfigure?: () => void
  onSync?: () => void
  isLoading?: boolean
}

export function IntegrationCard({
  integration,
  onConnect,
  onDisconnect,
  onConfigure,
  onSync,
  isLoading = false
}: IntegrationCardProps) {
  const Icon = integration.icon

  const formatLastSync = (date: Date | string | undefined) => {
    if (!date) return 'Never synced'
    const d = new Date(date)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minutes ago`
    if (diffHours < 24) return `${diffHours} hours ago`
    if (diffDays < 7) return `${diffDays} days ago`
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <div className="flex items-start gap-3">
          {Icon && (
            <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center">
              <Icon className="h-6 w-6 text-foreground" />
            </div>
          )}
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              {integration.name}
              <StatusIndicator status={integration.status} size="sm" />
            </CardTitle>
            <CardDescription className="mt-1">{integration.description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Error Message */}
        {integration.status === 'error' && integration.errorMessage && (
          <div className="mb-4 p-3 rounded-md bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm flex items-start gap-2">
            <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
            <span>{integration.errorMessage}</span>
          </div>
        )}

        {/* Last Sync Info */}
        {integration.status === 'connected' && (
          <div className="text-sm text-muted-foreground mb-4">
            Last synced: {formatLastSync(integration.lastSync)}
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {integration.status === 'connected' ? (
            <>
              {onSync && (
                <Button variant="outline" size="sm" onClick={onSync} disabled={isLoading}>
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4 mr-1" />
                  )}
                  Sync Now
                </Button>
              )}
              {onConfigure && (
                <Button variant="outline" size="sm" onClick={onConfigure} disabled={isLoading}>
                  <Settings className="h-4 w-4 mr-1" />
                  Configure
                </Button>
              )}
              {onDisconnect && (
                <Button variant="ghost" size="sm" onClick={onDisconnect} disabled={isLoading}>
                  <Unplug className="h-4 w-4 mr-1" />
                  Disconnect
                </Button>
              )}
            </>
          ) : (
            <>
              {onConnect && (
                <Button size="sm" onClick={onConnect} disabled={isLoading}>
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                  ) : (
                    <Link2 className="h-4 w-4 mr-1" />
                  )}
                  Connect
                </Button>
              )}
              {onConfigure && integration.status === 'not_configured' && (
                <Button variant="outline" size="sm" onClick={onConfigure} disabled={isLoading}>
                  <Settings className="h-4 w-4 mr-1" />
                  Configure
                </Button>
              )}
            </>
          )}

          {integration.externalUrl && (
            <Button variant="ghost" size="sm" asChild>
              <a href={integration.externalUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-1" />
                Open Portal
              </a>
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// API Key Management Component
// ============================================================================

interface APIKey {
  id: string
  name: string
  key: string
  createdAt: Date | string
  lastUsed?: Date | string
  expiresAt?: Date | string
  permissions?: string[]
}

interface APIKeyCardProps {
  apiKey: APIKey
  onRevoke?: () => void
  onCopy?: () => void
}

export function APIKeyCard({ apiKey, onRevoke, onCopy }: APIKeyCardProps) {
  const [copied, setCopied] = React.useState(false)
  const [showKey, setShowKey] = React.useState(false)

  const maskedKey = apiKey.key.slice(0, 8) + '...' + apiKey.key.slice(-4)

  const handleCopy = () => {
    navigator.clipboard.writeText(apiKey.key)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    onCopy?.()
  }

  const formatDate = (date: Date | string) => {
    return new Date(date).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
            <Key className="h-5 w-5" />
          </div>
          <div>
            <div className="font-medium">{apiKey.name}</div>
            <div className="text-sm text-muted-foreground">
              Created {formatDate(apiKey.createdAt)}
            </div>
          </div>
        </div>
        {onRevoke && (
          <Button variant="ghost" size="sm" className="text-destructive" onClick={onRevoke}>
            Revoke
          </Button>
        )}
      </div>

      <div className="mt-4 flex items-center gap-2">
        <code className="flex-1 p-2 bg-muted rounded text-sm font-mono">
          {showKey ? apiKey.key : maskedKey}
        </code>
        <Button variant="outline" size="sm" onClick={() => setShowKey(!showKey)}>
          {showKey ? 'Hide' : 'Show'}
        </Button>
        <Button variant="outline" size="sm" onClick={handleCopy}>
          {copied ? 'Copied!' : 'Copy'}
        </Button>
      </div>

      {apiKey.lastUsed && (
        <div className="mt-3 text-sm text-muted-foreground">
          Last used: {formatDate(apiKey.lastUsed)}
        </div>
      )}

      {apiKey.expiresAt && (
        <div className="mt-1 text-sm text-muted-foreground">
          Expires: {formatDate(apiKey.expiresAt)}
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Integration Status Summary Component
// ============================================================================

interface IntegrationStatusSummaryProps {
  integrations: Integration[]
  className?: string
}

export function IntegrationStatusSummary({ integrations, className }: IntegrationStatusSummaryProps) {
  const connected = integrations.filter(i => i.status === 'connected').length
  const errors = integrations.filter(i => i.status === 'error').length
  const total = integrations.length

  return (
    <div className={cn("flex items-center gap-4", className)}>
      <div className="flex items-center gap-2">
        <CheckCircle className="h-4 w-4 text-green-500" />
        <span className="text-sm">{connected} connected</span>
      </div>
      {errors > 0 && (
        <div className="flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span className="text-sm">{errors} errors</span>
        </div>
      )}
      <div className="text-sm text-muted-foreground">
        {total - connected - errors} not configured
      </div>
    </div>
  )
}

export default IntegrationCard
