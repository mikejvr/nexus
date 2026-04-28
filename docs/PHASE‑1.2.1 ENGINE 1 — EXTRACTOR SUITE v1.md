---

# **PHASE‑1 ENGINE 1 — EXTRACTOR SUITE v1**  
### *“The structural truth‑extraction layer of the deterministic substrate.”*

Phase‑1 Extractor Suite v1 is the **first engine** in the NEXUS‑I substrate.  
Its job is simple, strict, and non‑negotiable:

> Extract **only** structural, deterministic facts from a file — nothing more.

This engine defines the **ground truth** of every asset in the system.

---

# **1. PURPOSE**

Extractor Suite v1 exists to:

- read raw files  
- extract minimal structural metadata  
- classify the file deterministically  
- compute content hashes  
- produce a stable, schema‑validated dict  
- avoid all nondeterministic fields  

It is the **only** engine allowed to touch raw input files.

Everything downstream — canonicalization, shard writing, lineage, governance — depends on the purity of this step.

---

# **2. CONSTITUTIONAL REQUIREMENTS**

Extractors must be:

### **✔ Pure**
No global state, no environment access, no randomness.

### **✔ Deterministic**
Same input → same output, byte‑for‑byte.

### **✔ Stateless**
No caching, no memoization, no external references.

### **✔ Schema‑Stable**
Output must match `phase1_extractor.schema.json`.

### **✔ Minimal**
Extractors may **not** infer, interpret, or guess.

### **✔ Non‑semantic**
No content analysis, no heuristics, no decoding beyond structural parsing.

### **✔ No nondeterministic fields**
Forbidden:
- filesystem timestamps  
- OS metadata  
- UUIDs  
- environment variables  
- locale‑dependent values  

---

# **3. INPUT → OUTPUT CONTRACT**

### **Input**
A file path inside the Phase‑1 intake directory.

### **Output**
A dict matching the extractor schema:

```
{
  "asset_id": "<sha256 of file content>",
  "source_path": "<relative path>",
  "file_type": "<canonical type>",
  "size_bytes": <int>,
  "content_sha256": "<sha256>",
  "extractor": "<name>",
  "extractor_version": "<semver>",
  "schema_version": "1.0"
}
```

This is the **only** allowed output shape.

---

# **4. WHAT EXTRACTORS ARE ALLOWED TO DO**

Extractors may:

- read file bytes  
- compute SHA‑256  
- detect file type using deterministic rules  
- parse minimal structural metadata (e.g., image width/height, PDF version)  
- normalize values (e.g., lowercase extensions)  
- validate structural integrity (e.g., ZIP header present)  

---

# **5. WHAT EXTRACTORS ARE *NOT* ALLOWED TO DO**

Extractors may **not**:

- read filesystem timestamps  
- read OS metadata  
- read environment variables  
- use randomness  
- use non‑stdlib libraries  
- perform semantic analysis  
- perform content inference  
- decode formats beyond structural parsing  
- generate warnings that depend on environment  
- include nondeterministic fields  

This is enforced by the schema and validator.

---

# **6. EXTRACTOR TYPES**

Phase‑1 includes a suite of deterministic extractors:

### **1. Binary Extractor**
For unknown or unstructured files.

### **2. Text Extractor**
For `.txt`, `.md`, `.csv`, `.json`, etc.

### **3. Image Extractor**
Reads:
- width  
- height  
- bit depth  
- format signature  

### **4. PDF Extractor**
Reads:
- PDF version  
- page count (if deterministically extractable)  

### **5. ZIP Extractor**
Reads:
- entry count  
- compression flags  

### **6. HTML Extractor**
Reads:
- doctype  
- tag count  
- structural validity  

### **7. SVG Extractor**
Reads:
- root element  
- namespace  
- viewBox  

All extractors follow the same contract.

---

# **7. DETERMINISTIC FILE TYPE CLASSIFICATION**

Extractors must classify files using:

- extension (lowercased)  
- magic bytes (if available)  
- deterministic fallback rules  

Example:

```
.pdf → application/pdf
.png → image/png
.html → text/html
```

If ambiguous:

```
unknown/<sha256-prefix>
```

This prevents nondeterministic classification.

---

# **8. ERROR HANDLING**

Extractors must:

- never raise uncaught exceptions  
- return a valid payload even for malformed files  
- include deterministic warnings (optional)  
- never include stack traces or environment‑dependent messages  

If a file is unreadable:

```
file_type: "unknown"
size_bytes: 0
content_sha256: sha256("")
```

---

# **9. VERSIONING**

Each extractor must declare:

```
extractor_version: "1.0.0"
schema_version: "1.0"
```

Version bumps are constitutional events.

---

# **10. VALIDATION**

Extractor output is validated by:

- `phase1_extractor.schema.json`  
- Phase‑1 Validator  
- Phase‑1 Manifest Generator  

Any deviation is a constitutional violation.

---

# **11. DOWNSTREAM DEPENDENCIES**

Extractor Suite v1 feeds:

- Canonicalizer v1  
- Shard Writer v1  
- Shard Validator v1  
- Manifest Generator v1  
- Phase‑5 CAS Evaluator  
- Phase‑7 Lineage Agent  
- Phase‑8 Stability Engine  
- Phase‑9 Omnistructure Engine  

If extractors drift, the entire system collapses.

---

# **12. COMPLETION CRITERIA**

Extractor Suite v1 is complete when:

- all extractors produce deterministic output  
- all outputs validate against schema  
- no nondeterministic fields exist  
- file type classification is stable  
- content hashing is correct  
- extractor provenance is included  
- schema_version is correct  

This is the **first gate** of the NEXUS‑I substrate.

---
