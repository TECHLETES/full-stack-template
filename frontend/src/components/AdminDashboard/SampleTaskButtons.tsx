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
import { QUEUE_BADGE_MAP, SAMPLE_TASKS, type SampleTask } from "./data"

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
      queryClient.invalidateQueries({ queryKey: ["admin", "jobs"] })
    },
  })

  return (
    <div className="flex flex-col gap-2 rounded-xl border bg-card p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="mb-1 flex items-center gap-2">
            <span className="text-sm font-medium">{task.label}</span>
            <Badge variant={QUEUE_BADGE_MAP[task.queue] ?? "neutral"}>
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
        <p className="text-xs font-mono text-success">
          ✓ Queued: {lastJobId.slice(0, 16)}…
        </p>
      )}
      {mutation.isError && (
        <p className="text-xs text-destructive">✗ Failed to enqueue task</p>
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
            <CardTitle className="text-sm font-semibold">
              Sample Tasks
            </CardTitle>
            <CardDescription className="text-xs">
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
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {SAMPLE_TASKS.map((task) => (
            <TaskButton
              key={`${task.task_type}-${task.queue}-${task.label}`}
              task={task}
            />
          ))}
        </div>
        {runAllMutation.isSuccess && (
          <p className="mt-3 text-xs text-success">
            ✓ All {SAMPLE_TASKS.length} tasks queued successfully
          </p>
        )}
      </CardContent>
    </Card>
  )
}
