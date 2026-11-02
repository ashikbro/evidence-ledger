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

Project initialized locally. The GitHub repository will be published once
repository-creation permission is available for the authenticated account.
