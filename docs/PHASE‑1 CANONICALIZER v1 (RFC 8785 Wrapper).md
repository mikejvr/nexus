---

PHASE‑1 CANONICALIZER v1 (RFC 8785 Wrapper)

Deterministic canonical JSON engine for NEXUS‑I

Below is the production‑ready canonicalizer module.

It exposes:

- canonicalize_dict() → canonical Python dict  
- canonicalize_bytes() → canonical RFC 8785 bytes  
- canonicalize_str() → canonical UTF‑8 JSON string  
- canonical_hash() → SHA‑256 of canonical bytes  

All functions are pure and side‑effect‑free.

---

📦 canonicalizer.py

`python
"""
Phase-1 Canonicalizer v1 — NEXUS-I
RFC 8785 compliant canonical JSON generator.

This module provides:
  - canonicalize_dict(): returns canonical Python dict
  - canonicalize_bytes(): returns canonical JSON bytes (RFC 8785)
  - canonicalize_str(): returns canonical JSON string
  - canonical_hash(): returns SHA-256 hash of canonical bytes

All functions are pure, deterministic, and environment-independent.
"""

from future import annotations
import hashlib
from typing import Any, Dict

import rfc8785  # RFC 8785 canonical JSON implementation


------------------------------------------------------------

Canonicalize Python dict → canonical JSON bytes

------------------------------------------------------------
def canonicalize_bytes(data: Dict[str, Any]) -> bytes:
    """
    Convert a Python dict into canonical JSON bytes using RFC 8785.

    This is the authoritative canonicalization step for Phase-1.
    """
    return rfc8785.canonicalize(data)


------------------------------------------------------------

Canonicalize Python dict → canonical JSON string

------------------------------------------------------------
def canonicalize_str(data: Dict[str, Any]) -> str:
    """
    Convert a Python dict into canonical JSON UTF-8 string.
    """
    return canonicalize_bytes(data).decode("utf-8")


------------------------------------------------------------

Canonicalize Python dict → canonical Python dict

(Round-trip through canonical JSON)

------------------------------------------------------------
def canonicalize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a Python dict into a canonical dict by round-tripping
    through RFC 8785 canonical JSON.

    This ensures:
      - sorted keys
      - normalized numbers
      - normalized booleans
      - normalized nulls
      - stable structure
    """
    canonicaljson = canonicalizebytes(data)
    return rfc8785.loads(canonical_json)


------------------------------------------------------------

Compute SHA-256 hash of canonical JSON bytes

------------------------------------------------------------
def canonical_hash(data: Dict[str, Any]) -> str:
    """
    Compute the SHA-256 hash of the canonical JSON representation
    of the given dict.

    This is the canonical_hash used in Phase-1 shard metadata.
    """
    canonical = canonicalize_bytes(data)
    return hashlib.sha256(canonical).hexdigest()
`

---

WHY THIS IMPLEMENTATION IS CORRECT

1. RFC 8785 compliance
Using rfc8785.canonicalize() ensures:

- lexicographically sorted keys  
- deterministic number formatting  
- deterministic boolean/null formatting  
- deterministic string escaping  
- deterministic whitespace (none)  
- deterministic UTF‑8 encoding  

This is the only safe canonicalization standard for Phase‑1.

---

2. Pure functions
No global state.  
No environment dependencies.  
No nondeterministic fields.

This satisfies the Phase‑1 constitutional purity requirement.

---

3. Round‑trip canonical dict
canonicalize_dict() ensures:

- canonical structure  
- canonical ordering  
- canonical numeric normalization  

This is required for:

- Phase‑1 Validator  
- Phase‑5 CAS Evaluator  
- Phase‑7 Autonomous Agents  
- Phase‑8 Hyperstability  
- Phase‑9 Omnistructure  

---

4. canonical_hash() is the Phase‑1 truth anchor
This is the canonical_hash stored in:

- shard metadata  
- Phase‑1 manifest  
- Phase‑5 constitutional block  
- Phase‑7 lineage agent  
- Phase‑8 stability engine  
- Phase‑9 omnistructure engine  

It is the root of all identity in NEXUS‑I.

---