# Evidence Ledger

**Auditable evidence graph** for research and AI-assisted decisions.

Make claims traceable: every claim connects to its source, extraction method, transformation history, and confidence level.

## What it does now

- Claims and source references with stable identifiers
- Typed evidence links
- Review status and queue for unsupported or conflicting claims
- Append-only event history
- Portable JSON evidence bundles (`evidence-ledger/v1`)

## Quick start

```sh
python -m venv .venv
.venv/bin/pip install pytest
PYTHONPATH=src .venv/bin/pytest
```

```python
from evidence_ledger import EvidenceLedger

ledger = EvidenceLedger("evidence.db")
source = ledger.add_source("Research report", "https://example.test/report", "Relevant excerpt")
claim = ledger.add_claim("A traceable claim", confidence=0.8)
ledger.link(claim.id, source.id, "supports")
print(ledger.export_json())
```

## Browser demo

```sh
python -m http.server 8000 --directory web
```

## Keywords

knowledge graph · evidence · research · ai · audit · python · provenance
