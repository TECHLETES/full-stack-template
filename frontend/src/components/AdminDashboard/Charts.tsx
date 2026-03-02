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
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

const COLORS = [
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#ec4899",
]

// Fetch stats directly from API
const fetchJobsStats = async () => {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"}/admin/jobs/stats`,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
      },
    },
  )
  if (!response.ok) throw new Error("Failed to fetch job stats")
  return response.json()
}

export const JobStatusChart = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "jobs", "stats"],
    queryFn: fetchJobsStats,
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  if (isLoading) return <div>Loading...</div>
  if (!data) return null

  const chartData = [
    { name: "Queued", value: data.status_counts.queued },
    { name: "Started", value: data.status_counts.started },
    { name: "Finished", value: data.status_counts.finished },
    { name: "Failed", value: data.status_counts.failed },
    { name: "Deferred", value: data.status_counts.deferred },
    { name: "Stopped", value: data.status_counts.stopped },
  ].filter((item) => item.value > 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Status Distribution</CardTitle>
        <CardDescription>Current status of all background jobs</CardDescription>
      </CardHeader>
      <CardContent>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((_entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No jobs in system
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export const QueueDistributionChart = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "jobs", "stats"],
    queryFn: fetchJobsStats,
    refetchInterval: 5000,
  })

  if (isLoading) return <div>Loading...</div>
  if (!data) return null

  const chartData = data.queue_stats

  return (
    <Card>
      <CardHeader>
        <CardTitle>Jobs by Queue</CardTitle>
        <CardDescription>Distribution across priority levels</CardDescription>
      </CardHeader>
      <CardContent>
        {chartData && chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-8 text-gray-500">No queue data</div>
        )}
      </CardContent>
    </Card>
  )
}

export const JobsStatsSummary = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["admin", "jobs", "stats"],
    queryFn: fetchJobsStats,
    refetchInterval: 5000,
  })

  if (isLoading) return <div>Loading...</div>
  if (!data) return null

  const { status_counts, total_jobs } = data

  const stats = [
    {
      label: "Total Jobs",
      value: total_jobs,
      color: "bg-blue-100 text-blue-800",
    },
    {
      label: "Queued",
      value: status_counts.queued,
      color: "bg-yellow-100 text-yellow-800",
    },
    {
      label: "Running",
      value: status_counts.started,
      color: "bg-purple-100 text-purple-800",
    },
    {
      label: "Finished",
      value: status_counts.finished,
      color: "bg-green-100 text-green-800",
    },
    {
      label: "Failed",
      value: status_counts.failed,
      color: "bg-red-100 text-red-800",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <CardContent className="pt-6">
            <div className={`text-center p-4 rounded-lg ${stat.color}`}>
              <div className="text-sm font-medium">{stat.label}</div>
              <div className="text-3xl font-bold mt-2">{stat.value}</div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
