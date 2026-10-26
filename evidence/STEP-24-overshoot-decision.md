# Step 24 — Overshoot: decision record

**Date:** 2026-10-26 · **Bolt:** 007-weighing-station · **Story:** 002-weighing-station/005-overshoot-handling · **Requirement:** FR-14 (UQ-07, TA-11)

## 1. Observed problem

When the operator dispenses more than the upper tolerance bound (e.g. Yellow RGB 96.4 g against 94.0 g ±0.5 g), the component is over-dosed. The prototype shows a red surplus panel ("Surplus +2.4 g (+2.6%) — over tolerance") and *proposes* recalculating the remaining components to preserve the shade ratio (Sodium Sulphate 24.000 → 24.624 kg, Soda Ash 9.600 → 9.850 kg). Its question pin 25 asks FCI what "surplus compensation" actually means.

## 2. What is known and what is assumed

| Statement | Status | Source |
|-----------|--------|--------|
| An over-dose must be detected and the surplus shown | **Known** (required for this build) | PDF §6 Step 6 "Overweight… warns the operator"; Brief FR-20 |
| An out-of-tolerance weighing must not be accepted without explicit authorisation | **Known** | Brief BR-07, FR-18; PDF §6 Step 7 "explicit, authorized exception" |
| The business needs a *defined* response, not an ad-hoc one | **Known** | Brief BR-08 |
| Every override records who authorised it and why | **Known** | Brief BR-13, FR-24 |
| "Surplus compensation" = proportional recalculation of the remaining components | **Assumed** — Brief A-08, rated "the most likely misunderstanding in the document" | Brief §12 A-08, R-03; prototype pin 25 |
| Which over-doses are "compensable" | **Unknown** (Q25, Q26) | Brief §10, A-08 |
| Who may override, and whether remote approval is needed | **Unknown** (Q33) | Brief UQ-08 |
| WeighingMS must not modify recipes (OrgaTEX owns them) | **Known** | Brief C-01, BR-04 |

## 3. Safe training implementations considered

### Option A — Block and recover (no recalculation)
The over-dosed component stays unconfirmed (Confirm disabled). The operator recovers by:
1. removing material until the weight is back inside the band, then confirming; or
2. emptying the container and pressing **Re-tare** to weigh again; or
3. asking a supervisor for an **override** (PIN + mandatory reason) — recorded as `OVERRIDDEN` with the surplus.

*Impact:* simplest and safest; satisfies BR-07, BR-08, BR-13; no recipe values are changed in WeighingMS (C-01 respected); every exception is audited. Shade correction for an accepted over-dose is left to people (lab/supervisor), as today.

### Option B — Supervisor-approved proportional compensation (the prototype's proposal)
On over-dose, compute factor = actual / target and propose revised targets for the remaining components; a supervisor accepts, and the revised targets replace the snapshot values.

*Impact:* preserves the colour ratio if the assumption is right, but it changes recipe quantities outside OrgaTEX (conflicts with C-01), is unusable once later components are already weighed or when revised targets exceed scale capacity, and rests on the assumption the Brief itself calls the most likely misunderstanding (A-08). Much larger scope (new state, approvals, audit of adjusted targets, write-back of adjusted consumption).

### Option C — Accept with surplus recorded, no authorisation
Let the operator confirm an over-dose and just record the surplus.

*Impact:* fastest for the operator but **violates** BR-07 (no out-of-tolerance acceptance without authorisation). Unsafe — listed only to show why it is excluded.

## 4. Decision

**Option A — Block and recover.** Training rule:

> For this training implementation, an over-weight component remains unconfirmed. The operator must remove the excess until the weight is back inside the tolerance band, or empty the container and re-tare to weigh again, or obtain a supervisor override with PIN and reason, which is recorded as OVERRIDDEN together with the surplus. No automatic recipe recalculation is performed; that would require an approved business rule from FCI (Brief A-08, Q25/Q26).

**Decided by:** the agent, under the participant's explicit delegation of decisions ("do everything your way"). The participant can overturn it; switching to Option B would be a new story, not a code change in place.

## 5. Implementation (bolt 007)

- Domain: evaluation returns `zone = OVER`, surplus, surplus %, `canConfirm = false`, allowed actions `RETARE`, `QUIT`, `OVERRIDE`, and a guidance text describing the three recovery paths with the band limits.
- API: `GET /api/sessions/{id}/live` exposes the above; `POST /confirm` re-reads the scale and rejects with `OUT_OF_TOLERANCE`; `POST /override` requires a valid supervisor PIN and a reason.
- UI (bolt 008): red surplus panel with the guidance; Confirm disabled; Supervisor override dialog.
- Records: `result = OVERRIDDEN`, `surplus` stored; override row (supervisor, reason, time); `OVERRIDE` audit event.

## 6. Tests

- Domain: over-dose → Confirm blocked, surplus/surplus %, allowed actions and guidance; back inside the band → confirm allowed.
- API: confirm while over → 409 `OUT_OF_TOLERANCE`; override with wrong PIN → 403, empty reason → 422, valid → OVERRIDDEN record + audit; remove excess → confirm succeeds.
- Evidence: `STEP-24-overshoot-test.txt`, `STEP-24-overshoot-ui.png` (bolt 008).
