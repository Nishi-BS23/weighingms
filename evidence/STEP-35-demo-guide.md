# STEP 35 — Final demonstration script

Demonstrate the running product, not slides. The demo takes about 10 minutes.

## Before you start
1. In a terminal at the repository root, run `npm run dev`. Wait for the three processes (`dummy`, `api`, `web`).
2. Open **http://127.0.0.1:5173** in Chrome and press **F12** to open the **Network** tab (you need it in Part 6).
3. Below the terminal, click **Reset training data**. B-24187 should show `QUEUED`.
4. Keep a second tab ready on **http://127.0.0.1:8100/docs** (the Dummy OrgaTEX, scales, scanner and printer).

## Part 1 — Batch
- Show the **batch queue**. It is received from OrgaTEX; point at "Queue received from OrgaTEX at …" and the
  status strip (ORGATEX · LINKED).
- **Select B-24187**: touch the row, or type `B-24187` in *Batch ID* and press Enter.
- In the Network tab, point at `GET /api/batches/B-24187` and `GET /api/batches/B-24187/recipe`.

## Part 2 — Recipe
- Show the **five components** in the recipe rail: Blue RSPL 1240.0 g, Red RB 386.0 g, Yellow RGB 94.0 g,
  Sodium Sulphate 24.000 kg, Soda Ash 9.600 kg.
- Point at the header: the lot, container and tare for the active component.

## Part 3 — Scale
1. Touch **Remazol Yellow RGB** in the rail and show **SCALE SELECTED 3 kg precision · automatic** and the
   tolerance `±0.5 g (93.5 – 94.5)`.
2. Click **▶ Simulate dispense** (above the terminal), watch the live weight rise, then press **OK · Confirm**
   (or F1). **Yellow RGB is complete.**
3. Touch **Sodium Sulphate** and show **SCALE SELECTED 32 kg floor**, with units in kg (3 decimals) and the
   container `D-03 · TARE 1.850 kg`.

## Part 4 — Tolerance
1. On Sodium Sulphate, click **▶ Simulate overshoot**. The status reads **OVER TOLERANCE — SURPLUS …**, the
   surplus panel explains how to recover, and **OK · Confirm is disabled**. *An invalid weight cannot be
   confirmed.*
2. Click **Reset** (above the terminal) to put the weight back to zero. The status reads **DISPENSE — 24.000 kg
   REMAINING**, and Confirm is still disabled because the weight is under tolerance.
3. Click **▶ Simulate dispense**. Once the status reads **WITHIN TOLERANCE — PRESS OK TO CONFIRM**, **OK · Confirm
   is enabled**. Press it.

## Part 5 — Complete
- Weigh the remaining components (Blue RSPL, Red RB, Soda Ash): **Simulate dispense**, then **OK · Confirm**
  each time.
- Show the counter reaching **5 of 5** and the **Confirm & print** screen: All within tolerance **YES**, total,
  per-component results.

## Part 6 — Integration
- **The OrgaTEX API request.** In the Network tab, open the last `POST /api/sessions/…/confirm`. Confirming the
  fifth component completes the batch, and WeighingMS then posts the actual consumption to OrgaTEX. In the
  `npm run dev` terminal, the `dummy` log shows `POST /api/batches/B-24187/consumption`.
- **The successful response.** On screen, *Written to OrgaTEX* reads **CONFIRMED hh:mm:ss**. The `confirm`
  response body shows `"status": "COMPLETED"` and `"syncStatus": "SYNCED"`.
- **The stored transaction.** Open **http://127.0.0.1:8100/api/batches/B-24187/consumption**: one posting, with
  one line per component (dyestuff, lot, target, actual, scale, operator, result). Also open
  **http://127.0.0.1:5173/api/weighing-records?batchId=B-24187**: the five immutable weighing records.

## Part 7 — Ticket
- Show the **ticket preview**: header, batch, order, machine, shade, date, operator, TGT / ACT lines, ALL WITHIN
  TOLERANCE, and the barcode.
- Click **Print ticket** (F1). The screen shows "Ticket printed · TKT-…". Open
  **http://127.0.0.1:8100/api/tickets** to show the printed ticket. Print again to show **REPRINT**.

## Part 8 — Automated test
- In a second terminal, run `npm run test:e2e`. It shows **11 passed** in about 30 s. The run resets the training
  data, so do this last.
- Run `npm --prefix playwright run report` to show the HTML report, including the video of the B-24187 run.
- Optional: run `npm run check` (214 backend and 50 frontend tests, 97.86 % coverage).

## Optional extras, if time allows
- **Failure handling.** Below the terminal, untick *Printer* and press Print ticket: "Printer not available …".
  Untick *OrgaTEX* before the last Confirm: write-back is PENDING, then **Retry** gives CONFIRMED.
- **Supervisor override.** On an overshoot, press **Supervisor override**, enter PIN **2468** and a reason, then
  **Authorise**.
