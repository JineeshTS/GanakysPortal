'use client';

/**
 * Leave Balance Card Component
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import type { LeaveBalance, LeaveType } from '@/types/leave';

interface LeaveBalanceCardProps {
  balances: LeaveBalance[];
  isLoading?: boolean;
}

const leaveTypeColors: Record<LeaveType, { bg: string; text: string; progress: string }> = {
  earned: { bg: 'bg-blue-50', text: 'text-blue-700', progress: 'bg-blue-500' },
  casual: { bg: 'bg-green-50', text: 'text-green-700', progress: 'bg-green-500' },
  sick: { bg: 'bg-orange-50', text: 'text-orange-700', progress: 'bg-orange-500' },
  maternity: { bg: 'bg-pink-50', text: 'text-pink-700', progress: 'bg-pink-500' },
  paternity: { bg: 'bg-indigo-50', text: 'text-indigo-700', progress: 'bg-indigo-500' },
  bereavement: { bg: 'bg-gray-50', text: 'text-gray-700', progress: 'bg-gray-500' },
  comp_off: { bg: 'bg-purple-50', text: 'text-purple-700', progress: 'bg-purple-500' },
  unpaid: { bg: 'bg-red-50', text: 'text-red-700', progress: 'bg-red-500' },
};

export function LeaveBalanceCard({ balances, isLoading }: LeaveBalanceCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Leave Balance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 w-24 bg-muted rounded mb-2" />
                <div className="h-2 w-full bg-muted rounded" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (balances.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Leave Balance</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No leave balances available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Leave Balance</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {balances.map((balance) => {
            const colors = leaveTypeColors[balance.leave_type_code] || leaveTypeColors.earned;
            const usedPercentage = balance.total_quota > 0
              ? Math.min(100, (balance.used / balance.total_quota) * 100)
              : 0;

            return (
              <div key={balance.leave_type_id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors.bg} ${colors.text}`}>
                      {balance.leave_type_name}
                    </span>
                    {balance.pending > 0 && (
                      <span className="text-xs text-muted-foreground">
                        ({balance.pending} pending)
                      </span>
                    )}
                  </div>
                  <span className="text-sm font-medium">
                    {balance.available} / {balance.total_quota}
                  </span>
                </div>
                <Progress value={usedPercentage} className="h-2" />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Used: {balance.used}</span>
                  <span>Available: {balance.available}</span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

export default LeaveBalanceCard;
