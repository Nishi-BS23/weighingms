---
intent: 001-assisted-dyestuff-weighing
phase: inception
status: complete
source: docs/customize-weighing-station.html
updated: 2026-10-26T06:30:00Z
---

# UI/UX Prototype Analysis — WeighingMS Operator Terminal

The prototype is analysed as a **functional specification input**, not redesigned. Line numbers (`L…`) refer to `docs/customize-weighing-station.html`. Requirement IDs refer to `requirements.md`.

The file has two layers:
- **The device** (`.device` / `.screen`, L437–630): the product — a 15" dark HMI touch terminal.
- **Page chrome** (`.controls` L422–434, `.notes` L633–665): meeting aids — screen switcher, simulation buttons, question-pin toggle, notes. Not product features, except that the simulation buttons map to our training panel (TD-07).

---

## 1. Screen inventory

| # | Screen | Element | Lines | Purpose | FR |
|---|--------|---------|-------|---------|----|
| 1 | **Select batch** | `#v-queue` | L448–487 | Pick a batch from the OrgaTEX queue by scan or touch | FR-1, FR-2, FR-30 |
| 2 | **Weigh** | `#v-weigh` | L490–564 | Weigh the active component against target/tolerance; progress through the recipe | FR-3 – FR-15, FR-21, FR-22, FR-31 |
| 3 | **Confirm & print** | `#v-done` | L567–616 | Batch summary, OrgaTEX write-back status, ticket print and preview | FR-16 – FR-18, FR-23, FR-32 |
| — | Persistent chrome | `.topbar` L440–445, `.strip` L618–627 | Station identity, batch crumb, operator, device status, clock | FR-19, FR-24, FR-33 |

Screen switching: `showView()` L829–839, driven by the segmented control (L424–428) and by the confirm handler after the last component (L820).

## 2. UI components

| Component | Lines | Used on | Notes |
|-----------|-------|---------|-------|
| Device bezel + caption '15" INDUSTRIAL TOUCH TERMINAL' | L148–159, L437 | All | Dark in both themes (L4–6 comment) |
| Top bar: brandmark "WeighingMS / STATION 01" | L441 | All | |
| Batch crumb "BATCH · ORDER · MACHINE" | L442 | All (when batch active) | |
| Operator chip with status dot "Operator R. Karim · Shift A" | L444 | All | FR-19 |
| Scan prompt with animated beam | L450–456, L329–337 | Screen 1 | Animation disabled for reduced motion (L338) |
| Queue table (Batch, Order, Machine, Fabric / lot, Shade, Comp., Status) | L458–484 | Screen 1 | Selected row highlighted (`tr.sel`, L347) |
| Status tag (WEIGHING amber `.tag.now`, QUEUED neutral) | L348–352 | Screen 1 | |
| Recipe rail header ("Recipe · Teal 4C", batch, "n of 5 components weighed") | L494–498 | Screen 2 | |
| Component list item (swatch, name, code · scale, target qty, state) | L696–716, L209–225 | Screen 2 | States: done / active / pending |
| Weigh header: name + meta line (code · LOT · CONTAINER · TARE) | L504–507, L740–743 | Screen 2 | |
| Scale badge ("Scale selected / 3 kg precision / automatic") | L508–512 | Screen 2 | |
| Readout cells: Weighed now (large, zone-coloured), Still to weigh, Target | L515–528 | Screen 2 | Live cell 52 px font (L250) |
| Progress bar with fill, tolerance band, target line; caption 0 / band / max | L530–540 | Screen 2 | `role="progressbar"` (L531) |
| Status line (zone-coloured message) | L541, L275–282 | Screen 2 | |
| Surplus panel (surplus amount/% + recalculation proposal table) | L544–554 | Screen 2 (over only) | Proposal is a business question (pin 25) |
| Action keys: OK · Confirm F1, Re-tare F2, Quit F4, Supervisor override | L556–561 | Screen 2 | Keys ≥ 62 px high (L300) |
| Completion heading, summary list (6 rows), consumption note | L569–582 | Screen 3 | |
| Action keys: Print ticket F1, Next batch F3 | L583–586 | Screen 3 | |
| Ticket preview (paper-style, barcode, batch ID) | L590–610 | Screen 3 | Barcode is decorative PRNG bars (L848–856) |
| Status strip: SCALE 3 kg, SCALE 32 kg, SCANNER, PRINTER, ORGATEX · LINKED, EN, clock | L618–627 | All | Clock is a fake ticking time (L858–865) |
| Question pins | L377–385, inline | All | Meeting aid — not reproduced (TA-20) |

## 3. User actions

| Action | Where | Prototype behaviour | Lines | Product behaviour (FR) |
|--------|-------|---------------------|-------|------------------------|
| Scan a batch card | Screen 1 | Text only — no handler | L453 | Select batch by scan (FR-2) |
| Touch a queue row | Screen 1 | Not wired | L463–482 | Select batch (FR-2) |
| Touch a component in the rail | Screen 2 | `select(i)`: ignored if done; otherwise becomes active, previous active → pending, weight reset | L711, L718–724 | FR-15 |
| OK · Confirm (F1) | Screen 2 | Enabled only in zone `ok`; records actual, marks done, auto-selects next pending; if none → Screen 3 | L557, L779, L814–822 | FR-13, FR-15, FR-16 |
| Re-tare (F2) | Screen 2 | Resets weight to 0 | L811 | FR-7 (tare scale, weight → 0) |
| Quit (F4) | Screen 2 | Resets weight to 0 | L812 | FR-22 (abandon + safe exit to queue) — prototype is a placeholder |
| Supervisor override | Screen 2 | Status line "OVERRIDE REQUESTED — AWAITING SUPERVISOR" only | L824–826 | FR-21 (PIN + reason, recorded) |
| Print ticket (F1) | Screen 3 | Not wired | L584 | FR-18 |
| Next batch (F3) | Screen 3 | Not wired | L585 | FR-32 (back to Screen 1) |
| Simulate dispense / overshoot / Reset | Page chrome | Animated weight run to a landing value | L430–432, L787–810 | Training panel driving the Dummy Scale (FR-29, TD-07) |
| Screen switcher | Page chrome | Jump to any view | L424–428 | Step indicator following the workflow (TA-20) |

## 4. Application states

**Screen state:** `queue` → `weigh` → `done` (`showView`, L829).

**Component state** (`data-state`, L216–225): `pending` → `active` → `done`. Only one `active`. `done` is terminal (L719).

**Weighing zone** (`zone()`, L729–735) for the active component, evaluated on every reading:

| Zone | Condition (prototype) | Visual | Confirm |
|------|-----------------------|--------|---------|
| `under` | v < 0.9 × target | Neutral readout, steel bar | Disabled |
| `near` | 0.9 × target ≤ v < target − tol | Amber readout and bar (L253, L264) | Disabled |
| `ok` | target − tol ≤ v ≤ target + tol | Green (L254, L265) | **Enabled** |
| `over` | v > target + tol | Red (L255, L266); surplus panel on (L778) | Disabled |

**Batch state:** in progress (some components done) → complete (no pending → Screen 3, L820). Prototype opens mid-flow with 2 of 5 done (L678–682) — a snapshot; our seed starts at 0 of 5 so the full flow can be demonstrated.

**Simulation state:** `timer` running/stopped (L783–800).

## 5. Data displayed

| Data | Example | Lines |
|------|---------|-------|
| Station | STATION 01 | L441 |
| Batch, order, machine | B-24187, SO-9931, JET-04 | L442 |
| Operator, shift | R. Karim · Shift A | L444 |
| Queue received time | 06:12 | L454 |
| Queue rows | 4 batches incl. fabric/lot "100% CTN knit · 480 kg", shade, component count, status | L463–482 |
| Recipe shade | Teal 4C | L495 |
| Progress | "2 of 5 components weighed" | L497 |
| Component | name, code, colour, target, unit, tolerance, scale, lot, container, tare, actual | L677–683 |
| Weights | Weighed now, Still to weigh, Target — g with 1 dp, kg with 3 dp | L692–693, L746–749 |
| Tolerance caption | "TOLERANCE ±0.5 g (93.5 – 94.5)" | L538, L763–765 |
| Bar full scale | 125 g (Yellow RGB) | L539, L766 |
| Surplus | "+2.4 g (+2.6%)" and proposed new targets | L545–549 |
| Summary | 5 of 5; all within tolerance YES; total 35.322 kg; elapsed 6 min 41 s; operator; written to OrgaTEX CONFIRMED 07:48:22 | L572–577 |
| Ticket | header, batch, order, machine, shade, date, operator, component TGT/ACT, result line, barcode, batch ID | L591–609 |
| Device status | scales READY, scanner, printer, OrgaTEX LINKED 07:41, EN, clock | L619–626 |

## 6. Data required (to drive the screens)

| Entity | Fields | Source system | FR |
|--------|--------|---------------|----|
| Batch | batchId, orderRef, machineRef, fabricDesc, fabricWeightKg, shadeCode, componentCount, status, releasedAt | OrgaTEX (dummy) | FR-1 |
| Recipe | recipeId, batchId, shadeCode, version, components[] | OrgaTEX (dummy) | FR-3 |
| Recipe component | componentId, sequence, dyestuffCode, name, colourHex, targetQty, unit, tolerance (±abs), lotId | OrgaTEX (dummy) | FR-3 – FR-5, FR-12 |
| Container | containerId, type, tareQty, unit | WeighingMS master | FR-6, FR-7 |
| Scale | scaleId, class, label ("3 kg precision"), capacity, resolution, status, calibrationDue | Scale (dummy) + WeighingMS config | FR-8, FR-24 |
| Reading | grossWeight, netWeight, unit, stable, timestamp | Scale (dummy) | FR-9 |
| Operator | operatorId, name, shift, badgeId, role | WeighingMS | FR-19 |
| Weighing record | see FR-13 | WeighingMS | FR-13, FR-23 |
| Device status | per device up/down/degraded + last OrgaTEX sync time | All dummies | FR-24 |
| Ticket | composed from batch + records | WeighingMS → Printer (dummy) | FR-18 |

## 7. State transitions

```text
Screen 1 (queue)
  ── touch row / scan batch (selectable) ──► Screen 2 (weigh), first pending component active
  ── scan unknown / non-selectable batch ──► stay, show reason
Screen 2 (weigh)
  ── touch pending component ─────────────► that component active; previous active → pending; re-select scale; tare
  ── reading changes ─────────────────────► zone re-evaluated (under/near/ok/over)
  ── OK·Confirm (zone ok) ────────────────► component done; next pending active
  ── OK·Confirm on last pending ──────────► batch complete → write-back → Screen 3
  ── Supervisor override (valid PIN+reason)► component done (OVERRIDDEN); same progression
  ── Re-tare ─────────────────────────────► tare scale; net → 0
  ── Quit ────────────────────────────────► abandon attempt → Screen 1 (batch resumable)
Screen 3 (done)
  ── Print ticket ────────────────────────► ticket printed (preview stays)
  ── Next batch ──────────────────────────► Screen 1 (queue refreshed)
```
Prototype references: `select` L718, `btn-ok` L814–822, `showView` L829. Override, Quit, Print and Next batch transitions are **not** implemented in the prototype and come from requirements FR-18, FR-21, FR-22, FR-32.

## 8. Validation behaviour

| Rule | Prototype | Lines |
|------|-----------|-------|
| Confirm only within tolerance | `btn-ok.disabled = (z !== "ok")` | L779 |
| Inclusive bounds | `v > target + tol` → over; `v >= target − tol` → ok | L731–732 |
| Done component cannot be reselected | early return | L719 |
| Still to weigh never negative | `Math.max(0, …)` | L747, L775 |
| Bar never exceeds 100% | `Math.min(100, …)` | L751 |
| Band min width for visibility | `Math.max(0.6, hi − lo)` | L760 |
| No validation of scale connection, stability, operator, lot | — | (gap → FR-20, TA-16) |

## 9. Integration points

| Point | Prototype evidence | Pin | Product integration |
|-------|--------------------|-----|---------------------|
| OrgaTEX batch queue | "Queue received from OrgaTEX at 06:12" | 10 | `GET /api/batches` (dummy) via OrgaTEX adapter (FR-1) |
| OrgaTEX recipe/dyestuff/lot | Component data | 10 | `GET /api/batches/{id}`, `/recipe` (FR-3) |
| OrgaTEX write-back | "Written to OrgaTEX CONFIRMED 07:48:22" | 11 | `POST /api/batches/{id}/consumption` (FR-17) |
| OrgaTEX link status | "ORGATEX · LINKED 07:41" (amber dot) | 6 | Device status (FR-24) |
| Scales (continuous weight) | Weighed now, two scale strip items | 15, 16 | Dummy Scale API (FR-9, FR-26) |
| Scale tare | Re-tare key | — | `POST /api/scales/{id}/tare` (FR-7) |
| Barcode scanner | "Scan a batch card", strip item | — | Dummy Scanner (FR-2, FR-27) |
| Ticket printer | Print ticket, strip item, ticket | 18 | `POST /api/tickets` (FR-18, FR-28) |
| Supervisor authority | Override key | 33 | Override with PIN (FR-21) |

## 10. Business rules embedded in the JavaScript

| # | Rule | Lines | Treatment |
|---|------|-------|-----------|
| R1 | Tolerance zones: over > target+tol; ok ≥ target−tol; near ≥ 0.9·target; else under | L729–735 | Adopted (FR-12, TA-05) — evaluated in backend |
| R2 | Confirm enabled only in `ok` | L779 | Adopted (FR-13) |
| R3 | Display precision: kg → 3 dp, g → 1 dp | L692–693 | Adopted (FR-9) |
| R4 | Remaining = max(0, target − now) | L747 | Adopted (FR-11) |
| R5 | Surplus = now − target (shown when over) | L771 | Adopted (FR-14) |
| R6 | Surplus % = surplus / target (shown "+2.6%") | L545 | Adopted (FR-14) |
| R7 | **Surplus compensation: recalculate remaining components proportionally** (24.000 → 24.624 kg, 9.600 → 9.850 kg; factor = actual/target of the over-dosed component ≈ 1.026) | L547–551 | **Not adopted** — explicitly a proposal (pin 25); decision at Workbook Step 24 (TA-11, UQ-07) |
| R8 | Scale per component is pre-assigned in data ("3 kg precision" / "32 kg floor") | L678–682 | Replaced by a rule: target ≤ 3 kg → precision, else floor (FR-8, PDF §5.3) — consistent with all 5 prototype components |
| R9 | After confirm, auto-select first pending component | L818–821 | Adopted (FR-15) |
| R10 | All done → completion screen | L820 | Adopted (FR-16) |
| R11 | Re-tare and Quit both reset weight to 0 | L811–812 | Re-tare adopted; Quit extended to abandon + exit (FR-22) |
| R12 | Bar full scale per component (1600, 520, 125 g; 32, 14 kg) ≈ 1.3 × target | L678–682, L751 | Display rule: full scale ≈ 4/3 × target, rounded up (UI-only arithmetic) |
| R13 | Tolerance ≈ 0.5% of target (6.0/1240, 2.0/386, 0.5/94, 0.120/24, 0.048/9.6) | L678–682 | Values carried per component in seed data; 0.5% used as configurable default (TA-03) |
| R14 | Simulated pour: fast first, easing as target approaches; step = max(0.4% of target, 5.5% of remaining) every 34 ms | L787–800 | Adopted as the Dummy Scale "dispense" profile (FR-26) |
| R15 | Simulate dispense lands at target + 0.4·tol; simulate overshoot lands at target + 4.8·tol | L802–809 | Adopted as training panel presets (TD-07) |

## 11. Assumptions represented by the prototype

| Assumption | Evidence | Requirement link |
|------------|----------|------------------|
| Weight can be read continuously | Live readout, animated bar; note "What this mockup is testing" | TA-16, UQ-04 |
| Surplus compensation = recalculate the remainder | Surplus panel | TA-11, UQ-07 |
| One operator weighs one component at a time against a queue owned by OrgaTEX | Notes L645–648 | FR-15, TA-09 |
| "Weighed now" is net of tare | Starts at 0.0 with TARE shown | TA-06 |
| One container per component, lots known per component | Meta line per component | TA-07, TA-08 |
| Two scales: 3 kg precision, 32 kg floor | Scale badge, strip | TA-04 |
| Operator identified by name and shift | Op chip | TA-09 |
| Interface in English | "EN" in strip | TA-17 |
| Ticket content as drawn | "Label content is invented" L612 | TA-15 |
| Write-back happens at completion and succeeds | Summary row | TA-12, TA-13 |
| Queue statuses QUEUED / WEIGHING | Tags | TA-02 |

## 12. Questions the prototype cannot answer

| Question | Pin | Requirement link |
|----------|-----|------------------|
| What can be read from / written to OrgaTEX, and how? | 6, 10, 11 | UQ-01, UQ-02 |
| What happens if OrgaTEX is unreachable at completion? | 11 (Q13) | UQ-03 (TA-13 defines training behaviour) |
| Scale models/protocol; continuous vs stabilised only; selection threshold near the boundary | 15, 16 | UQ-04, UQ-05 |
| How tolerances are defined and by whom | 24 | UQ-06 |
| What surplus compensation really means; what if not compensable | 25 | UQ-07 |
| Container identity and lot capture | 29 | UQ-09 |
| Who may override, logging/approval | 33 | UQ-08 |
| Interface language | 35 | UQ-12 |
| Individual operator login | 37 | UQ-10 |
| Ticket printer and label content | 18 | UQ-11 |
| What Quit should do beyond resetting weight | — | FR-22 (defined by requirements) |
| What an unselectable batch looks like; scan errors | — | FR-2 (defined by requirements) |
| How device failures should appear | — | FR-20 (defined by requirements) |

---

## Fidelity checklist for construction (used again at Workbook Step 28)

- [ ] Dark HMI device frame with bezel caption; page chrome outside the device holds the training panel
- [ ] Top bar texts and operator chip
- [ ] Screen 1: scan prompt + beam, 7-column queue table, status tags
- [ ] Screen 2: rail (header, swatches, states), weigh header + meta line, scale badge, 3 readout cells, bar with band + target line + caption, status line texts, surplus panel, 4 keys with F-labels
- [ ] Screen 3: heading, 6 summary rows, consumption note, 2 keys, ticket preview with barcode
- [ ] Status strip with 5 device items, EN, clock
- [ ] Zone colours: neutral / amber / green / red; disabled keys at reduced opacity
- [ ] Units and decimals: g 1 dp, kg 3 dp; scale switch to kg for Sodium Sulphate
