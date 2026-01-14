'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

export default function CompanyProfileRedirect() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab === 'products') {
      router.replace('/settings/organization-setup?tab=products')
    } else if (tab === 'ai-settings') {
      router.replace('/settings/organization-setup?tab=ai-builder')
    } else {
      router.replace('/settings/organization-setup?tab=profile')
    }
  }, [router, searchParams])

  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-muted-foreground">Redirecting to Organization Setup...</p>
      </div>
    </div>
  )
}
