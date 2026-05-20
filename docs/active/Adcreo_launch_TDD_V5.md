# ADCREO — TECHNICAL DESIGN DOCUMENT v5

**Version:** 5.0
**Date:** 2026-05-19
**Supersedes:** TDD v4 (B-roll layer extended per v4-Δ1; downstream anchors migrated for consistency)
**Authority:** Architecture Review (18 May 2025) + System Architect pass (19 May 2026)
**Status:** CANONICAL — this document supersedes TDD v4 in all affected sections. The `[TDD-BROLL]` chapter (introduced in v4-Δ1) is the authoritative spec for B-roll behavior; all anchors that referenced the v3 flat-list contract have been migrated. Open design decisions are listed in the `CONSISTENCY FLAGS` block at the foot of this document; production-blocking items have been resolved in-document.

---

## Reader's Note — How This Document Is Assembled

TDD v4 is produced by mechanical merge of two inputs:

1. **TDD v3** — preserved verbatim in all Category 1 sections (anchors listed in `[TDD-CICD-MANIFEST]` below).
2. **Architecture Review (18 May 2025)** — the authority document whose decisions are encoded as new Category 2 (replace), Category 3 (extend), and Category 4 (new) sections.

Where a section anchor is marked `[SECTION PRESERVED FROM TDD V3 — COPY VERBATIM: <anchor>]`, the human merge step must paste the exact corresponding content from TDD v3 into that slot. No transformation is allowed on those slots — the placeholders are a copy-control mechanism, not a rewrite license.

Where a section is fully written here, it supersedes TDD v3 entirely or extends a v3 section with explicit append boundaries.

---

## Table of Contents

### Body
- `[TDD-META]` · System Directive for Agentic IDE *(preserved)*
- `[TDD-OVERVIEW]` · System Overview & Tech Stack *(preserved)*
- `[TDD-PILLARS]` · Architectural Literature Foundation — 7 Pillars *(preserved, Category 1)*
- `[TDD-BANNED]` · Banned Architectural Patterns *(preserved)*
- `[TDD-STACK]` · The 8-Layer Stack *(preserved)*
- `[TDD-DATA-FLOW]` · End-to-End Data Flow *(preserved)*
- `[TDD-R2-BUCKETS]` · R2 Bucket Structure *(preserved)*
- `[TDD-R2-RETENTION]` · R2 Data Retention Enforcement *(preserved, Category 1)*
- `[TDD-IMPORT-GRAPH]` · Component Boundary & Import Graph *(preserved, Category 1)*
- `[TDD-CHAT-CHAIN]` · Co-Pilot 5-Stage Middleware Chain *(preserved, Category 1)*
- `[TDD-SCAFFOLD]` · Project Scaffold *(preserved)*
- `[TDD-PINNED-CONTEXT]` · Context-Window Discipline *(preserved)*
- `[TDD-ENUMS]` · Postgres Extensions & Enums *(preserved, Category 1)*
- `[TDD-SCHEMA]` · Core Tables *(preserved)*
- `[TDD-FSM]` · State Transition Trigger *(extended — Category 3A)*
- `[TDD-TYPES]` · TypeScript Interfaces & Pydantic Models *(preserved, Category 1)*
- `[TDD-MIGRATIONS]` · Data Migrations *(preserved, Category 1)*
- `[TDD-INDICES]` · Required Database Indices *(preserved)*
- `[TDD-PROMPTS]` · PromptOps Architecture *(preserved, Category 1)*
- `[TDD-WORKERS]` · Worker Architecture & Implementations *(preserved, Category 1 — `[TDD-WORKERS]-C2` superseded by `[TDD-BROLL]` per v4-Δ1; `[TDD-WORKERS]-G` extended for template resolution + rotation logging)*
- `[TDD-BROLL]` · B-Roll Selection & Composition Strategy *(NEW — v4-Δ1, authoritative)*
- `[TDD-VIDEO]` · Video Composition & Provenance *(preserved, Category 1 — Worker-COMPOSE branch logic extended per `[TDD-BROLL]-H`; signature gains `structure_template`)*
- `[TDD-API]` · State Management & API Design *(preserved, Category 1)*
- `[TDD-REDIS]` · Redis Architecture, Key Design & Lua Scripts *(preserved, Category 1)*
- `[TDD-CONCURRENCY]` · Concurrency Patterns *(extended — Category 3B)*
- `[TDD-GATEWAY]` · Model Gateway & CostGuard *(preserved, Category 1)*
- `[TDD-GUARDS]` · OutputGuard & ComplianceGate *(preserved, Category 1)*
- `[TDD-FLYWHEEL]` · Data Flywheel & Style Memory *(preserved)*
- `[TDD-STRATEGY]` · Strategy Card & Chat Engine Contracts *(preserved, Category 1)*
- `[TDD-DLQ]` · Dead-Letter Queue Handler *(preserved, Category 1)*
- `[TDD-DIRECTOR]` · Director's Suggestion Engine *(preserved, Category 1)*
- `[TDD-SECURITY]` · Security Model *(preserved)*
- `[TDD-TAKEDOWN]` · IT Rules 2026 Auto-Takedown Pipeline *(preserved, Category 1)*
- `[TDD-CICD]` · CI/CD Pipeline **— REPLACED (Category 2A)**
- `[TDD-IDE]` · Antigravity Agentic IDE Directives *(preserved, Category 1)*
- `[TDD-TRACE]` · Traceability Matrix *(preserved)*
- `[TDD-ERROR-RECOVERY]` · Error Recovery Expectations *(preserved, Category 1)*
- `[TDD-OBSERVABILITY]` · Observability Stack **— REPLACED (Category 2B)**
- `[TDD-MIGRATION-SAFETY]` · Migration Safety Policy *(preserved)*
- `[TDD-ROLLBACK]` · Rollback Policy *(preserved, Category 1 — runbook split to `[TDD-DEPLOY-RUNBOOK]`)*
- `[TDD-API-STUBS]` · Static API Stubs for Agent CI *(preserved, Category 1)*

### New sections (Category 4)
- `[TDD-DEPLOYMENT]` · Infrastructure topology, Nginx + Cloudflare Tunnel, systemd
- `[TDD-DISASTER-RECOVERY]` · RTO/RPO, Neon PITR, R2 versioning, monthly drill
- `[TDD-DEPLOY-RUNBOOK]` · `deploy.sh`, `rollback.sh`, `/healthz` contracts
- `[TDD-ENV-MANIFEST]` · Complete environment variable inventory

### Tail
- `CONSISTENCY FLAGS` — issues for human review pass

---


## [TDD-META] · System Directive for Agentic IDE

**AGENT INSTRUCTION — READ ONCE, THEN IGNORE `<HumanContext>`.**

Content in `<HumanContext>...</HumanContext>` tags is human-facing narrative (rationale, pillar backstory). **Non-normative.** Skip past these blocks; anchor on `[TDD-*]` tags instead.

Every `[TDD-*]` tag is a stable searchable anchor. Every function name, ENUM value, SQL identifier, file path, and metric name is a frozen identifier. Grep them verbatim.

**Bi-directional traceability.** Every major section carries a **Fulfills PRD Requirement:** line naming the exact `[PRD-*]` tag(s) it implements. This forms the Directed Acyclic Graph (DAG) the agent walks from PRD tag → TDD implementation.

**Context-window discipline.** See `[TDD-PINNED-CONTEXT]`. Load into active context only the files the current task touches. Do not ingest the whole TDD.

**Single source of truth for behaviour.** PRD v3 defines WHAT; TDD v3 defines HOW. When they seem to disagree, the PRD is the contract — file a reconciliation ticket rather than silently diverging.

**Meta:**

| Attribute      | Value                                                                                                                                                  |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Version        | 3 (née v20.0, surgical repair of v2)                                                                                                                   |
| Date           | April 2026                                                                                                                                             |
| Classification | CONFIDENTIAL · GOLDEN RC · Source of Truth                                                                                                             |
| Status         | MVP Locked · Agent-Ready · Aligned to PRD Locked (Version 3)                                                                                           |
| Invariants     | Dynamic Playbook · Decoupled Export · Dual-Branch DLQ · 5-Stage Chat Chain · Origin-Preserving Webhook · Monotonic Idempotency · 2xx-Only Cache        |

---


---


## [TDD-OVERVIEW] · System Overview & Tech Stack

**Fulfills PRD Requirement:** `[PRD-VISION]`, `[PRD-PIPELINE]`, `[PRD-NON-NEGOTIABLES]`

### Product Context

Adcreo is an India-first agentic AI video ad co-pilot. Converts product URLs or photos into around 15-20 second SGI-compliant video ads in under 3 minutes. Starter users hard-gated at Phase 3 (HD-4) — cannot trigger renders. Every screen HD-1..HD-6 always shown, pre-filled ("Agentic Draft Model"). Confidence shapes visuals; never skips screens.

### Core Constraints

| Constraint              | Value                                                                                                                                                                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Target Latency          | <3 minutes end-to-end                                                                                                                                                                                                              |
| COGS Ceilings           | ₹2/₹10/₹14 (Starter/Essential/Pro), chat budget included                                                                                                                                                                           |
| Compliance              | IT Rules 2026 100%                                                                                                                                                                                                                 |
| Green Zone              | 5 categories (immutable enum)                                                                                                                                                                                                      |
| Export Formats          | Exactly 2: 1080×1080 (1:1) + 1080×1920 (9:16)                                                                                                                                                                                      |
| Free-Text Inputs        | Zero for primary inputs. Bounded chat (max 500 chars, 20 words, classified intents)                                                                                                                                                |
| Co-Pilot Chat           | Max 3 turns/gen, ~₹0.08/turn, 5-stage chain enforced — `[TDD-CHAT-CHAIN]`                                                                                                                                                          |
| Framework Routing       | Exactly 3 of 12 (default: 1 logic + 1 emotion + 1 conversion). SAFE_TRIO fallback on weak evidence — `[TDD-PROMPTS]`                                                                                                               |
| Strategy Card           | MANDATORY before Phase 4. Never auto-skipped                                                                                                                                                                                       |
| Credit Lock Ordering    | Lua `wallet_lock` fires in `/approve-strategy` BEFORE Phase 4 dispatch. Same pattern on `/retry-export` Step 7. No Phase 4 compute without active credit lock                                                                      |
| Export Decoupling       | `phase4_coordinator` ENDS at `preview_ready`. `worker_export` is separate ARQ function enqueued by L2 routes (`/declaration` or `/retry-export`)                                                                                   |
| DLQ Branching           | `on_job_dead` dispatches by `job.function_name`: phase4 → `failed_render`; worker_export → `failed_export`. Both refund                                                                                                            |
| Style Memory            | Opt-in, resettable. pgvector cosine similarity. Embedding: OpenAI `text-embedding-3-small` (1536-dim)                                                                                                                              |
| STRATEGIST Worker       | Zero external API. CI import-graph check                                                                                                                                                                                           |
| UI Flow                 | 6 linear screens HD-1..HD-6. Mobile: progressive disclosure                                                                                                                                                                        |
| Network Resiliency      | `Idempotency-Key` header on mutating routes. localStorage `aw_idem_{user_id}_{gen_id}_{action}` + server `actlock` fence (10s TTL). 5-min Redis cache. **2xx-only cache.** Monotonic key for retry-export: `:{export_retry_count}` |
| DLQ Self-Healing        | Dead ARQ jobs transition via `on_job_dead()`. SSE push <5s. Refund on all Phase-4 failures                                                                                                                                         |
| Infrastructure Budget   | ₹15,000/month fixed. Single Hetzner CCX32. No horizontal scaling                                                                                                                                                                   |
| Upload & Scraper Bounds | Uploads 10MB (L2, 413). Firecrawl 15s. Scraped images 15MB cap                                                                                                                                                                     |
| Data Retention          | Starter assets purged 7d; Paid source/preview 30d; SGI exports 5y. Daily cron 02:00 IST. Weekly orphan sweep Mon 02:30 IST                                                                                                         |
| Tab Resilience          | Mount → synchronous `GET /api/generations/{gen_id}` before SSE attach. SSE reconnect also triggers rehydration                                                                                                                     |

### Tech Stack

| Layer           | Primary                                                                                                                                | Notes                                                                                                                                  |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Frontend        | Next.js 15 (App Router) · React 19 · TypeScript · TailwindCSS · shadcn/ui                                                              | SSR shell + CSR interactivity                                                                                                          |
| Backend         | FastAPI · Python 3.12 · Pydantic v2                                                                                                    | ASGI via Uvicorn                                                                                                                       |
| Task Queue      | ARQ (Redis-backed)                                                                                                                     | 2 processes: `adcreo-studio`, `adcreo-render` (also hosts worker_export)                                                        |
| Database        | Neon Postgres 17 + pgvector                                                                                                            | Single region (Mumbai)                                                                                                                 |
| Cache/Lock      | Redis 7 (6 DBs)                                                                                                                        | DB0 wallet cache + balance SSE; DB1 ARQ queues; DB2 COGS tracker; DB3 provider health + CB; DB4 rate limits; DB5 idempotency + actlock |
| Object Storage  | Cloudflare R2                                                                                                                          | SSE-S3 encryption; 30-day lifecycle for previews                                                                                       |
| LLM Gateway     | DeepSeek (primary), GPT-4o (fallback), Gemini 2.0 Flash (vision fallback)                                                              | `gateway.route(capability)`                                                                                                            |
| Voice           | Sarvam TTS (Hindi/Hinglish), ElevenLabs (English fallback)                                                                             |                                                                                                                                        |
| Image→Video     | Fal.ai (primary), Minimax (fallback)                                                                                                   | Max 180s per candidate. Canonical list: `[TDD-GATEWAY]-A` `CAPABILITY_PROVIDERS`                                                       |
| Vision          | Gemini Vision Pro, GPT-4V                                                                                                              | `gateway.route(capability="vision")`                                                                                                   |
| Scraping        | Firecrawl API                                                                                                                          | 15s timeout, clean Markdown output                                                                                                     |
| Image Isolation | BiRefNet (local, Apache 2.0) — rembg library, model=birefnet-general                                                                                                                  | Loaded globally in ARQ process via rembg library                                                                                        |
| Safety          | Llama Guard (via Groq)                                                                                                                 | Routed via `gateway.route(capability='moderation')`                                                                                    |
| C2PA Signing    | c2patool (local binary)<br>Post-sign verification:<br>- MUST run `c2patool --verify`<br>- MUST NOT call any external verification APIs | returncode checked                                                                                                                     |
| Payments        | Razorpay (UPI)                                                                                                                         | Webhook-driven. HMAC-SHA256. `payment_status` FSM                                                                                      |

### Dev Tooling

| Tool                 | Purpose                                                                                               |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| Pytest               | Unit + integration; FSM transition fuzzer                                                             |
| Playwright           | E2E incl. cross-tab Idempotency-Key, retry-export inline re-sign                                      |
| Grafana + Prometheus | Metrics + alerting (incl. framework routing distribution)                                             |
| PostHog              | Product analytics, user signals (incl. v3 signals)                                                    |
| Grafana Cloud alerts | P1/P2 incident alerting                                                                               |
| GitHub Actions       | lint, test, promptops, compliance, strategist-sandbox (import-graph), fsm-coverage, migration-dry-run |

---



---


## [TDD-PILLARS] · Architectural Literature Foundation — 7 Pillars

**Fulfills PRD Requirement:** `[PRD-NON-NEGOTIABLES]`, `[PRD-PIPELINE]`

| #   | Pillar                          | Source                                              | What We Adopted                                                                                                                                                                                                                                                                                                                        |
| --- | ------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Agentic Orchestration**       | Biswas & Talukdar — *Building Agentic AI Systems*   | **CWD (Coordinator-Worker-Delegator).** Restricted Tools: workers call `gateway.route()`, never import SDKs. Import-graph CI (`[TDD-IMPORT-GRAPH]`) enforces STRATEGIST has zero `httpx`/`requests`/`aiohttp`. A2A multi-agent and MCP tool servers banned. Framework routing = single enum-validated LLM call, not multi-agent debate |
| 2   | **Bounded Inference Economics** | Chip Huyen — *AI Engineering*                       | **CostGuard** with hard per-gen ceilings (₹2/₹10/₹14). COGS recorded immediately on LLM return, before safety (closes rejected-chat-turn leak). ModelGateway with capability routing, `selection_reason` logging, circuit-breaker FSM. Dynamic Playbook routing bounds token spend to exactly 3 framework scripts                      |
| 3   | **Deep Modules**                | Ousterhout — *A Philosophy of Software Design*      | Each worker has simple interface (`process(gen_id, ...)`) hiding complex internals. 22-state FSM + `pre_topup_status` eliminates ambiguous limbos. `@idempotent(ttl=300, cache_only_2xx=True)` decorator. phase4_coordinator is deep module hiding TTS∥I2V fan-in                                                                      |
| 4   | **Data-Intensive Foundations**  | Kleppmann — *Designing Data-Intensive Applications* | **JSONB god-table** (`generations`). Exactly-once via Idempotency-Key + localStorage cross-tab. Append-only partitioned `audit_log` with REVOKE UPDATE/DELETE, 5-year DETACH archival. **Redis = Lock+Cache, Postgres = Ledger (ledger-first)**. `pre_topup_status` is snapshot column on god-table — single-row read hydrates screen  |
| 5   | **Stability Under Failure**     | Nygard — *Release It!*                              | **Circuit Breakers** CLOSED/OPEN/HALF_OPEN FSM. Timeouts: Firecrawl 15s, I2V 180s, TTS 30s, chat LLM 15s, c2patool 30s. Bulkheads: 6 isolated Redis DBs + per-phase ARQ worker processes. **Dual-branch DLQ** (`[TDD-DLQ]`): phase4 → `failed_render`; worker_export → `failed_export`. Each refunds independently                     |
| 6   | **Vertical-First Scalability**  | Ejsmont — *Web Scalability for Startup Engineers*   | Single Hetzner CCX32 (8 vCPU, 32GB). Async decoupling via ARQ with per-phase bulkheads. Day-2 escape: Upstash/Neon serverless. worker_export registered on existing `adcreo-render` — free bulkhead                                                                                                                                   |
| 7   | **Modular Monolith**            | Richardson — *Microservices Patterns*               | **Adopted: Compensating Transactions** (Redis Lua refund on any `failed_render` / `failed_export`). Banned: Sagas, Transactional Outbox, microservices decomposition. `/retry-export` 9-step chain = one DB txn + one Lua call + one ARQ enqueue                                                                                       |

---



---


## [TDD-BANNED] · Banned Architectural Patterns

**Fulfills PRD Requirement:** `[PRD-NON-NEGOTIABLES]`, `[PRD-PIPELINE]`

| Pattern                                           | Why Banned                                                                                                                                                                                                                                                                             | Pillar |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| Multi-Agent Negotiation (A2A)                     | Massive latency, high token costs, unpredictable UX                                                                                                                                                                                                                                    | 1      |
| MCP Servers / Tool Servers                        | We orchestrate, not host tool servers                                                                                                                                                                                                                                                  | 1      |
| Microservices Decomposition                       | Solo dev. Modularity via Python Deep Modules                                                                                                                                                                                                                                           | 7      |
| Sagas / Transactional Outbox                      | Over-engineering. Compensating transactions only                                                                                                                                                                                                                                       | 7      |
| Horizontal Scaling / Load Balancers               | Single CCX32. Vertical first                                                                                                                                                                                                                                                           | 6      |
| GPU Fleet / Self-Hosted Models                    | All inference via 3rd-party APIs                                                                                                                                                                                                                                                       | 2      |
| DB Sharding / Replication                         | Single Neon handles 10k-20k users                                                                                                                                                                                                                                                      | 4      |
| Global ASGI Response-Cache Middleware             | Starlette middleware that consumes `response.body()` after `call_next()` breaks SSE streams. Use route decorators                                                                                                                                                                      | 3      |
| `sessionStorage` for cross-tab state              | sessionStorage is per-tab. Use `localStorage` + `storage` event listener                                                                                                                                                                                                               | 4      |
| `-shortest` flag in FFmpeg compose                | Truncates to shortest input — silences or chops CTAs                                                                                                                                                                                                                                   | 3      |
| **Worker-COPY open-ended generation**             | "Generate 5 filter 2" wastes tokens, unpredictable variety. Use `framework_router → generate_per_framework`                                                                                                                                                                            | 1 + 2  |
| **`phase4_coordinator` enqueueing worker_export** | Couples render/export economics. HD-6 retries must preserve ~₹10 Phase-4 assets. Coordinator STOPS at `preview_ready`                                                                                                                                                                  | 3 + 7  |
| **Single-branch DLQ**                             | Dual-branch required. Dispatch by `job.function_name`                                                                                                                                                                                                                                  | 5      |
| **Hardcoded webhook restoration target**          | Razorpay webhook MUST read `pre_topup_status` and restore atomically. Hardcoding `status='strategy_preview'` silently kicks HD-6-origin users back to HD-4                                                                                                                             | 4      |
| **Presigned R2 URLs inside workers**              | Workers run minutes after URL minting; 10-min TTL expires. Workers MUST use credentialed `boto3` access exclusively. Presigned URLs are strictly forbidden inside workers. B-roll assets MUST be stored in Cloudflare R2 using structured folders (e.g. `/broll/category/archetype/`). | 5      |
| Zero-Shadowing policy                             | no module/package may reuse stdlib names or shadow sibling packages; canonical backend names are infra_* and schemas/* only.                                                                                                                                                           |        |

---


---


## [TDD-STACK] · The 8-Layer Stack

**Fulfills PRD Requirement:** `[PRD-PIPELINE]`, `[PRD-NON-NEGOTIABLES]`, `[PRD-UI-TREE]`

```
┌─────────────────────────────────────────────────────────────────────────┐
│ L1: CLIENT LAYER                                                         │
│ Next.js 15 · TailwindCSS · shadcn/ui · Zustand · SSE                    │
│ Components: ConfidenceFlag, CoPilotChatSheet, StrategyCard, ScriptCard, │
│ FrameworkLabel, MotionSelector, EnvCanvas, DirectorTips, TopUpDrawer    │
│ (state-aware overlay), DeclarationCheckboxes (inline re-sign path 4b)   │
│ All 6 screens always shown. No screen-skipping.                          │
│ Idempotency-Key in LOCALSTORAGE: aw_idem_{user_id}_{gen_id}_{action} +   │
│ cross-tab `storage` event sync.                                          │
│ Monotonic key for retry-export: suffix `:{export_retry_count}`.          │
│ On mount → GET hydration BEFORE SSE attach.                              │
│ SSE reconnect: GET rehydrate + backoff (1s,2s,4s,30s).                   │
│ 4xx (400,402,409,428) → drop localStorage key, fresh on next click.      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ L2: API GATEWAY (Delegator)                                              │
│ FastAPI · Pydantic v2 · JWT (session_version claim)                      │
│ ONLY layer with WALLET WRITE + pre_topup_status WRITE privileges.        │
│ @idempotent(ttl=300, action_key, cache_only_2xx=True) + actlock fence.   │
│ Upload hard cap 10MB (413). Razorpay HMAC-SHA256 verify.                 │
│ CREDIT LOCK LIVES HERE: /approve-strategy → wallet_lock.lua → enqueue    │
│   phase4_coordinator on DB1 (adcreo-render).                            │
│ DECOUPLED EXPORT: /declaration → enqueue worker_export on DB1; state    │
│   preview_ready → export_queued.                                         │
│ /retry-export: 9-step atomic chain (audit→lock→state→enqueue).          │
│ Lock-fail on either path: ATOMIC write of pre_topup_status +             │
│   status='awaiting_funds' in single UPDATE.                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ L3: COMPLIANCE LAYER                                                     │
│ ComplianceGate (input) · OutputGuard (output)                           │
│ /chat invokes ComplianceGate.check_input FIRST (Stage 1 of 5-stage).    │
│ /generate invokes ComplianceGate on URL/image at ingest.                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ L4: TASK QUEUE — ARQ (Redis) · PER-PHASE BULKHEAD                       │
│ Priority: Pro > Essential > Starter                                      │
│ Process A (interactive): adcreo-studio — phase1_extract,          │
│   phase2_chain, phase3_strategist, retention_sweep, r2_orphan_sweep,    │
│   partition_rotator                                                       │
│ Process B (heavy): adcreo-render — phase4_coordinator, worker_export   │
│   (DECOUPLED) · max_jobs=6 · job_timeout=300s                           │
│ DLQ Handler: on_job_dead() — DUAL-BRANCH ROUTING:                       │
│   function_name=='phase4_coordinator' → failed_render + REFUND          │
│   function_name=='worker_export'      → failed_export + REFUND          │
│ Timeouts: I2V=180s, TTS=30s, COMPOSE=60s, EXPORT=45s, COORD=300s        │
│ Daily: retention_sweep 02:00 IST (incl. 5-yr export purge)               │
│ Daily: partition_rotator 02:15 IST (next-month audit_log partition)      │
│ Weekly: r2_orphan_sweep Mon 02:30 IST                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ L5: AGENTIC ORCHESTRATOR (Coordinator)                                   │
│ CWD Coordinator · ModelGateway · CostGuard (COGS-first record)          │
│ PromptOps · Circuit-Breaker FSM (CLOSED/OPEN/HALF_OPEN)                  │
│ HALTS at strategy_preview. phase4_coordinator HALTS at preview_ready.    │
│ CANNOT: direct model calls, wallet mutation, pre_topup_status writes.    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ L6: WORKER FLEET (11 Workers + 1 Coordinator)                            │
│ EXTRACT · COPY (3 modes: framework_router/generate_per_framework/refine)│
│ · CRITIC · SAFETY · STRATEGIST · TTS · I2V · REFLECT · COMPOSE ·        │
│ EXPORT · phase4_coordinator (fan-in)                                     │
│ STRATEGIST: ZERO httpx/requests/aiohttp (CI-enforced).                   │
│ EXPORT: standalone ARQ job, NOT enqueued by coordinator.                 │
│ All workers use credentialed R2 access (NOT presigned URLs).             │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ L7: DATA LAYER — Postgres=Ledger, Redis=Lock+Cache                       │
│ Neon Postgres (State + pre_topup_status + Signals + pgvector +           │
│   audit_log PARTITIONED monthly)                                         │
│ Redis 7 (6 DBs):                                                         │
│   DB0 = Wallet cache (per-gen lock fields) + Balance SSE                 │
│   DB1 = ARQ queues (interactive + heavy)                                 │
│   DB2 = COGS tracker (24h TTL)                                          │
│   DB3 = Provider health + Circuit Breaker state                         │
│   DB4 = Rate limiting                                                    │
│   DB5 = Idempotency cache (300s) + actlock fence (10s)                  │
│ Postgres=Ledger (source of truth). All credit mutations → Postgres first.│
│ R2 lifecycle enforced by daily retention_sweep. DB-first, R2-second.     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ L8: EXTERNAL APIs                                                       │
│ I2V: Fal.ai ,Minimax                                                    │
│ TTS: Sarvam (Bulbul V3), ElevenLabs, Google Cloud                       │
│ LLM: DeepSeek V3.2,Groq,Gemini, Together AI, SiliconFlow                │
│ Vision: Gemini Vision Pro, GPT-4V                                       │
│ Embeddings: OpenAI text-embedding-3-small (1536 dim)                              │
│ Tools: Firecrawl, BiRefNet, c2patool, Razorpay (UPI)
│Auth: Google ADC (gcloud auth) strictly enforced; NO JSON keys allowed
└─────────────────────────────────────────────────────────────────────────┘
```








---



---


## [TDD-DATA-FLOW] · End-to-End Data Flow

**Fulfills PRD Requirement:** `[PRD-PIPELINE]`, `[PRD-HD1..HD6]`, `[PRD-FSM]`, `[PRD-PRETOPUP]`, `[PRD-PLAYBOOK]`

```
User pastes URL on HD-1
       │
       ▼
[L2 POST /generate] ── L3 ComplianceGate.check_input ──► REJECT → 400 ECM-002
       │ pass                 Upload>10MB → 413 ECM-014. Scraped>15MB → ECM-001.
       ▼
[L4 ARQ adcreo-studio] phase1_extract
       │
PHASE 1: INGESTION
  Worker-EXTRACT:
    ├── Firecrawl API (asyncio.timeout 15s, Markdown return)
    ├── BiRefNet (loaded globally in ARQ memory via rembg)
    └── gateway.route(capability='vision') → Gemini Vision
  → ProductBrief + confidence_score
       │
  State: extracting → brief_ready → HD-2 shown
       │
PHASE 2: STRATEGY — DYNAMIC PLAYBOOK
  Worker-COPY.framework_router (single LLM call, strict enum output)
    → routed_frameworks[3] + routing_rationale
  Worker-COPY.generate_per_framework (asyncio.gather × 3)
    → returns 3 framework-tagged scripts in parallel
       │
  State: scripting → critiquing
  Worker-CRITIC.score(3 scripts, brief) → ranked list
       │
  State: critiquing → safety_checking
  Worker-SAFETY.batch_check(3) → safe_scripts (≥1 else failed_safety, 1× safe-trio retry)
       │
  State: safety_checking → scripts_ready → HD-3
  UI shows 3 framework-labeled scripts; top scorer pre-selected.
       │
  /chat (≤3 turns): CANONICAL 5-STAGE CHAIN (see [TDD-CHAT-CHAIN])
    ComplianceGate → CostGuard.pre_check → LLM (script-refine) →
    CostGuard.record (immediate) → OutputGuard → atomic UPDATE
       │
  POST /advance → scripts_ready → strategy_preview (STRATEGIST, ZERO ext APIs)
  Worker-STRATEGIST resolves structure_template (T1..T5) and active_season,
  then invokes BRollPlanner.plan(template, angle, category, brand_tier, user_id)
  → produces b_roll_plan = {template, hook, context, cta} — see [TDD-BROLL]-G
       │
PHASE 3: INTENT GATE (MANDATORY HALT — HD-4)
  HD-4 shown. [Edit] → /edit-back (NULLs downstream).
  [Confirm & Use 1 Credit → Render] → /approve-strategy:
    ├── Starter → 403 STARTER_RENDER_BLOCKED
    ├── @idempotent cache + actlock fence
    ├── INSERT wallet_transactions(type='lock', status='locked', credits=-1, gen_id) [LEDGER FIRST]
    ├── wallet_lock.lua(user_id, gen_id):
    │      ├── fail → ATOMIC UPDATE status='awaiting_funds', pre_topup_status='strategy_preview'
    │      │           ROLLBACK ledger row
    │      └── success → UPDATE status='funds_locked'
    └── arq.enqueue('phase4_coordinator', gen_id) on DB1
       │
PHASE 4: PRODUCTION (HD-5 → HD-6)
  phase4_coordinator (fan-in):
    funds_locked → rendering
    await asyncio.gather(WorkerTTS, WorkerI2V×2)
    → Worker-REFLECT (SSIM + deformation guard) → reflecting → rendering
    → Worker-COMPOSE (FFmpeg 5s canonical, no -shortest, LUT, SGI drawtext) → composing
    → composing → preview_ready
    ★★★ COORDINATOR STOPS HERE. Does NOT enqueue worker_export. ★★★
       │
  HD-6: video player + 3 unsigned declaration checkboxes.
  User checks 3/3 + "Download HD" → /declaration:
    capture IP + UA + SHA256 → INSERT audit_log →
    UPDATE status='export_queued' → arq.enqueue('worker_export', gen_id) on DB1
       │
  worker_export (independent ARQ job):
    credentialed R2 download → ffmpeg scale 1080×1080 + 1080×1920 →
    c2patool sign each (rc checked, fail → DLQ) →
    upload R2 → UPDATE exports JSONB + c2pa_manifest_hash + status='export_ready'
    → SSE export_ready → Style Memory upsert
       │
  HAPPY PATH ENDS. Downloads active.
       │
  ─────────────── FAILURE BRANCHES (DUAL-BRANCH DLQ) ───────────────
       │
  Phase-4 render dies (TTS/I2V/REFLECT/COMPOSE/coordinator):
    on_job_dead(job) where function_name=='phase4_coordinator':
      → wallet_refund.lua + INSERT wallet_transactions(type='refund', status='refunded')
      → UPDATE status='failed_render', dlq_dead_at=NOW()
      → SSE 'render_failed' (HD-5 inline recovery)
      → [↻ Try Again] → failed_render → strategy_preview → HD-4 (re-lock)
  Worker-EXPORT dies (c2pa rc≠0, R2 upload fail, ffmpeg fail):
    on_job_dead(job) where function_name=='worker_export':
      → wallet_refund.lua + INSERT wallet_transactions(type='refund', status='refunded')
      → UPDATE status='failed_export', dlq_dead_at=NOW()
      → SSE 'export_failed' (HD-6 inline recovery)
      → [↻ Retry Export] → /retry-export 9-step chain
       │
  /retry-export (9-step atomic):
    1. Validate state=='failed_export' AND user owns gen_id
    2. Validate export_retry_count < 3 (else 410 ECM-019)
    3. Validate plan_tier != 'starter' (defensive 403)
    4. Check audit_log declaration freshness (<24h):
       STALE AND declarations!=[1,1,1] → 428 ECM-020 (NO state change)
       STALE AND declarations==[1,1,1] → INSERT new audit_log row (atomic preamble)
    5. R2 HEAD on preview_url. 404/410 → 410 ECM-018 (terminal)
    6. BEGIN transaction
    7. INSERT wallet_transactions(type='lock', status='locked') + wallet_lock.lua:
       lua=0 → ATOMIC UPDATE status='awaiting_funds', pre_topup_status='failed_export'
               ROLLBACK ledger; return 402 ECM-007
       lua=1 → continue
    8. UPDATE status='export_queued', export_retry_count = export_retry_count + 1
    9. arq.enqueue('worker_export', gen_id). COMMIT.
       │
  /webhook/razorpay (origin-preserving):
    HMAC-SHA256 verify (else 401)
    payment_status FSM: pending → captured|failed (terminal ignore reorder)
    On 'captured': UPSERT wallet_transactions(type='topup', payment_status='captured', credits=+4|+25)
      [UNIQUE INDEX prevents double-credit]
    Redis cache updated.
    ATOMIC UPDATE: SET status=pre_topup_status, pre_topup_status=NULL
                   WHERE user_id=? AND status='awaiting_funds'
    (Multi-row safe: HD-4-origin → strategy_preview; HD-6-origin → failed_export)
    SSE 'topup_captured' → all open tabs → drawer closes
```

---



---


## [TDD-R2-BUCKETS] · R2 Bucket Structure

**Fulfills PRD Requirement:** `[PRD-FEATURES-RETENTION]`, `[PRD-PIPELINE]`

```
adcreo-assets/
├── {user_id}/
│   ├── {gen_id}/
│   │   ├── source/original.{jpg|png}
│   │   ├── isolated/product.png
│   │   ├── tts/voiceover.{mp3|wav}
│   │   ├── i2v/
│   │   │   ├── candidate_0.mp4
│   │   │   └── candidate_1.mp4
│   │   ├── compose/preview.mp4
│   │   └── export/
│   │       ├── square_1x1.mp4        (1080×1080, C2PA-signed)
│   │       └── vertical_9x16.mp4     (1080×1920, C2PA-signed)
│   └── style-memory/profile.json
```

Worker-EXPORT overwrites export objects on retry (same path). Previous `c2pa_manifest_hash` overwritten in the same UPDATE — no orphan hashes.

---


---


## [TDD-R2-RETENTION] · R2 Data Retention Enforcement

**Fulfills PRD Requirement:** `[PRD-FEATURES-RETENTION]`, `[PRD-FEATURES-COMPLIANCE]`, `[PRD-NON-NEGOTIABLES]`

| Asset Type | Starter TTL | Paid TTL | Legal Basis |
|---|---|---|---|
| Source images | 7 days | 30 days | DPDP Act §8(7) |
| Isolated PNGs | 7 days | 30 days | DPDP Act §8(7) |
| Preview videos | 7 days | 30 days | DPDP Act §8(7) |
| Finalized SGI exports | N/A | 5 years (purged on anniversary) | IT Rules 2026 §5 + DPDP over-retention |
| Audit logs (PG, partitioned) | 5 years | 5 years | IT Rules 2026 §5 |

```python
# /app/workers/retention_sweep.py — DB-first, R2-second atomicity
async def retention_sweep(ctx):
    """Daily ARQ cron 02:00 IST. Pillar 5."""
    # Step 1: Starter 7-day
    starter_rows = await db.fetch("""
        SELECT gen_id, source_image_url, isolated_png_url, preview_url
        FROM generations WHERE plan_tier = 'starter'
          AND created_at < NOW() - INTERVAL '7 days'
          AND (source_image_url IS NOT NULL OR isolated_png_url IS NOT NULL
               OR preview_url IS NOT NULL)
        FOR UPDATE SKIP LOCKED""")
    await _atomic_purge_rows(starter_rows,
        keys=['source_image_url', 'isolated_png_url', 'preview_url'])

    # Step 2: Paid 30-day source/preview (NOT exports)
    paid_rows = await db.fetch("""
        SELECT gen_id, source_image_url, isolated_png_url, preview_url
        FROM generations WHERE plan_tier IN ('essential', 'pro')
          AND created_at < NOW() - INTERVAL '30 days'
          AND (source_image_url IS NOT NULL OR isolated_png_url IS NOT NULL
               OR preview_url IS NOT NULL)
        FOR UPDATE SKIP LOCKED""")
    await _atomic_purge_rows(paid_rows,
        keys=['source_image_url', 'isolated_png_url', 'preview_url'])

    # Step 3: 5-year finalized exports
    five_yr_rows = await db.fetch("""
        SELECT gen_id, exports FROM generations
        WHERE status = 'export_ready' AND exports IS NOT NULL
          AND COALESCE((exports->>'finalized_at')::timestamptz,
                       updated_at) < NOW() - INTERVAL '5 years'
        FOR UPDATE SKIP LOCKED""")
    for row in five_yr_rows:
        urls = [row['exports'].get('square_url'), row['exports'].get('vertical_url')]
        async with db.transaction():
            await db.execute("UPDATE generations SET exports = NULL WHERE gen_id = $1",
                             row['gen_id'])
        for u in filter(None, urls):
            try:
                await r2_client.delete_object(u)
                RETENTION_SWEEP_DELETIONS.inc()
            except Exception as e:
                logger.warning(f"5yr-purge R2 fail {u}: {e}")

async def _atomic_purge_rows(rows, keys):
    """DB-first, R2-second. Orphans > zombies."""
    for row in rows:
        async with db.transaction():
            set_clauses = ", ".join(f"{k} = NULL" for k in keys)
            await db.execute(f"UPDATE generations SET {set_clauses} WHERE gen_id = $1",
                             row['gen_id'])
        for k in keys:
            if row[k]:
                try:
                    await r2_client.delete_object(row[k])
                    RETENTION_SWEEP_DELETIONS.inc()
                except Exception as e:
                    logger.warning(f"R2 orphan {row[k]}: {e}")

async def partition_rotator(ctx):
    """Daily 02:15 IST. Pre-creates next-month audit_log partition."""
    next_month = (datetime.utcnow().replace(day=1) + timedelta(days=32)).replace(day=1)
    month_after = (next_month + timedelta(days=32)).replace(day=1)
    partition_name = f"audit_log_{next_month.strftime('%Y_%m')}"
    await db.execute(f"""
        CREATE TABLE IF NOT EXISTS {partition_name}
        PARTITION OF audit_log FOR VALUES FROM ('{next_month.isoformat()}')
        TO ('{month_after.isoformat()}');
        REVOKE UPDATE, DELETE ON {partition_name} FROM PUBLIC;
    """)
    PARTITION_ROTATIONS.labels(month=next_month.strftime('%Y-%m')).inc()
```

---


---


## [TDD-IMPORT-GRAPH] · Component Boundary & Import Graph

**Fulfills PRD Requirement:** `[PRD-NON-NEGOTIABLES]`

Pillar 1 (Restricted Tools) + Pillar 7 (no network microservices) + Pillar 3 (Deep Modules).

Worker-STRATEGIST has absolute zero external API access. CI import-graph blocks `httpx`, `requests`, `aiohttp` inside strategist module.

### Allowed-Imports Matrix

| Module \ Imports        | `httpx`/`requests` | `gateway.route` | `db` (asyncpg) | `redis_*`  | `rembg (BiRefNet)` | `ffmpeg` subp | `c2patool` subp |
| ----------------------- | :----------------: | :-------------: | :------------: | :--------: | :-------------------: | :-----------: | :-------------: |
| `workers/strategist.py` |                    |                 |     ✅ read     | ✅ DB3 read |                       |               |                 |
| `workers/extract.py`    |                    |        ✅        |       ✅        |            |           ✅           |               |                 |
| `workers/copy.py`       |                    |        ✅        |       ✅        |            |                       |               |                 |
| `workers/critic.py`     |                    |        ✅        |       ✅        |            |                       |               |                 |
| `workers/safety.py`     |                    |        ✅        |       ✅        |            |                       |               |                 |
| `workers/tts.py`        |                    |        ✅        |       ✅        |            |                       |               |                 |
| `workers/i2v.py`        |                    |        ✅        |       ✅        |            |                       |               |                 |
| `workers/reflect.py`    |                    |        ✅        |       ✅        |            |                       |               |                 |
| `workers/compose.py`    |                    |                 |       ✅        |            |                       |       ✅       |                 |
| `workers/export.py`     |                    |                 |       ✅        |            |                       |       ✅       |        ✅        |
| `infra_gateway.py`      |         ✅          |        —        |       ✅        |   ✅ DB3    |                       |               |                 |
| `api/routes/*.py` (L2)  |                    |                 |       ✅        |     ✅      |                       |               |                 |

**Golden rule:** Only `infra_gateway.py` imports external HTTP clients. Worker-SAFETY routes through `gateway.route(capability="moderation")` like every other worker — the prior direct-OpenAI carve-out is REMOVED to close the CI cost trap and the import-graph hole. CI `strategist-sandbox` hard-fails on violation.

```python
# /ci/strategist_sandbox_check.py — AST-based import guard
RULES = {
    "app/workers/strategist.py": ["httpx", "requests", "aiohttp", "urllib.request",
                                   "openai", "anthropic", "google.genai", "boto3"],
    "app/workers/compose.py":   ["httpx", "requests", "aiohttp"],
    "app/workers/export.py":    ["httpx", "requests", "aiohttp"],
    "app/workers/copy.py":      ["httpx", "requests", "aiohttp", "openai", "anthropic"],
    "app/workers/critic.py":    ["httpx", "requests", "aiohttp", "openai", "anthropic"],
    "app/workers/tts.py":       ["httpx", "requests", "aiohttp"],
    "app/workers/i2v.py":       ["httpx", "requests", "aiohttp"],
    "app/workers/reflect.py":   ["httpx", "requests", "aiohttp"],
    # v4-Δ1: extend sandbox to the B-roll planner module. Forbids both HTTP clients (defense
    # against drift into runtime API calls) AND embedding/vector ML libraries (defense against
    # drift toward learned clip selection — [TDD-BROLL]-J makes this an explicit non-goal).
    "app/broll/":               ["httpx", "requests", "aiohttp", "openai", "anthropic",
                                  "sentence_transformers", "chromadb", "faiss", "faiss-cpu",
                                  "transformers", "torch"],
}
# Walks AST, checks Import/ImportFrom nodes, exits non-zero on violation.
# v4-Δ1: prefix-match keys ending in '/' apply to all .py files under that directory.
```

**v4-Δ1 extension:** the strategist sandbox check (`ci/strategist_sandbox_check.py`) is extended to the entire `app/broll/` directory and additionally forbids imports of `sentence_transformers`, `chromadb`, `faiss`, `transformers`, and `torch` — defense against future drift toward embedding-based clip selection. The role-first deterministic SQL planner is the design contract; any pressure to add learned ranking should re-open `[TDD-BROLL]` rather than bypass this CI rule. See `[TDD-BROLL]-J`.

---


---


## [TDD-CHAT-CHAIN] · Co-Pilot 5-Stage Middleware Chain

**Fulfills PRD Requirement:** `[PRD-COPILOT]`, F-207, F-603, `[PRD-ERROR-MAP]`

The PRD mandates a strict 5-stage chain on every Co-Pilot Chat turn. This is the single normative specification; divergence in `/chat` route code is a CI failure.

```
POST /api/generations/{gen_id}/chat
Headers: Idempotency-Key, Authorization (JWT)
Body (mutually exclusive — exactly one field per request):
  Shape A (chip action): { "action": "chip_punchier" | "chip_hinglish" | "chip_diwali" }
  Shape B (free text):   { "message": string (1..500 chars, ≤20 words) }
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 0 (PRE-CHAIN): @idempotent + actlock fence                        │
│   - Look up cached 2xx response → return if present.                    │
│   - Acquire actlock:{gen_id}:chat (10s TTL). Cross-tab → 409 ECM-012.   │
│   - Validate state=='scripts_ready' AND chat_turns_used < 3.            │
└─────────────────────────────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: L3 ComplianceGate.check_input(req.message)                     │
│   - Sanitize control chars (zero-width, RTL marks)                      │
│   - Detect prompt-injection ("ignore previous", role-swap, etc.)        │
│   - Word count ≤ 20 words (hard fail)                                   │
│   On reject: emit `chat_compliance_rejected` → 400 ECM-011              │
│   (NO LLM call, turn NOT counted, NO COGS, release actlock, NO cache)   │
└─────────────────────────────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: L5 CostGuard.pre_check(gen_id, est_cost=0.08)                  │
│   - Read cogs_total from Redis DB2: cogs:{gen_id}                       │
│   - If current + 0.08 > CEILING[plan_tier]:                             │
│     emit `chat_costguard_rejected` → 429 ECM-009                        │
│     (NO LLM call, turn NOT counted, NO COGS, release actlock, NO cache) │
└─────────────────────────────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: LLM call via gateway.route(capability='llm')                   │
│   - PromptOps render: script-refine.v1.0.0.yaml                         │
│   - Model: deepseek-v3.2 · Timeout: 15s (asyncio.wait_for)              │
│   - On timeout/provider-fail: ProviderUnavailableError → 503            │
│     (NOT counted as turn; NO COGS — call failed, no spend)              │
└─────────────────────────────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: L5 CostGuard.record(gen_id, gateway.last_call_cost)            │
│   ★★★ MUST FIRE BEFORE STAGE 5 — rejected-turn-leak fix (F-603) ★★★      │
│   - HINCRBYFLOAT cogs:{gen_id} total +<actual_cost>                     │
│   - INSERT agent_traces(cost_inr, tokens_in, tokens_out, latency_ms,    │
│     model_used, selection_reason)                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: L3 OutputGuard.check_output(refined.full_text)                 │
│   - Llama Guard safety check (via ModelGateway) + PII regex +           │
│     competitor name regex                                                │
│   - Validate against script-refine.v1.0.0.yaml output_schema            │
│   On reject:                                                             │
│     emit `chat_outputguard_rejected`                                    │
│     UPDATE generations SET cogs_total = cogs_total + last_cost          │
│       (sync Postgres ledger with Redis DB2)                             │
│     → 422 ECM-010 (release actlock, NO cache)                           │
└─────────────────────────────────────────────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ COMMIT: atomic state-guarded UPDATE                                      │
│   UPDATE generations SET refined_script=$2,                              │
│          chat_turns_used = chat_turns_used + 1,                          │
│          chat_history = chat_history || $3::jsonb || $4::jsonb,          │
│          cogs_total = cogs_total + $5                                    │
│   WHERE gen_id=$1 AND status='scripts_ready' AND chat_turns_used < 3    │
│   RETURNING chat_turns_used;                                             │
│   rowcount=0 (state drifted) → 409 ECM-012, NO cache                    │
│   emit `chat_turn_complete`, release actlock, cache 2xx (300s TTL)      │
│   return ChatResponse { refined_script, turns_used, turns_remaining,    │
│                         cost_inr }                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Chip Action Bypass (implements BEF gap — MP3-C3)

HD-3 quick-action chips (Punchier / Hinglish / Diwali) are
system-authored commands, not user-crafted freetext. Running
them through Stage 1 ComplianceGate injection detection is
logically incorrect — we would be scanning our own strings.

**Payload dispatch (evaluated at Stage 0, before Stage 1):**

- IF request body contains `"action"` key (Shape A):
  → Skip Stage 1 entirely. The `action` value is system-authored.
  → Map `action` → instruction string via the server-side lookup
    table (defined in `app/api/routes/chat.py`). Pass the instruction
    string directly into Stage 3 (`WorkerCopy.refine`).
  → Log `source_type = "chip_action"` in `agent_traces`.
  → All other stages (0, 2, 3, 4, 5) and all invariants run
    unchanged. Turn counter, actlock, idempotency cache: unchanged.

- IF request body contains `"message"` key (Shape B):
  → Full 5-stage chain runs unchanged. No bypass.
  → Log `source_type = "free_text"` in `agent_traces`.

**Server-side chip action lookup table (frozen for MVP):**
````
"chip_punchier" → "Make this script more punchy and direct.
                   Keep the same framework and product facts."
"chip_hinglish" → "Rewrite this script in natural Hinglish
                   (Hindi-English mix). Keep the meaning intact."
"chip_diwali"   → "Add a Diwali festival context to this script.
                   Keep the product focus and framework."
````
These instruction strings are internal system text. They are NOT
stored as the user-turn in chat_history. The action code itself
(e.g. "chip_hinglish") is stored as the user-turn display value.

### Invariants enforced by the chain

| Invariant | Enforcement Site |
|---|---|
| ComplianceGate runs BEFORE any spend | Stage 1 returns 400 before Stage 2/3 |
| CostGuard.pre_check runs BEFORE any spend | Stage 2 returns 429 before Stage 3 |
| CostGuard.record runs BEFORE OutputGuard | Stage 4 mutates Redis BEFORE Stage 5. Enforced by `tests/test_chat_chain_order.py` |
| Rejected refinement preserves COGS | Stage 5 reject path commits recorded spend to Postgres |
| Rejected refinement does NOT count toward 3-turn limit | `chat_turns_used` only incremented in COMMIT |
| Rejected refinement NOT cached | All 4xx paths skip `redis_db5.setex(idem:...)` |
| Cross-tab safety | `actlock:{gen_id}:chat` fence (10s TTL) + 2xx-only cache |
| State-drift handled | Atomic UPDATE `WHERE status='scripts_ready' AND chat_turns_used < 3` RETURNING; rowcount=0 → 409 |

### CI Test Coverage

```python
# tests/test_chat_chain_order.py
async def test_compliance_runs_before_costguard(monkeypatch): ...
async def test_costguard_record_runs_before_outputguard(monkeypatch): ...
async def test_outputguard_reject_preserves_cogs_in_postgres(monkeypatch): ...
async def test_outputguard_reject_does_not_increment_turns(monkeypatch): ...
async def test_outputguard_reject_not_cached(monkeypatch): ...
```

---


---


## [TDD-SCAFFOLD] · Project Scaffold

**Fulfills PRD Requirement:** `[PRD-PIPELINE]`, `[PRD-UI-TREE]`

```
adcreo/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/              # L2 endpoints
│   │   ├── workers/                 # EXTRACT, COPY, CRITIC, SAFETY, STRATEGIST, TTS, I2V, REFLECT, COMPOSE, EXPORT, phase4_coordinator
│   │   ├── gateway/                 # ModelGateway · CostGuard · circuit breakers
│   │   ├── guards/                  # ComplianceGate · OutputGuard
│   │   ├── dlq/                     # on_job_dead · dual-branch routing
│   │   ├── models/                  # Pydantic schemas
│   │   ├── schemas/                   # shared enums (AdFramework, FrameworkAngle, PreTopupStatus)
│   │   ├── prompts/                 # PromptOps YAML catalog
│   │   ├── lua/                     # wallet_lock, wallet_consume, wallet_refund, circuit_breaker
│   │   ├── takedown/                # IT Rules 2026 auto-takedown pipeline
│   │   ├── broll/                   # Static B-roll library + planner + 5-template router (NEW v3, extended v4-Δ1)
│   │   │   ├── library.json
│   │   │   ├── planner.py
│   │   │   └── templates.py         # TEMPLATE_BY_CONTEXT + MOOD_BY_ANGLE (frozen, CI-locked)
│   │   └── migrations/              # alembic-style .sql forward-only
│   ├── tests/
│   │   ├── fsm/                     # test_state_transitions_v20.py
│   │   ├── api/                     # route tests
│   │   └── contracts/               # cross-repo type contract tests
│   └── ci/                          # strategist_sandbox_check.py, fsm_coverage_check.py, migration_dry_run.py
├── frontend/
│   ├── app/                         # Next.js App Router: /hd-1 .. /hd-6 + /error
│   ├── components/
│   ├── lib/
│   │   ├── tokens.ts
│   │   └── sse.ts
│   └── tests/                       # Playwright E2E + component tests
├── shared/
│   └── types/
└── docs/
    ├── MVP_PRD_(AdvertWise).md
    └── MVP_TDD_(AdvertWise).md
```

---


---


## [TDD-PINNED-CONTEXT] · Context-Window Discipline

**Fulfills PRD Requirement:** `[PRD-NON-NEGOTIABLES]` (agent hygiene)

Load only what the current task touches. Never ingest whole TDD or whole PRD.

| Task | Load into context |
|---|---|
| **FSM / migration change** | `backend/app/migrations/`, `[TDD-FSM]` section, `[TDD-MIGRATIONS]`, `tests/fsm/test_state_transitions_v20.py` |
| **Worker implementation** | That worker's file in `backend/app/workers/`, `[TDD-WORKERS]`, relevant Pydantic model, relevant prompt YAML |
| **API route change** | That route file in `backend/app/api/routes/`, relevant `[TDD-API-*]` subsection, relevant Pydantic model |
| **Prompt change** | `backend/app/prompts/{catalog.yaml, that prompt}.yaml`, `[TDD-PROMPTS]`, `tests/promptops/` |
| **Frontend screen change** | That screen's `frontend/app/hd-X/page.tsx`, related components, `shared/types/generation.ts`, `frontend/lib/tokens.ts` |
| **Design token change** | `frontend/app/globals.css`, `frontend/tailwind.config.ts`, `frontend/lib/tokens.ts`, `frontend/components.json`, `[PRD-DESIGN-TOKENS]` section |
| **Lua script change** | That `.lua` file in `backend/app/lua/`, `[TDD-REDIS]`, related worker/route using it, `tests/lua/` |
| **CI check addition** | `backend/ci/<check>.py`, `.github/workflows/ci.yml` |
| **Observability / metric** | `[TDD-OBSERVABILITY]`, relevant worker or route, Grafana dashboard JSON |
| **Error recovery / rollback** | `[TDD-ERROR-RECOVERY]`, `[TDD-ROLLBACK]`, `[TDD-DLQ]` |

**Never load:** the entire TDD or entire PRD unless doing full-system review. Grep by tag; pull the section; stop.

---


---


## [TDD-ENUMS] · Postgres Extensions & Enums

**Fulfills PRD Requirement:** `[PRD-FSM]`, `[PRD-PRETOPUP]`, `[PRD-GREENZONE]`, `[PRD-PLAYBOOK]`, `[PRD-PAYMENT-FSM]`

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 22-state FSM. pre_topup_status uses the SAME enum type as status but is a
-- separate column. Transitions validated by enforce_state_transition() trigger.
CREATE TYPE job_status AS ENUM (
    -- Phase 1
    'queued', 'extracting', 'brief_ready',
    -- Phase 2
    'scripting', 'critiquing', 'safety_checking', 'scripts_ready', 'regenerating',
    -- Phase 3
    'strategy_preview',
    'awaiting_funds',  -- HD-4 OR HD-6 (disambiguated by pre_topup_status)
    'funds_locked',
    -- Phase 4
    'rendering', 'reflecting', 'composing', 'preview_ready',
    'export_queued', 'export_ready',
    -- Terminal
    'failed_category', 'failed_compliance', 'failed_safety',
    'failed_render', 'failed_export'
);

CREATE TYPE plan_tier AS ENUM ('starter', 'essential', 'pro');

-- payment_status applies ONLY to wallet_transactions.type='topup' (Razorpay FSM).
CREATE TYPE payment_status AS ENUM ('pending', 'captured', 'failed', 'refunded');

-- wallet_status applies ONLY to wallet_transactions.type IN ('lock','consume','refund').
CREATE TYPE wallet_status AS ENUM (
    'locked',     -- credit reserved, not yet spent
    'consumed',   -- credit spent on successful export
    'refunded'    -- credit returned via DLQ compensation
);

-- Dynamic Playbook framework enum.
CREATE TYPE ad_framework AS ENUM (
    'pas_micro', 'clinical_flex', 'myth_buster',
    'asmr_trigger', 'usage_ritual', 'hyper_local_comfort',
    'spec_drop_flex', 'premium_upgrade', 'roi_durability_flex',
    'festival_occasion_hook', 'scarcity_drop', 'social_proof'
);

CREATE TYPE green_zone_category AS ENUM (
    'd2c_beauty', 'packaged_food', 'hard_accessories',
    'electronics', 'home_kitchen'
);
```

---


---


## [TDD-SCHEMA] · Core Tables

**Fulfills PRD Requirement:** `[PRD-FSM]`, `[PRD-PRETOPUP]`, `[PRD-HD1]`, `[PRD-HD2]`, `[PRD-HD3]`, `[PRD-HD4]`, `[PRD-HD5]`, `[PRD-HD6]`, `[PRD-FEATURES-PAYMENT]`

```sql
-- ═══════════════════════════════════════════════════════════════════════
-- generations — the JSONB god-table (Pillar 4: Deep Module)
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE generations (
    gen_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(user_id),
    status              job_status DEFAULT 'queued',
    -- Screen-context preservation across topup. Non-NULL IFF status='awaiting_funds'.
    pre_topup_status    job_status NULL,
    plan_tier           plan_tier NOT NULL,

    -- Phase 1
    source_url          VARCHAR(2048) CHECK (char_length(source_url) <= 2048),
    source_image_url    TEXT,
    isolated_png_url    TEXT,
    confidence_score    DECIMAL(3, 2),
    product_brief       JSONB,
    product_shape       VARCHAR(20),
    agent_crop_suggestion TEXT,
    agent_motion_suggestion INTEGER,

    -- Phase 2 (Dynamic Playbook)
    campaign_brief      JSONB,
    routed_frameworks   ad_framework[],     -- 3 frameworks selected by Worker-COPY
    routing_rationale   JSONB,               -- rationale per framework (LLM-supplied)
    raw_scripts         JSONB,               -- 3 framework-tagged scripts (NOT 5)
    critic_scores       JSONB,
    safety_flags        JSONB,
    safe_scripts        JSONB,
    selected_script_id  INTEGER,
    motion_archetype_id INTEGER,
    environment_preset_id INTEGER,
    -- v4-Δ1: shape changed from array to object {template, hook, context, cta} per [TDD-BROLL]-G.
    --        DEFAULT now NULL (the old DEFAULT '[]' violates the new CHECK; legacy rows are backfilled
    --        to NULL by migration step (22) before the new CHECK is applied).
    b_roll_plan                 JSONB DEFAULT NULL,
    -- v4-Δ1: B-roll template + season binding + reserved performance signal (see [TDD-BROLL]-E)
    structure_template          VARCHAR(5) CHECK (structure_template IN ('T1','T2','T3','T4','T5')),
    active_season               VARCHAR(30) REFERENCES seasons(season_tag),
    b_roll_performance_signal   JSONB,  -- reserved; populated by v2 attribution loop; see [TDD-BROLL]-I

    -- Co-Pilot Chat (capped at 3 turns = max 6 messages)
    chat_history        JSONB DEFAULT '[]' CHECK (jsonb_typeof(chat_history) = 'array'
                                                  AND jsonb_array_length(chat_history) <= 6),
    chat_turns_used     INTEGER DEFAULT 0 CHECK (chat_turns_used BETWEEN 0 AND 3),
    refined_script      JSONB,

    -- Phase 3
    strategy_card       JSONB,
    strategy_approved_at TIMESTAMPTZ,

    -- Phase 4
    tts_language        VARCHAR(20) DEFAULT 'hindi',
    tts_audio_url       TEXT,
    i2v_candidates      JSONB,
    selected_i2v_url    TEXT,
    preview_url         TEXT,
    exports             JSONB,                  -- {square_url, vertical_url, c2pa_manifest_hash, finalized_at}
    fallback_events     JSONB DEFAULT '[]',

    -- Monotonic retry counter for /retry-export
    export_retry_count  INTEGER NOT NULL DEFAULT 0 CHECK (export_retry_count BETWEEN 0 AND 3),

    -- Economics
    cogs_total          DECIMAL(10, 4) DEFAULT 0,

    -- Compliance (declaration provenance)
    declaration_accepted BOOLEAN DEFAULT FALSE,
    declaration_accepted_at TIMESTAMPTZ,
    declaration_ip      INET,
    declaration_ua      TEXT,
    declaration_hash    VARCHAR(64),
    c2pa_manifest_hash  VARCHAR(64),

    -- Errors
    error_code          VARCHAR(50),
    error_message       TEXT,
    retry_count         INTEGER DEFAULT 0,

    -- DLQ tracking
    dlq_dead_at         TIMESTAMPTZ,
    dlq_original_task   VARCHAR(50),

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),

    -- pre_topup_status paired-write invariant (CHECK + trigger defense in depth)
    CONSTRAINT chk_pre_topup_coupling CHECK (
        (status = 'awaiting_funds' AND pre_topup_status IN ('strategy_preview','failed_export'))
        OR
        (status <> 'awaiting_funds' AND pre_topup_status IS NULL)
    ),

    -- routed_frameworks must contain exactly 3 distinct values when set
    CONSTRAINT chk_routed_frameworks_cardinality CHECK (
        routed_frameworks IS NULL OR
        (array_length(routed_frameworks, 1) = 3 AND
         array_length(routed_frameworks, 1) = (SELECT COUNT(DISTINCT v) FROM unnest(routed_frameworks) v))
    ),

    -- v3: explicit JSONB shape constraints
    CONSTRAINT chk_product_brief_shape CHECK (
        product_brief IS NULL OR (
            jsonb_typeof(product_brief) = 'object'
            AND product_brief ? 'product_name'
            AND product_brief ? 'category'
            AND product_brief ? 'key_features'
            AND jsonb_typeof(product_brief->'key_features') = 'array'
        )
    ),
    CONSTRAINT chk_exports_shape CHECK (
        exports IS NULL OR (
            jsonb_typeof(exports) = 'object'
            AND exports ? 'square_url'
            AND exports ? 'vertical_url'
            AND exports ? 'c2pa_manifest_hash'
            AND exports ? 'finalized_at'
        )
    ),
    CONSTRAINT chk_strategy_card_shape CHECK (
        strategy_card IS NULL OR (
            jsonb_typeof(strategy_card) = 'object'
            AND strategy_card ? 'product_summary'
            AND strategy_card ? 'script_summary'
            AND strategy_card ? 'voice'
            AND strategy_card ? 'motion'
            AND strategy_card ? 'environment'
            AND strategy_card ? 'compliance'
        )
    ),
    -- v4-Δ1: b_roll_plan is now object-shaped {template, hook, context, cta} per [TDD-BROLL]-G/K.
    --        NULL is explicitly permitted (represents "no plan yet" pre-Phase 3 and is a valid terminal
    --        state if the strategist defers planning; Worker-COMPOSE refuses to run with NULL).
    CONSTRAINT chk_b_roll_plan_shape CHECK (
        b_roll_plan IS NULL
        OR (
            jsonb_typeof(b_roll_plan) = 'object'
            AND b_roll_plan ? 'template'
            AND b_roll_plan ? 'hook'
            AND (b_roll_plan->>'template') IN ('T1','T2','T3','T4','T5')
        )
    )
);

-- ═══════════════════════════════════════════════════════════════════════
-- users
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE users (
    user_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_id           VARCHAR(255) UNIQUE NOT NULL,
    email               VARCHAR(255) UNIQUE NOT NULL,
    name                VARCHAR(255),
    plan_tier           plan_tier DEFAULT 'starter',
    credits_remaining   INTEGER DEFAULT 0,
    plan_expires_at     TIMESTAMPTZ,
    generation_count    INTEGER DEFAULT 0,
    session_version     INTEGER DEFAULT 1,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════
-- wallet_transactions — split schema: payment_status vs status
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE wallet_transactions (
    txn_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(user_id),
    type                VARCHAR(20) NOT NULL
                        CHECK (type IN ('topup', 'lock', 'consume', 'refund', 'expire')),
    credits             INTEGER NOT NULL,
    razorpay_payment_id VARCHAR(100),

    -- Cleanly separated lifecycle columns
    payment_status      payment_status,  -- ONLY for type='topup'; NULL otherwise
    status              wallet_status,   -- ONLY for type IN ('lock','consume','refund'); NULL otherwise

    gen_id              UUID REFERENCES generations(gen_id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_wallet_status_coupling CHECK (
        (type = 'topup'  AND status IS NULL AND payment_status IS NOT NULL)
        OR
        (type IN ('lock','consume','refund') AND payment_status IS NULL AND status IS NOT NULL)
        OR
        (type = 'expire' AND payment_status IS NULL AND status IS NULL)
    )
);

CREATE UNIQUE INDEX ux_wallet_topup_dedup
    ON wallet_transactions (razorpay_payment_id)
    WHERE type = 'topup' AND payment_status = 'captured';

CREATE UNIQUE INDEX ux_wallet_active_lock
    ON wallet_transactions (gen_id)
    WHERE status = 'locked';

CREATE UNIQUE INDEX ux_wallet_refund_dedup
    ON wallet_transactions (gen_id, type)
    WHERE type = 'refund';

-- ═══════════════════════════════════════════════════════════════════════
-- audit_log — partitioned, 5-year archival via DETACH
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE audit_log (
    id                  BIGSERIAL,
    gen_id              UUID,
    user_id             UUID,
    action              VARCHAR(100) NOT NULL,
    payload             JSONB,
    ip_address          INET,
    user_agent          TEXT,
    declaration_sha256  VARCHAR(64),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- ═══════════════════════════════════════════════════════════════════════
-- status_history — forensic record of every FSM transition
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE status_history (
    id                  BIGSERIAL PRIMARY KEY,
    gen_id              UUID NOT NULL REFERENCES generations(gen_id),
    from_status         job_status,
    to_status           job_status NOT NULL,
    from_pre_topup_status job_status,
    to_pre_topup_status   job_status,
    changed_by          VARCHAR(50) DEFAULT 'system',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════
-- compliance_log
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE compliance_log (
    id                  BIGSERIAL PRIMARY KEY,
    gen_id              UUID NOT NULL REFERENCES generations(gen_id),
    check_type          VARCHAR(50) NOT NULL,
    result              VARCHAR(20) NOT NULL CHECK (result IN ('pass', 'fail', 'warn')),
    details             JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);


**`compliance_log.check_type` Canonical Taxonomy** (4 strings, fixed enum semantics):

| `check_type`           | Emitting Source                         | Trigger                                                    |
| ---------------------- | --------------------------------------- | ---------------------------------------------------------- |
| `c2pa_sign`            | `app/workers/export.py`                 | C2PA manifest written; `c2patool` returncode==0            |
| `sgi_burn_in`          | `app/workers/compose.py` + `export.py`  | FFmpeg `drawtext` SGI watermark applied                    |
| `declaration_capture`  | `app/api/routes/declaration.py`         | First-time HD-6 declaration accepted (audit_log INSERT)    |
| `freshness_check`      | `app/api/routes/retry_export.py` Step 4 | 24h freshness validated OR atomic re-sign performed        |

CI rule (`ci/validate_compliance_taxonomy.py`): grep all `INSERT INTO compliance_log` call-sites; assert `check_type` values are a subset of the 4 strings above.

-- ═══════════════════════════════════════════════════════════════════════
-- agent_traces
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE agent_traces (
    id                  BIGSERIAL PRIMARY KEY,
    gen_id              UUID NOT NULL REFERENCES generations(gen_id),
    worker              VARCHAR(50) NOT NULL,
    framework           ad_framework NULL,
    input_summary       JSONB,
    output_summary      JSONB,
    model_used          VARCHAR(100),
    tokens_in           INTEGER,
    tokens_out          INTEGER,
    cost_inr            DECIMAL(10, 4),
    latency_ms          INTEGER,
    selection_reason    TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════
-- user_signals
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE user_signals (
    id                  BIGSERIAL PRIMARY KEY,
    gen_id              UUID NOT NULL REFERENCES generations(gen_id),
    user_id             UUID NOT NULL REFERENCES users(user_id),
    signal_type         VARCHAR(50) NOT NULL,
    polarity            VARCHAR(20) NOT NULL CHECK (polarity IN ('positive', 'negative', 'neutral')),
    stage               VARCHAR(50) NOT NULL,
    signal_data         JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════
-- user_style_profiles — pgvector Style Memory
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE user_style_profiles (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             UUID NOT NULL REFERENCES users(user_id),
    category            VARCHAR(50) NOT NULL,
    audience            VARCHAR(50),
    benefit             VARCHAR(50),
    emotion             VARCHAR(50),
    language            VARCHAR(20),
    motion_archetype    INTEGER,
    environment_preset  INTEGER,
    preferred_framework ad_framework,
    embedding           vector(1536),
    -- v4-Δ1: brand tier drives template routing per [TDD-BROLL]-F.2; default 'mass' keeps the
    --        90% of small-merchant brands on T1/T3/T5 unless onboarding flow explicitly upgrades.
    brand_tier          VARCHAR(10) NOT NULL CHECK (brand_tier IN ('mass','premium','luxury')) DEFAULT 'mass',
    -- v4-Δ1: brand_color_primary is sourced by Worker-COMPOSE for the text-card CTA backdrop
    --        gradient in T2/T3/T4/T5 (see [TDD-BROLL]-H and [TDD-VIDEO]-B). NULL ⇒ Worker-COMPOSE
    --        falls back to a neutral charcoal (#1A1A1A) which is legible against any product image.
    --        Format: 7-char hex including the leading '#'.
    brand_color_primary VARCHAR(7) CHECK (brand_color_primary IS NULL OR brand_color_primary ~ '^#[0-9A-Fa-f]{6}$'),
    export_count        INTEGER DEFAULT 0,
    last_used_at        TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, category)
);

-- ═══════════════════════════════════════════════════════════════════════
-- director_tips
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE director_tips (
    id                  BIGSERIAL PRIMARY KEY,
    category            VARCHAR(50) NOT NULL,
    tip_text            TEXT NOT NULL,
    tip_type            VARCHAR(20) NOT NULL CHECK (tip_type IN ('lighting', 'environment', 'motion', 'general')),
    confidence_threshold DECIMAL(3,2) DEFAULT 0.85,
    active              BOOLEAN DEFAULT TRUE
);

-- ═══════════════════════════════════════════════════════════════════════
-- grievances — IT Rules 2026 grievance pipeline
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE grievances (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             UUID NOT NULL REFERENCES users(user_id),
    gen_id              UUID REFERENCES generations(gen_id),
    type                VARCHAR(50) NOT NULL,
    description         TEXT,
    status              VARCHAR(20) DEFAULT 'open',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    resolved_at         TIMESTAMPTZ
);

-- ═══════════════════════════════════════════════════════════════════════
-- broll_clips — static B-roll library (NEW v3, role-first routing v4-Δ1)
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE broll_clips (
    clip_id             VARCHAR(20) PRIMARY KEY,
    archetype           VARCHAR(50) NOT NULL,
    category            green_zone_category NOT NULL,
    duration_ms         INTEGER NOT NULL CHECK (duration_ms BETWEEN 1000 AND 5000),
    r2_url              TEXT NOT NULL,
    excludes_faces      BOOLEAN NOT NULL DEFAULT TRUE,
    excludes_hands      BOOLEAN NOT NULL DEFAULT TRUE,
    excludes_locations  BOOLEAN NOT NULL DEFAULT TRUE,
    license_ref         VARCHAR(100),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,

    -- v4-Δ1: role-first selection metadata per [TDD-BROLL]-E. Role is the PRIMARY filter and is
    --        fixed at curation time; selection logic never overrides it (see [TDD-BROLL]-K inv. 2).
    role                VARCHAR(15) NOT NULL CHECK (role IN ('hook','context','cta_bg')),
    mood_energy         VARCHAR(10) NOT NULL CHECK (mood_energy IN ('calm','active','intense')),
    mood_temperature    VARCHAR(10) NOT NULL CHECK (mood_temperature IN ('warm','cool','neutral')),
    negative_space_score SMALLINT NOT NULL CHECK (negative_space_score BETWEEN 0 AND 10),
    seasonality_tags    TEXT[] NOT NULL DEFAULT '{}',           -- empty = year-round; e.g. {'diwali','wedding'}
    brand_tier_fit      TEXT[] NOT NULL DEFAULT '{mass,premium,luxury}',  -- tier-agnostic by default

    -- Hard invariant: faces/hands/locations all excluded (F-405 safety)
    CONSTRAINT chk_broll_safety CHECK (
        excludes_faces = TRUE
        AND excludes_hands = TRUE
        AND excludes_locations = TRUE
    ),
    -- v4-Δ1: belt-and-braces — a cta_bg clip MUST have high negative space for text legibility.
    CONSTRAINT chk_cta_negative_space CHECK (
        role <> 'cta_bg' OR negative_space_score >= 7
    )
);
CREATE INDEX idx_broll_archetype_category
    ON broll_clips (archetype, category) WHERE is_active = TRUE;
-- v4-Δ1: partial index supports the planner's hot path (role + category + tier filter).
CREATE INDEX idx_broll_role_category_tier
    ON broll_clips (role, category, brand_tier_fit) WHERE is_active = TRUE;
-- v4-Δ1: GIN index supports the T4 (seasonal) selection branch with @> / && array ops.
CREATE INDEX idx_broll_seasonality
    ON broll_clips USING GIN (seasonality_tags)
    WHERE is_active = TRUE AND cardinality(seasonality_tags) > 0;

-- ═══════════════════════════════════════════════════════════════════════
-- v4-Δ1: broll_clip_usage — per-(user, gen) rotation history; planner deprioritizes
--        clips seen in this user's last 3 generations (see [TDD-BROLL]-G step 4).
--        ON DELETE CASCADE on clip_id: history follows clip retirement (F4 resolved).
--        users(user_id) is the canonical PK target across the entire schema (F7 — corrects
--        the typo `REFERENCES users(id)` in [TDD-BROLL]-E line 4025 which would have failed
--        migration; source-doc fix pending v6).
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE broll_clip_usage (
    user_id   UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    clip_id   VARCHAR(20) NOT NULL REFERENCES broll_clips(clip_id) ON DELETE CASCADE,
    gen_id    UUID NOT NULL REFERENCES generations(gen_id) ON DELETE CASCADE,
    used_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, clip_id, gen_id)
);
CREATE INDEX idx_broll_usage_user_recent
    ON broll_clip_usage (user_id, used_at DESC);

-- ═══════════════════════════════════════════════════════════════════════
-- v4-Δ1: seasons — lookup table for T4 (Festive Moment) template override.
--        Ops/marketing toggle `is_active` to enable/disable a season without code deploy.
--        active_from <= active_to enforced; planner uses a window check at strategy time.
-- ═══════════════════════════════════════════════════════════════════════
CREATE TABLE seasons (
    season_tag    VARCHAR(30) PRIMARY KEY,
    display_name  VARCHAR(60) NOT NULL,
    active_from   DATE NOT NULL,
    active_to     DATE NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT FALSE,  -- v4-Δ1: defaults to FALSE; ops enables manually after seeding
    CONSTRAINT chk_season_window CHECK (active_from <= active_to)
);
```

---


---


## [TDD-FSM] · State Transition Trigger

**Fulfills PRD Requirement:** `[PRD-FSM]`, `[PRD-PRETOPUP]`, `[PRD-STATE-MATRIX]`, `[PRD-AC-GLOBAL]` (G3)

This trigger is the **sole enforcer** of the 22-state machine. Every UPDATE to `generations.status` passes through it. Adding a new transition requires editing both the `valid_transitions` JSONB below AND `tests/fsm/test_state_transitions_v20.py`.


FSM transitions are loaded from `/state_transitions.yaml`.

CI validation (`validate_state_machine.py`) must ensure:
- All states are covered
- No illegal transitions exist




```sql
CREATE OR REPLACE FUNCTION enforce_state_transition() RETURNS TRIGGER AS $$
DECLARE
    valid_transitions JSONB := '{
        "queued":            ["extracting", "failed_category", "failed_compliance"],
        "extracting":        ["brief_ready", "failed_category", "failed_compliance"],
        "brief_ready":       ["scripting"],
        "scripting":         ["critiquing", "failed_safety"],
        "critiquing":        ["safety_checking"],
        "safety_checking":   ["scripts_ready", "failed_safety"],
        "scripts_ready":     ["strategy_preview", "regenerating", "brief_ready"],
        "regenerating":      ["scripts_ready", "failed_safety"],
        "strategy_preview":  ["funds_locked", "awaiting_funds", "scripts_ready", "brief_ready"],
        "awaiting_funds":    ["strategy_preview", "failed_export"],
        "funds_locked":      ["rendering", "failed_render"],
        "rendering":         ["reflecting", "composing", "failed_render"],
        "reflecting":        ["composing", "rendering", "failed_render"],
        "composing":         ["preview_ready", "failed_render"],
        "preview_ready":     ["export_queued"],
        "export_queued":     ["export_ready", "failed_export"],
        "export_ready":      [],
        "failed_category":   [],
        "failed_compliance": [],
        "failed_safety":     ["scripting"],
        "failed_render":     ["strategy_preview"],
        "failed_export":     ["export_queued", "awaiting_funds"]
    }'::jsonb;
    allowed JSONB;
BEGIN
    -- Allow no-op (idempotent UPDATEs)
    IF OLD.status = NEW.status THEN
        IF OLD.pre_topup_status IS DISTINCT FROM NEW.pre_topup_status THEN
            RAISE EXCEPTION 'pre_topup_status mutated without status transition (% -> %)',
                OLD.pre_topup_status, NEW.pre_topup_status;
        END IF;
        RETURN NEW;
    END IF;

    -- Validate transition
    allowed := valid_transitions -> OLD.status::text;
    IF allowed IS NULL OR NOT allowed ? NEW.status::text THEN
        RAISE EXCEPTION 'Invalid state transition: % -> %', OLD.status, NEW.status;
    END IF;

    -- pre_topup_status paired-write invariants
    -- Rule 1: any transition INTO awaiting_funds requires NEW.pre_topup_status set correctly.
    IF NEW.status = 'awaiting_funds' THEN
        IF OLD.status = 'strategy_preview' AND NEW.pre_topup_status IS DISTINCT FROM 'strategy_preview' THEN
            RAISE EXCEPTION 'strategy_preview -> awaiting_funds requires pre_topup_status=strategy_preview (got %)',
                NEW.pre_topup_status;
        END IF;
        IF OLD.status = 'failed_export' AND NEW.pre_topup_status IS DISTINCT FROM 'failed_export' THEN
            RAISE EXCEPTION 'failed_export -> awaiting_funds requires pre_topup_status=failed_export (got %)',
                NEW.pre_topup_status;
        END IF;
    END IF;

    -- Rule 2: any transition OUT of awaiting_funds must clear pre_topup_status AND restore to snapshot.
    IF OLD.status = 'awaiting_funds' THEN
        IF NEW.pre_topup_status IS NOT NULL THEN
            RAISE EXCEPTION 'Transition out of awaiting_funds must clear pre_topup_status (got %)',
                NEW.pre_topup_status;
        END IF;
        IF OLD.pre_topup_status = 'strategy_preview' AND NEW.status <> 'strategy_preview' THEN
            RAISE EXCEPTION 'awaiting_funds(pre=strategy_preview) must restore to strategy_preview (got %)', NEW.status;
        END IF;
        IF OLD.pre_topup_status = 'failed_export' AND NEW.status <> 'failed_export' THEN
            RAISE EXCEPTION 'awaiting_funds(pre=failed_export) must restore to failed_export (got %)', NEW.status;
        END IF;
    END IF;

    -- Rule 3: any other transition must have NEW.pre_topup_status NULL.
    IF NEW.status <> 'awaiting_funds' AND NEW.pre_topup_status IS NOT NULL THEN
        RAISE EXCEPTION 'pre_topup_status must be NULL when status<>awaiting_funds (got status=%, pre_topup_status=%)',
            NEW.status, NEW.pre_topup_status;
    END IF;

    NEW.updated_at := NOW();

    -- Capture status history with pre_topup_status snapshots for forensics
    INSERT INTO status_history (gen_id, from_status, to_status, from_pre_topup_status, to_pre_topup_status)
    VALUES (NEW.gen_id, OLD.status, NEW.status, OLD.pre_topup_status, NEW.pre_topup_status);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_enforce_state_transition
    BEFORE UPDATE OF status, pre_topup_status ON generations
    FOR EACH ROW EXECUTE FUNCTION enforce_state_transition();

-- Monotonicity guard on export_retry_count
CREATE OR REPLACE FUNCTION enforce_export_retry_monotonic() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.export_retry_count < OLD.export_retry_count THEN
        RAISE EXCEPTION 'export_retry_count cannot decrease (% -> %)',
            OLD.export_retry_count, NEW.export_retry_count;
    END IF;
    IF NEW.export_retry_count > OLD.export_retry_count + 1 THEN
        RAISE EXCEPTION 'export_retry_count must increment by exactly 1 (% -> %)',
            OLD.export_retry_count, NEW.export_retry_count;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_export_retry_monotonic
    BEFORE UPDATE OF export_retry_count ON generations
    FOR EACH ROW EXECUTE FUNCTION enforce_export_retry_monotonic();
```

---


### [TDD-FSM]-SCREEN-CONTRACT · Screen Routing Contract *(Category 3A — APPENDED)*

`state_transitions.yaml` is extended to own the full screen routing contract. The frontend has zero state-to-screen logic. It reads the descriptor and renders.

**Four new fields added to every state entry in `state_transitions.yaml`:**

```yaml
# Added to every state definition:
screen: "HD-1"          # HD-1..HD-6, or "derived" for awaiting_funds
type: "transient"       # transient | resident | terminal
ui_mode: "processing"   # processing | ready | blocked | error
allowed_actions: []     # list of action strings; empty for transient states
```

**Field semantics:**

| Field             | Domain                                         | Meaning                                                                   |
| ----------------- | ---------------------------------------------- | ------------------------------------------------------------------------- |
| `screen`          | `HD-1`..`HD-6` \| `derived`                    | Which of the six screens renders this state.                              |
| `type`            | `transient` \| `resident` \| `terminal`        | Whether the user can act (`resident`), the system is working (`transient`), or the generation is done (`terminal`). |
| `ui_mode`         | `processing` \| `ready` \| `blocked` \| `error`| Visual mode for the screen shell. Drives spinner / CTA / banner styling.  |
| `allowed_actions` | `string[]`                                     | Action names the frontend is permitted to render buttons for. Empty for transient states. |

**`derived` resolution rule:**

The `awaiting_funds` state uses `screen: derived`. Backend serializer reads `pre_topup_status` to resolve:
- `pre_topup_status = 'strategy_preview'` → `screen: HD-4`
- `pre_topup_status = 'failed_export'`    → `screen: HD-6`

These are the only two legal `pre_topup_status` values per the `chk_pre_topup_coupling` constraint in `[TDD-MIGRATIONS]`.

**Backend serializer contract:**

`models/generation_view.py` reads `state_transitions.yaml` once at process startup (cached in module global). On every `GET /api/generations/{gen_id}` response, the serializer computes a `screen_descriptor` block and includes it in the response:

```json
{
  "screen": "HD-4",
  "type": "resident",
  "ui_mode": "ready",
  "allowed_actions": ["approve_strategy", "edit_back"]
}
```

The serializer is the only code path that resolves the `derived` screen value. No worker, no LLM prompt, no frontend file resolves it.

**Frontend contract:**

The frontend imports the `screen_descriptor` and renders. No state-to-screen mapping exists in frontend code. Adding a new FSM state requires editing one file (`state_transitions.yaml`) and nothing else.

**CI enforcement (extends `ci/validate_state_machine.py`):**

The CI script must fail the build if any of the following hold:
1. Any state in `state_transitions.yaml` is missing one of: `screen`, `type`, `ui_mode`, `allowed_actions`.
2. A `screen` value is outside `{HD-1, HD-2, HD-3, HD-4, HD-5, HD-6, derived}`.
3. A `type` value is outside `{transient, resident, terminal}`.
4. A `ui_mode` value is outside `{processing, ready, blocked, error}`.
5. `allowed_actions` is non-empty for any state where `type=transient`.
6. Any file under `/app` imports or defines a state-to-screen constants map (grep for forbidden patterns: `STATE_TO_SCREEN`, `stateScreenMap`, `screenForState`).

---


## [TDD-TYPES] · TypeScript Interfaces & Pydantic Models

**Fulfills PRD Requirement:** `[PRD-FSM]`, `[PRD-PRETOPUP]`, `[PRD-FEATURES-CREATIVE]`, `[PRD-FEATURES-INTENT]`, `[PRD-FEATURES-PAYMENT]`, `[PRD-FEATURES-PRODUCTION]`, `[PRD-IDEMPOTENCY]`, `[PRD-AGENTIC-DRAFT]`

The type surface is split into two symmetric layers: the **TypeScript layer** (frontend) is the client-side mirror of the canonical hydration payload returned by `GET /api/generations/{gen_id}`; the **Pydantic layer** (FastAPI) is the server-side request-validation layer enforcing PRD invariants at the HTTP boundary.

### [TDD-TYPES]-A · TypeScript Interfaces (frontend)

```typescript
export type ConfidenceLevel = "high" | "medium" | "low";
export function getConfidenceLevel(score: number): ConfidenceLevel {
  if (score >= 0.90) return "high";
  if (score >= 0.85) return "medium";
  return "low";
}

export interface Script {
  hook: string;
  body: string;
  cta: string;
  full_text: string;
  word_count: number;
  language_mix: 'pure_hindi' | 'hinglish' | 'pure_english';
  framework: AdFramework;
  framework_angle: FrameworkAngle;
  framework_rationale: string;
  evidence_note: string;
  suggested_tone: string;
  critic_score?: number;
  critic_rationale?: string;
}

export interface FrameworkRoutingResult {
  selected: [AdFramework, AdFramework, AdFramework];
  default_trio_satisfied: boolean;
  fallback_triggered: boolean;
  routing_rationale: Record<AdFramework, string>;
}

export interface ChatMessage { role: "user" | "assistant"; content: string; timestamp: string; }
export interface ChatRequest { message: string; }
export interface ChatResponse {
  refined_script: Script;
  turns_used: number;
  turns_remaining: number;
  cost_inr: number;
}

export interface BRollClip {
  clip_id: string;
  archetype: string;
  duration_ms: number;
  r2_url: string;
  // v4-Δ1: role-first selection metadata per [TDD-BROLL]-E
  role: 'hook' | 'context' | 'cta_bg';
  mood_energy: 'calm' | 'active' | 'intense';
  mood_temperature: 'warm' | 'cool' | 'neutral';
  negative_space_score: number;            // 0-10; cta_bg clips MUST be >= 7
  seasonality_tags: string[];              // empty array = year-round
  brand_tier_fit: ('mass' | 'premium' | 'luxury')[];
}

// v4-Δ1: structured plan replacing the flat list per [TDD-BROLL]-G.
// `context` and `cta` are independently nullable; `cta: null` ⇒ Worker-COMPOSE
// renders a text-card backdrop instead of a clip (T2/T3/T4/T5).
export interface BRollPlan {
  template: 'T1' | 'T2' | 'T3' | 'T4' | 'T5';
  hook: BRollClip;                          // always present — every template guarantees a hook
  context: BRollClip | null;                // T3 and T4 only
  cta: BRollClip | null;                    // T1 only; null ⇒ text-card path
}

export interface StrategyCardV3 {
  product_summary: any;
  script_summary: any;
  voice: any;
  motion: any;
  environment: any;
  provider: any;
  cost_estimate: any;
  compliance: any;
  chat_turns_used: number;
  chat_cost_inr: number;
  // v4-Δ1: BRollPlan replaces BRollClip[]; null until strategist runs
  b_roll_plan: BRollPlan | null;
  structure_template: 'T1' | 'T2' | 'T3' | 'T4' | 'T5' | null;
  active_season: string | null;
  b_roll_available: boolean;                // true iff b_roll_plan !== null && b_roll_plan.hook != null
}

export interface DLQEvent {
  gen_id: string;
  failed_task: string;
  failed_at: string;
  recovery_action: 'retry_full' | 'retry_export' | 'refund_only' | 'abandon';
}

export interface RetryExportRequest {
  declarations?: [boolean, boolean, boolean];
}

export type JobStatus =
  | "queued" | "extracting" | "brief_ready"
  | "scripting" | "critiquing" | "safety_checking" | "scripts_ready" | "regenerating"
  | "strategy_preview" | "awaiting_funds" | "funds_locked"
  | "rendering" | "reflecting" | "composing"
  | "preview_ready" | "export_queued" | "export_ready"
  | "failed_category" | "failed_compliance" | "failed_safety"
  | "failed_render" | "failed_export";

export type PreTopupStatus = "strategy_preview" | "failed_export" | null;

export interface GenerationState {
  gen_id: string;
  status: JobStatus;
  pre_topup_status: PreTopupStatus;
  routed_frameworks?: AdFramework[];
  raw_scripts?: Script[];
  selected_script_id?: number;
  refined_script?: Script;
  chat_turns_used: number;
  export_retry_count: number;
  preview_url?: string;
  exports?: { square_url?: string; vertical_url?: string; c2pa_manifest_hash?: string; finalized_at?: string };
}
```

### [TDD-TYPES]-B · Pydantic Models (backend)

```python
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    message: Optional[str] = Field(default=None, min_length=1, max_length=500)
    action: Optional[Literal[
        "chip_punchier", "chip_hinglish", "chip_diwali"
    ]] = None

    @model_validator(mode='after')
    def validate_exactly_one_field(self) -> 'ChatRequest':
        has_message = self.message is not None
        has_action  = self.action  is not None
        if has_message == has_action:  # both or neither
            raise ValueError(
                "Exactly one of 'message' or 'action' must be provided."
            )
        return self

    @field_validator('message', mode='before')
    @classmethod
    def validate_word_count(cls, v):
        if v is not None and len(str(v).split()) > 20:
            raise ValueError("Chat message must be ≤ 20 words")
        return v

class ChatResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    refined_script: dict
    turns_used: int
    turns_remaining: int
    cost_inr: float

class EditBackRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    target_state: Literal["brief_ready", "scripts_ready"]
    target_field: Literal["product", "targeting", "script", "style"]

class ApproveStrategyRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    approved: bool = True

class SelectionsRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    audience: str
    benefit: str
    emotion: str
    language: str

class IdempotencyMeta(BaseModel):
    status_code: int
    body: dict
    created_at: str

class DeclarationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    declaration_accepted: bool = True
    confirms_commercial_use: bool
    confirms_image_rights: bool
    confirms_ai_disclosure: bool

    @field_validator('confirms_commercial_use', 'confirms_image_rights', 'confirms_ai_disclosure')
    @classmethod
    def must_be_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError("All three declarations must be checked")
        return v

class RetryExportRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    declarations: Optional[list[bool]] = None

    @field_validator('declarations')
    @classmethod
    def validate_declarations(cls, v: Optional[list[bool]]) -> Optional[list[bool]]:
        if v is None:
            return v
        if len(v) != 3 or not all(v):
            raise ValueError("declarations must be [True, True, True] when present")
        return v

class FrameworkRoutingOutput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    selected: list[str] = Field(min_length=3, max_length=3)
    rationale: dict[str, str]
    fallback_triggered: bool = False

    @field_validator('selected')
    @classmethod
    def must_be_distinct(cls, v: list[str]) -> list[str]:
        if len(set(v)) != 3:
            raise ValueError("Must select 3 distinct frameworks")
        return v

class RazorpayWebhookPayload(BaseModel):
    event: Literal["payment.captured", "payment.failed"]
    payload: dict


# v3 / v4-Δ1: B-roll planner output (deterministic, static-library backed; role-first selection)
class BRollClip(BaseModel):
    model_config = ConfigDict(extra='forbid')
    clip_id: str
    archetype: str
    duration_ms: int
    r2_url: str
    # v4-Δ1: role-first selection metadata per [TDD-BROLL]-E
    role: Literal['hook', 'context', 'cta_bg']
    mood_energy: Literal['calm', 'active', 'intense']
    mood_temperature: Literal['warm', 'cool', 'neutral']
    negative_space_score: int = Field(ge=0, le=10)
    seasonality_tags: list[str] = Field(default_factory=list)
    brand_tier_fit: list[Literal['mass', 'premium', 'luxury']] = Field(
        default_factory=lambda: ['mass', 'premium', 'luxury']
    )


# v4-Δ1: structured plan replacing flat list per [TDD-BROLL]-G.
# `context` and `cta` are independently nullable; `cta is None` ⇒ Worker-COMPOSE renders a text-card.
class BRollPlan(BaseModel):
    model_config = ConfigDict(extra='forbid')
    template: Literal['T1', 'T2', 'T3', 'T4', 'T5']
    hook: BRollClip                                 # always present
    context: BRollClip | None = None                # T3, T4 only
    cta: BRollClip | None = None                    # T1 only; None ⇒ text-card path


# v3 / v4-Δ1: HD-4 Strategy Card Data Packet (F-405 Integrated)
class StrategyCardOutput(BaseModel):
    """Server-side projection of [TDD-WORKERS]-G strategist output.
    Strict — extra='forbid' so leaked UI fields fail validation."""
    model_config = ConfigDict(extra='forbid')

    gen_id: str
    status: str
    selected_framework: str
    full_text: str
    rationale: str
    motion_archetype: int
    environment_preset: int

    # v4-Δ1: F-405 — structured plan instead of flat list. Null until strategist runs.
    b_roll_plan: BRollPlan | None = None
    structure_template: Literal['T1', 'T2', 'T3', 'T4', 'T5'] | None = None
    active_season: str | None = None

    is_refined: bool = False
```

---


---


## [TDD-MIGRATIONS] · Data Migrations (v19 → v20 → v3 schema)

**Fulfills PRD Requirement:** `[PRD-FSM]`, `[PRD-PRETOPUP]`, `[PRD-STATE-MATRIX]`, `[PRD-PAYMENT-FSM]`, `[PRD-FEATURES-PAYMENT]`, `[PRD-NON-NEGOTIABLES]`

This is the atomic schema-migration script. It is **append-only** (see `[TDD-MIGRATION-SAFETY]`): no column drops, no destructive type narrows.

```sql
-- ============================================================
-- v19 → v3 schema migration
-- ============================================================

BEGIN;

-- (1) Rename job_status column to status for clarity
ALTER TABLE generations RENAME COLUMN job_status TO status;

-- (2) Add pre_topup_status column
ALTER TABLE generations
    ADD COLUMN pre_topup_status job_status NULL;

-- (3) Add export_retry_count
ALTER TABLE generations
    ADD COLUMN export_retry_count INTEGER NOT NULL DEFAULT 0;

ALTER TABLE generations
    ADD CONSTRAINT chk_export_retry_count_bounds CHECK (export_retry_count BETWEEN 0 AND 3);

-- (4) Add framework routing columns
CREATE TYPE ad_framework AS ENUM (
    'pas_micro', 'clinical_flex', 'myth_buster',
    'asmr_trigger', 'usage_ritual', 'hyper_local_comfort',
    'spec_drop_flex', 'premium_upgrade', 'roi_durability_flex',
    'festival_occasion_hook', 'scarcity_drop', 'social_proof'
);

ALTER TABLE generations
    ADD COLUMN routed_frameworks ad_framework[],
    ADD COLUMN routing_rationale JSONB;

-- (5) v3 / v4-Δ1: B-roll plan column (replaces v2's b_roll_selections)
--     v4-Δ1: shape changed from JSONB array to JSONB object {template, hook, context, cta} per
--            [TDD-BROLL]-G. DEFAULT '[]' is incompatible with the new object CHECK; the column
--            is created with DEFAULT NULL and the old constraint is dropped + replaced after
--            the existing-row backfill (see step 22 below).
ALTER TABLE generations
    ADD COLUMN IF NOT EXISTS b_roll_plan JSONB DEFAULT NULL;

-- (6) pre_topup_status invariant
ALTER TABLE generations ADD CONSTRAINT chk_pre_topup_coupling CHECK (
    (status = 'awaiting_funds' AND pre_topup_status IN ('strategy_preview','failed_export'))
    OR
    (status <> 'awaiting_funds' AND pre_topup_status IS NULL)
);

-- (7) routed_frameworks cardinality
ALTER TABLE generations ADD CONSTRAINT chk_routed_frameworks_cardinality CHECK (
    routed_frameworks IS NULL
    OR (array_length(routed_frameworks, 1) = 3
        AND array_length(routed_frameworks, 1) = (SELECT COUNT(DISTINCT v) FROM unnest(routed_frameworks) v))
);

-- (8) v3: explicit JSONB shape constraints
ALTER TABLE generations ADD CONSTRAINT chk_product_brief_shape CHECK (
    product_brief IS NULL OR (
        jsonb_typeof(product_brief) = 'object'
        AND product_brief ? 'product_name'
        AND product_brief ? 'category'
        AND product_brief ? 'key_features'
        AND jsonb_typeof(product_brief->'key_features') = 'array'
    )
);
ALTER TABLE generations ADD CONSTRAINT chk_exports_shape CHECK (
    exports IS NULL OR (
        jsonb_typeof(exports) = 'object'
        AND exports ? 'square_url'
        AND exports ? 'vertical_url'
        AND exports ? 'c2pa_manifest_hash'
        AND exports ? 'finalized_at'
    )
);
ALTER TABLE generations ADD CONSTRAINT chk_strategy_card_shape CHECK (
    strategy_card IS NULL OR (
        jsonb_typeof(strategy_card) = 'object'
        AND strategy_card ? 'product_summary'
        AND strategy_card ? 'script_summary'
        AND strategy_card ? 'voice'
        AND strategy_card ? 'motion'
        AND strategy_card ? 'environment'
        AND strategy_card ? 'compliance'
    )
);
-- v4-Δ1: drop the old array-shape constraint; backfill array-shaped rows to NULL; then apply
--        the new object-shape constraint. The backfill must run BEFORE the new CHECK is added
--        or every legacy '[]' row will violate it on commit.
ALTER TABLE generations DROP CONSTRAINT IF EXISTS chk_b_roll_plan_shape;

UPDATE generations
   SET b_roll_plan = NULL
 WHERE b_roll_plan IS NOT NULL
   AND jsonb_typeof(b_roll_plan) <> 'object';

ALTER TABLE generations ADD CONSTRAINT chk_b_roll_plan_shape CHECK (
    b_roll_plan IS NULL
    OR (
        jsonb_typeof(b_roll_plan) = 'object'
        AND b_roll_plan ? 'template'
        AND b_roll_plan ? 'hook'
        AND (b_roll_plan->>'template') IN ('T1','T2','T3','T4','T5')
    )
);

-- (9) wallet_status enum (separate from payment_status)
CREATE TYPE wallet_status AS ENUM ('locked', 'consumed', 'refunded');

ALTER TABLE wallet_transactions
    ADD COLUMN status wallet_status NULL;

UPDATE wallet_transactions
SET status = CASE
    WHEN type = 'lock' THEN 'locked'::wallet_status
    WHEN type = 'consume' THEN 'consumed'::wallet_status
    WHEN type = 'refund' THEN 'refunded'::wallet_status
END,
payment_status = NULL
WHERE type IN ('lock','consume','refund');

ALTER TABLE wallet_transactions ADD CONSTRAINT chk_wallet_status_coupling CHECK (
    (type = 'topup' AND status IS NULL AND payment_status IS NOT NULL)
    OR
    (type IN ('lock','consume','refund') AND payment_status IS NULL AND status IS NOT NULL)
    OR
    (type = 'expire' AND payment_status IS NULL AND status IS NULL)
);

-- (10) Partial UNIQUE INDEX: single active lock per gen
CREATE UNIQUE INDEX ux_wallet_active_lock
    ON wallet_transactions (gen_id)
    WHERE status = 'locked';

-- (11) UNIQUE INDEX: single refund per gen
CREATE UNIQUE INDEX ux_wallet_refund_dedup
    ON wallet_transactions (gen_id, type)
    WHERE type = 'refund';

-- (12) status_history pre_topup_status capture columns
ALTER TABLE status_history
    ADD COLUMN from_pre_topup_status job_status,
    ADD COLUMN to_pre_topup_status job_status;

-- (13) audit_log declaration_sha256 explicit column
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS declaration_sha256 VARCHAR(64);
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS user_agent TEXT;

-- (14) agent_traces framework column
ALTER TABLE agent_traces ADD COLUMN IF NOT EXISTS framework ad_framework NULL;

-- (15) user_style_profiles preferred_framework column
ALTER TABLE user_style_profiles ADD COLUMN IF NOT EXISTS preferred_framework ad_framework;

-- (16) v3 / v4-Δ1: broll_clips static library
--      v4-Δ1: 6 new columns + chk_cta_negative_space + 2 new indices for role-first selection.
CREATE TABLE IF NOT EXISTS broll_clips (
    clip_id             VARCHAR(20) PRIMARY KEY,
    archetype           VARCHAR(50) NOT NULL,
    category            green_zone_category NOT NULL,
    duration_ms         INTEGER NOT NULL CHECK (duration_ms BETWEEN 1000 AND 5000),
    r2_url              TEXT NOT NULL,
    excludes_faces      BOOLEAN NOT NULL DEFAULT TRUE,
    excludes_hands      BOOLEAN NOT NULL DEFAULT TRUE,
    excludes_locations  BOOLEAN NOT NULL DEFAULT TRUE,
    license_ref         VARCHAR(100),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_broll_safety CHECK (
        excludes_faces = TRUE
        AND excludes_hands = TRUE
        AND excludes_locations = TRUE
    )
);
-- v4-Δ1: idempotent column additions for clusters that already have broll_clips from v3 seed.
ALTER TABLE broll_clips ADD COLUMN IF NOT EXISTS role VARCHAR(15);
ALTER TABLE broll_clips ADD COLUMN IF NOT EXISTS mood_energy VARCHAR(10);
ALTER TABLE broll_clips ADD COLUMN IF NOT EXISTS mood_temperature VARCHAR(10);
ALTER TABLE broll_clips ADD COLUMN IF NOT EXISTS negative_space_score SMALLINT;
ALTER TABLE broll_clips ADD COLUMN IF NOT EXISTS seasonality_tags TEXT[] NOT NULL DEFAULT '{}';
ALTER TABLE broll_clips ADD COLUMN IF NOT EXISTS brand_tier_fit TEXT[] NOT NULL DEFAULT '{mass,premium,luxury}';
-- v4-Δ1: backfill role for any v3-seeded rows (operator MUST review before re-deploy;
--        defaulting to 'context' is the safest holding role — never picks for hook/cta until
--        curator re-tags).
UPDATE broll_clips SET role = 'context' WHERE role IS NULL;
UPDATE broll_clips SET mood_energy = 'calm' WHERE mood_energy IS NULL;
UPDATE broll_clips SET mood_temperature = 'neutral' WHERE mood_temperature IS NULL;
UPDATE broll_clips SET negative_space_score = 5 WHERE negative_space_score IS NULL;
-- Now enforce NOT NULL + CHECK after backfill is guaranteed clean.
ALTER TABLE broll_clips ALTER COLUMN role SET NOT NULL;
ALTER TABLE broll_clips ALTER COLUMN mood_energy SET NOT NULL;
ALTER TABLE broll_clips ALTER COLUMN mood_temperature SET NOT NULL;
ALTER TABLE broll_clips ALTER COLUMN negative_space_score SET NOT NULL;
ALTER TABLE broll_clips DROP CONSTRAINT IF EXISTS chk_broll_role;
ALTER TABLE broll_clips ADD CONSTRAINT chk_broll_role CHECK (role IN ('hook','context','cta_bg'));
ALTER TABLE broll_clips DROP CONSTRAINT IF EXISTS chk_broll_mood_energy;
ALTER TABLE broll_clips ADD CONSTRAINT chk_broll_mood_energy CHECK (mood_energy IN ('calm','active','intense'));
ALTER TABLE broll_clips DROP CONSTRAINT IF EXISTS chk_broll_mood_temperature;
ALTER TABLE broll_clips ADD CONSTRAINT chk_broll_mood_temperature CHECK (mood_temperature IN ('warm','cool','neutral'));
ALTER TABLE broll_clips DROP CONSTRAINT IF EXISTS chk_broll_negative_space;
ALTER TABLE broll_clips ADD CONSTRAINT chk_broll_negative_space CHECK (negative_space_score BETWEEN 0 AND 10);
ALTER TABLE broll_clips DROP CONSTRAINT IF EXISTS chk_cta_negative_space;
ALTER TABLE broll_clips ADD CONSTRAINT chk_cta_negative_space CHECK (role <> 'cta_bg' OR negative_space_score >= 7);

CREATE INDEX IF NOT EXISTS idx_broll_archetype_category
    ON broll_clips (archetype, category) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_broll_role_category_tier
    ON broll_clips (role, category, brand_tier_fit) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_broll_seasonality
    ON broll_clips USING GIN (seasonality_tags)
    WHERE is_active = TRUE AND cardinality(seasonality_tags) > 0;

-- (17) Re-create state-transition trigger with v3 semantics
DROP TRIGGER IF EXISTS trg_enforce_state_transition ON generations;
DROP FUNCTION IF EXISTS enforce_state_transition();
-- (Re-create per [TDD-FSM].)

-- (18) export_retry monotonicity trigger (per [TDD-FSM])

-- (19) Pre-create next 3 months of audit_log partitions
DO $$
DECLARE
    m INTEGER;
    next_month DATE;
    month_after DATE;
    partition_name TEXT;
BEGIN
    FOR m IN 0..2 LOOP
        next_month := date_trunc('month', NOW()) + (m * INTERVAL '1 month');
        month_after := next_month + INTERVAL '1 month';
        partition_name := 'audit_log_' || to_char(next_month, 'YYYY_MM');
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF audit_log FOR VALUES FROM (%L) TO (%L)',
            partition_name, next_month, month_after
        );
        EXECUTE format('REVOKE UPDATE, DELETE ON %I FROM PUBLIC', partition_name);
    END LOOP;
END $$;

-- (20) feature_flags table — toggle mechanism for [TDD-ERROR-RECOVERY]-D Tier-1..4 degradation modes
CREATE TABLE IF NOT EXISTS feature_flags (
    key         TEXT PRIMARY KEY,
    value       JSONB NOT NULL,
    description TEXT,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed the 4 degradation tier flags (all default OFF; founder toggles via psql)
INSERT INTO feature_flags (key, value, description) VALUES
    ('tier1_degradation_enabled', 'false'::jsonb, 'Tier 1: pgvector heuristic fallback'),
    ('tier2_degradation_enabled', 'false'::jsonb, 'Tier 2: B-roll library coverage gap — force T1/text-card-CTA fallback (planner skips role lookups; Worker-COMPOSE uses neutral text-card) per [TDD-BROLL]-I'),
    ('tier3_degradation_enabled', 'false'::jsonb, 'Tier 3: Style Memory disabled'),
    ('tier4_degradation_enabled', 'false'::jsonb, 'Tier 4: Reflect step disabled')
ON CONFLICT (key) DO NOTHING;

-- (21) users.beta_invited — cohort allocation gate for [PRD-RELEASE-BETA] B1
ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS beta_invited BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_users_beta_invited 
    ON users (beta_invited) 
    WHERE beta_invited = TRUE;

-- (22) v4-Δ1: broll_clip_usage — per-(user, clip, gen) rotation history.
--      CASCADE on all FKs because history is meaningful only while the parent rows exist.
--      The FK target users(user_id) is the canonical PK (corrects the typo in [TDD-BROLL]-E
--      line 4025 which referenced users(id); F7 in CONSISTENCY FLAGS).
CREATE TABLE IF NOT EXISTS broll_clip_usage (
    user_id   UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    clip_id   VARCHAR(20) NOT NULL REFERENCES broll_clips(clip_id) ON DELETE CASCADE,
    gen_id    UUID NOT NULL REFERENCES generations(gen_id) ON DELETE CASCADE,
    used_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, clip_id, gen_id)
);
CREATE INDEX IF NOT EXISTS idx_broll_usage_user_recent
    ON broll_clip_usage (user_id, used_at DESC);

-- (23) v4-Δ1: seasons — lookup table for T4 (Festive Moment) template.
--      Seeded with is_active = FALSE; ops enables the row manually via psql/admin once the
--      curated festive clip set lands. No code deploy needed to switch a season on or off.
CREATE TABLE IF NOT EXISTS seasons (
    season_tag    VARCHAR(30) PRIMARY KEY,
    display_name  VARCHAR(60) NOT NULL,
    active_from   DATE NOT NULL,
    active_to     DATE NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_season_window CHECK (active_from <= active_to)
);

-- v4-Δ1: seed the six v1 Indian-market seasons. Ranges are placeholders set well-inside
-- 2026 calendar bounds; ops adjusts active_from / active_to and flips is_active=TRUE
-- when the curated clip set is ready.
INSERT INTO seasons (season_tag, display_name, active_from, active_to, is_active) VALUES
    ('diwali',          'Diwali',          DATE '2026-10-25', DATE '2026-11-15', FALSE),
    ('holi',            'Holi',            DATE '2026-03-01', DATE '2026-03-20', FALSE),
    ('wedding_season',  'Wedding Season',  DATE '2026-10-01', DATE '2027-02-15', FALSE),
    ('monsoon',         'Monsoon',         DATE '2026-06-15', DATE '2026-09-30', FALSE),
    ('new_year',        'New Year',        DATE '2026-12-20', DATE '2027-01-10', FALSE),
    ('raksha_bandhan',  'Raksha Bandhan',  DATE '2026-08-01', DATE '2026-08-20', FALSE)
ON CONFLICT (season_tag) DO NOTHING;

-- (24) v4-Δ1: generations gains structure_template + active_season + reserved performance slot.
--      structure_template is the persisted output of [TDD-BROLL]-G step 2; Worker-COMPOSE reads
--      it as the primary branch key. active_season is set only when T4 was chosen.
ALTER TABLE generations
    ADD COLUMN IF NOT EXISTS structure_template VARCHAR(5);
ALTER TABLE generations DROP CONSTRAINT IF EXISTS chk_structure_template;
ALTER TABLE generations ADD CONSTRAINT chk_structure_template
    CHECK (structure_template IS NULL OR structure_template IN ('T1','T2','T3','T4','T5'));
ALTER TABLE generations
    ADD COLUMN IF NOT EXISTS active_season VARCHAR(30) REFERENCES seasons(season_tag);
ALTER TABLE generations
    ADD COLUMN IF NOT EXISTS b_roll_performance_signal JSONB;  -- reserved for v2 attribution loop

-- (25) v4-Δ1: user_style_profiles gains brand_tier (template routing) + brand_color_primary
--      (Worker-COMPOSE text-card backdrop). Default 'mass' keeps existing rows tier-stable.
--      brand_color_primary is NULL by default — Worker-COMPOSE falls back to #1A1A1A.
ALTER TABLE user_style_profiles
    ADD COLUMN IF NOT EXISTS brand_tier VARCHAR(10) NOT NULL DEFAULT 'mass';
ALTER TABLE user_style_profiles DROP CONSTRAINT IF EXISTS chk_user_style_brand_tier;
ALTER TABLE user_style_profiles ADD CONSTRAINT chk_user_style_brand_tier
    CHECK (brand_tier IN ('mass','premium','luxury'));
ALTER TABLE user_style_profiles
    ADD COLUMN IF NOT EXISTS brand_color_primary VARCHAR(7);
ALTER TABLE user_style_profiles DROP CONSTRAINT IF EXISTS chk_user_style_brand_color_hex;
ALTER TABLE user_style_profiles ADD CONSTRAINT chk_user_style_brand_color_hex
    CHECK (brand_color_primary IS NULL OR brand_color_primary ~ '^#[0-9A-Fa-f]{6}$');

-- (26) v4-Δ1: forward-compat — structure_template feature flag (default FALSE so legacy code
--      paths still work during the rollout window). Worker-STRATEGIST consults this; when
--      FALSE it short-circuits to T1 + null context/cta so behavior matches v4 exactly.
INSERT INTO feature_flags (key, value, description) VALUES
    ('broll_v4_routing_enabled', 'false'::jsonb,
     'v4-Δ1: enables 5-template router in Worker-STRATEGIST. FALSE = legacy T1-only mode for safe rollout.')
ON CONFLICT (key) DO NOTHING;


COMMIT;
```

---


> **[CONSISTENCY-FLAG: Webhook idempotency migration]** `[TDD-CONCURRENCY]-F` (Category 3B) introduces a new `processed_webhooks` table. v3's `[TDD-MIGRATIONS]` does not include this table. A migration entry must be added during the human merge pass. See `CONSISTENCY FLAGS` at end of document.

---


## [TDD-INDICES] · Required Database Indices (Consolidated)

**Fulfills PRD Requirement:** `[PRD-FEATURES-INFRA]`, `[PRD-FEATURES-RETENTION]`, `[PRD-FEATURES-PAYMENT]`, `[PRD-IDEMPOTENCY]`, `[PRD-ERROR-MATRIX]`

```sql
-- (a) Webhook restoration: UPDATE generations WHERE user_id=? AND status='awaiting_funds'
CREATE INDEX idx_generations_user_awaiting_funds
    ON generations (user_id)
    WHERE status = 'awaiting_funds';

-- (b) Declaration freshness lookup (used by /retry-export Step 4)
CREATE INDEX idx_audit_log_gen_action_created
    ON audit_log (gen_id, action, created_at DESC);

-- (c) Wallet refund lookup
CREATE INDEX idx_wallet_txn_gen_type
    ON wallet_transactions (gen_id, type);

-- (d) Status history scans by gen_id
CREATE INDEX idx_status_history_gen_created
    ON status_history (gen_id, created_at DESC);

-- (e) Active generations per user
CREATE INDEX idx_generations_user_status
    ON generations (user_id, status, created_at DESC);

-- (f) Retention sweep candidates (Starter)
CREATE INDEX idx_generations_starter_retention
    ON generations (created_at)
    WHERE plan_tier = 'starter'
      AND (source_image_url IS NOT NULL OR isolated_png_url IS NOT NULL OR preview_url IS NOT NULL);

-- (g) Retention sweep candidates (Paid)
CREATE INDEX idx_generations_paid_retention
    ON generations (created_at)
    WHERE plan_tier IN ('essential', 'pro')
      AND (source_image_url IS NOT NULL OR isolated_png_url IS NOT NULL OR preview_url IS NOT NULL);

-- (h) 5-year export purge candidates
CREATE INDEX idx_generations_export_ready_finalized
    ON generations ((COALESCE((exports->>'finalized_at')::timestamptz, updated_at)))
    WHERE status = 'export_ready' AND exports IS NOT NULL;

-- (i) DLQ dead jobs
CREATE INDEX idx_generations_dlq
    ON generations (dlq_dead_at DESC)
    WHERE dlq_dead_at IS NOT NULL;

-- (j) Style Memory pgvector ANN
CREATE INDEX idx_user_style_profiles_embedding
    ON user_style_profiles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- (k) Compliance log lookups
CREATE INDEX idx_compliance_log_gen_check
    ON compliance_log (gen_id, check_type, created_at DESC);

-- (l) Agent traces by gen + framework
CREATE INDEX idx_agent_traces_gen_framework
    ON agent_traces (gen_id, framework, created_at DESC);

-- v4-Δ1: B-roll planner hot-path and rotation indices (mirror of [TDD-SCHEMA]).
-- (m) Planner's primary filter: (role, category, brand_tier_fit). Partial on is_active.
CREATE INDEX idx_broll_role_category_tier
    ON broll_clips (role, category, brand_tier_fit) WHERE is_active = TRUE;

-- (n) T4 seasonal selection (array containment / overlap operators). GIN, partial.
CREATE INDEX idx_broll_seasonality
    ON broll_clips USING GIN (seasonality_tags)
    WHERE is_active = TRUE AND cardinality(seasonality_tags) > 0;

-- (o) Rotation deprioritization: "clips this user used in last N gens". Sorted by used_at DESC.
CREATE INDEX idx_broll_usage_user_recent
    ON broll_clip_usage (user_id, used_at DESC);
```

---



---


## [TDD-PROMPTS] · PromptOps Architecture

**Fulfills PRD Requirement:** `[PRD-AGENTIC-DRAFT]`, `[PRD-PIPELINE]`, `[PRD-COPILOT]`, `[PRD-FEATURES-CREATIVE]`, `[PRD-PLAYBOOK]`

PromptOps is the **versioned contract layer** between the application and the LLM. Every prompt lives as a YAML file under `/app/prompts/<domain>/<id>.v<semver>.yaml` with a strict Pydantic/JSON-schema output contract.

### [TDD-PROMPTS]-A · Catalog Structure

```
/app/prompts/
├── catalog.yaml
├── extraction/
│   ├── product-brief.v3.2.0.yaml
│   └── category-classifier.v1.1.0.yaml
├── copywriting/
│   ├── framework-router.v1.0.0.yaml
│   ├── script-generator-per-framework.v1.0.0.yaml
│   ├── script-refine.v1.0.0.yaml
│   └── hinglish-adapter.v1.0.0.yaml
├── critique/
│   ├── script-critic.v2.5.0.yaml
│   └── brand-safety.v1.2.0.yaml
├── strategy/
│   ├── motion-recommendation.v1.0.0.yaml
│   ├── environment-recommendation.v1.0.0.yaml
│   └── reasoning-templates.v1.0.0.yaml
├── reflection/
│   ├── deformation-guard.v1.3.0.yaml
│   └── i2v-selector.v1.0.0.yaml
└── composition/
    └── timeline-composer.v1.1.0.yaml
```

### [TDD-PROMPTS]-B · PromptCatalog Implementation

```python
class PromptCatalog:
    """Loads versioned YAML prompt contracts. Renders via Jinja2 (StrictUndefined).
    Validates outputs against declared schemas using Pydantic.
    Pillar 3 (Deep Module): simple interface, complex internals."""

    def __init__(self, prompts_dir: str = "/app/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.catalog: dict[str, dict] = {}
        self._load_all()

    def _load_all(self):
        catalog_path = self.prompts_dir / "catalog.yaml"
        with open(catalog_path) as f:
            index = yaml.safe_load(f)
        for entry in index["prompts"]:
            prompt_id, version = entry["id"], entry["version"]
            file_path = self.prompts_dir / entry["path"]
            with open(file_path) as f:
                spec = yaml.safe_load(f)
            assert spec["prompt_id"] == prompt_id
            assert "system_prompt" in spec and "user_prompt_template" in spec
            self.catalog[f"{prompt_id}@{version}"] = spec

    def render(self, prompt_id: str, version: str, variables: dict) -> "RenderedPrompt":
        key = f"{prompt_id}@{version}"
        spec = self.catalog[key]
        env = jinja2.Environment(undefined=jinja2.StrictUndefined)
        user_prompt = env.from_string(spec["user_prompt_template"]).render(**variables)
        result = RenderedPrompt()
        result.system_prompt = spec["system_prompt"]
        result.user_prompt = user_prompt
        result.model_requirements = spec.get("model_requirements", {})
        return result

    def validate_output(self, prompt_id: str, output: dict, version: str) -> "ValidationResult":
        spec = self.catalog[f"{prompt_id}@{version}"]
        required = spec.get("output_schema", {}).get("required", [])
        missing = [f for f in required if f not in output]
        if missing:
            return ValidationResult(valid=False, error_message=f"Missing: {missing}")
        return ValidationResult(valid=True)
```

### [TDD-PROMPTS]-C · Output Token Compression

All system prompts enforce minified, schema-less JSON output. No conversational filler. No reasoning trace. Pure JSON object matching the declared `output_schema`.

### [TDD-PROMPTS]-D · `script-refine.v1.0.0.yaml`

```yaml
prompt_id: script-refine
version: "1.0.0"
description: "Refine an existing ad script based on a bounded user instruction."

model_requirements:
  capability: "llm"
  json_mode: true
  max_tokens: 400

input_schema:
  type: object
  required: [current_script, user_instruction, product_brief, language, framework]

output_schema:
  type: object
  required: [hook, body, cta, full_text, word_count, language_mix]
  properties:
    hook:          { type: string, maxLength: 60 }
    body:          { type: string, maxLength: 250 }
    cta:           { type: string, maxLength: 50 }
    full_text:     { type: string }
    word_count:    { type: integer, maximum: 35 }
    language_mix:  { type: string, enum: [pure_hindi, hinglish, pure_english] }

system_prompt: |
  You are an expert Indian e-commerce ad copywriter for Adcreo.
  You are refining an existing ad script based on the user's bounded feedback.
  Maintain the product facts from the brief. Stay within the specified language.
  PRESERVE the script's framework angle ({{ framework }}) — do not pivot to a different angle.
  Output ONLY the refined script as JSON. No explanations.
  Keep the total script under 35 words for a 5–10 second video.

user_prompt_template: |
  PRODUCT: {{ product_brief.product_name }} ({{ product_brief.category }})
  PRICE: ₹{{ product_brief.price_inr }}
  KEY FEATURES: {{ product_brief.key_features | join(', ') }}
  LANGUAGE: {{ language }}
  FRAMEWORK ANGLE (preserve): {{ framework }}
  CURRENT SCRIPT:
  [HOOK] {{ current_script.hook }}
  [BODY] {{ current_script.body }}
  [CTA]  {{ current_script.cta }}
  USER REQUEST: {{ user_instruction }}
  Refine the script according to the user's request. Return JSON only.
```

### [TDD-PROMPTS]-E · `framework-router.v1.0.0.yaml`

```yaml
prompt_id: framework-router
version: "1.0.0"
description: |
  Selects exactly 3 distinct ad frameworks from the 12-framework Dynamic Playbook
  catalog given a product_brief and a campaign_brief. Acts as a creative director.
  Default trio composition: 1 logic-led + 1 emotion-led + 1 conversion-led.
  Falls back to safe trio (pas_micro + usage_ritual + social_proof) if evidence is weak.

model_requirements:
  capability: "llm"
  json_mode: true
  max_tokens: 600

input_schema:
  type: object
  required: [product_brief, campaign_brief]

output_schema:
  type: object
  required: [selected, rationale, fallback_triggered]
  properties:
    selected:
      type: array
      minItems: 3
      maxItems: 3
      items:
        type: string
        enum:
          - pas_micro
          - clinical_flex
          - myth_buster
          - asmr_trigger
          - usage_ritual
          - hyper_local_comfort
          - spec_drop_flex
          - premium_upgrade
          - roi_durability_flex
          - festival_occasion_hook
          - scarcity_drop
          - social_proof
      uniqueItems: true
    rationale:
      type: object
      additionalProperties:
        type: string
        maxLength: 200
    evidence_assessment:
      type: object
      required: [strength, signal]
      properties:
        strength: { type: string, enum: [strong, moderate, weak] }
        signal:   { type: string, maxLength: 100 }
    fallback_triggered:
      type: boolean

system_prompt: |
  You are the Adcreo creative director. Your job is to evaluate a product brief
  and select EXACTLY 3 distinct ad frameworks from the 12-framework Dynamic Playbook.

  ROUTING PRINCIPLES:
    P1. Default trio MUST cover one logic-led + one emotion-led + one conversion-led.
    P2. If evidence is WEAK: set fallback_triggered=true and select safe trio
        [pas_micro, usage_ritual, social_proof].
    P3. STRONG factual proof → prefer clinical_flex or spec_drop_flex.
    P4. Motion-rich/texture-rich visuals → prefer asmr_trigger or usage_ritual.
    P5. Premium/high-consideration → prefer premium_upgrade or roi_durability_flex.
    P6. Calendar trigger (festival, payday) → prefer festival_occasion_hook.

  Return ONLY a JSON object matching the output_schema.

user_prompt_template: |
  PRODUCT BRIEF:
    Name: {{ product_brief.product_name }}
    Category: {{ product_brief.category }}
    Key Features: {{ product_brief.key_features | join('; ') }}
    Price (INR): {{ product_brief.price_inr | default('unknown') }}

  CAMPAIGN BRIEF:
    Creative Goal: {{ campaign_brief.creative_goal }}
    Audience State: {{ campaign_brief.audience_state }}
    Language: {{ campaign_brief.language }}
    Duration: {{ campaign_brief.duration_seconds }}s

  Select exactly 3 distinct frameworks. Return JSON only.
```

### [TDD-PROMPTS]-F · `script-generator-per-framework.v1.0.0.yaml`

```yaml
prompt_id: script-generator-per-framework
version: "1.0.0"
description: "Generate ONE ad script tailored to ONE specific framework."

model_requirements:
  capability: "llm"
  json_mode: true
  max_tokens: 400

input_schema:
  type: object
  required: [product_brief, campaign_brief, framework, framework_angle]

output_schema:
  type: object
  required: [hook, body, cta, full_text, word_count, language_mix,
             framework, framework_angle, evidence_note, suggested_tone]
  properties:
    hook:               { type: string, maxLength: 60 }
    body:               { type: string, maxLength: 250 }
    cta:                { type: string, maxLength: 50 }
    full_text:          { type: string }
    word_count:         { type: integer, maximum: 35 }
    language_mix:       { type: string, enum: [pure_hindi, hinglish, pure_english] }
    framework:          { type: string }
    framework_angle:    { type: string, enum: [logic, emotion, conversion] }
    evidence_note:      { type: string, maxLength: 200 }
    suggested_tone:     { type: string, maxLength: 80 }

system_prompt: |
  You are an expert Indian e-commerce ad copywriter for Adcreo.
  Generate ONE ad script that strictly embodies the assigned framework: {{ framework }}.
  Framework angle: {{ framework_angle }}.
  Keep the total script under 35 words for a 5–10 second video.
  Output ONLY the script JSON. No explanations.

user_prompt_template: |
  PRODUCT: {{ product_brief.product_name }} ({{ product_brief.category }})
  PRICE: ₹{{ product_brief.price_inr | default('unknown') }}
  KEY FEATURES: {{ product_brief.key_features | join(', ') }}
  LANGUAGE: {{ campaign_brief.language }}
  FRAMEWORK: {{ framework }}
  FRAMEWORK ANGLE: {{ framework_angle }}
  Generate ONE script in this framework's voice. Return JSON only.
```

---

---


---


## [TDD-WORKERS] · Worker Architecture & Implementations

**Fulfills PRD Requirement:** `[PRD-PIPELINE]`, `[PRD-AGENTIC-DRAFT]`, `[PRD-PLAYBOOK]`, `[PRD-HD3]`, `[PRD-HD4]`, `[PRD-HD5]`, `[PRD-HD6]`, `[PRD-FEATURES-CREATIVE]`, `[PRD-FEATURES-PRODUCTION]` The worker fabric is 11 functional workers plus one coordinator, split across two ARQ processes (`adcreo-studio`, `adcreo-render`). The permission matrix is **the** authority on what each worker is allowed to read/write — any deviation is a CI failure (`ci/worker_perm_guard.py`). The `pre_topup_status` column is explicitly carved out: **no worker may write it**; only L2 FastAPI route handlers and the Razorpay webhook do.

### [TDD-WORKERS]-A · Worker Permission Matrix

| Worker                     | Read                                                                                                  | Write                                                                                  | DENIED                                                                             |
| -------------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **EXTRACT**                | source_url, source_image                                                                              | product_brief, isolated_png_url, agent_motion_suggestion                               | wallet, scripts                                                                    |
| **COPY (router mode)**     | product_brief, campaign_brief                                                                         | routed_frameworks, routing_rationale                                                   | wallet, raw_scripts                                                                |
| **COPY (generate mode)**   | product_brief, campaign_brief, routed_frameworks                                                      | raw_scripts (3 framework-tagged)                                                       | wallet, refined_script                                                             |
| **COPY (refine mode)**     | refined_script (or selected from safe_scripts), user_instruction, product_brief                       | refined_script                                                                         | wallet, raw_scripts, safe_scripts                                                  |
| **CRITIC**                 | raw_scripts, product_brief                                                                            | critic_scores, rationale                                                               | wallet, modify scripts                                                             |
| **SAFETY**                 | raw_scripts (or chat-refined script)                                                                  | safety_flags, safe_scripts                                                             | wallet, publish                                                                    |
| **STRATEGIST**             | safe_scripts, style_memory (incl. brand_tier, brand_color_primary), health_scores, cogs_estimate, director_tips, chat_turns_used, broll_clips, seasons, broll_clip_usage | strategy_card, **b_roll_plan**, **structure_template**, **active_season**, broll_clip_usage (INSERT) | wallet, render, publish, ALL external APIs, ALL HTTP clients, **pre_topup_status** |
| **TTS**                    | selected_script (or refined_script)                                                                   | tts_audio_url                                                                          | wallet, I2V                                                                        |
| **I2V**                    | isolated_png, motion_id, env_id                                                                       | i2v_candidates[]                                                                       | wallet, TTS                                                                        |
| **REFLECT**                | i2v_candidates[], source_png                                                                          | selected_i2v_url                                                                       | wallet, re-render                                                                  |
| **COMPOSE**                | tts, selected_i2v, benefit, b_roll_plan, structure_template, broll_clips (DB fetch), user_style_profiles (brand_tier, brand_color_primary) | preview_url                                                                            | wallet                                                                             |
| **EXPORT (v3 standalone)** | preview_url, declaration                                                                              | exports JSONB, c2pa_manifest_hash, style_memory_update                                 | wallet (refund only via DLQ), **pre_topup_status**                                 |
| **phase4_coordinator**     | gen_id only                                                                                           | status transitions {funds_locked → rendering → reflecting → composing → preview_ready} | wallet, EXPORT enqueue (must NOT enqueue worker_export)                            |

**v3 invariant:** No worker (including L5/L6) writes `pre_topup_status`. Only L2 (FastAPI route handlers in `/approve-strategy` and `/retry-export`) and the Razorpay webhook handler write this column. CI rule: `ci/check_pre_topup_writes.py` greps `app/workers/` for any UPDATE/INSERT touching `pre_topup_status`.

### [TDD-WORKERS]-B · Worker-EXTRACT

**Fulfills PRD Requirement:** `[PRD-HD1]`, `[PRD-HD2]`, `[PRD-PIPELINE]` (Phase 1), `[PRD-CATEGORY]`, `[PRD-GREENZONE]`, `[PRD-CONFIDENCE]` Phase 1 entry worker. 15s Firecrawl timeout; 10MB upload cap at L2; 15MB scraped image cap inside the worker. Vision pass returns product_brief only. confidence_score
is computed deterministically from BiRefNet alpha mask
(GAP-10). No LLM call is involved for confidence.; confidence ≥ 0.90 triggers `agent_motion_suggestion`; Red Zone categories raise `CategoryError` → `failed_category`. 



```python
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10MB (L2 gate)
FIRECRAWL_TIMEOUT_SECONDS = 15

import asyncio
import httpx
from transformers import pipeline

# Load BiRefNet globally at worker startup (warm boot — saves ~3s per gen)
# Apache 2.0 license — commercially clean replacement for Bria RMBG-1.4
logger.info("Warming up BiRefNet model into memory...")
from rembg import remove, new_session
GLOBAL_BG_SESSION = new_session("birefnet-general")

class WorkerExtract:
    """Phase 1. Pillar 5: 15s Firecrawl timeout. 10MB upload cap."""

    async def process(self, gen_id, source_url=None, source_image_url=None):
        if source_url:
            async with asyncio.timeout(FIRECRAWL_TIMEOUT_SECONDS):
                scraped = await self.firecrawl_client.scrape(source_url)
                image_bytes = await self._download_image(scraped["metadata"]["og:image"])
        elif source_image_url:
            image_bytes = await self._download_from_r2(source_image_url)
        else:
            raise ValueError("Either source_url or source_image_url required")

        # BiRefNet runs in thread pool — keeps the event loop free
        isolated_pil = await asyncio.to_thread(
            remove, image_bytes, session=GLOBAL_BG_SESSION
        )
        isolated_url = await self._upload_to_r2(gen_id, "isolated/product.png", isolated_png)
        
        vision_result = await self.gateway.route(
            capability="vision",
            input_data={
                "image": isolated_png,
                "task": "product_analysis",
                "gen_id": gen_id,
            }
        )
        
        confidence = self._compute_confidence(isolated_pil)
        
        product_brief = {
            "product_name": vision_result["product_name"],
            "category": vision_result["category"],
            "price_inr": vision_result.get("price_inr"),
            "key_features": vision_result["key_features"],
            "color_palette": vision_result["color_palette"],
            "shape": vision_result["shape"],
        }

        if product_brief["category"] not in GREEN_ZONE_SET:
            raise CategoryError(f"Red Zone: {product_brief['category']}")
            
        motion_suggestion = (
            self._suggest_motion(product_brief["shape"]) if confidence >= 0.90 else None
        )

        return {
            "isolated_png_url": isolated_url,
            "confidence_score": confidence,
            "product_brief": product_brief,
            "product_shape": product_brief["shape"],
            "agent_motion_suggestion": motion_suggestion,
        }

    def _compute_confidence(self, isolated_pil) -> float:
        """
        Deterministic isolation quality score — GAP-10.
        Input : PIL Image with alpha channel (BiRefNet output).
        Output: float [0.0, 1.0]

        Tuning levers (tweakable without PRD/BEF changes):
          alpha > 128  — foreground pixel threshold
          0.4          — soft-edge penalty weight
        """
        import numpy as np
        alpha = np.array(isolated_pil.getchannel("A"))
        foreground_ratio = float((alpha > 128).mean())
        soft_edge_ratio  = float(
            ((alpha > 10) & (alpha < 245)).mean()
        )
        raw = foreground_ratio * (1.0 - soft_edge_ratio * 0.4)
        return round(min(max(raw, 0.0), 1.0), 4)

    async def _download_image(self, url):
        async with httpx.AsyncClient(timeout=FIRECRAWL_TIMEOUT_SECONDS) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
```

### [TDD-WORKERS]-C · Worker-COPY · 3 Modes

**Fulfills PRD Requirement:** `[PRD-AGENTIC-DRAFT]`, `[PRD-PLAYBOOK]`, `[PRD-FEATURES-CREATIVE]`, `[PRD-HD3]`, `[PRD-COPILOT]` Worker-COPY has three modes wired via distinct method entry points. `framework_router()` is the Dynamic Playbook center of gravity. `generate_per_framework()` fans out 3 parallel calls via `asyncio.gather`. `refine()` is the chat-mode pathway. 
```python
from app.types.frameworks import AdFramework, FRAMEWORK_ANGLE_MAP, SAFE_TRIO
import json
import asyncio

class WorkerCopy:
    """Pillar 1 (CWD: bounded coordination), Pillar 2 (bounded inference economics).
    Three modes:
    - framework_router(brief, campaign): selects 3 distinct frameworks via LLM.
    - generate_per_framework(brief, campaign, frameworks): generates 3 scripts in parallel.
    - refine(current_script, instruction, brief, language): chat refinement (single script).
    """
    def __init__(self, gateway, prompt_catalog, gen_id):
        self.gateway = gateway
        self.prompt_catalog = prompt_catalog
        self.gen_id = gen_id

    # ───────────────────────────── MODE 1: ROUTING ─────────────────────────────
    async def framework_router(self, product_brief: dict, campaign_brief: dict) -> tuple[list[AdFramework], dict[str, str], bool]:
        """Returns (selected_frameworks, rationale_per_framework, fallback_triggered)."""
        rendered = self.prompt_catalog.render(
            "framework-router", "1.0.0",
            variables={"product_brief": product_brief, "campaign_brief": campaign_brief}
        )
        try:
            response = await self.gateway.route(
                capability="llm",
                input_data={
                    "system_prompt": rendered.system_prompt,
                    "user_prompt": rendered.user_prompt,
                    "response_format": {"type": "json_object"},
                    "gen_id": self.gen_id,
                }
            )
            output = json.loads(response.text)
            from app.models.framework_routing import FrameworkRoutingOutput
            validated = FrameworkRoutingOutput(**output)
            selected = [AdFramework(f) for f in validated.selected]
            rationale = validated.rationale
            fallback = validated.fallback_triggered

            if len(set(selected)) != 3:
                raise ValueError("LLM returned non-distinct frameworks")

            angles = {FRAMEWORK_ANGLE_MAP[f] for f in selected}
            default_trio_satisfied = angles == {"logic", "emotion", "conversion"}

            FRAMEWORK_SELECTION_DISTRIBUTION.labels(
                fallback="true" if fallback else "false",
                default_trio_satisfied="true" if default_trio_satisfied else "false"
            ).inc()

            for f in selected:
                FRAMEWORK_PER_SELECTION.labels(framework=f.value).inc()

            return list(selected), rationale, fallback

        except Exception as e:
            logger.warning(f"framework_router fallback for {self.gen_id}: {e}")
            FRAMEWORK_FALLBACK_TRIGGERED.labels(reason="schema_violation").inc()
            safe_rationale = {
                AdFramework.PAS_MICRO.value: "Safe fallback: pain-point clarity",
                AdFramework.USAGE_RITUAL.value: "Safe fallback: lifestyle context",
                AdFramework.SOCIAL_PROOF.value: "Safe fallback: trust signal",
            }
            return list(SAFE_TRIO), safe_rationale, True

    # ───────────────────────── MODE 2: GENERATE-PER-FRAMEWORK ─────────────────────────
    async def generate_per_framework(self, product_brief: dict, campaign_brief: dict, frameworks: list[AdFramework]) -> list["Script"]:
        if len(frameworks) != 3:
            raise ValueError(f"Expected exactly 3 frameworks, got {len(frameworks)}")

        async def _gen_one(framework: AdFramework) -> "Script":
            angle = FRAMEWORK_ANGLE_MAP[framework]
            rendered = self.prompt_catalog.render(
                "script-generator-per-framework", "1.0.0",
                variables={
                    "product_brief": product_brief,
                    "campaign_brief": campaign_brief,
                    "framework": framework.value,
                    "framework_angle": angle,
                }
            )
            response = await self.gateway.route(
                capability="llm",
                input_data={
                    "system_prompt": rendered.system_prompt,
                    "user_prompt": rendered.user_prompt,
                    "response_format": {"type": "json_object"},
                    "gen_id": self.gen_id,
                }
            )
            output = json.loads(response.text)
            validation = self.prompt_catalog.validate_output("script-generator-per-framework", output, "1.0.0")
            if not validation.valid:
                raise ScriptGenerationError(f"Framework {framework.value}: {validation.error_message}")

            output["framework"] = framework.value
            output["framework_angle"] = angle
            await self._trace_framework_generation(framework, output)
            from app.types.script import Script
            return Script(**output)

        tasks = [_gen_one(f) for f in frameworks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        scripts: list["Script"] = []
        failures = 0

        for fw, res in zip(frameworks, results):
            if isinstance(res, Exception):
                failures += 1
                logger.warning(f"Framework {fw.value} generation failed: {res}")
                scripts.append(self._degraded_script(fw))
            else:
                scripts.append(res)

        if failures == 3:
            raise SafetyError("All 3 framework-routed drafts failed generation")
        return scripts

    def _degraded_script(self, framework: AdFramework) -> "Script":
        from app.types.script import Script
        return Script(
            hook="Discover quality you can trust.",
            body="Made for everyday Indian homes.",
            cta="Shop now.",
            full_text="Discover quality you can trust. Made for everyday Indian homes. Shop now.",
            word_count=12,
            language_mix="pure_english",
            framework=framework.value,
            framework_angle=FRAMEWORK_ANGLE_MAP[framework],
            framework_rationale="Degraded placeholder (generation failed)",
            evidence_note="N/A — placeholder",
            suggested_tone="neutral",
        )

    async def _trace_framework_generation(self, framework: AdFramework, output: dict) -> None:
        await db.execute(
            """INSERT INTO agent_traces (gen_id, worker, framework, output_summary, model_used, cost_inr, selection_reason)
               VALUES ($1, 'copy', $2, $3::jsonb, $4, $5, $6)""",
            self.gen_id,
            framework.value,
            json.dumps({"hook": output.get("hook"), "word_count": output.get("word_count")}),
            self.gateway.last_model_used,
            float(self.gateway.last_call_cost),
            f"framework={framework.value}; angle={FRAMEWORK_ANGLE_MAP[framework]}",
        )

    # ───────────────────────────── MODE 3: REFINE ─────────────────────────────
    async def refine(self, current_script: dict, user_instruction: str, product_brief: dict, language: str) -> "Script":
        framework = current_script.get("framework", "pas_micro")
        rendered = self.prompt_catalog.render(
            "script-refine", "1.0.0",
            variables={
                "current_script": current_script,
                "user_instruction": user_instruction,
                "product_brief": product_brief,
                "language": language,
                "framework": framework,
            }
        )
        response = await self.gateway.route(
            capability="llm",
            input_data={
                "system_prompt": rendered.system_prompt,
                "user_prompt": rendered.user_prompt,
                "response_format": {"type": "json_object"},
                "gen_id": self.gen_id,
            }
        )
        output = json.loads(response.text)
        validation = self.prompt_catalog.validate_output("script-refine", output, "1.0.0")
        if not validation.valid:
            raise RefineError(validation.error_message)

        output["framework"] = framework
        output["framework_angle"] = FRAMEWORK_ANGLE_MAP.get(AdFramework(framework), "logic")
        output["framework_rationale"] = current_script.get("framework_rationale", "")
        output["evidence_note"] = current_script.get("evidence_note", "")
        output["suggested_tone"] = current_script.get("suggested_tone", "")
        
        from app.types.script import Script
        return Script(**output)
```

### [TDD-WORKERS]-C2 · B-Roll Shot Planner *(SUPERSEDED by `[TDD-BROLL]` — v4-Δ1)*

**Status:** Superseded. The v3 deterministic library-backed planner described in this anchor has been extended into the role-first, template-driven design specified in `[TDD-BROLL]`. The anchor ID is preserved so existing cross-references (PRD F-405, BEF §9.6, agent prompts) continue to resolve.

**Authoritative spec:** `[TDD-BROLL]` (full chapter, lines 3840–4172 in the V4 source). Primary references for code work:

- Product goal & non-goals: `[TDD-BROLL]-A`
- Architecture summary (planner call surface, return shape): `[TDD-BROLL]-B`
- The 5 structural templates and their canonical 15s timelines: `[TDD-BROLL]-C`
- Role semantics (`hook` / `context` / `cta_bg`, role purity invariant): `[TDD-BROLL]-D`
- Clip & rotation & seasons schema (authoritative): `[TDD-BROLL]-E`
- Seasonality + brand-tier behavior: `[TDD-BROLL]-F`
- Selection logic in plain English (the planner contract): `[TDD-BROLL]-G`
- Worker-COMPOSE branch logic + text-card path: `[TDD-BROLL]-H`
- Intentionally deferred to v2 (perf feedback, color harmony, etc.): `[TDD-BROLL]-I`
- CI guards (coverage check, sandbox extension): `[TDD-BROLL]-J`
- Invariants (the contract Worker-STRATEGIST + Worker-COMPOSE must uphold): `[TDD-BROLL]-K`

**Worker integration:** Worker-STRATEGIST (see `[TDD-WORKERS]-G`) invokes `BRollPlanner.plan(template, angle, category, brand_tier, user_id)` and persists `b_roll_plan` + `structure_template` + `active_season` to the generation row, atomically with inserts into `broll_clip_usage` for every non-null clip in the plan. Worker-COMPOSE (`[TDD-WORKERS]-H` + `[TDD-VIDEO]-B`) reads these and branches per template.

**v3 hard constraints retained:** no LLM at runtime, no embeddings, no external API in the selection path, no new workers, no GPU. The planner remains a deterministic SQL read with total-ordered tiebreaks. CI extension forbids embedding-library imports in `app/broll/` (see `[TDD-IMPORT-GRAPH]` and `[TDD-BROLL]-J`).

**Why the supersede (not a rewrite of this anchor):** other documents (BEF, PRD F-405 traceability, in-repo docstrings) link to `[TDD-WORKERS]-C2`. Preserving the anchor with a clear pointer is the lowest-cost way to keep cross-references resolvable while moving authority to the new chapter.

### [TDD-WORKERS]-D · Phase-2 Chain Wiring

**Fulfills PRD Requirement:** `[PRD-PIPELINE]` (Phase 2), `[PRD-AGENTIC-DRAFT]`, `[PRD-HD3]`, `[PRD-AC-2]` The Phase-2 ARQ task `phase2_chain` invokes the workers in canonical order: `framework_router → generate_per_framework → CRITIC → SAFETY → scripts_ready`. State transitions are guarded by the FSM trigger. On `SafetyError`, the chain auto-retries once with the safe trio. 


```python
async def phase2_chain(ctx, gen_id: str):
    """Phase 2: routing → generation → critique → safety → scripts_ready."""
    gen = await db.fetchrow(
        "SELECT product_brief, campaign_brief, plan_tier FROM generations WHERE gen_id=$1 AND status='scripting'",
        gen_id
    )
    if not gen:
        return

    # 1. Framework router
    selected, rationale, fallback = await WorkerCopy(
        gateway=gateway, prompt_catalog=prompt_catalog, gen_id=gen_id
    ).framework_router(gen["product_brief"], gen["campaign_brief"])

    await db.execute(
        "UPDATE generations SET routed_frameworks = $2, routing_rationale = $3::jsonb WHERE gen_id = $1 AND status = 'scripting'",
        gen_id, [f.value for f in selected], json.dumps(rationale)
    )

    # 2. Generate per framework (parallel)
    scripts = await WorkerCopy(
        gateway=gateway, prompt_catalog=prompt_catalog, gen_id=gen_id
    ).generate_per_framework(gen["product_brief"], gen["campaign_brief"], selected)

    await db.execute(
        "UPDATE generations SET raw_scripts = $2::jsonb, status = 'critiquing' WHERE gen_id = $1 AND status = 'scripting'",
        gen_id, json.dumps([s.__dict__ for s in scripts])
    )

    # 3. Critique
    critic_result = await WorkerCritic(
        gateway=gateway, prompt_catalog=prompt_catalog, gen_id=gen_id
    ).process(scripts, gen["product_brief"])

    await db.execute(
        "UPDATE generations SET critic_scores = $2::jsonb, status = 'safety_checking' WHERE gen_id = $1 AND status = 'critiquing'",
        gen_id, json.dumps(critic_result["scores_by_framework"])
    )

    # 4. Safety batch
    try:
        safety_result = await WorkerSafety().process(critic_result["ranked_scripts"])
    except SafetyError:
        SAFETY_AUTORETRY_TOTAL.inc()
        scripts_safe = await WorkerCopy(
            gateway=gateway, prompt_catalog=prompt_catalog, gen_id=gen_id
        ).generate_per_framework(gen["product_brief"], gen["campaign_brief"], list(SAFE_TRIO))
        
        critic_result = await WorkerCritic(
            gateway=gateway, prompt_catalog=prompt_catalog, gen_id=gen_id
        ).process(scripts_safe, gen["product_brief"])
        
        try:
            safety_result = await WorkerSafety().process(critic_result["ranked_scripts"])
        except SafetyError:
            await db.execute("UPDATE generations SET status='failed_safety', error_code='ECM-003' WHERE gen_id=$1", gen_id)
            await sse_manager.push(gen_id, {"type": "state_change", "state": "failed_safety"})
            return

    await db.execute(
        """UPDATE generations SET safe_scripts = $2::jsonb, safety_flags = $3::jsonb, selected_script_id = 1, status = 'scripts_ready' WHERE gen_id = $1 AND status = 'safety_checking'""",
        gen_id, json.dumps(safety_result["safe_scripts"]), json.dumps(safety_result["safety_flags"])
    )
    await sse_manager.push(gen_id, {"type": "state_change", "state": "scripts_ready"})
```

### Checkpoint Re-entry Rule (implements BEF GAP — MP3-C1)

`phase2_chain` is replay-safe. On every execution, before invoking
any worker, the job reads the current checkpoint state:

```python
checkpoint = await db.fetchrow(
    """SELECT routed_frameworks, raw_scripts, critic_scores, safe_scripts
       FROM generations WHERE gen_id = $1""",
    gen_id
)
```

Stage skip rules (evaluated in this order before any worker runs):

- `routed_frameworks IS NOT NULL` → skip `WorkerCopy.framework_router`. Use the existing value; proceed directly to `generate_per_framework`.
- `raw_scripts IS NOT NULL` → skip `WorkerCopy.generate_per_framework`. Reconstruct `scripts` from the stored JSON; proceed to `WorkerCritic`.
- `critic_scores IS NOT NULL` → skip `WorkerCritic`. Reconstruct `critic_result` from stored scores; proceed to `WorkerSafety`.
- `safe_scripts IS NOT NULL` → job is a duplicate execution. Verify `status == 'scripts_ready'` and return early (idempotent success — no writes, no SSE push).

Re-entry reads only. It never resets, overwrites, or NULLs any checkpoint column. Stage skip does not bypass the FSM — state-guarded UPDATEs in the non-skipped stages still enforce the `WHERE status=` precondition. This prevents double-billing of LLM COGS on retry and ensures `CostGuard.pre_check` in the `/chat` chain reflects actual spend, not projected re-spend.

### [TDD-WORKERS]-E · Worker-CRITIC

**Fulfills PRD Requirement:** `[PRD-AGENTIC-DRAFT]`, `[PRD-PIPELINE]` (Phase 2), `[PRD-HD3]` CRITIC scores all 3 framework-tagged scripts. It does **no filtering**; it orders by score with tie-break by framework angle (conversion > emotion > logic). 

```python
import json

  

class WorkerCritic:

    """Scores 3 framework-tagged scripts. NO filtering — all 3 passed downstream to SAFETY. CRITIC orders by score."""

    def __init__(self, gateway, prompt_catalog, gen_id):

        self.gateway = gateway

        self.prompt_catalog = prompt_catalog

        self.gen_id = gen_id

  

    async def process(self, scripts: list["Script"], product_brief: dict) -> dict:

        if len(scripts) != 3:

            raise ValueError(f"CRITIC expects exactly 3 scripts, got {len(scripts)}")

        rendered = self.prompt_catalog.render(

            "script-critic", "2.5.0",

            variables={

                "scripts": [s.__dict__ for s in scripts],

                "product_brief": product_brief,

            }

        )

        response = await self.gateway.route(

            capability="llm",

            input_data={

                "system_prompt": rendered.system_prompt,

                "user_prompt": rendered.user_prompt,

                "response_format": {"type": "json_object"},

                "gen_id": self.gen_id,

            }

        )

        result = json.loads(response.text)

        scored_scripts = []

        scores_by_framework: dict[str, int] = {}

        for i, script in enumerate(scripts):

            score = int(result["scores"][i])

            rationale = result["rationales"][i]

            script.critic_score = score

            script.critic_rationale = rationale

            scored_scripts.append(script)

            scores_by_framework[script.framework] = score

            FRAMEWORK_CRITIC_SCORE.labels(framework=script.framework).observe(score)

        scored_scripts.sort(

            key=lambda s: (s.critic_score, {"conversion": 3, "emotion": 2, "logic": 1}[s.framework_angle]),

            reverse=True

        )

        return {

            "ranked_scripts": scored_scripts,

            "scores_by_framework": scores_by_framework,

            "rationales": result["rationales"],

        }
```

### [TDD-WORKERS]-F · Worker-SAFETY

**Fulfills PRD Requirement:** `[PRD-FEATURES-COMPLIANCE]`, `[PRD-NON-NEGOTIABLES]`, `[PRD-HD3]`, `[PRD-AC-2]` Batch safety gate. Per-script moderation + PII patterns + competitor-name denylist. All-3-rejected raises `SafetyError`. 
```python
import re

  

class WorkerSafety:

    """Batch safety check on 3 framework-tagged scripts.

    Rejection of any individual script removes it from safe_scripts.

    If all 3 are rejected: raises SafetyError → caller (phase2_chain) auto-retries with safe-trio once."""

    def __init__(self, gateway):

        self.gateway = gateway

  

    async def process(self, scored_scripts: list["Script"]) -> dict:

        safe_scripts: list["Script"] = []

        safety_flags: list[dict] = []

        for script in scored_scripts:

            flag = await self._check_single(script.full_text)

            safety_flags.append({**flag, "framework": script.framework})

            if flag["safe"]:

                safe_scripts.append(script)

        if not safe_scripts:

            raise SafetyError("All scripts failed safety checks")

        return {

            "safe_scripts": [s.__dict__ for s in safe_scripts],

            "safety_flags": safety_flags,

        }

  

    async def _check_single(self, text: str) -> dict:

        # L6-05 Fix: Routed through gateway instead of direct OpenAI SDK call

        mod_result = await self.gateway.route(

            capability="moderation",

            input_data={"text": text}

        )

        if not mod_result.get("safe", True):

            return {"safe": False, "reason": "moderation_flagged"}

        for pattern, pii_type in [

            (r'\b\d{10}\b', 'phone'),

            (r'\b[\w.+-]+@[\w-]+\.[\w.]+\b', 'email'),

            (r'\b\d{4}\s?\d{4}\s?\d{4}\b', 'aadhaar'),

        ]:

            if re.search(pattern, text):

                return {"safe": False, "reason": f"pii:{pii_type}"}

        for comp in ["creatify", "invideo", "canva", "runway", "pika", "oxolo", "vidyo"]:

            if comp in text.lower():

                return {"safe": False, "reason": f"competitor:{comp}"}

        return {"safe": True, "reason": None}
```

### [TDD-WORKERS]-G · Worker-STRATEGIST

**Fulfills PRD Requirement:** `[PRD-HD4]`, `[PRD-COPILOT]`, `[PRD-AGENTIC-DRAFT]`, `[PRD-FEATURES-INTENT]` F-701 **ZERO external API access** — CI-enforced via `ci/strategist_sandbox_check.py`. Read-only over `generations + user_style_profiles + broll_clips + seasons + broll_clip_usage`. Surfaces `routed_frameworks + rationale + b_roll_plan + structure_template + active_season` in the Strategy Card.

**v4-Δ1:** resolves `active_season` (from `seasons` lookup) + `brand_tier` (from `user_style_profiles`) + `structure_template` (from `TEMPLATE_BY_CONTEXT` with T4 festive override) before invoking the planner. Persists plan + template + season + usage rows in a single transaction. The legacy single-arg call `BRollPlanner.plan(framework_angle, category)` is replaced by the contract specified in `[TDD-BROLL]-G`. The `broll_v4_routing_enabled` feature flag gates the new path during rollout; when FALSE the strategist short-circuits to T1 with `context=None, cta=None` (i.e. the v4 baseline behavior is preserved exactly).

```python
import json

class WorkerStrategist:
    """ZERO external API access. Read-only over Postgres + Redis health.

    v3: surfaces routed_frameworks + rationale + b_roll_plan in Strategy Card.
    v4-Δ1: resolves structure_template + active_season before planner call; atomically logs
           every selected clip to broll_clip_usage. See [TDD-BROLL]-G."""

    def __init__(self, db_pool):
        self.db = db_pool
        self.broll_planner = BRollPlanner(db_pool)

    async def process(self, gen_id, user_id, selected_script, motion_archetype_id,
                      environment_preset_id, tts_language, plan_tier, product_brief):
        gen = await self.db.fetchrow(
            """SELECT chat_turns_used, cogs_total, confidence_score, fallback_events,
                      routed_frameworks, routing_rationale
                 FROM generations WHERE gen_id=$1""",
            gen_id
        )
        chat_turns = gen["chat_turns_used"] or 0
        chat_cost = chat_turns * 0.08
        primary = await self._get_best_provider("i2v", plan_tier)
        fallback = await self._get_fallback_provider("i2v", plan_tier, exclude=primary)

        # v3 / v4-Δ1: deterministic B-roll plan (no LLM, no vector search). See [TDD-BROLL]-G.
        framework_angle = selected_script.get("framework_angle", "logic")
        category = product_brief["category"]

        # v4-Δ1 step 1: resolve active_season (single-row read; defaults to None when no row active).
        season_row = await self.db.fetchrow(
            """SELECT season_tag FROM seasons
                WHERE is_active = TRUE
                  AND NOW()::DATE BETWEEN active_from AND active_to
                ORDER BY season_tag
                LIMIT 1"""
        )
        active_season = season_row["season_tag"] if season_row else None

        # v4-Δ1 step 2: resolve brand_tier from style memory (cold-start defaults to 'mass';
        # also surface brand_color_primary so Worker-COMPOSE can read it via the strategy_card).
        style_row = await self.db.fetchrow(
            """SELECT brand_tier, brand_color_primary
                 FROM user_style_profiles
                WHERE user_id=$1 AND category=$2
                LIMIT 1""",
            user_id, category
        )
        brand_tier = (style_row["brand_tier"] if style_row else None) or "mass"

        # v4-Δ1 step 3: resolve structure_template. Precedence per [TDD-BROLL]-C:
        #   (1) feature-flag gate (legacy mode = T1 only)
        #   (2) festive override (active_season → T4)
        #   (3) TEMPLATE_BY_CONTEXT (angle, category_class, brand_tier) lookup
        #   (4) DEFAULT_TEMPLATE (T1)
        from app.broll.templates import (
            TEMPLATE_BY_CONTEXT, DEFAULT_TEMPLATE, FESTIVE_OVERRIDE_TEMPLATE, CATEGORY_CLASS,
        )
        if not await self._flag_enabled("broll_v4_routing_enabled"):
            structure_template = "T1"
        elif active_season is not None:
            structure_template = FESTIVE_OVERRIDE_TEMPLATE  # "T4"
        else:
            category_class = CATEGORY_CLASS.get(category, "functional")
            structure_template = TEMPLATE_BY_CONTEXT.get(
                (framework_angle, category_class, brand_tier),
                DEFAULT_TEMPLATE,  # "T1"
            )

        # v4-Δ1 step 4: planner emits {template, hook, context, cta}.
        # Hook is guaranteed non-null by the CI coverage check ([TDD-BROLL]-J); the planner
        # itself raises BRollCoverageError if a hook lookup ever returns empty in production.
        b_roll_plan = await self.broll_planner.plan(
            template=structure_template,
            angle=framework_angle,
            category=category,
            brand_tier=brand_tier,
            user_id=user_id,
            active_season=active_season,
        )

        # v4-Δ1 step 5: persist plan + template + season AND log rotation usage in ONE transaction.
        # The atomicity is critical: a partial write (plan without usage rows) would corrupt
        # rotation determinism on the next generation for this user.
        async with self.db.transaction():
            await self.db.execute(
                """UPDATE generations
                      SET b_roll_plan = $2::jsonb,
                          structure_template = $3,
                          active_season = $4
                    WHERE gen_id = $1""",
                gen_id, json.dumps(b_roll_plan), structure_template, active_season,
            )
            for slot in ("hook", "context", "cta"):
                clip = b_roll_plan.get(slot)
                if clip is not None:
                    await self.db.execute(
                        """INSERT INTO broll_clip_usage (user_id, clip_id, gen_id)
                                VALUES ($1, $2, $3)
                            ON CONFLICT (user_id, clip_id, gen_id) DO NOTHING""",
                        user_id, clip["clip_id"], gen_id,
                    )

        return {
            "product_summary": {
                "name": product_brief["product_name"],
                "category": product_brief["category"],
                "confidence": float(gen["confidence_score"]),
            },
            "script_summary": {
                "text": selected_script["full_text"][:100],
                "score": selected_script.get("critic_score", 0),
                "framework": selected_script.get("framework"),
                "framework_angle": selected_script.get("framework_angle"),
            },
            "frameworks_considered": {
                "selected": gen["routed_frameworks"],
                "rationale": gen["routing_rationale"],
            },
            "voice": {
                "language": tts_language,
                "provider": await self._get_best_provider("tts", plan_tier),
            },
            "motion": {
                "archetype_id": motion_archetype_id,
                "name": MOTION_NAMES[motion_archetype_id],
            },
            "environment": {
                "preset_id": environment_preset_id,
                "name": ENV_NAMES[environment_preset_id],
            },
            "provider": {
                "primary": primary,
                "fallback": fallback,
            },
            "cost_estimate": {
                "estimated_inr": float(gen["cogs_total"]) + chat_cost + self._estimate_phase4(plan_tier),
                "ceiling_inr": CostGuard.CEILING[plan_tier],
            },
            "compliance": {
                "sgi": True,
                "c2pa": True,
                "it_rules_2026": True,
            },
            "chat_turns_used": chat_turns,
            "chat_cost_inr": chat_cost,
            # v4-Δ1: structured plan + template + season + brand color surfaced to HD-4 + HD-5.
            "b_roll_plan": b_roll_plan,
            "structure_template": structure_template,
            "active_season": active_season,
            "brand_color_primary": (style_row["brand_color_primary"] if style_row else None),
            "b_roll_available": (b_roll_plan is not None and b_roll_plan.get("hook") is not None),
        }
```


### Cold-Start Style Defaults + b_roll_available (implements BEF GAP-12)

**`b_roll_available` field:** Added to the `strategy_card` JSONB payload returned by `WorkerStrategist.process()`. Value is `True` when `b_roll_plan` is non-null AND `b_roll_plan.hook` is non-null (every template guarantees a hook clip — see `[TDD-BROLL]-K` invariant 5). HD-5 reads this field from the hydrated `strategy_card` to decide whether to show the "B-roll" stage row in the render progress UI. Worker-COMPOSE branches on `structure_template` (T1..T5) and renders a text-card CTA when `b_roll_plan.cta` is null (T2/T3/T4/T5) — see `[TDD-BROLL]-H` and `[TDD-VIDEO]-B`. The pre-v4 contract (`b_roll_plan` as flat list) no longer applies; the supersede pointer in `[TDD-WORKERS]-C2` documents the migration.

**Cold-start style defaults:** When `user_style_profiles` returns zero rows for the current `user_id` (new user, no style memory), `WorkerStrategist` uses the `COLD_START_DEFAULTS` constant defined in `app/workers/strategist.py` to populate `motion_archetype_id` and `environment_preset_id`. The constant is defined per BEF GAP-12 resolution. Lookup: `COLD_START_DEFAULTS.get(category, DEFAULT_FALLBACK)`. This constant is consulted only when pgvector returns zero rows. As soon as a user completes their first generation, the style memory upsert in Worker-EXPORT fires and `COLD_START_DEFAULTS` is never used again for that user.

### [TDD-WORKERS]-H · Worker-TTS, I2V, REFLECT, COMPOSE

**Fulfills PRD Requirement:** `[PRD-PIPELINE]` (Phase 4), `[PRD-HD5]`, `[PRD-FEATURES-PRODUCTION]`, `[PRD-AC-4]`, F-205, F-403 Four Phase-4 workers. TTS language-provider routing is static. I2V uses credentialed R2 access. REFLECT applies SSIM ≥ 0.65 + deformation guard. COMPOSE canonicalizes to 5s with explicit padding — **never** `-shortest`. 
```python
import asyncio

  

class WorkerTTS:

    LANGUAGE_PROVIDER_MAP = {

        "hindi": "sarvam", "hinglish": "sarvam", "marathi": "sarvam",

        "punjabi": "sarvam", "bengali": "sarvam", "tamil": "sarvam",

        "telugu": "sarvam", "english": "elevenlabs",

    }

  

    def __init__(self, gateway):

        self.gateway = gateway

  

    async def process(self, gen_id, script_text, language):

        response = await self.gateway.route(

            capability="tts",

            input_data={"text": script_text, "language": language, "gen_id": gen_id}

        )

        return await self._upload_to_r2(gen_id, "tts/voiceover.mp3", response.audio_bytes)

  
  

class WorkerI2V:

    MOTION_ARCHETYPES = {1: "orbit", 2: "drift", 3: "hero_zoom", 4: "unbox", 5: "liquid_pour"}

  

    def __init__(self, gateway):

        self.gateway = gateway

  

    async def process(self, gen_id, isolated_png_url, motion_id, env_id, attempt=0):

        prompt = (f"Product {self.MOTION_ARCHETYPES[motion_id]} motion. "

                  f"{ENV_PRESETS[env_id]} environment. Smooth camera. 5 seconds. Commercial quality.")

        image_bytes = await self._download_from_r2(isolated_png_url)

        response = await self.gateway.route(

            capability="i2v",

            input_data={

                "image": image_bytes,

                "prompt": prompt,

                "duration": 5,

                "seed": self._generate_seed(attempt),

                "gen_id": gen_id,

            }

        )

        return await self._upload_to_r2(gen_id, f"i2v/candidate_{attempt}.mp4", response.video_bytes)

  
  

class WorkerReflect:

    SSIM_THRESHOLD = 0.65

  

    def __init__(self, gateway):

        self.gateway = gateway

  

    async def process(self, gen_id, candidates: list[str], source_png_url: str) -> str:

        source_bytes = await self._download_from_r2(source_png_url)

        best_url, best_score = None, 0.0

        for url in candidates:

            video_bytes = await self._download_from_r2(url)

            first_frame = self._extract_first_frame(video_bytes)

            ssim = self._compute_ssim(source_bytes, first_frame)

            deform = await self.gateway.route(

                capability="vision",

                input_data={"image": first_frame, "task": "deformation_check", "gen_id": gen_id}

            )

            if ssim >= self.SSIM_THRESHOLD and not deform.get("deformed"):

                combined = ssim * 0.6 + deform.get("quality_score", 0.5) * 0.4

                if combined > best_score:

                    best_score, best_url = combined, url

        if not best_url:

            raise ReflectError("No candidates passed SSIM + deformation guard")

        return best_url

  
  

CANONICAL_VIDEO_DURATION_S = 5

MAX_ALLOWED_DURATION_S = 10

  

class WorkerCompose:

    """FFmpeg: I2V + TTS + LUT + SGI. Canonical 15s. TTS padded/trimmed. No -shortest.

    v3: pads/loops video if I2V output is shorter than canonical 15s.

    v4-Δ1: reads b_roll_plan AND structure_template from generation row. Branches per template
    (T1..T5). For T2/T3/T4/T5, renders the CTA as a text-card via FFmpeg drawtext over a
    brand-color gradient (see [TDD-BROLL]-H). brand_color_primary defaults to #1A1A1A when null."""

  

    async def process(self, gen_id, i2v_url, tts_url, b_roll_plan, structure_template, benefit, plan_tier, brand_color_primary=None):
    
	    # Fetch from DB and inject 2-4 clips between A-roll segments based on scene_type mapping:
    # Transition -> motion/texture clips, Context -> warehouse/packaging/environment clips.

        video_path = f"/tmp/{gen_id}_video.mp4"

        audio_path = f"/tmp/{gen_id}_audio.mp3"

        output_path = f"/tmp/{gen_id}_preview.mp4"

        video_bytes = await self._download_from_r2(i2v_url)

        audio_bytes = await self._download_from_r2(tts_url)

        await asyncio.to_thread(self._write_file, video_path, video_bytes)

        await asyncio.to_thread(self._write_file, audio_path, audio_bytes)

        vid_dur = await self._probe_duration(video_path)

        aud_dur = await self._probe_duration(audio_path)

        if vid_dur > MAX_ALLOWED_DURATION_S or aud_dur > MAX_ALLOWED_DURATION_S:

            raise ComposeDurationError(f"Duration OOB: v={vid_dur}s a={aud_dur}s")

        lut = self._select_lut(benefit)

        target = CANONICAL_VIDEO_DURATION_S

        # v3: pad/loop video if shorter than target; trim if longer (no -shortest)

        video_filter = (

            f"lut3d={lut},"

            f"tpad=stop_mode=clone:stop_duration={max(0, target - vid_dur):.3f},"

            f"trim=end={target},"

            f"drawtext=text='AI Generated Content':fontsize=14:"

            f"fontcolor=white@0.7:x=10:y=h-30"

        )

        audio_filter = f"atrim=end={target},apad=whole_dur={target}"

        cmd = [

            "ffmpeg", "-y", "-i", video_path, "-i", audio_path,

            "-filter_complex", f"[0:v]{video_filter}[v];[1:a]{audio_filter}[a]",

            "-map", "[v]", "-map", "[a]",

            "-c:v", "libx264", "-preset", "fast", "-crf", "23",

            "-c:a", "aac", "-b:a", "128k", "-t", str(target), output_path,

        ]

        process = await asyncio.create_subprocess_exec(

            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE

        )

        _, stderr = await process.communicate()

        if process.returncode != 0:

            raise ComposeError(f"FFmpeg failed: {stderr.decode()[:500]}")

        return await self._upload_to_r2(

            gen_id, "compose/preview.mp4",

            await asyncio.to_thread(self._read_file, output_path)

        )

  

    def _select_lut(self, benefit):

        return {

            "premium": "luts/premium_warm.cube",

            "trending": "luts/trending_vivid.cube",

            "gift": "luts/gift_festive.cube",

            "natural": "luts/natural_green.cube",

        }.get(benefit, "luts/neutral_balanced.cube")
```

### [TDD-WORKERS]-I · Worker-EXPORT · Decoupled Standalone ARQ Job

**Fulfills PRD Requirement:** `[PRD-HD6]`, `[PRD-FEATURES-PAYMENT]`, `[PRD-FEATURES-PRODUCTION]` F-404, `[PRD-FEATURES-COMPLIANCE]`, `[PRD-AC-5]`, `[PRD-AC-6]`

Worker-EXPORT is **NOT** called from `phase4_coordinator`. Standalone ARQ function registered on `adcreo-render` and enqueued exclusively by L2 routes (`/declaration` for first export, `/retry-export` for retries). 
```python
import asyncio

import hashlib

import json

from datetime import datetime

  

class WorkerExport:

    """Standalone ARQ job. Decoupled from phase4_coordinator (v3).

    - Reads preview_url + declaration provenance from generations row.

    - Produces 2 final formats (1080×1080 square + 1080×1920 vertical).

    - C2PA signs both (returncode checked; failure → DLQ → failed_export + refund).
      Verification Step:
		- After signing, verification MUST be done using local `c2patool --verify`
		- External verification APIs are strictly forbidden in worker execution and
		  CI

    - Overwrites c2pa_manifest_hash on every successful run (retry-aware).

    - Updates style_memory on successful export.

    - Consumes 1 credit via wallet_consume.lua AFTER all artifacts are persisted."""

    async def process(self, gen_id: str):

        gen = await db.fetchrow(

            """SELECT user_id, preview_url, declaration_accepted, declaration_hash, product_brief, plan_tier, export_retry_count

               FROM generations WHERE gen_id = $1 AND status = 'export_queued'""",

            gen_id

        )

        if not gen:

            return  # Idempotent

        if not gen["declaration_accepted"]:

            raise ExportPreconditionError("Declaration not accepted; cannot export")

        # v3: defensive R2 check before doing expensive work

        if not await self._r2_head_exists(gen["preview_url"]):

            await db.execute("UPDATE generations SET status='failed_export', error_code='ECM-018' WHERE gen_id=$1", gen_id)

            raise ExportPreconditionError("Preview purged; cannot export")

        preview_path = f"/tmp/{gen_id}_preview.mp4"

        await asyncio.to_thread(

            self._write_file, preview_path,

            await self._download_from_r2(gen["preview_url"])

        )

        # 2 final formats

        square_path = f"/tmp/{gen_id}_square.mp4"

        vertical_path = f"/tmp/{gen_id}_vertical.mp4"

        await self._ffmpeg_scale(preview_path, square_path, "1080:1080", crf=18)

        await self._ffmpeg_scale(preview_path, vertical_path, "1080:1920", crf=18)

        # C2PA sign each (returncode checked)

        square_signed = await self._c2pa_sign(square_path, gen_id)

        vertical_signed = await self._c2pa_sign(vertical_path, gen_id)

        # Upload to R2 (overwrites previous retry artifacts at same path)

        square_url = await self._upload_to_r2(

            gen_id, "export/square_1x1.mp4",

            await asyncio.to_thread(self._read_file, square_signed)

        )

        vertical_url = await self._upload_to_r2(

            gen_id, "export/vertical_9x16.mp4",

            await asyncio.to_thread(self._read_file, vertical_signed)

        )

        # Atomic DB commit + wallet consume

        async with db.transaction():

            await db.execute(

                """UPDATE generations SET exports = $2::jsonb, c2pa_manifest_hash = $3, status = 'export_ready'

                   WHERE gen_id = $1 AND status = 'export_queued'""",

                gen_id,

                json.dumps({

                    "square_url": square_url,

                    "vertical_url": vertical_url,

                    "c2pa_manifest_hash": self._last_manifest_hash,

                    "finalized_at": datetime.utcnow().isoformat(),

                }),

                self._last_manifest_hash

            )

            await db.execute(

                """UPDATE wallet_transactions SET status = 'consumed'::wallet_status

                   WHERE gen_id = $1 AND type = 'lock' AND status = 'locked'""",

                gen_id

            )

            await redis_lua.wallet_consume(user_id=gen["user_id"], gen_id=gen_id)

        # Style Memory (best-effort)

        try:

            await self._update_style_memory(gen_id, gen["user_id"])

        except Exception as e:

            logger.warning(f"Style Memory update failed for {gen_id}: {e}")

        await sse_manager.push(gen_id, {

            "type": "state_change",

            "state": "export_ready",

            "exports": {"square_url": square_url, "vertical_url": vertical_url},

        })

  

    async def _c2pa_sign(self, video_path: str, gen_id: str) -> str:

        """Returncode checked. Failure → C2PASignError → DLQ → failed_export + refund."""

        output_path = video_path.replace(".mp4", "_signed.mp4")

        manifest = self._build_manifest(gen_id)

        cmd = ["c2patool", video_path, "--output", output_path, "--manifest", manifest]

        proc = await asyncio.create_subprocess_exec(

            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE

        )

        try:

            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

        except asyncio.TimeoutError:

            proc.kill()

            raise C2PASignError(f"c2patool timeout for {gen_id}")

        if proc.returncode != 0:

            raise C2PASignError(f"c2patool failed rc={proc.returncode}: {stderr.decode()[:500]}")

        self._last_manifest_hash = hashlib.sha256(manifest.encode()).hexdigest()

        return output_path

  

    async def _r2_head_exists(self, url: str) -> bool:

        try:

            await r2_client.head_object(url)

            return True

        except Exception:

            return False
```

### [TDD-WORKERS]-J · phase4_coordinator · Stops at `preview_ready`

**Fulfills PRD Requirement:** `[PRD-PIPELINE]` (Phase 4), `[PRD-HD5]`, `[PRD-HD6]`, `[PRD-FSM]`, `[PRD-AC-4]`, F-205, F-401


> **Disambiguation for the agent:** Coordinator IS the writer of the `composing → preview_ready` state UPDATE — this UPDATE is REQUIRED, not banned. Coordinator is NOT the enqueuer of `worker_export` — that is exclusively `app/api/routes/declaration.py` and `app/api/routes/retry_export.py`. The CI rule `ci/check_banned_patterns.py` blocks `arq.enqueue.*worker_export` inside coordinator code; it does NOT block the state UPDATE.


```python
import asyncio

  

async def phase4_coordinator(ctx, gen_id: str):

    """Pillar 3 & 5. Canonical 15s total duration, segment structure per `structure_template` (T1..T5 — see [TDD-BROLL]-C).

    Opt 3: LLM Prompt Pre-flight. Opt 1: Sequential Early-Exit. Opt 2: Fractional Render."""

    gen = await db.fetchrow(

        """SELECT isolated_png_url, refined_script, safe_scripts, selected_script_id,

                  motion_archetype_id, environment_preset_id, tts_language, product_brief, plan_tier, b_roll_plan, structure_template, strategy_card

           FROM generations WHERE gen_id = $1 AND status = 'funds_locked'""",

        gen_id

    )

    if not gen: return

    await db.execute("UPDATE generations SET status='rendering' WHERE gen_id=$1", gen_id)

    selected_script = gen["refined_script"] or gen["safe_scripts"][(gen["selected_script_id"] or 1) - 1]

    # 1. PARALLEL: Start TTS + Prompt Pre-Flight concurrently

    tts_task = asyncio.create_task(

        WorkerTTS(gateway=gateway).process(gen_id, selected_script["full_text"], gen["tts_language"])

    )

    prompt_preflight_task = asyncio.create_task(

        gateway.route(

            capability="llm",

            input_data={

                "system_prompt": "You are a master cinematographer. Convert the inputs into a highly dense, comma-separated camera and lighting prompt optimized for AI video models. Max 30 words.",

                "user_prompt": f"Product: {gen['product_brief']['product_name']}. Motion: {MOTION_NAMES[gen['motion_archetype_id']]}. Environment: {ENV_NAMES[gen['environment_preset_id']]}.",

                "gen_id": gen_id

            }

        )

    )

    try:

        tts_url, prompt_resp = await asyncio.gather(tts_task, prompt_preflight_task)

        optimized_i2v_prompt = prompt_resp.text

    except Exception as e:

        logger.error(f"phase4_coordinator prep failed {gen_id}: {e}")

        raise

    # 2. SEQUENTIAL EARLY-EXIT: Render Attempt 1 (9 seconds)

    i2v_worker = WorkerI2V(gateway=gateway)

    reflect_worker = WorkerReflect(gateway=gateway)

    i2v_url_1 = await i2v_worker.process(

        gen_id, gen["isolated_png_url"], optimized_i2v_prompt, duration=9, attempt=1

    )

    await db.execute("UPDATE generations SET status='reflecting' WHERE gen_id=$1", gen_id)

    try:

        # Check if Attempt 1 passes SSIM + Deformation gates

        selected_i2v = await reflect_worker.process(gen_id, [i2v_url_1], gen["isolated_png_url"])

        i2v_candidates = [i2v_url_1]

    except ReflectError:

        # 3. FALLBACK: Attempt 1 failed. Run Attempt 2.

        logger.info(f"Gen {gen_id} failed early-exit. Running I2V fallback.")

        i2v_url_2 = await i2v_worker.process(

            gen_id, gen["isolated_png_url"], optimized_i2v_prompt, duration=9, attempt=2

        )

        i2v_candidates = [i2v_url_1, i2v_url_2]

        try:

            selected_i2v = await reflect_worker.process(gen_id, [i2v_url_2], gen["isolated_png_url"])

        except ReflectError:

            # Both failed quality gates. Fallback to Attempt 2 to prevent pipeline death.

            selected_i2v = i2v_url_2

  

    await db.execute(

        """UPDATE generations SET tts_audio_url = $2, i2v_candidates = $3::jsonb, selected_i2v_url = $4

           WHERE gen_id = $1""",

        gen_id, tts_url, json.dumps(i2v_candidates), selected_i2v

    )

    # 4. COMPOSE: stitch segments per `structure_template` (T1..T5). CTA may be a clip (T1)
    #    or an FFmpeg-rendered text-card (T2..T5). See [TDD-VIDEO]-B and [TDD-BROLL]-H.

    await db.execute("UPDATE generations SET status='composing' WHERE gen_id=$1", gen_id)

    preview_url = await WorkerCompose().process(

        gen_id, selected_i2v, tts_url, gen["b_roll_plan"], gen["structure_template"],
        gen["product_brief"].get("benefit"), gen["plan_tier"],
        brand_color_primary=(gen["strategy_card"] or {}).get("brand_color_primary"),

    )

    await db.execute("UPDATE generations SET preview_url=$2, status='preview_ready' WHERE gen_id=$1", gen_id, preview_url)

    await cost_guard.check_post_hoc(gen_id)

    await sse_manager.push(gen_id, {"type": "state_change", "state": "preview_ready", "preview_url": preview_url})
```



---


> **[CONSISTENCY-FLAG: Worker process names]** Category 3C renames `adcreo-studio` → `adcreo-studio` and `adcreo-render` → `adcreo-render`. v3's `[TDD-WORKERS]` body contains the old names in: the permission matrix preamble, ARQ queue name strings (`_queue_name="adcreo-studio"`, `_queue_name="adcreo-render"`), and `phase4_coordinator` enqueue calls. **Apply find-replace during paste** so the worker bodies match the deployment topology defined in `[TDD-DEPLOYMENT]`. See `CONSISTENCY FLAGS` at end of document for the full list of occurrences identified.

---

# [TDD-BROLL] · B-Roll Selection & Composition Strategy (v4-Δ1)

**Status:** Proposed. Supersedes the placeholder logic embedded in `[TDD-WORKERS]-C2`, `[TDD-VIDEO]-A`, and the `broll_clips` schema in `[TDD-SCHEMA]`. **Fulfills:** `[PRD-FEATURES-PRODUCTION]` F-405, `[PRD-NON-NEGOTIABLES]` (Product-Visual First), `[PRD-DIFFS]` (controlled B-roll), `[PRD-HD4]`. **Constraints honored:** deterministic, no runtime LLM, no runtime GPU, no external API in selection path, no new workers, single-server execution.

---

## [TDD-BROLL]-A · Product Goal

The B-roll subsystem provides **role-aware atmospheric framing** for the 15s smart-stitch render. The product hero (Worker-I2V output) carries the brand and product narrative; B-roll provides the surrounding emotional, contextual, and conversion surfaces — hook attention, context extension, and CTA backdrop. It exists to make Adcreo's output **coherent and India-aware**, not merely "AI-generated stock-matched."

The system is intentionally deterministic and curated: 25–30 hand-selected clips at launch, role-tagged, mood-tagged, season-tagged, brand-tier-tagged, selected by SQL filters and total-ordered for reproducibility. No embeddings. No prompt-router. No runtime model calls. The intelligence lives in the **metadata + the 5 structural templates**, not in inference.

---

## [TDD-BROLL]-B · Architecture Summary

```
Worker-STRATEGIST
  ├─ picks structure_template ∈ {T1..T5}  (frozen routing dict)
  ├─ resolves (framework_angle, category, brand_tier, active_season) → template
  └─ calls BRollPlanner.plan(template, angle, category, brand_tier, user_id, active_season)
        └─ returns { template, hook, context, cta }   # v5-correction: object-shaped per [TDD-BROLL]-G/K
              ├─ template : T1..T5  (echoed back so Worker-COMPOSE has a single source)
              ├─ hook     : 1 clip (always — every template guarantees a hook)
              ├─ context  : clip | None  (None for T1, T2, T5; non-null for T3, T4)
              └─ cta      : clip | None  (None for T2, T3, T4, T5 → Worker-COMPOSE renders text-card)

Worker-COMPOSE
  ├─ branches on structure_template
  ├─ if cta is None → renders text-card via FFmpeg drawtext + gradient backdrop
  └─ FFmpeg filter_complex stitches per the template timeline
```

The planner is a single deterministic SQL call (`asyncpg`, ~10ms). No new workers, no new external IO, no FSM changes.

---

## [TDD-BROLL]-C · The 5 Structural Templates

All templates sum to canonical 15.000s. Template selection is governed by `TEMPLATE_BY_CONTEXT` — a frozen Python dict, CI-locked, mirrored in `app/broll/templates.py`.

### T1 · Bookended (Default Sensory)

**When:** `emotion` angle · sensory categories (`d2c_beauty`, `packaged_food`) **Timing:** 3s hook B-roll → 9s I2V product → 3s CTA B-roll

|Segment|Time|Source|
|---|---|---|
|Hook|0.0–3.0s|`broll_clips` WHERE role='hook'|
|Body|3.0–12.0s|Worker-I2V|
|CTA|12.0–15.0s|`broll_clips` WHERE role='cta_bg'|

### T2 · Product-Dominant (Premium)

**When:** `brand_tier='premium'` OR `brand_tier='luxury'`, any angle except `conversion` **Timing:** 2s hook B-roll → 11s I2V product → 2s CTA text-card

|Segment|Time|Source|
|---|---|---|
|Hook|0.0–2.0s|`broll_clips` WHERE role='hook'|
|Body|2.0–13.0s|Worker-I2V|
|CTA|13.0–15.0s|FFmpeg text-card (brand-color gradient + price/URL)|

### T3 · Problem-Story (Functional)

**When:** `logic` angle · functional categories (supplements, electronics, home goods) **Timing:** 3s hook B-roll → 4s context B-roll → 5s I2V product → 3s CTA text-card

|Segment|Time|Source|
|---|---|---|
|Hook|0.0–3.0s|`broll_clips` WHERE role='hook'|
|Context|3.0–7.0s|`broll_clips` WHERE role='context'|
|Body|7.0–12.0s|Worker-I2V|
|CTA|12.0–15.0s|FFmpeg text-card|

### T4 · Festive Moment (Seasonal Override)

**When:** `active_season IS NOT NULL` at strategy time, any angle/category/tier **Timing:** 3s hook B-roll (festive) → 4s context B-roll (festive) → 5s I2V product → 3s CTA text-card

|Segment|Time|Source|
|---|---|---|
|Hook|0.0–3.0s|`broll_clips` WHERE role='hook' AND $season=ANY(seasonality_tags)|
|Context|3.0–7.0s|`broll_clips` WHERE role='context' AND $season=ANY(seasonality_tags)|
|Body|7.0–12.0s|Worker-I2V|
|CTA|12.0–15.0s|FFmpeg text-card (festive accent color)|

T4 **overrides** T1/T2/T3 when an active season is in scope. Active seasons are resolved by Worker-STRATEGIST from the `seasons` lookup table (`active_from`, `active_to` window check against `NOW()`).

### T5 · Offer-Forward (Conversion-Heavy)

**When:** `conversion` angle · mass-tier brands OR explicit discount campaigns **Timing:** 2s hook B-roll → 10s I2V product → 3s CTA text-card (extended)

|Segment|Time|Source|
|---|---|---|
|Hook|0.0–2.0s|`broll_clips` WHERE role='hook' AND mood_energy='intense'|
|Body|2.0–12.0s|Worker-I2V|
|CTA|12.0–15.0s|FFmpeg text-card (price + offer + urgency stack)|

### Template Routing (frozen)

```python
# app/broll/templates.py
# Precedence: (1) festive override > (2) brand_tier > (3) angle/category

TEMPLATE_BY_CONTEXT: dict[tuple[str, str, str], str] = {
    # (angle, category_class, brand_tier) → template_id
    ("emotion",    "sensory",    "mass"):    "T1",
    ("emotion",    "sensory",    "premium"): "T2",
    ("emotion",    "sensory",    "luxury"):  "T2",
    ("emotion",    "functional", "mass"):    "T1",
    ("emotion",    "functional", "premium"): "T2",
    ("logic",      "sensory",    "mass"):    "T3",
    ("logic",      "functional", "mass"):    "T3",
    ("logic",      "functional", "premium"): "T2",
    ("conversion", "sensory",    "mass"):    "T5",
    ("conversion", "functional", "mass"):    "T5",
    ("conversion", "sensory",    "premium"): "T5",
    ("conversion", "functional", "premium"): "T5",
    # luxury × conversion is intentionally absent → falls back to T2
}
DEFAULT_TEMPLATE = "T1"
FESTIVE_OVERRIDE_TEMPLATE = "T4"  # applied when active_season resolves
```

---

## [TDD-BROLL]-D · Role Semantics

Three roles. Each clip is exactly one role. Role is the **primary filter** in selection — non-negotiable, never overridden by mood or season.

| Role      | Purpose                                | Required Properties                                                        |
| --------- | -------------------------------------- | -------------------------------------------------------------------------- |
| `hook`    | Stop the scroll in first 2–3s          | High motion (`mood_energy='active'\|'intense'`), distinctive opening frame |
| `context` | Extend the product story between beats | Medium motion, supportive composition, narrative-friendly                  |
| `cta_bg`  | Backdrop for text overlay (T1 only)    | Low motion (`mood_energy='calm'`), `negative_space_score ≥ 7`              |

A clip CANNOT serve multiple roles. Curation discipline > schema flexibility. If a clip "could work as either hook or context," it gets the role its best 1-second moment supports.

---

## [TDD-BROLL]-E · Minimum Clip Metadata (v1)

Extends the `broll_clips` table from `[TDD-SCHEMA]`. All columns NOT NULL with CHECK constraints for enum-like discipline.

```sql
ALTER TABLE broll_clips
  ADD COLUMN role VARCHAR(15) NOT NULL
    CHECK (role IN ('hook', 'context', 'cta_bg')),
  ADD COLUMN mood_energy VARCHAR(10) NOT NULL
    CHECK (mood_energy IN ('calm', 'active', 'intense')),
  ADD COLUMN mood_temperature VARCHAR(10) NOT NULL
    CHECK (mood_temperature IN ('warm', 'cool', 'neutral')),
  ADD COLUMN negative_space_score SMALLINT NOT NULL
    CHECK (negative_space_score BETWEEN 0 AND 10),
  ADD COLUMN seasonality_tags TEXT[] NOT NULL DEFAULT '{}',
  ADD COLUMN brand_tier_fit TEXT[] NOT NULL DEFAULT '{mass,premium,luxury}';

-- Belt-and-braces: a cta_bg clip MUST have high negative space
ALTER TABLE broll_clips
  ADD CONSTRAINT chk_cta_negative_space
    CHECK (role <> 'cta_bg' OR negative_space_score >= 7);

-- Partial index for the planner's hot path
CREATE INDEX idx_broll_role_category_tier
  ON broll_clips (role, category, brand_tier_fit)
  WHERE is_active = TRUE;

CREATE INDEX idx_broll_seasonality
  ON broll_clips USING GIN (seasonality_tags)
  WHERE is_active = TRUE AND cardinality(seasonality_tags) > 0;
```

**Field reference:**

|Column|Type|Purpose|
|---|---|---|
|`role`|enum-like|Primary selection filter|
|`mood_energy`|enum-like|calm / active / intense — matched to angle|
|`mood_temperature`|enum-like|warm / cool / neutral — matched to angle|
|`negative_space_score`|0–10|CTA legibility constraint|
|`seasonality_tags`|text[]|e.g. `{'diwali','wedding'}`; empty = year-round|
|`brand_tier_fit`|text[]|e.g. `{'mass','premium'}`; defaults to all three|

The existing `archetype` column is retained as **secondary descriptive metadata** for human curation audits; it is no longer the primary routing key.

### Rotation Table (new)

```sql
CREATE TABLE broll_clip_usage (
  user_id   UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  clip_id   VARCHAR(20) NOT NULL REFERENCES broll_clips(clip_id) ON DELETE CASCADE,
  gen_id    UUID NOT NULL REFERENCES generations(gen_id) ON DELETE CASCADE,
  used_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, clip_id, gen_id)
);
CREATE INDEX idx_broll_usage_user_recent
  ON broll_clip_usage (user_id, used_at DESC);
```

### Seasons Lookup (new)

```sql
CREATE TABLE seasons (
  season_tag    VARCHAR(30) PRIMARY KEY,
  display_name  VARCHAR(60) NOT NULL,
  active_from   DATE NOT NULL,
  active_to     DATE NOT NULL,
  is_active     BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT chk_season_window CHECK (active_from <= active_to)
);
-- Seeded examples: diwali, holi, wedding_season, monsoon, new_year, raksha_bandhan
```

Worker-STRATEGIST queries: `SELECT season_tag FROM seasons WHERE is_active AND NOW()::DATE BETWEEN active_from AND active_to LIMIT 1`. If a row returns, `active_season` is set and T4 takes precedence.

### Generations Table Addition

```sql
ALTER TABLE generations
  ADD COLUMN structure_template VARCHAR(5)
    CHECK (structure_template IN ('T1','T2','T3','T4','T5')),
  ADD COLUMN active_season VARCHAR(30) REFERENCES seasons(season_tag),
  ADD COLUMN b_roll_performance_signal JSONB;  -- reserved, nullable, v2-populated
```

---

## [TDD-BROLL]-F · The Two Kept Enhancements

### F.1 Seasonality Tags

`seasonality_tags TEXT[]` on `broll_clips`. Empty array means year-round (default). Non-empty means the clip is _only_ eligible when an `active_season` is in scope AND that season tag is in the array.

Behavior:

- **No active season:** planner ignores `seasonality_tags`; year-round clips selected as normal.
- **Active season resolved:** template switches to **T4**; planner adds `$active_season = ANY(seasonality_tags)` filter; year-round clips become **ineligible** during festive windows for hook/context slots (CTA text-card adopts festive accent color).
- **Season exists but no matching clips:** planner falls back to year-round library; logs warning; T4 still applies for the text-card accent. Never raises.

Seasons table is the single source of truth for active windows. Operations/marketing team flips `is_active` in the `seasons` table to manually disable a season early or extend it. No code deploy needed.

### F.2 Brand Tier

`brand_tier_fit TEXT[]` on `broll_clips` (which tiers the clip fits). New column on `user_style_profiles`: `brand_tier VARCHAR(10) CHECK (brand_tier IN ('mass','premium','luxury')) DEFAULT 'mass'`.

Behavior:

- Brand tier is set per-brand once during onboarding (or inferred from price-band + style heuristics during Phase 1 brand extraction — separate flow).
- Worker-STRATEGIST reads `user_style_profiles.brand_tier` and includes it in the template routing key.
- Planner SQL adds `$brand_tier = ANY(brand_tier_fit)` filter to every clip selection query.
- Default `brand_tier_fit = {mass,premium,luxury}` means new clips are tier-agnostic until intentionally restricted.

Brand tier influences **template choice** (T2 for premium, T5 default for mass-conversion) AND **clip eligibility** (a luxury-only clip won't surface for a mass brand). Two layers, one column each.

---

## [TDD-BROLL]-G · Selection Logic in Plain English

When Worker-STRATEGIST is composing the Strategy Card:

1. **Resolve context:** read `framework_angle`, `category`, `brand_tier` (from `user_style_profiles`), and `active_season` (from `seasons` table).
2. **Pick template:** if `active_season` is non-null → **T4**. Else look up `(angle, category_class, brand_tier)` in `TEMPLATE_BY_CONTEXT` → falls back to `T1` if absent.
3. **Determine required slots:** each template declares which roles it needs — T1 needs `hook + cta_bg`, T2 needs `hook` only, T3 needs `hook + context`, T4 needs `hook + context` (both festive), T5 needs `hook` only.
4. **For each required slot, call planner:** `BRollPlanner.pick_one(role, category, brand_tier, mood_target, active_season, user_id)`. The planner runs **one SQL query**:
    - filter by `role`, `category`, `brand_tier_fit`, safety flags, `is_active`
    - if `active_season`: AND `season = ANY(seasonality_tags)`
    - ORDER BY:
        - mood match (energy + temperature exact match first, partial match next, mismatch last)
        - rotation (clips NOT used by this `user_id` in last 3 generations first)
        - archetype priority (tiebreak using existing `ARCHETYPE_BY_ANGLE`)
        - `clip_id ASC` (final total-order tiebreak — guarantees determinism)
    - `LIMIT 1`
5. **Compose plan:** return `{template: 'T3', hook: clip_a, context: clip_b, cta: None}`. `cta: None` is the signal to Worker-COMPOSE that this template uses a text-card.
6. **Write to `generations.b_roll_plan` and `generations.structure_template`.**
7. **Log usage:** insert `(user_id, clip_id, gen_id)` into `broll_clip_usage` for every clip in the plan, atomically with the plan write.

Same inputs always produce the same output (rotation history is part of the input). Total runtime: one query per slot, ≤ 3 slots, ~30ms total.

---

## [TDD-BROLL]-H · Worker-COMPOSE Branch Logic

Worker-COMPOSE reads `structure_template` from the generation row and branches:

```python
async def process(self, gen_id, i2v_url, tts_url, b_roll_plan, ...):
    template = b_roll_plan["template"]
    segments = await self._build_segments(template, b_roll_plan, ...)
    # segments = list of (kind, path | render_spec, duration)
    return await self._render_filter_complex(segments, tts_url, ...)
```

Text-card rendering uses FFmpeg's existing `drawtext` capability (already used for SGI watermark per F-403) over a 2–3-second gradient backdrop generated via `color=` source filter. Brand color comes from `user_style_profiles.brand_color_primary` (added in v4-Δ1 — a 7-char hex string; see `[TDD-SCHEMA]`). When that column is NULL (cold-start users; brands that haven't run onboarding), Worker-COMPOSE falls back to a neutral charcoal `#1A1A1A` which is legible against any product image. No new dependencies.

**Inconsistency resolution:** the empty-plan failure case in current `[TDD-VIDEO]-B` (`raise ComposeError("Missing required B-Roll clips for Hook and CTA")`) is removed. Every template guarantees a renderable plan: hook is always a clip; CTA is either a clip (T1) or a text-card (T2/T3/T4/T5). The planner cannot return a state where compose has no path forward. If hook clip resolution returns empty for a `(category, brand_tier)` pair, the seed-time CI check has already failed — deploy is blocked before this can occur in production.

---

## [TDD-BROLL]-I · Intentionally Deferred to v2

The following are explicitly **not** in v1 scope. Schema slots are reserved where useful; logic is absent.

|Capability|Status|Reason|
|---|---|---|
|Performance feedback loop|Schema reserved (`b_roll_performance_signal JSONB`), unpopulated|Requires post-launch attribution data; meaningless without 4–6 weeks of run data|
|Cross-segment color harmony|Not built|Requires LUT/color analysis per I2V output; runtime cost not justified for v1|
|Audio compatibility profiling|Not built|TTS dominates the audio track; ambient clip audio is currently muted at compose time|
|Camera-move taxonomy|Not built|Curator judgment captured in `archetype` is sufficient for 25–30 clips|
|pgvector / embedding-based selection|Explicitly rejected|Library size makes deterministic dict + filters strictly superior|
|Dynamic per-ad timing curves|Explicitly rejected|5 templates cover the design space without runtime variability|
|Brand-palette filtering of clips|Deferred|`brand_tier_fit` provides 80% of the value at 10% of the complexity|
|User-uploaded custom B-roll|Deferred|Curation discipline > user variance for v1|

---

## [TDD-BROLL]-J · CI Guards

Two new checks, both run in the existing seed-time + pre-deploy pipeline:

1. **Library coverage check** (`ci/broll_coverage_check.py`): For every `(angle, category, brand_tier)` triple resolvable via `TEMPLATE_BY_CONTEXT`, assert that the required roles for the resolved template have ≥1 active clip in `broll_clips`. Blocks deploy on any uncovered combination.
2. **Strategist sandbox extension:** existing `ci/strategist_sandbox_check.py` already extends to `app/broll/`. Extend to also forbid imports of any clip-selection ML library (`sentence_transformers`, `chromadb`, `faiss`) — defense against future drift toward embedding-based selection inside the planner.

---

## [TDD-BROLL]-K · Invariants

1. **Determinism:** same `(framework_angle, category, brand_tier, user_id, active_season)` → same `b_roll_plan`. Rotation history is treated as part of the input.
2. **Role purity:** a clip's role is fixed at curation time and never overridden by selection logic.
3. **Safety preserved:** existing `chk_broll_safety` constraint untouched. `excludes_faces/hands/locations` remain hard invariants.
4. **Bounded output:** `b_roll_plan` has at most 1 hook + 1 context + 1 cta_bg clip — three clips maximum, often fewer (T2/T5 ship only a hook). `chk_b_roll_plan_shape` on `generations.b_roll_plan` is **rewritten** in v4-Δ1 from the v3 array form to the new object form `{template, hook, context, cta}` (see `[TDD-SCHEMA]` and `[TDD-MIGRATIONS]` step 22). The bounded-clip invariant is now enforced structurally by the JSONB object shape itself plus role purity, not by an array-length check.
5. **No empty-plan crashes:** every template path produces a renderable compose plan. CI coverage check enforces this at deploy time.
6. **Compose path is template-deterministic:** Worker-COMPOSE branch logic is exhaustive over `T1..T5`; an unrecognized template ID raises before R2 downloads to fail fast and cheap.

---

---


## [TDD-VIDEO] · Video Composition & Provenance

**Fulfills PRD Requirement:** `[PRD-PIPELINE]` (Phase 4), `[PRD-LEGAL]`, `[PRD-UX-FREEZE-SCREENS]` (HD-5).

This layer governs the final assembly of the MP4 artifact. Because L2 constraints (10MB upload) and inference costs are paramount, video generation is fractional. We generate only the core product motion (9s) via expensive AI (I2V) and bookend it with pre-rendered, static B-Roll (6s) from the database.

### [TDD-VIDEO]-A · The 15-Second Smart-Stitch Timeline

Total Canonical Duration: **15.000 seconds**. *(v4-Δ1: five template-specific timelines T1..T5 are authoritatively defined in `[TDD-BROLL]-C`; each sums to 15.000s. Worker-COMPOSE branches per `structure_template`.)*

**Template T1 (Bookended, default sensory)** shown below for backward continuity with the v3 contract. T2/T3/T4/T5 timelines live in `[TDD-BROLL]-C` and are not duplicated here to keep one source of truth.

|Segment|Time|Source|Content|Cost|
|---|---|---|---|---|
|**Hook**|0.0s – 3.0s|DB `broll_clips` WHERE `role='hook'`|Fast atmospheric motion (e.g., splashing liquid, fabric drape)|₹0.00|
|**Body**|3.0s – 12.0s|`Worker-I2V` (Fal.ai)|AI-Generated product motion based on brief|~₹7.00|
|**CTA**|12.0s – 15.0s|DB `broll_clips` WHERE `role='cta_bg'` AND `negative_space_score >= 7`|Low-motion background for price/logo overlay|₹0.00|

For T2 (Product-Dominant, premium), T3 (Problem-Story, functional/logic), T4 (Festive Moment, seasonal override), and T5 (Offer-Forward, conversion) timelines, see `[TDD-BROLL]-C`. In T2..T5 the CTA segment is an FFmpeg-rendered text-card over a brand-color gradient, not a clip — Worker-COMPOSE branches per template.

### [TDD-VIDEO]-B · Worker-COMPOSE FFmpeg Logic (F-406)

`Worker-COMPOSE` executes locally on the ARQ worker. It takes the I2V video file, the TTS audio track, and the structured `b_roll_plan` (`{template, hook, context, cta}`), and uses an FFmpeg `filter_complex` graph to stitch, grade, and watermark. **v4-Δ1:** branches on `structure_template` (T1..T5); the CTA segment may be a clip (T1) or an FFmpeg-rendered text-card over a brand-color gradient (T2/T3/T4/T5). See `[TDD-BROLL]-H` for the branch contract.

```
import asyncio
import logging

logger = logging.getLogger(__name__)

class WorkerCompose:
    """
    F-406: Assembles the 15s fractional render.
    Applies LUT color grading based on product benefit.
    Burns in the 'AI Generated Content' watermark (IT Rules 2026).
    v4-Δ1: template-driven segment graph; text-card CTA path for T2/T3/T4/T5.
    """
    CANONICAL_DURATION_S = 15.0
    DEFAULT_BRAND_COLOR = "#1A1A1A"  # v4-Δ1: neutral charcoal fallback when brand_color_primary is NULL

    async def process(self, gen_id: str, i2v_url: str, tts_url: str, b_roll_plan: dict, structure_template: str, benefit: str, plan_tier: str, brand_color_primary: str | None = None) -> str:
        # 1. Prepare local temporary file paths
        i2v_path = f"/tmp/{gen_id}_i2v.mp4"
        tts_path = f"/tmp/{gen_id}_tts.mp3"
        output_path = f"/tmp/{gen_id}_preview.mp4"

        # 2. Download I2V + TTS (always needed regardless of template)
        await asyncio.to_thread(self._write_file, i2v_path, await self._download_from_r2(i2v_url))
        await asyncio.to_thread(self._write_file, tts_path, await self._download_from_r2(tts_url))

        # v4-Δ1: Template-driven segment build per [TDD-BROLL]-H.
        # Every template guarantees a renderable plan: hook is always a clip; CTA is a clip (T1)
        # or a text-card generated via _render_cta_text_card (T2/T3/T4/T5). The CI coverage check
        # ([TDD-BROLL]-J) enforces hook-clip availability at deploy time so this method never
        # has to handle "no hook" in production. If the assertion fires anyway, fail loudly.
        if not b_roll_plan or not b_roll_plan.get("hook"):
            raise ComposeError(
                f"b_roll_plan missing hook clip for gen_id={gen_id} template={structure_template}. "
                "CI coverage check should have caught this at deploy time — escalate."
            )
        brand_color = brand_color_primary or self.DEFAULT_BRAND_COLOR
        segments = await self._build_segments_for_template(
            structure_template, b_roll_plan, i2v_path, brand_color, benefit
        )

        # 3. Select Color Grade (LUT)
        lut_file = self._select_lut(benefit)

        # 4. Construct FFmpeg filter_complex from `segments` (variable-arity).
        # The graph generalizes the v3 fixed 3-stream concat: n=len(segments), each segment
        # contributes one input stream. Audio remains a single TTS track padded/trimmed to 15s.
        n = len(segments)
        input_args = []
        concat_inputs = ""
        for idx, (_kind, path, _dur) in enumerate(segments):
            input_args += ["-i", path]
            concat_inputs += f"[{idx}:v]"
        # Audio input goes last
        input_args += ["-i", tts_path]
        audio_idx = n  # 0-based index of TTS in the input list

        filter_graph = (
            f"{concat_inputs}concat=n={n}:v=1:a=0[concat_v];"
            f"[concat_v]lut3d={lut_file}[graded_v];"
            f"[graded_v]drawtext=text='AI Generated Content':fontsize=14:fontcolor=white@0.7:x=10:y=h-30[watermarked_v];"
            f"[{audio_idx}:a]atrim=end={self.CANONICAL_DURATION_S},apad=whole_dur={self.CANONICAL_DURATION_S}[padded_a]"
        )

        cmd = [
            "ffmpeg", "-y",
            *input_args,
            "-filter_complex", filter_graph,
            "-map", "[watermarked_v]", "-map", "[padded_a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(self.CANONICAL_DURATION_S),
            output_path,
        ]

        # 5. Execute Subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise ComposeError(f"FFmpeg composition failed: {stderr.decode()[:500]}")

        # 6. Upload final composed preview to R2
        return await self._upload_to_r2(
            gen_id, "compose/preview_15s.mp4",
            await asyncio.to_thread(self._read_file, output_path)
        )

    def _select_lut(self, benefit: str) -> str:
        """Matches the product's core benefit to a pre-defined color grade."""
        luts = {
            "premium": "luts/premium_warm.cube",
            "trending": "luts/trending_vivid.cube",
            "gift": "luts/gift_festive.cube",
            "natural": "luts/natural_green.cube",
        }
        return luts.get(benefit, "luts/neutral_balanced.cube")

    # v4-Δ1: returns ordered list of (kind, path_or_render_spec, duration_s) segments for the given
    # template per [TDD-BROLL]-C. For T2/T3/T4/T5 the CTA segment is materialized via
    # _render_cta_text_card and the resulting local .mp4 path is returned just like a clip.
    async def _build_segments_for_template(self, structure_template: str, b_roll_plan: dict,
                                           i2v_path: str, brand_color: str, benefit: str) -> list[tuple]:
        hook_clip = b_roll_plan["hook"]
        ctx_clip = b_roll_plan.get("context")
        cta_clip = b_roll_plan.get("cta")

        # Download every required B-roll clip (hook always; context/cta conditionally).
        hook_path = f"/tmp/{hook_clip['clip_id']}.mp4"
        await asyncio.to_thread(self._write_file, hook_path,
                                await self._download_from_r2(hook_clip["r2_url"]))

        if structure_template == "T1":
            # Bookended: 3s hook + 9s I2V + 3s CTA clip
            cta_path = f"/tmp/{cta_clip['clip_id']}.mp4"
            await asyncio.to_thread(self._write_file, cta_path,
                                    await self._download_from_r2(cta_clip["r2_url"]))
            return [("hook", hook_path, 3.0), ("i2v", i2v_path, 9.0), ("cta", cta_path, 3.0)]

        if structure_template == "T2":
            # Product-Dominant: 2s hook + 11s I2V + 2s text-card CTA
            cta_path = await self._render_cta_text_card(brand_color, price_text="", offer_text=None, duration_s=2.0)
            return [("hook", hook_path, 2.0), ("i2v", i2v_path, 11.0), ("cta_card", cta_path, 2.0)]

        if structure_template == "T3":
            # Problem-Story: 3s hook + 4s context + 5s I2V + 3s text-card CTA
            ctx_path = f"/tmp/{ctx_clip['clip_id']}.mp4"
            await asyncio.to_thread(self._write_file, ctx_path,
                                    await self._download_from_r2(ctx_clip["r2_url"]))
            cta_path = await self._render_cta_text_card(brand_color, price_text="", offer_text=None, duration_s=3.0)
            return [("hook", hook_path, 3.0), ("context", ctx_path, 4.0),
                    ("i2v", i2v_path, 5.0), ("cta_card", cta_path, 3.0)]

        if structure_template == "T4":
            # Festive Moment: 3s hook(festive) + 4s context(festive) + 5s I2V + 3s text-card CTA(festive accent)
            ctx_path = f"/tmp/{ctx_clip['clip_id']}.mp4"
            await asyncio.to_thread(self._write_file, ctx_path,
                                    await self._download_from_r2(ctx_clip["r2_url"]))
            cta_path = await self._render_cta_text_card(brand_color, price_text="", offer_text=None, duration_s=3.0)
            return [("hook", hook_path, 3.0), ("context", ctx_path, 4.0),
                    ("i2v", i2v_path, 5.0), ("cta_card", cta_path, 3.0)]

        if structure_template == "T5":
            # Offer-Forward: 2s hook + 10s I2V + 3s text-card CTA (urgency stack)
            cta_path = await self._render_cta_text_card(brand_color, price_text="", offer_text="LIMITED TIME", duration_s=3.0)
            return [("hook", hook_path, 2.0), ("i2v", i2v_path, 10.0), ("cta_card", cta_path, 3.0)]

        # [TDD-BROLL]-K invariant 6: unknown template is a hard-fail before R2 downloads.
        raise ComposeError(f"Unknown structure_template={structure_template!r}; expected T1..T5.")

    async def _render_cta_text_card(self, brand_color: str, price_text: str,
                                    offer_text: str | None, duration_s: float) -> str:
        """v4-Δ1: Generates a `duration_s` CTA text-card via FFmpeg `color=` source filter + `drawtext`.
        Uses the same drawtext pattern as the F-403 SGI watermark — no new dependencies. Returns
        the local .mp4 path. See [TDD-BROLL]-H.

        The implementation is a single ffmpeg invocation:
            ffmpeg -y -f lavfi -i color=c=<brand_color>:s=1080x1920:d=<duration_s> \
                   -vf "drawtext=text='<offer_text>':...:y=h/2" \
                   -c:v libx264 -t <duration_s> /tmp/<uuid>.mp4
        """
        import uuid as _uuid
        out_path = f"/tmp/cta_{_uuid.uuid4().hex[:12]}.mp4"
        # Strip leading '#' if present for ffmpeg color spec
        color_spec = brand_color.lstrip("#")
        text = offer_text if offer_text else (price_text or "")
        # Escape single quotes for drawtext
        text_escaped = text.replace("'", r"\'") if text else ""
        vf = (
            f"drawtext=text='{text_escaped}':fontsize=72:fontcolor=white:"
            f"x=(w-text_w)/2:y=(h-text_h)/2"
        ) if text else "null"
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"color=c=0x{color_spec}:s=1080x1920:d={duration_s}:r=30",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-t", str(duration_s),
            out_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise ComposeError(f"CTA text-card render failed: {stderr.decode()[:500]}")
        return out_path
```

### [TDD-VIDEO]-C · C2PA Cryptographic Provenance (F-407)

**Fulfills PRD Requirement:** `[PRD-LEGAL]`, `[PRD-EXPORT]`. To comply with IT Rules 2026, the final exported video MUST contain cryptographic metadata proving it is AI-generated and linking it back to the specific user session. This is handled exclusively by `Worker-EXPORT` using the Rust `c2patool` binary.

1. **Manifest Generation:** Worker-EXPORT dynamically writes a `manifest.json` file to `/tmp/`.
    
2. **Assertions:** The manifest includes the `gen_id`, `user_id`, and a strict `action: "c2pa.created.ai_generation"` assertion.
    
3. **Execution:** The binary is called via subprocess.
    
    - `c2patool /tmp/square.mp4 --output /tmp/square_signed.mp4 --manifest /tmp/manifest.json`
        
4. **Validation:** If `c2patool` returns a non-zero exit code, `Worker-EXPORT` raises `C2PASignError`, which trips the DLQ and refunds the user. **Unsigned videos are never returned to the client.**

---


---


## [TDD-API] · State Management & API Design

**Fulfills PRD Requirement:** `[PRD-HD1]`, `[PRD-HD2]`, `[PRD-HD3]`, `[PRD-HD4]`, `[PRD-HD5]`, `[PRD-HD6]`, `[PRD-FLOW]`, `[PRD-FLOW-INVARIANTS]`, `[PRD-IDEMPOTENCY]`, `[PRD-AC]`, `[PRD-FSM]`, `[PRD-PRETOPUP]`, `[PRD-PAYMENT-FSM]`, `[PRD-ERROR-MATRIX]`

The L2 FastAPI surface is the canonical authority for all state transitions the client can trigger. Every route that mutates state is wrapped with `@idempotent` (Redis DB5, 300s TTL, 2xx-only caching), gated by a per-action advisory lock (`actlock:{gen_id}:{action}`), and terminates in a state-guarded UPDATE.

### [TDD-API]-A · Canonical Endpoint Map

|Method|Path|Auth|Idempotency-Key|Action|Allowed States|
|---|---|---|---|---|---|
|POST|`/api/generations`|JWT|required|Create gen, enqueue Phase 1|n/a (creates)|
|GET|`/api/generations/{gen_id}`|JWT|n/a|Hydrate gen state|any|
|POST|`/api/generations/{gen_id}/advance`|JWT|required|HD-2 → HD-3 advance|`brief_ready`|
|POST|`/api/generations/{gen_id}/selections`|JWT|required|Set motion/env/lang|`brief_ready`|
|POST|`/api/generations/{gen_id}/regenerate`|JWT|required|Chip change → re-run Phase 2|`scripts_ready`|
|POST|`/api/generations/{gen_id}/chat`|JWT|required|5-stage chain refinement|`scripts_ready`|
|POST|`/api/generations/{gen_id}/edit-back`|JWT|required|HD-4 [Edit] NULL downstream|`strategy_preview`|
|POST|`/api/generations/{gen_id}/approve-strategy`|JWT|required|Lua lock + Phase 4 dispatch|`strategy_preview`|
|POST|`/api/generations/{gen_id}/declaration`|JWT|required|Capture provenance + enqueue worker_export|`preview_ready`|
|POST|`/api/generations/{gen_id}/retry-export`|JWT|required (monotonic)|9-step atomic retry chain|`failed_export`|
|POST|`/api/wallet/topup`|JWT|required|Razorpay order create|n/a|
|POST|`/api/webhook/razorpay`|HMAC|n/a|Origin-preserving restoration|any user gens in `awaiting_funds`|
|POST|`/api/grievance`|JWT|n/a|IT Rules 2026 takedown ticket|any|
|GET|`/api/sse/{gen_id}`|JWT (cookie)|n/a|SSE subscription|any|


Peripheral Routes:
- `/grievance` is a static route
- No FSM interaction
- No dependency on generation state

### [TDD-API]-B · GET /api/generations/{gen_id} — Hydration Endpoint

**Fulfills PRD Requirement:** `[PRD-FLOW-INVARIANTS]`, `[PRD-IDEMPOTENCY]`, `[PRD-AC-GLOBAL]` G5 Hydration is the single source of truth on mount and on every SSE reconnect. Response shape is the canonical GenerationState interface (`[TDD-TYPES]-A`). No mutations.

```
@router.get("/api/generations/{gen_id}", response_model=StatusResponse)
async def get_status(gen_id: str, user=Depends(get_current_user), db=Depends(get_db)):
    """
    Polling fallback / Initial hydration for screens.
    Strictly Read-Only. Used to resolve FSM state on UI refresh.
    """
    
    # ── STEP 1: Fetch FSM State ──
    gen = await db.fetchrow(
        "SELECT status, error_code, confidence_score FROM generations WHERE gen_id=$1 AND user_id=$2",
        gen_id, user.id
    )
    
    # ── STEP 2: Guard & Return ──
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
        
    return {
        "status": gen["status"],
        "error_code": gen["error_code"],
        "confidence_score": gen["confidence_score"]
    }
```

### [TDD-API]-C · POST /api/generations/{gen_id}/chat — 5-Stage Canonical Chain

**Fulfills PRD Requirement:** `[PRD-COPILOT]`, F-207, F-603, `[PRD-ERROR-MAP]` Implementation of `[TDD-CHAT-CHAIN]`. The `chain_stages_traversed` list is logged for CI assertion.

```
@router.post("/api/generations/{gen_id}/chat") 
@idempotent(ttl=300, action_key="chat", cache_only_2xx=True)
async def chat(
    gen_id: UUID, req: ChatRequest, request: Request, 
    idempotency_key: str = Header(..., alias="Idempotency-Key"), 
    user=Depends(get_current_user)
): 
    """5-stage canonical chain. Cross-tab safe via actlock fence."""
    
    # ── STEP 1: Distributed Lock (Prevent Double Clicks) ──
    lock_key = f"actlock:{gen_id}:chat" 
    acquired = await redis_db5.set(lock_key, "1", nx=True, ex=10)
    if not acquired:
        raise HTTPException(409, detail={"error_code": "ECM-012"})
        
    stages_traversed = []
    
    try:
        # ── STEP 2: Pre-chain state & Limit Guard ──
        gen = await db.fetchrow(
            """SELECT status, chat_turns_used, refined_script, safe_scripts, 
               selected_script_id, product_brief, tts_language, plan_tier 
               FROM generations WHERE gen_id=$1 AND user_id=$2 FOR UPDATE""", 
            gen_id, user["user_id"]
        )
        if not gen: raise HTTPException(404)
        if gen["status"] != "scripts_ready": raise HTTPException(409, detail={"error_code": "ECM-012"})
        if gen["chat_turns_used"] >= 3: raise HTTPException(429, detail={"error_code": "ECM-008"})
            
        # ── STEP 3: Compliance & Cost Gates ──
        stages_traversed.append("compliance_gate") 
        c_result = await compliance_gate.check_input(req.message)
        if not c_result.safe: raise HTTPException(400, detail={"error_code": "ECM-011"})
            
        stages_traversed.append("cost_guard_pre") 
        pre = await cost_guard.pre_check(str(gen_id), 0.08, gen["plan_tier"])
        if not pre.ok: raise HTTPException(429, detail={"error_code": "ECM-009"})
            
        # ── STEP 4: LLM Generation (Routed via Gateway) ──
        stages_traversed.append("llm") 
        current = gen["refined_script"] or gen["safe_scripts"][(gen["selected_script_id"] or 1) - 1]
        try: 
            refined = await WorkerCopy(gateway=gateway, prompt_catalog=prompt_catalog, gen_id=str(gen_id))\
                .refine(current, req.message, gen["product_brief"], gen["tts_language"])
        except Exception as e:
            raise HTTPException(503, detail={"error_code": "ECM-013", "message": str(e)}) 
            
        last_cost = float(gateway.last_call_cost)
        
        # ── STEP 5: Output Guard & Ledger Recording ──
        stages_traversed.append("cost_guard_record")
        await cost_guard.record(str(gen_id), last_cost, "chat", gateway.last_model_used)
        
        stages_traversed.append("output_guard") 
        og = await output_guard.check_output(refined.full_text)
        if not og.safe:
            await db.execute("UPDATE generations SET cogs_total = cogs_total + $2 WHERE gen_id = $1", gen_id, last_cost) 
            raise HTTPException(422, detail={"error_code": "ECM-010"})
            
        # ── STEP 6: Commit Atomic FSM Update ──
        result = await db.fetchrow(
            """UPDATE generations SET 
               refined_script = $2::jsonb, chat_turns_used = chat_turns_used + 1, 
               chat_history = chat_history || $3::jsonb || $4::jsonb, cogs_total = cogs_total + $5 
               WHERE gen_id = $1 AND status = 'scripts_ready' AND chat_turns_used < 3 
               RETURNING chat_turns_used""", 
            gen_id, json.dumps(refined.__dict__), 
            json.dumps({"role": "user", "content": req.message, "timestamp": datetime.utcnow().isoformat()}), 
            json.dumps({"role": "assistant", "content": refined.full_text, "timestamp": datetime.utcnow().isoformat()}), 
            last_cost
        )
        
        await sse_manager.push(gen_id, { "type": "chat_turn", "turns_used": result["chat_turns_used"], "turns_remaining": 3 - result["chat_turns_used"] })
        return { "refined_script": refined.__dict__, "turns_used": result["chat_turns_used"], "turns_remaining": 3 - result["chat_turns_used"], "cost_inr": last_cost }
        
    finally:
        logger.info("chat_chain_order", extra={"gen_id": str(gen_id), "chain_stages_traversed": stages_traversed})
        await redis_db5.delete(lock_key)
```

### [TDD-API]-D · POST /api/generations/{gen_id}/approve-strategy

**Fulfills PRD Requirement:** `[PRD-HD4]`, `[PRD-FEATURES-PAYMENT]`, F-303, F-701, `[PRD-PRETOPUP]`, `[PRD-AC-4]` Lua lock-fail writes `pre_topup_status='strategy_preview'` atomically with `status='awaiting_funds'`.

```
@router.post("/api/generations/{gen_id}/approve-strategy") 
@idempotent(ttl=300, action_key="approve-strategy", cache_only_2xx=True)
async def approve_strategy(
    gen_id: UUID, request: Request, 
    idempotency_key: str = Header(..., alias="Idempotency-Key"), 
    user=Depends(get_current_user)
):
    """
    Financial Gate. Locks wallet credit before dispatching 15s fractional render.
    """
    # ── STEP 1: Lock & Verify Status ──
    lock_key = f"actlock:{gen_id}:approve-strategy" 
    acquired = await redis_db5.set(lock_key, "1", nx=True, ex=10)
    if not acquired: raise HTTPException(409, detail={"error_code": "ECM-012"})
        
    try:
        gen = await db.fetchrow("SELECT status, plan_tier FROM generations WHERE gen_id = $1 AND user_id = $2 FOR UPDATE", gen_id, user["user_id"])
        if not gen: raise HTTPException(404)
        if gen["status"] != "strategy_preview": raise HTTPException(409, detail={"error_code": "ECM-012"})
        if gen["plan_tier"] == "starter": raise HTTPException(403, detail={"error_code": "ECM-006"})
        
        # ── STEP 2: Atomic Ledger & Redis Lock ──
        async with db.transaction():
            txn_id = await db.fetchval(
                """INSERT INTO wallet_transactions (user_id, type, credits, status, gen_id) 
                   VALUES ($1, 'lock', -1, 'locked'::wallet_status, $2) RETURNING txn_id""", 
                user["user_id"], gen_id
            )
            
            lua_result = await redis_lua.wallet_lock(user_id=user["user_id"], gen_id=gen_id, credits=1)
            
            if lua_result == 0:
                # User has no credits: Rollback transaction and set status to 'awaiting_funds'
                await db.execute("DELETE FROM wallet_transactions WHERE txn_id = $1", txn_id)
                await db.execute(
                    """UPDATE generations SET status = 'awaiting_funds', pre_topup_status = 'strategy_preview' 
                       WHERE gen_id = $1 AND status = 'strategy_preview'""", gen_id
                ) 
                await sse_manager.push(gen_id, { "type": "state_change", "state": "awaiting_funds", "restore_screen": "HD-4" })
                raise HTTPException(402, detail={"error_code": "ECM-007"})
                
            # Payment success
            await db.execute("UPDATE generations SET status = 'funds_locked' WHERE gen_id = $1", gen_id)
            
        # ── STEP 3: Dispatch Phase 4 Coordinator ──
        # Triggers the optimized Option 1/2/3 15-second rendering logic
        await arq_pool.enqueue_job("phase4_coordinator", gen_id=str(gen_id), _queue_name="adcreo-render", _job_id=f"phase4:{gen_id}")
        await sse_manager.push(gen_id, {"type": "state_change", "state": "funds_locked"})
        return {"status": "funds_locked"}
        
    finally:
        await redis_db5.delete(lock_key)
```

### [TDD-API]-E · POST /api/generations/{gen_id}/edit-back

**Fulfills PRD Requirement:** `[PRD-HD4]`, F-704, `[PRD-FLOW-INVARIANTS]` NULLs downstream when user clicks an [Edit] target on HD-4. Validates target is one of the 4 PRD-defined targets (Product, Targeting, Script, Style).

```
@router.post("/api/generations/{gen_id}/edit-back") 
@idempotent(ttl=300, action_key="edit-back", cache_only_2xx=True)
async def edit_back(
    gen_id: UUID, req: EditBackRequest, request: Request, 
    idempotency_key: str = Header(..., alias="Idempotency-Key"), 
    user=Depends(get_current_user)
): 
    """Safely rewinds FSM state by NULLing future dependencies to prevent data contamination."""
    
    lock_key = f"actlock:{gen_id}:edit-back" 
    acquired = await redis_db5.set(lock_key, "1", nx=True, ex=10)
    if not acquired: raise HTTPException(409, detail={"error_code": "ECM-012"})
    
    try:
        gen = await db.fetchrow("SELECT status FROM generations WHERE gen_id = $1 AND user_id = $2 FOR UPDATE", gen_id, user["user_id"])
        if not gen: raise HTTPException(404)
        if gen["status"] != "strategy_preview": raise HTTPException(409, detail={"error_code": "ECM-012"}) 
        
        target = req.target_field 
        
        # ── STEP 1: Conditional State Rewind ──
        if target == "product":
            await db.execute("""UPDATE generations SET status = 'brief_ready', routed_frameworks = NULL, routing_rationale = NULL, raw_scripts = NULL, critic_scores = NULL, safe_scripts = NULL, selected_script_id = NULL, refined_script = NULL, chat_history = '[]'::jsonb, chat_turns_used = 0, motion_archetype_id = NULL, environment_preset_id = NULL, b_roll_plan = '[]'::jsonb, strategy_card = NULL WHERE gen_id = $1""", gen_id)
        elif target == "targeting":
            await db.execute("""UPDATE generations SET status = 'scripts_ready', routed_frameworks = NULL, routing_rationale = NULL, raw_scripts = NULL, critic_scores = NULL, safe_scripts = NULL, selected_script_id = NULL, refined_script = NULL, chat_history = '[]'::jsonb, chat_turns_used = 0, b_roll_plan = '[]'::jsonb, strategy_card = NULL WHERE gen_id = $1""", gen_id)
            await arq_pool.enqueue_job("phase2_chain", gen_id=str(gen_id), _queue_name="adcreo-studio")
        elif target == "script":
            await db.execute("""UPDATE generations SET status = 'scripts_ready', strategy_card = NULL, b_roll_plan = '[]'::jsonb WHERE gen_id = $1""", gen_id)
        elif target == "style":
            await db.execute("""UPDATE generations SET status = 'scripts_ready', motion_archetype_id = NULL, environment_preset_id = NULL, strategy_card = NULL, b_roll_plan = '[]'::jsonb WHERE gen_id = $1""", gen_id)
        else:
            raise HTTPException(400, detail={"error_code": "INVALID_EDIT_TARGET"})
            
        await sse_manager.push(gen_id, { "type": "edit_back_complete", "target_field": target, "target_state": req.target_state })
        return {"status": req.target_state, "target_field": target}
    finally:
        await redis_db5.delete(lock_key)
```

### [TDD-API]-F · POST /api/generations/{gen_id}/declaration

**Fulfills PRD Requirement:** `[PRD-HD6]`, F-505, F-611, `[PRD-AC-5]` Captures provenance, INSERTs audit_log row, transitions preview_ready → export_queued, and enqueues Worker-EXPORT independently.

```
@router.post("/api/generations/{gen_id}/declaration") 
@idempotent(ttl=300, action_key="declaration", cache_only_2xx=True)
async def declaration(
    gen_id: UUID, req: DeclarationRequest, request: Request, 
    idempotency_key: str = Header(..., alias="Idempotency-Key"), 
    user=Depends(get_current_user)
): 
    """Capture IP/UA/timestamp/SHA256 → audit_log → enqueue worker_export."""
    lock_key = f"actlock:{gen_id}:declaration" 
    acquired = await redis_db5.set(lock_key, "1", nx=True, ex=10)
    if not acquired: raise HTTPException(409, detail={"error_code": "ECM-012"})
    
    try:
        # ── STEP 1: Cryptographic Provenance (IT Rules 2026) ──
        ip = request.client.host
        ua = request.headers.get("user-agent", "")
        decl_hash = hashlib.sha256(f"{gen_id}|{user['user_id']}|{ip}|{ua}|{datetime.utcnow().isoformat()}".encode()).hexdigest()
        
        async with db.transaction():
            gen = await db.fetchrow("SELECT status FROM generations WHERE gen_id = $1 AND user_id = $2 FOR UPDATE", gen_id, user["user_id"])
            if not gen: raise HTTPException(404)
            if gen["status"] != "preview_ready":
                raise HTTPException(409, detail={"error_code": "ECM-012"})
                
            # ── STEP 2: Write Audit Log ──
            await db.execute(
                """UPDATE generations SET declaration_accepted = TRUE, declaration_accepted_at = NOW(), 
                   declaration_ip = $2, declaration_ua = $3, declaration_hash = $4 WHERE gen_id = $1""", 
                gen_id, ip, ua, decl_hash
            )
            await db.execute(
                """INSERT INTO audit_log (gen_id, user_id, action, ip_address, user_agent, declaration_sha256, payload) 
                   VALUES ($1, $2, 'declaration_accepted', $3, $4, $5, $6::jsonb)""", 
                gen_id, user["user_id"], ip, ua, decl_hash, 
                json.dumps({ "commercial_use": req.confirms_commercial_use, "image_rights": req.confirms_image_rights, "ai_disclosure": req.confirms_ai_disclosure })
            )
            await db.execute("UPDATE generations SET status = 'export_queued' WHERE gen_id = $1", gen_id)
            
        # ── STEP 3: Decoupled Dispatch ──
        # Triggers C2PA signing. Export is separate from rendering to save costs on retries.
        await arq_pool.enqueue_job("worker_export", gen_id=str(gen_id), _queue_name="adcreo-render", _job_id=f"export:{gen_id}:0")
        await sse_manager.push(gen_id, {"type": "state_change", "state": "export_queued"})
        return {"status": "export_queued"}
    finally:
        await redis_db5.delete(lock_key)
```

### [TDD-API]-G · POST /api/generations/{gen_id}/retry-export — 9-Step Atomic Chain

**Fulfills PRD Requirement:** `[PRD-HD6]`, `[PRD-AC-6]`, `[PRD-PRETOPUP]`, `[PRD-PAYMENT-FSM]`, `[PRD-ERROR-MATRIX]`, `[PRD-IDEMPOTENCY]`, F-404a, F-611, F-612

```
MAX_EXPORT_RETRIES = 3
DECLARATION_FRESHNESS_SECONDS = 24 * 3600 # 24h 

@router.post("/api/generations/{gen_id}/retry-export") 
@idempotent(ttl=300, action_key="retry-export", cache_only_2xx=True)
async def retry_export(
    gen_id: UUID, req: RetryExportRequest, request: Request, 
    idempotency_key: str = Header(..., alias="Idempotency-Key"), 
    user=Depends(get_current_user)
): 
    """9-step atomic retry chain. Persists legal re-sign even if credit lock fails."""
    lock_key = f"actlock:{gen_id}:retry-export" 
    acquired = await redis_db5.set(lock_key, "1", nx=True, ex=10)
    if not acquired: raise HTTPException(409, detail={"error_code": "ECM-012"})
    
    try:
        # ── STEP 1: Validation (Ownership, State, Retry Count) ──
        gen = await db.fetchrow("SELECT status, export_retry_count, plan_tier, preview_url, declaration_accepted_at FROM generations WHERE gen_id = $1 AND user_id = $2", gen_id, user["user_id"])
        if not gen: raise HTTPException(404)
        if gen["status"] != "failed_export": raise HTTPException(409, detail={"error_code": "ECM-012"})
        if gen["export_retry_count"] >= MAX_EXPORT_RETRIES: raise HTTPException(410, detail={"error_code": "ECM-019"})
        
        # ── STEP 2: Declaration Freshness & Inline Re-sign ──
        last_decl = await db.fetchval("SELECT MAX(created_at) FROM audit_log WHERE gen_id = $1 AND action IN ('declaration_accepted', 'declaration_resigned')", gen_id)
        is_stale = (last_decl is None or (datetime.utcnow() - last_decl.replace(tzinfo=None)).total_seconds() > DECLARATION_FRESHNESS_SECONDS)
        
        if is_stale:
            if req.declarations != [True, True, True]: raise HTTPException(428, detail={"error_code": "ECM-020", "requires_declarations": True})
            ip, ua = request.client.host, request.headers.get("user-agent", "")
            decl_hash = hashlib.sha256(f"{gen_id}|{user['user_id']}|{ip}|{ua}|{datetime.utcnow().isoformat()}|resigned".encode()).hexdigest()
            await db.execute("""INSERT INTO audit_log (gen_id, user_id, action, ip_address, user_agent, declaration_sha256, payload) VALUES ($1, $2, 'declaration_resigned', $3, $4, $5, $6::jsonb)""", gen_id, user["user_id"], ip, ua, decl_hash, json.dumps({"inline_resign": True}))
            await db.execute("UPDATE generations SET declaration_accepted_at = NOW() WHERE gen_id = $1", gen_id)
            
        # ── STEP 3: R2 Availability Check ──
        try: await r2_client.head_object(gen["preview_url"])
        except Exception:
            await db.execute("UPDATE generations SET error_code = 'ECM-018' WHERE gen_id = $1", gen_id)
            raise HTTPException(410, detail={"error_code": "ECM-018"})
            
        # ── STEP 4: Transactional State Update & Credit Lock ──
        async with db.transaction():
            txn_id = await db.fetchval("INSERT INTO wallet_transactions (user_id, type, credits, status, gen_id) VALUES ($1, 'lock', -1, 'locked'::wallet_status, $2) RETURNING txn_id", user["user_id"], gen_id)
            lua_result = await redis_lua.wallet_lock(user_id=user["user_id"], gen_id=gen_id, credits=1)
            
            if lua_result == 0:
                await db.execute("DELETE FROM wallet_transactions WHERE txn_id = $1", txn_id)
                await db.execute("UPDATE generations SET status = 'awaiting_funds', pre_topup_status = 'failed_export' WHERE gen_id = $1", gen_id)
                lock_failed, new_retry_count = True, gen["export_retry_count"]
            else:
                lock_failed, new_retry_count = False, gen["export_retry_count"] + 1
                await db.execute("UPDATE generations SET status = 'export_queued', export_retry_count = $2 WHERE gen_id = $1", gen_id, new_retry_count)
                
        # ── STEP 5: Post-Commit Dispatch ──
        if lock_failed:
            await sse_manager.push(gen_id, { "type": "state_change", "state": "awaiting_funds", "pre_topup_status": "failed_export", "restore_screen": "HD-6" })
            raise HTTPException(402, detail={"error_code": "ECM-007"})
            
        await arq_pool.enqueue_job("worker_export", gen_id=str(gen_id), _queue_name="adcreo-render", _job_id=f"export:{gen_id}:{new_retry_count}")
        await sse_manager.push(gen_id, { "type": "state_change", "state": "export_queued", "export_retry_count": new_retry_count })
        return {"status": "export_queued", "export_retry_count": new_retry_count}
    finally:
        await redis_db5.delete(lock_key)
```

### [TDD-API]-H · POST /api/webhook/razorpay — Origin-Preserving Restoration

**Fulfills PRD Requirement:** `[PRD-PAYMENT-FSM]`, `[PRD-PRETOPUP]`, `[PRD-FEATURES-PAYMENT]`, `[PRD-NON-NEGOTIABLES]`, `[PRD-ERROR-MATRIX]`, F-301 HMAC-verified. Multi-row atomic restore: `SET status = pre_topup_status WHERE status='awaiting_funds'`. Correct for the edge case of a user holding BOTH an HD-4-origin and an HD-6-origin generation simultaneously.

```
@router.post("/api/webhook/razorpay")
async def razorpay_webhook(request: Request, db=Depends(get_db)): 
    """
    Origin-Preserving Async Restoration.
    Correctly unpauses generations after payment succeeds.
    """
    # ── STEP 1: Cryptographic Webhook Verification ──
    body = await request.body() 
    signature = request.headers.get("x-razorpay-signature", "") 
    expected_sig = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        raise HTTPException(401, "Invalid webhook signature") 
        
    payload = json.loads(body)
    event = payload.get("event")
    
    # ── STEP 2: Extract Entities ──
    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_payment_id = payment_entity.get("id")
    user_id = payment_entity.get("notes", {}).get("user_id")
    amount_paise = payment_entity.get("amount", 0)
    
    if not all([razorpay_payment_id, user_id]): raise HTTPException(400, "Missing required payload entities")
        
    # Map Razorpay statuses
    target_status = "captured" if event == "payment.captured" else "failed" if event == "payment.failed" else None
    if not target_status: return {"ok": True, "ignored": True}
        
    # Determine credit package
    if amount_paise == 39900: credits_delta, plan = 4, "essential"
    elif amount_paise == 149900: credits_delta, plan = 25, "pro"
    else: raise HTTPException(400, f"Unknown amount: {amount_paise}")
    
    # ── STEP 3: Atomic Ledger & Multi-Row Restore ──
    async with db.transaction():
        try:
            # Prevents webhook double-counting via UniqueViolation
            await db.execute(
                """INSERT INTO wallet_transactions (user_id, type, credits, payment_status, razorpay_payment_id) 
                   VALUES ($1, 'topup', $2, $3::payment_status, $4)""", 
                user_id, credits_delta, target_status, razorpay_payment_id
            )
        except asyncpg.UniqueViolationError:
            return {"ok": True, "dedup": True}
            
        if target_status != "captured":
            return {"ok": True, "status": target_status}
            
        # Grant Credits
        await db.execute(
            """UPDATE users SET credits_remaining = credits_remaining + $2, plan_tier = $3::plan_tier, 
               plan_expires_at = NOW() + (CASE WHEN $3='essential' THEN INTERVAL '30 days' ELSE INTERVAL '45 days' END) 
               WHERE user_id = $1""", user_id, credits_delta, plan
        )
        await redis_db0.hincrby(f"wallet:{user_id}", "balance", credits_delta)
        
        # ★★★ Origin-preserving multi-row atomic restore ★★★ 
        # This solves the issue if user was paused on HD-4 AND HD-6 at the same time.
        restored_rows = await db.fetch(
            """UPDATE generations SET status = pre_topup_status, pre_topup_status = NULL 
               WHERE user_id = $1 AND status = 'awaiting_funds' RETURNING gen_id, status""", 
            user_id
        )
        
    # ── STEP 4: SSE Broadcast ──
    for row in restored_rows:
        await sse_manager.push(str(row["gen_id"]), { 
            "type": "state_change", "state": row["status"], 
            "pre_topup_status": None, "source": "topup_captured" 
        })
        
    return { "ok": True, "credits_applied": credits_delta, "restored_count": len(restored_rows) }
```

---


> **[CONSISTENCY-FLAG: `screen_descriptor` not in `GET /generations/{id}` response]** Category 3A (`[TDD-FSM]-SCREEN-CONTRACT`) specifies that the hydration endpoint response MUST include a `screen_descriptor` block. v3's `[TDD-API]-B` response is:
>
> ```python
> return {
>     "status": gen["status"],
>     "error_code": gen["error_code"],
>     "confidence_score": gen["confidence_score"]
> }
> ```
>
> This shape is missing `screen_descriptor`. During the human merge pass, extend the response (and the `StatusResponse` Pydantic model in `[TDD-TYPES]-B`) to include the descriptor as serialized by `models/generation_view.py`. Do **not** rewrite the route — only add the descriptor field. See `CONSISTENCY FLAGS`.

> **[CONSISTENCY-FLAG: Webhook handler does not use `processed_webhooks` table]** Category 3B (`[TDD-CONCURRENCY]-F`) specifies that the Razorpay webhook handler MUST perform an `INSERT INTO processed_webhooks (event_id, payment_id)` as the first write inside the transaction. v3's `[TDD-API]-H` handler dedups on `razorpay_payment_id` UniqueViolation only — it does not use a webhook-event-id dedup table, and Razorpay can deliver the same payment event with the same `event_id` across multiple delivery attempts. During the human merge pass, prepend the `processed_webhooks` INSERT to the transaction body. Keep the existing `razorpay_payment_id` UniqueViolation guard as the third safety net. See `CONSISTENCY FLAGS`.

---


## [TDD-REDIS] · Redis Architecture, Key Design & Lua Scripts

**Fulfills PRD Requirement:** `[PRD-PAYMENT-FSM]`, `[PRD-PRETOPUP]`, `[PRD-FEATURES-PAYMENT]`, `[PRD-IDEMPOTENCY]`, `[PRD-FEATURES-INFRA]`, `[PRD-NON-NEGOTIABLES]`

Redis is the authoritative wallet surface at runtime — Postgres holds the immutable ledger, but Redis is the fast path. The 6-DB namespace split is a Bulkhead pattern: a hot key in one DB cannot starve another. All wallet mutations are Lua-scripted to guarantee atomicity and prevent double-spend race conditions.


### [TDD-REDIS]-INIT · Redis Initialization & Access Pattern

Redis is initialized during FastAPI lifespan startup in `main.py`.

- A single Redis manager instance is created and attached to `app.state.redis_mgr`.
- All guards, routes, and workers MUST access Redis via:
  `request.app.state.redis_mgr`

**Rules:**
- No module may instantiate its own Redis client.
- All Redis usage must go through the shared manager.
- Logical DB separation (DB0–DB5) is handled inside `infra_redis.py`.

**Rationale:**
- Prevents connection duplication
- Ensures consistent locking and idempotency behavior
- Aligns with Zero-Shadowing and infra_* modular architecture

### [TDD-REDIS]-A · Redis 6-DB Namespace Scheme

| DB      | Purpose               | Key patterns                                                | TTL                   |
| ------- | --------------------- | ----------------------------------------------------------- | --------------------- |
| **DB0** | Wallet cache + locks  | `wallet:{user_id}`, `walletlock:{user_id}:{gen_id}`         | 5min cache, 300s lock |
| **DB1** | ARQ job queues        | `arq:queue:phase1_to_3`, `arq:queue:adcreo-render`         | per-job               |
| **DB2** | COGS per-gen tracker  | `cogs:{gen_id}` (hash: total, chat)                         | 24h                   |
| **DB3** | Provider health (CB)  | `health:{provider}`, `cb:{provider}`, `feature_flags:{key}` | 5min                  |
| **DB4** | Rate limiting         | `rl:user:{user_id}:{endpoint}:{window}`                     | sliding window        |
| **DB5** | Idempotency & actlock | `idem:{u_id}:{gen_id}`, `actlock:{gen_id}:{action}`         | 300s / 10s            |

### [TDD-REDIS]-B · Lua Script: wallet_lock.lua

**Fulfills PRD Requirement:** `[PRD-PAYMENT-FSM]`, `[PRD-PRETOPUP]`, `[PRD-AC-4]`, `[PRD-AC-6]`

Atomic per-generation credit lock. Called by the API layer (`/approve-strategy` and `/retry-export`) _before_ enqueueing expensive AI work. Prevents race conditions if a user double-clicks.

```
-- =====================================================================
-- SCRIPT: wallet_lock.lua
-- PURPOSE: Atomically check balance and reserve 1 credit for a generation.
-- KEYS[1]: wallet:{user_id}               (The user's main wallet hash)
-- KEYS[2]: walletlock:{user_id}:{gen_id}  (The temporary lock key)
-- ARGV[1]: credits_to_lock                (Int, usually 1)
-- ARGV[2]: ttl_seconds                    (Int, usually 300)
-- RETURNS: 1 on success, 0 on insufficient funds.
-- =====================================================================

-- 1. Fetch current balance
local balance = tonumber(redis.call('HGET', KEYS[1], 'balance')) or 0
local credits = tonumber(ARGV[1])

-- 2. Guard: Ensure user can afford the operation
if balance < credits then
    return 0
end

-- 3. Idempotency Check: Is this generation already locked?
local existing = redis.call('EXISTS', KEYS[2])
if existing == 1 then
    -- Existing active lock found (e.g., network retry). Treat as success.
    return 1
end

-- 4. Atomic Deduct & Lock
-- Decrement the balance hash
redis.call('HINCRBY', KEYS[1], 'balance', -credits)
-- Create an expiring lock key to represent the reserved funds
redis.call('SET', KEYS[2], credits, 'EX', tonumber(ARGV[2]))

return 1
```

### [TDD-REDIS]-C · Lua Script: wallet_consume.lua

**Fulfills PRD Requirement:** `[PRD-PAYMENT-FSM]`, `[PRD-HD6]`, `[PRD-AC-5]`

Converts a temporary lock into a permanent consume. Called exclusively by `Worker-EXPORT` _after_ the final MP4 is successfully signed with C2PA and uploaded to R2.

```
-- =====================================================================
-- SCRIPT: wallet_consume.lua
-- PURPOSE: Finalize a transaction after successful video generation.
-- KEYS[1]: wallet:{user_id}
-- KEYS[2]: walletlock:{user_id}:{gen_id}
-- RETURNS: 1 on success, 0 if no active lock exists.
-- =====================================================================

-- 1. Verify the lock still exists
local locked = redis.call('GET', KEYS[2])
if locked == false then
    -- Lock expired or was already consumed/refunded
    return 0
end

-- 2. Consume the lock
-- Delete the temporary lock key
redis.call('DEL', KEYS[2])
-- Increment the lifetime consumed tracking metric
redis.call('HINCRBY', KEYS[1], 'consumed_total', tonumber(locked))

return 1
```

### [TDD-REDIS]-D · Lua Script: wallet_refund.lua

**Fulfills PRD Requirement:** `[PRD-PAYMENT-FSM]`, `[PRD-ERROR-MATRIX]`, `[PRD-NON-NEGOTIABLES]`

The financial safety net. Called by the Dead Letter Queue (DLQ) handler if `phase4_coordinator` or `Worker-EXPORT` crashes. Ensures users are never charged for failed generations.

```
-- =====================================================================
-- SCRIPT: wallet_refund.lua
-- PURPOSE: Return locked credits back to the user's balance on error.
-- KEYS[1]: wallet:{user_id}
-- KEYS[2]: walletlock:{user_id}:{gen_id}
-- RETURNS: 1 on refund applied, 0 if nothing to refund.
-- =====================================================================

-- 1. Find the active lock
local locked = redis.call('GET', KEYS[2])
if locked == false then
    -- Nothing is locked, so there is nothing to refund
    return 0
end

local credits = tonumber(locked)

-- 2. Execute Refund
-- Give the credits back to the main balance
redis.call('HINCRBY', KEYS[1], 'balance', credits)
-- Destroy the lock
redis.call('DEL', KEYS[2])

return 1
```

> _Implementation Note:_ The DLQ handler wraps this Lua script with a Postgres `INSERT INTO wallet_transactions (type='refund')` protected by `ON CONFLICT DO NOTHING` to ensure the immutable ledger stays synced with the Redis state.

### [TDD-REDIS]-E · Lua Script: circuit_breaker.lua

**Fulfills PRD Requirement:** `[PRD-FEATURES-INFRA]`, `[PRD-PRICING]`

Protects the Model Gateway from hanging requests when external AI providers (like Groq, Minimax, or Fal.ai) experience outages.

```
-- =====================================================================
-- SCRIPT: circuit_breaker.lua
-- PURPOSE: State machine for API provider health routing.
-- KEYS[1]: cb:{provider} (e.g., cb:groq, cb:fal)
-- ARGV[1]: action ('check' | 'record_success' | 'record_failure')
-- ARGV[2]: failure_threshold (e.g., 5 errors)
-- ARGV[3]: window_seconds (e.g., 60s cooldown)
-- ARGV[4]: half_open_probe_count (e.g., 3 test requests)
-- RETURNS: 'closed' (healthy), 'open' (failing), 'half_open' (testing)
-- =====================================================================

local state = redis.call('HGET', KEYS[1], 'state') or 'closed'
local failures = tonumber(redis.call('HGET', KEYS[1], 'failures')) or 0
local opened_at = tonumber(redis.call('HGET', KEYS[1], 'opened_at')) or 0
local now = tonumber(redis.call('TIME')[1])

-- ACTION: CHECK BEFORE ROUTING
if ARGV[1] == 'check' then
    -- If open, see if the cooldown window has expired
    if state == 'open' and (now - opened_at) > tonumber(ARGV[3]) then
        -- Transition to half-open to test the provider
        redis.call('HSET', KEYS[1], 'state', 'half_open', 'probes_remaining', ARGV[4])
        return 'half_open'
    end
    return state

-- ACTION: RECORD SUCCESSFUL API CALL
elseif ARGV[1] == 'record_success' then
    if state == 'half_open' then
        -- Subtract one from the test probe count
        local remaining = tonumber(redis.call('HINCRBY', KEYS[1], 'probes_remaining', -1))
        if remaining <= 0 then
            -- Tests passed. Close the breaker (healthy again).
            redis.call('HMSET', KEYS[1], 'state', 'closed', 'failures', 0, 'opened_at', 0)
            return 'closed'
        end
    elseif state == 'closed' then
        -- Reset failure count on a successful call
        redis.call('HSET', KEYS[1], 'failures', 0)
    end
    return state

-- ACTION: RECORD API TIMEOUT OR 5xx ERROR
elseif ARGV[1] == 'record_failure' then
    local new_failures = tonumber(redis.call('HINCRBY', KEYS[1], 'failures', 1))
    
    -- If we hit the threshold, open the breaker
    if new_failures >= tonumber(ARGV[2]) and state ~= 'open' then
        redis.call('HMSET', KEYS[1], 'state', 'open', 'opened_at', now)
        return 'open'
    end
    return state
end
```
---


> **[CONSISTENCY-FLAG: ARQ queue names in DB1 namespace]** v3's `[TDD-REDIS]-A` namespace table lists `arq:queue:phase1_to_3` and `arq:queue:adcreo-render`. Per Category 3C rename, the human merge must update these to `arq:queue:adcreo-studio` and `arq:queue:adcreo-render` consistently with `[TDD-DEPLOYMENT]`. ARQ queue names appear in worker enqueue calls — keep them in lock-step. See `CONSISTENCY FLAGS`.

---


## [TDD-CONCURRENCY] · Concurrency Patterns

**Fulfills PRD Requirement:** `[PRD-AC-GLOBAL]`, `[PRD-PAYMENT-FSM]`, `[PRD-FLOW-INVARIANTS]`, `[PRD-PRETOPUP]`, `[PRD-IDEMPOTENCY]`

Every API endpoint that affects user credits or mutates the FSM state must compose these five canonical patterns in a strict, declared order: **Action Lock (outside) → Ledger-First Write → Redis Lua Validation → State-Guarded UPDATE (inside) → Enqueue Background Job (after COMMIT).**

### [TDD-CONCURRENCY]-A · Per-Action Locking Pattern (The "Double-Click" Defense)

Prevents the same user from triggering the exact same FSM transition simultaneously (e.g., rapid-clicking the UI).

```
# The @idempotent decorator sits OUTSIDE the fence. 
# If a cached 2xx response exists, it is returned immediately, skipping the lock entirely.
@idempotent(ttl=300, action_key="chat", cache_only_2xx=True)
async def some_action(gen_id: UUID):
    
    # 1. Advisory Lock: Set a 10-second lock in Redis DB5. 
    # 'nx=True' ensures it only sets if the key DOES NOT exist.
    lock_key = f"actlock:{gen_id}:{action}" 
    acquired = await redis_db5.set(lock_key, "1", nx=True, ex=10)
    
    if not acquired:
        # If lock exists, another request is currently processing this action. Reject immediately.
        raise HTTPException(409, detail={"error_code": "ECM-012"})
        
    try:
        # ... execute core FSM business logic here ...
        pass
    finally:
        # 2. Release Lock: Always delete the lock when finished, even if the logic crashed.
        await redis_db5.delete(lock_key)
```

### [TDD-CONCURRENCY]-B · State-Guarded UPDATE Pattern (Optimistic Concurrency)

Never assume the database state hasn't changed between your `SELECT` and your `UPDATE`. Always include the `expected_status` in your `WHERE` clause.

```
-- DANGEROUS (Prone to race conditions):
-- UPDATE generations SET status = 'funds_locked' WHERE gen_id = $1;

-- SAFE (State-Guarded):
UPDATE generations 
SET status = 'funds_locked' 
WHERE gen_id = $1 
  AND status = 'strategy_preview' -- Optimistic Concurrency Check
RETURNING gen_id;
```

```
# Inside the API route:
result = await db.fetchrow(
    """UPDATE generations SET status = $2 
       WHERE gen_id = $1 AND status = $3 RETURNING gen_id""", 
    gen_id, new_status, expected_status
)

if not result:
    # If no row was returned, it means the status changed mid-flight. Halt execution.
    raise HTTPException(409, "State changed mid-flight. Transition aborted.")
```

### [TDD-CONCURRENCY]-C · Ledger-First Pattern (Postgres Source-of-Truth)

All wallet mutations must write to the immutable Postgres ledger _before_ invoking the fast-path Redis Lua script. Redis is merely a projection; Postgres is the ultimate source of truth.

```
# Executed inside routes like /approve-strategy or /retry-export
async with db.transaction():
    # 1. LEDGER FIRST: Optimistically insert the transaction into Postgres.
    txn_id = await db.fetchval(
        """INSERT INTO wallet_transactions (user_id, type, credits, status, gen_id) 
           VALUES ($1, 'lock', -1, 'locked', $2) RETURNING txn_id""", 
        user_id, gen_id
    )
    
    # 2. REDIS LUA: Attempt the atomic lock in the fast-cache
    lua_result = await redis_lua.wallet_lock(user_id=user_id, gen_id=gen_id, credits=1)
    
    if lua_result == 0:
        # 3. ROLLBACK: If Redis says "insufficient funds", we delete the optimistic ledger entry.
        # Because we are inside async with db.transaction(), this is perfectly atomic.
        await db.execute("DELETE FROM wallet_transactions WHERE txn_id = $1", txn_id)
        # Proceed to update state to 'awaiting_funds'
```

### [TDD-CONCURRENCY]-D · Double-Refund Defense

When an AI worker fails (e.g., the Fal.ai I2V render times out), the DLQ (Dead Letter Queue) handler gives the user their credit back. This defense guarantees a user cannot receive _two_ refunds if the DLQ accidentally processes the failure twice.

1. **Redis Lua Constraint:** `wallet_refund.lua` checks for the active lock marker. If there is no lock (`GET == false`), it immediately returns `0` (abort).
    
2. **Postgres Schema Constraint:** A `UNIQUE INDEX` exists on `(gen_id, type)` where `type='refund'`. The database physically cannot store two refunds for the same generation.
    
3. **Application Layer Logic:** The DLQ handler uses `ON CONFLICT DO NOTHING` when inserting the refund, gracefully ignoring duplicate DLQ events without crashing.
    

### [TDD-CONCURRENCY]-E · Pre-Topup Status Invariant Pattern

When a user runs out of credits, we must safely "pause" them and remember exactly where they were, so when the Razorpay webhook fires, we resume them correctly. Three layers defend this paired-write invariant:

**1. Postgres CHECK Constraint:**

```
-- Ensures the DB can never hold an invalid FSM pause state.
CHECK (
  (status = 'awaiting_funds' AND pre_topup_status IN ('strategy_preview', 'failed_export')) 
  OR 
  (status <> 'awaiting_funds' AND pre_topup_status IS NULL)
)
```

**2. Application State Triggers:** Every `UPDATE` query that pauses a generation must atomically write both columns:

```
UPDATE generations 
SET status = 'awaiting_funds', pre_topup_status = 'strategy_preview' 
WHERE gen_id = $1 AND status = 'strategy_preview';
```

**3. Atomic Webhook Restoration (Multi-Row):** When the Razorpay webhook hits, it executes a single, atomic `UPDATE` that cannot produce an intermediate state. It mutates both columns simultaneously for _all_ paused generations owned by the user.

```
UPDATE generations 
SET status = pre_topup_status, pre_topup_status = NULL 
WHERE user_id = $1 AND status = 'awaiting_funds' 
RETURNING gen_id, status;
```

---


### [TDD-CONCURRENCY]-F · Razorpay Webhook Idempotency *(Category 3B — APPENDED)*

**Context:** Razorpay delivers the same webhook 2–5× over 5–6 days on non-200 responses. The existing `@idempotent` decorator (`[TDD-CONCURRENCY]-A`) MUST NOT be used for webhooks — it expects a client-sent `Idempotency-Key` header (Razorpay never sends one) and has a 300s TTL (Razorpay retries for 5+ days).

**Pattern:** Atomic `processed_webhooks` table dedup, inside a single Postgres transaction that wraps all four writes.

**Migration (must be added to `[TDD-MIGRATIONS]`):**

```sql
CREATE TABLE processed_webhooks (
  event_id    TEXT        PRIMARY KEY,
  payment_id  TEXT        NOT NULL,
  processed_at TIMESTAMPTZ DEFAULT NOW(),
  result      JSONB
);
```

`event_id` is the Razorpay `payload.payment.entity.id` paired with `payload.event` — or the top-level webhook event id if Razorpay supplies one. The pairing chosen MUST be documented at migration time and never changed.

**Webhook handler contract:**

The four writes below execute inside a single `db.transaction()`. All four commit atomically or all four roll back together.

1. `INSERT INTO processed_webhooks (event_id, payment_id) VALUES ($1, $2)`. On `asyncpg.UniqueViolationError`: return HTTP 200 immediately, zero further processing, no SSE push, no Redis write.
2. `INSERT INTO wallet_transactions (user_id, type, credits, payment_status, razorpay_payment_id) VALUES (...)` — credit the wallet.
3. `UPDATE users SET credits_remaining = credits_remaining + $delta, plan_tier = $plan, plan_expires_at = ... WHERE user_id = $1`.
4. `UPDATE generations SET status = pre_topup_status, pre_topup_status = NULL WHERE user_id = $1 AND status = 'awaiting_funds'` — the origin-preserving restore.

**Redis wallet cache update:**

Redis `walletbal:{user_id}` cache is updated AFTER the DB transaction commits — never before, never inside the transaction. If the DB transaction rolls back, the Redis write does not happen. This eliminates the Redis/Postgres split-brain failure mode where Redis was incremented but Postgres was not.

**Safety nets (defence in depth):**

1. Primary dedup: `processed_webhooks.event_id PRIMARY KEY` (this section).
2. Secondary dedup: `wallet_transactions.razorpay_payment_id UNIQUE` constraint (v3 `[TDD-API]-H` already enforces this — preserved).
3. Idempotent SSE push: the multi-row restore `RETURNING` block deduplicates implicitly because the `WHERE status='awaiting_funds'` clause matches zero rows on the second delivery.

**CI test (must be added):**

`tests/integration/test_webhook_idempotency.py` asserts:
- Same `event_id` sent twice produces exactly one `wallet_transactions` row.
- `users.credits_remaining` is incremented exactly once.
- Both deliveries return HTTP 200.
- The Redis `walletbal:{user_id}` value matches the Postgres `users.credits_remaining` value after both deliveries complete.
- A delivery whose `payment.entity.id` matches an existing `razorpay_payment_id` but with a fresh `event_id` is also deduplicated (the secondary safety net catches it).

---


## [TDD-GATEWAY] · Model Gateway & CostGuard

**Fulfills PRD Requirement:** `[PRD-PRICING]`, `[PRD-FEATURES-INFRA]`, `[PRD-AGENTIC-DRAFT]`, `[PRD-COPILOT]`, `[PRD-NON-NEGOTIABLES]`

ModelGateway is the sole owner of outbound HTTP clients (enforced by `[TDD-IMPORT-GRAPH]`). Capability-based routing decouples worker code from provider identity. It uses **Health-Weighted Contextual Routing** to guarantee uptime, optimize costs, and enforce cultural accuracy. CostGuard gates every call against a per-plan-tier rupee ceiling.

### [TDD-GATEWAY]-A · ModelGateway · Capability Routing

```
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

class ModelGateway:
    """
    Pillar 1 (Restricted Tools): Sole owner of external HTTP clients. No SDKs in workers.
    Pillar 5 (Release It!): Per-provider circuit breakers and graceful fallbacks.
    Pillar 2 (Economics): Capability routing via Aggregator Pools.
    """
    
    # ── BLOCK 1: DYNAMIC AGGREGATOR POOLS ──
    # We do not map 1-to-1 models. We map to capability pools to prevent vendor lock-in.
    CAPABILITY_PROVIDERS = {
        "llm": ["groq", "together", "siliconflow", "google_studio"], 
        "vision": ["google_studio", "together"], 
        "tts": ["sarvam", "elevenlabs", "google_cloud"], 
        "i2v": ["fal_ai", "minimax"], 
        "moderation": ["groq", "openai"],  # Llama Guard via Groq (primary), OpenAI Moderation (fallback)
    }

    async def route(self, capability: str, input_data: dict) -> "GatewayResponse":
        """
        The Execution Loop.
        Tries the best provider. If it fails, trips the circuit breaker and tries the next.
        """
        # Step 1: Get the optimized, sorted list of providers
        providers = await self._rank_providers(capability, input_data)
        last_error = None
        
        # Step 2: The Fallback Execution Loop
        for provider in providers:
            # Check Circuit Breaker (skip instantly if provider is known to be down)
            cb_state = await self._check_circuit_breaker(provider)
            if cb_state == "open": 
                continue 
                
            try:
                # Execute with strict capability-specific timeout (e.g., 5s for LLM, 30s for I2V)
                async with asyncio.timeout(self._timeout_for(capability)):
                    response = await self._invoke(provider, capability, input_data)
                    
                # SUCCESS PATH
                await self._record_success(provider) # Heal circuit breaker
                await self._record_cogs(input_data.get("gen_id"), response.cost_inr)
                
                # Expose metadata for CostGuard
                self.last_call_cost = response.cost_inr
                self.last_model_used = provider
                return response
                
            except (httpx.TimeoutException, httpx.HTTPError, ProviderError) as e:
                # FAILURE PATH
                await self._record_failure(provider) # Register failure to CB
                last_error = e
                # Track fallback events in Prometheus for infrastructure monitoring
                FALLBACK_EVENTS.labels(from_provider=provider, to_provider="next", capability=capability).inc()
                continue
                
        # Step 3: Pipeline Halt (Only reached if ALL providers in the pool are dead)
        raise ProviderUnavailableError(f"All providers exhausted for {capability}. Last error: {last_error}")

    async def _rank_providers(self, capability: str, input_data: dict) -> list[str]:
        """
        The Scoring Engine.
        Prioritizes by Context (Language) -> Health Score -> Base Cost.
        """
        candidates = self.CAPABILITY_PROVIDERS[capability][:]
        
        # ── BLOCK 2: CONTEXT CHECK ──
        # Business Rule: Indian vernacular must route to Sarvam for highest accuracy.
        preferred_provider = None
        if capability == "tts":
            lang = input_data.get("language", "english")
            if lang in ["hindi", "hinglish", "marathi", "punjabi", "bengali", "tamil", "telugu"]:
                preferred_provider = "sarvam"
                             
        # ── BLOCK 3: HEALTH CHECK & SORTING ──
        scored = []
        for p in candidates:
            # Fetch live health score (0-100) from Redis DB3
            health = int(await redis_db3.get(f"health:{p}") or "100")
            
            # Artificial score boost for contextually preferred providers
            if p == preferred_provider:
                health += 500 # Guarantees top placement unless health is literally 0
                
            # Tie-breaker logic: In production, this would read a live pricing table.
            # For MVP, we assign a static tier weight (lower index = cheaper).
            cost_weight = candidates.index(p) 
            
            scored.append((p, health, cost_weight))
            
        # Sort logic: Highest Health first. If health is equal, lowest Cost Weight first.
        scored.sort(key=lambda x: (-x[1], x[2]))
        
        # Return just the ordered strings
        return [p for p, _, _ in scored]
```

### [TDD-GATEWAY]-B · CostGuard · Per-Gen COGS Ledger

```
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class CostGuard:
    """
    The Financial Firewall.
    Ensures the 15-second rendering logic and AI chat loops never bankrupt the system.
    """
    
    # Strict PRD unit economic ceilings in INR
    CEILING = {
        "starter": Decimal("2.00"),    # Highly bounded
        "essential": Decimal("10.00"), # Standard 15s fractional render allowance
        "pro": Decimal("14.00")        # Buffer for premium Wan2.2 models
    }

    # ── BLOCK 1: PREDICTIVE GATE (Before execution) ──
    async def pre_check(self, gen_id: str, est_cost: float, plan_tier: str) -> "PreCheckResult":
        """
        Circuit breaker for user actions.
        Prevents API dispatch if the estimated cost will push the total over the ceiling.
        """
        key = f"cogs:{gen_id}"
        # Fetch current accumulated spend from fast cache
        current = Decimal(await redis_db2.hget(key, "total") or "0")
        ceiling = self.CEILING[plan_tier]
        
        projected = current + Decimal(str(est_cost))
        ok = projected <= ceiling
        
        return PreCheckResult(ok=ok, current_cogs=current, projected=projected)

    # ── BLOCK 2: IMMUTABLE LEDGER (After execution) ──
    async def record(self, gen_id: str, cost_inr: float, worker: str, model_used: str) -> None:
        """
        Records the actual API cost. 
        MUST fire regardless of safety/output validation so we don't bleed hidden tokens.
        """
        key = f"cogs:{gen_id}"
        
        # 1. Update Redis (Fast path for subsequent pre_checks)
        await redis_db2.hincrbyfloat(key, "total", cost_inr)
        await redis_db2.expire(key, 24 * 3600)
        
        # 2. Update Postgres (Immutable Audit Log for Billing/Analytics)
        await db.execute(
            """INSERT INTO agent_traces (gen_id, worker, model_used, cost_inr, selection_reason) 
               VALUES ($1, $2, $3, $4, $5)""", 
            gen_id, worker, model_used, Decimal(str(cost_inr)), f"{worker} via {model_used}"
        )

    # ── BLOCK 3: POST-HOC AUDIT (End of lifecycle) ──
    async def check_post_hoc(self, gen_id: str) -> None:
        """
        Called by phase4_coordinator after the final 15s video preview is ready. 
        Graceful Degradation: If COGS overshoots due to fallbacks, we DO NOT block 
        the user. We emit an alert for engineering to tune the routing weights.
        """
        gen = await db.fetchrow("SELECT cogs_total, plan_tier FROM generations WHERE gen_id=$1", gen_id)
        if not gen: return
            
        ceiling = self.CEILING[gen["plan_tier"]]
        actual_cost = Decimal(str(gen["cogs_total"]))
        
        if actual_cost > ceiling:
            # Emits to Prometheus for Grafana dashboard alerting
            COGS_OVERSHOOT_TOTAL.labels(plan_tier=gen["plan_tier"]).inc()
            logger.warning(
                f"COGS OVERSHOOT | gen={gen_id} | actual={actual_cost} INR | ceiling={ceiling} INR"
            )
```

---


---


## [TDD-GUARDS] · OutputGuard & ComplianceGate

**Fulfills PRD Requirement:** `[PRD-FEATURES-COMPLIANCE]`, `[PRD-NON-NEGOTIABLES]`, `[PRD-HD3]`, `[PRD-COPILOT]`

Two symmetric safety gates surround every LLM call (especially in the Copilot chain). `ComplianceGate` operates on the input side (zero cost, regex-based). `OutputGuard` operates on the output side (API-based, regex-based).

**Crucial Chain Ordering:** In the 5-Stage API Chain, cost is recorded (Stage 4) _before_ output is validated (Stage 5). This guarantees that users who intentionally trigger safety filters still consume their wallet credits, preventing malicious budget-draining (DDoS-via-LLM).

### [TDD-GUARDS]-A · ComplianceGate · Input-Side

**Purpose:** Defend the system against Prompt Injections and invisible control characters. Operates entirely in memory for 0ms latency overhead.

```
import re

class ComplianceGate:
    """
    Input-side guard. 
    Runs as Stage 1 of the 5-stage chat chain + on every /generate request.
    """
    
    # ── BLOCK 1: MALICIOUS PATTERNS ──
    # Standard heuristic patterns to catch 95% of casual prompt injection attempts.
    INJECTION_PATTERNS = [
        r"ignore (?:previous|all|above) (?:instructions?|rules?)",
        r"you are (?:now )?(?:a |an )?(?:different|new) (?:ai|assistant|model)",
        r"system (?:prompt|message|instruction)[\s:]",
        r"</?(?:system|user|assistant)>",
        r"<\|(?:system|user|assistant)\|>",
    ]

    # ── BLOCK 2: THE MAIN VALIDATOR ──
    async def check_input(self, text: str) -> "ComplianceResult":
        """
        Validates user input. Completely synchronous/CPU-bound.
        """
        # 1. Control Character Sanitization
        # Prevents users from using invisible unicode to bypass filters or break parsers.
        sanitized = text.translate(str.maketrans('', '', ''.join(chr(c) for c in range(0, 32) if c not in (9, 10, 13))))
        sanitized = re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', sanitized)
        
        if sanitized != text:
            return ComplianceResult(safe=False, reason="control_chars")

        # 2. Injection Pattern Detection
        low = text.lower()
        for pat in self.INJECTION_PATTERNS:
            if re.search(pat, low):
                return ComplianceResult(safe=False, reason="prompt_injection")

        # Note: Word count constraints (e.g., max 500 chars) are handled 
        # upstream by FastAPI/Pydantic validation, not here.
        
        return ComplianceResult(safe=True, reason=None)
```

### [TDD-GUARDS]-B · OutputGuard · Output-Side

**Purpose:** Defend the brand and the end-consumer against AI hallucinations, competitor references, and PII leaks.

```
import re

class OutputGuard:
    """
    Output-side guard. 
    Stage 5 of the 5-stage chat chain + runs on every worker output 
    that will ultimately be surfaced to the user or rendered into a video.
    """
    
    def __init__(self, gateway):
        # ── ARCHITECTURAL INVARIANT ──
        # Inject the ModelGateway. We NEVER import openai_client directly.
        # This routes moderation requests through our aggregator/circuit breakers.
        self.gateway = gateway

    # ── BLOCK 1: THE MAIN VALIDATOR ──
    async def check_output(self, text: str) -> "OutputResult":
        """
        Scans the LLM's generated script for brand-safety violations.
        """
        # 1. AI Moderation API Call (NSFW, Violence, Hate Speech)
        mod_result = await self.gateway.route(
            capability="moderation", 
            input_data={"text": text}
        )
        if not mod_result.get("safe", True):
            return OutputResult(safe=False, reason="moderation_flagged")

        # 2. Local PII Check (Aadhaar, Email, Phone)
        pii = self._pii_scan(text)
        if pii:
            return OutputResult(safe=False, reason=f"pii:{pii}")

        # 3. Local Competitor Check
        comp = self._competitor_scan(text)
        if comp:
            return OutputResult(safe=False, reason=f"competitor:{comp}")

        return OutputResult(safe=True, reason=None)


    # ── BLOCK 2: LOCAL SCANNERS (Regex/String matching) ──
    def _pii_scan(self, text: str) -> str | None:
        """
        Ensures the AI didn't hallucinate random real-world personal data.
        Crucial for IT Rules 2026 data privacy compliance.
        """
        for pattern, pii_type in [
            (r'\b\d{10}\b', 'phone'),                        # 10-digit Indian mobile
            (r'\b[\w.+-]+@[\w-]+\.[\w.]+\b', 'email'),       # Basic email structure
            (r'\b\d{4}\s?\d{4}\s?\d{4}\b', 'aadhaar'),       # 12-digit Aadhaar pattern
        ]:
            if re.search(pattern, text):
                return pii_type
        return None

    def _competitor_scan(self, text: str) -> str | None:
        """
        Prevents the AI from accidentally recommending a competitor 
        if it pulls from its training data instead of our frameworks.
        """
        # Hardcoded list of direct AI-video/design competitors
        for comp in ["creatify", "invideo", "canva", "runway", "pika", "oxolo", "vidyo"]:
            if comp in text.lower():
                return comp
        return None
```

---


---


## [TDD-FLYWHEEL] · Data Flywheel & Style Memory

**Fulfills PRD Requirement:** `[PRD-MOATS]`, `[PRD-FEATURES-CREATIVE]`, `[PRD-FEATURES-RETENTION]`, `[PRD-AGENTIC-DRAFT]`

Style Memory is the first-party flywheel. Every successful export upserts a single row in `user_style_profiles` keyed by `(user_id, category)`. `pgvector` cosine similarity over the embedded script text powers the "Magic Defaults" on HD-2 after the user has exported ≥ 2 generations in a category.

### [TDD-FLYWHEEL]-A · Style Memory · Opt-In pgvector

```
import asyncio
import logging

logger = logging.getLogger(__name__)

class StyleMemory:
    """
    Pillar 4 (Data-Intensive): Single-row upsert per (user_id, category).
    Uses pgvector cosine similarity. Strict 200ms budget timeout.
    """
    
    # Matches the dimensionality of the selected embedding model
    EMBEDDING_DIM = 768 # Updated for standard open-source/aggregator models
    
    def __init__(self, gateway):
        # ── ARCHITECTURAL INVARIANT ──
        # Inject the ModelGateway. We NEVER import openai_client directly.
        self.gateway = gateway

    # ── BLOCK 1: UPSERT (The Learning Phase) ──
    async def upsert_on_export(self, gen_id: str, user_id: str) -> None:
        """
        Triggered by Worker-EXPORT upon successful video creation.
        Learns the user's preferred framework, language, and motion styles.
        """
        gen = await db.fetchrow(
            """SELECT product_brief, refined_script, safe_scripts, selected_script_id, 
                      motion_archetype_id, environment_preset_id, tts_language 
               FROM generations WHERE gen_id = $1""", 
            gen_id
        )
        if not gen: return
            
        category = gen["product_brief"]["category"]
        selected = gen["refined_script"] or gen["safe_scripts"][(gen["selected_script_id"] or 1) - 1]
        preferred_framework = selected.get("framework")
        
        # Call the ModelGateway to generate a vector embedding of the winning script
        embedding = await self._embed(selected["full_text"], gen_id)
        
        # Atomic Upsert: If the user has made a shoe ad before, update their preferences.
        await db.execute(
            """INSERT INTO user_style_profiles 
               (user_id, category, language, motion_archetype, environment_preset, 
                preferred_framework, embedding, export_count, last_used_at) 
               VALUES ($1, $2, $3, $4, $5, $6, $7, 1, NOW()) 
               ON CONFLICT (user_id, category) DO UPDATE SET 
                  language = EXCLUDED.language, 
                  motion_archetype = EXCLUDED.motion_archetype, 
                  environment_preset = EXCLUDED.environment_preset, 
                  preferred_framework = EXCLUDED.preferred_framework, 
                  embedding = EXCLUDED.embedding, 
                  export_count = user_style_profiles.export_count + 1, 
                  last_used_at = NOW()""", 
            user_id, category, gen["tts_language"], gen["motion_archetype_id"], 
            gen["environment_preset_id"], preferred_framework, embedding
        )

    # ── BLOCK 2: RETRIEVAL (The Prediction Phase) ──
    async def get_defaults(self, user_id: str, category: str) -> dict | None:
        """
        Triggered by API HD-2 (Brief Ready). 
        Fetches the user's learned preferences. Strict 200ms timeout prevents
        the "Magic Defaults" feature from slowing down the core user experience.
        """
        try:
            async with asyncio.timeout(0.2):
                row = await db.fetchrow(
                    """SELECT language, motion_archetype, environment_preset, 
                              preferred_framework, export_count 
                       FROM user_style_profiles 
                       WHERE user_id = $1 AND category = $2""", 
                    user_id, category
                )
                
                # PRD Business Rule: Only apply magic defaults if the user has
                # explicitly validated this style by paying for it twice.
                if row and row["export_count"] >= 2:
                    return dict(row)
                    
        except asyncio.TimeoutError:
            # Metric for Grafana: If this spikes, our Postgres DB is under heavy load.
            STYLE_MEMORY_TIMEOUT_TOTAL.inc()
            
        return None

    async def _embed(self, text: str, gen_id: str) -> list[float]:
        """
        Generates a vector embedding using the aggregator gateway.
        """
        resp = await self.gateway.route(
            capability="embedding",
            input_data={"text": text, "gen_id": gen_id}
        )
        return resp.embedding_data
```

### [TDD-FLYWHEEL]-B · Signals Table · User Behavior Telemetry

The `user_signals` table captures granular positive/negative/neutral events per stage. This powers the internal admin dashboard and allows engineering to tune safety filters without guessing.

| signal_type                    | polarity | stage                | Use Case (Why we track this)                            |
| ------------------------------ | -------- | -------------------- | ------------------------------------------------------- |
| `lock_fail`                    | negative | phase3, phase4_retry | Triggers UX experiments for the Top-Up Drawer           |
| `cb_state_change`              | neutral  | any                  | Powers internal Provider Health dashboards              |
| `export_retry_dispatched`      | neutral  | phase4_retry         | Tracks how often the C2PA worker fails                  |
| `export_retry_count_exhausted` | negative | phase4_retry         | Alerts engineering to systemic pipeline failure         |
| `stale_declaration_rejected`   | negative | phase4_retry         | Tracks frequency of ECM-020 (User waited >24h to retry) |
| `inline_resign_accepted`       | positive | phase4_retry         | Measures conversion rate of inline legal re-signing     |
| `chat_compliance_rejected`     | negative | phase2               | Measures the Prompt-Injection attempt rate              |
| `chat_costguard_rejected`      | negative | phase2               | Indicates the ₹10 Cost Ceiling might be too restrictive |
| `chat_outputguard_rejected`    | negative | phase2               | Measures AI hallucination/brand-safety failure rate     |
| `chat_turn_complete`           | positive | phase2               | Measures overall Copilot Chat adoption                  |
| `framework_fallback_triggered` | neutral  | phase2               | Assesses the quality of LLM JSON routing schema         |


---


---


## [TDD-STRATEGY] · Strategy Card & Chat Engine Contracts

**Fulfills PRD Requirement:** `[PRD-HD3]`, `[PRD-HD4]`, `[PRD-COPILOT]`, `[PRD-AGENTIC-DRAFT]`

This section defines the strict operational boundaries for the UI representations of AI state (The Strategy Card) and the interactive AI modification loops (The Copilot Chat).

### [TDD-STRATEGY]-A · Strategy Card Contract (HD-4)

The Strategy Card is the final "checkout" summary presented to the user on HD-4 before they commit their wallet funds.

1. **Projection, Not Truth:** The Strategy Card is computed dynamically by `Worker-STRATEGIST` (`[TDD-WORKERS]-G`). It is a read-only projection of the `generations` row at a specific point in time.
    
2. **Idempotency:** Regenerating the Strategy Card is perfectly idempotent and safe. If the UI needs to refresh it, the worker simply re-reads the DB state and rebuilds the JSON payload.
    
3. **Volatility:** When a user clicks an [Edit] target on HD-4 (triggering `[TDD-API]-E`), the Strategy Card JSON is explicitly set to `NULL` in the database. This guarantees that stale data is never accidentally rendered if the user modifies their underlying choices.
    

### [TDD-STRATEGY]-B · Chat Engine Specification (HD-3)

The chat engine's canonical implementation is handled by the 5-Stage Chain in `[TDD-API]-C`. This specification defines the non-implementation business rules the Agentic IDE must enforce globally:

1. **The Turn Limit (Strict Cap):** * Maximum **3 turns** per generation.
    
    - After 3 successful turns, the `chat_turns_used` counter hits the limit.
        
    - **Forward Path Only:** Once the limit is reached, the chat interface must lock, and "Continue to Strategy" becomes the only permitted forward path.
        
2. **Mandatory Execution Path:** * Every turn must run the complete 5-stage chain (`[TDD-API]-C`). No "fast paths" or skips are allowed, even for trivial requests.
    
3. **Budget & Ledger Accounting for Rejections:**
    
    - **Input-Side Rejections:** If a turn is rejected by `ComplianceGate` or the `CostGuard` pre-check, the LLM is never invoked. Therefore, COGS remain untouched, and the `chat_turns_used` budget is **NOT** decremented.
        
    - **Output-Side Rejections:** If a turn is rejected by `OutputGuard` (e.g., the LLM hallucinates a competitor's name), the API cost has already been incurred. The cost **MUST** be preserved in the `cogs_total` ledger, but the `chat_turns_used` budget is **NOT** decremented (since the user didn't get a usable result). The generation is still protected globally by the `CostGuard` ceiling.
        
4. **Cache Bypassing:** * Rejected turns (4xx/5xx HTTP codes) are **NOT** cached by the `@idempotent` decorator. The decorator is strictly configured for `cache_only_2xx=True` to prevent users from getting permanently stuck by a transient moderation flag.
    
5. **Architectural Preservation:** * Chat refinement must strictly preserve the underlying strategic structure. The LLM prompt MUST instruct the model to maintain the original `framework` and `framework_angle` assigned during Phase 2. Chat is for tweaking tone and copy, not for silently overriding the core marketing strategy.

---


---


## [TDD-DLQ] · Dead-Letter Queue Handler · Dual-Branch Routing

**Fulfills PRD Requirement:** `[PRD-ERROR-MATRIX]`, `[PRD-HD5]`, `[PRD-HD6]`, `[PRD-PAYMENT-FSM]`, `[PRD-FEATURES-INFRA]`, `[PRD-NON-NEGOTIABLES]`

`on_job_dead` converts an exhausted retry count into a persistent terminal FSM state + compensating wallet refund. The handler dispatches on `job.function_name`, not on the generation's current state — this is the **Dual-Branch DLQ invariant**. Because we separated rendering (15s fractional stitch) from exporting (C2PA signing), a dead job belongs to either `phase4_coordinator` or `worker_export`. These map to different FSM terminals, different ECM error codes, and different SSE events wired to different HD screens.

### [TDD-DLQ]-A · Handler Implementation

```
import logging
import asyncpg

logger = logging.getLogger(__name__)

async def on_job_dead(ctx, job: "ArqJob"): 
    """
    Pillar 5 (Release It!): Compensating transaction on dead jobs. 
    Executes Dual-Branch routing based on job.function_name.
    """
    gen_id = job.kwargs.get("gen_id")
    if not gen_id:
        logger.error(f"DLQ job {job.function_name} has no gen_id; cannot recover")
        return 
        
    function_name = job.function_name
    logger.error(
        f"DLQ fire: function={function_name} gen_id={gen_id} " 
        f"attempts={job.job_try} last_error={job.last_error}"
    )
    
    # Prometheus Metric for systemic alerting
    DLQ_DEAD_TOTAL.labels(function=function_name).inc()
    
    # ── BLOCK 1: DUAL-BRANCH ROUTING ──
    if function_name == "phase4_coordinator": 
        # The 15s Smart-Stitch failed (e.g., Fal.ai outage or FFmpeg crash)
        target_state = "failed_render"
        error_code = "ECM-005"
        failure_stage = "phase4_render"
        sse_event = "render_failed"
    elif function_name == "worker_export": 
        # The C2PA Cryptographic signing failed (e.g., Rust binary crash)
        target_state = "failed_export"
        error_code = "ECM-016"
        failure_stage = "phase4_export"
        sse_event = "export_failed"
    else:
        # Failsafe: Do not accidentally refund for background maintenance jobs
        logger.warning(f"DLQ: unmapped function {function_name} for gen_id={gen_id}")
        return
        
    # ── BLOCK 2: ATOMIC REFUND & STATE UPDATE ──
    async with db.transaction():
        gen = await db.fetchrow("SELECT user_id, status FROM generations WHERE gen_id = $1 FOR UPDATE", gen_id)
        if not gen: return 
        
        user_id = gen["user_id"]
        
        # Step A: Idempotent Refund (Ledger First)
        try:
            # 1. Postgres Ledger (Source of Truth)
            await db.execute(
                """INSERT INTO wallet_transactions (user_id, type, credits, status, gen_id) 
                   VALUES ($1, 'refund', 1, 'refunded'::wallet_status, $2)""", 
                user_id, gen_id
            )
            
            # 2. Redis Fast-Cache
            await redis_lua.wallet_refund(user_id=user_id, gen_id=gen_id)
            await redis_db0.hincrby(f"wallet:{user_id}", "balance", 1)
            
            # 3. User Table Sync
            await db.execute("UPDATE users SET credits_remaining = credits_remaining + 1 WHERE user_id = $1", user_id)
            
        except asyncpg.UniqueViolationError:
            # Prevent Double-Refund: The DB already has a refund for this gen_id.
            REFUND_DEDUP_HITS.inc()
            
        # Step B: Mark the original lock as refunded for auditability
        await db.execute(
            """UPDATE wallet_transactions SET status = 'refunded'::wallet_status 
               WHERE gen_id = $1 AND type = 'lock' AND status = 'locked'""", 
            gen_id
        )
        
        # Step C: Terminal State Update
        await db.execute(
            """UPDATE generations SET status = $2, error_code = $3, 
                  dlq_dead_at = NOW(), dlq_original_task = $4 
               WHERE gen_id = $1""", 
            gen_id, target_state, error_code, function_name
        )
        
        # Step D: Alert the UI to display the fallback screen (HD-5 or HD-6)
        await sse_manager.push(gen_id, { 
            "type": sse_event, "state": target_state, 
            "error_code": error_code, "failure_stage": failure_stage 
        })
```

### [TDD-DLQ]-B · Invariants

1. **Ledger-first refund:** The `wallet_transactions` INSERT precedes the Redis Lua refund. If a `UniqueViolationError` occurs, it means the refund was already applied (e.g., due to a zombie worker). We gracefully catch this and increment `REFUND_DEDUP_HITS`.
    
2. **Function-name dispatch:** `job.function_name` is the _only_ dispatch key. The DLQ must never branch on `gen.status`, because the worker might have died mid-transition leaving the FSM state ambiguous.
    
3. **Forensic Logging:** `dlq_original_task` is captured so forensic queries can reconstruct which specific worker pipeline killed the generation.
    
4. **No Cascading Enqueues:** The DLQ halts the pipeline. Recovery is strictly **user-initiated**: `failed_render` requires the user to click retry on HD-5 to trigger `/approve-strategy` (re-lock); `failed_export` requires the user to trigger `/retry-export` on HD-6.
    
5. **Unknown Job Safety:** Unmapped function names short-circuit with a warning log and _never_ trigger a refund.
---


---


## [TDD-DIRECTOR] · Director's Suggestion Engine

**Fulfills PRD Requirement:** `[PRD-HD2]`, `[PRD-CONFIDENCE]`, `[PRD-AGENTIC-DRAFT]`, `[PRD-FEATURES-CREATIVE]`

The Director's Tips surfaced on the HD-2 (Brief Ready) screen are a pure deterministic read of two sources: the `confidence_score` generated by `Worker-EXTRACT` (Phase 1) and category-keyed static copy from the `director_tips` table.

**Architectural Rule:** There is NO LLM call involved in the Director's Suggestion Engine. All suggestions are pre-authored to guarantee 0ms latency and ₹0.00 execution cost.

### [TDD-DIRECTOR]-A · Confidence Gating Matrix

This matrix dictates exactly how the HD-2 UI behaves based on the Vision model's certainty.

|Confidence Score|UI Flag|Surface Behavior|Fields Populated|
|---|---|---|---|
|**≥ 0.90 (HIGH)**|🟢 Green|★ Recommended defaults enabled. Suggests specific camera motions.|`agent_crop_suggestion` & `agent_motion_suggestion` are non-NULL.|
|**0.85 – 0.89 (MED)**|🟡 Yellow|"Please confirm" tooltip shown. Suggests category, but no Magic Defaults.|Suggestions shown but NOT ★-badged.|
|**< 0.85 (LOW)**|🔴 Red|"Manual category selection recommended" warning. UI defaults to empty.|`agent_crop_suggestion` = NULL, `agent_motion_suggestion` = NULL.|

### [TDD-DIRECTOR]-B · Tips Table Schema

A static, pre-populated table that stores the conversational "Director" advice shown to the user on HD-2.

```
CREATE TABLE IF NOT EXISTS director_tips (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,          -- e.g., 'skincare', 'electronics'
    tip_type TEXT NOT NULL,          -- e.g., 'lighting', 'motion'
    copy_en TEXT NOT NULL,           -- English tip (e.g., "Use harsh shadows to highlight the tech.")
    copy_hi TEXT NOT NULL,           -- Hindi localization
    min_confidence NUMERIC(3,2) NOT NULL DEFAULT 0.85, -- Only show if vision score >= this
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (category, tip_type, copy_en)
);
```

### [TDD-DIRECTOR]-C · Architectural Invariants

1. **Category Isolation:** Tips must never leak across categories. A skincare tip must never appear on an electronics generation. Enforced via database constraint: `CHECK category IN (SELECT unnest(enum_range(NULL::greenzone_category)))`.
    
2. **Read-Only Telemetry:** Director's Tips are UI additive features only. They are NOT routing inputs. The `Worker-ROUTER` (Phase 2) does _not_ read the `director_tips` table; it relies strictly on the `product_brief` and `confidence_score`.
    
3. **Silent Degradation:** Agentic suggestions must degrade silently and safely. If `confidence_score < 0.85`, the UI renders the Red flag and drops the user into manual mode. The Agentic Draft Model is explicitly forbidden from forcing a low-confidence guess into the FSM state.

---


---


## [TDD-SECURITY] · Security Model · JWT · Auth Matrix · Razorpay HMAC

**Fulfills PRD Requirement:** `[PRD-NON-NEGOTIABLES]`, `[PRD-FEATURES-PAYMENT]`, `[PRD-FEATURES-COMPLIANCE]`, `[PRD-FEATURES-INFRA]`, `[PRD-PAYMENT-FSM]`

This layer defines the cryptographic and access-control boundaries of Adcreo. It ensures that money, API credentials, and legal audit logs are mathematically secured against both external attacks and internal bugs.

### [TDD-SECURITY]-A · JWT with Session Versioning

**Purpose:** Provides instant, stateless token revocation without the latency/cost of a Redis blocklist.

```
import jwt
from fastapi import HTTPException

class JWTAuth:
    """
    Handles Stateless Authentication.
    Access tokens have a 24h TTL. No refresh tokens in MVP.
    """
    
    async def verify(self, token: str) -> dict:
        """
        Validates the JWT and checks the session version against the DB.
        """
        try:
            # 1. Decode token. 
            # SECURITY: explicitly define algorithms=["HS256"] to prevent algorithm-substitution attacks.
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            raise HTTPException(401, "Invalid or expired token")
            
        # 2. Fetch the user's CURRENT state from the DB
        user = await db.fetchrow(
            "SELECT user_id, plan_tier, session_version FROM users WHERE user_id=$1", 
            payload["user_id"]
        )
        
        if not user:
            raise HTTPException(401, "User not found")
            
        # 3. The "Stateless Revocation" Check
        # If user changed password or plan, their DB session_version bumped.
        # This instantly invalidates any old, outstanding tokens.
        if payload["session_version"] != user["session_version"]:
            raise HTTPException(401, "Session invalidated. Please log in again.")
            
        return dict(user)
```



JWT minting reads `users.beta_invited` and embeds it as the `beta` claim. Auth dependency `get_current_user` rejects (HTTP 403, ECM-006-style) any request from a user where `beta_invited=FALSE` while the global feature flag `beta_gate_active` is TRUE.


### [TDD-SECURITY]-B · Authorization Matrix

**Purpose:** Strict enforcement of the Principle of Least Privilege. Limits what data the L2 API surface and internal Workers can read/mutate.

|Resource|Owner Column|Read Scope|Mutation Scope|
|---|---|---|---|
|`generations`|`user_id`|Owner only|Owner only (via guarded L2 routes)|
|`wallet_transactions`|`user_id`|Owner only|**Internal Only** (L2 routes + DLQ handler)|
|`audit_log`|`user_id`|Internal-only|**Append-Only**; DB revokes UPDATE/DELETE to app role|
|`user_style_profiles`|`user_id`|Owner only|`Worker-EXPORT` only (upsert)|
|`grievances`|`user_id`|Owner + Ops|Owner (create) + Ops-Role (resolve)|
|`director_tips`|—|All authenticated|Seed script only (Static Table)|
|`agent_traces`|`gen_id`→`user_id`|Owner (aggregated)|Workers: COPY, TTS, I2V, STRATEGIST|

### [TDD-SECURITY]-C · Razorpay Webhook HMAC

**Purpose:** Prevents hackers from spoofing payment webhooks and giving themselves free credits.

```
import hmac
import hashlib
from fastapi import HTTPException

def verify_razorpay_signature(raw_body_bytes: bytes, header_sig: str) -> bool:
    """
    Cryptographically verifies that a webhook originated from Razorpay.
    """
    if not header_sig:
        return False
        
    # 1. Generate the expected signature using our private secret
    expected = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(), 
        raw_body_bytes, 
        hashlib.sha256
    ).hexdigest()
    
    # 2. Constant-Time Comparison
    # SECURITY: Never use `expected == header_sig`. It is vulnerable to timing attacks.
    # hmac.compare_digest takes the exact same time to execute regardless of the string mismatch.
    if not hmac.compare_digest(expected, header_sig):
        raise HTTPException(400, "Invalid signature: Potential Spoofing Attack Detected")
        
    return True
```

> _Replay Defense:_ Razorpay webhooks carry an `event.id`. The webhook endpoint dedups these via a partial `UNIQUE` index on `wallet_transactions(razorpay_payment_id)`. If a hacker intercepts and replays a valid webhook, Postgres rejects the duplicate insert, and the API returns a safe, no-op `200 OK`.

### [TDD-SECURITY]-D · Secrets Hygiene & Log Sanitization

**Purpose:** Ensures no API keys or PII ever leak into our logging infrastructure (Datadog/Grafana), protecting us from insider threats and satisfying IT Rules 2026.

1. **Environment Isolation:** All secrets (`JWT_SECRET`, `RAZORPAY_WEBHOOK_SECRET`, Model Aggregator keys, Firecrawl tokens) live strictly in the Hetzner container's environment variables. They are NEVER hardcoded in the repo.
    
2. **Runtime Log Redaction:** Structured log emitters in `app/logging/sanitize.py` maintain an aggressive denylist key-matcher (`authorization`, `razorpay_signature`, `api_key`, `secret`, `token`). If these keys appear in any dictionary being logged, their values are physically replaced with `***REDACTED***` before the string is written to `stdout`.
    
3. **CI Pipeline Gates:** The GitHub Action `compliance-gate` runs a regex grep against all PRs for literal keys matching common patterns (e.g., `sk-*`, `rzp_live_*`, `rzp_test_*`). If a developer accidentally commits an active key, the PR immediately fails the build and blocks merging.
---


---


## [TDD-TAKEDOWN] · IT Rules 2026 Auto-Takedown Pipeline

**Fulfills PRD Requirement:** `[PRD-FEATURES-COMPLIANCE]`, `[PRD-FEATURES-RETENTION]`, `[PRD-NON-NEGOTIABLES]`, `[PRD-ERROR-MATRIX]`, F-506, F-610

IT Rules 2026 require platforms to Acknowledge (ACK) grievances within 24 hours and resolve them within 15 days to maintain "Safe Harbour" protections under the IT Act. Adcreo implements a fully automated, zero-touch content-takedown path to guarantee compliance without relying on human support agents.

### [TDD-TAKEDOWN]-A · Endpoint POST /api/grievance

**Purpose:** The public-facing entry point for IP violations, deepfakes, or privacy reports.

```
@router.post("/api/grievance", status_code=202)
async def create_grievance(payload: GrievanceRequest, db=Depends(get_db)):
    """
    Step 1: The Instant Receiver.
    Guarantees < 24h ACK by responding instantly and enqueueing a background worker.
    """
    # LEGAL LOGIC: Calculate the strict 24-hour Service Level Objective (SLO) deadline.
    deadline = datetime.utcnow() + timedelta(hours=24)
    
    # SYSTEM LOGIC: Save the complaint to the database immediately.
    grievance_id = await db.fetchval(
        """INSERT INTO grievances (type, gen_id, description, contact_email, status, slo_deadline_ts) 
           VALUES ($1, $2, $3, $4, 'received', $5) RETURNING id""", 
        payload.type, payload.gen_id, payload.description, payload.contact_email, deadline
    )
    
    # SYSTEM LOGIC: Tell the background worker to start deleting the content.
    await arq_pool.enqueue_job("grievance_processor", grievance_id)
    
    # LEGAL LOGIC: Return '202 Accepted' instantly with a Ticket ID. 
    # This acts as the legal receipt for the victim.
    return {"ticket_id": grievance_id, "slo_deadline_ts": deadline.isoformat()}
```

### [TDD-TAKEDOWN]-B · Automated Content-Violation Pipeline

**Purpose:** The execution arm. Physically destroys the offending content and permanently modifies the user's state so the video can never be accessed again.

```
import logging

logger = logging.getLogger(__name__)

async def grievance_processor(ctx, grievance_id: int): 
    """
    Step 2: The Terminator.
    Background worker that resolves the ticket automatically by deleting the files.
    """
    g = await db.fetchrow("SELECT * FROM grievances WHERE id=$1", grievance_id)
    if not g: return
        
    if g["type"] == "content_violation":
        # SYSTEM LOGIC: Update the database so the user's dashboard no longer shows the video link.
        # Setting error_code to 'TAKEDOWN' lets the frontend show a red "Removed for Violation" badge.
        await db.execute(
            """UPDATE generations SET exports = NULL, error_code = 'TAKEDOWN' 
               WHERE gen_id = $1""", 
            g["gen_id"]
        )
        
        # SYSTEM LOGIC: Find exactly where the video is stored in Cloudflare R2.
        gen = await db.fetchrow("SELECT preview_url, exports FROM generations WHERE gen_id=$1", g["gen_id"])
        
        # SYSTEM LOGIC: Physically obliterate the MP4 file from the internet.
        if gen and gen.get("preview_url"):
            await r2_client.delete_object(gen["preview_url"])
            
        # LEGAL LOGIC: Mark the ticket as 'resolved' to stop the SLA Watchdog timer.
        await db.execute(
            "UPDATE grievances SET status='resolved', resolved_at=NOW() WHERE id=$1", 
            grievance_id
        )
        
        # LEGAL LOGIC: Write to the immutable Audit Log. 
        # If the government asks for proof that we deleted it, this is our evidence.
        await db.execute(
            """INSERT INTO audit_log (gen_id, action, payload) 
               VALUES ($1, 'takedown_executed', $2::jsonb)""", 
            g["gen_id"], json.dumps({"grievance_id": grievance_id, "resolved_ts": datetime.utcnow().isoformat()})
        )
```

> _Takedown vs. Standard Retention:_ Normal retention sweeps (e.g., deleting 7-day old free ads) are slow, time-based CRONs. Takedowns are event-based and immediate. A legal takedown order overrides ALL standard retention rules.

### [TDD-TAKEDOWN]-C · SLA Watchdog

**Purpose:** Failsafe mechanism. Ensures no ticket ever breaches the legal resolution limits if a server crashes.

```
# CRON Job: Runs automatically every 5 minutes
async def sla_watchdog():
    """
    Step 3: The Alarm Bell.
    Fires a (Alerting:
- Handled via Grafana Cloud alerts
   P0 alert for any unresolved grievances nearing their legal deadline.
    """
    # SYSTEM LOGIC: Find any ticket that is NOT resolved, where the 24-hour deadline 
    # is less than 1 hour away.
    breaches = await db.fetch(
        """SELECT id, type, slo_deadline_ts FROM grievances 
           WHERE status <> 'resolved' AND slo_deadline_ts < NOW() + INTERVAL '1 hour'"""
    )
    
    if breaches:
        # LEGAL/OPS LOGIC: Wake up the engineering team immediately.
        # This prevents the company from losing Safe Harbour status.
        trigger_p0_alert(f"CRITICAL: IT Rules 2026 SLA Breach Imminent for {len(breaches)} tickets. Manual intervention required immediately.")
```

### [TDD-TAKEDOWN]-D · Architectural Invariants

1. **Irreversibility:** Takedown is a one-way street. Once `error_code='TAKEDOWN'` is set and the R2 file is deleted, there is no "Restore" or "Undo" function in the codebase.
    
2. **Mandatory Audit Trail:** Every takedown MUST write to `audit_log` with the `content_id`, `requester_id` (if available), `slo_deadline_ts`, and `resolved_ts`. This provides legal proof of compliance for Indian courts.
    
3. **Ghost Purges (Handling Missing Files):** If a takedown request targets a `Starter` tier generation that is past its 7-day retention limit, the physical files were already deleted by normal cleanups. The system must handle this gracefully (logging a no-op resolution), rather than crashing.


---


---

## [TDD-CICD] · CI/CD Pipeline *(Category 2A — REPLACED)*

The previous `[TDD-CICD]-A` defined 10 flat parallel jobs without explicit ordering. This section replaces that with a four-stage pipeline. Failure in an earlier stage prevents later stages from running, conserving runner minutes and producing faster feedback.

The four stages are: **Static Analysis → Unit and Logic Tests → Integration and Contract Tests → E2E**. Branch protection on `main` requires all four stages green before the Merge button activates. E2E is required on PR→main merges and on `hotfix/*` branches.

### [TDD-CICD]-A · Stage 1 — Static Analysis

**Triggers:** every push to every branch.
**Service containers:** none.
**Fail-fast contract:** if Stage 1 is red, Stages 2, 3, 4 do not run.

Jobs (all run in parallel):

| Job              | Command                                                                                                                                                    | Blocks Merge? |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `lint`           | `ruff check . && black --check .`                                                                                                                          | Yes           |
| `typecheck`      | `mypy app/`                                                                                                                                                | Yes           |
| `static-guards`  | Six scripts run sequentially within one job (see below).                                                                                                   | Yes           |

`static-guards` runs the following six scripts in this order. Any non-zero exit fails the job:

1. `ci/check_banned_patterns.py` — leaked keys, banned imports, `print()` statements.
2. `ci/validate_prompts.py` — LLM prompt template variable resolution.
3. `ci/strategist_sandbox_check.py` — import graph: STRATEGIST has zero `httpx` / `requests` / `aiohttp` imports. *(v4-Δ1: scope extended to `app/broll/`; additionally forbids `sentence_transformers`, `chromadb`, `faiss`, `transformers`, `torch` — see `[TDD-IMPORT-GRAPH]` and `[TDD-BROLL]-J`.)*
4. `ci/non_goals_guard.py` — bans non-goal keywords per PRD.
5. `ci/observability_lint.py` *(new — added in this version)* — asserts structured log emission in critical paths (CostGuard, wallet Lua wrapper, DLQ handler, state transition trigger). See `[TDD-OBSERVABILITY]`.
6. `ci/validate_env_manifest.py` *(new — added in this version)* — asserts `.env.example` is not stale relative to code references. Greps `os.getenv(...)` and `os.environ[...]` across `app/` and confirms every key appears in `.env.example` and in `[TDD-ENV-MANIFEST]`.
7. `ci/broll_coverage_check.py` *(v4-Δ1)* — asserts every `(angle, category_class, brand_tier)` triple resolvable via `TEMPLATE_BY_CONTEXT` has ≥ 1 active clip for each required role of the resolved template (per `[TDD-BROLL]-G` step 3). Also asserts every active season tag in `seasons` has ≥ 1 hook + 1 context clip with that tag in `seasonality_tags`. Blocks deploy on any uncovered combination. See `[TDD-BROLL]-J`.

### [TDD-CICD]-B · Stage 2 — Unit and Logic Tests

**Triggers:** every push; runs only if Stage 1 passes.
**Service containers:** none.

Jobs (all run in parallel):

| Job                   | Command                                                                                                                       |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `unit-test`           | `pytest tests/unit/ -v` — pure functions, no DB, no Redis, no network.                                                        |
| `fsm-test`            | `pytest tests/fsm/ --fsm-coverage` — 22-state DAG, all transitions, all illegal transitions, all `pre_topup_status` coupling. |
| `migration-dry-run`   | `python ci/run_migrations.py --dry-run` — schema diff only, no DB write.                                                      |

### [TDD-CICD]-C · Stage 3 — Integration and Contract Tests

**Triggers:** every PR; runs only if Stage 2 passes.
**Service containers required:** `postgres:15`, `redis:7`.
**Mandatory env (set in job env):** `AW_API_MODE=stub`, `TZ=Asia/Kolkata`.

Jobs (run in parallel):

| Job                | Command                       | Covers                                                                                                                                                                                                                                                       |
| ------------------ | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `integration-test` | `pytest tests/integration/ -v` | ARQ → Redis → Neon handshakes, wallet Lua scripts, DLQ dual-branch routing, Prometheus metric emission via Pushgateway, idempotency cache behaviour, **webhook idempotency** (`processed_webhooks` dedup — see `[TDD-CONCURRENCY]-F`). |
| `contract-test`    | `pytest tests/contract/ -v`    | API response schemas (incl. `screen_descriptor` per `[TDD-FSM]-SCREEN-CONTRACT`), Razorpay webhook HMAC validation, error code matrix, idempotency key replay behaviour.                                                                                     |

### [TDD-CICD]-D · Stage 4 — E2E

**Triggers:** PR→`main` merge AND nightly cron. Not on feature-branch pushes.
**Environment:** staging (real workers, real R2, `AW_API_MODE=stub`).

**Mandatory pre-job steps (Linux runner):**

```yaml
- name: Install ffmpeg (Linux)
  run: sudo apt-get update && sudo apt-get install -y ffmpeg

- name: Install c2patool (Linux)
  run: |
    curl -L https://github.com/contentauth/c2patool/releases/latest/download/c2patool-linux-x86_64.tar.gz -o c2patool.tar.gz
    tar -xzf c2patool.tar.gz
    sudo mv c2patool /usr/local/bin/
    c2patool --version

- name: Verify ffmpeg filters
  run: |
    ffmpeg -filters | grep -E 'lut3d|tpad|apad|drawtext' | wc -l | grep -q '^4$'
```

The `adcreo-tools/*.exe` Windows binaries from v3 are dev-machine artifacts only and MUST NOT be invoked from CI. The Linux binaries above are the canonical CI binaries.

| Job        | Description                                                                                                                                                                                                       |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `e2e-test` | Playwright: full HD-1 → HD-6 happy path + credit-lock → export flow + DLQ recovery flow + C2PA manifest verify via local `c2patool --verify`. Must run against staging with real R2 reads/writes (stubbed AI providers). |

### [TDD-CICD]-E · Branch Protection & Global CI Env

**Branch protection on `main`:** all four stages must be green before the Merge button activates. E2E is required for PRs to `main` and for `hotfix/*` branches.

**Global CI env vars (set unconditionally in every job, every stage):**

```yaml
env:
  AW_API_MODE: stub
  TZ: Asia/Kolkata
```

The `AW_API_MODE=stub` invariant per `[TDD-API-STUBS]-B` is preserved exactly. The `TZ=Asia/Kolkata` invariant is required for Postgres trigger time-window correctness.

### [TDD-CICD]-F · Prometheus Metrics Inventory

### [TDD-CICD]-B · Prometheus Metrics · Consolidated Inventory

Every backend service emits metrics. These are the raw signals scraped by Prometheus to monitor the financial and operational health of the application.

```
# ── FSM & STATE METRICS ──
# Tracks where users are in the app. A sudden drop in HD-4 means checkout is broken.
GENERATION_STATE_TOTAL = Counter('aw_generation_state_total', ['state', 'plan_tier'])

# ── FINANCIAL METRICS (The CFO Dashboard) ──
# Fired by CostGuard if the 15s fractional render or Copilot chat breaches the unit economic ceiling.
COGS_OVERSHOOT_TOTAL = Counter('aw_cogs_overshoot_total', ['plan_tier'])

# ── RELIABILITY METRICS ──
# Fired by [TDD-DLQ]. Tracks 'phase4_coordinator' (render fails) vs 'worker_export' (C2PA fails).
DLQ_DEAD_TOTAL = Counter('aw_dlq_dead_total', ['function'])
# Tracks the ModelGateway. If this spikes, an AI provider is down and we are auto-routing.
FALLBACK_EVENTS = Counter('aw_fallback_events_total', ['from_provider', 'to_provider', 'capability'])
# Tracks UI drop-offs and connection instability.
SSE_RECONNECT_TOTAL = Counter('aw_sse_reconnect_total')
# Fired by [TDD-FLYWHEEL] if the pgvector DB takes > 200ms to fetch Magic Defaults.
STYLE_MEMORY_TIMEOUT_TOTAL = Counter('aw_style_memory_timeout_total')

# ── DATA LIFECYCLE METRICS ──
REFUND_DEDUP_HITS = Counter('aw_refund_dedup_hits_total')
RETENTION_SWEEP_DELETIONS = Counter('aw_retention_sweep_deletions_total')
PARTITION_ROTATIONS = Counter('aw_partition_rotations_total', ['month'])

# ── AI QUALITY & ROUTING METRICS ──
# Tracks how often the LLM generated unsafe content that we had to auto-retry.
SAFETY_AUTORETRY_TOTAL = Counter('aw_safety_autoretry_total')
# Tracks which marketing frameworks the LLM is picking (e.g., PAS-Micro vs Feature-Benefit).
FRAMEWORK_SELECTION_DISTRIBUTION = Counter('aw_framework_selection_total', ['fallback', 'default_trio_satisfied'])
FRAMEWORK_PER_SELECTION = Counter('aw_framework_per_selection_total', ['framework'])
FRAMEWORK_FALLBACK_TRIGGERED = Counter('aw_framework_fallback_total', ['reason'])
# A histogram tracking the LLM CRITIC score of generated scripts (0-100).
FRAMEWORK_CRITIC_SCORE = Histogram('aw_framework_critic_score', ['framework'], buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

# ── LATENCY HISTOGRAMS ──
PHASE1_LATENCY = Histogram('aw_phase1_latency_s', buckets=[5, 10, 15, 20, 30])    # Firecrawl Extraction
PHASE2_LATENCY = Histogram('aw_phase2_latency_s', buckets=[3, 5, 8, 12, 20])      # LLM Generation
PHASE4_LATENCY = Histogram('aw_phase4_latency_s', buckets=[5, 10, 15, 30, 60])    # 15s fractional render (I2V + FFmpeg)
EXPORT_LATENCY = Histogram('aw_export_latency_s', buckets=[2, 5, 10, 15, 30])     # C2PA Rust Binary
```


### [TDD-CICD]-G · Grafana Dashboards

### [TDD-CICD]-C · Grafana Dashboards

Metrics are aggregated into visual dashboards for the team to monitor daily.

|Dashboard|Panels|
|---|---|
|**Generation Funnel**|State transitions per hour, Completion rate (HD1→HD6), Drop-off rate per phase.|
|**COGS per Tier**|Overshoot rate (Did we spend >₹10 on Essential?), Avg COGS per plan, Chat API cost distribution.|
|**Provider Health**|Circuit Breaker state (Open/Closed), Fallback events, API Latency per model (Groq, Fal, Sarvam).|
|**DLQ & Recovery**|Dead jobs by function, Refund success rate, Inline recovery actions.|
|**Retention & DB**|Sweeps per day, R2 object deletions, Partition rotations, pgvector timeout rate.|
|**Framework Routing**|Selection distribution, Fallback rate, CRITIC score percentiles per framework.|

### [TDD-CICD]-H · Framework Routing Observability

### [TDD-CICD]-D · Framework Routing Observability

Thresholds for automated alerts related to AI script generation quality.

|Metric|Alert Threshold|Severity|
|---|---|---|
|`aw_framework_fallback_total` `{reason="schema_violation"}`|rate > 5% in 1h|**P2** (LLM is failing to return valid JSON)|
|`aw_framework_selection_total` `{fallback="true"}`|rate > 30% in 24h|**P3** (Router is struggling to map frameworks)|
|`aw_framework_selection_total` `{default_trio_satisfied="false"}`|rate > 40%|**P3** (User briefs are getting poorly matched)|
|`aw_framework_critic_score`|p50 < 50 over 1k gens|**P3** (Copywriting quality degrades)|
|`aw_safety_autoretry_total`|rate > 1%|**P2** (OutputGuard is tripping constantly, burning money)|

### [TDD-CICD]-I · Alerting

The alert matrix is moved to `[TDD-OBSERVABILITY]` (Category 2B). The v3 `[TDD-CICD]-E` content is superseded by the consolidated alert matrix there. Do not duplicate.

---


## [TDD-IDE] · Antigravity Agentic IDE Directives

**Fulfills PRD Requirement:** `[PRD-META]`, `[PRD-SPRINTS]`, `[PRD-AGENTIC-DRAFT]`, `[PRD-NON-NEGOTIABLES]`

This section is strictly for the Agentic IDE (the AI coding assistant). It defines the Directed Acyclic Graph (DAG) for generating the codebase. The Agent must strictly follow this sequence to prevent circular dependencies, hallucinated imports, and context-window exhaustion.

### [TDD-IDE]-A · Canonical Initialization Sequence

**AGENT DIRECTIVE:** Build exactly one file per task. Earlier files in this list are guaranteed dependencies for later files. Do not stub imports; if a file needs an import, the dependency must be built first.

**Phase A: Core Foundations & State**

1. `app/schemas/schemas.py` (Enums, `GenerationState`, Pydantic models)
    
2. `app/db/migrations/001_initial.sql` (Schema per `[TDD-POSTGRES]`)


```
2a. `ci/run_migrations.py` — Migration runner with two modes:
    - `--dry-run`: parses every `.sql` in `app/db/migrations/` in lexicographic order, asserts append-only per `[TDD-MIGRATION-SAFETY]-A` (no `DROP TABLE`, `DROP COLUMN`, `RENAME` outside the Multi-Deploy Dance protocol `[TDD-MIGRATION-SAFETY]-C`), prints planned ordered SQL to stdout, exits 0 on clean / 1 on violation.
    - `--apply`: opens a single asyncpg connection to `DATABASE_URL`, wraps the full migration set in `BEGIN ... COMMIT`, applies in lexicographic order, records each applied filename to `schema_migrations(filename TEXT PRIMARY KEY, applied_at TIMESTAMPTZ DEFAULT NOW())`, skips already-applied files, exits 0 on success / 1 on any failure (auto-rollback).
    - Both modes accept `DATABASE_URL` from env. Both modes log to stdout in JSON-line format for CI consumption.
    - Used by: `[TDD-CICD]-A` job 9 `migration-dry-run`; Blueprint Daily Ritual pre-flight gate.
```


   
3. `app/redis/lua/wallet_lock.lua`
    
4. `app/redis/lua/wallet_consume.lua`
    
5. `app/redis/lua/wallet_refund.lua`
    
6. `app/redis/lua/circuit_breaker.lua`
    

**Phase B: Utilities, Gateway & Guards** 7. `app/infra_gateway.py` (ModelGateway: Aggregator routing & CB checks) 8. `app/services/cost_guard.py` (Financial ceiling enforcement) 9. `app/services/compliance_gate.py` (Regex prompt-injection guard) 10. `app/services/output_guard.py` (Brand safety & PII guard) 11. `app/services/style_memory.py` (pgvector flywheel upsert/retrieval)

**Phase C: AI Workers (Phases 1-3)** 12. `app/prompts/copywriting/*.yaml` (All LLM prompt templates) 13. `app/workers/extract.py` (Firecrawl integration) 14. `app/workers/copy.py` (Router, Gen, and Refine modes) 15. `app/workers/critic.py` (3-script internal scoring) 16. `app/workers/phase2_chain.py` (The orchestrator for extracting/scoring scripts) 17. `app/workers/strategist.py` (Surfaces strategy card & reads style memory) 18. `app/workers/copilot.py` (HD-3 Chat execution via 5-Stage Chain)

**Phase D: Video Rendering (Phase 4)** 19. `app/broll/library.json` (Static B-Roll catalog for 15s stitch) 20. `app/broll/planner.py` (Deterministic matching of B-Roll to product category) 21. `app/workers/tts.py` (Sarvam/ElevenLabs audio generation) 22. `app/workers/i2v.py` (Fal.ai/Minimax 9s video rendering) 23. `app/workers/reflect.py` (Quality control: SSIM & vision checks) 24. `app/workers/compose.py` (FFmpeg: 3s Hook + 9s I2V + 3s CTA + LUT + Watermark) 25. `app/workers/phase4_coordinator.py` (Fan-in orchestrator. Stops at `preview_ready`) 26. `app/workers/export.py` (Standalone C2PA Rust binary signing & R2 upload)

**Phase E: API Surface (The Bouncers)** 27. `app/api/dependencies.py` (JWT Auth & DB pooling) 28. `app/api/routes/ingest.py` (HD-1 entry) 29. `app/api/routes/status.py` (HD-2/3/5 Hydration) 30. `app/api/routes/chat.py` (Copilot UI) 31. `app/api/routes/approve_strategy.py` (HD-4 Wallet lock) 32. `app/api/routes/edit_back.py` (FSM rewind & state wiping) 33. `app/api/routes/declaration.py` (IT Rules 2026 compliance logging) 34. `app/api/routes/retry_export.py` (9-step atomic chain) 35. `app/api/routes/webhook.py` (Razorpay origin-preserving restore) 36. `app/api/routes/grievance.py` (Auto-Takedown entry point)

**Phase F: Infrastructure & Reliability** 37. `app/arq/dlq.py` (`on_job_dead` dual-branch routing) 38. `app/arq/settings.py` (ARQ queue registration) 39. `app/workers/takedown_processor.py` (IT Rules 2026 R2 deletion) 40. `app/workers/retention_sweep.py` (Time-based data purging)

**Phase G: Observability & CI/CD** 41. `ci/check_banned_patterns.py` (Secret leakage scanner) 42. `ci/validate_prompts.py` 43. `tests/fsm/test_state_transitions.py` (DAG testing) 44. `tests/test_chat_chain_order.py` (CostGuard invariant test) 45. `tests/test_dlq_dual_branch.py` (Render vs Export failure routing)

### [TDD-IDE]-B · Agent Task Decomposition Rules

1. **Single-File Scope:** Generate or edit only ONE file per task. No multi-file refactors in a single prompt execution.
    
2. **Context Anchoring:** Each task must quote the TDD section it implements (e.g., _"Implementing `[TDD-WORKERS]-I` Worker-EXPORT"_).
    
3. **Pre-task Precondition:** Do not begin writing a new file if the CI/Linting of the previously generated file is red.
    
4. **Post-task Verification:** Own tests must pass locally before the agent is permitted to run `git commit`.
    

### [TDD-IDE]-C · Human-in-the-Loop Checkpoints

**AGENT DIRECTIVE: PAUSE execution and await explicit Founder approval at these stages:**

- **Checkpoint 1 (After Step 10 - Guards):** Founder verifies that `OutputGuard` and `CostGuard` logs are correctly hitting the Postgres DB.
    
- **Checkpoint 2 (After Step 16 - Phase 2 Chain):** Founder checks the framework routing output shape via the UI/Postman to ensure the LLM JSON is parsing correctly.
    
- **Checkpoint 3 (After Step 20 - B-Roll Planner):** Founder verifies the determinism logic. Does a "skincare" brief correctly pull a "splashing water" hook?
    
- **Checkpoint 4 (After Step 26 - Export):** Founder runs a full end-to-end Phase 4 render to verify the 15s FFmpeg stitch and C2PA signing.
    
- **Checkpoint 5 (After Step 36 - Webhooks):** Founder runs a manual Razorpay test webhook to verify the origin-preserving multi-row FSM restore.
    

### [TDD-IDE]-D · Context-Window Discipline

**AGENT DIRECTIVE:** Do NOT ingest the entire TDD or PRD for every task. This causes hallucination and forgetting. Per task, load ONLY:

1. The single TDD section the task implements (e.g., `[TDD-GATEWAY]`).
    
2. The specific PRD sections named in that TDD section's "Fulfills PRD Requirement" header.
    
3. The immediate file being written and its direct `import` dependencies.



---


---


## [TDD-TRACE] · Traceability Matrix · PRD F-IDs → TDD Sections

**Fulfills PRD Requirement:** `[PRD-META]` (covers every PRD F-ID exactly once)

This matrix is a flat index from every PRD functional ID to its canonical TDD implementation section. It guarantees bi-directional traceability: no orphaned requirements (missing implementation) and no scope creep (implementation without a requirement). Every F-ID is verbatim from the `[PRD-FEATURES-*]` blocks in PRD v3.

### [TDD-TRACE]-A · Acquisition & Onboarding (Phase 1)

|PRD F-ID|PRD Requirement (Summary)|TDD Implementation Anchor(s)|
|---|---|---|
|**F-101**|Google 1-Tap Login (OAuth 2.0, JWT session versioning)|`[TDD-SECURITY]-A` + `[TDD-OVERVIEW]`|
|**F-102**|Free Preview (Starter tier limits & gating)|`[TDD-API]-D` (ECM-006) + `[TDD-API]-G`|
|**F-103**|Isolation Preview (Firecrawl + BiRefNet + size limits)|`[TDD-WORKERS]-B` + `[TDD-TYPES]-A`|

### [TDD-TRACE]-B · Creative Selection (Phase 2)

|PRD F-ID|PRD Requirement (Summary)|TDD Implementation Anchor(s)|
|---|---|---|
|**F-201**|Director's Chips · Enum chips · ★ Style Memory|`[TDD-WORKERS]-D` + `[TDD-FLYWHEEL]-A`|
|**F-202**|Script Selection (Framework-Routed trio)|`[TDD-WORKERS]-C` (framework_router) + `[TDD-PROMPTS]-E`|
|**F-203**|Motion Selector · 5 archetypes|`[TDD-WORKERS]-G` + `[TDD-TYPES]-A`|
|**F-204**|Environment Canvas · 8 presets|`[TDD-WORKERS]-G`|
|**F-207**|Co-Pilot Chat · Canonical 5-stage chain|`[TDD-CHAT-CHAIN]` + `[TDD-API]-C` + `[TDD-GUARDS]-A`|

### [TDD-TRACE]-C · Intent Gate (Phase 3)

|PRD F-ID|PRD Requirement (Summary)|TDD Implementation Anchor(s)|
|---|---|---|
|**F-701**|Strategy Card (HD-4) · STRATEGIST · pre_topup_status|`[TDD-WORKERS]-G` + `[TDD-API]-D` + `[TDD-STRATEGY]-A`|
|**F-702**|Style Memory · pgvector · resettable|`[TDD-FLYWHEEL]-A` + `[TDD-SCHEMA]` (user_style_profiles)|
|**F-703**|Fallback Reasoning SSE during failures|`[TDD-DLQ]-A` + `[TDD-API]-G`|
|**F-704**|Edit-Back navigation (4 targets) · NULLs downstream|`[TDD-API]-E`|

### [TDD-TRACE]-D · Payment & Wallet

|PRD F-ID|PRD Requirement (Summary)|TDD Implementation Anchor(s)|
|---|---|---|
|**F-301**|UPI QR + Webhook · Origin-preserving restoration|`[TDD-API]-H` + `[TDD-CONCURRENCY]-E`|
|**F-302**|Balance Widget · low-balance nudge|`[TDD-SCHEMA]` (wallet_txn) + `[TDD-REDIS]-A` (DB0)|
|**F-303**|Credit Lock / Consume / Refund (scoped + per-gen)|`[TDD-REDIS]-B/C/D` + `[TDD-CONCURRENCY]-C/D`|

### [TDD-TRACE]-E · Generation & Export (Phase 4)

|PRD F-ID|PRD Requirement (Summary)|TDD Implementation Anchor(s)|
|---|---|---|
|**F-205**|Parallel I2V (asyncio.gather × 2) + REFLECT SSIM|`[TDD-WORKERS]-J` + `[TDD-WORKERS]-H` (Worker-REFLECT)|
|**F-401**|OutputGuard before TTS + on chat response|`[TDD-GUARDS]-B` + `[TDD-CHAT-CHAIN]` (Stage 5)|
|**F-403**|Composition & LUT · canonical 15s fractional stitch|`[TDD-VIDEO]-A/B` + `[TDD-WORKERS]-H` (Worker-COMPOSE)|
|**F-404**|HD Export + C2PA (Decoupled, standalone ARQ job)|`[TDD-WORKERS]-I` + `[TDD-VIDEO]-C` + `[TDD-API]-F`|
|**F-404a**|HD Export Retry (`/retry-export` 9-step atomic chain)|`[TDD-API]-G` + `[TDD-WORKERS]-I`|
|**F-405**|B-roll Planner · role-first, 5-template, deterministic selection (v4-Δ1)|`[TDD-BROLL]` (full chapter, authoritative) + `[TDD-SCHEMA]` (broll_clips, broll_clip_usage, seasons) + `[TDD-WORKERS]-G` (strategist integration) + `[TDD-VIDEO]-A/B` (Worker-COMPOSE branch) + `[TDD-WORKERS]-C2` *(supersede pointer)*|

### [TDD-TRACE]-F · Compliance & Legal

|PRD F-ID|PRD Requirement (Summary)|TDD Implementation Anchor(s)|
|---|---|---|
|**F-501**|InputScrubber · Prompt-injection defense|`[TDD-GUARDS]-A` + `[TDD-API]-C` (Stage 1)|
|**F-503**|SGI Labeling · FFmpeg drawtext at all resolutions|`[TDD-VIDEO]-B` + `[TDD-WORKERS]-H`|
|**F-505**|Immutable Audit · partitioned log · atomic re-sign|`[TDD-SCHEMA]` (audit_log) + `[TDD-API]-F` + `[TDD-API]-G`|
|**F-506**|Auto-Takedown · Pipeline + SLA Watchdog|`[TDD-TAKEDOWN]-A/B/C/D`|

### [TDD-TRACE]-G · Infrastructure & Orchestration

| PRD F-ID  | PRD Requirement (Summary)                                 | TDD Implementation Anchor(s)                                  |
| --------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| **F-601** | PromptOps · versioned YAML schemas                        | `[TDD-PROMPTS]-A/B`                                           |
| **F-602** | Model Gateway · `gateway.route()` · Circuit Breakers      | `[TDD-GATEWAY]-A` + `[TDD-REDIS]-E`                           |
| **F-603** | CostGuard · ₹2/10/14 ceilings · COGS-first record         | `[TDD-GATEWAY]-B` + `[TDD-CHAT-CHAIN]` (Stage 4)              |
| **F-604** | Health Monitor · Contextual Routing                       | `[TDD-GATEWAY]-A` (`_rank_providers`) + `[TDD-REDIS]-A` (DB3) |
| **F-605** | State Machine (22 states + `pre_topup_status` invariants) | `[TDD-FSM]` + `[TDD-CONCURRENCY]-E`                           |
| **F-606** | Data Flywheel · User Signals telemetry                    | `[TDD-FLYWHEEL]-B`                                            |
| **F-607** | Idempotency Gateway · monotonic + 2xx-only cache          | `[TDD-CONCURRENCY]-A` + `[TDD-API]` (Decorators)              |
| **F-608** | ARQ DLQ Handler · Dual-branch dispatch by function        | `[TDD-DLQ]-A/B`                                               |
| **F-609** | R2 Retention Sweep · DB-first, R2-second atomicity        | `[TDD-R2-RETENTION]`                                          |
| **F-610** | Takedown Pipeline implementation                          | `[TDD-TAKEDOWN]-A/B`                                          |
| **F-611** | Declaration Provenance Capture · Atomic re-sign           | `[TDD-API]-F` + `[TDD-API]-G` (Step 4)                        |
| **F-612** | Declaration Freshness Guard · 428 ECM-020                 | `[TDD-API]-G` (Step 4)                                        |



---



---


## [TDD-ERROR-RECOVERY] · Error Recovery Expectations

**Fulfills PRD Requirement:** `[PRD-ERROR-MATRIX]`, `[PRD-ERROR-COPY]`, `[PRD-ERROR-MAP]`, `[PRD-IDEMPOTENCY]`, `[PRD-NON-NEGOTIABLES]`, `[PRD-PAYMENT-FSM]`, `[PRD-HD5]`, `[PRD-HD6]`

Canonical fallback behavior. Each row maps to a PRD Acceptance Criteria (AC) and the TDD subsystem that implements it. **Agents must strictly implement these recovery paths and must not invent new ones.**

### [TDD-ERROR-RECOVERY]-A · External API Timeouts

How we handle failures when 3rd-party services (LLMs, Voice, Video, Payments) go down.

|Failure Class|Trigger|Fallback Behavior|Subsystem|PRD AC|
|---|---|---|---|---|
|**LLM hard timeout (>30s)**|ModelGateway HTTP timeout|Circuit breaker records failure → instantly re-routes to next aggregator provider.|`[TDD-GATEWAY]-A` + `[TDD-REDIS]-E`|F-PRD-AC-2, F-PRD-AC-3|
|**LLM 5xx burst (≥3 in 60s)**|Breaker CLOSED → OPEN|Provider auto-excluded for 60s → HALF_OPEN probe → CLOSED on success.|`[TDD-GATEWAY]-A` + `[TDD-REDIS]-E`|F-PRD-AC-3, G5|
|**LLM 429 rate-limit**|HTTP 429 from provider|Exponential backoff + re-route within tier; if all fail → `503 ECM-013`.|`[TDD-GATEWAY]-A`|F-PRD-AC-3|
|**CostGuard ceiling hit mid-chat**|`cogs_total + est_cost > ceiling`|Stage 2 aborts with `429 ECM-009`; chat input disables; turn NOT counted against 3-turn limit.|`[TDD-GATEWAY]-B` + `[TDD-CHAT-CHAIN]`|F-PRD-AC-3, G4|
|**Razorpay webhook timeout**|No webhook within 5min|Reconciler CRON polls Razorpay REST every 2min for 30min → replays internally.|`[TDD-API]-H` + Reconciler|F-PRD-AC-4|
|**R2 PUT/HEAD timeout**|Cloudflare > 10s or 5xx|Retry 3× exp backoff; terminal → `ECM-018`.|`[TDD-R2-RETENTION]` + `[TDD-API]-G` Step 5|F-PRD-AC-5, F-PRD-AC-6|
|**Razorpay order-create timeout**|≥15s on `/orders`|Client receives `503` + retry banner; **no state mutation** occurs.|`[TDD-API]-D`|F-PRD-AC-4|

> **Crucial FSM Invariant:** No LLM timeout or failure ever transitions the FSM state. Only successfully completed LLM calls with successfully captured COGS ledgers can advance the database state.

### [TDD-ERROR-RECOVERY]-B · Worker-Node Failures

How we handle failures when our own background ARQ workers crash (OOM, SIGKILL, exception).

| Failure Class                     | Trigger                                                            | Fallback Behavior                                                                                       | Subsystem                     | PRD AC                 |
| --------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- | ----------------------------- | ---------------------- |
| **ARQ worker crash mid-job**      | OS SIGKILL, OOM, container restart                                 | ARQ natively re-queues per `max_tries` (default 3); exhaustion drops job to `on_job_dead`.              | `[TDD-WORKERS]` + `[TDD-DLQ]` | F-PRD-AC-4, F-PRD-AC-5 |
| **DLQ — phase4_coordinator**      | `function_name ∈ {phase4_coordinator, tts, i2v, compose, reflect}` | **Branch A:** state → `failed_render`; Lua refund; HD-5 inline recovery (re-lock needed).               | `[TDD-DLQ]` branch A          | F-PRD-AC-4             |
| **DLQ — worker_export**           | `function_name == worker_export`                                   | **Branch B:** state → `failed_export`; Lua refund; HD-6 inline retry panel.                             | `[TDD-DLQ]` branch B          | F-PRD-AC-5, F-PRD-AC-6 |
| **Ledger-before-Redis violation** | Code path attempts Redis mutation before Postgres INSERT           | Runtime assertion aborts with HTTP `500` + immediate Grafana Cloud alerts.                              | `[TDD-CONCURRENCY]-C/D`       | G2                     |
| **Worker starvation**             | Queue depth > 1000 for 5min                                        | Grafana Cloud alerts P1; DLQ is intentionally NOT auto-drained (avoids a thundering-herd refund storm). | `[TDD-CICD]-E`                | —                      |

### [TDD-ERROR-RECOVERY]-C · State-Machine Stalls

How we handle dropped client connections, cross-tab conflicts, and zombie database rows.

|Failure Class|Trigger| Fallback Behavior                                                                            |Subsystem|PRD AC|
|---|---|---|---|---|
|**SSE connection drops**|Network flap, proxy timeout, tab background| Client auto-reconnects exp backoff; on reconnect fires `GET /api/generations/{gen_id}`.      |`[TDD-API]-B`|G5|
|**Client/server state drift**|Client shows stale state after reconnect| Server is source of truth; client UI is re-projected from hydration response.                |`[TDD-API]-B`|G5|
|**Cross-tab desync**|Two tabs open on same `gen_id`| `storage` event listener propagates state; drops stale idempotency key on 4xx.               |`[TDD-API]-B` + `[PRD-IDEMPOTENCY]`|F-PRD-AC-6|
|**Stuck "in-flight" state > 10min**|FSM stuck in `{extracting, scripting, rendering, exporting}` past SLA| Stale-row scanner CRON every 60s → checks ARQ status → triggers manual `on_job_dead` replay. |Stale Scanner|F-PRD-AC-1, F-PRD-AC-2|
|**`pre_topup_status` violation**|CHECK constraint fires at DB trigger| DB Transaction rolled back; no partial write allowed; Grafana Cloud alerts P1.               |`[TDD-FSM]` + `[TDD-CONCURRENCY]-E`|G3|

### [TDD-ERROR-RECOVERY]-D · Degradation Tiers

When systemic infrastructure fails, we disable features starting with the most expensive, keeping core flows alive as long as possible.

1. **Tier-1 (Aggregator Pools Down):** ModelGateway all breakers OPEN. Fallback: Disable `/chat` UI (`503 ECM-003`); preserve in-flight generations so they can reach `preview_ready` and export.
    
2. **Tier-2 (TTS provider down):** Pause new Phase-4 rendering enqueues; in-flight coordinators complete using the last cached voice fallback.
    
3. **Tier-3 (Razorpay down):** New top-up attempts respond with a maintenance banner; existing wallet credits are completely unaffected and can be spent.
    
4. **Tier-4 (Neon DB or Upstash Redis down):** Full read-only mode; no new writes allowed; global maintenance page activated.
   
   
	Implementation Detail: Each tier has a dedicated Grafana panel and a corresponding feature flag `tier_{1..4}_degraded_mode` in the admin dashboard._
---


---

## [TDD-OBSERVABILITY] · Observability Stack *(Category 2B — REPLACED)*

The previous `[TDD-OBSERVABILITY]` defined six log event schemas but was silent on implementation. This section replaces it with a complete specification covering four components: structured logging, metrics, error tracking, and product analytics. The six event schemas from v3 are preserved as the contract that `ci/observability_lint.py` enforces — they now have implementation backing.

### [TDD-OBSERVABILITY]-A · Component 1 — Structured Logging (`structlog`)

**Install:** `structlog`.
**Configure once:** in `app/main.py`.

- Production: JSON renderer. Every log line is a single JSON object.
- Development (`ENV=development`): ConsoleRenderer (human-readable, colourised).

**Mandatory base fields** on every log line — injected by the processor chain, not by the developer:

| Field     | Value example                          | Source                  |
| --------- | -------------------------------------- | ----------------------- |
| `ts`      | `"2026-05-18T14:23:01.234Z"`           | ISO8601 processor       |
| `env`     | `"production"` \| `"staging"` \| `"development"` | `ENV` env var |
| `service` | `"fastapi"` \| `"arq-worker"`          | Set at structlog init   |
| `level`   | `"info"` \| `"warning"` \| `"error"`   | structlog level         |

**Worker binding pattern.** At the top of every `process()` method (every worker, every ARQ function):

```python
log = structlog.get_logger().bind(
    gen_id=gen_id, user_id=user_id, worker="<worker_name>", plan_tier=plan_tier
)
```

Every subsequent `log.info(...)` / `log.error(...)` call in that worker automatically carries these fields. `gen_id` is the universal search key — it MUST appear on every single log line emitted by a worker without exception. Routes follow the same pattern bound on `gen_id` and `user_id` per request.

**Six mandatory structured event schemas.** These are preserved from v3 and are the events `ci/observability_lint.py` enforces — the CI script greps the critical code paths (CostGuard wrapper, wallet Lua wrapper, DLQ handler `on_job_dead`, FSM state-transition logger) and fails the build if any path lacks the corresponding emission.

| Event                | Required fields                                                                                |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| `state_transition`   | `from_state`, `to_state`, `trigger_route`, `pre_topup_status_before`, `pre_topup_status_after`, `tx_id` |
| `wallet_op`          | `op` (`lock` \| `consume` \| `refund`), `result`, `balance_before`, `balance_after`, `ledger_row_id`   |
| `api_call`           | `route`, `status_code`, `latency_ms`, `chain_stages_traversed`, `ecm_code`                     |
| `cost_ledger`        | `provider`, `capability`, `cost_inr`, `gen_id`                                                 |
| `framework_routing`  | `selected_frameworks`, `fallback_applied`, `evidence_strength`                                 |
| `compliance_event`   | `event` (`declaration` \| `c2pa_sign` \| `takedown` \| `grievance`), `gen_id`, `sha256`        |

**Privacy invariant.** Request bodies and response bodies are logged only as `sha256` hashes (field name: `payload_sha256` / `response_sha256`). Raw text never logged. This applies to FastAPI route logging middleware and to worker logs.

**Shipping path.** Grafana Agent on the production VPS tails worker stdout (which contains JSON lines via systemd journal) and ships to Grafana Loki. Config file: `/etc/grafana-agent/config.yml`.

**Retention:** 90 days live-searchable in Loki. Cold storage after.

**Required env vars** (also listed in `[TDD-ENV-MANIFEST]`): `LOKI_PUSH_URL`, `GRAFANA_AGENT_TOKEN`, `ENV`.

### [TDD-OBSERVABILITY]-B · Component 2 — Metrics (Prometheus + Pushgateway)

**Problem.** ARQ workers are long-running background processes with no inbound HTTP endpoint. Prometheus's pull model cannot scrape them.

**Solution.** Prometheus Pushgateway as a sidecar on the same VPS.

- **Install:** `prometheus-pushgateway` as a sidecar process on the Hetzner VPS, listening on `localhost:9091`. Process supervised by systemd; see `[TDD-DEPLOYMENT]`.
- **Worker contract:** every ARQ job pushes its metrics to `localhost:9091` after the job completes — both on success and on failure. The push happens in the worker's `on_job_end` / `on_job_dead` hooks so it cannot be skipped by an exception.
- **Prometheus scrape:** Prometheus on the VPS scrapes Pushgateway on a 15s interval.
- **Remote write:** Prometheus forwards metrics to Grafana Cloud via `remote_write`.

**Mandatory metric counters and histograms** (every worker must push these — not optional):

| Metric                                                          | Type      | Labels                                |
| --------------------------------------------------------------- | --------- | ------------------------------------- |
| `aw_generation_state_total`                                     | Counter   | `state`, `plan_tier`                  |
| `aw_dlq_dead_total`                                             | Counter   | `function`                            |
| `aw_cogs_overshoot_total`                                       | Counter   | `plan_tier`                           |
| `aw_fallback_events_total`                                      | Counter   | `from_provider`, `to_provider`, `capability` |
| `aw_sse_reconnect_total`                                        | Counter   | —                                     |
| `wallet_op_total`                                               | Counter   | `op`, `result`                        |
| `llm_cogs_rupees`                                               | Histogram | `provider`, `capability`              |

The full v3 inventory (`[TDD-CICD]-F` in this document) is preserved alongside these; this table lists the minimum mandatory set that ALL workers must emit regardless of function.

**Node exporter.** Install `prometheus-node-exporter` on the VPS. Scrapes CPU, memory, disk, network. Required for the disk-free alert (see `[TDD-OBSERVABILITY]-E` alert matrix).

### [TDD-OBSERVABILITY]-C · Component 3 — Error Tracking (Sentry)

**Install:** `sentry-sdk[fastapi,arq]`.
**Configure:** in `app/main.py` with `SENTRY_DSN` env var.

**FastAPI.** Add Sentry middleware — all unhandled route exceptions auto-captured.

**Workers.** In every `except` block, before `capture_exception()`:

```python
sentry_sdk.set_tag("gen_id", gen_id)
sentry_sdk.set_tag("worker", "compose")
sentry_sdk.set_tag("plan_tier", plan_tier)
```

**DLQ handler.** `on_job_dead` always captures with full job context (function name, args sha256, retries-exhausted count, last exception).

**Ignored exceptions** (do not send to Sentry — these are expected, recoverable, and would otherwise saturate the free tier budget):

- ARQ internal retry signals.
- Razorpay 429 rate-limit responses.
- Circuit-breaker open-state errors when the breaker is already OPEN (transition OPEN → OPEN).

**Free-tier budget.** Sentry free tier: 5K errors / month — sufficient for the MVP 3K-user target.

**Alert.** "New issue type" → same Slack/email channel as Grafana alerts.

### [TDD-OBSERVABILITY]-D · Component 4 — Product Analytics (PostHog)

`POSTHOG_API_KEY` is provisioned. The event model is **backend-primary**: 70% of meaningful events happen in workers with no frontend involvement, so the backend is the source of truth.

**Seven mandatory backend events** — emitted from FastAPI routes after the corresponding successful state transition:

| Event                | Emitted from / when                                          | Maps to screen |
| -------------------- | ------------------------------------------------------------ | -------------- |
| `generation_created` | `POST /api/generations` success                              | HD-1           |
| `strategy_confirmed` | `GET /status` confirms `brief_ready`                          | HD-2           |
| `script_locked`      | Scripts approved (selected_script_id set)                    | HD-3           |
| `credit_locked`      | `POST /approve-strategy` success — **most important conversion event** | HD-4           |
| `preview_ready`      | `phase4_coordinator` completes                                | HD-5           |
| `export_complete`    | `Worker-EXPORT` completes (revenue event)                     | HD-6           |
| `generation_failed`  | Any terminal failure state, with `{reason, state, plan_tier}` | any            |

**Three frontend events** via PostHog JS SDK: `page_viewed`, `upload_initiated`, `export_downloaded`.

**Implementation per route** — two lines per route handler:

```python
posthog.capture(
    distinct_id=user_id,
    event='credit_locked',
    properties={'plan_tier': plan_tier, 'gen_id': str(gen_id), 'category': category}
)
```

**Implementation priority order** during sprint: `credit_locked` → `export_complete` → `generation_failed` → remaining HD screens.

### [TDD-OBSERVABILITY]-E · Alert Matrix (Grafana — MVP minimum)

| Signal                                              | Threshold              | Severity | Channel        |
| --------------------------------------------------- | ---------------------- | -------- | -------------- |
| `aw_dlq_dead_total`                                 | > 0 in 5 min           | P1       | Slack + email  |
| `wallet_op_total{result="duplicate"}`               | > 0 in 5 min           | P1       | Slack + email  |
| C2PA sign failure rate                              | > 1%                   | P1       | Slack + email  |
| Generation success rate                             | < 85% rolling 1h       | P1       | Slack + email  |
| Illegal FSM transition (trigger blocks)             | any occurrence         | P1       | Slack + email  |
| `aw_cogs_overshoot_total`                           | > 0                    | P2       | Slack only     |
| `aw_fallback_events_total`                          | > 10% of traffic       | P2       | Slack only     |
| Phase 4 P95 latency                                 | > 240s                 | P2       | Slack only     |
| `node_filesystem_avail_bytes` free                  | < 30%                  | P2       | Slack only     |
| `node_filesystem_avail_bytes` free                  | < 15%                  | P1       | Slack + email  |

No PagerDuty at MVP. Alerts via Grafana notification channels (email and webhook to Slack).

### [TDD-OBSERVABILITY]-F · Log Rotation and Disk Management

Three components, all mandatory before production cutover:

**1. logrotate.** `/etc/logrotate.d/adcreo`:

- Rotate daily.
- Keep 7 days local.
- Compress after 1 day.
- `postrotate` sends `SIGHUP` to Grafana Agent so it re-opens file handles after rotation.

This caps local log disk usage at approximately 3 GB.

**2. journald size cap.** `/etc/systemd/journald.conf`:

```ini
SystemMaxUse=2G
```

Journal auto-evicts oldest entries when the cap is reached. This is the second layer of protection.

**3. Disk alert.** Per the alert matrix in `[TDD-OBSERVABILITY]-E` above. `node_filesystem_avail_bytes` scraped by node exporter; Grafana alert at 30% (P2) and 15% (P1).

---


## [TDD-MIGRATION-SAFETY] · Migration Safety Policy

**Fulfills PRD Requirement:** `[PRD-NON-NEGOTIABLES]`, `[PRD-FEATURES-INFRA]`, `[PRD-SPRINTS]`, `[PRD-RELEASE-MVP]`

Database schema changes under Agentic development are the highest-risk class of operations. An AI agent's tendency to refactor code aggressively must be physically prevented at the database layer to avoid catastrophic data loss or table locks. **These rules are absolute.**

### [TDD-MIGRATION-SAFETY]-A · Append-Only Principle

We treat the production database as an append-only ledger.

**✅ ALLOWED IN MIGRATIONS (Additive & Safe):**

- `CREATE TABLE ... IF NOT EXISTS`
    
- `ALTER TABLE ... ADD COLUMN ... DEFAULT ... NULL` (Must be nullable or have a default so old rows don't break)
    
- `CREATE INDEX CONCURRENTLY IF NOT EXISTS` (Concurrently prevents table locks)
    
- `ALTER TYPE <enum> ADD VALUE ...` (Enums can only grow, never shrink)
    
- `CREATE OR REPLACE FUNCTION / TRIGGER`
    
- Creating new partitions on existing partitioned tables (e.g., for `audit_log`)
    
- Backfill jobs that safely write to new nullable columns in batches
    

**❌ FORBIDDEN IN PRODUCTION MIGRATIONS (Destructive & Unsafe):**

- `DROP TABLE`, `DROP COLUMN`, `DROP TYPE`, `DROP CONSTRAINT`
    
- `DROP INDEX` (unless `CONCURRENTLY` is explicitly used)
    
- `ALTER COLUMN ... TYPE ...` (Changes data types, causing full table locks and possible casting failures)
    
- `ALTER COLUMN ... SET NOT NULL` (Will crash if existing rows have NULLs and aren't fully backfilled)
    
- `TRUNCATE` or `DELETE FROM` without a strict `WHERE` clause
    
- Renaming columns or tables (e.g., `ALTER TABLE x RENAME COLUMN y TO z`)
    
- Removing values from an `ENUM`
    

### [TDD-MIGRATION-SAFETY]-B · Migration File Conventions

1. **Naming:** One migration per file, formatted as `VYYYYMMDDHHMM__<kebab_description>.sql`.
    
2. **Rollbacks:** Every migration MUST have a matching `rollback_VYYYYMMDDHHMM__<kebab_description>.sql` file.
    
3. **Idempotency:** Every migration must be safely re-runnable (always use `IF NOT EXISTS` / `IF EXISTS` guards).
    
4. **Separation of Concerns:** No migration file mixes fast DDL (like adding a column) with slow DML backfills (like updating 10,000 rows) in one transaction.
    

### [TDD-MIGRATION-SAFETY]-C · Destructive-Change Protocol (The Multi-Deploy Dance)

If a column or table absolutely MUST be removed or renamed, it requires a carefully orchestrated multi-step deployment to ensure Zero Downtime.

- **Deploy N (Prepare):** Add the new column/type. Update application code to perform "Dual-writes" (writing to both the old and new column simultaneously).
    
- **Deploy N+1 (Backfill):** Run a background script to backfill historical data from the old column into the new column. Once complete, update the application to strictly read from the _new_ column.
    
- **Deploy N+2 (Soak):** Stop writing to the old column entirely. Monitor the system for ≥ 48 hours to ensure no edge-case queries are failing.
    
- **Deploy N+3 (Destroy):** `DROP` the old column. This requires a manual, human-approved pull request.
    
- **Sprint Constraint:** For our 15-day sprint (Apr 26 – May 10), **no destructive changes are allowed after Day 10.**
    

### [TDD-MIGRATION-SAFETY]-D · CI Enforcement

Human review isn't enough; the CI pipeline enforces these rules mechanically via `migration_safety_guard.py`.

This script runs on every Pull Request and:

1. **Greps for forbidden statements:** If `DROP TABLE` or `RENAME` is found in a `.sql` migration file, the PR is instantly blocked.
    
2. **Pairs Verification:** Verifies every `V*.sql` file has a corresponding `rollback_*.sql` file.
    
3. **Null-Safety Check:** Verifies that any `ADD COLUMN` command includes either `NULL` or an explicit `DEFAULT` constraint.
    
4. **Lock Prevention:** Verifies `CREATE INDEX` strictly uses the `CONCURRENTLY` keyword on any table known to have > 1000 rows.
    

### [TDD-MIGRATION-SAFETY]-E · Prohibition on Agent-Driven Destructive Migrations

**AGENT DIRECTIVE:** The Antigravity agent (Cursor/Devin) is physically forbidden from authoring a migration containing any FORBIDDEN statement.

If the agent determines a `DROP` or `RENAME` is necessary to complete a task, it must **HALT** and instruct the user to create a human-authored PR with a change-advisory RFC. Agents may author additive migrations freely.



---


---


## [TDD-ROLLBACK] · Rollback Policy

**Fulfills PRD Requirement:** `[PRD-NON-NEGOTIABLES]`, `[PRD-FEATURES-INFRA]`, `[PRD-RELEASE-MVP]`, `[PRD-RELEASE-BETA]`, `[PRD-PAYMENT-FSM]`, `[PRD-ERROR-MATRIX]`

This section defines the emergency procedures for recovering from catastrophic failures (P0/P1 incidents). It strictly separates Application Rollbacks (fast, safe) from Database/State Rollbacks (slow, dangerous).

### [TDD-ROLLBACK]-A · Deployment Rollback — Application Layer

Triggered immediately upon a P0/P1 incident originating from a newly deployed build.

- **T+0:** On-call engineer reverts to the previous known-good Docker image tag via Docker Compose.
    
- **T+2min:** Verify that `GET /healthz` returns the pinned old commit SHA.
    
- **T+5min:** Confirm via Grafana that the error rate has returned to baseline and the DLQ depth is no longer growing.
    
- **T+15min:** File the post-incident ticket documenting the bad commit SHA, the rolled-back-to SHA, the timeline, and initiating a ledger-integrity check.
    

**Invariant:** Application rollback alone NEVER touches the Postgres database.

### [TDD-ROLLBACK]-B · Schema Rollback — Data Layer

**HARD RULE: Production schema is NEVER rolled back by running `rollback_*.sql`.** Forward-fix is always the path.

1. **Additive Migration:** If the bad deploy included a purely additive migration (e.g., adding a new nullable column), take no action on the DB. Rolling back the app layer is sufficient (the old app will just ignore the new column).
    
2. **Strict Constraint:** If a new `CHECK` constraint or trigger is violated by the old app, drop the constraint via a NEW forward migration.
    
3. **Data Corruption:** If a migration corrupted data, recover via Neon Point-In-Time Recovery (PITR) or reconstruct the data from the `audit_log`. NEVER run `TRUNCATE + reload` on the production database.
    

### [TDD-ROLLBACK]-C · State-Corruption Recovery

If the FSM (State Machine) or the financial ledger becomes inconsistent due to a crash:

1. **Freeze Writes:** Instantly freeze the affected `gen_id` or `user_id` using a feature flag: `freeze_user_{user_id}=true`.
    
2. **Establish Source-of-Truth:** Trust hierarchy is: Postgres `wallet_transactions` > Postgres `generations` > Redis balance.
    
3. **Re-derive Redis Balance:** If Redis desyncs, recompute it from the ledger: `SUM(wallet_transactions.delta WHERE user_id=?)` → `SET wallet:balance:{user_id}`.
    
4. **Stuck Generations:** Re-project stuck FSM states from `status_history`. If the state is ambiguous, forcefully set it to a safe terminal state (`failed_render` or `failed_export`) and issue a refund.
    
5. **Unfreeze:** Remove the feature flag only after manual verification.
    

### [TDD-ROLLBACK]-D · Webhook & Payment Reconciliation

If Razorpay webhooks fail to deliver or the system crashes mid-processing:

- **Poll:** Poll the Razorpay REST API (`/payments/`) for all `captured` events that occurred during the incident window.
    
- **Cross-Check:** Compare the Razorpay list against `wallet_transactions WHERE payment_status='captured'`.
    
- **Reconcile:** Missing rows in our DB → replay the webhook internally to credit the user. Extra rows in our DB → flag for immediate manual investigation.
    
- **Invariant:** NEVER process a financial refund automatically during reconciliation. Refunds require human approval.
    

### [TDD-ROLLBACK]-E · R2 / Asset Rollback

R2 objects (images, videos) are immutable post-upload.

- **Deletion:** Delete bad or corrupted objects using the established `retention_sweep` tool, NOT ad-hoc SQL/Bash scripts.
    
- **Recall:** For finalized exports that a user has already downloaded, do NOT attempt a digital recall. Issue a public correction notice via an in-app banner if legally required.
    

### [TDD-ROLLBACK]-F · Rollback Drill

A mandatory exercise run once on staging before the Beta opens to the public:

- Hetzner Docker rollback must complete in < 5 minutes.
    
- Grafana dashboards must successfully populate from the rolled-back build.
    
- Verify no orphaned Redis locks remain (they must naturally TTL-expire within 5 minutes).
    
- Webhook reconciler must replay cleanly without double-crediting.
    

### [TDD-ROLLBACK]-G · Rollback Authority

Strict permissions for executing disaster recovery commands:

- **Application rollback:** The on-call engineer executes this _without_ further approval in a P0/P1 event.
    
- **Schema forward-fix:** Requires a 2-reviewer approval on the fix PR before merge.
    
- **Destructive data recovery:** Executing a Neon PITR or manual row surgery requires explicit sign-off in writing from the Founder + the on-call engineer..

---



# AdvertWise TDD v3 — Engineering Reference (Part 2 of 2)

> **Classification:** CONFIDENTIAL · GOLDEN RC · Source of Truth
> **Status:** MVP Locked · Agent-Ready · Aligned to PRD Locked (Version 3)
> **Scope:** Section `[TDD-API-STUBS]` (Zero-Cost CI Test Harness).
> **Part 1** covers `[TDD-META]` through `[TDD-ROLLBACK]`.

---



---


## [TDD-API-STUBS] · Static API Stubs for Agent CI · Zero-Cost Test Harness

**Fulfills PRD Requirement:** `[PRD-META]`, `[PRD-FEATURES-INFRA]`, `[PRD-SPRINTS]`, `[PRD-AGENTIC-DRAFT]`, `[PRD-RELEASE-BETA]`

The Antigravity agent runs tests continuously during authoring. Hitting real LLM, TTS, I2V, Vision, and Scraper providers on every CI run would burn real money and introduce non-deterministic test flakes.

This section defines the deterministic, static-response fixtures every external provider must have. Tests pin to these fixtures via the environment flag `AW_API_MODE=stub`. CI sets this unconditionally; Staging and Production NEVER do.

### [TDD-API-STUBS]-A · Scope & Invariants

| Provider               | Capability                          | Stub Module Location                |
| ---------------------- | ----------------------------------- | ----------------------------------- |
| **DeepSeek**           | `completion` (copywriting primary)  | `app/stubs/deepseek_stub.py`        |
| **GPT-4o-mini**        | `completion` (copywriting fallback) | `app/stubs/openai_stub.py`          |
| **Gemini Flash**       | `vision` (category fallback)        | `app/stubs/gemini_stub.py`          |
| **GPT-4V**             | `vision` (fallback)                 | `app/stubs/gpt4v_stub.py`           |
| **Firecrawl**          | `scraping`                          | `app/stubs/firecrawl_stub.py`       |
| **Sarvam**             | `tts`                               | `app/stubs/sarvam_stub.py`          |
| **Fal.ai**             | `i2v` (primary)                     | `app/stubs/fal_stub.py`             |
| **Minimax**            | `i2v` (fallback)                    | `app/stubs/minimax_stub.py`         |
| **Llama Guard / Groq** | `moderation`                        | `app/stubs/groq_moderation_stub.py` |

### [TDD-API-STUBS]-B · Environment Gating

**Purpose:** The physical switch that disconnects the Gateway from the internet during testing.

```
# app/infra_gateway.py
import os
from app.stubs import stub_registry

class ModelGateway:
    def __init__(self):
        # SECURITY & ECONOMICS: If this is 'stub', no real network requests fire.
        self.is_stub_mode = os.getenv("AW_API_MODE") == "stub"

    async def route(self, capability: str, input_data: dict):
        if self.is_stub_mode:
            # Returns the hardcoded JSON fixtures defined below
            return await stub_registry.get_fixture(capability, input_data)
            
        # ... real aggregator routing logic ...
```

### [TDD-API-STUBS]-C · DeepSeek Completion · `framework-router` Response

**Fulfills PRD Requirement:** `[PRD-PLAYBOOK]`, `[PRD-AGENTIC-DRAFT]`, `[TDD-WORKERS]-C`

The framework-router stub MUST perfectly validate against the `FrameworkRoutingOutput` Pydantic model (`[TDD-TYPES]-B`). Because that model uses `ConfigDict(extra='forbid')`, any leaked fields will crash the test.

> **Logic Invariant:** Fields like `b_roll_plan` and `turns_remaining` are strictly **NOT** present in these fixtures. `b_roll_plan` is generated by the deterministic Python planner (`[TDD-WORKERS]-C2`), not the LLM. Any stub fixture containing these fields will fail validation and MUST be rejected during agentic code review.

```
# app/stubs/fixtures/deepseek/framework_router.py

# ── Fixture 1: High-evidence routing (default trio NOT triggered) ─────────────
FIXTURE_HIGH_EVIDENCE = {
    "selected": ["clinical_flex", "usage_ritual", "social_proof"],
    "rationale": {
        "clinical_flex": "Strong ingredient/spec proof supports claim-led logic angle.",
        "usage_ritual":  "Routine-driven product fits lifestyle emotion framing.",
        "social_proof":  "Trust signals drive conversion for established categories.",
    },
    "fallback_triggered": False,
    # Metadata for CostGuard to simulate unit economic tracking
    "_meta_tokens_in":  812,
    "_meta_tokens_out": 186,
}

# ── Fixture 2: Low-evidence routing (SAFE_TRIO fallback) ─────────────────────
FIXTURE_LOW_EVIDENCE_SAFE_TRIO = {
    "selected": ["pas_micro", "usage_ritual", "social_proof"],   # SAFE_TRIO per [PRD-PLAYBOOK]
    "rationale": {
        "pas_micro":    "SAFE_TRIO default — logic anchor (pain-point clarity).",
        "usage_ritual": "SAFE_TRIO default — emotion anchor (lifestyle context).",
        "social_proof": "SAFE_TRIO default — conversion anchor (trust signal).",
    },
    "fallback_triggered": True,
    "_meta_tokens_in":  812,
    "_meta_tokens_out": 168,
}

# ── Fixture 3: Schema violation (Tests the router's error recovery mechanism) ─
FIXTURE_SCHEMA_VIOLATION = "{ this is intentionally malformed JSON"   # Not a dict
```

### [TDD-API-STUBS]-F · Gemini Vision · `category-classifier` Response

**Fulfills PRD Requirement:** `[PRD-CATEGORY]`, `[PRD-GREENZONE]`, `[PRD-CONFIDENCE]`, `[TDD-WORKERS]-B`

```
# app/stubs/fixtures/gemini/vision.py

# ── Fixture 1: High-confidence, Green Zone product ────────────────────────────
FIXTURE_VISION_HIGH = {
    "category": "d2c_beauty",                      # MUST be a valid Green Zone enum value
    "confidence_score": 0.94,
    "agent_crop_suggestion": {"x": 48, "y": 48, "w": 960, "h": 960},
    "agent_motion_suggestion": 1,                  # motion_archetype INTEGER per schema
    "_meta_tokens_in":  1200,                      # vision is image-tokens heavy
    "_meta_tokens_out":   48,
}

# ── Fixture 2: Red Zone category (tests CategoryError → failed_category flow) ─
FIXTURE_VISION_OUT_OF_ZONE = {
    "category": "apparel",                         # Red Zone per [PRD-GREENZONE] → Triggers Error
    "confidence_score": 0.91,
    "_meta_tokens_in":  1200,
    "_meta_tokens_out":   32,
}
```

### [TDD-API-STUBS]-G · Groq Moderation · `safety-check` Response

**Fulfills PRD Requirement:** `[PRD-NON-NEGOTIABLES]`, `[TDD-WORKERS]-F`

```
# app/stubs/fixtures/groq/moderation.py

# ── Fixture 1: Safe content (default — passes Worker-SAFETY) ─────────────────
FIXTURE_SAFE = {
    "flagged": False,
    "categories": {},
    "_meta_tokens_in":  120,
    "_meta_tokens_out":  16,
}

# ── Fixture 2: Unsafe content (triggers failed_safety FSM transition) ────────
FIXTURE_FLAGGED = {
    "flagged": True,
    "categories": {"harassment": True, "violence": False, "self_harm": False},
    "_meta_tokens_in":  120,
    "_meta_tokens_out":  24,
}
```
```



---



### [TDD-API-STUBS]-P · Invariants Summary

These are the strict rules the AI Agent must follow when interacting with the Test Harness:

1. **Unconditional CI Mode:** `AW_API_MODE=stub` is set unconditionally in CI via `.github/workflows/*.yml`. Production and Staging always set `AW_API_MODE=live`. Any Pull Request that attempts to remove the CI environment line is blocked by the `compliance-gate` check.
    
2. **Import Graph Isolation:** Stubs live exclusively in `app/stubs/` and are imported _only_ from `app/infra_gateway.py' at initialization. **No production code path** is allowed to import from `app/stubs/` directly. This is mechanically enforced by `ci/check_stub_import_graph.py`.
    
3. **The Four Properties:** Stub data must be **Deterministic**, **Offline**, **Schema-Valid**, and **COGS-Accurate**. Any stub that violates one of these properties is a bug, not a feature.
    
4. **Versioned Fixtures:** Stub fixtures are strictly versioned. The `app/stubs/fixtures/` directory carries a `VERSION` file that is bumped on every fixture change. Tests pin to a version, so a fixture edit is a deliberate, reviewed event — never a silent drift.


---


---

# NEW SECTIONS (Category 4)

---

## [TDD-DEPLOYMENT] · Infrastructure Topology, Entry Path, Process Supervision

### [TDD-DEPLOYMENT]-A · Topology

- **Single Hetzner VPS** is the entire production fleet at MVP. No Kubernetes. No Docker Compose. No multi-region.
- **Four systemd-managed processes** on that VPS:

  | Unit               | Role                                                                                                |
  | ------------------ | --------------------------------------------------------------------------------------------------- |
  | `adcreo-api`       | FastAPI process (uvicorn), serves all HTTP API routes.                                              |
  | `adcreo-studio`    | ARQ worker process — handles the creative pipeline: `phase1_extract`, `phase2_chain` (copy, critic, safety, strategist, b-roll-planner). Formerly `adcreo-studio`. |
  | `adcreo-render`    | ARQ worker process — handles the production pipeline: `phase4_coordinator` (tts, i2v, reflect, compose) and `worker_export`. Formerly `adcreo-render`. |
  | `adcreo-redis`     | Redis 7 instance, all six logical DBs (`[TDD-REDIS]-A`).                                            |

  Additional supervised sidecars (not in the four-unit core but required):

  | Sidecar                       | Role                                                                                                |
  | ----------------------------- | --------------------------------------------------------------------------------------------------- |
  | `prometheus-pushgateway`      | Receives metrics pushes from `adcreo-studio` and `adcreo-render`. Listens on `localhost:9091`.       |
  | `prometheus-node-exporter`    | Exports VPS host metrics (CPU, memory, disk, network).                                              |
  | `grafana-agent`               | Tails worker stdout (JSON lines) and ships to Grafana Loki.                                          |
  | `nginx`                       | Internal reverse proxy. Receives traffic from Cloudflare Tunnel. Never bound to a public interface. |
  | `cloudflared`                 | Cloudflare Tunnel daemon. The only inbound network path to the VPS.                                  |

- **All four core unit files version-controlled** in `/infra/systemd/`:

  - `/infra/systemd/adcreo-api.service`
  - `/infra/systemd/adcreo-studio.service`
  - `/infra/systemd/adcreo-render.service`
  - `/infra/systemd/adcreo-redis.service`

  Sidecar unit files version-controlled alongside them as `/infra/systemd/<name>.service`.

### [TDD-DEPLOYMENT]-B · Entry Path — Nginx + Cloudflare Tunnel

- **No public IP exposed.** Ports 80 and 443 are never open on the VPS firewall. The VPS has no inbound listener on a public interface.
- **Cloudflare Tunnel terminates at the Cloudflare edge.** `cloudflared` on the VPS holds an outbound persistent connection to Cloudflare and receives traffic over it.
- **Nginx** receives traffic from `cloudflared` over loopback (`127.0.0.1`) and reverse-proxies to `adcreo-api`.
- **Nginx responsibilities:**

  1. Internal routing (path → upstream).
  2. SSE token log redaction (security requirement, per Architecture Review A-3-01).
  3. `Cache-Control` header enforcement (per Architecture Review G-6-03).

- **Nginx config** version-controlled at `/infra/nginx.conf`.

#### [TDD-DEPLOYMENT]-B.1 · SSE Token Log Redaction

The SSE auth pattern (per `[TDD-SECURITY]`) issues a short-lived (60 s) single-use SSE token via `POST /api/sse-token`. The browser passes it as `?t=<sse_token>` in the `EventSource` URL because browser `EventSource` cannot carry an `Authorization` header.

Nginx access logs MUST redact the `t` query parameter so it never appears in `/var/log/nginx/access.log` or in any log shipped to Loki. The `log_format` directive in `/infra/nginx.conf` must redact `t=<value>` before write. Example pattern (the exact regex is owned by `/infra/nginx.conf`):

- Capture the request URL.
- Substitute `t=[^&]*` with `t=REDACTED` in the captured form.
- Use the redacted form in the `log_format` template.

Even if a token leaks into a log line during a misconfiguration, the 60 s TTL means it has expired before the log is flushed. The redaction is the primary defence; the short TTL is the safety net.

#### [TDD-DEPLOYMENT]-B.2 · Cache-Control Header Enforcement

Nginx enforces `Cache-Control` per response class:

| Response class            | `Cache-Control`                       |
| ------------------------- | ------------------------------------- |
| Export MP4 files          | `public, max-age=3600`                |
| API responses (default)   | `no-store`                            |
| Static assets             | `public, max-age=86400`               |

Cache headers are enforced at the Nginx layer so the application code does not have to set them on every response. The R2 origin's Cache-Control headers are honoured for export files served via Cloudflare CDN (consistent with Architecture Review G-3-02 / G-6-03).

### [TDD-DEPLOYMENT]-C · Process Supervision

Each of the four core systemd unit files MUST define:

```ini
[Service]
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
```

`Restart=always` guarantees the worker comes back after a crash; `RestartSec=5` prevents a tight crash-restart loop from saturating the CPU. `StandardOutput=journal` and `StandardError=journal` ensure all output is captured for Grafana Agent ingestion (`[TDD-OBSERVABILITY]-A`).

For `adcreo-studio.service` and `adcreo-render.service` specifically:

```ini
[Service]
KillMode=process
TimeoutStopSec=300
```

`KillMode=process` (not the default `control-group`) sends `SIGTERM` to the main process only — not the entire process group. This allows ARQ's graceful-shutdown handler to complete in-flight jobs before the process exits. `TimeoutStopSec=300` (5 minutes) is the maximum drain time; jobs not completed in that window are killed and enter the DLQ via the normal `on_job_dead` path.

`adcreo-api.service` does not need `KillMode=process` — uvicorn handles graceful shutdown of in-flight requests via its own signal handler.

`adcreo-redis.service` uses the upstream Redis package's recommended unit file with the additional `Restart=always` clause.

---

## [TDD-DISASTER-RECOVERY] · RTO/RPO, Neon PITR, R2 Versioning, Monthly Drill

### [TDD-DISASTER-RECOVERY]-A · Recovery Objectives

| Objective | Target     | Definition                                                                                                                   |
| --------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------- |
| RTO       | 2 hours    | Time from incident declaration to confirmed Postgres restore complete AND FSM integrity check passing.                       |
| RPO       | 5 minutes  | Maximum tolerable data loss measured in clock time. Constrained by Neon PITR granularity.                                    |

The RTO target presumes the env var manifest in the password manager (per Architecture Review G-9-04 — see `[TDD-ENV-MANIFEST]` security rules) is current. Disaster recovery is blocked if env vars are unrecoverable.

### [TDD-DISASTER-RECOVERY]-B · Neon Postgres Recovery

- **PITR enabled** on the production Neon branch. This is configured in the Neon dashboard at branch creation and is verified in the monthly drill.
- **Restore target:** the most recent point in time before the corruption-causing event. Operator selects the timestamp by examining `audit_log` and the application timeline.
- **Restore procedure** documented as a runbook in `/scripts/restore_drill.sh` (see `[TDD-DISASTER-RECOVERY]-D` below).
- **Post-restore integrity check (MANDATORY before resuming traffic):**

  ```
  python ci/validate_state_machine.py --against=$RESTORED_DB_URL
  ```

  The script confirms no row in `generations` is in an illegal state and no `pre_topup_status` coupling is violated. If it fails, do not redirect traffic to the restored branch.

### [TDD-DISASTER-RECOVERY]-C · Cloudflare R2 Recovery

- **Object versioning enabled** on the `adcreo-assets` bucket via the Cloudflare dashboard. Verified in the monthly drill.
- **Retention:** versioned objects recoverable for 30 days. Storage cost is negligible at MVP volume (low-hundreds of MB of versioned tombstones).
- **Recovery procedure:** `aws s3api list-object-versions --bucket adcreo-assets --prefix <user_id>/...` to enumerate; `aws s3api copy-object --copy-source ...&versionId=<vid>` to restore a specific version.
- **Bucket-level invariant:** the `retention_sweep` worker (per `[TDD-R2-RETENTION]`) MUST NOT issue bucket-level delete operations. Object deletes only, per documented `WHERE` clause. Versioning protects against operator error in that script's `WHERE` clause regardless.

### [TDD-DISASTER-RECOVERY]-D · Monthly Restore Drill

- **Script:** `/scripts/restore_drill.sh`.
- **Scope:**

  1. Neon PITR restore to a fresh **staging** branch (never to production).
  2. R2 versioned object recovery test — pick one object, delete it, restore it via the versioned API, verify byte-for-byte identity.
  3. FSM integrity check (`ci/validate_state_machine.py`) against the staging branch.

- **Pass criterion:**

  - FSM integrity check green on staging.
  - One R2 object successfully restored to its original byte content.

- **Documentation:** drill result logged to `docs/restore_drills/YYYY-MM-DD.md`. Each report contains: drill date, operator, RTO observed, RPO observed (Neon timestamp delta), R2 object tested, pass/fail flag, observations.
- **Cadence:** monthly, before the 5th of each month.

### [TDD-DISASTER-RECOVERY]-E · Paired Requirement

The env var manifest in the password manager (Architecture Review G-9-04, encoded in `[TDD-ENV-MANIFEST]`) MUST be complete before the first paying user. If the VPS is lost and env vars are not recoverable from the password manager, the restore is blocked regardless of how good Neon PITR is.

Disaster recovery is the pair of (data recovery) + (configuration recovery). Neither is sufficient alone.

---

## [TDD-DEPLOY-RUNBOOK] · `deploy.sh`, `rollback.sh`, `/healthz` Contracts

### [TDD-DEPLOY-RUNBOOK]-A · `/scripts/deploy.sh` Contract

The deployment script runs on the VPS, executed by the founder (or authorised operator per `[TDD-ROLLBACK]-G`). Sequence:

1. `git pull origin main` — fetch the latest commit.
2. `python ci/run_migrations.py --dry-run` — abort entire deploy if dry-run fails. Print the diff before aborting.
3. `python ci/run_migrations.py --apply` — apply migrations. Migrations are append-only per `[TDD-MIGRATION-SAFETY]-A`.
4. `systemctl kill -s SIGTERM adcreo-studio` and `systemctl kill -s SIGTERM adcreo-render`. Wait for graceful drain. Max wait: 5 minutes (matches `TimeoutStopSec=300` in `[TDD-DEPLOYMENT]-C`). ARQ finishes in-flight jobs, refuses new ones, then exits cleanly.
5. `systemctl restart adcreo-api adcreo-studio adcreo-render`.
6. **Health check loop:** `curl -fsS http://127.0.0.1:8000/healthz` retrying every 5 seconds for 30 seconds (6 attempts total). Abort the deploy and trigger `rollback.sh` if no `HTTP 200` is observed.
7. `git rev-parse HEAD > /var/adcreo/deployed.txt` — record the deployed commit hash. This is the source of truth for "what's running" and is read by `rollback.sh`.
8. `journalctl -u adcreo-api -u adcreo-studio -u adcreo-render --since "30 sec ago" --follow` for 60 seconds, then exit 0. The operator visually confirms there is no error spam in the tail before walking away.

Exit codes:
- `0` — deploy successful.
- non-zero — abort; previous version still serving; `rollback.sh` MAY be invoked depending on the failure point.

### [TDD-DEPLOY-RUNBOOK]-B · `/scripts/rollback.sh <commit-hash>` Contract

Sequence:

1. If `<commit-hash>` argument not provided: read `cat /var/adcreo/deployed.txt`. The contents are the PREVIOUSLY deployed commit (recorded by `deploy.sh` step 7 of the prior deploy). Use that.
2. `git checkout <commit-hash>`.
3. Repeat `deploy.sh` steps 4 through 7 (drain → restart → health-check → record).

**Rollback does NOT reverse migrations.** Migrations are forward-only and must be backwards-compatible per `[TDD-MIGRATION-SAFETY]-A` (Append-Only Principle). Reversing them in a rollback would corrupt in-flight transactions and the wallet ledger.

If the rollback target requires a migration to be undone, follow the Multi-Deploy Dance (`[TDD-MIGRATION-SAFETY]-C`) — destructive changes are not the responsibility of the rollback script.

### [TDD-DEPLOY-RUNBOOK]-C · Graceful Drain Requirement

ARQ workers handle `SIGTERM` by:

1. Stopping consumption of new jobs from the queue.
2. Completing all currently in-flight jobs to their normal `on_job_end` or `on_job_dead` exit.
3. Exiting cleanly.

This is enabled by `KillMode=process` and `TimeoutStopSec=300` in the systemd unit files (see `[TDD-DEPLOYMENT]-C`). Maximum drain timeout: 5 minutes. A job exceeding 5 minutes is killed by systemd; the job enters DLQ via the normal `on_job_dead` path on next worker startup.

### [TDD-DEPLOY-RUNBOOK]-D · `/healthz` Endpoint Contract

Route: `GET /healthz` on `adcreo-api`. No authentication. No rate limit beyond what Nginx applies globally.

Returns `HTTP 200` with body:

```json
{"status": "ok", "ts": "<iso8601>"}
```

…if BOTH of the following hold:

- Postgres connection pool is responsive: `SELECT 1` succeeds within 2 seconds.
- Redis is responsive: `PING` returns `PONG` within 2 seconds.

Returns `HTTP 503` with body:

```json
{"status": "error", "ts": "<iso8601>", "failing": ["postgres" | "redis"]}
```

…if either check fails.

The route MUST NOT touch the wallet ledger, the FSM trigger, or any per-user state. It is a pure liveness probe — independent of any individual user's data.

Used by:
- `deploy.sh` step 6 (post-restart health check).
- Optional Cloudflare Tunnel health check (configured in the Cloudflare dashboard).

---

## [TDD-ENV-MANIFEST] · Environment Variable Inventory

Every environment variable the application reads is listed below. The `ci/validate_env_manifest.py` Stage 1 CI job (see `[TDD-CICD]-A`) greps `os.getenv(...)` and `os.environ[...]` across `app/` and fails the build if any read key is not present in this manifest and `.env.example`.

**Convention.** Required = the process refuses to start (or fails its `/healthz` probe) without it. Optional = sensible default is hard-coded; setting the var overrides the default.

### [TDD-ENV-MANIFEST]-A · Core Application

| Variable                | Required | Read by                  | Example (non-secret)                | Description                                                                                                       |
| ----------------------- | -------- | ------------------------ | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `JWT_SECRET`            | yes      | `adcreo-api`             | (256-bit random hex)                | HS256 signing key for user JWTs. Rotated quarterly. NEVER in code — `[TDD-SECURITY]-A`.                            |
| `ENV`                   | yes      | all services             | `production` \| `staging` \| `development` | Drives structlog renderer choice (JSON vs Console) and Sentry environment tag.                            |
| `NEXT_PUBLIC_APP_URL`   | yes      | Next.js frontend         | `https://adcreo.com`                | Public origin of the frontend. Used by the frontend to build absolute URLs.                                       |

### [TDD-ENV-MANIFEST]-B · Database (Neon Postgres)

| Variable                | Required | Read by                                      | Example (non-secret)                       | Description                                                                                                       |
| ----------------------- | -------- | -------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`          | yes      | `adcreo-api`, `adcreo-studio`, `adcreo-render` | `postgresql://...neon.tech/adcreo?sslmode=require` | Neon connection string. Includes `?sslmode=require`. Replica vs primary routed via Neon branch URL.        |
| `DB_POOL_MIN`           | optional | all services                                 | `2`                                        | Min connections per process. Default 2.                                                                            |
| `DB_POOL_MAX`           | optional | all services                                 | `10`                                       | Max connections per process. Default 10. Tune so total ≤ Neon connection ceiling.                                  |

### [TDD-ENV-MANIFEST]-C · Redis

| Variable                | Required | Read by                                      | Example (non-secret)         | Description                                                                                                       |
| ----------------------- | -------- | -------------------------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `REDIS_URL`             | yes      | `adcreo-api`, `adcreo-studio`, `adcreo-render` | `redis://127.0.0.1:6379`     | Base Redis URL. DB index is appended per usage per `[TDD-REDIS]-A`.                                                |
| `REDIS_DB_INDEX_MAP`    | optional | services                                     | (hard-coded; not env)        | The 6-DB index map is fixed in `[TDD-REDIS]-A`. This var exists only for staging override; production uses code defaults. |

### [TDD-ENV-MANIFEST]-D · AI Providers

| Variable                | Required | Read by                                | Example (non-secret)                   | Description                                                       |
| ----------------------- | -------- | -------------------------------------- | -------------------------------------- | ----------------------------------------------------------------- |
| `OPENAI_API_KEY`        | yes      | `adcreo-studio` (Gateway)              | `sk-...`                               | OpenAI capability route.                                          |
| `DEEPSEEK_API_KEY`      | yes      | `adcreo-studio` (Gateway)              | `sk-...`                               | DeepSeek for framework-router and script generation.              |
| `GROQ_API_KEY`          | yes      | `adcreo-studio` (Gateway)              | `gsk_...`                              | Groq Llama Guard for `safety-check`.                              |
| `GEMINI_API_KEY`        | yes      | `adcreo-studio` (Gateway)              | `AIza...`                              | Gemini vision for category-classifier.                            |
| `TOGETHER_API_KEY`      | yes      | `adcreo-studio` (Gateway)              | `...`                                  | Together AI fallback for chat / critic.                           |
| `SILICONFLOW_API_KEY`   | yes      | `adcreo-studio` (Gateway)              | `sk-...`                               | SiliconFlow fallback.                                             |
| `FAL_API_KEY`           | yes      | `adcreo-render` (I2V worker)           | `<key>:<secret>`                       | Fal.ai for image-to-video.                                        |
| `MINIMAX_API_KEY`       | yes      | `adcreo-render` (I2V worker)           | `...`                                  | Minimax I2V fallback.                                             |

### [TDD-ENV-MANIFEST]-E · Voice / TTS

| Variable                | Required | Read by                  | Example (non-secret) | Description                                          |
| ----------------------- | -------- | ------------------------ | -------------------- | ---------------------------------------------------- |
| `SARVAM_API_KEY`        | yes      | `adcreo-render` (TTS)    | `...`                | Sarvam Bulbul V3 — primary Indic TTS.                |
| `ELEVENLABS_API_KEY`    | yes      | `adcreo-render` (TTS)    | `...`                | ElevenLabs fallback for non-Indic voices.            |

### [TDD-ENV-MANIFEST]-F · Scraping

| Variable                | Required | Read by                       | Example (non-secret) | Description                                          |
| ----------------------- | -------- | ----------------------------- | -------------------- | ---------------------------------------------------- |
| `FIRECRAWL_API_KEY`     | yes      | `adcreo-studio` (extract)     | `fc-...`             | Firecrawl for product URL extraction.                |

### [TDD-ENV-MANIFEST]-G · Storage (Cloudflare R2)

| Variable                  | Required | Read by                                    | Example (non-secret)                                  | Description                                              |
| ------------------------- | -------- | ------------------------------------------ | ----------------------------------------------------- | -------------------------------------------------------- |
| `R2_ENDPOINT`             | yes      | `adcreo-api`, `adcreo-render`              | `https://<accountid>.r2.cloudflarestorage.com`         | R2 S3-compatible endpoint URL.                          |
| `R2_BUCKET`               | yes      | services                                   | `adcreo-assets`                                        | Bucket name. Versioning enabled per `[TDD-DISASTER-RECOVERY]-C`. |
| `R2_ACCESS_KEY_ID`        | yes      | services                                   | (per Architecture Review A-2-01, scoped, rotated quarterly) | Write token scoped to `gen-uploads/` and `gen-exports/`.          |
| `R2_SECRET_ACCESS_KEY`    | yes      | services                                   | `...`                                                  | Paired secret for the above.                            |
| `R2_READONLY_ACCESS_KEY_ID` | optional | read-only paths                           | `...`                                                  | Read-only token. Scoped to specific prefixes.            |
| `R2_READONLY_SECRET_ACCESS_KEY` | optional | read-only paths                       | `...`                                                  | Paired secret for the above.                            |

### [TDD-ENV-MANIFEST]-H · Payments (Razorpay)

| Variable                       | Required | Read by      | Example (non-secret) | Description                                                  |
| ------------------------------ | -------- | ------------ | -------------------- | ------------------------------------------------------------ |
| `RAZORPAY_KEY_ID`              | yes      | `adcreo-api` | `rzp_live_...`       | Public key ID for Razorpay SDK and frontend Checkout config. |
| `RAZORPAY_KEY_SECRET`          | yes      | `adcreo-api` | `...`                | Private key for server-side API calls.                       |
| `RAZORPAY_WEBHOOK_SECRET`      | yes      | `adcreo-api` | `...`                | HMAC-SHA256 webhook signature secret, per `[TDD-SECURITY]-C`. |

### [TDD-ENV-MANIFEST]-I · Authentication (Google OAuth)

| Variable                       | Required | Read by      | Example (non-secret) | Description                                          |
| ------------------------------ | -------- | ------------ | -------------------- | ---------------------------------------------------- |
| `GOOGLE_OAUTH_CLIENT_ID`       | yes      | `adcreo-api`, Next.js | `...apps.googleusercontent.com` | Google OAuth client ID.                              |
| `GOOGLE_OAUTH_CLIENT_SECRET`   | yes      | `adcreo-api` | `...`                | Google OAuth client secret.                          |

### [TDD-ENV-MANIFEST]-J · Observability

| Variable                  | Required | Read by                                   | Example (non-secret)                | Description                                                                |
| ------------------------- | -------- | ----------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------- |
| `SENTRY_DSN`              | yes      | `adcreo-api`, `adcreo-studio`, `adcreo-render` | `https://...@sentry.io/...`         | Sentry project DSN. Configured in `app/main.py`. See `[TDD-OBSERVABILITY]-C`. |
| `POSTHOG_API_KEY`         | yes      | `adcreo-api`, Next.js                     | `phc_...`                           | PostHog backend write key. See `[TDD-OBSERVABILITY]-D`.                     |
| `POSTHOG_HOST`            | optional | `adcreo-api`, Next.js                     | `https://app.posthog.com`           | PostHog API host. Default `app.posthog.com`.                                |
| `LOKI_PUSH_URL`           | yes      | `grafana-agent` sidecar                   | `https://logs-prod-...grafana.net/loki/api/v1/push` | Grafana Loki ingest URL.                                          |
| `GRAFANA_AGENT_TOKEN`     | yes      | `grafana-agent` sidecar                   | `...`                               | Bearer token for Grafana Cloud authentication.                              |
| `PROMETHEUS_REMOTE_WRITE_URL` | optional | local Prometheus                       | `https://prometheus-prod-...grafana.net/api/prom/push` | Remote-write target. Required only when Prometheus runs on VPS.       |

### [TDD-ENV-MANIFEST]-K · Feature Flags

| Variable                | Required | Read by                                      | Example (non-secret)         | Description                                                                                                       |
| ----------------------- | -------- | -------------------------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `AW_API_MODE`           | yes      | `adcreo-api`, `adcreo-studio`, `adcreo-render` | `stub` (CI) \| `live` (production) | Per `[TDD-API-STUBS]-B`. `stub` activates the static fixture harness. `live` calls real providers.            |

### [TDD-ENV-MANIFEST]-L · CI-Specific

| Variable      | Required | Read by   | Example      | Description                                                                                |
| ------------- | -------- | --------- | ------------ | ------------------------------------------------------------------------------------------ |
| `TZ`          | yes (CI) | CI runner | `Asia/Kolkata` | Required for Postgres trigger time-window correctness. Set unconditionally in all CI jobs. |

### [TDD-ENV-MANIFEST]-M · Security Rules

Mandatory, repeated here so they cannot be missed:

1. **`.env` files are never committed to git.** Only `.env.example` (with placeholder values) is committed.
2. **Separate keys for development and production.** Credentials are never shared across environments. Compromise of dev never gives access to production.
3. **Rotate all keys before the first paying user.** This includes Razorpay keys, R2 tokens, JWT secret, all AI provider keys. Document the rotation date alongside each key in the password manager.
4. **All production secrets stored in GCP Secret Manager** (already provisioned). The password manager (per Architecture Review G-9-04) holds the *manifest* — the list of which keys exist, what they unlock, and when they were last rotated. The actual values live in Secret Manager and are injected to systemd units via the `EnvironmentFile=` directive pointing to a root-readable secrets file populated at deploy time.
5. **Quarterly rotation cadence** for `JWT_SECRET`, all R2 tokens, and all AI provider keys. Each rotation logged to `docs/secret_rotations/YYYY-MM-DD.md` with the operator's signature.

---

## CONSISTENCY FLAGS

The merge identified the following issues during the consistency pass per the instructions. Each flag names the section that contains the issue and the action required. **None of these are fixed in this document — they are reported here so the human merge pass can address them systematically.**

### Check 1 — CI job name consistency

**Status:** PASS — no stale references identified.

The new `[TDD-CICD]` defines jobs by these names: `lint`, `typecheck`, `static-guards`, `unit-test`, `fsm-test`, `migration-dry-run`, `integration-test`, `contract-test`, `e2e-test`.

Old v3 job names that no longer exist as standalone jobs: `lint-and-typecheck` (never used — v3 had separate `lint` and `typecheck`, preserved), `promptops-validate` (rolled into `static-guards` as `ci/validate_prompts.py`), `compliance-gate` (rolled into `static-guards` as `ci/check_banned_patterns.py`), `strategist-sandbox` (rolled into `static-guards` as `ci/strategist_sandbox_check.py`), `fsm-coverage` (renamed to `fsm-test`), `chat-chain-order` (this was a pytest target, not a CI job name — preserved within `unit-test` or `integration-test`).

Scan of preserved Category 1 sections reveals no body references to these standalone job names. If a TDD v3 section that I have placeholdered (and that the human must paste) contains a reference, the human merge pass must update the reference at paste time. To verify: after pasting, `grep -E 'promptops-validate|compliance-gate|strategist-sandbox|fsm-coverage|chat-chain-order' TDD_v4_final.md` should return only mentions inside the `static-guards` definition itself (where they appear as script names) and inside this Consistency Flags section.

### Check 2 — Worker name consistency — `[CONSISTENCY-FLAG]`

**Status:** FLAGGED — expected stale references in preserved Category 1 sections.

Old names: `adcreo-studio`, `adcreo-render`.
New names: `adcreo-studio`, `adcreo-render` respectively.

Confirmed occurrences in TDD v3 sections preserved verbatim (line numbers from the v3 source file as supplied):

| Line  | Section / context                              | Stale reference                                                |
| ----- | ---------------------------------------------- | -------------------------------------------------------------- |
| 78    | `[TDD-OVERVIEW]` Tech Stack row "Task Queue"   | `adcreo-studio`, `adcreo-render`                        |
| 116   | `[TDD-PILLARS]` Pillar 6 row                   | `adcreo-render`                                               |
| 174   | `[TDD-STACK]` ASCII diagram                    | `adcreo-render`                                               |
| 192–195 | `[TDD-STACK]` process description            | `adcreo-studio`, `adcreo-render`                        |
| 271   | `[TDD-DATA-FLOW]` flow box                     | `adcreo-studio`                                          |
| 2080  | `[TDD-WORKERS]` preamble                        | `adcreo-studio`, `adcreo-render`                        |
| 3253  | `[TDD-WORKERS]-I` Worker-EXPORT registration   | `adcreo-render`                                               |
| 3942  | `[TDD-API]-D` enqueue call                      | `_queue_name="adcreo-render"`                                 |
| 3980  | `[TDD-API]-E` enqueue call                      | `_queue_name="adcreo-studio"`                            |
| 4039  | `[TDD-API]-F` enqueue call                      | `_queue_name="adcreo-render"`                                 |
| 4108  | `[TDD-API]-G` enqueue call                      | `_queue_name="adcreo-render"`                                 |
| 4227  | `[TDD-REDIS]-A` namespace table                 | `arq:queue:phase1_to_3`, `arq:queue:adcreo-render`            |

**Action required:** during the human merge pass, perform a project-wide find-replace **inside the pasted Category 1 sections**:

- `adcreo-studio` → `adcreo-studio`
- `adcreo-render` → `adcreo-render`
- `arq:queue:phase1_to_3` → `arq:queue:adcreo-studio`
- `arq:queue:adcreo-render` → `arq:queue:adcreo-render`

After replacement, run a final grep to confirm zero remaining occurrences of the old names anywhere in the document (except in this Consistency Flags section, which intentionally preserves them as audit evidence).

### Check 3 — Observability cross-reference consistency

**Status:** PASS.

`ci/observability_lint.py` is named as a Stage 1 CI script in `[TDD-CICD]-A` under the `static-guards` job (item 5 of the six-script list). `[TDD-OBSERVABILITY]-A` references it by the same name. The two definitions are consistent.

### Check 4 — Screen contract cross-reference — `[CONSISTENCY-FLAG]`

**Status:** FLAGGED.

`[TDD-FSM]-SCREEN-CONTRACT` (Category 3A) requires `GET /api/generations/{gen_id}` to include a `screen_descriptor` block in its response. The preserved `[TDD-API]-B` response shape is:

```python
return {
    "status": gen["status"],
    "error_code": gen["error_code"],
    "confidence_score": gen["confidence_score"]
}
```

This shape does NOT include `screen_descriptor`.

**Action required:** during the human merge pass, extend `[TDD-API]-B` to compute and return `screen_descriptor`. The serializer logic is owned by `models/generation_view.py` per `[TDD-FSM]-SCREEN-CONTRACT`. The route call site simply includes the descriptor in the response dict. Also extend the `StatusResponse` Pydantic model in `[TDD-TYPES]-B` to declare the field. Do not rewrite the route — only add the field.

A flag is also implicit in `[TDD-TYPES]-A` (TypeScript `GenerationState` interface): a `screen_descriptor` field must be added there too, mirroring the Pydantic model.

### Check 5 — Webhook idempotency cross-reference — `[CONSISTENCY-FLAG]`

**Status:** FLAGGED.

`[TDD-CONCURRENCY]-F` (Category 3B) introduces a new `processed_webhooks` table. The preserved `[TDD-MIGRATIONS]` migration script does NOT contain this table.

**Action required:** during the human merge pass, append the following migration step to `[TDD-MIGRATIONS]` (placed BEFORE the COMMIT of the existing append-only migration, or as a new sequentially-numbered migration file per `[TDD-MIGRATION-SAFETY]-B`):

```sql
CREATE TABLE processed_webhooks (
  event_id    TEXT        PRIMARY KEY,
  payment_id  TEXT        NOT NULL,
  processed_at TIMESTAMPTZ DEFAULT NOW(),
  result      JSONB
);
```

A second, related flag: the preserved `[TDD-API]-H` (Razorpay webhook handler) does NOT perform the `processed_webhooks` INSERT before the wallet transaction writes. During the human merge pass, prepend the INSERT inside the `async with db.transaction()` block per the contract in `[TDD-CONCURRENCY]-F`. Keep the existing `razorpay_payment_id` UniqueViolation guard as the third safety net (it already exists in v3; do not remove it).

### Check 6 — Sentry, PostHog, Loki env vars in manifest

**Status:** PASS.

All five required keys appear in `[TDD-ENV-MANIFEST]-J · Observability`:

- `SENTRY_DSN` ✓
- `POSTHOG_API_KEY` ✓
- `POSTHOG_HOST` ✓ (optional with default)
- `LOKI_PUSH_URL` ✓
- `GRAFANA_AGENT_TOKEN` ✓

### Summary of action items for the human merge pass

| # | Action                                                                                                       | Section to edit              | Difficulty |
| - | ------------------------------------------------------------------------------------------------------------ | ---------------------------- | ---------- |
| 1 | Paste every Category 1 section from TDD v3 into its placeholder slot.                                        | All Category 1 sections      | Mechanical |
| 2 | Find-replace worker names `adcreo-studio` → `adcreo-studio` and `adcreo-render` → `adcreo-render` in pasted content. | All Category 1 sections      | Mechanical |
| 3 | Find-replace ARQ queue names `arq:queue:phase1_to_3` → `arq:queue:adcreo-studio` and `arq:queue:adcreo-render` → `arq:queue:adcreo-render`. | `[TDD-REDIS]-A`             | Mechanical |
| 4 | Add `screen_descriptor` field to `[TDD-API]-B` response shape and to `StatusResponse` (Pydantic) and `GenerationState` (TS). | `[TDD-API]-B`, `[TDD-TYPES]-A`, `[TDD-TYPES]-B` | Trivial |
| 5 | Add `processed_webhooks` migration to `[TDD-MIGRATIONS]`.                                                    | `[TDD-MIGRATIONS]`           | Trivial    |
| 6 | Prepend `processed_webhooks` INSERT inside the transaction block of `[TDD-API]-H`.                            | `[TDD-API]-H`                | Trivial    |
| 7 | Add traceability rows for `[TDD-DEPLOYMENT]`, `[TDD-DISASTER-RECOVERY]`, `[TDD-DEPLOY-RUNBOOK]`, `[TDD-ENV-MANIFEST]` under group G of `[TDD-TRACE]`. | `[TDD-TRACE]-G` | Trivial    |
| 8 | After all edits: run a project-wide `grep` for `adcreo-studio`, `adcreo-render`, `arq:queue:phase1_to_3`, `arq:queue:adcreo-render` — confirm zero occurrences outside this `CONSISTENCY FLAGS` section. | global | Verification |

---

---

## V5 CHANGELOG (v4 → v5 — v4-Δ1 B-Roll consistency migration)

This changelog enumerates every edit landed in v5. Section anchors are preserved; the `[TDD-BROLL]` chapter introduced in v4-Δ1 is the authoritative source for B-roll behavior. Every edit below traces back to an `[TDD-BROLL]-X` sub-anchor.

1. **Header** — version 4.0 → 5.0; date 2026-05-18 → 2026-05-19; supersedes line updated; status note clarified.
2. **Table of Contents** — `[TDD-BROLL]` inserted between `[TDD-WORKERS]` and `[TDD-VIDEO]`; trailing notes added to `[TDD-WORKERS]` (C2 superseded; G extended) and `[TDD-VIDEO]` (signature change).
3. **`[TDD-DATA-FLOW]`** — strategist comment rewritten to describe template resolution + structured plan output (was `b_roll_plan[3]` flat list).
4. **`[TDD-SCAFFOLD]`** — `broll/` directory now shows `library.json`, `planner.py`, `templates.py` (CI-locked routing dict module).
5a. **`[TDD-SCHEMA]` · `generations`** — `b_roll_plan` DEFAULT `'[]'` → `NULL`; three new columns added (`structure_template`, `active_season`, `b_roll_performance_signal`).
5b. **`[TDD-SCHEMA]` · `chk_b_roll_plan_shape`** — rewritten from array-shape CHECK to object-shape CHECK with `template` ∈ `{T1..T5}` enum guard.
6. **`[TDD-SCHEMA]` · `broll_clips`** — 6 new columns (`role`, `mood_energy`, `mood_temperature`, `negative_space_score`, `seasonality_tags`, `brand_tier_fit`), `chk_cta_negative_space` CHECK, two new indices (`idx_broll_role_category_tier` partial, `idx_broll_seasonality` GIN).
7. **`[TDD-SCHEMA]` · `user_style_profiles`** — `brand_tier` (mass/premium/luxury) + `brand_color_primary` (7-char hex, nullable, neutral-charcoal fallback in Worker-COMPOSE) added. *(Resolves F3 with Option A: explicit column.)*
8. **`[TDD-SCHEMA]` · new tables** — `broll_clip_usage` (per-(user, clip, gen) rotation history; CASCADE on all FKs; FK target is the canonical `users(user_id)`, not `users(id)`) and `seasons` (lookup with `is_active = FALSE` default for ops gating).
9. **`[TDD-TYPES]-A`** — `BRollClip` extended with 6 fields; new `BRollPlan` interface; `StrategyCardV3.b_roll_plan` typed as `BRollPlan | null`; `structure_template` + `active_season` + `b_roll_available` surfaced.
10. **`[TDD-TYPES]-B`** — Pydantic `BRollClip` extended with `Literal`-typed enums; new `BRollPlan` model; `StrategyCardOutput.b_roll_plan: BRollPlan | None`; `structure_template` + `active_season` fields.
11. **`[TDD-MIGRATIONS]` · `broll_clips` IF NOT EXISTS** — idempotent `ADD COLUMN IF NOT EXISTS` for all 6 new columns, with safe backfills before NOT NULL/CHECK constraints are enforced; partial + GIN indices `IF NOT EXISTS`.
12. **`[TDD-MIGRATIONS]` · `b_roll_plan` shape migration** — DEFAULT changed to NULL; legacy array rows backfilled to NULL BEFORE the new CHECK is applied; CHECK rewritten to object shape with template enum guard.
13. **`[TDD-MIGRATIONS]` · new steps (22)–(26)** — added INSIDE the existing transaction (before `COMMIT;`): (22) `broll_clip_usage` table + index, (23) `seasons` table + seed (six Indian-market seasons with `is_active = FALSE`), (24) `generations.structure_template / active_season / b_roll_performance_signal`, (25) `user_style_profiles.brand_tier / brand_color_primary`, (26) `broll_v4_routing_enabled` feature flag (default FALSE — safe rollout).
14. **`[TDD-MIGRATIONS]` · `tier2_degradation_enabled` description** — rewritten to describe new degradation behavior (force T1/text-card-CTA fallback) per `[TDD-BROLL]-I`.
15. **`[TDD-INDICES]`** — three new index entries appended (`idx_broll_role_category_tier`, `idx_broll_seasonality`, `idx_broll_usage_user_recent`).
16. **`[TDD-WORKERS]-A`** — STRATEGIST row reads extended (`seasons`, `broll_clip_usage`, `brand_tier`, `brand_color_primary`) + writes extended (`structure_template`, `active_season`, `broll_clip_usage` INSERT); COMPOSE row reads extended (`structure_template`, `brand_tier`, `brand_color_primary`).
17. **`[TDD-WORKERS]-C2`** — body replaced (149 lines) with a supersede pointer block listing every relevant `[TDD-BROLL]-X` sub-anchor; anchor ID preserved so PRD F-405 traceability + BEF §9.6 + in-repo docstring references continue to resolve.
18. **`[TDD-WORKERS]-G` · `WorkerStrategist.process()`** — adds 5-step template resolution flow (season → brand tier → template → planner → atomic persist + usage log); feature-flag gate (`broll_v4_routing_enabled`) short-circuits to T1-only in legacy mode; the entire plan + template + season + clip-usage writes happen inside one `self.db.transaction()` so rotation determinism is never corrupted by a partial write.
19. **`[TDD-WORKERS]-G` · `b_roll_available`** — paragraph rewritten for the new shape (`b_roll_plan is non-null AND b_roll_plan.hook is non-null`); reference to the superseded `[TDD-WORKERS]-C2` invariants updated.
20. **`[TDD-WORKERS]-H` · Worker-COMPOSE docstring + signature** — `Canonical 5s` typo fixed to `Canonical 15s` (was incorrect in v3/v4); v4-Δ1 docstring added; `process()` signature extended with `structure_template`, optional `brand_color_primary`.
21. **`phase4_coordinator`** — docstring updated (segment structure per `structure_template`); generation SELECT widened to include `structure_template` + `strategy_card`; the "Stitch 3s + 9s + 3s" comment generalized; `WorkerCompose().process(...)` call passes the new args including `brand_color_primary` sourced from the strategy card.
22. **`[TDD-VIDEO]-A`** — 15s timeline rewritten as pointer to `[TDD-BROLL]-C`; T1 retained inline as backward-continuity example with `role`-filtered `broll_clips` sources.
23. **`[TDD-VIDEO]-B`** — `WorkerCompose` code block rewritten: signature now takes `b_roll_plan: dict` + `structure_template: str` + optional `brand_color_primary`; empty-plan hard-fail kept as a defense-in-depth check (CI coverage is the primary guarantee); new `_build_segments_for_template` method materializes per-template segment list (T1..T5) and downloads only the clips the template needs; new `_render_cta_text_card` method generates the T2/T3/T4/T5 CTA via `lavfi color=` + `drawtext` (no new dependencies, mirrors F-403 watermark pattern); `filter_complex` graph generalized from fixed 3-stream concat to variable-arity `n=len(segments)` concat — works for all five templates without further code changes.
24. **`[TDD-IMPORT-GRAPH]`** — `RULES` dict gains an `app/broll/` prefix entry forbidding HTTP clients AND embedding-library imports (`sentence_transformers`, `chromadb`, `faiss`, `transformers`, `torch`); v4-Δ1 note added explaining the rationale.
25a. **`[TDD-CICD]-A`** — `ci/broll_coverage_check.py` added as static-guards item #7 (asserts every routable `(angle, category_class, brand_tier)` triple has clips for every required role, and every active season has clips with matching `seasonality_tags`); existing `ci/strategist_sandbox_check.py` bullet annotated with the v4-Δ1 scope extension.
25b. **`[TDD-TRACE]-E` · F-405 row** — rewritten to point at `[TDD-BROLL]` (full chapter), the three new schema tables, `[TDD-WORKERS]-G`, and `[TDD-VIDEO]-A/B`, while preserving the `[TDD-WORKERS]-C2` link (now a supersede pointer).

### Architect-pass corrections beyond the consistency migration

26. **FK target typo in `[TDD-BROLL]-E`** — `broll_clip_usage.user_id REFERENCES users(id)` corrected to `REFERENCES users(user_id)` (the canonical PK target used by every other FK in the schema). Without this fix the migration would have failed on apply.
27. **Architecture-summary plan shape in `[TDD-BROLL]-B`** — `{hook, context[], cta}` (array notation) corrected to `{template, hook, context, cta}` (object) to match the rest of the chapter, the JSONB CHECK, the TypeScript types, and the Pydantic models.
28. **Routing dict name mismatch in `[TDD-BROLL]-C`** — `TEMPLATE_BY_ANGLE_AND_TIER` (introductory sentence) corrected to `TEMPLATE_BY_CONTEXT` (matches the actual frozen dict that follows + the strategist import + the coverage check).
29. **`[TDD-BROLL]-K` invariant 4 wording** — clarified that `chk_b_roll_plan_shape` was **rewritten** in v4-Δ1 (not "retained" as the original wording said); structural bounding is now provided by the JSONB object shape itself plus role purity.
30. **`[TDD-BROLL]-H` brand color fallback** — explicit `#1A1A1A` neutral-charcoal fallback documented for NULL `brand_color_primary` (cold-start brands); aligns the chapter with the schema decision documented in EDIT 7.
31. **`Canonical 5s` docstring typo** — Worker-COMPOSE class docstring at the `[TDD-WORKERS]-H` site corrected to `Canonical 15s` (pre-existing v3/v4 bug; unrelated to B-roll but caught during this pass).

### V5 verification (run by the architect during the pass)

- `grep -E 'b_roll_plan\[[0-9]\]|len\(b_roll_plan\)|b_roll_plan: list\[BRollClip\]'` → zero hits (only a documentation comment that *describes* the old shape).
- `grep -E 'REFERENCES users\(id\)'` → zero hits.
- `grep -E '^-- \(2[2-6]\)'` → all five new migration steps present, in numeric order, before the `COMMIT;`.
- All 12 `[TDD-BROLL]-*` anchors intact and untouched in body content (only internal typos and the FK target were corrected per architect authorization).
- `Canonical 5s` → zero hits across the document.

---

## CONSISTENCY FLAGS

Flags carried forward from v4-Δ1 design pass. All production-blocking items are RESOLVED in this V5 (see V5 CHANGELOG). The remaining flags are architectural decisions deferred to v2 or items pending source-doc cleanup.

| ID | Status | Description |
|----|--------|-------------|
| **F1** | RESOLVED (in V5) | `chk_b_roll_plan_shape` rewritten in `[TDD-SCHEMA]` and `[TDD-MIGRATIONS]` from array form to object form with `template ∈ {T1..T5}` enum guard. NULL permitted explicitly. `[TDD-BROLL]-K` invariant 4 wording corrected to say "rewritten" rather than "retained" (was misleading). |
| **F2** | RESOLVED (in V5) | `b_roll_plan` DEFAULT changed to NULL in both `[TDD-SCHEMA]` and `[TDD-MIGRATIONS]`. Migration step 22 includes the backfill `UPDATE generations SET b_roll_plan = NULL WHERE jsonb_typeof(b_roll_plan) <> 'object'` which runs BEFORE the new CHECK is applied — legacy `'[]'` rows are migrated cleanly. |
| **F3** | RESOLVED (Option A — column added) | `brand_color_primary VARCHAR(7) CHECK hex-format` added to `user_style_profiles` with NULL default. Worker-COMPOSE falls back to `#1A1A1A` (neutral charcoal) when NULL. `[TDD-BROLL]-H` updated to document the fallback. Rationale: deferring this would have made `[TDD-BROLL]-H` reference a dead column permanently; adding a nullable column with a sensible fallback costs nothing and gives forward flexibility for onboarding-driven brand customization. |
| **F4** | RESOLVED | `broll_clip_usage` FKs are all `ON DELETE CASCADE`. Rationale: rotation history only matters while parent rows exist; clip retirement (`is_active=FALSE` then hard-delete in cleanup) should sweep the dead history with it. Also applied to `user_id` and `gen_id` FKs for the same reason. |
| **F5** | FLAGGED (v2 work, not v1-blocking) | `broll_clip_usage` has no retention policy. At 3,000 users × ~1 gen/day × ≤3 clips/gen × 90 days the table is ≤810K rows — trivial for Postgres at that scale and rotation only ever needs the last 3 gens per user. **Recommended v2 action:** daily prune job removing rows older than 90 days, or piggyback on the existing R2 retention sweep. Not adding the prune job in v1 is a deliberate choice — the table is bounded enough at launch volume that adding a sweep would be cargo-culted complexity. Re-evaluate at 10K MAU. |
| **F6** | RESOLVED (decoupled) | `plan_tier × structure_template` interaction is explicitly **decoupled** in v1. Template selection depends on `(framework_angle, category_class, brand_tier)` and the festive override — NOT on `plan_tier`. Rationale: `brand_tier` is per-brand (a small-merchant Starter user with a premium brand should still get T2); `plan_tier` is per-user-account and already gates other things (generation count, model quality). Conflating the two would mean a Starter user with a luxury watch brand gets a mass-market template — wrong for both the user and the brand. The `broll_v4_routing_enabled` feature flag (migration step 26) provides a global kill-switch if T2-T5 turn out to be too expensive on Starter at scale; we re-evaluate post-launch with real cost data. |
| **F7** | RESOLVED (in V5) | `broll_clip_usage.user_id REFERENCES users(id)` in the original `[TDD-BROLL]-E` was a typo — the canonical PK target is `users(user_id)` (every other FK in the schema confirms this). Corrected in both the source chapter AND in the schema/migrations. |
| **EDIT-23.5** | RESOLVED (in V5) | The fixed 3-stream `filter_complex` concat in `[TDD-VIDEO]-B` (valid only for T1/T3/T4 in the original prompt's framing) has been generalized to a variable-arity `concat=n=len(segments):v=1:a=0` graph. T2 and T5 (2-stream) and T3/T4 (4-stream) all flow through the same code path. No further generalization work needed for v1. |

### Carried-forward items from v4 (NOT v4-Δ1 — original v3→v4 flags)

These are pre-existing flags from the original v3→v4 merge. Listed here for completeness; none are blocked by the v4-Δ1 work.

- **Webhook idempotency migration** (`[TDD-CONCURRENCY]-F` Category 3B introduced `processed_webhooks`; v3 migrations did not). Tracked in the v4 "action items for the human merge pass" table at the foot of this document.
- **Category 1 verbatim pastes** (`[SECTION PRESERVED FROM TDD V3 — COPY VERBATIM]` placeholders, if any remain). Verify via global grep in CI.

### Out-of-scope SSOT misalignments (PRD / BEF tickets)

These require edits to PRD and BEF, not to TDD. **Open separate tickets, do not bundle into V5.**

- **PRD F-405** — describes B-roll categories as "abstract / motion / texture / warehouse / packaging"; conflicts with the new role-based taxonomy and the "warehouse" category implies a recognizable location which contradicts `[PRD-NON-NEGOTIABLES]` Product-Visual First. Update PRD F-405 to reflect role-first taxonomy.
- **BEF §9.6** — `BRollPlanner.plan(framework_angle, category)` signature is stale; new contract is `plan(template, angle, category, brand_tier, user_id, active_season)`.
- **BEF G3** — determinism statement covers only two inputs; new contract is five (rotation history is treated as part of the input).
- **BEF L1355** — `broll_clips` schema description missing role / mood / seasonality / brand_tier_fit fields.
- **BEF L1445** — STRATEGIST permission line missing reads/writes for `seasons`, `broll_clip_usage`, `brand_tier`, `brand_color_primary`, `structure_template`, `active_season`.
- **BEF L1492 / TDD-R2-BUCKETS** — R2 folder structure (`/broll/abstract/`, `/broll/motion/`, etc.) may not match the new role-first curation plan. Verify against the curated `app/broll/library.json` shipped with v1 and update either side to match.

---

**END OF TDD v5**

