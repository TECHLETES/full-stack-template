import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { TasksService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

type QueueLevel = "default" | "high" | "low"

interface SampleTask {
  label: string
  description: string
  task_type: "send_email" | "export_data" | "process_file"
  queue: QueueLevel
  kwargs: Record<string, unknown>
}

const SAMPLE_TASKS: SampleTask[] = [
  {
    label: "Send Email",
    description: "Simulates sending a transactional email (~0.5s)",
    task_type: "send_email",
    queue: "default",
    kwargs: {
      to: "test@example.com",
      subject: "Hello from the task queue",
      _body: "This is a test email sent via the background task system.",
    },
  },
  {
    label: "Export Data (CSV)",
    description: "Simulates a long-running data export (~2s)",
    task_type: "export_data",
    queue: "low",
    kwargs: { user_id: "demo-user", format: "csv" },
  },
  {
    label: "Export Data (JSON)",
    description: "Simulates a data export in JSON format (~2s)",
    task_type: "export_data",
    queue: "low",
    kwargs: { user_id: "demo-user", format: "json" },
  },
  {
    label: "Process File",
    description: "Simulates file post-processing, e.g. OCR (~1s)",
    task_type: "process_file",
    queue: "default",
    kwargs: { file_id: "sample-file-001" },
  },
  {
    label: "Process File (High Priority)",
    description: "Same processing, but on the high-priority queue",
    task_type: "process_file",
    queue: "high",
    kwargs: { file_id: "urgent-file-002" },
  },
]

const queueColors: Record<QueueLevel, string> = {
  high: "bg-red-100 text-red-800",
  default: "bg-blue-100 text-blue-800",
  low: "bg-gray-100 text-gray-800",
}

interface TaskButtonProps {
  task: SampleTask
}

const TaskButton = ({ task }: TaskButtonProps) => {
  const queryClient = useQueryClient()
  const [lastJobId, setLastJobId] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () =>
      TasksService.enqueueTask({
        requestBody: {
          task_type: task.task_type,
          queue: task.queue,
          kwargs: task.kwargs,
        },
      }),
    onSuccess: (data) => {
      setLastJobId(data.id)
      // Refresh both the jobs list and stats
      queryClient.invalidateQueries({ queryKey: ["admin", "jobs"] })
    },
  })

  return (
    <div className="flex flex-col gap-2 p-4 rounded-lg border bg-card">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-sm">{task.label}</span>
            <Badge className={`text-xs ${queueColors[task.queue]}`}>
              {task.queue}
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">{task.description}</p>
        </div>
        <Button
          size="sm"
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending}
          className="shrink-0"
        >
          {mutation.isPending ? "Queuing…" : "Run"}
        </Button>
      </div>
      {mutation.isSuccess && lastJobId && (
        <p className="text-xs text-green-600 font-mono">
          ✓ Queued: {lastJobId.slice(0, 16)}…
        </p>
      )}
      {mutation.isError && (
        <p className="text-xs text-red-600">✗ Failed to enqueue task</p>
      )}
    </div>
  )
}

export const SampleTaskButtons = () => {
  const queryClient = useQueryClient()

  const runAllMutation = useMutation({
    mutationFn: async () => {
      await Promise.all(
        SAMPLE_TASKS.map((task) =>
          TasksService.enqueueTask({
            requestBody: {
              task_type: task.task_type,
              queue: task.queue,
              kwargs: task.kwargs,
            },
          }),
        ),
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "jobs"] })
    },
  })

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Sample Tasks</CardTitle>
            <CardDescription>
              Enqueue test jobs to verify the task system end-to-end
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => runAllMutation.mutate()}
            disabled={runAllMutation.isPending}
          >
            {runAllMutation.isPending ? "Queuing all…" : "Run All"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {SAMPLE_TASKS.map((task) => (
            <TaskButton
              key={`${task.task_type}-${task.queue}-${task.label}`}
              task={task}
            />
          ))}
        </div>
        {runAllMutation.isSuccess && (
          <p className="text-xs text-green-600 mt-3">
            ✓ All {SAMPLE_TASKS.length} tasks queued successfully
          </p>
        )}
      </CardContent>
    </Card>
  )
}
