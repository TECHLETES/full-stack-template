import { useQuery } from "@tanstack/react-query"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { AdminService } from "@/client"
import ChartCard from "@/components/Common/ChartCard"
import MetricCard from "@/components/Common/MetricCard"
import { Skeleton } from "@/components/ui/skeleton"
import { CHART_COLORS, PIE_CHART_COLORS, TASK_METRICS } from "./data"

function MetricsSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-28 rounded-2xl" />
      ))}
    </div>
  )
}

export const JobStatusChart = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "jobs", "stats"],
    queryFn: () => AdminService.getJobsStats(),
    refetchInterval: 5000,
  })

  if (isLoading) {
    return (
      <ChartCard
        title="Job Status Distribution"
        description="Current status of all background jobs"
      >
        <Skeleton className="h-64 w-full rounded-xl" />
      </ChartCard>
    )
  }
  if (!data) return null

  const chartData = [
    { name: "Queued", value: data.status_counts.queued },
    { name: "Running", value: data.status_counts.running },
    { name: "Completed", value: data.status_counts.completed },
    { name: "Failed", value: data.status_counts.failed },
    { name: "Cancelled", value: data.status_counts.cancelled },
  ].filter((item) => (item.value ?? 0) > 0)

  return (
    <ChartCard
      title="Job Status Distribution"
      description="Current status of all background jobs"
    >
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}`}
              outerRadius={100}
              fill={CHART_COLORS.primary}
              dataKey="value"
              strokeWidth={2}
            >
              {chartData.map((_entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={PIE_CHART_COLORS[index % PIE_CHART_COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                borderRadius: "0.75rem",
                border: "1px solid var(--border)",
                background: "var(--card)",
                color: "var(--card-foreground)",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
          No jobs in system
        </div>
      )}
    </ChartCard>
  )
}

export const QueueDistributionChart = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "jobs", "stats"],
    queryFn: () => AdminService.getJobsStats(),
    refetchInterval: 5000,
  })

  if (isLoading) {
    return (
      <ChartCard
        title="Jobs by Queue"
        description="Distribution across priority levels"
      >
        <Skeleton className="h-64 w-full rounded-xl" />
      </ChartCard>
    )
  }
  if (!data) return null

  const chartData = data.queue_stats

  return (
    <ChartCard
      title="Jobs by Queue"
      description="Distribution across priority levels"
    >
      {chartData && chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--border)"
              strokeOpacity={0.5}
            />
            <XAxis
              dataKey="name"
              tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
              axisLine={{ stroke: "var(--border)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                borderRadius: "0.75rem",
                border: "1px solid var(--border)",
                background: "var(--card)",
                color: "var(--card-foreground)",
              }}
            />
            <Bar
              dataKey="count"
              fill={CHART_COLORS.primary}
              radius={[6, 6, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
          No queue data
        </div>
      )}
    </ChartCard>
  )
}

export const JobsStatsSummary = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "jobs", "stats"],
    queryFn: () => AdminService.getJobsStats(),
    refetchInterval: 5000,
  })

  if (isLoading) return <MetricsSkeleton />
  if (!data) return null

  const { status_counts, total_jobs } = data

  const values = [
    total_jobs,
    status_counts.queued,
    status_counts.running,
    status_counts.completed,
    status_counts.failed,
  ]

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
      {TASK_METRICS.map((metric, i) => (
        <MetricCard
          key={metric.label}
          label={metric.label}
          value={values[i] ?? 0}
          icon={metric.icon}
        />
      ))}
    </div>
  )
}
