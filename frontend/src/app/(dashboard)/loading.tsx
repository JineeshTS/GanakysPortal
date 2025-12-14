/**
 * Dashboard Loading State
 * Displayed while dashboard content is loading.
 * WBS Reference: FIX-WBS Task 3.2.1.3
 */

import { Loader2 } from 'lucide-react';

export default function DashboardLoading() {
  return (
    <div className="flex min-h-[400px] items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}
