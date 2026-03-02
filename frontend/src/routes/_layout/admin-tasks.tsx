import { createFileRoute } from "@tanstack/react-router"
import {
  JobStatusChart,
  JobsList,
  JobsStatsSummary,
  QueueDistributionChart,
} from "@/components/AdminDashboard"

export const Route = createFileRoute("/_layout/admin-tasks")({
  component: AdminTasksDashboard,
})

function AdminTasksDashboard() {
  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Task Dashboard</h1>
        <p className="text-gray-600 mt-2">Monitor and manage background jobs</p>
      </div>

      {/* Statistics Summary */}
      <JobsStatsSummary />

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <JobStatusChart />
        <QueueDistributionChart />
      </div>

      {/* Jobs List */}
      <JobsList />
    </div>
  )
}
