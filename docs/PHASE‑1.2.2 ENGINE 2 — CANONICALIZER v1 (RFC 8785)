---

# **PHASE‑1 ENGINE 2 — CANONICALIZER v1 (RFC 8785)**  
### *“The byte‑level normalizer that guarantees structural determinism.”*

Canonicalizer v1 is the **second engine** in the Phase‑1 deterministic substrate.  
It transforms extractor output into **canonical JSON**, ensuring that:

- every shard is byte‑for‑byte reproducible  
- every hash is stable forever  
- every downstream engine receives identical input  
- no nondeterministic formatting survives  

This engine is the **mathematical core** of Phase‑1.

---

# **1. PURPOSE**

Canonicalizer v1 exists to:

- convert Python structures into RFC 8785 canonical JSON  
- normalize all values (numbers, booleans, nulls, strings)  
- enforce deterministic key ordering  
- eliminate whitespace and formatting drift  
- produce canonical bytes for hashing  
- guarantee cross‑machine reproducibility  

It is the **only** engine allowed to produce canonical JSON.

---

# **2. CONSTITUTIONAL REQUIREMENTS**

Canonicalizer v1 must be:

### **✔ RFC 8785 compliant**  
No custom rules, no deviations.

### **✔ Pure**  
No side effects, no environment access.

### **✔ Deterministic**  
Same input → same canonical bytes.

### **✔ Total**  
Must accept any JSON‑serialisable value.

### **✔ Stable**  
Output must not change across Python versions, OSes, or locales.

### **✔ Hash‑safe**  
Canonical bytes must be safe for SHA‑256 hashing.

### **✔ Schema‑neutral**  
Canonicalizer does not enforce schemas — that is the validator’s job.

---

# **3. INPUT → OUTPUT CONTRACT**

### **Input**
Any JSON‑serialisable Python object:

- dict  
- list  
- string  
- number  
- boolean  
- null  

### **Output**
Three canonical forms:

1. **canonical bytes** (UTF‑8, RFC 8785)  
2. **canonical string** (UTF‑8 decoded)  
3. **canonical Python structure** (round‑tripped)  

### **Hash**
```
canonical_hash = sha256(canonical_bytes)
```

This is the **canonical_hash** stored in every Phase‑1 shard.

---

# **4. WHAT THE CANONICALIZER DOES**

### **4.1 Sorts keys lexicographically**
RFC 8785 defines a strict ordering:

- Unicode codepoint order  
- No locale influence  
- No case folding  

### **4.2 Normalizes numbers**
Examples:

- `1.0` → `1`  
- `0.0` → `0`  
- `1e3` → `1000`  
- `-0` → `0`  

### **4.3 Normalizes booleans and null**
- `True` → `true`  
- `False` → `false`  
- `None` → `null`  

### **4.4 Normalizes strings**
- escapes  
- Unicode normalization  
- no extraneous whitespace  

### **4.5 Removes all formatting drift**
No:

- indentation  
- newlines  
- spaces  
- trailing commas  

### **4.6 Produces canonical UTF‑8 bytes**
This is the **ground truth** for hashing.

---

# **5. WHAT THE CANONICALIZER DOES *NOT* DO**

Canonicalizer v1 must **not**:

- modify semantic values  
- reorder lists  
- infer types  
- drop keys  
- add keys  
- validate schemas  
- interpret content  
- perform compression  
- perform pretty‑printing  

It is a **pure normalizer**, not a validator or transformer.

---

# **6. ERROR HANDLING**

Canonicalizer v1 must:

- raise a deterministic `CanonicalizationError` on invalid input  
- never produce partial output  
- never silently coerce unsupported types  
- never swallow exceptions  

If extractors produce invalid structures, the canonicalizer must fail fast.

---

# **7. DEPENDENCY LOCKING**

Canonicalizer v1 depends on:

- **rfc8785** (strict version pin + hash)

This dependency must be:

- locked in `requirements.txt` or `poetry.lock`  
- verified via constitutional test vectors  
- never upgraded without a constitutional vote  

This prevents canonicalization drift.

---

# **8. CONSTITUTIONAL TEST VECTOR**

Canonicalizer v1 must pass the frozen test vector:

```
{"b":1,"a":2}
→ canonical bytes hex = 7b2261223a322c2262223a317d
```

Any deviation is a constitutional violation.

---

# **9. DOWNSTREAM DEPENDENCIES**

Canonicalizer v1 feeds:

- Shard Writer v1  
- Shard Validator v1  
- Manifest Generator v1  
- Phase‑5 CAS Evaluator  
- Phase‑7 Lineage Agent  
- Phase‑8 Stability Engine  
- Phase‑9 Omnistructure Engine  

If canonicalization drifts, **every downstream hash breaks**.

---

# **10. COMPLETION CRITERIA**

Canonicalizer v1 is complete when:

- RFC 8785 compliance is verified  
- canonical bytes are stable across environments  
- canonical_hash is correct  
- test vectors pass  
- dependency version is locked  
- error handling is deterministic  
- round‑trip canonicalization is correct  

This engine is the **mathematical anchor** of the NEXUS‑I substrate.

---
