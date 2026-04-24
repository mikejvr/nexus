---

PHASE‑1 MANIFEST GENERATOR v1 (NEXUS‑I)

Deterministic, canonical, audit‑ready manifest builder

This module:

- walks the shard directory in deterministic order  
- validates each shard  
- extracts canonical metadata  
- computes the manifest  
- computes the optional Merkle root  
- writes all outputs using canonical JSON (RFC 8785)  
- guarantees byte‑for‑byte reproducibility  

---

📦 manifest_generator.py

`python
"""
Phase-1 Manifest Generator v1 — NEXUS-I
Produces:
  - /logs/phase1_validation.json
  - /logs/phase1_hashes.json
  - /phase1_manifest.json

All outputs are:
  - deterministic
  - RFC 8785 canonical JSON
  - sorted lexicographically
  - constitutionally stable
"""

from future import annotations
import hashlib
from pathlib import Path
from typing import Dict, List, Any

from canonicalizer import (
    canonicalize_bytes,
    canonicalize_dict,
    canonicalize_str,
    canonical_hash,
)
from validator import validate_shard  # Phase-1 shard validator
from deterministicio import walksorted  # deterministic traversal


------------------------------------------------------------

Optional Merkle root (sorted canonical_hash list)

------------------------------------------------------------
def computemerkleroot(hashes: List[str]) -> str:
    """
    Compute a simple Merkle root from a sorted list of canonical_hash values.
    Deterministic, stable, and constitutional.
    """
    if not hashes:
        return hashlib.sha256(b"").hexdigest()

    layer = [bytes.fromhex(h) for h in hashes]

    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else left
            next_layer.append(hashlib.sha256(left + right).digest())
        layer = next_layer

    return layer[0].hex()


------------------------------------------------------------

Manifest Generator

------------------------------------------------------------
def generatephase1manifest(root: Path) -> None:
    """
    Generate all Phase-1 logs and manifest files.
    """
    shards_root = root / "shards"
    logs_root = root / "logs"
    logsroot.mkdir(parents=True, existok=True)

    validation_log = []
    hash_log = {}
    manifest_entries = []

    # Deterministic traversal of all shard files
    for shardpath in walksorted(shards_root):
        if not shardpath.isfile() or shard_path.suffix != ".json":
            continue

        relpath = shardpath.relativeto(root).asposix()

        # Validate shard (schema + canonical hash + timestamp chain)
        validationresult = validateshard(shard_path)
        validation_log.append({
            "path": rel_path,
            "valid": validation_result["valid"],
            "errors": validation_result.get("errors", []),
        })

        # Load canonical shard
        sharddata = canonicalizedict(shardpath.readtext())

        canonicalhashvalue = sharddata["canonicalhash"]
        extractor = shard_data["extractor"]
        extractorversion = sharddata["extractor_version"]

        hashlog[relpath] = canonicalhashvalue

        manifest_entries.append({
            "path": rel_path,
            "canonicalhash": canonicalhash_value,
            "extractor": extractor,
            "extractorversion": extractorversion,
        })

    # Sort manifest entries lexicographically by path
    manifestentries = sorted(manifestentries, key=lambda x: x["path"])

    # Compute Merkle root (optional but recommended)
    sortedhashes = sorted([entry["canonicalhash"] for entry in manifest_entries])
    merkleroot = computemerkleroot(sortedhashes)

    # Logical timestamp for manifest (seq = number of shards)
    logical_timestamp = {
        "seq": len(manifest_entries),
        "prevhash": merkleroot,
    }

    # Build manifest
    manifest = {
        "phase": 1,
        "version": "1.0",
        "logicaltimestamp": logicaltimestamp,
        "shards": manifest_entries,
        "roothash": merkleroot,
    }

    # Write logs + manifest using canonical JSON
    (logsroot / "phase1validation.json").write_text(
        canonicalizestr(validationlog)
    )

    (logsroot / "phase1hashes.json").write_text(
        canonicalizestr(hashlog)
    )

    (root / "phase1manifest.json").writetext(
        canonicalize_str(manifest)
    )
`

---

WHY THIS IMPLEMENTATION IS CORRECT

1. Deterministic traversal
walk_sorted() ensures:

- lexicographic ordering  
- stable across OS  
- stable across filesystems  
- stable across runs  

2. Canonical JSON everywhere
All outputs use:

- RFC 8785 canonical JSON  
- canonical UTF‑8  
- canonical dict ordering  

3. Manifest entries are sorted
This ensures:

- reproducibility  
- stable hashing  
- stable Merkle root  

4. Merkle root is deterministic
Even with odd numbers of leaves.

5. Logical timestamp is constitutional
`
seq = number of shards
prevhash = merkleroot
`

6. Validation log is complete
Every shard is validated:

- schema  
- canonical hash  
- timestamp chain  

7. Hash log is sorted and canonical
This is required for:

- Phase‑5 CAS Evaluator  
- Phase‑7 Lineage Agent  
- Phase‑8 Stability Engine  

---

WHAT THIS ENABLES

With this manifest generator:

- Phase‑1 becomes a true genesis ledger  
- Phase‑5 can enforce constitutional invariants  
- Phase‑7 agents can rely on stable lineage  
- Phase‑8 hyperstability can anchor to Phase‑1  
- Phase‑9 omnistructure can unify structures  

This is the foundation of the entire NEXUS‑I system.

---
---

Below is a fixed and tightened Phase‑1 Manifest Generator v1, incorporating:

- correct JSON parsing  
- consistent naming  
- Merkle over manifest order  
- domain separation in the Merkle tree  
- robust error handling  
- richer validation log  
- self‑verifying manifest hash  
- explicit shard_count  

`python
"""
Phase-1 Manifest Generator v1 — NEXUS-I (Hardened)
Produces:
  - /logs/phase1_validation.json
  - /logs/phase1_hashes.json
  - /phase1_manifest.json

All outputs:
  - deterministic
  - RFC 8785 canonical JSON
  - lexicographically ordered
  - cryptographically anchored
"""

from future import annotations
import hashlib
import unicodedata
from pathlib import Path
from typing import Dict, List, Any

import rfc8785

from canonicalizer import (
    canonicalize_bytes,
    canonicalize_dict,
    canonicalize_str,
)
from validator import validate_shard  # Phase-1 shard validator
from deterministicio import walksorted  # deterministic traversal


LEAF_PREFIX = b"\x00"
NODE_PREFIX = b"\x01"


def normalizepathforsort(p: Path) -> bytes:
    """
    Normalize path for deterministic Unicode-aware sorting.
    """
    s = p.as_posix()
    s = unicodedata.normalize("NFC", s)
    return s.encode("utf-8")


------------------------------------------------------------

Merkle root with domain separation

------------------------------------------------------------
def computemerkleroot(hashes: List[str]) -> str:
    """
    Compute a Merkle root from a list of canonical_hash values
    in the given order, with domain separation between leaves
    and internal nodes.
    """
    if not hashes:
        return hashlib.sha256(b"").hexdigest()

    layer = [hashlib.sha256(LEAF_PREFIX + bytes.fromhex(h)).digest() for h in hashes]

    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i + 1] if i + 1 < len(layer) else left
            next_layer.append(
                hashlib.sha256(NODE_PREFIX + left + right).digest()
            )
        layer = next_layer

    return layer[0].hex()


------------------------------------------------------------

Manifest Generator

------------------------------------------------------------
def generatephase1manifest(root: Path) -> None:
    """
    Generate all Phase-1 logs and manifest files.
    """
    shards_root = root / "shards"
    logs_root = root / "logs"
    logsroot.mkdir(parents=True, existok=True)

    validation_log: List[Dict[str, Any]] = []
    hash_log: Dict[str, str] = {}
    manifest_entries: List[Dict[str, Any]] = []

    # Deterministic traversal of all shard files
    for shardpath in walksorted(shardsroot, key=normalizepathfor_sort):
        if not shardpath.isfile() or shard_path.suffix != ".json":
            continue

        relpath = shardpath.relativeto(root).asposix()

        # Validate shard (schema + canonical hash + timestamp chain)
        try:
            validationresult = validateshard(shard_path)
            valid = validation_result["valid"]
            errors = validation_result.get("errors", [])
        except Exception as e:
            valid = False
            errors = [f"validation_exception: {e!r}"]

        # Load shard as canonical dict (strict parse)
        shard_data: Dict[str, Any]
        try:
            rawjson = shardpath.read_text(encoding="utf-8")
            parsed = rfc8785.loads(raw_json)
            sharddata = canonicalizedict(parsed)
            canonicalhashvalue = sharddata["canonicalhash"]
            extractor = shard_data["extractor"]
            extractorversion = sharddata["extractor_version"]
        except Exception as e:
            # Corrupt shard: record and continue
            validation_log.append({
                "path": rel_path,
                "valid": False,
                "errors": errors + [f"parse_exception: {e!r}"],
                "canonical_hash": None,
            })
            continue

        # Update logs
        validation_log.append({
            "path": rel_path,
            "valid": valid,
            "errors": errors,
            "canonicalhash": canonicalhash_value,
        })

        hashlog[relpath] = canonicalhashvalue

        manifest_entries.append({
            "path": rel_path,
            "canonicalhash": canonicalhash_value,
            "extractor": extractor,
            "extractorversion": extractorversion,
        })

    # Sort manifest entries lexicographically by path
    manifestentries = sorted(manifestentries, key=lambda x: x["path"])

    # Merkle root over manifest order
    hashesinorder = [entry["canonicalhash"] for entry in manifestentries]
    merkleroot = computemerkleroot(hashesin_order)

    shardcount = len(manifestentries)

    logical_timestamp = {
        "seq": shard_count,
        "prevhash": merkleroot,
    }

    # Build manifest without manifest_hash first
    manifest: Dict[str, Any] = {
        "phase": 1,
        "version": "1.0",
        "logicaltimestamp": logicaltimestamp,
        "shards": manifest_entries,
        "roothash": merkleroot,
        "shardcount": shardcount,
    }

    # Self-verifying manifest: compute manifest_hash over manifest without hash
    manifestbytes = canonicalizebytes(manifest)
    manifesthash = hashlib.sha256(manifestbytes).hexdigest()
    manifest["manifesthash"] = manifesthash

    # Write logs + manifest using canonical JSON
    (logsroot / "phase1validation.json").write_text(
        canonicalizestr(validationlog),
        encoding="utf-8",
    )

    (logsroot / "phase1hashes.json").write_text(
        canonicalizestr(hashlog),
        encoding="utf-8",
    )

    (root / "phase1manifest.json").writetext(
        canonicalize_str(manifest),
        encoding="utf-8",
    )
`