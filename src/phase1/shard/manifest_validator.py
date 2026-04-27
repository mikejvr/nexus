import hashlib
import rfc8785
from jsonschema import Draft202012Validator
from canonicalizer import canonicalize_bytes
from phase1_schemas import MANIFEST_SCHEMA, RESOLVER

def validate_manifest(manifest_path) -> dict:
    raw = manifest_path.read_text(encoding="utf-8")

    try:
        parsed = rfc8785.loads(raw)
    except Exception as e:
        return {"valid": False, "errors": [f"invalid canonical JSON: {e}"]}

    validator = Draft202012Validator(MANIFEST_SCHEMA, resolver=RESOLVER)
    errors = sorted(validator.iter_errors(parsed), key=lambda e: e.path)

    # Deterministic ordering check
    paths = [entry["path"] for entry in parsed["shards"]]
    if paths != sorted(paths):
        errors.append(Exception("shards array is not sorted lexicographically by path"))

    # Self-verifying manifest hash
    manifest_copy = dict(parsed)
    manifest_hash = manifest_copy.pop("manifest_hash", None)

    canonical_bytes = canonicalize_bytes(manifest_copy)
    computed_hash = hashlib.sha256(canonical_bytes).hexdigest()

    if manifest_hash != computed_hash:
        errors.append(
            Exception(
                f"manifest_hash mismatch: expected {manifest_hash}, got {computed_hash}"
            )
        )

    return {
        "valid": len(errors) == 0,
        "errors": [str(e) for e in errors],
    }
