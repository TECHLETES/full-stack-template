"""Admin endpoints for monitoring background jobs and queue statistics."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rq import Queue

from backend.api.deps import SuperUserDep
from backend.core.queue import get_redis_conn

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------


class JobStatusCount(BaseModel):
    queued: int = 0
    started: int = 0
    finished: int = 0
    failed: int = 0
    deferred: int = 0
    canceled: int = 0
    stopped: int = 0


class QueueStats(BaseModel):
    name: str
    count: int


class JobInfo(BaseModel):
    id: str
    func: str
    status: str
    queue: str
    created_at: str | None = None
    started_at: str | None = None
    ended_at: str | None = None


class JobsStatsResponse(BaseModel):
    status_counts: JobStatusCount
    queue_stats: list[QueueStats]
    total_jobs: int


class JobsListResponse(BaseModel):
    jobs: list[JobInfo]
    total: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/jobs/stats", response_model=JobsStatsResponse)
def get_jobs_stats(
    _superuser: SuperUserDep,
) -> Any:
    """Get statistics about all background jobs (superuser only)."""
    conn = get_redis_conn()

    # Count jobs by status across all queues
    status_counts = JobStatusCount()

    for queue_name in ["high", "default", "low"]:
        queue = Queue(queue_name, connection=conn)

        # Get jobs by status
        status_counts.queued += len(queue.get_job_ids())
        status_counts.finished += len(queue.finished_job_registry.get_job_ids())
        status_counts.failed += len(queue.failed_job_registry.get_job_ids())
        status_counts.started += len(queue.started_job_registry.get_job_ids())
        status_counts.deferred += len(queue.deferred_job_registry.get_job_ids())
        status_counts.canceled += len(queue.canceled_job_registry.get_job_ids())

    # Get queue stats
    queue_stats = []
    for queue_name in ["high", "default", "low"]:
        queue = Queue(queue_name, connection=conn)
        count = len(queue.get_job_ids())
        queue_stats.append(QueueStats(name=queue_name, count=count))

    total = (
        status_counts.queued
        + status_counts.started
        + status_counts.finished
        + status_counts.failed
        + status_counts.deferred
        + status_counts.canceled
    )

    return JobsStatsResponse(
        status_counts=status_counts,
        queue_stats=queue_stats,
        total_jobs=total,
    )


@router.get("/jobs/list", response_model=JobsListResponse)
def get_jobs_list(
    _superuser: SuperUserDep,
    queue: str = "default",
    status_filter: str | None = None,
    limit: int = 50,
) -> Any:
    """List jobs from a specific queue (superuser only).

    Query parameters:
    - queue: "high", "default", or "low"
    - status_filter: Filter by status (queued, started, finished, failed, etc)
    - limit: Max results to return (default 50)
    """
    if queue not in ["high", "default", "low"]:
        raise HTTPException(
            status_code=400, detail="Queue must be high, default, or low"
        )

    conn = get_redis_conn()
    q = Queue(queue, connection=conn)

    jobs_info = []

    # Get jobs from appropriate registry based on status_filter
    if status_filter == "queued":
        job_ids = q.get_job_ids()
    elif status_filter == "started":
        job_ids = q.started_job_registry.get_job_ids()
    elif status_filter == "finished":
        job_ids = q.finished_job_registry.get_job_ids()
    elif status_filter == "failed":
        job_ids = q.failed_job_registry.get_job_ids()
    elif status_filter == "deferred":
        job_ids = q.deferred_job_registry.get_job_ids()
    else:
        # Get all jobs across all registries
        job_ids = (
            q.get_job_ids()
            + q.started_job_registry.get_job_ids()
            + q.finished_job_registry.get_job_ids()
            + q.failed_job_registry.get_job_ids()
            + q.deferred_job_registry.get_job_ids()
        )

    # Limit and fetch job details
    for job_id in job_ids[:limit]:
        try:
            from rq.job import Job

            job = Job.fetch(job_id, connection=conn)
            jobs_info.append(
                JobInfo(
                    id=job.id,
                    func=job.func_name or "unknown",
                    status=str(job.get_status()) if job.get_status() else "unknown",
                    queue=queue,
                    created_at=job.created_at.isoformat() if job.created_at else None,
                    started_at=job.started_at.isoformat() if job.started_at else None,
                    ended_at=job.ended_at.isoformat() if job.ended_at else None,
                )
            )
        except Exception:
            # Skip jobs that can't be fetched
            pass

    return JobsListResponse(jobs=jobs_info, total=len(job_ids))
