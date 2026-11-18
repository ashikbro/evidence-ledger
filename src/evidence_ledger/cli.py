"""Minimal CLI for the evidence ledger."""

import argparse
import json
from pathlib import Path

from evidence_ledger.ledger import EvidenceLedger


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditable evidence ledger")
    parser.add_argument("command", choices=["demo", "export"])
    parser.add_argument("--db", type=Path, default=Path(":memory:"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    ledger = EvidenceLedger(args.db)
    if args.command == "demo":
        source = ledger.add_source("Example Report", "https://example.com/report", "Key finding excerpt.")
        claim = ledger.add_claim("The finding is supported by the report.", confidence=0.8)
        ledger.link(claim.id, source.id, "supports")
        print("Demo ledger created.")
        print("Review queue:", len(ledger.review_queue()), "claims")
    elif args.command == "export":
        data = ledger.export_json()
        if args.output:
            args.output.write_text(data)
            print(f"Exported to {args.output}")
        else:
            print(data)


if __name__ == "__main__":
    main()
