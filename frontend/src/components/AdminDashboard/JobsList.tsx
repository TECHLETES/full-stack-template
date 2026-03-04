import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { AdminService } from "@/client"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  QUEUE_FILTER_OPTIONS,
  STATUS_BADGE_MAP,
  STATUS_FILTER_OPTIONS,
} from "./data"

function TableSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton key={i} className="h-10 w-full rounded-xl" />
      ))}
    </div>
  )
}

export const JobsList = () => {
  const [selectedQueue, setSelectedQueue] = useState<
    "high" | "default" | "low" | undefined
  >(undefined)
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>(
    undefined,
  )

  const { data, isLoading } = useQuery({
    queryKey: ["admin", "jobs", "list", selectedQueue, selectedStatus],
    queryFn: () =>
      AdminService.getJobsList({
        queue: selectedQueue,
        statusFilter: selectedStatus,
        limit: 100,
      }),
    refetchInterval: 5000,
  })

  const jobs = data?.jobs || []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-semibold">Recent Jobs</CardTitle>
        <CardDescription className="text-xs">
          View detailed information about background tasks
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Queue Filter */}
          <Tabs
            value={selectedQueue ?? "all"}
            onValueChange={(val) =>
              setSelectedQueue(
                val === "all"
                  ? undefined
                  : (val as (typeof QUEUE_FILTER_OPTIONS)[number]),
              )
            }
          >
            <TabsList>
              <TabsTrigger value="all">All Queues</TabsTrigger>
              {QUEUE_FILTER_OPTIONS.map((q) => (
                <TabsTrigger key={q} value={q} className="capitalize">
                  {q} Priority
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>

          {/* Status Filter */}
          <div className="flex gap-2 flex-wrap">
            <Badge
              variant={selectedStatus === undefined ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => setSelectedStatus(undefined)}
            >
              All Statuses
            </Badge>
            {STATUS_FILTER_OPTIONS.map((status) => (
              <Badge
                key={status}
                variant={selectedStatus === status ? "default" : "outline"}
                className="cursor-pointer capitalize"
                onClick={() => setSelectedStatus(status)}
              >
                {status}
              </Badge>
            ))}
          </div>

          {/* Jobs Table */}
          {isLoading ? (
            <TableSkeleton />
          ) : jobs.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Job ID</TableHead>
                    <TableHead>Task Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Queue</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead>Ended</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell className="font-mono text-xs">
                        {job.id.slice(0, 12)}…
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {job.func}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={STATUS_BADGE_MAP[job.status] ?? "neutral"}
                          className="capitalize"
                        >
                          {job.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm capitalize">
                        {job.queue}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground tabular-nums">
                        {job.created_at
                          ? new Date(job.created_at).toLocaleTimeString()
                          : "–"}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground tabular-nums">
                        {job.started_at
                          ? new Date(job.started_at).toLocaleTimeString()
                          : "–"}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground tabular-nums">
                        {job.ended_at
                          ? new Date(job.ended_at).toLocaleTimeString()
                          : "–"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
              No jobs found
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
