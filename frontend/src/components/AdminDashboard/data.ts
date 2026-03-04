import type { LucideIcon } from "lucide-react"
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Layers,
  PlayCircle,
} from "lucide-react"

export interface TaskMetric {
  label: string
  value: number
  change?: number
  changeLabel?: string
  icon: LucideIcon
}

export const TASK_METRICS: TaskMetric[] = [
  {
    label: "Total Jobs",
    value: 0,
    icon: Layers,
  },
  {
    label: "Queued",
    value: 0,
    icon: Clock,
  },
  {
    label: "Running",
    value: 0,
    icon: PlayCircle,
  },
  {
    label: "Completed",
    value: 0,
    icon: CheckCircle2,
  },
  {
    label: "Failed",
    value: 0,
    icon: AlertCircle,
  },
]

export type QueueLevel = "default" | "high" | "low"

export interface SampleTask {
  label: string
  description: string
  task_type: "send_email" | "export_data" | "process_file"
  queue: QueueLevel
  kwargs: Record<string, unknown>
}

export const SAMPLE_TASKS: SampleTask[] = [
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

export const STATUS_FILTER_OPTIONS = [
  "queued",
  "running",
  "completed",
  "failed",
  "cancelled",
] as const

export const QUEUE_FILTER_OPTIONS = ["high", "default", "low"] as const

/** Maps job status to badge variant */
export const STATUS_BADGE_MAP: Record<
  string,
  "success" | "warning" | "danger" | "info" | "neutral"
> = {
  queued: "warning",
  running: "info",
  completed: "success",
  failed: "danger",
  cancelled: "neutral",
}

/** Maps queue priority to badge variant */
export const QUEUE_BADGE_MAP: Record<string, "danger" | "info" | "neutral"> = {
  high: "danger",
  default: "info",
  low: "neutral",
}

/** Chart theme colors using CSS variable references */
export const CHART_COLORS = {
  primary: "var(--chart-1)",
  success: "var(--chart-2)",
  info: "var(--chart-3)",
  warning: "var(--chart-4)",
  danger: "var(--chart-5)",
} as const

export const PIE_CHART_COLORS = [
  CHART_COLORS.primary,
  CHART_COLORS.success,
  CHART_COLORS.info,
  CHART_COLORS.warning,
  CHART_COLORS.danger,
]
