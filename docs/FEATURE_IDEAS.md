# Feature Ideas — Full-Stack Template

This document collects suggested features, grouped and annotated with their current status.

**Status legend:** ✅ Done · 🚧 Partial · 💡 Idea

---

## What's Already Built

| Feature | Status | Notes |
|---------|--------|-------|
| FastAPI + SQLModel + PostgreSQL + Alembic | ✅ | Full CRUD scaffold with typed models |
| React + TypeScript + Vite + shadcn/ui | ✅ | Strict mode, auto-generated client |
| Single unified Docker image | ✅ | Multi-stage build, Caddy reverse proxy |
| JWT authentication (email + password) | ✅ | Argon2/bcrypt, timing-safe verify |
| Microsoft Entra ID SSO | ✅ | Multi-tenant, role sync, auto-create users |
| RBAC (Roles + Permissions) | ✅ | DB-backed, assignable, permission checks in API |
| File storage (S3 + local fallback) | ✅ | Pluggable backend, signed URL pattern |
| Background tasks (RQ + Redis) | ✅ | Priority queues, DB-tracked lifecycle |
| Task dashboard | ✅ | Live stats, charts, job list, sample task launcher |
| WebSocket notifications | ✅ | Auth-gated, per-user push via pub/sub |
| GitHub Actions CI | ✅ | Test, lint, build, Docker image |
| Playwright E2E test scaffold | ✅ | Auth setup, shared state |

---

## API & Client

- 💡 **CI client generation gate** — Generate `openapi.json` in CI and fail the PR if the TypeScript client is out of date. Prevents silent type drift.
- 💡 **API key authentication** — Allow programmatic access via long-lived API keys (stored hashed in DB) as an alternative to JWT. Useful for integrations, scripts, and service-to-service calls.
- 💡 **Cursor-based pagination** — Offer cursor/keyset pagination alongside offset. Stable pages on large/fast-changing tables; include a migration guide for existing offset endpoints.
- 💡 **Bulk operation endpoints** — `POST /items/bulk` for create/update/delete with per-item validation and a summary response (`{succeeded: N, failed: [{index, error}]}`).
- 💡 **GraphQL option** — Optional Strawberry endpoint auto-derived from SQLModel schemas. Opt-in, versioned alongside REST.
- 💡 **Webhook outbound scaffold** — Subscribe endpoints that fan out events (`item.created`, `task.completed`) to registered URLs with HMAC signing and retry logic.

---

## Authentication & Authorization

- 💡 **OAuth providers** — GitHub and Google sign-in (via `authlib`), secure callback handling, account linking when email matches an existing user.
- 💡 **Passwordless / magic links** — Sign-in via a time-limited, single-use token emailed to the user. Lower friction for B2C flows.
- 💡 **Two-factor authentication (TOTP)** — Authenticator app (TOTP) support: enroll, verify, recovery codes, and a flag on the User model. Optional enforcement per role.
- 💡 **Admin user impersonation** — Superusers can issue a short-lived token scoped to any user for debugging. Logged to the audit trail.
- 💡 **Session management** — Track active sessions (device, IP, last seen), allow users to view and revoke them. Pairs with the refresh token pattern.

---

## Data & Storage

- 💡 **Full-text search** — PostgreSQL `tsvector` + GIN index as a zero-dependency first step; pluggable interface to swap in Meilisearch/Typesense. Include an indexing background task.
- 💡 **Redis caching layer** — `@cache(ttl=60)` decorator pattern for expensive reads. Invalidation helpers tied to model save/delete signals.
- 💡 **Soft deletes** — `deleted_at` timestamp pattern on chosen models, automatic filter in queries, recovery endpoint, and a periodic hard-delete task.
- 💡 **Audit log** — Append-only `AuditEvent` table (`who`, `what`, `resource_id`, `diff`, `ip`, `timestamp`). Hook into CRUD helpers and auth events. Expose read-only admin endpoint.
- 💡 **Data import (CSV / Excel)** — Upload a file → validate rows as background task → stream progress via WebSocket → return per-row errors. Pairs with the existing file storage and task system.
- 💡 **GDPR / privacy tools** — `GET /me/export` triggers a background task that packages the user's data as a ZIP + download link. `DELETE /me` hard-deletes with a confirmation token.

---

## Background Tasks & Scheduling

- 💡 **Scheduled / periodic tasks** — RQ Scheduler integration: define cron-style tasks in config (e.g. `cleanup_old_tasks` nightly). Dashboard shows next run time and last result.
- 💡 **Task chaining / pipelines** — Declarative pipelines (`upload → validate → process → notify`) using RQ's dependency API. Visualise the DAG in the dashboard.
- 💡 **Task retry policy** — Per-task `max_retries` and exponential backoff config. Store attempt count and last error on the `Task` model; surface in dashboard.
- 💡 **WebSocket task progress** — Push `task.progress` events via the existing WebSocket notification system instead of client-side polling. Tasks call `notify_user(task_id, progress)`.

---

## Payments & Billing

- 💡 **Stripe integration scaffold** — `Plan`, `Subscription`, `Invoice` models + Stripe webhook handler with idempotency. Middleware to gate routes behind active subscription.
- 💡 **Usage metering** — Track per-user resource consumption (API calls, storage bytes, task minutes) in a `UsageEvent` table. Aggregate for billing or rate-limit enforcement.

---

## Observability & Reliability

- 💡 **Structured JSON logging** — Replace default Uvicorn logs with `structlog` or `python-json-logger`. Include `request_id`, `user_id`, `duration_ms` on every request log.
- 💡 **OpenTelemetry tracing** — Auto-instrument FastAPI, SQLAlchemy, and RQ. Export to an OTLP collector (Jaeger/Grafana Tempo). Trace IDs surfaced in error responses.
- 💡 **Prometheus metrics endpoint** — `GET /metrics` with request counts, latency histograms, active task gauge, DB pool stats. Add a Grafana dashboard JSON to `docs/`.
- 💡 **Deep health check** — `GET /health` returns DB, Redis, and storage connectivity status. Used by Caddy/load balancer probes and on-call runbooks.
- 💡 **Sentry integration** — Drop-in error capture with environment-tagged releases, performance sampling, and PII scrubbing.

---

## Security & Hardening

- 💡 **Rate limiting** — Per-user and per-IP throttling with `slowapi` (wraps `limits`). Configurable per route, stored in Redis. Returns `Retry-After` header.
- 💡 **Security headers** — Caddy or middleware preset: CSP, HSTS, `X-Frame-Options`, `Permissions-Policy`. Testing checklist and `securityheaders.com` score target.
- 💡 **Input sanitisation middleware** — Strip/escape dangerous content from string fields before persistence. Configurable blocklist per model field.
- 💡 **Dependency vulnerability scanning** — Add `uv audit` / `pip-audit` + `npm audit` to CI. Break on high/critical. Dependabot config for auto-PRs.
- 💡 **Secrets rotation guide** — Runbook and helper script for rotating `SECRET_KEY`, DB credentials, and Redis password without downtime.

---

## CI/CD & Infrastructure

- 💡 **IaC starter (Terraform / Pulumi)** — Boilerplate for cloud VPC, managed Postgres, Redis, object storage, and container registry. Multi-environment (staging/prod) with variable files.
- 💡 **Preview environments** — GitHub Actions workflow to spin up an ephemeral stack per PR (e.g. Railway or Fly.io), run E2E tests, and tear down on merge.
- 💡 **Database seeding CLI** — `uv run python -m backend.scripts.seed` that creates realistic demo data for local dev and staging. Configurable counts and deterministic UUIDs.
- 💡 **Zero-downtime migrations** — Patterns and a checklist for additive schema changes (expand/contract), feature flags to guard migration phases, and rollback procedures.

---

## Frontend & UX

- 💡 **Dark/light mode user preference** — Persist theme choice in the `User` record (not just `localStorage`) so it roams across devices.
- 💡 **Internationalisation (i18n)** — `react-i18next` scaffold, `i18next-parser` extraction, and a locale-switching component. Backend returns locale-aware error messages.
- 💡 **Onboarding wizard** — Post-signup walkthrough (profile completion, first item, invite team) with completion tracking stored on the User model.
- 💡 **In-app notification centre** — Persistent notification list (read/unread, types, links) backed by a DB table, fed by the existing WebSocket push channel.
- 💡 **Admin bulk user management** — Multi-select user table: bulk invite via CSV, bulk role assignment, bulk deactivation. Progress shown via background task + WebSocket.
- 💡 **Offline / optimistic updates** — React Query optimistic mutation patterns and a service worker example for PWA-style offline support.

---

## Testing & Quality

- 💡 **Contract tests** — Validate that the live backend OpenAPI spec matches what the TypeScript client was generated from. CI job fails on drift.
- 💡 **E2E CI job** — Playwright suite running against `docker compose` on GitHub Actions with video artifacts on failure and test-container postgres.
- 💡 **Load test scaffold** — `locust` script covering auth, CRUD, file upload, and task enqueue. Run in CI on merge to main; alert on regression.
- 💡 **Property-based tests** — `hypothesis` examples for model validators and CRUD edge cases (null fields, boundary values, unicode).
- 💡 **Mutation testing** — `mutmut` baseline score and CI gate. Identifies tests that don't actually assert anything meaningful.

---

## Documentation & Onboarding

- 💡 **Architecture diagram (Mermaid)** — Service topology, auth flows, task lifecycle, and file upload flow as Mermaid diagrams embedded in `docs/`.
- 💡 **Cookbook** — Short recipes: "Add an endpoint", "Add a model field + migrate", "Regen client", "Add a new task type", "Add a Playwright test". Keep it in `docs/cookbook.md`.
- 💡 **Deploy runbook** — Step-by-step: first deploy, rollback, DB migration in production, secret rotation, incident response checklist.
- 💡 **ADR log** — Architecture Decision Records for key choices (why RQ over Celery, why SQLModel, why single Docker image). Helps future contributors understand tradeoffs.

---

## Optional Integrations

- 🚧 **Microsoft Entra ID** — Done; gaps: automated tenant onboarding flow, provisioning API, group-to-role mapping, and Entra ID-side app manifest docs.
- 💡 **AI / LLM connector** — Example `LLMService` wrapping Mistral AI (or OpenAI-compatible): prompt template pattern, streaming response, token usage tracking, and cost guard.
- 💡 **Email provider abstraction** — Swap the current SMTP stub for Resend/SendGrid/Postmark with a common `EmailBackend` interface. HTML template tooling via Jinja2.
- 💡 **Analytics event pipeline** — `AnalyticsEvent` model + background task that forwards to PostHog or Segment. Track signups, feature usage, and funnels without blocking requests.
- 💡 **Data connectors** — Pluggable source connectors (SQL databases, REST APIs, CSV files) that ingest into a staging table as background tasks. Foundation for data pipeline features.

---

## Prioritisation Tiers (suggested)

| Tier | Features |
|------|----------|
| **1 · Quick wins** | API key auth, rate limiting, structured logging, deep health check, DB seeding CLI, CI client-gen gate |
| **2 · High value** | Audit log, scheduled tasks, task retry + WebSocket progress, full-text search, TOTP 2FA, Sentry, preview environments |
| **3 · Growth features** | Stripe billing, OAuth providers, GDPR tools, data import, i18n, in-app notification centre |
| **4 · Advanced** | OpenTelemetry, IaC starter, LLM connector, data connectors, load testing, mutation testing |

---

*Last updated: 2026-03-03. Discuss priorities during sprint planning.*
