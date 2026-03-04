import { createFileRoute } from "@tanstack/react-router"
import {
  JobStatusChart,
  JobsList,
  JobsStatsSummary,
  QueueDistributionChart,
  SampleTaskButtons,
} from "@/components/AdminDashboard"

export const Route = createFileRoute("/_layout/admin-tasks")({
  component: AdminTasksDashboard,
  head: () => ({
    meta: [
      {
        title: "Task Dashboard - Techletes",
      },
    ],
  }),
})

function AdminTasksDashboard() {
  return (
    <div className="flex flex-col gap-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Task Dashboard
        </h1>
        <p className="text-sm text-muted-foreground">
          Monitor and manage background jobs
        </p>
      </div>

      {/* Metric tiles */}
      <JobsStatsSummary />

      {/* Sample task launcher */}
      <SampleTaskButtons />

      {/* Charts grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <JobStatusChart />
        <QueueDistributionChart />
      </div>

      {/* Jobs list table */}
      <JobsList />
    </div>
  )
}
