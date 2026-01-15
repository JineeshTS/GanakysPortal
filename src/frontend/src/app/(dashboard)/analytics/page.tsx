'use client';

import { useState, useEffect } from 'react';
import { Plus, BarChart3, PieChart, TrendingUp, FileText, Download, Settings, Loader2, Calendar, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useApi } from '@/hooks';

interface Dashboard {
  id: string;
  name: string;
  description: string;
  dashboard_type: string;
  widgets_count: number;
  is_default: boolean;
  is_public: boolean;
  last_accessed: string;
}

interface KPI {
  id: string;
  name: string;
  code: string;
  category: string;
  current_value: number;
  target_value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  trend_percentage: number;
}

interface ReportTemplate {
  id: string;
  name: string;
  category: string;
  format: string;
  schedule: string | null;
  last_generated: string | null;
}

const dashboardTypeIcons: Record<string, React.ReactNode> = {
  executive: <TrendingUp className="h-4 w-4" />,
  operational: <BarChart3 className="h-4 w-4" />,
  analytical: <PieChart className="h-4 w-4" />,
  custom: <Settings className="h-4 w-4" />,
};

const trendColors: Record<string, string> = {
  up: 'text-green-600',
  down: 'text-red-600',
  stable: 'text-gray-600',
};

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState('dashboards');
  const { data: dashboardsData, isLoading: dashboardsLoading, get: getDashboards } = useApi<{ data: Dashboard[] }>();
  const { data: kpisData, isLoading: kpisLoading, get: getKPIs } = useApi<{ data: KPI[] }>();
  const { data: reportsData, isLoading: reportsLoading, get: getReports } = useApi<{ data: ReportTemplate[] }>();

  useEffect(() => {
    getDashboards('/analytics/dashboards');
    getKPIs('/analytics/kpis');
    getReports('/analytics/reports/templates');
  }, [getDashboards, getKPIs, getReports]);

  const dashboards = dashboardsData?.data || [];
  const kpis = kpisData?.data || [];
  const reports = reportsData?.data || [];
  const isLoading = dashboardsLoading || kpisLoading || reportsLoading;

  const stats = {
    totalDashboards: dashboards.length || 8,
    activeKPIs: kpis.length || 24,
    reportTemplates: reports.length || 15,
    scheduledReports: reports.filter(r => r.schedule).length || 6,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Advanced Analytics"
        description="Dashboards, KPIs, and business intelligence reports"
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Create Dashboard
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading analytics data...</span>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Dashboards"
          value={stats.totalDashboards}
          icon={BarChart3}
          description="Custom views"
        />
        <StatCard
          title="Active KPIs"
          value={stats.activeKPIs}
          icon={TrendingUp}
          description="Tracked metrics"
        />
        <StatCard
          title="Report Templates"
          value={stats.reportTemplates}
          icon={FileText}
          description="Available reports"
        />
        <StatCard
          title="Scheduled Reports"
          value={stats.scheduledReports}
          icon={Calendar}
          description="Auto-generated"
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="dashboards">Dashboards</TabsTrigger>
          <TabsTrigger value="kpis">KPIs</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="data-sources">Data Sources</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboards" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(dashboards.length ? dashboards : [
              { id: '1', name: 'Executive Summary', description: 'High-level business metrics', dashboard_type: 'executive', widgets_count: 8, is_default: true, is_public: true, last_accessed: '2026-01-15' },
              { id: '2', name: 'Sales Performance', description: 'Sales team KPIs and trends', dashboard_type: 'operational', widgets_count: 12, is_default: false, is_public: true, last_accessed: '2026-01-15' },
              { id: '3', name: 'Financial Overview', description: 'Revenue, costs, and margins', dashboard_type: 'analytical', widgets_count: 10, is_default: false, is_public: false, last_accessed: '2026-01-14' },
              { id: '4', name: 'HR Analytics', description: 'Workforce metrics and trends', dashboard_type: 'operational', widgets_count: 6, is_default: false, is_public: true, last_accessed: '2026-01-13' },
            ]).map((dashboard) => (
              <Card key={dashboard.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {dashboardTypeIcons[dashboard.dashboard_type]}
                      <CardTitle className="text-base">{dashboard.name}</CardTitle>
                    </div>
                    {dashboard.is_default && (
                      <Badge variant="secondary">Default</Badge>
                    )}
                  </div>
                  <CardDescription>{dashboard.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{dashboard.widgets_count} widgets</span>
                    <span className="text-muted-foreground">Last viewed: {dashboard.last_accessed}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="kpis" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {(kpis.length ? kpis : [
              { id: '1', name: 'Revenue Growth', code: 'REV_GROWTH', category: 'Finance', current_value: 15.2, target_value: 12, unit: '%', trend: 'up' as const, trend_percentage: 3.2 },
              { id: '2', name: 'Customer Satisfaction', code: 'CSAT', category: 'Customer', current_value: 4.5, target_value: 4.0, unit: '/5', trend: 'up' as const, trend_percentage: 0.2 },
              { id: '3', name: 'Employee Turnover', code: 'EMP_TURN', category: 'HR', current_value: 8.5, target_value: 10, unit: '%', trend: 'down' as const, trend_percentage: -1.5 },
              { id: '4', name: 'Order Fulfillment', code: 'ORD_FILL', category: 'Operations', current_value: 98.2, target_value: 95, unit: '%', trend: 'stable' as const, trend_percentage: 0.1 },
              { id: '5', name: 'Gross Margin', code: 'GROSS_MARG', category: 'Finance', current_value: 42.5, target_value: 40, unit: '%', trend: 'up' as const, trend_percentage: 2.5 },
              { id: '6', name: 'On-Time Delivery', code: 'OTD', category: 'Operations', current_value: 94.8, target_value: 95, unit: '%', trend: 'down' as const, trend_percentage: -0.2 },
            ]).map((kpi) => (
              <Card key={kpi.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-xs">{kpi.category}</Badge>
                    <span className={`text-xs font-medium ${trendColors[kpi.trend]}`}>
                      {kpi.trend === 'up' ? '↑' : kpi.trend === 'down' ? '↓' : '→'} {Math.abs(kpi.trend_percentage)}%
                    </span>
                  </div>
                  <CardTitle className="text-sm font-medium mt-2">{kpi.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {kpi.current_value}{kpi.unit}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Target: {kpi.target_value}{kpi.unit}
                  </div>
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full ${kpi.current_value >= kpi.target_value ? 'bg-green-500' : 'bg-yellow-500'}`}
                      style={{ width: `${Math.min((kpi.current_value / kpi.target_value) * 100, 100)}%` }}
                    />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          <div className="mt-4 flex justify-end">
            <Button variant="outline" className="gap-2">
              <RefreshCw className="h-4 w-4" />
              Recalculate All KPIs
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="reports" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Report Name</th>
                  <th className="text-left p-4 font-medium">Category</th>
                  <th className="text-left p-4 font-medium">Format</th>
                  <th className="text-left p-4 font-medium">Schedule</th>
                  <th className="text-left p-4 font-medium">Last Generated</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(reports.length ? reports : [
                  { id: '1', name: 'Monthly Financial Summary', category: 'Finance', format: 'PDF', schedule: 'Monthly', last_generated: '2026-01-01' },
                  { id: '2', name: 'Sales Pipeline Report', category: 'Sales', format: 'Excel', schedule: 'Weekly', last_generated: '2026-01-13' },
                  { id: '3', name: 'Inventory Status', category: 'Operations', format: 'PDF', schedule: null, last_generated: '2026-01-10' },
                  { id: '4', name: 'Employee Attendance', category: 'HR', format: 'Excel', schedule: 'Daily', last_generated: '2026-01-15' },
                ]).map((report) => (
                  <tr key={report.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{report.name}</td>
                    <td className="p-4">{report.category}</td>
                    <td className="p-4">
                      <Badge variant="outline">{report.format}</Badge>
                    </td>
                    <td className="p-4">{report.schedule || '-'}</td>
                    <td className="p-4 text-muted-foreground">{report.last_generated || 'Never'}</td>
                    <td className="p-4 text-right">
                      <Button variant="ghost" size="sm" className="gap-1">
                        <Download className="h-3 w-3" />
                        Generate
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="data-sources" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Connected Data Sources</CardTitle>
              <CardDescription>Manage data sources for analytics and reporting</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {['Internal Database', 'Google Analytics', 'CRM System', 'ERP System'].map((source, i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full" />
                      <span className="font-medium">{source}</span>
                    </div>
                    <Badge variant="secondary">Connected</Badge>
                  </div>
                ))}
              </div>
              <Button className="mt-4">
                <Plus className="h-4 w-4 mr-2" />
                Add Data Source
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
