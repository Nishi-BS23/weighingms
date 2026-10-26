# Step 7: Requirements + Checkpoint 2 (Requirements validation)

Artifact: `memory-bank/intents/001-assisted-dyestuff-weighing/requirements.md`
Validation: self-validated by the agent on the participant's delegation (2026-10-26)

## Contents
- Clarifying questions (inception Checkpoint 1) answered from the sources
- 34 functional requirements (FR-1 … FR-20 map 1:1 to the workbook's 20 areas; FR-21 … FR-34 supporting)
- 18 non-functional requirements with metrics
- Every requirement/criterion tagged: [C] confirmed for this build, [A] assumption, [Q] unresolved, [T] training-only
- Assumptions register TA-01 … TA-20, unresolved questions UQ-01 … UQ-14, training-only behaviour TD-01 … TD-08
- Training scenario table (B-24187, 5 components) taken from the prototype

## Checkpoint 2 checks (per requirement)
| Check | Result |
|-------|--------|
| Can I understand what the system must do? | Yes — each FR has a description and Given/When/Then-style criteria |
| Can I test it? | Yes — criteria are binary, with concrete values (e.g. 93.4 / 93.5 / 94.0 / 94.5 / 94.6 g; 3.000 kg vs 3.001 kg) |
| Can I trace it to the Brief or UI? | Yes — every FR cites Brief IDs, PDF sections, prototype elements or workbook steps |
| Real OrgaTEX contracts invented? | No — Dummy contracts labelled training-only (TA-01, FR-25, constraints) |
| Unresolved items hidden? | No — 14 open questions kept open; overshoot response deferred to Step 24 decision |

## Revisions made during validation
- Overshoot response left as provisional assumption (TA-11) instead of copying the prototype's recalculation proposal (Workbook Step 24 rule).
- Component identity verification by barcode scan explicitly excluded and kept as UQ-13 (prototype does not show it).
- Write-back failure behaviour defined (PENDING + retry, idempotent) so Step 30 "OrgaTEX unavailable" has defined behaviour.

Result: APPROVE REQUIREMENTS
