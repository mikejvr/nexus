from pathlib import Path
import json
from jsonschema import Draft202012Validator, RefResolver

SCHEMA_DIR = Path(__file__).parent / "schemas"

def load_schema(name: str) -> dict:
    path = SCHEMA_DIR / name
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

EXTRACTOR_SCHEMA = load_schema("phase1_extractor.schema.json")
SHARD_SCHEMA = load_schema("phase1_shard.schema.json")
MANIFEST_SCHEMA = load_schema("phase1_manifest.schema.json")

# Preload resolver for local $ref resolution
RESOLVER = RefResolver(
    base_uri=f"file://{SCHEMA_DIR.as_posix()}/",
    referrer=SHARD_SCHEMA,
)
