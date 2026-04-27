import hashlib
import rfc8785
from jsonschema import Draft202012Validator
from canonicalizer import canonicalize_bytes
from phase1_schemas import SHARD_SCHEMA, RESOLVER

def validate_shard(shard_path) -> dict:
    raw = shard_path.read_text(encoding="utf-8")

    try:
        parsed = rfc8785.loads(raw)
    except Exception as e:
        return {"valid": False, "errors": [f"invalid canonical JSON: {e}"]}

    validator = Draft202012Validator(SHARD_SCHEMA, resolver=RESOLVER)
    errors = sorted(validator.iter_errors(parsed), key=lambda e: e.path)

    # Canonical hash check
    try:
        canonical_bytes = canonicalize_bytes(parsed["payload"])
        computed_hash = hashlib.sha256(canonical_bytes).hexdigest()
        if computed_hash != parsed["canonical_hash"]:
            errors.append(
                Exception(
                    f"canonical_hash mismatch: expected {parsed['canonical_hash']}, got {computed_hash}"
                )
            )
    except Exception as e:
        errors.append(Exception(f"canonicalization failure: {e}"))

    return {
        "valid": len(errors) == 0,
        "errors": [str(e) for e in errors],
        "canonical_hash": parsed.get("canonical_hash"),
    }
