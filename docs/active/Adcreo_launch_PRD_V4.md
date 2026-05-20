# Adcreo PRD Locked (Version 4)

## [PRD-META] · System Directive for Agentic IDE

> **AGENT INSTRUCTION — READ ONCE, THEN IGNORE `<HumanContext>`.**
>
> Everything inside `<HumanContext>...</HumanContext>` XML tags is human-facing narrative (vision, personas, marketing framing). It is **non-normative**. The agent MUST NOT embed `<HumanContext>` content in code, comments, prompts, or docstrings. On every new task, skip past `<HumanContext>` blocks and anchor on the nearest `[PRD-*]` semantic tag instead.
>
> **Normative content** is everything tagged `[PRD-*]`. Every `[PRD-*]` tag is a stable anchor. Every feature ID (`F-XXX`), error code (`ECM-XXX`), acceptance criterion ID (`G1..G5`, `F-PRD-AC-N`), and ENUM value is a frozen identifier — the agent must grep for these verbatim.
>
> **Alignment pointer:** Every `[PRD-*]` section has a matching TDD section. Cross-references use the form `→ TDD §X.Y`.
>
> **Context-window discipline:** When implementing a task, pin into context only the `[PRD-*]` sections it touches + their TDD counterparts (see TDD `[TDD-PINNED-CONTEXT]`). Do not load the whole PRD.

**Meta:**

| Attribute      | Value                                                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Version        | 4 (née v3, surgical reconciliation for v4-Δ1 B-roll architecture + canonical-15s + product rename)                                               |
| Date           | May 2026                                                                                                                                         |
| Classification | CONFIDENTIAL · GOLDEN RC                                                                                                                         |
| Status         | MVP Locked · Scope-Locked · Aligned to TDD V5 · Aligned to BEF V2                                                                                |
| Invariants     | Credit Lock Before Compute · Atomic Retry Re-Sign · Screen-Context Preservation · Idempotent Monotonic Keys · 2xx-Only Cache · Canonical 15.000s |

---

<HumanContext>

## Vision & Narrative (Non-Normative)

> *"Show the product. Let physics do the selling. Let the director refine the draft. Every credit lock is attached to exactly the compute it authorizes. Every declaration is fresh at the moment of spend. Every awaiting-funds generation returns to the screen it left."*

Adcreo is a solo-bootstrapped, India-first, UPI-native AI video-ad co-pilot for MSMEs and D2C brands. It converts a product URL or photo into a ~15-second SGI-compliant video ad in under 3 minutes, with regional Indic TTS, I2V camera motion, and role-aware atmospheric B-roll framing, for one pre-paid credit. Cross-device responsive web application only.

The three competitive moats are (1) IT Rules 2026 compliance baked in (SGI + C2PA + 5-year audit + <60min takedown), (2) Indic TTS across Hindi/Hinglish/Marathi/Punjabi/Bengali/Tamil/Telugu, and (3) UPI-native INR pricing that eliminates USD-card friction for Indian MSMEs.

</HumanContext>

---

## [PRD-PRICING] · Pricing Plans

| Plan | Price & Validity | Credits | COGS Ceiling | Auth |
|---|---|---|---|---|
| **Starter (Free)** | ₹0 · No expiry | Full Phase 1–3 access (no render) · Max 3 gens | ₹2.00/gen (Phase 1–3 only) | Mandatory Google Login |
| **Essential** | ₹399 · 30-day · 4 credits | 1 credit = 1 HD export (2 formats) | ₹10/gen · CostGuard enforced | Mandatory Google Login |
| **Pro** | ₹1,499 · 45-day · 25 credits | 1 credit = 1 HD export (2 formats) | ₹14/gen · CostGuard enforced | Mandatory Google Login |

**Budget:** Fixed infra ₹15,000/month · ₹1L runway over 6 months (₹90K infra + ₹10K API buffer) · CostGuard enforces ceilings per generation.

**Plan-tier × B-roll template decoupling:** `plan_tier` (per-account) and `structure_template` (per-brand, T1..T5) are orthogonal. Template selection depends on `(framework_angle, category_class, brand_tier, active_season)` only — never on `plan_tier`. A Starter user with a premium brand still gets T2; `plan_tier` only gates rendering capability. → TDD `[TDD-BROLL]-C` + BEF §4.10.

---

## [PRD-VISION] · Mission

Adcreo converts a single product URL or photo into a marketing-ready, SGI-compliant video ad with a **fixed 15-second duration**, with platform-recommended defaults, Indian environments, multi-regional TTS, I2V camera motion, and role-aware atmospheric B-roll framing — delivered in under 3 minutes for one pre-paid credit.

## [PRD-AGENTIC-DRAFT] · The Agentic Draft Model

**Rejects two failure modes:** "Blank Canvas" (traditional SaaS editors → friction) and "Magic Button" (zero-review autonomous gen → burned compute).

**Core mechanics:**
- Multi-agent pre-computation pipeline: system acts as a digital ad agency. User never types a prompt to start — only reviews, refines, approves.
- Defensive economics: bounded pipeline locks generation into predictable COGS boundaries (₹10–₹14 ceiling).
- Cognitive-load floor: Indian SMBs lack prompt-engineering expertise → pre-filled screens drive velocity.
- Financial firewall: the mandatory Phase-3 Strategy Card gate ensures expensive compute is only spent on explicitly approved assets.

**Flow:** 6 screens, strictly linear. `HD-1 → HD-2 → HD-3 → HD-4 → HD-5 → HD-6`. Every user sees every screen, every time.

## [PRD-CONFIDENCE] · Confidence Flagging (Not Routing)

**Engineering invariant:** The system **never dynamically skips screens** based on AI confidence. Dynamic routing breaks state predictability and causes silent failures. Confidence is a **visual signal only**.

| Score | Treatment | Default Primary Action |
|---|---|---|
| **≥ 0.90 (High)** | Ambient green ring on HD-2 | `✓ Continue to Scripts →` |
| **0.85–0.89 (Medium)** | Ambient yellow ring | `✓ Continue` with "double-check" nudge |
| **< 0.85 (Low)** | Ambient red ring | `↻ Re-upload` (primary); `Continue Anyway` (secondary) |

---

## [PRD-PLAYBOOK] · The Dynamic Playbook (12 Frameworks → Execute 3)

Worker-COPY does **not** generate from open-ended prompting. It routes through a **framework-selection system** using a strict 12-value ENUM → TDD `[TDD-ENUMS]`. Routing behaves like a **creative director**, not a text generator.

### Routing Inputs (4 dimensions)

| Dimension | Valid signals |
|---|---|
| **Creative Goal** | stop-scroll · build-trust · explain-feature · create-urgency · defend-price · increase-desire |
| **Evidence Strength** | ingredient/spec/claim · demo/texture/motion · customer-proof · price-value · emotional-only |
| **Visual Fit** | close-up · packaging · usage-in-action · premium-look · text-heavy · before-after |
| **Audience State** | cold · comparison-shopper · warm-retargeting · repeat-buyer · festival-buyer |

### Routing Rule

Worker-COPY MUST select **3 distinct frameworks**. Default trio covers one **logic-led**, one **emotion-led**, one **conversion-led**. On weak evidence → `SAFE_TRIO = [pas_micro, usage_ritual, social_proof]`.

### The 12 Framework Families (ENUM values · angle · best-fit)

| # | ENUM value | Family | Angle | Best when | Example hook |
|---|---|---|---|---|---|
| 1 | `pas_micro` | Problem/Efficacy | logic | Daily-frustration product | "Hair fall every morning? Here's a simpler fix." |
| 2 | `clinical_flex` | Problem/Efficacy | logic | Strong spec/ingredient proof | "10% Niacinamide. Built for visible skin improvement." |
| 3 | `myth_buster` | Problem/Efficacy | logic | Crowded skeptical category | "Expensive does not always mean better." |
| 4 | `asmr_trigger` | Sensory/Desire | emotion | Visual-rich sensory product | "Ekdum crispy. Har bite mein satisfaction." |
| 5 | `usage_ritual` | Sensory/Desire | emotion | Routine-driven product | "Your perfect morning ritual, now made easier." |
| 6 | `hyper_local_comfort` | Sensory/Desire | emotion | Cultural-closeness advantage | "Familiar taste. Local comfort. Everyday joy." |
| 7 | `spec_drop_flex` | Status/Value | logic | One premium feature | "Premium matte finish. Built for all-day use." |
| 8 | `premium_upgrade` | Status/Value | emotion | Aspiration-led product | "Upgrade the way you carry your everyday essentials." |
| 9 | `roi_durability_flex` | Status/Value | logic | High-consideration value | "Built to last. Better value with every use." |
| 10 | `festival_occasion_hook` | Urgency/Conversion | conversion | Calendar-tied campaign | "Ready for the season. Perfect for the moment." |
| 11 | `scarcity_drop` | Urgency/Conversion | conversion | Real supply/time scarcity | "Limited stock. Once it's gone, it's gone." |
| 12 | `social_proof` | Urgency/Conversion | conversion | Trust/popularity-led buy | "Trusted by thousands of customers." |

### Selection Safety Rules

- Weak proof → avoid claim-led frameworks (`clinical_flex`, `spec_drop_flex`).
- Strong factual proof → prefer claim-led.
- Motion/texture-rich visuals → prefer sensory (`asmr_trigger`, `usage_ritual`).
- Premium/high-consideration → prefer `premium_upgrade` / `roi_durability_flex`.
- Campaign moment (festival/payday) → prefer `festival_occasion_hook`.
- If framework doesn't match available evidence → fallback to safer option.

### Router Output Contract

```json
{
  "selected": ["pas_micro", "usage_ritual", "social_proof"],
  "rationale": { "pas_micro": "...", "usage_ritual": "...", "social_proof": "..." },
  "evidence_assessment": { "strength": "moderate", "signal": "..." },
  "fallback_triggered": false
}
```

Cardinality + distinctness enforced by Postgres CHECK constraint on `generations.routed_frameworks ad_framework[]` → TDD `[TDD-ENUMS]`. Worker-CRITIC then scores and ranks.

## [PRD-COPILOT] · Co-Pilot Refinement (Phase 2 Only)

Bounded refinement layer above framework engine. **NOT open-ended chat.**

**Interaction model:** Pre-defined refinement actions: `strengthen hook` · `add urgency` · `make it Hinglish` · `make it emotional` · `simplify language` · `add offer/CTA`. Constrained free-text (≤500 chars, ≤20 words) classified into structured refinement intents. Free-form prompting banned.

**Bounds:**
- Max **3 refinement turns** per generation (hard FSM + DB CHECK).
- ~₹0.08/turn; CostGuard tracks all usage.
- ComplianceGate validates every input; OutputGuard validates every output.
- 5-stage middleware chain enforced → TDD `[TDD-CHAT-CHAIN]`.
- Each turn produces a new script version; changes highlighted.

**System Boundary — refinement CANNOT:**
- Change product facts · Introduce unsupported claims · Bypass framework constraints · Alter strategy outside Phase 2 · Pivot framework angle.

User is always refining an existing AI draft — never starting from scratch.

---

## [PRD-PIPELINE] · The 4-Phase Pipeline

```
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 1 · INGESTION                                                    │
│ InputScrubber (sync) → EXTRACT (Firecrawl API 15s, Markdown output)    │
│   → BiRefNet (local, Apache 2.0) → Gemini Vision (GreenZone class.)    │
│   → product_brief                                                      │
│ 10MB upload cap. Green Zone gate.                                      │
│ → HD-2 shown with isolation DONE. Confidence flag attached.            │
├────────────────────────────────────────────────────────────────────────┤
│ PHASE 2 · STRATEGY (Dynamic Playbook — 12 Frameworks, Execute 3)       │
│ COPY.framework_router() → 3 distinct frameworks (default trio or       │
│   SAFE_TRIO fallback) → COPY.generate_per_framework() (asyncio.gather  │
│   parallel) → 3 framework-tagged scripts → CRITIC ranks → SAFETY batch │
│   → 3 ranked drafts.                                                    │
│ → HD-3: 3 scripts pre-drafted, framework-labeled, top pre-selected.    │
│ →→ Co-Pilot Refinement (≤3 turns · ~₹0.08/turn) — 5-stage chain:       │
│     ComplianceGate → CostGuard.pre_check → LLM(script-refine) →        │
│     CostGuard.record → OutputGuard → atomic state-guarded UPDATE.      │
│ → Style pre-filled from Style Memory or heuristics.                    │
├────────────────────────────────────────────────────────────────────────┤
│ PHASE 3 · INTENT GATE (MANDATORY · HD-4)                               │
│ STRATEGIST compiles Strategy Card (ZERO external API, CI-enforced).    │
│ v4-Δ1: STRATEGIST resolves active_season (seasons lookup) + brand_tier │
│   (user_style_profiles) + structure_template (T1..T5 via               │
│   TEMPLATE_BY_CONTEXT, with T4 festive override) BEFORE calling the    │
│   deterministic role-first BRollPlanner. Plan + template + season +    │
│   broll_clip_usage rows persisted atomically in a single transaction.  │
│ SYSTEM HALTS. User reviews. 4× [Edit] buttons route back (NULL         │
│   downstream incl. b_roll_plan, structure_template, active_season,     │
│   b_roll_performance_signal). Primary CTA = "Confirm & Use 1 Credit →  │
│   Render":                                                              │
│   - Starter → 403 ECM-006.                                             │
│   - Insufficient funds → awaiting_funds (pre_topup_status=             │
│       'strategy_preview') → Top-Up Drawer overlays HD-4.               │
│   - Funds OK → Lua lock → funds_locked → Phase 4 dispatched.           │
├────────────────────────────────────────────────────────────────────────┤
│ PHASE 4 · PRODUCTION (HD-5 Render → HD-6 Preview/Export)               │
│ phase4_coordinator: asyncio.gather(TTS, I2V×2) → REFLECT (SSIM) →      │
│   COMPOSE (FFmpeg canonical 15s, template-branched per structure_      │
│   template T1..T5, no -shortest, pad/trim both streams)                │
│   → preview_ready. COORDINATOR STOPS HERE — does NOT enqueue export.   │
│ HD-6 state-aware: Declaration signed (IP/UA/SHA256 captured) →         │
│   /declaration transitions preview_ready → export_queued AND enqueues  │
│   worker_export independently on DB1 phase4_workers.                    │
│ Worker-EXPORT standalone: ffmpeg scale → 2 formats → c2patool sign     │
│   (returncode checked, local verification only) → wallet consume →     │
│   export_ready.                                                         │
│ Failures (DLQ dual-branch by job.function_name):                       │
│   phase4_coordinator (or child) → failed_render → refund → HD-5 inline │
│     → [↻ Try Again] → strategy_preview → HD-4 (full re-lock required). │
│   worker_export → failed_export → refund → HD-6 inline recovery:       │
│     - Fresh declaration (≤24h) → [↻ Retry Export · 1 Credit] →          │
│       /retry-export 9-step chain, EXPORT-only re-run.                   │
│     - Stale declaration (>24h) → 428 ECM-020 → inline re-sign on HD-6  │
│       → atomic audit_log INSERT + lock + dispatch in single call.      │
│   HD-6 retry lock-fail → awaiting_funds(pre='failed_export') → Top-Up  │
│     Drawer overlays HD-6; webhook restores to HD-6 (not HD-4).         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## [PRD-PROBLEM] · The Problem

India: 63M MSMEs, 50M+ online sellers. <1% have video ads. Barriers: cost (₹50K+), time (2–8 weeks), expertise, friction (blank text boxes). Compliance gap: IT Rules 2026 mandates SGI labeling, C2PA, 5-year audit, <3h takedown — no competitor is compliant.

---

## [PRD-NON-NEGOTIABLES] · Product Non-Negotiables

**Financial & Economic Boundaries**
- **Credit Lock Before Compute:** Lua lock fires in `/approve-strategy` BEFORE Phase-4 dispatch. Every lock is scoped to the exact compute it authorizes — full-render locks originate at HD-4; export-only retry locks originate at HD-6.
- **Zero-Risk Generation:** Users never charged for system failures. Any Phase-4 failure (render or export) triggers a credit refund via DLQ.
- **No Double-Compute:** Once Phase-4 render assets persist to R2, no recovery path re-runs render. Retries target only the failed compute.
- **Screen-Context Preservation on Top-Up:** A user entering `awaiting_funds` from HD-6 retry context MUST return to HD-6 on payment capture — never silently relocated to HD-4. Durable invariant via `generations.pre_topup_status` column.
- **Algorithmic Model Selection:** User cannot select underlying AI models. System autonomously routes via ModelGateway circuit-breaker.
- **Zero Marginal Cost B-Roll Selection:** The B-roll planner makes zero external API calls, runs no LLM, performs no vector search; selection is a single deterministic SQL read with total-ordered tiebreaks → TDD `[TDD-BROLL]-G/J` + BEF F9.

**Legal & Compliance Boundaries**
- **Statutory Compliance:** 100% IT Rules 2026 + DPDP Act 2023. Mandates visible SGI labeling + cryptographic C2PA signing on all exports.
- **Declaration Provenance & Atomicity:** Every export declaration captures IP, User-Agent, server timestamp, SHA256 hash, persisted to partitioned immutable `audit_log`. Declarations >24h require re-capture BEFORE retry export; retry is atomic — new `audit_log` row + credit lock + state transition commit together or not at all.
- **Data Minimization & Purging:** 7 days unpaid · 30 days paid source assets · exactly 5 years finalized SGI exports.
- **Automated Takedown SLA:** Complete, automated asset purging (DB + R2) within 60 minutes of moderation trigger.
- **B-Roll Safety Purity:** Every clip in `broll_clips` has `excludes_faces = excludes_hands = excludes_locations = TRUE` (DB CHECK `chk_broll_safety`). Every `role='cta_bg'` clip has `negative_space_score >= 7` for text-card legibility (DB CHECK `chk_cta_negative_space`) → BEF L8.

**UX & Product Identity Boundaries**
- **Product-Visual First:** User's actual product is the hero asset in every ad. Generic stock product footage, avatar-led ads, human spokespersons are prohibited. Atmospheric B-roll may be used as secondary context only.
- **Role-First B-Roll Architecture:** B-roll clips are tagged at curation time by **role** (`hook` / `context` / `cta_bg`), `mood_energy` (`calm` / `active` / `intense`), `mood_temperature` (`warm` / `cool` / `neutral`), `seasonality_tags` (e.g. `{diwali, wedding}`), and `brand_tier_fit` (`{mass, premium, luxury}`). A clip's role is fixed at curation and never overridden by selection logic. Runtime selection is a deterministic SQL read in Worker-STRATEGIST — no LLM, no embeddings, no vector search, no external API. Recognizable locations are forbidden by the `chk_broll_safety` constraint. Plan output is bounded to a `{template, hook, context, cta}` JSONB object with at most 3 clips total (often fewer; T2/T5 ship hook only). → TDD `[TDD-BROLL]-A/D/E/G/K`.
- **Green Zone Restriction:** System processes only products in 5 approved `GreenZone` categories (I2V physics reliability).
- **Zero Free-Text Primary Inputs:** Open-ended prompting banned. User input restricted to UI selections + bounded Co-Pilot Chat.
- **Mandatory Intent Gate:** Phase-3 Strategy Card (HD-4) is a hard stop. No auto-approval of render without explicit human-in-the-loop consent.
- **Co-Pilot Refinement Constraint:** Structured refinement of AI drafts in Phase 2 only. No free-form prompting, no framework bypass.

### Peripheral Routes

The grievance form is a peripheral route:

- Path: `/grievance`
- Outside FSM (HD-1 → HD-6)
- No state transitions
- Accessible via footer only

**System Predictability Boundaries**
- **Strictly Linear Flow:** Every screen HD-1..HD-6 shown. No dynamic screen-skipping. Contextual overlays (Top-Up Drawer, Plan Modal) are not screens — they preserve the underlying screen state.

### FSM Transition Source of Truth

All state transitions must be defined in:

`/state_transitions.yaml`

- Backend must strictly enforce this file
- CI must validate all transitions against it
- No transitions are allowed outside this definition

## [PRD-GREENZONE] · Green Zone & Red Zone

```typescript
enum GreenZone { d2c_beauty, packaged_food, hard_accessories, electronics, home_kitchen }
enum RedZone   { apparel, footwear, fabric_home, organic_produce }
```

Backed by Postgres ENUM `green_zone_category` → TDD `[TDD-ENUMS]`.

---

## [PRD-TECH-CONSTRAINTS] · Technical Constraints

- PEP 8 namespace isolation is mandatory; no folder/file shadowing of stdlib modules or sibling packages.
- Backend canonical paths are `app/infra_gateway.py`, `app/infra_redis.py`, and `app/schemas/`.
- Gate 1 is considered Verified only when:
  - `/api/generate` returns ECM-007 middleware response
  - Redis is active via `app.state.redis_mgr`
  - Postgres connectivity is confirmed

## [PRD-COMPETITION] · Competitive Intelligence

### Direct Competitors

| Competitor | Pricing | Localization | I2V Native | IT Rules 2026 | Verdict |
|---|---|---|---|---|---|
| Creatify | $49/mo USD | ❌ EN only | ✅ URL→video | ❌ Fails SGI & Audit | Black-box; no draft review; no chat |
| Oxolo | $99/mo USD | ❌ EN only | ✅ Product hero | ❌ Fails SGI & Audit | Cost-prohibitive for Indian MSMEs |
| Typeframes | $29/mo USD | ❌ EN only | ❌ Template | ❌ Fails SGI & Audit | Non-agentic; manual editor |
| Vidyo.ai | $30/mo USD | ⚠️ India HQ | ❌ Repurposing | ❌ Fails SGI & Audit | Irrelevant for product ads |

### India-Adjacent

| Competitor | Pricing | I2V | IT Rules 2026 | Verdict |
|---|---|---|---|---|
| Rocketium | Custom B2B | ❌ Template | ❌ | Enterprise friction |
| InVideo | ₹750/mo | ❌ Stock | ❌ | Manual timeline |
| Predis.ai | $29/mo USD | ⚠️ Template | ❌ | Static layouts |

### Global AI Models

| Competitor | Pricing | Core Tech | IT Rules 2026 | Verdict |
|---|---|---|---|---|
| HeyGen | $89/mo | ❌ Avatar | ❌ | Not product ads |
| Runway | $76/mo | ✅ Raw I2V | ❌ | Blank-canvas anxiety |
| Pika | $28/mo | ✅ Raw I2V | ❌ | Missing pipeline |

### Uncontested Quadrant

```
                     HIGH India Localization
             ┌───────────────┼───────────────┐
             │ InVideo       │ ★ Adcreo      │
             │ Predis        │ (I2V+India+   │
             │ (Templates)   │  Compliance+  │
             │               │  Co-Pilot)    │
LOW I2V ─────┼───────────────┼───────────────┼──── HIGH I2V
             │ Static Ads    │ Creatify      │
             │ Canva         │ Oxolo, Runway │
             │ (No video)    │ (USD, no chat)│
             └───────────────┼───────────────┘
                     LOW India Localization
```

## [PRD-MOATS] · Moats → Middleware Mapping

| Strategic Moat | Middleware Enforcement → TDD anchor |
|---|---|
| **Regulatory Defensibility (IT Rules 2026)** | L3 ComplianceGate + L6 Worker-EXPORT (SGI watermark + `c2patool` returncode) + Takedown Pipeline <60min → TDD `[TDD-WORKERS]-I` + `[TDD-TAKEDOWN]-A/B/C/D` |
| **Inference Economics** | L5 CostGuard evaluates ceiling before dispatch. COGS recorded instantly on LLM return. Hard ceilings ₹10/₹14. Export-retry preserves ~₹10 of Phase-4 compute per retry → TDD `[TDD-GATEWAY]-B` (CostGuard · Per-Gen COGS Ledger) |
| **Hyper-Localization (Indic Native)** | L6 Worker-TTS routes dynamically to Sarvam AI for regional languages. PromptOps catalog injects Indian cultural nuances. Festive template T4 binds to `seasons` lookup for Diwali / Holi / wedding / monsoon / new-year / raksha-bandhan windows → TDD `[TDD-GATEWAY]` + `[TDD-PROMPTS]` + `[TDD-BROLL]-C` |
| **UPI-Native Financials** | L2 API Gateway (Razorpay). Redis Lua atomic locks/consumes/refunds. Postgres ledger. `pre_topup_status` snapshot ensures origin-screen restore → TDD `[TDD-REDIS]-B/C/D` (wallet_lock/consume/refund Lua) + `[TDD-API]-H` (Razorpay webhook · Origin-Preserving Restoration) |
| **High Switching Cost (Style Memory)** | L7 pgvector `user_style_profiles`. Learns brand aesthetic over exports; surfaces `brand_tier` and `brand_color_primary` → TDD `[TDD-FLYWHEEL]-A` (Style Memory · Opt-In pgvector) |
| **Agentic Draft Trust Loop** | Every screen pre-filled. Confidence flags guide hierarchy. Credit lock strictly at Strategy Card gate → TDD `[TDD-FSM]` |

### C2PA Verification Constraint (MVP)

All C2PA verification must be performed locally using `c2patool --verify`.

External verification services (e.g., Adobe VerifyContentCredentials) are strictly forbidden and must not be used in any part of the system.

---

<HumanContext>

## [PRD-PERSONAS] · Personas (Non-Normative)

**SOM Year 1:** 500–1,000 paying users · MRR ₹2.5L.

### Priya — The Regional Reseller

| Attribute | Detail |
|---|---|
| Profile | 28 · Surat/Ludhiana · Meesho reseller · ₹2–5K ad budget |
| UX Constraint | **Mobile-Web (<768px).** HD-3 Chat behind Shadcn `Sheet` FAB; HD-3 tabs (Script/Style) for progressive disclosure |
| Language | Regional TTS (Hindi, Hinglish, Marathi, Punjabi, Bengali, Tamil, Telugu) |
| Plan | Essential ₹399 / 4 credits |

Pain → System Solution: zero design skills → AI drafts everything · expensive agencies → ₹100/video · flaky network → `localStorage` Idempotency-Key + server `actlock` fence prevents double-spend · DLQ friendly error + credit refund · payment-then-timeout → `pre_topup_status` snapshot guarantees origin-screen return.

### Arjun — The D2C Brand Owner

| Attribute | Detail |
|---|---|
| Profile | 34 · Delhi · Shopify D2C · ₹10K ad budget |
| UX Constraint | **Desktop-first.** Power user. Uses all 3 chat turns; appreciates 4-zone HD-3 workspace |
| Plan | Pro ₹1,499 / 25 credits |

Pain → System Solution: slow turnaround → pre-filled screens · no consistency → Style Memory · A/B test hooks → Co-Pilot Chat · multi-gen → per-gen wallet locks with partial UNIQUE INDEX · HD-6 retry edge cases → 428 ECM-020 keeps user on HD-6, never kicks back to HD-4.

### Sneha — The Growth Marketer

| Attribute | Detail |
|---|---|
| Profile | 26 · Mumbai · Growth marketer at D2C · ₹2–5L/mo budget |
| UX Constraint | Cross-device. Multi-tab workflow |
| Plan | Pro ₹1,499 / 25 credits |

Pain → System Solution: creative fatigue → Chat · regulatory anxiety → Compliance trust row on HD-4 · multi-tab safety → idempotency keys versioned by `export_retry_count` prevent cross-tab cache collisions.

</HumanContext>

---

## [PRD-POSITIONING] · Positioning Statement

**For** Indian e-commerce sellers and D2C brands **who** need video ads but lack budget, time, or expertise, **Adcreo** is a cross-device AI video co-pilot **that** converts product URLs into marketing-ready ~15-second videos in under 3 minutes with transparent pre-filled drafts and Co-Pilot Chat for refinement. **Unlike** template tools (InVideo), avatar platforms (HeyGen), black-box generators (Creatify), or agencies (₹50K+), **we** use your actual product with I2V motion physics, multi-regional Indic voiceovers, role-aware atmospheric B-roll framing, agentic drafts with confidence transparency, and strict IT Rules 2026 compliance.

## [PRD-DIFFS] · Key Differentiators → Engineering Constraints

| Differentiator | Engineering Constraint |
|---|---|
| **Actual Product Hero + Role-First B-roll** | Ad centers user's actual product. Atmospheric B-roll is selected by **role** (`hook` / `context` / `cta_bg`) via a deterministic SQL planner across 5 structural templates (T1..T5); no generic stock product, no avatar-led creative. See `[PRD-FEATURES-PRODUCTION]` F-405. |
| **Zero Prompting for Inputs** | Primary inputs = URL + enum selections only. |
| **Co-Pilot Chat for Refinement** | 3 turns/gen · ~₹0.08/turn · ComplianceGate + OutputGuard · CostGuard tracked · Phase 2 only. |
| **₹ UPI-First** | Razorpay/UPI only. `payment_status` FSM on topup transactions. `pre_topup_status` restores exact pre-lock-fail screen on webhook capture. |
| **IT Rules 2026** | ComplianceGate + Worker-EXPORT enforce SGI + `c2patool` (returncode checked; local verification only). Declaration provenance with 24h freshness + atomic re-sign via 428 ECM-020. → TDD `[TDD-WORKERS]-I` + `[TDD-VIDEO]-C` (C2PA) + `[TDD-API]-G` Step 4 (declaration freshness) |
| **Regional TTS** | `SupportedTTSLanguages` enum routing to Sarvam/ElevenLabs. |
| **3-Minute SLA** | Pre-filled drafts + `phase4_coordinator` fan-in. |
| **Agentic Drafts** | Every screen pre-filled. Confidence flags, not screen-skipping. |
| **Style Memory** | `user_style_profiles` (pgvector). Resettable. Surfaces `brand_tier` and `brand_color_primary`. |
| **Credit-Lock-Before-Compute** | Lua lock in `/approve-strategy` BEFORE Phase 4. HD-6 retry lock authorizes Worker-EXPORT only — preserves ~₹10 of Phase-4 assets. |
| **Flaky-Network Safe** | `localStorage` Idempotency-Keys versioned per-retry (`{gen_id}:retry-export:{export_retry_count}`) + `actlock` fence + 2xx-only cache. DLQ refund on ALL Phase-4 failures. |

## [PRD-CATEGORY] · Product Category

**Verticalized AI Co-Pilot.** Strictly bounded, workflow-driven generation tool — NOT an open-ended text-to-video prompter. Engineering treats this as a structured B2B pipeline where AI generates a pre-filled draft and user refines via bounded chat.

---

## [PRD-FSM] · The 22-State Machine ENUM

The ENUM is the single source of truth. UI is a reactive projection. Postgres `generations.status` column stores this ENUM; all API responses, SSE events, and route decisions derive from it. A **second** column, `generations.pre_topup_status` (nullable), captures origin-screen context while `status='awaiting_funds'`.

```sql
CREATE TYPE job_status AS ENUM (
    -- Phase 1: Ingestion
    'queued',               -- HD-1 | POST /generate accepted
    'extracting',           -- HD-1 | Worker-EXTRACT running
    'brief_ready',          -- HD-2 | Phase 1 complete

    -- Phase 2: Strategy
    'scripting',            -- HD-3 | Worker-COPY drafting
    'critiquing',           -- HD-3 | Worker-CRITIC scoring
    'safety_checking',      -- HD-3 | Worker-SAFETY batch
    'scripts_ready',        -- HD-3 | Phase 2 complete
    'regenerating',         -- HD-3 | chip-change re-run

    -- Phase 3: Intent Gate
    'strategy_preview',     -- HD-4 | Worker-STRATEGIST complete
    'awaiting_funds',       -- HD-4 OR HD-6 | Lua lock failed → Top-Up Drawer overlay
                            --   (origin disambiguated by pre_topup_status)
    'funds_locked',         -- HD-5 | Lua lock succeeded (<1s transient)

    -- Phase 4: Production
    'rendering',            -- HD-5 | TTS + I2V (asyncio.gather)
    'reflecting',           -- HD-5 | Worker-REFLECT SSIM
    'composing',            -- HD-5 | Worker-COMPOSE FFmpeg (template-branched)
    'preview_ready',        -- HD-6 | Preview live, declarations unsigned
    'export_queued',        -- HD-6 | Declaration signed, Worker-EXPORT running
    'export_ready',         -- HD-6 | C2PA signed, downloads active

    -- Terminal Failures
    'failed_category',      -- HD-1 re-entry
    'failed_compliance',    -- HD-1 re-entry
    'failed_safety',        -- HD-3 inline
    'failed_render',        -- HD-5 inline recovery → HD-4 re-lock
    'failed_export'         -- HD-6 inline recovery → /retry-export
);
```

### FSM Transition Contract

All valid state transitions are defined in:

`/state_transitions.yaml`

- This file is the single source of truth for allowed transitions
- Used by CI (`validate_state_machine.py`)
- Backend must reject any undefined transition

Design Separation:
- PRD → defines states (ENUM)
- YAML → defines transitions
- CI → enforces correctness

## [PRD-PRETOPUP] · The `pre_topup_status` Column

```sql
ALTER TABLE generations ADD COLUMN pre_topup_status job_status NULL;

-- Invariant enforced by CHECK constraint + trigger:
--   status='awaiting_funds' → pre_topup_status IN ('strategy_preview','failed_export')
--   status≠'awaiting_funds' → pre_topup_status IS NULL
-- Only L2 API Gateway may write to this column. Workers DENIED.
```

**Why it exists:** Before v28, the Razorpay webhook hardcoded a state restore to `strategy_preview`. This silently kicked HD-6 retry users (who had entered `awaiting_funds` from `failed_export → /retry-export → Lua lock fail`) back to HD-4, destroying their preview context. The column snapshots the origin state at entry to `awaiting_funds`; webhook restores atomically on capture.

**Critical projection rules:**

1. Phase-4 resident states (`preview_ready`, `export_queued`, `export_ready`) all resolve to HD-6. HD-6 component progressively enables UI elements based on `status`.
2. `failed_export` resides on HD-6. Recovery never routes user back to HD-4. Dedicated `/retry-export` preserves Phase-4 assets, re-runs Worker-EXPORT only.
3. `awaiting_funds` resolves to HD-4 OR HD-6 via `pre_topup_status`: `'strategy_preview'` → HD-4; `'failed_export'` → HD-6.
4. `pre_topup_status` is semantically paired with `status='awaiting_funds'`. No meaning elsewhere; enforced NULL outside the `awaiting_funds` window.

## [PRD-FLOW] · The Linear Flow — 6 Screens

| # | Screen | Resident State(s) | Transient States | Phase | Primary Action | API |
|---|---|---|---|---|---|---|
| **HD-1** | Product Ingestion | `queued` | `extracting` | 1 | Paste URL · Upload image | `POST /generate` |
| **HD-2** | Isolation Review | `brief_ready` | — | 1 | Approve isolation | `POST /gen/{id}/advance` |
| **HD-3** | Creative Workspace | `scripts_ready` | `scripting`, `critiquing`, `safety_checking`, `regenerating` | 2 | Accept script · Refine via Chat (≤3 turns) | `POST /gen/{id}/chat`, `/regenerate`, `/advance` |
| **HD-4** | Your Ad Plan · Credit Gate | `strategy_preview` | `awaiting_funds` *(pre='strategy_preview')* (overlay) | 3 | Confirm & Use 1 Credit | `POST /gen/{id}/approve-strategy` · `POST /wallet/topup` |
| **HD-5** | Render Progress | `rendering` | `funds_locked`, `reflecting`, `composing` | 4 | Passive watch | SSE only |
| **HD-6** | Your Ad · Preview + Download | `preview_ready`, `export_queued`, `export_ready`, `failed_export`, `awaiting_funds` *(pre='failed_export')* (overlay) | — | 4 | Sign 3 declarations → Download HD; Retry Export on failure | `POST /gen/{id}/declaration` · `POST /gen/{id}/retry-export` · `GET /gen/{id}/download/{format}` |

### [PRD-FLOW-INVARIANTS] · Flow Invariants (Non-Negotiable)

1. **Linearity:** Every screen shown. Confidence flagging adapts UI, never skips.
2. **Credit Lock Before Compute:** Every Lua lock is scoped to the compute it authorizes. HD-4 lock authorizes full Phase-4 render. HD-6 retry lock authorizes Worker-EXPORT only. **No lock ever re-authorizes already-performed compute.**
3. **State is DB-backed:** `generations.status` is source of truth. Frontend hydrates via `GET /gen/{id}` on mount; SSE streams thereafter.
4. **Idempotency everywhere:** Every mutating endpoint uses `@idempotent(ttl=300, action_key, cache_only_2xx=True)` + client `localStorage` key + server `actlock` fence. **Recoverable 4xx (400, 402, 409, 428) NEVER cached** — client clears localStorage on receipt and re-issues fresh key.
5. **Audit trail immutable:** Every state transition writes to partitioned `audit_log`. Re-signing declarations INSERTs a new row; prior rows preserved forever.
6. **Ledger semantic cleanliness:** `payment_status` applies ONLY to `type='topup'` (Razorpay FSM); `status` applies ONLY to `type IN ('lock','consume','refund')`.
7. **Screen-Context Preservation:** `pre_topup_status` snapshots origin screen. Razorpay webhook restores it on capture.
8. **Retry-Key Monotonicity:** `/retry-export` idempotency key embeds `export_retry_count` → prevents cache collision across retries.
9. **B-Roll Plan Atomic Persistence:** Worker-STRATEGIST's UPDATE of `generations.b_roll_plan + structure_template + active_season` AND the INSERTs into `broll_clip_usage` for every non-null clip in the plan happen inside a single `db.transaction()`. A partial write would corrupt rotation determinism on the next generation for this user. → TDD `[TDD-WORKERS]-G` step 5.

---

## [PRD-HD1] · HD-1 — Product Ingestion

**State:** `queued` (entry) · `extracting` (transient)

```
┌─────────────────────────────────────────────────────────────┐
│   🔗  Paste your product URL                                 │
│       ┌──────────────────────────────────────────┐           │
│       │ https://www.meesho.com/…                  │ [ → ]    │
│       └──────────────────────────────────────────┘           │
│                         — or —                               │
│   📷  Upload product image (JPEG / PNG · max 10MB)           │
│       [ Choose File ]                                        │
│   Supported: Beauty · Food · Accessories · Electronics ·     │
│              Home & Kitchen                                  │
│   ⏱️  Takes about 10 seconds to analyze your product         │
└─────────────────────────────────────────────────────────────┘
```

**Rationale:** URL-first matches Indian seller muscle memory (Meesho/Flipkart links). Image upload is fallback for Firecrawl-blocked domains. GreenZone categories disclosed upfront → users self-filter BEFORE Phase-1 compute burn.

**Behind-the-Scenes:**

| Trigger | API Call | Backend Chain | State Transition | SSE Event |
|---|---|---|---|---|
| URL submit | `POST /generate { url }` | L2 validate → InputScrubber → INSERT `generations` → ARQ enqueue Worker-EXTRACT | → `queued` | — |
| Image upload | `POST /generate` (multipart) | Same, image → R2 `/uploads/{user_id}/{gen_id}.png` | → `queued` | — |
| Worker-EXTRACT starts | — | Firecrawl API (15s timeout) → BiRefNet (local, Apache 2.0) → Gemini Vision | `queued → extracting` | `status_update` |
| Phase 1 complete | — | Writes `isolated_png_url`, `confidence_score`, `category` | `extracting → brief_ready` | `phase_complete` → HD-2 |

**Failure paths (all stay on HD-1):**

| Condition | ENUM | Code | Recovery |
|---|---|---|---|
| Non-GreenZone category | `failed_category` | ECM-001 | `[Start Over]` → fresh `gen_id` |
| Scraped image > 15MB | `failed_category` | ECM-001 | `[Start Over]` |
| InputScrubber trip | `failed_compliance` | ECM-002 | `[Start Over]` |
| Firecrawl > 15s | — | ECM-015 | Upload tab auto-selected |
| Upload > 10MB | — | ECM-014 | 413 inline |

**Mobile:** Single-column layout; upload uses `<input type="file" accept="image/*" capture>`.

---

## [PRD-HD2] · HD-2 — Isolation Review

**State:** `brief_ready`

```
┌─────────────────────────────────────────────────────────────┐
│ [ ambient green border — high confidence ]                   │
│  Looks good — we isolated your product.                      │
│       ┌──────────────────────────────┐                       │
│       │      [ isolated PNG on       │                       │
│       │       checkerboard ]         │                       │
│       └──────────────────────────────┘                       │
│       [ Source ] ⇄ [ Isolated ]                              │
│  [ ↻ Re-upload ]         [ ✓ Continue to Scripts → ]         │
└─────────────────────────────────────────────────────────────┘
```

**Ambient confidence treatment:**

| Confidence | Border | Primary | Secondary | Headline |
|---|---|---|---|---|
| ≥ 0.90 | Soft green | `✓ Continue to Scripts →` | `↻ Re-upload` | "Looks good — we isolated your product." |
| 0.85–0.89 | Soft yellow | `✓ Continue to Scripts →` | `↻ Re-upload` | "Edges look thin — double-check before continuing." |
| < 0.85 | Soft red | `↻ Re-upload` | `Continue Anyway` | "We had trouble isolating the product. Try re-uploading with a plain background." |

**Rationale:** First trust moment; Phase-1 COGS only ₹0.15 — cheapest/highest-ROI validation. Confidence Flagging (not Routing) preserved. Before/after toggle = proof-of-competence at a glance.

**Behind-the-Scenes:**

| Trigger | API | Backend | State | SSE |
|---|---|---|---|---|
| Mount | `GET /gen/{id}` | Hydrate; R2 presigned URL for `isolated_png` (10-min TTL) | — | SSE attached |
| `✓ Continue` | `POST /gen/{id}/advance` | L2 validate → ARQ enqueue `phase2_chain` → status = `scripting` | `brief_ready → scripting` | `phase_complete` → HD-3 |
| `↻ Re-upload` | — | Client routes to HD-1 with fresh `gen_id` | — | — |

---

## [PRD-HD3] · HD-3 — Creative Workspace

**State:** `scripts_ready` (resident) · `scripting`, `critiquing`, `safety_checking`, `regenerating` (transient)

**Desktop layout (≥768px) — 4-zone workspace:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  [ context chip bar: Women · Premium · Energy · Hindi · 15s ] [ ✎ ]     │
├─────────────────────────────────────────┬───────────────────────────────┤
│  SCRIPT ZONE (3 tiles)                  │  STYLE ZONE                   │
│  ★ PAS-Micro · 82                       │  Motion archetype: Orbit ★    │
│  "Radiance, redefined…" [SELECTED]      │  Environment: Golden Hour ★   │
│  Clinical · 78                          │  Voice: Hindi · Sarvam        │
│  ASMR · 75                              │  Duration: 15s (fixed)        │
├─────────────────────────────────────────┼───────────────────────────────┤
│  CHAT ZONE · Co-Pilot (2 of 3 turns)    │  DIRECTOR TIPS                │
│  Quick: [Punchier] [Hinglish] [Diwali]  │  ✓ Strong ingredient proof    │
│  [ Type refinement (≤500 chars) ][ → ]  │  ⚠ Consider adding urgency    │
├──────────────────────────────────────────┴──────────────────────────────┤
│                                        [ Continue to Strategy → ]        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Mobile layout (<768px) — Progressive Disclosure:**

```
┌────────────────────────────────────────┐
│ [Women] [Premium] [Energy] [Hindi] [15s]│ ← Sticky horizontal-scroll chips
├────────────────────────────────────────┤
│ ┌─────────────┬─────────────┐          │ ← Shadcn Tabs
│ │   Script    │    Style    │          │
│ └─────────────┴─────────────┘          │
├────────────────────────────────────────┤
│  ★ PAS-Micro · 82        [Selected]    │
│    "Radiance, redefined..."            │
│  Clinical · 78           [Select]      │
│  ASMR · 75               [Select]      │
│                                  ╭─╮   │
│                                  │💬2│   │ ← Chat FAB (badge = turns left)
│                                  ╰─╯   │
├────────────────────────────────────────┤
│ [ Continue to Strategy → ]             │ ← Sticky bottom CTA
└────────────────────────────────────────┘
```

**Chat FAB bottom-sheet (mobile):**

```
┌────────────────────────────────────────┐
│ Co-Pilot Chat              (2 of 3)    │
│ Quick refinements:                     │
│ [ Punchier ] [ Hinglish ] [ Diwali ]   │
│ ┌──────────────────────────┐  ┌───┐    │
│ │ Type a tweak...           │  │ → │    │
│ └──────────────────────────┘  └───┘    │
│ [ ↓ Close ]                            │
└────────────────────────────────────────┘
```

**Mobile IA rules (implementation contract):**
- Sticky top chips horizontally scrollable; tap opens chip-detail modal.
- Shadcn `Tabs` (Script | Style): default Script. Tab switch client-only, no API call.
- Chat as FAB + Shadcn `Sheet` bottom-sheet: ~70% viewport; dismisses via swipe-down/backdrop/close. Counter badge = turns remaining.
- Sticky bottom CTA always one tap from progressing.
- **Duration chip is a non-editable display in MVP** (canonical 15s per `[TDD-VIDEO]-A`). Variable duration (5s / 10s) deferred post-MVP.

**Rationale:** Desktop 4-zone layout = all creative levers in view for power users. Mobile progressive disclosure solves scroll-hell: Script primary, Style secondary, Chat opt-in. Pre-selected top script matches 85% usage pattern.

**Behind-the-Scenes:**

| Trigger | API | Backend | State | SSE |
|---|---|---|---|---|
| Chip change | `POST /gen/{id}/regenerate { chip, value }` | UPDATE chip → NULL downstream (incl. `b_roll_plan`, `structure_template`, `active_season`, `b_roll_performance_signal`) → ARQ re-run COPY→CRITIC→SAFETY → reset chat counter to 3 | `scripts_ready → regenerating → scripts_ready` | `regenerating_start`, `regenerating_complete` |
| Chat turn | `POST /gen/{id}/chat { message }` | 5-stage chain → TDD `[TDD-CHAT-CHAIN]` | — (5-stage guards state) | `chat_turn` |
| `✓ Continue` | `POST /gen/{id}/advance` | Worker-STRATEGIST compiles card (resolves active_season + brand_tier + structure_template; invokes BRollPlanner; atomically persists plan + template + season + usage rows) | `scripts_ready → strategy_preview` | `phase_complete` → HD-4 |

---

## [PRD-HD4] · HD-4 — Your Ad Plan · Credit-Usage Approval Gate

**State:** `strategy_preview` (resident) · `awaiting_funds` *(with `pre_topup_status='strategy_preview'`)* (Top-Up Drawer overlay)

```
┌─────────────────────────────────────────────────────────────┐
│  📋  YOUR AD PLAN                            gen #AW-7421    │
│  🖼️  Product      GlowCraft Serum                [ Edit ]   │
│  🎯  Targeting    Women · Premium Glow           [ Edit ]   │
│  📝  Script       "Radiance, redefined…"         [ Edit ]   │
│      💬 Refined via Co-Pilot (2 turns used)                  │
│  🎬  Style        Orbit Motion · Golden Hour     [ Edit ]   │
│      [▶ GIF preview loops]                                   │
│  🎞️  Template     T1 · Bookended (Default Sensory)           │
│      Festive accent: — (no active season)                    │
│  🎤  Voice        Hindi · Sarvam Bulbul v3                   │
│  ⏱️  Duration     15 seconds (fixed)                          │
│  ✅  SGI watermark · ✅ C2PA signed · ✅ 5-yr audit           │
│  ⏱️  Est. render time: ~2 minutes                             │
│  ─────────────────────────────────────────────────           │
│  💳  Credits: 3 available  (after this render: 2)            │
│       ┌────────────────────────────────────────┐             │
│       │  ✓  Confirm & Use 1 Credit → Render    │             │
│       └────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

> **Note on the new Strategy Card rows (v4-Δ1):** "Template" surfaces the resolved `structure_template` (T1..T5) and "Festive accent" surfaces `active_season` (or `—` when no season is active). These two rows are payload-required (returned by Worker-STRATEGIST) and visible to the user; they sit between the existing Style and Voice rows. Zone structure (Z3) is preserved — these are additional rows within the existing summary block, not new zones.

**Server-driven primary button (3 modes, 1 position):**

| Tier | Balance | Label | On Click |
|---|---|---|---|
| Essential / Pro | ≥ 1 credit | `✓ Confirm & Use 1 Credit → Render` | Lua lock → `funds_locked` → HD-5 |
| Essential / Pro | = 0 | `+ Add Credits to Render` | State → `awaiting_funds` with `pre_topup_status='strategy_preview'` · Top-Up Drawer overlays HD-4 |
| Starter | N/A | `⚡ Upgrade to Render` | Plan Modal; direct API call returns 403 ECM-006 |

**[Edit] button targets (4 fields):**

| Target | State Returns To | Fields NULLed | Pipeline Re-runs |
|---|---|---|---|
| Product | `brief_ready` | scripts, critic_scores, strategy_card, selected_script_id, motion_id, scene_id, **b_roll_plan, structure_template, active_season, b_roll_performance_signal** | Phase 2 full (COPY→CRITIC→SAFETY) |
| Targeting | `scripts_ready` (triggers `regenerating`) | strategy_card, **b_roll_plan, structure_template, active_season, b_roll_performance_signal** | Phase 2 full |
| Script | `scripts_ready` | strategy_card, **b_roll_plan, structure_template, active_season, b_roll_performance_signal** | STRATEGIST only |
| Style (motion+scene) | `scripts_ready` | strategy_card, **b_roll_plan, structure_template, active_season, b_roll_performance_signal**, motion, scene | STRATEGIST only |

> **`broll_clip_usage` rows are NOT deleted on [Edit].** They are historical per-(user, clip, gen) and remain valid; rotation history persists across edits. CASCADE will sweep them only if the entire `generations` row is deleted. → BEF §6.8 v2 note + invariant S13.

**Rationale:** Credit-first language; paid users already transacted. COGS (₹) absent from UI; CostGuard enforces server-side. Trust row makes compliance visible as differentiator. Motion GIF preview reduces anxiety. Template row gives the user transparency about which compositional layout the system has chosen, without requiring them to understand T1..T5 mechanics.

**Top-Up Drawer (Shadcn `Sheet` — right on desktop, bottom on mobile):**

```
┌─────────────────────────────────────────────────────────────┐
│  [ HD-4 Strategy Card — dimmed but fully visible ]           │
│  ╭─────────────── Top-Up Drawer ───────────────╮             │
│  │  You have 0 credits. Add credits to render. │             │
│  │  ┌──────────────────┐  ┌──────────────────┐│             │
│  │  │ ESSENTIAL  ₹399  │  │ PRO      ₹1,499  ││             │
│  │  │ +4 credits       │  │ +25 credits      ││             │
│  │  │ 30-day validity  │  │ 45-day validity  ││             │
│  │  └──────────────────┘  └──────────────────┘│             │
│  │  [ Pay with UPI ]                           │             │
│  │  Your strategy is saved — you'll return     │             │
│  │  here automatically after payment.          │             │
│  ╰──────────────────────────────────────────────╯             │
└─────────────────────────────────────────────────────────────┘
```

**Behind-the-Scenes — Ledger Schema:**

```sql
-- wallet_transactions row for a credit lock (NOT a Razorpay payment):
INSERT INTO wallet_transactions (user_id, type, credits, status, gen_id)
VALUES ($1, 'lock', -1, 'locked'::wallet_status, $2);
-- payment_status LEFT NULL — reserved for type='topup' (Razorpay FSM)
-- status tracks lock lifecycle: 'locked' → 'consumed' | 'refunded'
-- Partial UNIQUE INDEX (gen_id) WHERE status='locked' prevents double-lock.
```

| Trigger | API | Backend | State | SSE |
|---|---|---|---|---|
| Mount | `GET /gen/{id}` | Hydrate `strategy_card` (incl. `b_roll_plan`, `structure_template`, `active_season`, `brand_color_primary`, `b_roll_available`), `wallet_balance`, tier, GIF URL | — | SSE attached |
| `[Edit] X` | `POST /gen/{id}/edit-back { target }` | UPDATE → NULL downstream (incl. v4-Δ1 fields) → ARQ if re-run needed | `strategy_preview → brief_ready`/`scripts_ready`/`regenerating` | `edit_back_complete` |
| `Confirm & Use 1 Credit` (paid, bal≥1) | `POST /gen/{id}/approve-strategy` | `@idempotent` + `actlock` → tier check → Lua `wallet_lock` → INSERT wallet row (ledger-first) → UPDATE status=`funds_locked` → ARQ enqueue `phase4_coordinator` | `strategy_preview → funds_locked` | `phase4_dispatched` → HD-5 |
| Lua lock FAILS | Same | ATOMIC UPDATE: status=`awaiting_funds`, pre_topup_status=`strategy_preview`; rollback ledger | `strategy_preview → awaiting_funds` | `lock_failed` → Top-Up Drawer |
| `Pay with UPI` | `POST /wallet/topup { plan }` | Razorpay Orders API → QR + `payment_id` | — | — |
| Razorpay webhook | `POST /webhook/razorpay` | HMAC verify → `payment_status` FSM → UNIQUE INDEX dedup → INSERT wallet row → ATOMIC UPDATE: `status=pre_topup_status, pre_topup_status=NULL WHERE user_id=? AND status='awaiting_funds'` (multi-row safe) | `awaiting_funds → <restored>` | `topup_captured` |
| Starter click | Same endpoint | 403 `STARTER_RENDER_BLOCKED` without calling Lua | — | — (client shows Plan Modal) |

**Failure paths:**

| Condition | ENUM | Code | Recovery |
|---|---|---|---|
| Starter renders | — | 403 ECM-006 | Plan Modal; HD-4 unchanged |
| Lua lock fails | `awaiting_funds` *(pre='strategy_preview')* | 402 ECM-007 | Top-Up Drawer on HD-4; strategy preserved |
| Cross-tab duplicate | — | 409 ECM-012 | `[Refresh]` toast |

---

## [PRD-HD5] · HD-5 — Render Progress

**State:** `funds_locked` (transient <1s) · `rendering` · `reflecting` · `composing`

```
┌─────────────────────────────────────────────────────────────┐
│  🎬  RENDERING YOUR AD                                        │
│  ████████████████████░░░░░░░░░░░  62%                         │
│  ~45 seconds remaining                                        │
│  ✅  Voice recorded · Hindi · Sarvam Bulbul v3                │
│  🔄  Rendering with Fal.ai (primary I2V)…                     │
│  ⏳  Selecting best render…                                    │
│  ⏳  Stitching B-roll…                                         │
│  ⏳  Composing final video…                                    │
│  [ provider-swap toast ]                                      │
│  ⚠️  "Fal.ai timed out. Switching to Minimax."                 │
│                                                               │
│  [ DLQ failure state ]                                        │
│  ❌  "Rendering failed. Your credit has been refunded."        │
│  [ ↻ Try Again ]        [ ← Back to Strategy ]                │
└─────────────────────────────────────────────────────────────┘
```

> **B-roll stage row visibility:** The "Stitching B-roll…" stage row is rendered only when `strategy_card.b_roll_available` is `TRUE` (i.e. `b_roll_plan` is non-null AND `b_roll_plan.hook` is non-null). Every template T1..T5 guarantees a hook clip per `[TDD-BROLL]-K` invariant 5, so in practice this row is always visible except during Tier-2 degradation (library coverage gap).

**Rationale:** Transparency beats speed. Named stages > generic spinner. Fallback messaging proves system is fighting, not silently retrying. Refund confirmation at failure removes ambiguity.

**Behind-the-Scenes — `phase4_coordinator`:**

```python
# phase4_coordinator (ARQ worker on DB1 phase4_workers)
# See TDD [TDD-WORKERS]-J (phase4_coordinator · Stops at preview_ready) for full implementation.

async def phase4_coordinator(gen_id):
    update_status(gen_id, 'rendering')
    tts_result, i2v_results = await asyncio.gather(
        worker_tts(script, language),
        worker_i2v_parallel(png, motion, scene)
    )
    update_status(gen_id, 'reflecting')
    best_i2v = await worker_reflect(i2v_results, source_png)
    update_status(gen_id, 'composing')
    # Worker-COMPOSE branches on structure_template (T1..T5).
    # CTA segment is a clip for T1 (b_roll_plan.cta non-null) or an
    # FFmpeg-rendered text-card over a brand-color gradient for T2..T5.
    preview_url = await worker_compose(
        tts_result, best_i2v, b_roll_plan, structure_template,
        benefit_lut, sgi_drawtext, brand_color_primary
    )
    update_status(gen_id, 'preview_ready')
    # NOTE: Coordinator STOPS here. Worker-EXPORT enqueued independently by L2.
```

| Trigger | Worker | State | SSE |
|---|---|---|---|
| `funds_locked` reached | `phase4_coordinator` starts | `funds_locked → rendering` | `render_started` |
| TTS completes | Worker-TTS | — | `worker_complete: tts` |
| I2V timeout / health <40 | ModelGateway CB (CLOSED/OPEN/HALF_OPEN) | — | `provider_fallback` toast |
| I2V × 2 complete | Worker-I2V | — | `worker_complete: i2v` |
| REFLECT picks best | Worker-REFLECT | `rendering → reflecting → rendering` | `reflecting` |
| COMPOSE assembles (template-branched per `structure_template`) | Worker-COMPOSE (FFmpeg, pad/trim, no `-shortest`, variable-arity concat) | `rendering → composing` | `composing` |
| Phase-4 render complete | — | `composing → preview_ready` | `preview_ready` → HD-6 |
| Coordinator or child dies | DLQ (`job.function_name='phase4_coordinator'`) → `wallet_refund.lua` → UPDATE status=`failed_render` | `rendering → failed_render` | `render_failed` within 5s |

**Failure recovery:**

| Condition | ENUM | Code | Recovery |
|---|---|---|---|
| DLQ catches dead Phase-4 job | `failed_render` | ECM-004 | Refund auto-applied; `[↻ Try Again]` → `strategy_preview` → HD-4 (re-lock). **Correct because Phase-4 assets are incomplete — full re-render required.** |
| `[← Back to Strategy]` | — | — | `strategy_preview` (no re-lock; user may `[Edit]` first) |

---

## [PRD-HD6] · HD-6 — Your Ad · Preview + Download (State-Aware Component)

**States:** `preview_ready` (entry) · `export_queued` (transient) · `export_ready` (terminal) · `failed_export` (inline recovery) · `awaiting_funds` *(with `pre_topup_status='failed_export'`)* (Top-Up Drawer overlay)

**Economics invariant:** HD-6 recovery **must NOT re-run Phase-4**. By HD-6, TTS + I2V + REFLECT + COMPOSE have all succeeded and persist in R2. Only Worker-EXPORT failed. `/retry-export` locks 1 credit and re-runs Worker-EXPORT in isolation, preserving ~₹10 of Phase-4 compute per retry.

**Atomic re-sign invariant:** When a retry is attempted with a stale declaration (>24h), the server does NOT transition status to `preview_ready`. Instead, it returns **428 ECM-020** and the user is kept on `failed_export` with 3 declaration checkboxes rendered inline above the retry button. The next `/retry-export` click carries the checkboxes in the request body; server inserts a new `audit_log` row, acquires the lock, updates state, and enqueues Worker-EXPORT in a single atomic chain.

### State 1: `preview_ready` (landing — declarations unsigned)

```
┌─────────────────────────────────────────────────────────────┐
│  🎬  YOUR AD IS READY                                         │
│  [ Video Player · SGI watermarked · 480p preview ]           │
│  ▶  00:04 / 00:15       🔊 Unmute                             │
│  Before you download the HD versions:                         │
│  ☐  I confirm this is for commercial advertising purposes.   │
│  ☐  I have rights to use this product image.                 │
│  ☐  I understand this is AI-generated per IT Rules 2026.     │
│  ┌──────────────────────┐     ┌──────────────────────┐       │
│  │  🔒 1:1 Square HD    │     │  🔒 9:16 Vertical HD │       │
│  │  (sign to download)  │     │  (sign to download)  │       │
│  └──────────────────────┘     └──────────────────────┘       │
│  [ 🔄 Start Over ]                  Credits remaining: 2     │
└─────────────────────────────────────────────────────────────┘
```

### State 2: `export_queued` (transient ~5–10s after user signs)

```
│  ✅  Declaration signed · Processing HD exports…              │
│  ┌──────────────────────┐     ┌──────────────────────┐       │
│  │  ⏳ Preparing 1:1…    │     │  ⏳ Preparing 9:16…    │       │
│  │  C2PA signing…       │     │  C2PA signing…       │       │
│  └──────────────────────┘     └──────────────────────┘       │
```

### State 3: `export_ready` (terminal)

```
│  ✅  YOUR AD IS COMPLETE                                       │
│  [ Video Player — still visible ]                             │
│  ┌──────────────────────┐     ┌──────────────────────┐       │
│  │  ⬇  1:1 Square HD    │     │  ⬇  9:16 Vertical HD │       │
│  │  1080×1080 · MP4     │     │  1080×1920 · MP4     │       │
│  │  ✅ C2PA signed       │     │  ✅ C2PA signed       │       │
│  └──────────────────────┘     └──────────────────────┘       │
│  🧠  Your style has been saved for next time.                 │
│  [ Manage Style Memory → ]   [ Reset ]                        │
│  Credits remaining: 2         [ + Create Another Ad → ]       │
```

### State 4a: `failed_export` (fresh declaration · ≤24h)

```
│  ❌  Export Failed                                             │
│  [ Video Player — still visible · preview assets preserved ] │
│  Export processing failed. Your credit has been refunded.    │
│  Our team has been alerted.                                  │
│  Your preview is intact — we just need to retry the final    │
│  signing step. This uses 1 credit (no re-rendering needed).  │
│  ┌────────────────────────────────────────┐                  │
│  │  ↻  Retry Export · Use 1 Credit        │                  │
│  └────────────────────────────────────────┘                  │
│  Retry attempts: 1 of 3                                       │
│  [ 🔄 Start Over ]                  Credits remaining: 2     │
```

### State 4b: `failed_export` (declaration stale · >24h — inline re-sign required)

Reached when client detects `now - declaration.signed_at > 24h` on hydration OR when server returns 428 ECM-020 on a retry without declarations. 3 checkboxes rendered **inline above** the retry button. User is still on `failed_export` — no state change has occurred.

```
│  ❌  Export Failed                                             │
│  [ Video Player — still visible · preview assets preserved ] │
│  Export processing failed. Your credit has been refunded.    │
│  Because your last declaration is more than 24 hours old,    │
│  please re-confirm below before retrying the export.         │
│  ☐  I confirm this is for commercial advertising purposes.   │
│  ☐  I have rights to use this product image.                 │
│  ☐  I understand this is AI-generated per IT Rules 2026.     │
│  ┌────────────────────────────────────────┐                  │
│  │  ↻  Retry Export · Use 1 Credit        │  ← disabled until │
│  └────────────────────────────────────────┘    3/3 checked   │
│  Retry attempts: 1 of 3                                       │
```

### The 3 Mandatory Declaration Checkboxes (Legally Non-Negotiable)

| # | Checkbox Text | Legal Basis |
|---|---|---|
| 1 | "I confirm this is for commercial advertising purposes." | Commercial use affirmation — distinguishes from personal/satirical use |
| 2 | "I have rights to use this product image." | Rights attestation — shifts liability to user for copyright/trademark claims |
| 3 | "I understand this is AI-generated per IT Rules 2026." | SGI disclosure acknowledgment — statutory requirement per §5 of IT Rules 2026 |

Each checkbox is an independent legal assertion. Bundling creates collateral-attack risk in grievance/litigation contexts.

**Rationale:**

- Single state-aware component; matches 2026 industry pattern.
- `failed_export` stays on HD-6 (economics) — preview context preserved.
- Download buttons visible from landing (disabled) → telegraphs outcome.
- Retry copy explicitly says "no re-rendering needed" — transparency on cost.
- Retry attempt counter → user knows they're bounded.
- Inline re-sign (State 4b) keeps user on `failed_export` rather than ping-ponging through `preview_ready` — retry intent preserved in FSM + audit trail.

**Behind-the-Scenes — Original Export Flow (first-time declaration sign):**

| Trigger | API | Backend | State | SSE |
|---|---|---|---|---|
| Mount (from HD-5 `preview_ready`) | `GET /gen/{id}` | Hydrate `preview_url` (R2 presigned 10-min TTL); declarations unsigned | — | SSE attached |
| 3 boxes checked + download click | `POST /gen/{id}/declaration { confirms_commercial_use, confirms_image_rights, confirms_ai_disclosure }` | Client validates 3/3 (else ECM-017) → Server captures IP/UA/timestamp/`sha256(declaration_text + gen_id + user_id)` → INSERT partitioned `audit_log` → UPDATE status=`export_queued` → **ARQ enqueue Worker-EXPORT on DB1 phase4_workers (independent of `phase4_coordinator`)** | `preview_ready → export_queued` | `declaration_signed` |
| Worker-EXPORT runs | — | Read `preview_url` + latest `audit_log` → Generate 2 HD formats → `c2patool` sign each → **returncode explicitly checked** → UPSERT `user_style_profiles` (200ms timeout, persists `brand_tier` + `brand_color_primary`) → R2 upload → UPDATE `wallet_transactions.status='consumed'` → UPDATE status=`export_ready` | `export_queued → export_ready` | `export_ready` |
| `c2patool` non-zero OR worker dies | DLQ `job.function_name='worker_export'` | `wallet_refund.lua` (ledger-first) → UPDATE status=`failed_export`. `export_retry_count` NOT incremented on original failure — only on retry dispatch | `export_queued → failed_export` | `export_failed` |

**Behind-the-Scenes — Retry Export Flow (9-step atomic re-sign chain):**

`/retry-export` endpoint accepts an **optional** `declarations: [1,2,3]` array. When last `audit_log` declaration is stale (>24h), server demands fresh signing; checkboxes arrive inside retry payload so `audit_log` INSERT + wallet lock + state transition + ARQ enqueue happen atomically. No silent state transition to `preview_ready` ever.

**Request contract:**

```http
POST /gen/{id}/retry-export
Idempotency-Key: <UUIDv4-generated-fresh-per-click>
Content-Type: application/json

{ "declarations": [true, true, true] }     ← OPTIONAL; REQUIRED only if latest audit_log stale
```

**9-step validation (enforced in order — see TDD `[TDD-API]-G` POST /api/generations/{gen_id}/retry-export — 9-Step Atomic Chain):**

| # | Step | Behavior on fail |
|---|---|---|
| 1 | `@idempotent(ttl=300, cache_only_2xx=True)` + `actlock` fence | Cached 2xx returned; else 409 ECM-012 |
| 2 | Validate `status == 'failed_export'` | 409 ECM-012 |
| 3 | Validate `export_retry_count < 3` | 410 ECM-019 |
| 4 | **Freshness check:** Query latest `audit_log.signed_at`; compute `is_stale = (NOW() - signed_at) > 24h`. If stale AND `declarations` missing → **428 ECM-020**, NO state change, NO ledger action. If stale AND `declarations==[1,1,1]` → INSERT fresh `audit_log` row (IP/UA/timestamp/SHA256) atomically → proceed | 428 ECM-020 (4b UI projection) |
| 5 | R2 HEAD on `preview_url` | 410 ECM-018 (terminal) |
| 6 | Tier check: Starter → 403 (defensive) | 403 ECM-006 |
| 7 | INSERT `wallet_transactions(type='lock', status='locked')` + `wallet_lock.lua`. Fail → ATOMIC UPDATE `status='awaiting_funds', pre_topup_status='failed_export'`; ROLLBACK ledger | 402 ECM-007 (HD-6 Top-Up Drawer) |
| 8 | Conditional UPDATE: `status='export_queued', export_retry_count += 1 WHERE status='failed_export'` (cross-tab race guard) | 409 ECM-012 |
| 9 | ARQ enqueue Worker-EXPORT standalone on DB1 phase4_workers | — |

**Step 4 ordering clarification:**

```
AUDIT_LOG INSERT (Step 4) → LUA LOCK (Step 7) → STATE UPDATE (Step 8) → ARQ ENQUEUE (Step 9)
    ↑ legal ack first
                               ↑ money moves second
                                                     ↑ state flips third
                                                                           ↑ compute dispatched last
```

If `audit_log` INSERT succeeds but Lua lock subsequently fails (Step 7 → `awaiting_funds`), the newly-inserted row is **kept** — legally valid regardless of money movement. On topup resumption, if declaration still fresh (<24h), next retry skips Step 4 re-sign.

**Schema additions → TDD `[TDD-MIGRATIONS]`:**

```sql
ALTER TABLE generations ADD COLUMN export_retry_count INTEGER NOT NULL DEFAULT 0
    CHECK (export_retry_count BETWEEN 0 AND 3);
ALTER TABLE generations ADD COLUMN pre_topup_status job_status NULL;
ALTER TABLE generations ADD CONSTRAINT chk_pre_topup_coupling CHECK (
    (status = 'awaiting_funds' AND pre_topup_status IN ('strategy_preview','failed_export'))
    OR (status <> 'awaiting_funds' AND pre_topup_status IS NULL)
);

-- v4-Δ1 additive columns on generations:
ALTER TABLE generations
  ADD COLUMN structure_template VARCHAR(5)
    CHECK (structure_template IN ('T1','T2','T3','T4','T5')),
  ADD COLUMN active_season VARCHAR(30) REFERENCES seasons(season_tag),
  ADD COLUMN b_roll_performance_signal JSONB;  -- reserved; v2-populated

-- Ledger: payment_status (topup FSM) vs status (lock lifecycle) — orthogonal lifecycles.
-- Partial UNIQUE INDEX preventing double-active-lock:
CREATE UNIQUE INDEX ux_wallet_active_lock
    ON wallet_transactions (gen_id) WHERE status = 'locked';
-- Double-credit guard on topups:
CREATE UNIQUE INDEX ux_wallet_topup_dedup
    ON wallet_transactions (razorpay_payment_id)
    WHERE type = 'topup' AND payment_status = 'captured';
```

**Postgres trigger — transitions that touch `pre_topup_status`:**

- `strategy_preview → awaiting_funds` requires `NEW.pre_topup_status = 'strategy_preview'`
- `failed_export → awaiting_funds` requires `NEW.pre_topup_status = 'failed_export'`
- `awaiting_funds → strategy_preview` requires `OLD.pre_topup_status = 'strategy_preview'` AND `NEW.pre_topup_status IS NULL`
- `awaiting_funds → failed_export` requires `OLD.pre_topup_status = 'failed_export'` AND `NEW.pre_topup_status IS NULL`
- Any other transition into/out of `awaiting_funds` → REJECT.

**Failure recovery (MECE, all inline on HD-6):**

| Condition | ENUM | Code | Recovery |
|---|---|---|---|
| Fewer than 3 declarations on first sign | — | 400 ECM-017 | Unchecked box flashes red |
| Worker-EXPORT fails (1st or 2nd) | `failed_export` | ECM-005 | Refund; inline "Retry Export · Use 1 Credit" |
| Retry attempt ≥ 3 | `failed_export` | ECM-019 | "Contact Support" CTA; retry disabled; credit refunded |
| R2 preview purged (>30d) | — (terminal) | ECM-018 | "Assets Expired" inline; only CTA = `[Start New Generation]` |
| **Declaration >24h stale AND no declarations in payload** | **no transition (`failed_export`)** | **428 ECM-020** | **State 4b inline checkbox panel; next click bundles `declarations:[1,1,1]`** |
| Declaration stale AND declarations present | `failed_export → export_queued` (if Steps 5–9 pass) | — (happy path) | New `audit_log` row; retry proceeds |
| Wallet balance 0 at retry (Step 7 fail) | `awaiting_funds` *(pre='failed_export')* | 402 ECM-007 | Top-Up Drawer on HD-6; webhook restores to `failed_export` |

**Quiet celebration on `export_ready`:** background transitions neutral → warm cream over 400ms. No confetti.

---

## [PRD-STATE-MATRIX] · State → Screen Coverage (MECE)

| ENUM | `pre_topup_status` | Resident Screen | UI Treatment |
|---|---|---|---|
| `queued` | NULL | HD-1 | Inline spinner; CTA disabled |
| `extracting` | NULL | HD-1 | "Analyzing your product…" shimmer |
| `brief_ready` | NULL | HD-2 | Isolated PNG + ambient confidence border |
| `scripting` | NULL | HD-3 | Shimmer over script-card zone |
| `critiquing` | NULL | HD-3 | "Scoring drafts…" shimmer |
| `safety_checking` | NULL | HD-3 | "Running safety filter…" shimmer |
| `scripts_ready` | NULL | HD-3 | Full workspace |
| `regenerating` | NULL | HD-3 | Single-card or full shimmer |
| `strategy_preview` | NULL | HD-4 | Strategy Card · primary `Confirm & Use 1 Credit` |
| `awaiting_funds` | `'strategy_preview'` | HD-4 | Strategy Card dimmed + Top-Up Drawer |
| `awaiting_funds` | `'failed_export'` | HD-6 | Preview + `failed_export` context dimmed + Top-Up Drawer |
| `funds_locked` | NULL | HD-5 | "Starting render…" (transient <1s) |
| `rendering` | NULL | HD-5 | Progress + stage labels |
| `reflecting` | NULL | HD-5 | "Selecting best render…" stage |
| `composing` | NULL | HD-5 | "Composing final video…" stage (template-branched) |
| `preview_ready` | NULL | HD-6 | Player + 3 unsigned declarations + disabled downloads |
| `export_queued` | NULL | HD-6 | Player + signed decls + "Preparing…" buttons |
| `export_ready` | NULL | HD-6 | Player + active downloads + Style Memory ack |
| `failed_category` | NULL | HD-1 (re-entry) | ECM-001 error card |
| `failed_compliance` | NULL | HD-1 (re-entry) | ECM-002 error card |
| `failed_safety` | NULL | HD-3 (inline) | ECM-003; auto-retry 1×; else `[Back to Scripts]` |
| `failed_render` | NULL | HD-5 (inline) | ECM-004 + refund toast · `[↻ Try Again]` → HD-4 re-lock |
| `failed_export` (fresh decl) | NULL | HD-6 (inline 4a) | ECM-005 + refund toast · `[↻ Retry Export · 1 Credit]` |
| `failed_export` (stale decl) | NULL | HD-6 (inline 4b) | ECM-005 + 3 inline checkboxes above retry button |

**MECE audit:** 22/22 ENUM values mapped. `awaiting_funds` has two projections disambiguated by `pre_topup_status`. `failed_export` has two UI projections (4a/4b) disambiguated by client-side comparison of `audit_log.signed_at` against `NOW()-24h`; both are the SAME database state. 0 orphan states. 0 ambiguous projections.

---

## [PRD-ERROR-MATRIX] · Error State Matrix & Recovery Paths (Zero Dead Ends)

| Error | Origin | Recovery Target | Mechanism | ENUM Transition | Compute Impact |
|---|---|---|---|---|---|
| `failed_category` | HD-1 | HD-1 (fresh `gen_id`) | `[Start Over]` | Current gen abandoned → new row | None |
| `failed_compliance` | HD-1 | HD-1 (fresh `gen_id`) | `[Start Over]` | Same | None |
| `failed_safety` | HD-3 | HD-3 (auto-retry 1×) | System retry → user edits chips | `failed_safety → regenerating → scripts_ready` | Re-runs Phase 2 (~₹0.30) |
| `failed_render` | HD-5 | HD-4 (re-lock) | `[↻ Try Again]` | `failed_render → strategy_preview` | Full Phase-4 re-run — legitimate (assets incomplete) |
| `failed_export` | HD-6 (stays) | HD-6 | `[↻ Retry Export · 1 Credit]` via `/retry-export` | `failed_export → export_queued` OR `→ awaiting_funds` *(pre='failed_export')* OR no transition (428 ECM-020) | Worker-EXPORT only (~₹0.35); preserves ~₹10 of Phase-4 assets |
| `STARTER_RENDER_BLOCKED` | HD-4 | HD-4 | Plan Modal | — | None |
| `INSUFFICIENT_FUNDS` (HD-4) | HD-4 | HD-4 | Top-Up Drawer | `strategy_preview → awaiting_funds` *(pre='strategy_preview')* | None |
| `INSUFFICIENT_FUNDS` (HD-6 retry) | HD-6 | HD-6 | Top-Up Drawer | `failed_export → awaiting_funds` *(pre='failed_export')* | None |
| `CHAT_LIMIT_REACHED` | HD-3 | HD-3 | Chat disabled; Continue active | — | None |
| `CHAT_CEILING_HIT` | HD-3 | HD-3 | Chat disabled (budget); Continue active | — | None |
| `CHAT_SAFETY_REJECT` | HD-3 | HD-3 | Input re-enabled; counter preserved | — | COGS already recorded |
| `CHAT_COMPLIANCE_REJECT` | HD-3 | HD-3 | Input cleared, re-enabled | — | None (no LLM call) |
| `CROSS_TAB_CONFLICT` | Any mutating call | Current | `[Refresh]` toast | — | None |
| `HYDRATION_FAILED` | Any mount | Current | `[Refresh Page]` | — | None |
| `UPLOAD_TOO_LARGE` | HD-1 | HD-1 | 413 inline | — | None |
| `FIRECRAWL_TIMEOUT` | HD-1 | HD-1 | Tab switches to Upload | — | None |
| `C2PA_SIGN_FAILED` | HD-6 (DLQ) | HD-6 (inline) | Treated as `failed_export` → `/retry-export` | `export_queued → failed_export` | Same as `failed_export` |
| `DECLARATION_INVALID` | HD-6 | HD-6 | Checkbox highlight | — | None |
| `EXPORT_RETRY_EXHAUSTED` | HD-6 | HD-6 (inline) | "Contact Support" CTA; retry disabled | `failed_export` (terminal after 3 retries) | Credit refunded; no further retries |
| `EXPORT_ASSETS_EXPIRED` | HD-6 | HD-6 (inline, only CTA = `[Start New Generation]`) | R2 HEAD returned 404 (>30d purge) | `failed_export` (terminal) | Credit refunded; new `gen_id` required |
| **`DECLARATION_REFRESH_REQUIRED` (ECM-020)** | **HD-6 retry attempt** | **HD-6 (stays `failed_export`, State 4b)** | **Client renders 3 checkboxes above retry; next call carries `declarations:[1,1,1]`** | **No transition** | **None on 428; retry cost on subsequent atomic retry** |

**Dead-end audit:** 20/20 error codes have defined recovery + mechanism. 0 dead ends.

---

## [PRD-IDEMPOTENCY] · Network Resiliency — Idempotency & Retry

| Endpoint | Idempotency Behavior | Cross-Tab |
|---|---|---|
| `POST /generate` | `localStorage` UUIDv4 · 5-min TTL · cache only 2xx | 409 |
| `POST /gen/{id}/advance` | Same | 409 |
| `POST /gen/{id}/regenerate` | Same; prevents double chip-change | 409 |
| `POST /gen/{id}/chat` | Same; prevents double turn + double COGS | 409 |
| `POST /gen/{id}/edit-back` | Same; prevents double NULL-downstream | 409 |
| `POST /gen/{id}/approve-strategy` | Same + server `actlock` over Redis lock | **Critical — wallet-lock race prevented** |
| `POST /gen/{id}/declaration` | Same; prevents double `audit_log` INSERT | 409 |
| `POST /gen/{id}/retry-export` | **Monotonic key `{gen_id}:retry-export:{export_retry_count}`** — prevents cache collision. UUIDv4 value; cache only 2xx. On 4xx (400/402/409/428), client clears entry and generates fresh UUIDv4. Server `actlock` + conditional UPDATE on `status='failed_export'` | 409 — partial UNIQUE INDEX guards double-lock |
| `POST /wallet/topup` | Razorpay `payment_id` natural key + `payment_status` FSM | — |
| `GET /gen/{id}/download/{format}` | — (idempotent by nature; returns presigned URL) | — |

**Client contract:**

- UUIDv4 Idempotency-Key per action click, sent in `Idempotency-Key` HTTP header.
- Persisted in `localStorage` keyed by `{gen_id}:{action}` (plus `:{export_retry_count}` for `retry-export`).
- `@idempotent` caches ONLY 2xx terminal responses. Recoverable 4xx (400/402/409/428) and 5xx NEVER cached.
- Cross-tab sync via `storage` event listener.
- `GET /gen/{id}` on mount BEFORE attaching SSE.
- SSE reconnect re-issues GET to close missed-event gap.
- Exponential backoff: 1s → 2s → 4s → max 30s.

> **Note on localStorage key prefix:** The `aw_` prefix in legacy code (`aw_idem_{user_id}_{gen_id}_{action}`) is a frozen code constant for cache compatibility with existing user devices; it does **not** track the product-name rename to "Adcreo" and must not be renamed. CI gate `localstorage_prefix_lint.py` enforces the `aw_` prefix.

---

## [PRD-ERROR-COPY] · Error Copy Matrix

| ID | Code | HTTP | Title | Body | Recovery | Landing |
|---|---|---|---|---|---|---|
| **ECM-001** | `failed_category` | SSE | "Product Not Supported" | "We don't support this product category yet. We work best with beauty, food, accessories, electronics, and home products." | `[Start Over]` | HD-1 |
| **ECM-002** | `failed_compliance` | SSE | "Content Flagged" | "This content didn't pass our safety check required by IT Rules 2026. Please try a different product." | `[Start Over]` | HD-1 |
| **ECM-003** | `failed_safety` | SSE | "Scripts Need Adjustment" | "Our brand safety check flagged all scripts. We're regenerating with adjusted parameters…" | Auto-retry 1×; else `[Back to Scripts]` | HD-3 |
| **ECM-004** | `failed_render` | SSE | "Rendering Failed" | "Video rendering failed after retries. **Your credit has been refunded to your wallet.**" | `[↻ Try Again]` · `[← Back to Strategy]` | HD-5 → HD-4 |
| **ECM-005** | `failed_export` | SSE | "Export Failed — Retry Available" | "Export processing failed. **Your credit has been refunded.** Your preview is intact — we just need to retry the final signing step. This uses 1 credit (no re-rendering needed)." | `[↻ Retry Export · Use 1 Credit]` | HD-6 (stays inline) |
| **ECM-006** | `STARTER_RENDER_BLOCKED` | 403 | "Upgrade to Render" | "The free plan lets you preview your strategy. Upgrade to Essential or Pro to render your video." | `[View Plans]` | HD-4 (modal) |
| **ECM-007** | `INSUFFICIENT_FUNDS` | 402 | "Add Credits to Render" | "You need at least 1 credit to render. Top up your wallet — your strategy is saved." | `[Add Credits]` | HD-4 or HD-6 (Top-Up Drawer) |
| **ECM-008** | `CHAT_LIMIT_REACHED` | 429 | "Chat Limit Reached" | "You've used all 3 refinement turns for this video. Review your script and continue." | (Disabled) | HD-3 |
| **ECM-009** | `CHAT_CEILING_HIT` | 429 | "Budget Limit" | "Another chat turn would exceed this generation's cost ceiling. Continue with your current script." | (Disabled) | HD-3 |
| **ECM-010** | `CHAT_SAFETY_REJECT` | 422 | "Refinement Flagged" | "That refinement didn't pass our brand safety filter. Try a different instruction. (This turn was not counted.)" | (Re-enabled) | HD-3 |
| **ECM-011** | `CHAT_COMPLIANCE_REJECT` | 400 | "Invalid Input" | "Your message contained content we can't process. Please rephrase your instruction." | (Cleared, re-enabled) | HD-3 |
| **ECM-012** | `CROSS_TAB_CONFLICT` | 409 | "Action In Progress" | "This action is being processed in another tab. Please wait a moment and try again." | `[Refresh]` | Current |
| **ECM-013** | `HYDRATION_FAILED` | — | "Connection Lost" | "We couldn't load your generation. Please refresh the page." | `[Refresh Page]` | Current |
| **ECM-014** | `UPLOAD_TOO_LARGE` | 413 | "File Too Large" | "Images must be under 10MB. Please resize or compress your image." | `[Try Again]` | HD-1 |
| **ECM-015** | `FIRECRAWL_TIMEOUT` | SSE | "Scraping Timeout" | "We couldn't fetch your product page in time. Try uploading a product image directly." | `[Upload Image]` · `[Try URL Again]` | HD-1 |
| **ECM-016** | `C2PA_SIGN_FAILED` | DLQ | "Signing Failed" | "We couldn't sign your video for compliance. **Your credit has been refunded.** Our team is investigating." | Treated as `failed_export` → `[↻ Retry Export]` | HD-6 (inline) |
| **ECM-017** | `DECLARATION_INVALID` | 400 | "Declaration Required" | "Please accept all 3 declarations before exporting." | (Checkbox highlight) | HD-6 |
| **ECM-018** | `EXPORT_ASSETS_EXPIRED` | 410 | "Preview Assets Expired" | "Your render is more than 30 days old, so we've cleaned up the preview files. You'll need to start a new generation — we're sorry for the inconvenience." | `[Start New Generation]` | HD-6 → HD-1 |
| **ECM-019** | `EXPORT_RETRY_EXHAUSTED` | 410 | "Export Retry Limit Reached" | "Export failed 3 times. **All credits have been refunded.** Please contact support so we can investigate this generation." | `[Contact Support]` · `[Start New Generation]` | HD-6 (terminal) |
| **ECM-020** | `DECLARATION_REFRESH_REQUIRED` | **428** | "Declaration Refresh Required" | "Your last declaration is more than 24 hours old. Please re-confirm the 3 declarations above to retry the export. No credit will be charged until you re-sign." | 3 checkboxes inline above retry; on 3/3 + re-click, `/retry-export` body carries `declarations:[1,1,1]` → atomic flow | HD-6 (stays `failed_export`, State 4b) |

---

## [PRD-PAYMENT-FSM] · Payment Lifecycle State Machine

Governs Razorpay webhook processing. Semantically distinct from `wallet_transactions.status` (lock lifecycle).

```
                ┌──────────┐
                │ pending  │  ← wallet_transactions.payment_status
                └────┬─────┘     (type='topup' ONLY)
                     │
           ┌─────────┴─────────┐
           ▼                   ▼
     ┌──────────┐         ┌──────────┐
     │ captured │         │  failed  │  (terminal)
     └────┬─────┘         └──────────┘
          │
          ▼ optional admin action
     ┌──────────┐
     │ refunded │  (terminal)
     └──────────┘
```

**Webhook FSM rules (Razorpay `captured` / `failed` events):**

1. **Idempotency via natural key:** `razorpay_payment_id` is UNIQUE-indexed on `wallet_transactions WHERE type='topup' AND payment_status='captured'`. Duplicate `captured` events → no-op.
2. **Reorder safety:** `captured` can arrive before or after `failed`. Webhook applies FSM:
   - `pending → captured` ✅
   - `pending → failed` ✅
   - `captured → failed` ❌ (ignored — terminal)
   - `failed → captured` ❌ (ignored — terminal)
3. **Origin restoration (atomic with capture):**

   ```sql
   -- Executed by webhook handler on 'captured' event, after wallet credit UPSERT:
   UPDATE generations
   SET status = pre_topup_status,
       pre_topup_status = NULL
   WHERE user_id = $1 AND status = 'awaiting_funds';
   ```
   Multi-row safe: if a user has multiple parked gens (HD-4 and HD-6), both restore atomically.

4. **Signature:** HMAC-SHA256 verification via `X-Razorpay-Signature` header. Signature fail → 401, no mutation.

---

## [PRD-DESIGN-TOKENS] · Design Token Dictionary

Strict key-value dictionary. **Agent MUST NOT hallucinate colors, spacing, or type.** All values below are frozen identifiers. Any deviation fails `ui_tokens_lint.py` CI job.

### Tailwind Configuration

File: `tailwind.config.ts`. The agent builds this file verbatim from the tables below.

#### Brand Tokens (CSS vars → Tailwind `theme.extend.colors`)

| Token key | CSS var | Hex (light) | Hex (dark) | Usage |
|---|---|---|---|---|
| `brand.primary` | `--brand-primary` | `#0D9488` (teal-600) | `#5EEAD4` (teal-300) | Primary CTAs, links |
| `brand.primary-hover` | `--brand-primary-hover` | `#0F766E` (teal-700) | `#2DD4BF` (teal-400) | CTA hover |
| `brand.primary-fg` | `--brand-primary-fg` | `#FFFFFF` | `#0F172A` (slate-900) | Text on primary |
| `brand.accent` | `--brand-accent` | `#F59E0B` (amber-500) | `#FBBF24` (amber-400) | Credit/₹ indicators |
| `brand.muted` | `--brand-muted` | `#F1F5F9` (slate-100) | `#1E293B` (slate-800) | Card backgrounds |
| `brand.border` | `--brand-border` | `#E2E8F0` (slate-200) | `#334155` (slate-700) | Default borders |
| `brand.fg` | `--brand-fg` | `#0F172A` (slate-900) | `#F1F5F9` (slate-100) | Body text |
| `brand.fg-muted` | `--brand-fg-muted` | `#64748B` (slate-500) | `#94A3B8` (slate-400) | Secondary text |

> Note: `user_style_profiles.brand_color_primary` (consumed by Worker-COMPOSE for T2..T5 text-card CTA backgrounds) is a **DB column**, not a design token. Worker-COMPOSE falls back to a neutral charcoal `#1A1A1A` when this column is NULL (cold-start brands).

#### Semantic Confidence Tokens (non-negotiable per `[PRD-CONFIDENCE]`)

| Token key | CSS var | Hex (light) | Hex (dark) | Used on |
|---|---|---|---|---|
| `confidence.high` | `--confidence-high` | `#10B981` (emerald-500) | `#34D399` (emerald-400) | HD-2 border when `score ≥ 0.90` |
| `confidence.high-bg` | `--confidence-high-bg` | `#ECFDF5` (emerald-50) | `#064E3B` (emerald-900) | Ambient fill behind PNG |
| `confidence.medium` | `--confidence-medium` | `#F59E0B` (amber-500) | `#FBBF24` (amber-400) | HD-2 border when `0.85 ≤ score < 0.90` |
| `confidence.medium-bg` | `--confidence-medium-bg` | `#FFFBEB` (amber-50) | `#78350F` (amber-900) | Ambient fill |
| `confidence.low` | `--confidence-low` | `#EF4444` (red-500) | `#F87171` (red-400) | HD-2 border when `score < 0.85` |
| `confidence.low-bg` | `--confidence-low-bg` | `#FEF2F2` (red-50) | `#7F1D1D` (red-900) | Ambient fill |

#### Semantic State Tokens

| Token key | CSS var | Hex | Used on |
|---|---|---|---|
| `state.success` | `--state-success` | `#10B981` | `export_ready` checks, `declaration_signed` |
| `state.warning` | `--state-warning` | `#F59E0B` | `awaiting_funds` drawer header, retry counter `2 of 3` |
| `state.danger` | `--state-danger` | `#EF4444` | `failed_render`, `failed_export`, `ECM-018`, `ECM-019` |
| `state.info` | `--state-info` | `#0EA5E9` | Provider-swap toasts, SSE reconnect banner |
| `state.neutral-fg` | `--state-neutral-fg` | `#475569` | Disabled labels, greyed-out states |

### Typography

| Token | Value | Tailwind key |
|---|---|---|
| `font.sans` | `ui-sans-serif, system-ui, -apple-system, "Segoe UI", "Inter", "Roboto", "Noto Sans", "Noto Sans Devanagari", sans-serif` | `fontFamily.sans` |
| `font.mono` | `ui-monospace, SFMono-Regular, "Cascadia Code", "Source Code Pro", Menlo, monospace` | `fontFamily.mono` |

**No webfont downloads.** System-stack-first is non-negotiable — mandatory to preserve first-paint performance on Indian 3G/4G networks.

**Devanagari support** (`Noto Sans Devanagari` in the stack) is REQUIRED so the ₹ symbol renders correctly and future Indic UI copy is preserved on older Android devices.

| Scale | Size / Leading | Usage |
|---|---|---|
| `text.xs` | 12px / 16px | Metadata, turn counters |
| `text.sm` | 14px / 20px | Body, chip labels |
| `text.base` | 16px / 24px | Default body (accessibility floor) |
| `text.lg` | 18px / 28px | Card headings |
| `text.xl` | 20px / 28px | Section headings |
| `text.2xl` | 24px / 32px | Screen titles (HD-1..HD-6) |
| `text.3xl` | 30px / 36px | Strategy Card product summary |

| Weight | Value | Usage |
|---|---|---|
| `weight.regular` | 400 | Body |
| `weight.medium` | 500 | Labels, chip text |
| `weight.semibold` | 600 | CTAs, card titles |
| `weight.bold` | 700 | Screen titles only |

### Spacing / Radius / Shadow

| Token | Value | Usage |
|---|---|---|
| `space.1` | 4px | Tight inline spacing |
| `space.2` | 8px | Chip padding |
| `space.3` | 12px | Form input padding-Y |
| `space.4` | 16px | Card padding (mobile), stack gap |
| `space.6` | 24px | Card padding (desktop), section gap |
| `space.8` | 32px | Screen padding |
| `space.12` | 48px | Between major zones |
| `radius.sm` | 6px | Chips, toasts |
| `radius.md` | 10px | Buttons, inputs |
| `radius.lg` | 14px | Cards, script tiles |
| `radius.xl` | 20px | Sheets, modals |
| `shadow.sm` | `0 1px 2px 0 rgb(0 0 0 / 0.05)` | Chips, disabled buttons |
| `shadow.md` | `0 4px 6px -1px rgb(0 0 0 / 0.1)` | Cards, primary buttons |
| `shadow.lg` | `0 10px 15px -3px rgb(0 0 0 / 0.1)` | Sheets, dialogs |

### Motion

| Token | Value | Usage |
|---|---|---|
| `motion.fast` | 150ms cubic-bezier(0.4, 0, 0.2, 1) | Hover state changes |
| `motion.base` | 250ms cubic-bezier(0.4, 0, 0.2, 1) | Sheet open/close, tab switch |
| `motion.slow` | 400ms cubic-bezier(0.4, 0, 0.2, 1) | **Quiet celebration** on `export_ready` (warm-cream fade) |
| `motion.reduce` | `@media (prefers-reduced-motion)` → set all to 0ms | Accessibility |

### Breakpoints

| Token | min-width | Usage |
|---|---|---|
| `bp.sm` | 640px | Small tablets |
| `bp.md` | **768px** | **Mobile/desktop split — HD-3 layout switches here** |
| `bp.lg` | 1024px | Desktop full-width 4-zone HD-3 |
| `bp.xl` | 1280px | Max container width |

### ShadcnUI Base Config (`components.json`)

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

**ShadcnUI components allowed (MVP scope):** `Button`, `Card`, `Dialog`, `Sheet`, `Tabs`, `Checkbox`, `Input`, `Label`, `Toast` (via `sonner`), `Progress`, `Skeleton`, `Badge`, `Alert`, `AlertDialog`. Any additional component requires PRD change.

---

## [PRD-UI-TREE] · Component Hierarchy (Next.js 15 App Router)

Absolute tree. **Agent MUST NOT invent additional top-level directories.** Matches TDD `[TDD-SCAFFOLD]`.

```
frontend/
├── app/
│   ├── layout.tsx                          # Root layout · <html>, <body>, providers
│   ├── page.tsx                            # "/" — landing (auth-gated)
│   ├── globals.css                         # Tailwind base + design-token CSS vars
│   ├── error.tsx                           # Route-level error boundary (ECM-013)
│   ├── not-found.tsx                       # 404
│   │
│   ├── (auth)/
│   │   └── callback/
│   │       └── route.ts                    # Google OAuth callback → set JWT cookie → redirect /
│   │
│   ├── [gen_id]/
│   │   ├── page.tsx                        # State-aware router — mounts <GenerationShell/>
│   │   ├── loading.tsx                     # Hydration skeleton
│   │   └── error.tsx                       # Per-gen error boundary (recoverable errors)
│   │
│   └── api/                                # Thin Next.js API routes proxy → FastAPI L2
│       ├── auth/[...]/route.ts             # NextAuth.js routes
│       └── sse/[gen_id]/route.ts           # SSE proxy (EventSource forwarding)
│
├── components/
│   │
│   ├── shell/
│   │   ├── GenerationShell.tsx             # Top-level state router
│   │   ├── TopBar.tsx                      # Logo · credits widget · profile menu
│   │   └── CreditsWidget.tsx               # Pulses red at 1 credit · shows active lock count
│   │
│   ├── hd/                                 # One folder per screen
│   │   ├── HD1Ingestion.tsx                # URL-tab + Upload-tab · 10MB gate · ECM-001/002/014/015
│   │   ├── HD2Isolation.tsx                # Before/after toggle · <ConfidenceBorder>
│   │   ├── HD3CreativeWorkspace.tsx        # Desktop 4-zone · Mobile tabs + FAB
│   │   │   ├── ScriptZone.tsx              # 3 framework-labeled <ScriptCard> tiles
│   │   │   ├── StyleZone.tsx               # <MotionSelector> + <SceneSelector>
│   │   │   ├── ChipBar.tsx                 # Sticky horizontal-scroll context chips
│   │   │   └── CoPilotChatSheet.tsx        # Shadcn Sheet (desktop: right panel, mobile: bottom FAB)
│   │   ├── HD4StrategyCard.tsx             # 4× [Edit] targets · server-driven 3-mode primary button
│   │   │   ├── StrategySummary.tsx         # Product/Targeting/Script/Style/Template/Voice/Duration rows
│   │   │   ├── ComplianceTrustRow.tsx      # SGI · C2PA · 5-yr audit badges
│   │   │   └── MotionGifPreview.tsx        # Looping GIF from /gen/{id}
│   │   ├── HD5RenderProgress.tsx           # Progress + stage list · SSE-driven · B-roll stage gated by b_roll_available
│   │   └── HD6Preview.tsx                  # SINGLE state-aware composite (5 states + 4a/4b split)
│   │       ├── StatePreviewReady.tsx       # State 1: player + 3 unsigned decls + disabled downloads
│   │       ├── StateExportQueued.tsx       # State 2: "Preparing..." buttons
│   │       ├── StateExportReady.tsx        # State 3: active downloads + StyleMemoryAck
│   │       ├── StateFailedExport4a.tsx     # State 4a: fresh decl, retry button + counter
│   │       ├── StateFailedExport4b.tsx     # State 4b: stale decl, inline 3-checkbox bank + retry
│   │       ├── VideoPlayer.tsx             # 480p preview with SGI watermark
│   │       ├── DeclarationCheckboxes.tsx   # 3-checkbox bank (used in State 1 AND State 4b)
│   │       ├── RetryExportPanel.tsx        # Retry button + attempt counter
│   │       └── StyleMemoryAck.tsx          # "Your style has been saved" · manage · reset
│   │
│   ├── shared/
│   │   ├── ConfidenceBorder.tsx            # Wraps children with confidence-level ring
│   │   ├── FrameworkLabel.tsx              # Badge for one of 12 framework enum values
│   │   ├── ScriptCard.tsx                  # [HOOK][BODY][CTA] with framework + score
│   │   ├── MotionSelector.tsx              # 5 motion archetypes · ★ from Style Memory
│   │   ├── SceneSelector.tsx               # 8 environment presets
│   │   ├── TopUpDrawer.tsx                 # Shadcn Sheet · overlays HD-4 OR HD-6 by pre_topup_status
│   │   ├── PlanModal.tsx                   # Shadcn Dialog · Starter upgrade (ECM-006)
│   │   ├── ErrorToast.tsx                  # sonner wrapper · ECM-012, fallback messages
│   │   ├── EcmErrorCard.tsx                # Full-screen failure card (HD-1 re-entry: ECM-001/002)
│   │   └── LoadingShimmer.tsx              # Transient state shimmers
│   │
│   └── ui/                                 # Shadcn primitives (generated by shadcn-cli · DO NOT HAND-EDIT)
│       ├── button.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── sheet.tsx
│       ├── tabs.tsx
│       ├── checkbox.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── progress.tsx
│       ├── skeleton.tsx
│       ├── badge.tsx
│       ├── alert.tsx
│       ├── alert-dialog.tsx
│       └── sonner.tsx
│
├── lib/
│   ├── api/
│   │   ├── client.ts                       # fetch wrapper · JWT header injection · 4xx-drop-idem-key rule
│   │   ├── types.ts                        # Imported from @shared/types (single source of truth)
│   │   └── endpoints.ts                    # Constants: "/api/generations", "/gen/{id}/chat", etc.
│   ├── sse/
│   │   └── client.ts                       # EventSource wrapper · exponential backoff 1→2→4→30s
│   ├── idempotency/
│   │   └── keys.ts                         # localStorage keys: aw_idem_{user_id}_{gen_id}_{action}  (frozen prefix)
│   ├── state/
│   │   └── store.ts                        # Zustand · hydrated from GET · SSE sink · cross-tab sync
│   ├── tokens.ts                           # Design-token TypeScript constants (mirror of CSS vars)
│   └── utils.ts                            # cn(), getConfidenceLevel(), formatRupees(), etc.
│
├── shared/                                 # Shared with backend via symlink or submodule
│   └── types/
│       ├── job_status.ts                   # JobStatus union (22 values, matches Postgres ENUM)
│       ├── ad_framework.ts                 # AdFramework enum + FRAMEWORK_ANGLE_MAP + SAFE_TRIO
│       ├── ecm_codes.ts                    # ECM_CODES const record (ECM-001..ECM-020)
│       ├── generation.ts                   # GenerationState + StrategyCardV3 + BRollClip + BRollPlan
│       └── api.ts                          # Request/response contracts
│
├── tailwind.config.ts
├── components.json                         # Shadcn config (see [PRD-DESIGN-TOKENS])
├── next.config.mjs
├── tsconfig.json
└── package.json
```

**Agent rules:**

- New route under `/app/*` that does NOT map to `HD-1..HD-6` is auto-rejected (see `[PRD-UX-FREEZE]`). Peripheral `/grievance` is the only exception.
- New shadcn primitive import requires PM sign-off.
- `shared/types/` is the single source of truth; backend imports the same types (symlinked).
- No component under `components/ui/*` is hand-edited (shadcn-cli owns these).
- `StrategyCardV3.b_roll_plan` is typed `BRollPlan | null` (object form `{template, hook, context, cta}`), not `BRollClip[]`. `structure_template`, `active_season`, `brand_color_primary`, and `b_roll_available` are payload fields on the strategy card.

---

## [PRD-UI-MOCKS] · UI Mock State JSONs

Every major state has a concrete static JSON payload that the `GET /api/generations/{gen_id}` endpoint returns. The agent uses these for **offline UI development**: Storybook stories, Playwright fixtures, and pure-component rendering without a live backend. Every JSON is a valid subset of the full `GenerationState` interface (→ TDD `[TDD-TYPES]`).

**Common scaffold** (shared across all mocks):

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "11111111-2222-3333-4444-555555555555",
  "plan_tier": "essential",
  "created_at": "2026-05-15T10:00:00Z",
  "updated_at": "2026-05-15T10:02:34Z"
}
```

### MOCK-01 · HD-1 · `queued` → `extracting` (Phase 1 in-flight)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "11111111-2222-3333-4444-555555555555",
  "plan_tier": "essential",
  "status": "extracting",
  "pre_topup_status": null,
  "source_url": "https://www.meesho.com/glowcraft-serum/p/abc123",
  "source_image_url": null,
  "confidence_score": null,
  "product_brief": null,
  "routed_frameworks": null,
  "raw_scripts": null,
  "chat_turns_used": 0,
  "export_retry_count": 0,
  "error_code": null,
  "created_at": "2026-05-15T10:00:00Z",
  "updated_at": "2026-05-15T10:00:08Z"
}
```

### MOCK-02 · HD-2 · `brief_ready` · HIGH confidence (≥0.90)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "11111111-2222-3333-4444-555555555555",
  "plan_tier": "essential",
  "status": "brief_ready",
  "pre_topup_status": null,
  "confidence_score": 0.94,
  "product_brief": {
    "product_name": "GlowCraft Niacinamide Serum",
    "category": "d2c_beauty",
    "price_inr": 499,
    "key_features": ["10% Niacinamide", "1% Zinc", "Dermat-tested", "Cruelty-free"],
    "color_palette": ["#E8DFCF", "#8B7355"],
    "shape": "bottle_cylindrical"
  },
  "product_shape": "bottle_cylindrical",
  "isolated_png_url": "https://r2.adcreo.com/presigned/...isolated/product.png",
  "agent_motion_suggestion": 1,
  "chat_turns_used": 0,
  "export_retry_count": 0,
  "created_at": "2026-05-15T10:00:00Z",
  "updated_at": "2026-05-15T10:00:12Z"
}
```

### MOCK-03 · HD-2 · `brief_ready` · LOW confidence (<0.85)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "11111111-2222-3333-4444-555555555555",
  "plan_tier": "essential",
  "status": "brief_ready",
  "pre_topup_status": null,
  "confidence_score": 0.78,
  "product_brief": {
    "product_name": "Unknown beverage can",
    "category": "packaged_food",
    "price_inr": null,
    "key_features": ["carbonated"],
    "color_palette": ["#E63946"],
    "shape": "can_cylindrical"
  },
  "product_shape": "can_cylindrical",
  "isolated_png_url": "https://r2.adcreo.com/presigned/...isolated/product.png",
  "agent_motion_suggestion": null,
  "chat_turns_used": 0,
  "export_retry_count": 0
}
```

UI: red border + red headline + primary = `[↻ Re-upload]`, secondary = `[Continue Anyway]`.

### MOCK-04 · HD-3 · `scripts_ready` (Phase 2 complete · 3 framework-tagged scripts)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "11111111-2222-3333-4444-555555555555",
  "plan_tier": "essential",
  "status": "scripts_ready",
  "pre_topup_status": null,
  "confidence_score": 0.94,
  "product_brief": {
    "product_name": "GlowCraft Niacinamide Serum",
    "category": "d2c_beauty",
    "price_inr": 499,
    "key_features": ["10% Niacinamide", "1% Zinc", "Dermat-tested"]
  },
  "routed_frameworks": ["clinical_flex", "usage_ritual", "social_proof"],
  "routing_rationale": {
    "clinical_flex": "Strong ingredient proof (10% Niacinamide) supports claim-led angle.",
    "usage_ritual": "Morning skincare routine fits lifestyle framing.",
    "social_proof": "Established D2C beauty category benefits from trust signals."
  },
  "raw_scripts": [
    {
      "hook": "10% Niacinamide. Dermat-tested.",
      "body": "Visible reduction in dark spots within 4 weeks.",
      "cta": "Try GlowCraft today.",
      "full_text": "10% Niacinamide. Dermat-tested. Visible reduction in dark spots within 4 weeks. Try GlowCraft today.",
      "word_count": 19,
      "language_mix": "pure_english",
      "framework": "clinical_flex",
      "framework_angle": "logic",
      "framework_rationale": "Strong ingredient proof (10% Niacinamide).",
      "evidence_note": "Spec-backed: percentage + dermat-tested.",
      "suggested_tone": "authoritative",
      "critic_score": 82,
      "critic_rationale": "Direct evidence, clear benefit, strong CTA."
    },
    {
      "hook": "Your perfect morning glow ritual.",
      "body": "2 drops, 30 seconds, radiant skin all day.",
      "cta": "Start your ritual.",
      "full_text": "Your perfect morning glow ritual. 2 drops, 30 seconds, radiant skin all day. Start your ritual.",
      "word_count": 18,
      "language_mix": "pure_english",
      "framework": "usage_ritual",
      "framework_angle": "emotion",
      "framework_rationale": "Routine-driven product.",
      "evidence_note": "Usage-in-moment appeal.",
      "suggested_tone": "warm",
      "critic_score": 78,
      "critic_rationale": "Emotional anchor, clear usage."
    },
    {
      "hook": "Trusted by 50,000+ Indian women.",
      "body": "Join the GlowCraft community — visible results, real reviews.",
      "cta": "Shop bestseller.",
      "full_text": "Trusted by 50,000+ Indian women. Join the GlowCraft community — visible results, real reviews. Shop bestseller.",
      "word_count": 18,
      "language_mix": "pure_english",
      "framework": "social_proof",
      "framework_angle": "conversion",
      "framework_rationale": "Trust signals drive conversion.",
      "evidence_note": "Community-led proof.",
      "suggested_tone": "inviting",
      "critic_score": 75,
      "critic_rationale": "Decent trust signal, slightly weaker hook."
    }
  ],
  "critic_scores": {"clinical_flex": 82, "usage_ritual": 78, "social_proof": 75},
  "safe_scripts": "[same shape as raw_scripts — all 3 passed safety]",
  "selected_script_id": 1,
  "chat_turns_used": 0,
  "refined_script": null,
  "chat_history": [],
  "export_retry_count": 0
}
```

### MOCK-05 · HD-3 · `scripts_ready` · post-chat refinement (2 of 3 turns used)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "scripts_ready",
  "pre_topup_status": null,
  "selected_script_id": 1,
  "chat_turns_used": 2,
  "refined_script": {
    "hook": "10% Niacinamide. Dermat-approved.",
    "body": "Spots fade in 4 weeks — 50,000+ Indian women agree.",
    "cta": "Order on COD.",
    "full_text": "10% Niacinamide. Dermat-approved. Spots fade in 4 weeks — 50,000+ Indian women agree. Order on COD.",
    "word_count": 19,
    "language_mix": "hinglish",
    "framework": "clinical_flex",
    "framework_angle": "logic",
    "framework_rationale": "Strong ingredient proof (10% Niacinamide).",
    "evidence_note": "Spec-backed + social proof overlay.",
    "suggested_tone": "authoritative-warm"
  },
  "chat_history": [
    {"role": "user", "content": "Make it Hinglish and add COD mention", "timestamp": "2026-05-15T10:05:10Z"},
    {"role": "assistant", "content": "...", "timestamp": "2026-05-15T10:05:12Z"},
    {"role": "user", "content": "Add social proof too", "timestamp": "2026-05-15T10:06:01Z"},
    {"role": "assistant", "content": "...", "timestamp": "2026-05-15T10:06:03Z"}
  ]
}
```

UI: chat FAB shows badge `1` (1 turn left). Refined script tile is the active selection.

### MOCK-06 · HD-4 · `strategy_preview` (Essential, balance ≥1)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_tier": "essential",
  "status": "strategy_preview",
  "pre_topup_status": null,
  "selected_script_id": 1,
  "chat_turns_used": 2,
  "strategy_card": {
    "product_summary": {
      "name": "GlowCraft Niacinamide Serum",
      "category": "d2c_beauty",
      "confidence": 0.94
    },
    "script_summary": {
      "text": "10% Niacinamide. Dermat-approved. Spots fade in 4 weeks...",
      "score": 82,
      "framework": "clinical_flex",
      "framework_angle": "logic"
    },
    "frameworks_considered": {
      "selected": ["clinical_flex", "usage_ritual", "social_proof"],
      "rationale": {
        "clinical_flex": "Strong ingredient proof.",
        "usage_ritual": "Routine-driven product.",
        "social_proof": "Trust signals drive conversion."
      }
    },
    "voice": {"language": "hindi", "provider": "sarvam"},
    "motion": {"archetype_id": 1, "name": "orbit"},
    "environment": {"preset_id": 1, "name": "golden_hour"},
    "provider": {"primary": "fal_ai", "fallback": "minimax"},
    "cost_estimate": {"estimated_inr": 7.22, "ceiling_inr": 10.0},
    "compliance": {"sgi": true, "c2pa": true, "it_rules_2026": true},
    "chat_turns_used": 2,
    "chat_cost_inr": 0.16,

    "b_roll_plan": {
      "template": "T1",
      "hook": {
        "clip_id": "BR-HK-009",
        "archetype": "splash_warm",
        "duration_ms": 3000,
        "r2_url": "https://r2.adcreo.com/presigned/.../broll/hook/BR-HK-009.mp4",
        "role": "hook",
        "mood_energy": "active",
        "mood_temperature": "warm",
        "negative_space_score": 4,
        "seasonality_tags": [],
        "brand_tier_fit": ["mass", "premium", "luxury"]
      },
      "context": null,
      "cta": {
        "clip_id": "BR-CTA-014",
        "archetype": "soft_gradient",
        "duration_ms": 3000,
        "r2_url": "https://r2.adcreo.com/presigned/.../broll/cta_bg/BR-CTA-014.mp4",
        "role": "cta_bg",
        "mood_energy": "calm",
        "mood_temperature": "warm",
        "negative_space_score": 8,
        "seasonality_tags": [],
        "brand_tier_fit": ["mass", "premium", "luxury"]
      }
    },
    "structure_template": "T1",
    "active_season": null,
    "brand_color_primary": null,
    "b_roll_available": true
  },
  "_ui_hints": {
    "wallet_balance": 3,
    "primary_button_mode": "approve",
    "primary_button_label": "✓ Confirm & Use 1 Credit → Render"
  }
}
```

> **Note on the new strategy_card fields (v4-Δ1):**
> - `b_roll_plan` is JSONB-object-shaped `{template, hook, context, cta}` per TDD `[TDD-BROLL]-G/K` and `chk_b_roll_plan_shape`. `hook` is always non-null; `context` is non-null only for T3/T4; `cta` is non-null only for T1 (a clip) — T2/T3/T4/T5 emit `cta=null` and Worker-COMPOSE renders a text-card.
> - `structure_template` echoes the resolved template (T1..T5) so Worker-COMPOSE has a single source.
> - `active_season` is non-null only when `seasons.is_active = TRUE` AND `NOW()::DATE` is within `[active_from, active_to]`; T4 then takes precedence.
> - `brand_color_primary` is the user's brand hex (`#RRGGBB`) from `user_style_profiles`; `null` on cold-start (Worker-COMPOSE falls back to `#1A1A1A` neutral charcoal).
> - `b_roll_available` is `true` iff `b_roll_plan` is non-null AND `b_roll_plan.hook` is non-null. HD-5 reads this to show or hide the "Stitching B-roll…" stage row.

### MOCK-07 · HD-4 · `awaiting_funds` *(pre='strategy_preview')* — balance 0, Top-Up Drawer overlays HD-4

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_tier": "essential",
  "status": "awaiting_funds",
  "pre_topup_status": "strategy_preview",
  "selected_script_id": 1,
  "strategy_card": "<same shape and contents as MOCK-06 strategy_card>",
  "_ui_hints": {
    "wallet_balance": 0,
    "primary_button_mode": "top_up",
    "primary_button_label": "+ Add Credits to Render",
    "overlay": "TopUpDrawer",
    "resident_screen": "HD-4"
  }
}
```

UI: HD-4 renders dimmed underneath; `<TopUpDrawer/>` overlays (right on desktop, bottom on mobile). The `strategy_card` payload (including all v4-Δ1 fields: `b_roll_plan`, `structure_template`, `active_season`, `brand_color_primary`, `b_roll_available`) is identical to MOCK-06.

### MOCK-08 · HD-4 · Starter tier (primary button = Upgrade)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_tier": "starter",
  "status": "strategy_preview",
  "pre_topup_status": null,
  "strategy_card": "<same shape and contents as MOCK-06 strategy_card>",
  "_ui_hints": {
    "wallet_balance": 0,
    "primary_button_mode": "upgrade",
    "primary_button_label": "⚡ Upgrade to Render"
  }
}
```

Click → Plan Modal. If direct API call is made, server returns 403 ECM-006. The `strategy_card` payload (including all v4-Δ1 fields) is identical to MOCK-06.

### MOCK-09 · HD-5 · `rendering` (mid-render, 62% progress SSE snapshot)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "rendering",
  "pre_topup_status": null,
  "_sse_snapshot": {
    "type": "state_change",
    "state": "rendering",
    "progress_pct": 62,
    "eta_seconds": 45,
    "stages": [
      {"name": "tts", "status": "complete", "provider": "sarvam"},
      {"name": "i2v", "status": "running", "provider": "fal_ai"},
      {"name": "reflect", "status": "pending"},
      {"name": "broll", "status": "pending", "structure_template": "T1", "b_roll_available": true},
      {"name": "compose", "status": "pending"}
    ]
  }
}
```

> The `broll` stage is rendered in the UI only when `b_roll_available == true`. The `structure_template` field on the stage entry is informational so the client can label the row "Stitching B-roll (T1)" if desired; the row visibility itself depends only on `b_roll_available`.

### MOCK-10 · HD-5 · `failed_render` (DLQ caught, refund applied)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed_render",
  "pre_topup_status": null,
  "error_code": "ECM-004",
  "error_message": "Rendering failed after retries. Your credit has been refunded.",
  "dlq_dead_at": "2026-05-15T10:08:45Z",
  "dlq_original_task": "phase4_coordinator",
  "_ui_hints": {
    "buttons": ["[↻ Try Again]", "[← Back to Strategy]"],
    "resident_screen": "HD-5"
  }
}
```

### MOCK-11 · HD-6 · `preview_ready` (landing, declarations unsigned)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "preview_ready",
  "pre_topup_status": null,
  "preview_url": "https://r2.adcreo.com/presigned/.../compose/preview.mp4",
  "exports": null,
  "declaration_accepted": false,
  "declaration_accepted_at": null,
  "export_retry_count": 0,
  "_ui_hints": {
    "checkboxes_required": [1, 2, 3],
    "download_buttons_state": "locked",
    "resident_screen": "HD-6",
    "sub_state": "preview_ready"
  }
}
```

### MOCK-12 · HD-6 · `export_queued` (transient ~5–10s after declaration signed)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "export_queued",
  "pre_topup_status": null,
  "preview_url": "https://r2.adcreo.com/presigned/.../compose/preview.mp4",
  "declaration_accepted": true,
  "declaration_accepted_at": "2026-05-15T10:10:00Z",
  "exports": null,
  "export_retry_count": 0,
  "_ui_hints": {
    "download_buttons_state": "preparing",
    "resident_screen": "HD-6",
    "sub_state": "export_queued"
  }
}
```

### MOCK-13 · HD-6 · `export_ready` (terminal happy path)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "export_ready",
  "pre_topup_status": null,
  "preview_url": "https://r2.adcreo.com/presigned/.../compose/preview.mp4",
  "declaration_accepted": true,
  "declaration_accepted_at": "2026-05-15T10:10:00Z",
  "exports": {
    "square_url": "https://r2.adcreo.com/presigned/.../export/square_1x1.mp4",
    "vertical_url": "https://r2.adcreo.com/presigned/.../export/vertical_9x16.mp4",
    "c2pa_manifest_hash": "a1b2c3d4e5f6...",
    "finalized_at": "2026-05-15T10:10:35Z"
  },
  "export_retry_count": 0,
  "_ui_hints": {
    "download_buttons_state": "active",
    "show_style_memory_ack": true,
    "resident_screen": "HD-6",
    "sub_state": "export_ready"
  }
}
```

### MOCK-14 · HD-6 · `failed_export` · State 4a (fresh declaration ≤24h)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed_export",
  "pre_topup_status": null,
  "preview_url": "https://r2.adcreo.com/presigned/.../compose/preview.mp4",
  "declaration_accepted": true,
  "declaration_accepted_at": "2026-05-15T10:10:00Z",
  "exports": null,
  "export_retry_count": 1,
  "error_code": "ECM-005",
  "error_message": "Export processing failed. Your credit has been refunded.",
  "dlq_dead_at": "2026-05-15T10:11:22Z",
  "dlq_original_task": "worker_export",
  "_ui_hints": {
    "resident_screen": "HD-6",
    "sub_state": "failed_export_4a",
    "retry_button_enabled": true,
    "retry_attempts_display": "1 of 3",
    "wallet_balance": 2
  }
}
```

### MOCK-15 · HD-6 · `failed_export` · State 4b (stale declaration >24h — inline re-sign required)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed_export",
  "pre_topup_status": null,
  "preview_url": "https://r2.adcreo.com/presigned/.../compose/preview.mp4",
  "declaration_accepted": true,
  "declaration_accepted_at": "2026-05-14T09:00:00Z",
  "exports": null,
  "export_retry_count": 1,
  "error_code": "ECM-005",
  "dlq_original_task": "worker_export",
  "_ui_hints": {
    "resident_screen": "HD-6",
    "sub_state": "failed_export_4b",
    "checkboxes_required": [1, 2, 3],
    "retry_button_enabled": false,
    "retry_button_enables_when": "all_3_checkboxes_checked",
    "retry_attempts_display": "1 of 3",
    "stale_since": "2026-05-14T09:00:00Z",
    "next_retry_payload_shape": {"declarations": [true, true, true]}
  }
}
```

**Client-side derivation rule:** `sub_state == "failed_export_4b"` iff `status == "failed_export"` AND `(NOW() - declaration_accepted_at) > 24h`. This comparison is done on the client at hydration time; the server does NOT encode 4a/4b in `status`.

### MOCK-16 · HD-6 · `awaiting_funds` *(pre='failed_export')* — Top-Up Drawer overlays HD-6 after Step-7 lock-fail on retry

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "awaiting_funds",
  "pre_topup_status": "failed_export",
  "preview_url": "https://r2.adcreo.com/presigned/.../compose/preview.mp4",
  "declaration_accepted": true,
  "declaration_accepted_at": "2026-05-15T10:10:00Z",
  "exports": null,
  "export_retry_count": 1,
  "_ui_hints": {
    "wallet_balance": 0,
    "overlay": "TopUpDrawer",
    "resident_screen": "HD-6",
    "sub_state": "awaiting_funds_from_failed_export"
  }
}
```

UI: HD-6 `failed_export` state dimmed underneath (preview player still visible); TopUpDrawer overlays. On webhook `captured`, `status` restored to `failed_export` → drawer closes → user lands on State 4a (if declaration still fresh) or 4b (if now stale).

### MOCK-17 · HD-6 · ECM-019 terminal (retry exhausted)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed_export",
  "pre_topup_status": null,
  "preview_url": "https://r2.adcreo.com/presigned/.../compose/preview.mp4",
  "exports": null,
  "export_retry_count": 3,
  "error_code": "ECM-019",
  "error_message": "Export failed 3 times. All credits have been refunded.",
  "_ui_hints": {
    "retry_button_enabled": false,
    "buttons": ["[Contact Support]", "[Start New Generation]"],
    "resident_screen": "HD-6",
    "sub_state": "failed_export_terminal_exhausted"
  }
}
```

### MOCK-18 · HD-6 · ECM-018 terminal (R2 assets expired >30d)

```json
{
  "gen_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed_export",
  "pre_topup_status": null,
  "preview_url": null,
  "exports": null,
  "export_retry_count": 1,
  "error_code": "ECM-018",
  "error_message": "Your render is more than 30 days old. Please start a new generation.",
  "_ui_hints": {
    "retry_button_enabled": false,
    "buttons": ["[Start New Generation]"],
    "resident_screen": "HD-6",
    "sub_state": "failed_export_terminal_expired"
  }
}
```

### MOCK-19 · SSE event examples (keyed by `event` type)

```json
// event: state_change
{"type": "state_change", "gen_id": "550e8400-...", "state": "preview_ready", "pre_topup_status": null, "preview_url": "https://..."}

// event: chat_turn (after 5-stage chain commits)
{"type": "chat_turn", "gen_id": "550e8400-...", "turns_used": 2, "turns_remaining": 1}

// event: provider_fallback (toast only, no state change)
{"type": "provider_fallback", "gen_id": "550e8400-...", "from": "fal_ai", "to": "minimax", "capability": "i2v"}

// event: lock_failed (ATOMIC with state_change to awaiting_funds)
{"type": "state_change", "gen_id": "550e8400-...", "state": "awaiting_funds", "pre_topup_status": "strategy_preview"}

// event: render_failed (DLQ)
{"type": "render_failed", "gen_id": "550e8400-...", "state": "failed_render", "error_code": "ECM-004"}

// event: export_failed (DLQ)
{"type": "export_failed", "gen_id": "550e8400-...", "state": "failed_export", "error_code": "ECM-005"}

// event: topup_captured (webhook restoration)
{"type": "state_change", "gen_id": "550e8400-...", "state": "strategy_preview", "pre_topup_status": null, "source": "topup_captured"}
```

**Agent rule:** Mocks are the CI fixtures. Every component has a Storybook story per mock. Playwright E2E tests seed state by calling an internal `/api/test/seed-mock` route that accepts any mock JSON above.

---

## [PRD-ERROR-MAP] · Error-to-Component Mapping

Every ECM code routes to a specific React component. **Agent MUST use the Target Component column verbatim** — do not invent new error surfaces.

| ECM | Code | HTTP | Target UI Component | Component Path | Trigger | Dismissal |
|---|---|---|---|---|---|---|
| **ECM-001** | `failed_category` | SSE | `<EcmErrorCard/>` (full-screen re-entry) | `components/shared/EcmErrorCard.tsx` | Server SSE `state_change → failed_category` | `[Start Over]` creates fresh `gen_id` |
| **ECM-002** | `failed_compliance` | SSE | `<EcmErrorCard/>` (full-screen re-entry) | `components/shared/EcmErrorCard.tsx` | Server SSE | `[Start Over]` |
| **ECM-003** | `failed_safety` | SSE | `<Alert variant="destructive"/>` inline on HD-3 | `components/ui/alert.tsx` inside `HD3CreativeWorkspace.tsx` | Server SSE | Auto-retry 1×; else `[Back to Scripts]` button → GET rehydrate |
| **ECM-004** | `failed_render` | SSE | `<Alert variant="destructive"/>` + action buttons on HD-5 | `HD5RenderProgress.tsx` | DLQ branch A | `[↻ Try Again]` → `POST /approve-strategy` (fresh key); `[← Back to Strategy]` → `POST /edit-back` |
| **ECM-005** | `failed_export` | SSE | `<StateFailedExport4a/>` or `<StateFailedExport4b/>` (state-aware inline panel) | `components/hd/HD6Preview/StateFailedExport{4a,4b}.tsx` | DLQ branch B | `[↻ Retry Export · 1 Credit]` → `POST /retry-export` |
| **ECM-006** | `STARTER_RENDER_BLOCKED` | 403 | `<PlanModal/>` (Shadcn `Dialog`) | `components/shared/PlanModal.tsx` | Response to `POST /approve-strategy` or `/retry-export` | `[View Plans]` — links out; `[Close]` dismisses |
| **ECM-007** | `INSUFFICIENT_FUNDS` | 402 | `<TopUpDrawer/>` (Shadcn `Sheet`) | `components/shared/TopUpDrawer.tsx` | Response to `POST /approve-strategy` OR `/retry-export` Step 7 fail | `[Pay with UPI]` → `POST /wallet/topup`; drawer auto-closes on webhook `captured` |
| **ECM-008** | `CHAT_LIMIT_REACHED` | 429 | `<Alert variant="default"/>` inline within `<CoPilotChatSheet/>` | `components/hd/HD3CreativeWorkspace/CoPilotChatSheet.tsx` | Response to `POST /chat` | Input disabled; no action |
| **ECM-009** | `CHAT_CEILING_HIT` | 429 | `<Alert variant="warning"/>` inline within `<CoPilotChatSheet/>` | same | Response to `POST /chat` (Stage 2 reject) | Input disabled; no action |
| **ECM-010** | `CHAT_SAFETY_REJECT` | 422 | `<Alert variant="destructive"/>` inline within `<CoPilotChatSheet/>` | same | Response to `POST /chat` (Stage 5 reject) | Input re-enabled; counter preserved |
| **ECM-011** | `CHAT_COMPLIANCE_REJECT` | 400 | `<Alert variant="destructive"/>` inline within `<CoPilotChatSheet/>` | same | Response to `POST /chat` (Stage 1 reject) | Input cleared, re-enabled |
| **ECM-012** | `CROSS_TAB_CONFLICT` | 409 | `<ErrorToast/>` (sonner) | `components/shared/ErrorToast.tsx` | Response to any mutating call (`actlock` or cache mismatch) | Auto-dismiss 4s; `[Refresh]` button triggers `GET /gen/{id}` |
| **ECM-013** | `HYDRATION_FAILED` | — | `<app/error.tsx>` (full-screen route error boundary) | `app/[gen_id]/error.tsx` | Next.js error boundary catches GET failure | `[Refresh Page]` → `window.location.reload()` |
| **ECM-014** | `UPLOAD_TOO_LARGE` | 413 | Inline `<Label/>` error + red `<Input/>` state on HD-1 | `HD1Ingestion.tsx` | Response to `POST /generate` (multipart) | Error clears on next file selection |
| **ECM-015** | `FIRECRAWL_TIMEOUT` | SSE | Inline `<Alert/>` + tab auto-switch in `<HD1Ingestion/>` | `HD1Ingestion.tsx` | Server SSE during `extracting` | Upload tab auto-selected; `[Upload Image]` active |
| **ECM-016** | `C2PA_SIGN_FAILED` | DLQ | Same as ECM-005 (`<StateFailedExport4a/4b>`) | `components/hd/HD6Preview/StateFailedExport*.tsx` | DLQ branch B (C2PA returncode ≠ 0) | `[↻ Retry Export]` |
| **ECM-017** | `DECLARATION_INVALID` | 400 | Red flash on unchecked `<Checkbox/>` in `<DeclarationCheckboxes/>` | `components/hd/HD6Preview/DeclarationCheckboxes.tsx` | Response to `POST /declaration` | Flash 800ms; clears on check |
| **ECM-018** | `EXPORT_ASSETS_EXPIRED` | 410 | `<StateFailedExportTerminalExpired/>` inline card on HD-6 | `components/hd/HD6Preview/StateFailedExport*.tsx` (terminal variant) | Response to `POST /retry-export` Step 5 | Only CTA: `[Start New Generation]` → creates fresh `gen_id` |
| **ECM-019** | `EXPORT_RETRY_EXHAUSTED` | 410 | `<StateFailedExportTerminalExhausted/>` inline card on HD-6 | same (terminal variant) | Response to `POST /retry-export` Step 3 | `[Contact Support]`, `[Start New Generation]` |
| **ECM-020** | `DECLARATION_REFRESH_REQUIRED` | **428** | `<StateFailedExport4b/>` (inline checkbox bank above retry) | `components/hd/HD6Preview/StateFailedExport4b.tsx` | Response to `POST /retry-export` without `declarations` on stale state | On 3/3 check + re-click → `POST /retry-export {declarations:[true,true,true]}` |

**Full-screen vs inline decision rule (agent reference):**

| Criterion | Full-screen Error Boundary | Inline Alert / Panel | Toast | Drawer / Modal |
|---|---|---|---|---|
| Is the flow recoverable on the same screen? | ❌ NO (ECM-001, 002, 013) | ✅ YES (ECM-003..005, 014..020) | ✅ YES ephemeral (ECM-012) | ✅ YES action-required (ECM-006, 007) |
| Does user need to start over? | ✅ (fresh `gen_id`) | ❌ | ❌ | ❌ |
| Does it block all interaction until dismissed? | ✅ | ❌ | ❌ | ✅ (Drawer/Modal) |
| Can it be auto-dismissed? | ❌ | Sometimes | ✅ (4s) | ❌ |

---

## [PRD-FEATURES] · Feature Specifications

### [PRD-FEATURES-ACQ] · Acquisition & Onboarding

| F-ID | Feature | Constraints | Acceptance Criteria |
|---|---|---|---|
| **F-101** | Google 1-Tap Login | OAuth 2.0 · httpOnly JWT 30-day · `session_version` claim | ✅ 1-Tap popup · ✅ Auto-provisions DB · ✅ httpOnly · ✅ `sv` claim validated every request |
| **F-102** | Free Preview (Starter) | Phase 1–3 access · Max 3 gens · HD-4 render → 403 ECM-006 · `/retry-export` also defensively returns 403 | ✅ Requires login · ✅ Strategy Card shown · ✅ HD-4 render button shows "Upgrade to Render" · ✅ 3-gen limit · ✅ `/retry-export` returns 403 for Starter |
| **F-103** | Isolation Preview | BiRefNet (local, Apache 2.0) · Confidence · 15s Firecrawl · 10MB upload · 15MB scraped stream | ✅ <15s · ✅ Ambient confidence border (not pill) · ✅ >10MB → 413 (ECM-014) · ✅ Scraped >15MB → ECM-001 · ✅ Before/after toggle |

### [PRD-FEATURES-CREATIVE] · Creative Selection (Phase 2)

| F-ID | Feature | Constraints | Acceptance Criteria |
|---|---|---|---|
| **F-201** | Director's Chips | Enum chips · ★ from 3-tier chain · chip change → full regen + chat counter reset · Mobile sticky · Duration chip is fixed display (15s, non-editable in MVP) | ✅ Tappable · ✅ Chip change → COPY/CRITIC/SAFETY + chat reset · ✅ Mobile sticky top · ✅ Duration chip non-editable |
| **F-202** | Script Selection (Framework-Routed) | Worker-COPY routes to exactly **3 frameworks** from 12-catalog. Default trio = 1 logic + 1 emotion + 1 conversion. Each script tagged with framework + rationale + evidence + tone + CRITIC score. Pre-selected = top CRITIC scorer | ✅ Exactly 3 scripts, never 5 · ✅ Each tagged with framework enum value · ✅ Default trio satisfied unless evidence-weak fallback · ✅ Framework + score visible on card · ✅ `[HOOK][BODY][CTA]` preserved · ✅ NO manual text edit · ✅ Mobile collapse/expand · ✅ Selection rationale logged to `agent_traces.selection_reason` |
| **F-203** | Motion Selector | 5 archetypes · ★ from Style Memory or decision table · GIF preview on Strategy Card | ✅ GIF previews · ✅ ★ badge · ✅ Mobile tab-gated under "Style" |
| **F-204** | Environment Canvas | 8 presets · ★ from benefit + season + Style Memory | ✅ Seasonal auto-highlight |
| **F-207** | Co-Pilot Chat | **Canonical 5-stage middleware chain** (no step skipped/reordered): (1) L3 ComplianceGate.check_input (reject → ECM-011, no LLM, turn NOT counted) → (2) L5 CostGuard.pre_check (breach → ECM-009, no LLM, turn NOT counted) → (3) LLM via `gateway.route()` → (4) L5 CostGuard.record IMMEDIATELY (before safety — rejected-turn-leak fix) → (5) L3 OutputGuard.check_output (reject → ECM-010, turn NOT counted, COGS preserved). Max 3 turns · ~₹0.08/turn. Idempotency-Key per turn. Mobile Sheet FAB. Chips: Punchier/Hinglish/Diwali | ✅ <3s · ✅ Turn counter · ✅ Stage order: Compliance BEFORE CostGuard.pre_check; CostGuard.record BEFORE OutputGuard · ✅ CostGuard disables chat at ceiling · ✅ Compliance rejects injections (ECM-011, no spend) · ✅ Pre-check rejects budget breach (ECM-009, no spend) · ✅ CostGuard.record fires before OutputGuard · ✅ OutputGuard rejects unsafe (ECM-010, COGS kept, turn NOT counted) · ✅ Duplicate idempotency-key → cached 2xx · ✅ Mobile FAB dismisses cleanly |

### [PRD-FEATURES-INTENT] · Intent Gate (Phase 3)

| F-ID | Feature | Constraints | Acceptance Criteria |
|---|---|---|---|
| **F-701** | Strategy Card (HD-4) | Worker-STRATEGIST compiles (ZERO external APIs, CI-enforced). Resolves `active_season` (from `seasons` lookup) + `brand_tier` (from `user_style_profiles`) + `structure_template` (from `TEMPLATE_BY_CONTEXT` with T4 festive override) BEFORE invoking the deterministic role-first `BRollPlanner`. Persists `b_roll_plan` + `structure_template` + `active_season` + `broll_clip_usage` rows atomically in a single transaction. Server-driven 3-mode primary button. **4 `[Edit]` targets** (Product · Targeting · Script · Style) — NULL downstream incl. `b_roll_plan`, `structure_template`, `active_season`, `b_roll_performance_signal`. Top-Up Drawer overlay on `awaiting_funds`. Render click: Starter → 403 → Plan Modal; Paid bal≥1 → Lua lock → `funds_locked` → HD-5; Paid bal=0 → Lua fail → L2 writes `pre_topup_status='strategy_preview'` atomically → Top-Up Drawer overlays HD-4. COGS absent from UI. Surfaces `b_roll_plan` (object form `{template, hook, context, cta}`), `structure_template` (T1..T5), `active_season` (string or null), `brand_color_primary` (hex or null), `b_roll_available` (bool) | ✅ Always shown · ✅ <2s STRATEGIST · ✅ `[Edit]` routes NULL downstream incl. v4-Δ1 fields · ✅ Server-driven button per tier+balance · ✅ Top-Up Drawer overlays HD-4 · ✅ Post-topup webhook → status restored from `pre_topup_status='strategy_preview'` → drawer auto-closes · ✅ Multi-row webhook restoration · ✅ Trust row (SGI + C2PA + 5yr) visible · ✅ Motion GIF preview loops · ✅ Strategy Card payload includes `b_roll_plan` (object, not array), `structure_template`, `active_season`, `brand_color_primary`, `b_roll_available` · ✅ Plan + template + usage rows persisted in single transaction (atomic) · ✅ Worker-STRATEGIST makes ZERO external API calls (CI-enforced via `ci/strategist_sandbox_check.py`) |
| **F-702** | Style Memory | pgvector · active ≥3 prior exports · resettable · opt-in · never overrides explicit selection · stores `brand_tier` and `brand_color_primary` per user-category | ✅ 200ms timeout → fallback · ✅ `DELETE /api/style-memory` clears · ✅ ★ badge on pre-fills · ✅ `brand_tier` defaults to `'mass'` on cold-start · ✅ `brand_color_primary` nullable on cold-start |
| **F-703** | Fallback Reasoning | SSE during Phase-4 failures · DLQ messages include refund confirmation | ✅ In HD-5 <3s · ✅ DLQ SSE <5s · ✅ "Credit refunded" in DLQ message |
| **F-704** | Edit-Back Navigation (4 targets) | Validates backward from `strategy_preview` · NULLs downstream per `[PRD-HD4]` matrix (incl. v4-Δ1 fields) · `broll_clip_usage` rows NOT deleted | ✅ Valid targets only · ✅ Invalid → 400 · ✅ Downstream cleared (incl. `b_roll_plan`, `structure_template`, `active_season`, `b_roll_performance_signal`) · ✅ Post-edit status transitions correctly · ✅ Rotation history preserved |

### [PRD-FEATURES-PAYMENT] · Payment & Wallet

| F-ID | Feature | Constraints | Acceptance Criteria |
|---|---|---|---|
| **F-301** | UPI QR Payment + Webhook Restoration | Razorpay · UPI · `payment_status` FSM (topup only) · reorder-safe · **Origin-Preserving Restoration:** on `captured`, after wallet credit UPSERT, webhook runs `UPDATE generations SET status = pre_topup_status, pre_topup_status = NULL WHERE user_id=? AND status='awaiting_funds'`. Multi-row safe. Webhook NEVER hardcodes destination | ✅ QR <2s · ✅ Webhook → wallet credit · ✅ Duplicate `captured` → no double-credit (UNIQUE idx) · ✅ Reordered `failed → captured` → `captured` ignored · ✅ HD-4-origin user lands on HD-4 with Strategy Card intact · ✅ HD-6-origin user lands on HD-6 `failed_export` (not HD-4) · ✅ Multiple parked gens restored atomically · ✅ `pre_topup_status` NULLed after restore |
| **F-302** | Balance Widget | SSE on Redis DB0 · low-balance nudge · shows active lock count | ✅ Pulses red at 1 credit · ✅ Transaction history · ✅ Shows active locks per `gen_id` |
| **F-303** | Credit Lock / Consume / Refund (scoped) | Redis Lua per-gen lock fields. Postgres ledger row-first. Lock lifecycle: `locked → consumed` (on export success) or `locked → refunded` (on DLQ fail). **Partial UNIQUE INDEX on `(gen_id) WHERE status='locked'`** prevents double-active-lock. **On lock-fail, L2 writes `pre_topup_status` atomically** with `awaiting_funds` transition. `pre_topup_status` written by L2 ONLY, denied to workers | ✅ Full-render lock BEFORE Phase-4 dispatch (HD-4) · ✅ Export-only lock BEFORE retry dispatch (HD-6) · ✅ Auto-refund on ALL Phase-4 failures · ✅ Zero double-spend · ✅ Per-gen fields: concurrent gens safe · ✅ Double-lock → partial UNIQUE violation → 409 ECM-012 · ✅ `payment_status` NULL for lock/consume/refund rows · ✅ On Lua lock-fail from `/approve-strategy`: `pre_topup_status='strategy_preview'` + `status='awaiting_funds'` in one UPDATE · ✅ On Lua lock-fail from `/retry-export` Step 7: `pre_topup_status='failed_export'` + `status='awaiting_funds'` in one UPDATE · ✅ CHECK constraint enforces coupling |

### [PRD-FEATURES-PRODUCTION] · Generation & Export (Phase 4)

| F-ID | Feature | Constraints | Acceptance Criteria |
|---|---|---|---|
| **F-205** | Parallel I2V | 2 renders via `phase4_coordinator` `asyncio.gather` · REFLECT SSIM · DLQ | ✅ REFLECT picks best · ✅ Max 2 rounds · ✅ Any coordinator-child failure → single DLQ → refund |
| **F-401** | OutputGuard | Before TTS · on every chat response | ✅ Rejects PII/toxicity · ✅ Logged |
| **F-403** | Composition & LUT (Canonical 15s · Template-Branched) | **Canonical 15.000s smart-stitch.** Worker-COMPOSE branches per `structure_template` (T1..T5) per TDD `[TDD-BROLL]-C` and `[TDD-VIDEO]-B`. T1 = 3s hook clip + 9s I2V + 3s CTA clip. T2 = 2s hook + 11s I2V + 2s text-card CTA (FFmpeg `color=` + `drawtext`, brand-color gradient). T3 = 3s hook + 4s context + 5s I2V + 3s text-card CTA. T4 = 3s festive hook + 4s festive context + 5s I2V + 3s text-card CTA (festive accent). T5 = 2s hook + 10s I2V + 3s text-card CTA (urgency stack). Variable-arity `filter_complex` concat. Benefit-aware LUT applied to concatenated stream. SGI drawtext burned in. **No `-shortest` flag** — TTS padded/trimmed via `tpad`/`apad` to canonical 15.000s. Unknown template raises before R2 downloads (fail fast) | ✅ Final video duration = 15.000s ± 5ms · ✅ Correct LUT applied to full concat · ✅ SGI visible at all resolutions · ✅ TTS padded/trimmed to 15s · ✅ Template-branched segment graph · ✅ Text-card CTA for T2/T3/T4/T5 uses brand color (fallback `#1A1A1A`) · ✅ No `-shortest` flag in any FFmpeg invocation · ✅ Unknown template → `ComposeError` raised before R2 download |
| **F-404** | HD Export + C2PA (Post-Declaration, Original Path) | **Decoupled from `phase4_coordinator`**. Enqueued by L2 `POST /declaration` on DB1 phase4_workers. Reads `preview_url` from R2 + latest `audit_log` for `gen_id` (chronologically newest). Produces 2 formats (1080×1080, 1080×1920). **`c2patool` returncode explicitly checked**. Style Memory UPSERT on success (pgvector, 200ms; persists `brand_tier` + `brand_color_primary`). `wallet_transactions.status` transition `locked → consumed` on success | ✅ C2PA manifest in both formats · ✅ Returncode non-zero → DLQ → `failed_export` + refund · ✅ Style Memory UPSERT idempotent · ✅ Worker-EXPORT read-only on `preview_url` — never regenerates · ✅ Status transition `export_queued → export_ready` atomic · ✅ EXPORT reads newest `audit_log` row — identical for `/declaration` OR `/retry-export` Step-4 re-sign |
| **F-404a** | HD Export Retry (`/retry-export` · Atomic Re-Sign) | Second entry point for Worker-EXPORT · Enqueued by L2 `POST /gen/{id}/retry-export` on DB1 phase4_workers. **9-step validation** per `[PRD-HD6]`. **3-attempt cap** via `generations.export_retry_count`. **Fresh Lua lock required** each retry. Partial UNIQUE INDEX prevents double-active-lock. **Monotonic idempotency key** `{gen_id}:retry-export:{export_retry_count}`. **@idempotent cache scope** = 2xx only; 4xx (400/402/409/428) never cached. Worker-EXPORT identical code path whether invoked from `/declaration` or `/retry-export`. **Stale-declaration handling:** returns 428 ECM-020 when decl>24h and request omits `declarations`; when request includes `declarations:[1,1,1]`, Step 4 inserts fresh `audit_log` row atomically BEFORE Step 7 lock | ✅ Only transitions `failed_export → export_queued` (conditional UPDATE) · ✅ `export_retry_count` incremented atomically at dispatch · ✅ 3rd retry failure → ECM-019 terminal · ✅ R2 HEAD check catches expired → ECM-018 · ✅ Stale decl without acks → 428 ECM-020; state stays · ✅ Stale WITH acks → `audit_log` INSERT before lock; if lock fails, audit row preserved · ✅ Idempotency key per retry count: 2nd retry uses `:retry-export:2` not `:retry-export:1` · ✅ 4xx never cached · ✅ Balance 0 → `awaiting_funds` on HD-6 + `pre_topup_status='failed_export'` · ✅ Starter → 403 defensively · ✅ Retry economics: ~₹0.05–0.10 vs ~₹10 coordinator re-run |
| **F-405** | B-Roll Planner (Deterministic Role-First · Template-Driven) | **Architecture:** Atmospheric B-roll is selected by a deterministic SQL planner in Worker-STRATEGIST — **zero external API, zero LLM, zero vector search, zero embeddings** (CI-enforced via `ci/strategist_sandbox_check.py` extended to `app/broll/` and an ML-library import blocklist). Curated library of 25–30 hand-selected clips at launch, tagged at curation time. **Three roles** (`hook`, `context`, `cta_bg`) — a clip's role is fixed at curation and never overridden by selection logic. Tag dimensions: `role`, `mood_energy` (`calm`/`active`/`intense`), `mood_temperature` (`warm`/`cool`/`neutral`), `seasonality_tags` (e.g. `{diwali, wedding, monsoon, raksha_bandhan, new_year, holi}`), `brand_tier_fit` (`{mass, premium, luxury}`), `negative_space_score` (1–10, ≥7 required for `cta_bg`). **Five structural templates** T1..T5 (each exactly 15.000s — frozen `TEMPLATE_BY_CONTEXT` in `app/broll/templates.py`, CI-locked): T1 Bookended (hook+I2V+cta clip), T2 Product-Dominant (hook+I2V+text-card), T3 Problem-Story (hook+context+I2V+text-card), T4 Festive Moment (festive hook+festive context+I2V+text-card with festive accent), T5 Offer-Forward (hook+I2V+text-card urgency stack). Worker-STRATEGIST resolves `active_season` (from `seasons` lookup; non-null only when `is_active=TRUE` AND `NOW()::DATE BETWEEN active_from AND active_to`) + `brand_tier` (from `user_style_profiles`, default `'mass'`) + `structure_template` (from `TEMPLATE_BY_CONTEXT[(framework_angle, category_class)]`; T4 takes precedence when `active_season` is non-null). Plan persistence: a single `db.transaction()` UPDATEs `generations.b_roll_plan + structure_template + active_season` AND INSERTs `broll_clip_usage(user_id, clip_id, gen_id)` rows for every non-null clip in the plan. Plan output is a bounded JSONB object `{template, hook, context, cta}` enforced by `chk_b_roll_plan_shape`; `hook` is always non-null per `[TDD-BROLL]-K` invariant 5, `context` non-null only for T3/T4, `cta` is a clip only for T1 (T2/T3/T4/T5 emit `cta=null` and Worker-COMPOSE renders an FFmpeg text-card over a brand-color gradient — no extra deps). Selection algorithm is total-ordered (rotation-deprioritized via `broll_clip_usage` JOIN; `brand_tier_fit` filter; `seasonality_tags` filter for festive slots; mood mapping via `MOOD_BY_ANGLE`; deterministic tiebreak by `clip_id`). Tier-2 degradation (library coverage gap): force T1 + hook + text-card CTA (no context). Safety: every clip has `excludes_faces = excludes_hands = excludes_locations = TRUE`; every `cta_bg` clip has `negative_space_score >= 7` (DB CHECKs `chk_broll_safety` + `chk_cta_negative_space`). User-uploaded B-roll, performance-feedback loop, embeddings/CLIP, and brand-palette color filtering are out-of-scope for MVP (see `[PRD-NON-GOALS-FEATURE]`) | ✅ Planner makes zero external API calls (CI-enforced) · ✅ No LLM, no vector search, no embeddings imported under `app/broll/*` (CI blocklist) · ✅ Clip `role` is fixed at curation; selection never overrides · ✅ Plan output is `{template, hook, context, cta}` JSONB object — never a flat array · ✅ `chk_b_roll_plan_shape` constraint passes on every UPDATE · ✅ `hook` non-null in every successful plan · ✅ `context=null` for T1/T2/T5; non-null for T3/T4 · ✅ `cta` is a clip for T1; null for T2/T3/T4/T5 · ✅ Plan + `structure_template` + `active_season` + `broll_clip_usage` rows committed atomically (single transaction; partial write impossible) · ✅ `TEMPLATE_BY_CONTEXT` is the only template router (no LLM fallback) · ✅ T4 selected when `active_season` non-null, regardless of `(framework_angle, category_class)` mapping · ✅ Festive-slot selection filters by `seasonality_tags @> ARRAY[active_season]` · ✅ `brand_tier_fit @> ARRAY[brand_tier]` always satisfied for selected clips · ✅ Rotation: clips with most recent `broll_clip_usage.created_at` deprioritized · ✅ Deterministic tiebreak by `clip_id` (re-running planner with identical state yields identical plan) · ✅ Tier-2 degradation: T1 + hook clip + text-card CTA when library coverage gap detected · ✅ All clips pass `chk_broll_safety` (no faces/hands/locations) · ✅ All `cta_bg` clips pass `chk_cta_negative_space` (score ≥ 7) · ✅ `b_roll_available=true` iff plan non-null AND `plan.hook` non-null · ✅ HD-5 shows B-roll stage row only when `b_roll_available=true` |

### [PRD-FEATURES-COMPLIANCE] · Compliance & Safety

| F-ID | Feature | Constraints | Acceptance Criteria |
|---|---|---|---|
| **F-501** | SGI Watermark | FFmpeg drawtext · burned-in · ≥ 24pt · "AI-Generated" + IT Rules 2026 §5 watermark | ✅ Visible on every export · ✅ Cannot be removed without re-encoding |
| **F-503** | C2PA Manifest | `c2patool` v0.21+ Linux binary · provisioned at L1 build (Dockerfile RUN step) · returncode explicitly checked · local verification only | ✅ Manifest embedded in every export · ✅ Returncode non-zero → DLQ ECM-016 · ✅ External (Adobe) verification path forbidden in CI and runtime · ✅ Linux binary present in build image (Dockerfile step) |
| **F-505** | 3-Checkbox Declaration (Independent) | Independent legal assertions · captured atomically with state transition + lock + ARQ dispatch · `audit_log` immutable, partitioned, 5-year retention · 24h freshness re-capture via 428 ECM-020 atomic chain | ✅ 3/3 required (else ECM-017) · ✅ IP/UA/SHA256 captured · ✅ Each declaration stored as separate column · ✅ Stale (>24h) on retry → 428 ECM-020 inline re-sign · ✅ Re-sign atomic with retry dispatch · ✅ `audit_log` rows never deleted |
| **F-506** | Grievance Officer Page | DPDP Act compliant · `/grievance` outside FSM · peripheral route · accessible via footer | ✅ Public route · ✅ Outside HD-1..HD-6 · ✅ Contact form + officer details · ✅ Submission timestamped to `audit_log` |

#### Verification Mechanism (MVP Constraint)

All C2PA verification is performed using the local `c2patool --verify` command.

- The Linux `c2patool` binary is provisioned at L1 image build time (Dockerfile `RUN` step).
- All verification — in CI gates, in runtime self-checks, and in any future tooling — MUST use the local binary.
- External verification services (Adobe VerifyContentCredentials and equivalent) are strictly forbidden.
- This eliminates Adobe SDK dependency and external network calls for verification.
- This decision is reflected in:
  - TDD V5 ([TDD-WORKERS]-I and [TDD-VIDEO]-C)
  - BEF V2 (Conflict C5 + L1 + L4)
  - M6 in `[PRD-RELEASE-MVP]`

### [PRD-FEATURES-RETENTION] · Retention & Style Memory

| F-ID | Feature | Constraints | Acceptance Criteria |
|---|---|---|---|
| **F-401a** | Source Asset Retention | 7d unpaid · 30d paid · Lifecycle Policy on R2 bucket | ✅ Auto-purge · ✅ DB row preserved (analytics) |
| **F-401b** | Finalized Export Retention | Exactly 5 years per IT Rules 2026 · separate R2 bucket lifecycle | ✅ Audit-discoverable for full 5y · ✅ Auto-purge at year 5 |
| **F-401c** | Takedown Pipeline | <60min purge SLA · DB + R2 hard-delete · grievance + DPDP triggers | ✅ Triggered async on moderation event · ✅ Completion logged to `audit_log` · ✅ SLA monitored via Grafana |

### [PRD-FEATURES-INFRA] · Platform & Infrastructure

| F-ID | Feature | Constraints | Acceptance Criteria |
|---|---|---|---|
| **F-601** | L1 API Gateway | FastAPI · Pydantic v2 · uvicorn workers · health checks · Linux base image with `c2patool` binary | ✅ Health/ready endpoints · ✅ `c2patool` binary present in image |
| **F-602** | L2 Service Gateway | Tier check · idempotency middleware · `@idempotent` decorator + `actlock` fence · auth · CSRF | ✅ `pre_topup_status` written by L2 only (workers DENIED) |
| **F-603** | L3 ComplianceGate | InputScrubber sync · ModelGuard async · regex + PII detection · prompt-injection patterns | ✅ Phase 1 sync gate · ✅ Phase 2/3 async gate |
| **F-604** | L4 ModelGateway | Circuit-breaker (CLOSED/OPEN/HALF_OPEN) · health scoring · provider fallback · capability routing | ✅ I2V Fal.ai → Minimax fallback · ✅ TTS Sarvam → ElevenLabs fallback · ✅ Provider-fallback SSE toast |
| **F-605** | L5 CostGuard | Per-gen COGS ledger · `pre_check` before LLM dispatch · `record` immediately on LLM return · ceilings ₹2/₹10/₹14 by tier | ✅ Ceiling breach → ECM-009 · ✅ Record-before-safety (rejected-turn-leak fix) |
| **F-606** | L6 Worker Layer | ARQ on Redis DB1 phase4_workers · async coroutines · DLQ on death · returncode-checked subprocess calls (`c2patool`, `ffmpeg`) | ✅ DLQ dual-branch by `job.function_name` · ✅ Refund auto-applied on Phase-4 deaths |
| **F-607** | L7 Postgres | Neon Postgres 17 · pgvector 1536-dim · `text-embedding-3-small` for Style Memory · partitioned `audit_log` · raw-SQL migrations via `ci/run_migrations.py` (no Alembic) | ✅ FSM ENUM frozen · ✅ `chk_pre_topup_coupling` enforced · ✅ Partial UNIQUE INDEXes on `wallet_transactions` · ✅ Migrations CI-validated |
| **F-608** | Redis Topology | 6 logical DBs: 0 wallet · 1 phase4_workers · 2 idempotency · 3 SSE · 4 actlock · 5 cache | ✅ Lua atomic scripts on DB0 · ✅ ARQ on DB1 · ✅ Idempotency keyspace TTL 5min |
| **F-609** | R2 Storage | Cloudflare R2 buckets: `adcreo-assets` (sources, 30d), `adcreo-previews` (10min presigned), `adcreo-exports` (5yr) · lifecycle policies enforce auto-purge | ✅ Presigned URLs · ✅ Lifecycle policy verifiable via R2 API |
| **F-610** | Observability | Grafana + Loki + Prometheus · Grafana alerts wired (Razorpay webhook lag, DLQ depth, takedown SLA breach, COGS ceiling burn-rate) · OpenTelemetry traces | ✅ Grafana alerts route to email/Slack only · ✅ No PagerDuty integration (intentionally excluded in MVP) · ✅ Trace IDs on all logs |
| **F-611** | CI Gates | All gates non-negotiable: `validate_state_machine.py` · `chk_pre_topup_coupling` migration test · `strategist_sandbox_check.py` (zero-external-API, ML-library blocklist, extended to `app/broll/`) · `chk_b_roll_plan_shape` migration test · `chk_broll_safety` migration test · `chk_cta_negative_space` migration test · `templates_freeze_check.py` (T1..T5 immutable) · `localstorage_prefix_lint.py` (`aw_` prefix preserved) · `ui_tokens_lint.py` · `c2patool` returncode test · Playwright E2E covering MOCK-01..MOCK-19 | ✅ All gates green before merge · ✅ Templates freeze + B-roll sandbox checks block any new external API or LLM in `app/broll/` |
| **F-612** | DLQ Dual-Branch Recovery | DLQ inspects `job.function_name`: `phase4_coordinator` → refund + `failed_render` (HD-5 recovery); `worker_export` → refund + `failed_export` (HD-6 recovery, preserves Phase-4 assets) · Idempotent refund (skips if `wallet_transactions.status` already `refunded`) | ✅ Branch correctly per task name · ✅ `failed_render` routes to HD-5 inline; `failed_export` routes to HD-6 inline · ✅ Double-DLQ → idempotent (no double refund) |

#### Observability Stack (MVP)

- Grafana + Loki + Prometheus is the MVP observability stack.
- Grafana alerts are wired for: Razorpay webhook lag, DLQ depth, takedown SLA breach, COGS ceiling burn-rate.
- Alerts route to email/Slack only.
- **PagerDuty is intentionally excluded in MVP.**
  - Reduces operational overhead at MVP scale.
  - Reduces external dependencies.
  - Will be reassessed post-MVP based on incident volume.
- Decision is locked in TDD V5 §19.7 and BEF V2 (Conflict C7 + L6).

---

## [PRD-SPRINTS] · Sprint Roadmap (Informational)

> **Non-normative — calendar is historical reference.** Current build state, current sprint, and current execution scope live in **BEF V2 §16.13**. All contractual obligations are in the feature tables above; the sprint table below documents the original scoping rather than dictating current work.

| Sprint | Window | Focus | Notes |
|---|---|---|---|
| Sprint 0 | Pre-build | Audit hardening (PRD V3 → V4, TDD V5, BEF V2) · v4-Δ1 reconciliation | Document-only |
| Sprint 1 | Build kickoff | Auth · L1/L2/L3 · HD-1/HD-2 · Postgres FSM · Redis topology · Migrations runner (`ci/run_migrations.py`) | Foundation |
| Sprint 2 | Build core | Worker pipeline (EXTRACT → COPY → CRITIC → SAFETY → STRATEGIST → COMPOSE → EXPORT) · B-Roll Planner v4-Δ1 (deterministic role-first, T1..T5 templates) · Atomic Re-Sign chain (ECM-020) · DLQ dual-branch · Payment FSM + webhook restoration | Closes happy path + HD-6 inline recovery |
| Sprint 3 | Build polish | B-Roll Planner + Templates · Tier-2/3/4 Degradation · Style Memory pgvector · Takedown pipeline · CI gate suite | Closes flywheel + compliance |
| Sprint 4 | Pre-launch | Beta hardening · observability dashboards · E2E Playwright pass · final compliance audit | Launch readiness |

---

## [PRD-AC] · Acceptance Criteria (Per Screen + Global)

### [PRD-AC-1] · HD-1 Ingestion

| F-PRD-AC-ID | Criterion | Verification |
|---|---|---|
| **F-PRD-AC-1.1** | URL submit transitions `queued → extracting` within 1s | E2E + SSE assertion |
| **F-PRD-AC-1.2** | Phase 1 completes in <15s (95th percentile) | Grafana SLO |
| **F-PRD-AC-1.3** | Non-GreenZone product → `failed_category` + ECM-001 within 5s | E2E |
| **F-PRD-AC-1.4** | Upload >10MB → 413 ECM-014 inline | E2E |

### [PRD-AC-2] · HD-2 Isolation

| F-PRD-AC-ID | Criterion | Verification |
|---|---|---|
| **F-PRD-AC-2.1** | Confidence border color matches score thresholds (0.90/0.85) | Visual regression test |
| **F-PRD-AC-2.2** | Confidence flagging never skips HD-3 | E2E + invariant assertion |
| **F-PRD-AC-2.3** | Before/after toggle works on desktop + mobile | Playwright |

### [PRD-AC-3] · HD-3 Creative Workspace

| F-PRD-AC-ID | Criterion | Verification |
|---|---|---|
| **F-PRD-AC-3.1** | Exactly 3 framework-tagged scripts shown (never 5) | E2E + DB CHECK |
| **F-PRD-AC-3.2** | Top critic-scored script pre-selected on landing | E2E |
| **F-PRD-AC-3.3** | Chat turn cap = 3 enforced via DB CHECK + FSM | DB integration test |
| **F-PRD-AC-3.4** | 5-stage middleware chain order preserved (Compliance → Pre-check → LLM → Record → OutputGuard) | Unit + integration |
| **F-PRD-AC-3.5** | OutputGuard rejection preserves COGS but does NOT count turn | Integration test |
| **F-PRD-AC-3.6** | Chip change NULLs all downstream (incl. `b_roll_plan`, `structure_template`, `active_season`, `b_roll_performance_signal`) and resets chat counter | E2E + DB assertion |
| **F-PRD-AC-3.7** | Mobile chat behind FAB; tab switch client-only (no API call) | Playwright mobile |
| **F-PRD-AC-3.8** | Duration chip is non-editable in MVP (display-only 15s) | Playwright |

### [PRD-AC-4] · HD-4 Strategy Card

| F-PRD-AC-ID | Criterion | Verification |
|---|---|---|
| **F-PRD-AC-4.1** | Strategy Card always shown (mandatory gate; no skip) | E2E |
| **F-PRD-AC-4.2** | 4 `[Edit]` targets route correctly + NULL downstream (incl. v4-Δ1 fields: `b_roll_plan`, `structure_template`, `active_season`, `b_roll_performance_signal`); `broll_clip_usage` rows preserved | E2E + DB assertion |
| **F-PRD-AC-4.3** | Server-driven primary button (3 modes by tier+balance) | Integration test |
| **F-PRD-AC-4.4** | Starter render → 403 ECM-006 → Plan Modal | E2E |
| **F-PRD-AC-4.5** | Balance 0 → `awaiting_funds` *(pre='strategy_preview')* + Top-Up Drawer overlay | E2E |
| **F-PRD-AC-4.6** | Lua lock-fail writes `pre_topup_status` atomically with `awaiting_funds` transition | DB CHECK + integration |
| **F-PRD-AC-4.7** | Strategy Card payload includes `b_roll_plan` (object form), `structure_template`, `active_season`, `brand_color_primary`, `b_roll_available` | Contract test (JSON schema) |
| **F-PRD-AC-4.8** | Worker-STRATEGIST persists `b_roll_plan` + `structure_template` + `active_season` + `broll_clip_usage` rows in single transaction | DB integration test |
| **F-PRD-AC-4.9** | Worker-STRATEGIST makes zero external API calls (CI sandbox check) | CI gate |
| **F-PRD-AC-4.10** | "Template" + "Festive accent" rows visible in Strategy Card UI | Visual regression |

### [PRD-AC-5] · HD-5 Render Progress

| F-PRD-AC-ID | Criterion | Verification |
|---|---|---|
| **F-PRD-AC-5.1** | Phase-4 ≤180s (95th percentile) | Grafana SLO |
| **F-PRD-AC-5.2** | Provider-fallback toast appears within 3s of CB OPEN | E2E |
| **F-PRD-AC-5.3** | DLQ-caught Phase-4 failure → `failed_render` + refund within 5s | E2E |
| **F-PRD-AC-5.4** | `[↻ Try Again]` on `failed_render` re-locks credit (legitimate Phase-4 re-run) | E2E + ledger assertion |
| **F-PRD-AC-5.5** | `phase4_coordinator` stops at `preview_ready` (does NOT enqueue Worker-EXPORT) | Integration test |
| **F-PRD-AC-5.6** | Final video duration = 15.000s ± 5ms (no `-shortest`) | Codec test on output |
| **F-PRD-AC-5.7** | Worker-COMPOSE branches per `structure_template` (T1..T5); unknown template raises before R2 download | Unit test |
| **F-PRD-AC-5.8** | B-roll stage row shown in HD-5 only when `b_roll_available=true` | Playwright |
| **F-PRD-AC-5.9** | Text-card CTA (T2/T3/T4/T5) uses `brand_color_primary` or `#1A1A1A` fallback | Visual regression |

### [PRD-AC-6] · HD-6 Preview + Export

| F-PRD-AC-ID | Criterion | Verification |
|---|---|---|
| **F-PRD-AC-6.1** | Single state-aware component handles all 5 states + 4a/4b split | Component test |
| **F-PRD-AC-6.2** | `failed_export` stays on HD-6 (never routes to HD-4) | E2E |
| **F-PRD-AC-6.3** | `/retry-export` 9-step chain enforced in order; 428 ECM-020 returned when decl stale + no `declarations` | Integration test |
| **F-PRD-AC-6.4** | Stale decl with `declarations:[1,1,1]` → fresh `audit_log` row inserted before lock | DB assertion |
| **F-PRD-AC-6.5** | `export_retry_count` capped at 3; 4th attempt → 410 ECM-019 | E2E |
| **F-PRD-AC-6.6** | R2 HEAD on `preview_url` 404 → 410 ECM-018 terminal | E2E |
| **F-PRD-AC-6.7** | HD-6 retry lock-fail → `awaiting_funds` *(pre='failed_export')* + Top-Up Drawer overlays HD-6 | E2E |
| **F-PRD-AC-6.8** | Webhook captures restore HD-6 user to `failed_export` (not `strategy_preview`) | Webhook integration test |
| **F-PRD-AC-6.9** | Idempotency key per retry includes `export_retry_count` — no cache collision across retries | Unit test |
| **F-PRD-AC-6.10** | 4xx (400/402/409/428) NEVER cached by `@idempotent`; client drops key on 4xx | Integration test |
| **F-PRD-AC-6.11** | C2PA manifest validates locally via `c2patool --verify` (no external Adobe path) | CI gate |
| **F-PRD-AC-6.12** | 3 declaration checkboxes are independent legal assertions; each stored as separate column | DB schema test |

### [PRD-AC-GLOBAL] · Global Invariants

| G-ID | Criterion | Verification |
|---|---|---|
| **G1** | Every `[PRD-*]` anchor present in source · CI grep enforces | CI gate |
| **G2** | Every Feature ID, ECM code, AC ID, and JobStatus ENUM value referenced ≥1 in code and tests | CI cross-ref |
| **G3** | 6-screen linear flow preserved — no screen-skipping based on confidence | E2E invariant test |
| **G4** | 22-state FSM ENUM matches Postgres ENUM; `chk_pre_topup_coupling` enforced | Schema test |
| **G5** | All FFmpeg worker invocations forbid `-shortest`; all `c2patool` calls explicitly check returncode | grep + CI gate |

---

## [PRD-NON-GOALS] · Non-Goals (MVP Scope Boundary)

### [PRD-NON-GOALS-VISUAL]

- No avatars, lip-sync, talking heads.
- No human spokespersons.
- No generic stock product footage in place of user's actual product.

### [PRD-NON-GOALS-INTERACTIVE]

- No real-time collaborative editing.
- No video timeline editor with manual scrubbing.
- No user-customizable LUT/grading curves.
- No public sharing / social-platform direct-post (export only).

### [PRD-NON-GOALS-LANGUAGE]

- No machine-translated TTS outputs (Sarvam/ElevenLabs native voices only).
- No support for languages outside `SupportedTTSLanguages` enum.

### [PRD-NON-GOALS-MODEL]

- No user-visible model selection.
- No "advanced mode" with raw prompt control.
- No model fine-tuning surfaced to user.

### [PRD-NON-GOALS-PRICING]

- No subscription model (one-time validity-bound packs only).
- No team / multi-seat billing.
- No annual plans.
- No usage-based metered billing.

### [PRD-NON-GOALS-FEATURE]

- No video timeline editing post-render.
- No GIF / animated-thumbnail export.
- No batch generation (one URL → one ad).
- No multi-product montage in single ad.
- No A/B testing harness inside the product (export → external tooling).
- **No user-uploaded B-roll in MVP** (curated 25–30 clip library is the entire universe).
- **No B-roll performance-feedback loop in MVP** (`b_roll_performance_signal` column reserved but unpopulated).
- **No CLIP/embedding-based B-roll selection in MVP** (deterministic SQL planner only; ML-library import blocklist enforced under `app/broll/*`).
- **No brand-palette color-similarity filtering of B-roll in MVP** (`brand_color_primary` is used by Worker-COMPOSE for text-card gradients only).
- **No variable duration selection in MVP** (canonical 15.000s only; 5s/10s deferred post-MVP).
- No PagerDuty integration in MVP (Grafana alerts → email/Slack only).

---

## [PRD-RELEASE] · Release Criteria

### [PRD-RELEASE-MVP] · MVP Launch Gate

All 10 must be green for MVP launch.

| Gate | Criterion | Verification |
|---|---|---|
| **M1** | All AC-1..AC-6 + G1..G5 pass | CI report |
| **M2** | All 22 FSM ENUM values reachable + correctly projected | E2E matrix coverage |
| **M3** | All 20 ECM error codes have working recovery path | E2E error-injection suite |
| **M4** | 100% of payment FSM rules verified (idempotency, reorder, restoration) | Webhook integration suite |
| **M5** | Atomic Re-Sign chain (ECM-020) verified end-to-end (stale decl → 428 → re-sign + retry atomic) | E2E |
| **M6** | C2PA manifest validates locally via `c2patool --verify`. External verification (Adobe and equivalent) forbidden in CI and runtime. | CI gate + runtime test |
| **M7** | Phase-4 SLA <180s @ p95 under expected load | Grafana SLO |
| **M8** | Takedown pipeline <60min @ p95 | Async job timing test |
| **M9** | Grafana alerts wired per TDD §19.7 (Razorpay webhook lag, DLQ depth, takedown SLA, COGS ceiling burn-rate). Email/Slack routing only — no PagerDuty. | Alert manifest review |
| **M10** | B-Roll Planner CI gates green: `chk_b_roll_plan_shape`, `chk_broll_safety`, `chk_cta_negative_space`, `templates_freeze_check.py`, `strategist_sandbox_check.py` extended to `app/broll/` | CI gate suite |

### [PRD-RELEASE-BETA] · Beta → GA Promotion Criteria

**Beta entry (B1..B5):**

| Gate | Criterion |
|---|---|
| **B1** | All MVP gates M1..M10 green for 7 consecutive days |
| **B2** | Zero P0 incidents in past 7 days |
| **B3** | Wallet refund rate <2% of all renders |
| **B4** | Takedown SLA <60min @ p95 sustained 7 days |
| **B5** | CostGuard ceiling breaches <0.5% of all generations |

**Beta exit / GA criteria (E1..E6):**

| Gate | Criterion |
|---|---|
| **E1** | 500+ paid generations completed end-to-end |
| **E2** | Compliance audit (external) signed off |
| **E3** | All P1 incidents resolved or documented as accepted |
| **E4** | Recovery paths exercised for ≥80% of ECM codes in production |
| **E5** | Style Memory adoption rate ≥30% of repeat users |
| **E6** | B-Roll Planner observed in production for all 5 templates (T1..T5) across paid generations |

---

## [PRD-UX-FREEZE] · UX Freeze Rules

These are CI-enforced. Any PR that violates a freeze rule is auto-rejected.

### [PRD-UX-FREEZE-Z1] · 6-Screen Flow Freeze

- Exactly 6 screens: `HD-1`, `HD-2`, `HD-3`, `HD-4`, `HD-5`, `HD-6`.
- No additional screens may be added.
- No screen may be removed.
- Strictly linear navigation. Confidence Flagging adapts UI, not flow.
- Peripheral route `/grievance` is allowed (DPDP / IT Rules 2026 requirement); never enters FSM.

### [PRD-UX-FREEZE-Z2] · FSM ENUM Freeze

- 22 `JobStatus` ENUM values frozen. No additions, no removals, no renames.
- `pre_topup_status` column frozen as `job_status NULL` with `chk_pre_topup_coupling`.
- Postgres ENUM and TypeScript union always in sync (`validate_state_machine.py`).

### [PRD-UX-FREEZE-Z3] · Component Identity Freeze

- HD-6 is exactly ONE state-aware component (`HD6Preview.tsx`), not five separate routes.
- HD-3 mobile uses Shadcn `Sheet` FAB for chat; desktop uses 4-zone workspace.
- HD-4 Strategy Card layout zones are frozen: Product · Targeting · Script · Style · **Template · Festive accent (v4-Δ1)** · Voice · Duration · Compliance Trust Row · Cost row.
- Top-Up Drawer is the only overlay used for `awaiting_funds`; Plan Modal is the only overlay used for Starter render blocking.

### [PRD-UX-FREEZE-Z4] · Server-Driven Primary CTA Freeze

- HD-4 primary button has exactly 3 modes (`approve` / `top_up` / `upgrade`).
- Mode is server-decided in `GET /gen/{id}` response (`_ui_hints.primary_button_mode`).
- Client never decides button label or action heuristically.

### [PRD-UX-FREEZE-Z5] · Error Copy + ECM Freeze

- 20 ECM codes (`ECM-001..ECM-020`) frozen. No additions, no removals, no renames.
- Error copy strings frozen in `shared/types/ecm_codes.ts` and `[PRD-ERROR-COPY]`.
- Recovery actions frozen per `[PRD-ERROR-MATRIX]`.

### [PRD-UX-FREEZE-Z6] · Linearity Freeze

- No screen may dynamically skip another based on AI confidence or any other signal.
- Confidence is visual only.

### [PRD-UX-FREEZE-Z7] · Idempotency + Cache Scope Freeze

- All mutating endpoints use UUIDv4 Idempotency-Key + server `actlock`.
- `@idempotent` decorator caches ONLY 2xx terminal responses.
- 4xx (400/402/409/428) and 5xx NEVER cached.
- `/retry-export` idempotency key includes `export_retry_count` (monotonic).
- `aw_` `localStorage` prefix is frozen — never renamed (CI gate `localstorage_prefix_lint.py`).

### [PRD-UX-FREEZE-Z8] · FFmpeg `-shortest` Ban

- No FFmpeg invocation in any worker may include `-shortest`.
- Padding/trimming is explicit via `tpad` / `apad` to canonical 15.000s.
- CI grep enforces this across `app/workers/**` and `app/broll/**`.

### [PRD-UX-FREEZE-Z9] · B-Roll Templates + Planner Freeze (v4-Δ1)

- `app/broll/templates.py` is frozen. `T1..T5` structural templates, `TEMPLATE_BY_CONTEXT`, `MOOD_BY_ANGLE`, `CATEGORY_CLASS` are immutable in MVP.
- CI gate `templates_freeze_check.py` blocks any modification to these constants.
- B-roll plan output shape `{template, hook, context, cta}` is enforced by `chk_b_roll_plan_shape`.
- `strategist_sandbox_check.py` is extended to `app/broll/*` and includes an ML-library import blocklist (no `torch`, `tensorflow`, `transformers`, `clip`, `sentence_transformers`, `openai`, `anthropic`, `httpx` / `requests` to external hosts inside `app/broll/*`).
- DB CHECK constraints `chk_broll_safety` and `chk_cta_negative_space` are frozen.

---

*Adcreo PRD Locked (Version 4) · CONFIDENTIAL · GOLDEN RC · Aligned to TDD V5 · Aligned to BEF V2*
