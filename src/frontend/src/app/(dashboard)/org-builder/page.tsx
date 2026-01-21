'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function OrgBuilderRedirect() {
  const router = useRouter()

  useEffect(() => {
    router.replace('/settings/organization?tab=ai-builder')
  }, [router])

  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-muted-foreground">Redirecting to Organization Setup...</p>
      </div>
    </div>
  )
}
