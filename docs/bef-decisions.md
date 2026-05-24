2026-05-24 — Beta launch: payment skip + auto-provision Pro

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
