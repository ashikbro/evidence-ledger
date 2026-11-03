# Evidence Ledger

An auditable evidence graph for research and AI-assisted decisions.

## Why this project

AI systems can produce persuasive answers without preserving the chain of
evidence behind them. Evidence Ledger is intended to make claims traceable:
every claim should connect to its source, extraction method, transformation
history, and confidence level.

## MVP

- Capture claims and source references with stable identifiers.
- Preserve excerpts, timestamps, and source metadata.
- Record how a claim was transformed or summarized.
- Expose a review view showing unsupported or conflicting claims.
- Export a portable, machine-readable evidence bundle.

## Non-goals for the first release

- Training or hosting a foundation model.
- Replacing domain experts or formal peer review.
- Building a general-purpose notes application.

## Proposed stack

- **API:** Python, FastAPI, and Pydantic
- **Storage:** PostgreSQL with an append-only event history
- **Search:** PostgreSQL full-text search first; pluggable semantic search later
- **UI:** React and TypeScript
- **Quality:** pytest, contract tests, and reproducible export fixtures

## First milestone

1. Define the claim, source, citation, and transformation model.
2. Implement append-only persistence and evidence-bundle export.
3. Add a minimal review interface for claim coverage and conflicts.
4. Publish one end-to-end example using public research material.

## Status

**MVP core implemented.** The dependency-free `EvidenceLedger` class supports
claims, sources, typed evidence links, review status, an append-only event
history, a review queue for unsupported or conflicting claims, and portable
JSON bundles.

## Development

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

The export format is versioned as `evidence-ledger/v1`. Content is never
silently replaced: claim reviews, source additions, and links are recorded in
the append-only event history.
