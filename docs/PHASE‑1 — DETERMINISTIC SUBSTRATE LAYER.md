---

PHASE‑1 — DETERMINISTIC SUBSTRATE LAYER (NEXUS‑I)

“The constitutional ground truth of the system.”

Phase‑1 defines the immutable, deterministic substrate upon which all later phases depend.  
It is intentionally minimal, rigid, and drift‑proof.

This updated specification incorporates the corrections required for full constitutional compliance.

---

1. PURPOSE OF PHASE‑1

Phase‑1 establishes:

- deterministic extraction  
- deterministic canonicalization (RFC 8785)  
- deterministic hashing  
- deterministic shard writing  
- deterministic validation  
- deterministic file ordering  
- deterministic lineage anchors  
- deterministic manifest + logs  

Phase‑1 must be:

- reproducible  
- immutable  
- schema‑stable  
- drift‑proof  
- environment‑independent  

If Phase‑1 drifts, the entire system collapses.

---

2. PHASE‑1 COMPONENTS (UPDATED)

Phase‑1 consists of six engines:

1. Extractor Suite v1  
2. Canonicalizer v1 (RFC 8785)  
3. Shard Writer v1  
4. Shard Validator v1  
5. Deterministic IO Layer v1  
6. Phase‑1 Manifest + Logs Generator v1

These engines form the constitutional substrate.

---

3. EXTRACTOR SUITE v1 (UPDATED)

Responsibilities
- extract minimal, structural, deterministic fields  
- no timestamps from filesystem  
- no nondeterministic metadata  
- no inference  
- no heuristics  
- no environment‑dependent behavior  

Output Schema
`
{
  "assetid": "<contenthash>",
  "sourcepath": "<relativepath>",
  "filetype": "<canonicaltype>",
  "size_bytes": <int>,
  "hash_sha256": "<sha256>",
  "extractor": "<name>",
  "extractor_version": "<semver>"
}
`

Removed Fields
❌ created  
❌ modified  
❌ any filesystem timestamp  
❌ any nondeterministic metadata  

Controlled Vocabulary
file_type must be one of:

- MIME type  
- or NEXUS canonical type list (Phase‑1 Appendix A)

Extractors must be:

- pure  
- stateless  
- deterministic  
- schema‑stable  

---

4. CANONICALIZER v1 (RFC 8785)

Responsibilities
- convert extractor output into canonical JSON using RFC 8785  
- remove nondeterministic fields  
- normalize numeric, boolean, null formats  
- produce byte‑stable output across machines  

Output
canonicaldict and canonicalbytes

Guarantees
- byte‑for‑byte identical output for identical input  
- stable across OS, locale, Python version  
- stable across time  
- stable across environments  

This is the first constitutional drift‑prevention layer.

---

5. SHARD WRITER v1 (UPDATED)

Shard Layout
The updated, constitutional layout is:

`
/shards/<extractor>/<normalized_hash>.json
`

This preserves:

- extractor provenance  
- deduplication  
- collision resistance  
- auditability  

Responsibilities
- write canonicalized output to deterministic path  
- compute canonical hash = SHA‑256(canonical_bytes)  
- attach Phase‑1 metadata  
- write atomically  

Shard Metadata
`
{
  "phase": 1,
  "version": "1.0",
  "canonical_hash": "<sha256>",
  "extractor": "<name>",
  "extractor_version": "<semver>",
  "logicaltimestamp": "<seq:prevhash>"
}
`

Logical Timestamp
Phase‑1 uses deterministic logical time, not wall‑clock time:

`
logical_timestamp = {
  "seq": <monotonic integer>,
  "prev_hash": <sha256 of previous shard>,
}
`

This creates a deterministic temporal chain.

---

6. SHARD VALIDATOR v1

Responsibilities
- validate extractor schema  
- validate canonical structure  
- validate canonical hash  
- validate shard metadata  
- validate deterministic naming rules  
- validate logical timestamp chain  

Guarantees
- no malformed shards  
- no nondeterministic shards  
- no schema drift  
- no missing extractor metadata  
- no broken logical time chain  

Validator v1 is the constitutional gatekeeper.

---

7. DETERMINISTIC IO LAYER v1

Responsibilities
- enforce deterministic directory traversal  
- enforce deterministic file ordering  
- enforce deterministic read/write operations  
- enforce atomic writes  

Contract
`
walk_sorted(path):
    yield all files in lexicographically sorted order
`

Guarantees
- no OS‑dependent ordering  
- no race conditions  
- no nondeterministic traversal  

This layer ensures Phase‑1 is reproducible anywhere.

---

8. PHASE‑1 MANIFEST + LOGS GENERATOR v1

Phase‑1 must produce:

1. /logs/phase1_validation.json
List of all validation results.

2. /logs/phase1_hashes.json
Mapping of:

`
<extractor>/<normalizedhash> → canonicalhash
`

Sorted lexicographically.

3. /phase1_manifest.json
Contains:

`
{
  "phase": 1,
  "version": "1.0",
  "shards": [
      {
        "path": "...",
        "canonical_hash": "...",
        "extractor": "...",
        "extractor_version": "..."
      }
  ],
  "roothash": "<optionalmerkle_root>",
  "logicaltimestamp": "<seq:prevhash>"
}
`

This is the genesis ledger anchor.

---

9. PHASE‑1 EXECUTION FLOW (UPDATED)

`
[1] Extractor Suite v1
        ↓
[2] Canonicalizer v1 (RFC 8785)
        ↓
[3] Shard Writer v1
        ↓
[4] Shard Validator v1
        ↓
[5] Deterministic IO Layer v1
        ↓
[6] Manifest + Logs Generator v1
`

This flow is strict, immutable, and constitutional.

---

10. PHASE‑1 COMPLETION CRITERIA (UPDATED)

Phase‑1 is complete when:

- all extractors produce deterministic output  
- all canonicalization is RFC 8785‑compliant  
- all shards validate  
- all hashes match  
- all file ordering is deterministic  
- all metadata is deterministic  
- manifest + logs are produced  
- the entire Phase‑1 run is byte‑for‑byte reproducible  

This is the Phase‑1 Determinism Test.

---

11. PHASE‑1 GUARANTEES

✔ Deterministic

✔ Reproducible

✔ Drift‑Proof

✔ Schema‑Stable

✔ Immutable

✔ Constitutional

✔ Genesis‑Ledger‑Ready

---

12. PHASE‑1 IS NOW FULLY CONSTITUTIONAL

This updated specification:

- resolves all determinism conflicts  
- aligns with the current codebase  
- incorporates your improvements  
- enables Phase‑5 governance  
- enables Phase‑7 autonomous agents  
- enables Phase‑8 hyperstability  
- enables Phase‑9 omnistructure  

Phase‑1 is now a true substrate.

---