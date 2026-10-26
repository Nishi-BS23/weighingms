"""Bolt state helper for the specsmd bolt-start skill (steps 6 and 9 + construction log).

Usage:
  python3 .specsmd/local/bolt_state.py start <bolt-id> <first-stage>
  python3 .specsmd/local/bolt_state.py stage <bolt-id> <stage> <artifact> <next-stage|none>
  python3 .specsmd/local/bolt_state.py done <bolt-id>   (construction-log entry after bolt-complete.cjs)

Final-stage completion is done by `.specsmd/aidlc/scripts/bolt-complete.cjs`, not by this helper.
"""

import re
import sys
from datetime import UTC, datetime
from pathlib import Path

BOLTS = Path("memory-bank/bolts")
INTENTS = Path("memory-bank/intents")


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def set_field(text: str, key: str, value: str) -> str:
    new, n = re.subn(rf"^{key}: .*$", f"{key}: {value}", text, count=1, flags=re.M)
    if n != 1:
        raise SystemExit(f"field {key} not found")
    return new


def log(bolt_text: str, line: str) -> None:
    unit = re.search(r"^unit: (.*)$", bolt_text, re.M).group(1)
    intent = re.search(r"^intent: (.*)$", bolt_text, re.M).group(1)
    path = INTENTS / intent / "units" / unit / "construction-log.md"
    if not path.exists():
        path.write_text(
            f"---\nunit: {unit}\nintent: {intent}\ncreated: {now()}\nlast_updated: {now()}\n---\n\n"
            f"# Construction Log: {unit}\n\n## Execution History\n\n"
        )
    text = path.read_text()
    text = re.sub(r"^last_updated: .*$", f"last_updated: {now()}", text, count=1, flags=re.M)
    path.write_text(text.rstrip("\n") + f"\n- **{now()}**: {line}\n")


def main() -> None:
    cmd, bolt_id = sys.argv[1], sys.argv[2]
    path = BOLTS / bolt_id / "bolt.md"
    text = path.read_text()
    if cmd == "start":
        stage = sys.argv[3]
        text = set_field(text, "status", "in-progress")
        text = set_field(text, "started", now())
        text = set_field(text, "current_stage", stage)
        text = set_field(text, "blocks", "false")
        path.write_text(text)
        log(text, f"{bolt_id} started - Stage 1: {stage}")
    elif cmd == "done":
        stages = len(re.findall(r"^  - name: ", text, re.M))
        log(text, f"{bolt_id} completed - All {stages} stages done")
    elif cmd == "stage":
        stage, artifact, nxt = sys.argv[3], sys.argv[4], sys.argv[5]
        entry = f"  - name: {stage}\n    completed: {now()}\n    artifact: {artifact}\n"
        if "stages_completed: []" in text:
            text = text.replace("stages_completed: []", "stages_completed:\n" + entry.rstrip("\n"))
        else:
            text = re.sub(r"(stages_completed:\n(?:  .*\n)*)", lambda m: m.group(1) + entry, text, count=1)
        text = set_field(text, "current_stage", nxt if nxt != "none" else "null")
        path.write_text(text)
        log(text, f"{bolt_id} stage-complete - {stage} → {nxt}")
    else:
        raise SystemExit(__doc__)
    print(f"{bolt_id}: {cmd} ok")


if __name__ == "__main__":
    main()
