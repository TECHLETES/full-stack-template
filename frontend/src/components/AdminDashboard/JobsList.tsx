import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

const statusColors: Record<string, string> = {
  queued: "bg-yellow-100 text-yellow-800",
  started: "bg-blue-100 text-blue-800",
  finished: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
  deferred: "bg-gray-100 text-gray-800",
  stopped: "bg-orange-100 text-orange-800",
  canceled: "bg-purple-100 text-purple-800",
}

// Fetch jobs list directly from API
const fetchJobsList = async (queue: string, statusFilter?: string) => {
  const params = new URLSearchParams({
    queue,
    limit: "100",
  })
  if (statusFilter) {
    params.append("status_filter", statusFilter)
  }
  const response = await fetch(
    `${import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"}/admin/jobs/list?${params.toString()}`,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
      },
    },
  )
  if (!response.ok) throw new Error("Failed to fetch jobs list")
  return response.json()
}

export const JobsList = () => {
  const [selectedQueue, setSelectedQueue] = useState<
    "high" | "default" | "low"
  >("default")
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>(
    undefined,
  )

  const { data, isLoading } = useQuery({
    queryKey: ["admin", "jobs", "list", selectedQueue, selectedStatus],
    queryFn: () => fetchJobsList(selectedQueue, selectedStatus),
    refetchInterval: 5000,
  })

  if (isLoading) return <div>Loading jobs...</div>

  const jobs = data?.jobs || []

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Jobs</CardTitle>
        <CardDescription>
          View detailed information about background tasks
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Queue Filter */}
          <Tabs
            value={selectedQueue}
            onValueChange={(val) =>
              setSelectedQueue(val as "high" | "default" | "low")
            }
          >
            <TabsList>
              <TabsTrigger value="high">High Priority</TabsTrigger>
              <TabsTrigger value="default">Default Priority</TabsTrigger>
              <TabsTrigger value="low">Low Priority</TabsTrigger>
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
            {["queued", "started", "finished", "failed", "deferred"].map(
              (status) => (
                <Badge
                  key={status}
                  variant={selectedStatus === status ? "default" : "outline"}
                  className="cursor-pointer"
                  onClick={() => setSelectedStatus(status)}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </Badge>
              ),
            )}
          </div>

          {/* Jobs Table */}
          {jobs.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[200px]">Job ID</TableHead>
                    <TableHead className="w-[250px]">Function</TableHead>
                    <TableHead className="w-[100px]">Status</TableHead>
                    <TableHead className="w-[150px]">Created</TableHead>
                    <TableHead className="w-[150px]">Started</TableHead>
                    <TableHead className="w-[150px]">Ended</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobs.map(
                    (job: {
                      id: string
                      func: string
                      status: string
                      created_at?: string
                      started_at?: string
                      ended_at?: string
                    }) => (
                      <TableRow key={job.id}>
                        <TableCell className="font-mono text-xs">
                          {job.id.slice(0, 12)}...
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {job.func}
                        </TableCell>
                        <TableCell>
                          <Badge
                            className={
                              statusColors[job.status] ||
                              "bg-gray-100 text-gray-800"
                            }
                          >
                            {job.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">
                          {job.created_at
                            ? new Date(job.created_at).toLocaleTimeString()
                            : "-"}
                        </TableCell>
                        <TableCell className="text-sm">
                          {job.started_at
                            ? new Date(job.started_at).toLocaleTimeString()
                            : "-"}
                        </TableCell>
                        <TableCell className="text-sm">
                          {job.ended_at
                            ? new Date(job.ended_at).toLocaleTimeString()
                            : "-"}
                        </TableCell>
                      </TableRow>
                    ),
                  )}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No jobs found in {selectedQueue} queue
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
