"""Write the WeighingMS OpenAPI schema to frontend/openapi.json (input for openapi-typescript)."""

import json
from pathlib import Path

from weighingms.api.app import create_app

target = Path(__file__).resolve().parents[1] / "frontend" / "openapi.json"
target.write_text(json.dumps(create_app().openapi(), indent=2) + "\n")
print(f"wrote {target}")
