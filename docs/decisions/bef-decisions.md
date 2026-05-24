# BEF Decisions Log

> **Purpose:** Durable record of every authority-stack conflict resolution per BEF §1.4 and §3.7 step 4. Every divergence between PRD V4, TDD V5, and BEF V2 that requires Founder or Architect adjudication lands here so future agent sessions inherit the precedent.
>
> **Format per entry:** Date · Axis (A1/A2/A3) · Surface · Resolution · References · Decided by.

---

## 2026-05-20 · D-001 · docs/ restructure + GAP-15 TDD residual cleanup

**Axis:** A3 (execution sequencing) for the restructure; A1+A2 (product/impl) for the TDD edits.

**Surface:**
- Root-level legacy docs `MVP_PRD_(AdvertWise).md`, `MVP_TDD_(AdvertWise).md`, `MVP_BEF_(AdvertWise).md` were V3-era old-brand artifacts coexisting with the active SSOT (Adcreo V4/V5/V2) in Founder's staging folder.
- TDD V5 staging copy contained 11 residual `AdvertWise` references that contradicted BEF V2 V2 CHANGELOG (R2 bucket rename, scaffold rename, brand replacement).
- GAP-15 (PRD V3→V4 sync) was tracked open in BEF §16.7.

**Resolution:**
- Created annotated tag `baseline/1fd3110-pre-docs-restructure` at HEAD `1fd3110` as the shallow rollback anchor. Prior tag `baseline/0d9cde7-pre-restructure` at `0d9cde7` preserved as deeper rollback point.
- Scaffolded `docs/active/`, `docs/archive/`, `docs/decisions/`, `docs/build-logs/gates/`.
- Archived the 3 legacy V3 root docs into `docs/archive/` with original filenames preserved (literal historical record).
- Placed real Adcreo V4/V5/V2 SSOT docs into `docs/active/` as the new canonical contract surface.
- Applied 11 surgical edits to `docs/active/Adcreo_launch_TDD_V5.md`:
  - R2 bucket: `advertwise-assets` → `adcreo-assets` (per BEF §11.8 V2 CHANGELOG entry 25).
  - Scaffold root: `advertwise/` → `adcreo/` (per BEF V2 V2 CHANGELOG document-wide rename).
  - 3 LLM prompt templates: brand string updated (runtime-sent text).
  - 2 product-narrative sections: brand string updated.
  - 1 tooling path: `advertwise-tools` → `adcreo-tools`.
  - 2 archive-filename references corrected to match the real on-disk filenames in `docs/archive/`.
  - 1 legacy v3 section header preserved (intentional historical marker).
- Zero changes under `backend/`, `frontend/`, `shared/`, `scripts/`, `backend/ci/`. No runtime path touched. No service restart required.

**References:**
- BEF V2 §1.4 (three-axis authority stack), §1.5 R5/R6 (single-file scope), §3.7 (escalation), §16.7 GAP-15, §16.13 (current build reality).
- Tag: `baseline/1fd3110-pre-docs-restructure`.
- Commits: `ea8eae9`, `3509d25`, `090f52b`, `c650840`, `8347a18`, and this entry's commit.

**Decided by:** Founder + Architect (Claude Opus 4.7 strategy session, 2026-05-20).

**Status:** GAP-15 closed for TDD V5. PRD V4 was verified clean during the same restructure (zero `advertwise` hits). BEF V2 V2 CHANGELOG references preserved as intended historical record.

---

## 2026-05-21 — G1 Foundation gate: conditional clear

Context: BEF §15.7 row 1 has 4 criteria for G1.
Resolution:
  (i)  ci/run_migrations.py --apply clean — VERIFIED
  (ii) Seeded ENUMs match [TDD-ENUMS] — VERIFIED (6 ENUMs via psql)
  (iii) audit_log REVOKE policy — UNVERIFIABLE (no adcreo_app role
        on Neon free tier; only neondb_owner exists). Deferred to
        before first paying user. Application layer enforces
        append-only in the interim.
  (iv) CI-A green — VERIFIED (GitHub Actions run #3, SHA 4c7916b)
G1 declared conditionally clear. REVOKE gap logged as D-002.
Authority: BEF §15.7 row 1 + BEF §3.7
Resolved by: Abhishek (Founder)

---

## 2026-05-21 — audit_log REVOKE policy untestable on Neon free tier

Context: Neon staging has no separate adcreo_app role.
Resolution: adcreo_app role to be provisioned before first paying
user. Logged as gap, not blocker for beta launch.
Authority: BEF §15.7 row 1 criterion (iii)
Resolved by: Abhishek (Founder)

---

## 2026-05-21 — d2c_fashion added to GreenZone (D-003)

Context: worker_extract.py GREEN_ZONE_SET contained d2c_fashion
which was not in [PRD-GREENZONE] or [TDD-ENUMS] 5-category definition.
Resolution: Founder decision — keep d2c_fashion as valid GreenZone
category. Added to green_zone_category ENUM via migration
V202605211400. PRD V4 and TDD V5 acknowledged as needing doc update
(non-blocking for launch). Worker GREEN_ZONE_SET already correct.
Authority: PRD [PRD-GREENZONE] + TDD [TDD-ENUMS] — doc update pending
Resolved by: Abhishek (Founder)



## 2026-05-24 — Beta launch: payment skip + auto-provision Pro

Context: /wallet/topup route does not exist. Razorpay webhook handler does not
         exist. Redis wallet (wallet:{user_id} on DB0) is never seeded anywhere
         in the codebase. All users hit awaiting_funds on first render attempt.
         10-12 friends soft-launch tonight. No payment needed.

Resolution:
  1. auth.py INSERT changed: plan_tier 'starter' → 'pro', credits_remaining 0 → 5
  2. auth.py now seeds Redis DB0 via HSETNX wallet:{user_id} balance 5 after upsert
     (HSETNX = no-op if key exists — safe for returning users, never overwrites)
  3. G5 gate deferred to post-launch week 1
  4. Razorpay integration fully deferred — no test keys wired, no webhook route
  5. awaiting_funds flow remains in FSM and schema intact — unreachable at launch
     because all beta users have credits. Zero FSM or schema changes made.

Authority: BEF §3.7 Founder override — explicit launch decision.
           Hard Invariant §6 #13 preserved — no new JobStatus ENUMs.
           Hard Invariant §6 #3 preserved — no pre_topup_status mutation in workers.
Resolved by: Abhishek (Founder)

---
