"""Background task enqueueing and status endpoints."""

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rq.exceptions import NoSuchJobError
from rq.job import Job

from backend.api.deps import CurrentUser, SuperUserDep
from backend.core.queue import get_queue

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class EnqueueRequest(BaseModel):
    task: Literal["send_email", "export_data", "process_file"]
    queue: Literal["default", "high", "low"] = "default"
    # Task-specific keyword arguments
    kwargs: dict[str, Any] = {}


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Any = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/enqueue", response_model=JobStatusResponse)
def enqueue_task(
    *,
    body: EnqueueRequest,
    _current_user: CurrentUser,
) -> Any:
    """Enqueue a background task. Returns the job ID immediately."""
    task_map = {
        "send_email": "backend.tasks.example.send_email_task",
        "export_data": "backend.tasks.example.export_data_task",
        "process_file": "backend.tasks.example.process_file_task",
    }

    func_path = task_map[body.task]
    module_path, func_name = func_path.rsplit(".", 1)

    import importlib

    module = importlib.import_module(module_path)
    func = getattr(module, func_name)

    q = get_queue(body.queue)
    job = q.enqueue(func, **body.kwargs)

    return JobStatusResponse(job_id=job.id, status="queued")


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(
    job_id: str,
    _current_user: CurrentUser,
) -> Any:
    """Check the status of an enqueued job."""
    from backend.core.queue import get_redis_conn

    try:
        job = Job.fetch(job_id, connection=get_redis_conn())
    except NoSuchJobError:
        raise HTTPException(status_code=404, detail="Job not found") from None

    status = job.get_status()
    result = job.result if status and status.value == "finished" else None
    error = job.exc_info if status and status.value == "failed" else None

    return JobStatusResponse(
        job_id=job_id,
        status=str(status.value) if status else "unknown",
        result=result,
        error=str(error) if error else None,
    )


@router.delete("/{job_id}")
def cancel_job(
    job_id: str,
    _: SuperUserDep,
) -> dict[str, str]:
    """Cancel a queued job (superuser only)."""
    from backend.core.queue import get_redis_conn

    try:
        job = Job.fetch(job_id, connection=get_redis_conn())
    except NoSuchJobError:
        raise HTTPException(status_code=404, detail="Job not found") from None

    job.cancel()
    return {"message": f"Job {job_id} cancelled"}
