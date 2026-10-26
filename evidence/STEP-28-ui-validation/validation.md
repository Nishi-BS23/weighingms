# STEP 28 — UI/UX validation: prototype vs implementation

- **Prototype:** `docs/customize-weighing-station.html`.
- **Implementation:** `npm run dev`, then http://127.0.0.1:5173.

The captures were taken at the same 1240 px width and cropped to the terminal (`.device`). The prototype's
question pins are hidden because they are notes for the workshop, not part of the product.

To make the comparison fair, the implementation was driven with the prototype's own weights: Blue 1241.5 g,
Red 385.4 g, Yellow 94.2 g, Na2SO4 23.980 kg and Soda Ash 9.621 kg, a total of 35.322 kg.
The capture scripts are not part of the product. They used the training API, and the browser console showed
**no errors**.

| Screen | Comparison |
|---|---|
| 1 · Select batch | [screen-1-comparison.png](screen-1-comparison.png) |
| 2 · Weigh | [screen-2-comparison.png](screen-2-comparison.png) |
| 3 · Confirm & print | [screen-3-comparison.png](screen-3-comparison.png) |

## Screen by screen

### Screen 1 · Select batch
- **Same:**
  - Top bar (WeighingMS · STATION 01 · Operator R. Karim · Shift A).
  - The "Scan a batch card to begin" prompt.
  - The queue columns (BATCH, ORDER, MACHINE, FABRIC / LOT, SHADE, COMP., STATUS).
  - The status tags.
  - The status strip, the `EN` language indicator and the clock.
- **Differences, all intentional:**
  - **Live data, not a fixed picture.** The queue time, clock and batch statuses come from OrgaTEX and the
    station clock. After a training reset all four batches are `QUEUED`. The prototype is frozen in the middle
    of B-24187 (`WEIGHING`, with its batch already in the top bar).
  - **"Batch ID" field.** Type the batch number, or scan it with a keyboard-wedge scanner (FR-2: "touching its
    row or scanning its batch barcode"). The prototype only allows touching a row.
  - **Readable rows.** The prototype has no `<!doctype html>`, so it renders in quirks mode, where table cells
    don't inherit the dark theme's text colour, and its queue text is almost invisible. The implementation sets
    the colour explicitly.
  - **ORGATEX dot.** Green when OrgaTEX is reachable. The prototype shows amber because the interface was an open
    question (pin 6).

### Screen 2 · Weigh (Remazol Yellow RGB, 2 of 5 weighed)
- **Same:**
  - Recipe rail: Blue RSPL ✓ 1241.5 and Red RB ✓ 385.4 done; Yellow RGB `WEIGHING`; Sodium Sulphate and Soda Ash
    `PENDING`.
  - Header: `DYE-4471 · LOT 2026-0387 · CONTAINER C-12 · TARE 214.0 g`.
  - **SCALE SELECTED 3 kg precision · automatic**.
  - WEIGHED NOW `0.0 g`, STILL TO WEIGH `94.0 g`, TARGET `94.0 g`.
  - Tolerance bar: 0 to 125.0 g, with the caption `TOLERANCE ±0.5 g (93.5 – 94.5)`.
  - `DISPENSE — 94.0 g REMAINING`.
  - The keys OK · Confirm F1 (disabled), Re-tare F2, Quit F4 and Supervisor override.
- **Differences:**
  - **Vertical spacing only.** The prototype renders in quirks mode, so its text blocks are a few pixels taller.
  - **Rail rows** were matched with one CSS rule: 61.6 px against the prototype's 60.6 px. They were 71.2 px
    before.
  - **Weigh panel.** The header, readout and bar are each about 5 px shorter than in the prototype. The key row
    is pinned to the bottom of the panel, so it shows a gap about 26 px larger above it.
  - **Unchanged:** the elements, their order, all values, and the key height (62 px, NFR-8).

### Screen 3 · Confirm & print
- **Same:**
  - Heading "Batch B-24187 weighed".
  - Rows: Components weighed **5 of 5**, All within tolerance **YES**, Total dispensed **35.322 kg**, Operator
    R. Karim, Written to OrgaTEX **CONFIRMED hh:mm:ss**.
  - The release sentence.
  - Print ticket F1 and Next batch F3.
  - Ticket layout: FCI DYEING — WEIGHING TICKET; BATCH, ORDER, MACHINE, SHADE, DATE and OPER.; the
    COMPONENT / TGT / ACT lines with short names (Blue RSPL … Na2SO4, Soda Ash); ALL WITHIN TOLERANCE; and a
    barcode with B-24187.
- **Differences, all intentional:**
  - **Per-component table** (target, actual, result). The project requirement asks for a completed-job summary
    with the records (FR-23).
  - **Real elapsed time and ticket date.** The automated run took 1 s; the prototype's 6 min 41 s is invented.
  - **Real barcode.** It encodes the batch ID, which is why it is narrower. The prototype draws decorative bars.
  - **No "Label content is invented." caption.** It was a note for the mock-up (pin 18).

## Aspect checklist

| Aspect | Result | How it was checked |
|---|---|---|
| States | ✅ | Zones UNDER, NEAR, WITHIN, OVER and OFFLINE: status lines, colours and Confirm enabling match the prototype. Checked by the e2e tolerance and failure tests and by `WeighingPanel` unit tests. |
| Interactions | ✅ | Touch a row or scan to select. F1 Confirm, F2 Re-tare, F4 Quit; on the done screen F1 Print and F3 Next. Touching a rail item jumps to it. Simulate dispense / overshoot are in the training panel. |
| Data | ✅ | B-24187 · SO-9931 · JET-04 · Teal 4C, with all five components, targets, tolerances, lots and containers exactly as in the prototype (`data/seed/orgatex-seed.json`). |
| Labels | ✅ | Same wording and capitalisation throughout: status lines, key captions, summary rows, ticket header. |
| Units | ✅ | g to 1 dp on the 3 kg scale; kg to 3 dp on the 32 kg scale; the unit changes with the scale. |
| Tolerance | ✅ | Inclusive band: 93.4 refused, 93.5 accepted, 94.5 accepted, 94.6 refused (Step 22 and the e2e boundary test). |
| Scale switching | ✅ | Yellow RGB (94 g) uses `3 kg precision`; Sodium Sulphate (24 kg) uses `32 kg floor`, header `CONTAINER D-03 · TARE 1.850 kg`. |
| Component progression | ✅ | Confirming moves to the next pending component, rail ✓ values update, and "n of 5 components weighed" counts up. |
| Completion | ✅ | 5 of 5 gives the done screen with a 35.322 kg total and OrgaTEX write-back CONFIRMED. |
| Ticket | ✅ | Preview matches the prototype's layout. Printing goes to the dummy printer (`TKT-…`); reprints are marked REPRINT. |
