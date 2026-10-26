---
id: 011-function-keys
unit: 006-weighing-station-ui
intent: 001-assisted-dyestuff-weighing
status: complete
priority: could
created: 2026-10-26T06:32:30.000Z
assigned_bolt: 010-weighing-station-ui
implemented: true
---

# Story: 011-function-keys

**Title**: Function keys F1–F4

## User Story

**As a** weighing operator at the industrial terminal
**I want** the F-keys printed on the buttons to work
**So that** I can operate without touching the screen

## Requirements

- FR-34 Function keys

## Acceptance Criteria

- [x] Screen 2: F1 Confirm (only if enabled), F2 Re-tare, F4 Quit; Screen 3: F1 Print ticket, F3 Next batch
- [x] Keys ignored while a dialog is open

## UI/UX Impact

Key labels already shown on buttons (prototype `.fn`).

## API Dependencies

- Same as the corresponding buttons

## Test Expectations

- Vitest: key handler dispatch per screen

## Technical Notes

None

## Dependencies

### Requires
- 006-weighing-actions
- 008-completion-summary-screen

### Enables
- None

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Browser default for F-keys | preventDefault on handled keys |

## Out of Scope

- Full 21-key mapping
