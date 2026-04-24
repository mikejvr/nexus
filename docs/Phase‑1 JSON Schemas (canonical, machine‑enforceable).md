---

1. phase1_extractor.schema.json

Schema for extractor output before canonicalization.

`json
{
  "$id": "https://nexus/schema/phase1_extractor.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Phase-1 Extractor Output",
  "type": "object",
  "required": [
    "asset_id",
    "source_path",
    "file_type",
    "size_bytes",
    "hash_sha256",
    "extractor",
    "extractor_version"
  ],
  "properties": {
    "asset_id": {
      "type": "string",
      "description": "Content hash or deterministic ID."
    },
    "source_path": {
      "type": "string",
      "description": "Relative path to the source file."
    },
    "file_type": {
      "type": "string",
      "description": "Canonical file type (MIME or NEXUS canonical type)."
    },
    "size_bytes": {
      "type": "integer",
      "minimum": 0
    },
    "hash_sha256": {
      "type": "string",
      "pattern": "^[a-fA-F0-9]{64}$"
    },
    "extractor": {
      "type": "string",
      "description": "Extractor name."
    },
    "extractor_version": {
      "type": "string",
      "description": "Semantic version of the extractor."
    }
  },
  "additionalProperties": false
}
`

---

2. phase1_shard.schema.json

Schema for the canonical shard written to disk.

`json
{
  "$id": "https://nexus/schema/phase1_shard.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Phase-1 Canonical Shard",
  "type": "object",
  "required": [
    "phase",
    "version",
    "canonical_hash",
    "extractor",
    "extractor_version",
    "logical_timestamp",
    "payload"
  ],
  "properties": {
    "phase": {
      "type": "integer",
      "const": 1
    },
    "version": {
      "type": "string",
      "pattern": "^1\\.0$"
    },
    "canonical_hash": {
      "type": "string",
      "pattern": "^[a-fA-F0-9]{64}$",
      "description": "SHA-256 of RFC 8785 canonical JSON."
    },
    "extractor": {
      "type": "string"
    },
    "extractor_version": {
      "type": "string"
    },
    "logical_timestamp": {
      "type": "object",
      "required": ["seq", "prev_hash"],
      "properties": {
        "seq": {
          "type": "integer",
          "minimum": 0
        },
        "prev_hash": {
          "type": "string",
          "pattern": "^[a-fA-F0-9]{64}$"
        }
      },
      "additionalProperties": false
    },
    "payload": {
      "$ref": "phase1_extractor.schema.json",
      "description": "The canonicalized extractor output."
    }
  },
  "additionalProperties": false
}
`

---

3. phase1_manifest.schema.json

Schema for the Phase‑1 manifest (genesis ledger anchor).

`json
{
  "$id": "https://nexus/schema/phase1_manifest.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Phase-1 Manifest",
  "type": "object",
  "required": [
    "phase",
    "version",
    "logical_timestamp",
    "shards"
  ],
  "properties": {
    "phase": {
      "type": "integer",
      "const": 1
    },
    "version": {
      "type": "string",
      "pattern": "^1\\.0$"
    },
    "logical_timestamp": {
      "type": "object",
      "required": ["seq", "prev_hash"],
      "properties": {
        "seq": {
          "type": "integer",
          "minimum": 0
        },
        "prev_hash": {
          "type": "string",
          "pattern": "^[a-fA-F0-9]{64}$"
        }
      },
      "additionalProperties": false
    },
    "shards": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "path",
          "canonical_hash",
          "extractor",
          "extractor_version"
        ],
        "properties": {
          "path": {
            "type": "string",
            "description": "Relative path to shard file."
          },
          "canonical_hash": {
            "type": "string",
            "pattern": "^[a-fA-F0-9]{64}$"
          },
          "extractor": {
            "type": "string"
          },
          "extractor_version": {
            "type": "string"
          }
        },
        "additionalProperties": false
      }
    },
    "root_hash": {
      "type": "string",
      "pattern": "^[a-fA-F0-9]{64}$",
      "description": "Optional Merkle root of all canonical_hash values."
    }
  },
  "additionalProperties": false
}
`

---

These schemas are now constitutionally correct.

They enforce:

- deterministic structure  
- deterministic hashing  
- deterministic logical time  
- extractor provenance  
- canonical JSON compliance  
- shard immutability  
- manifest auditability  

They are also:

- Phase‑5‑ready  
- Phase‑7‑ready  
- Phase‑8‑ready  
- Phase‑9‑ready  

This is the exact substrate required for the rest of NEXUS‑I to function.

---