import json

import pytest

from evidence_ledger import EvidenceLedger


def test_claim_source_link_review_and_export():
    ledger = EvidenceLedger()
    source = ledger.add_source("Public report", "https://example.test/report", "The report states the result.")
    claim = ledger.add_claim("The result is reproducible.", confidence=0.8)
    ledger.link(claim.id, source.id, "supports", "Direct excerpt")
    assert ledger.review_queue()[0].id == claim.id
    assert ledger.review(claim.id, "supported").status == "supported"
    bundle = json.loads(ledger.export_json())
    assert bundle["format"] == "evidence-ledger/v1"
    assert bundle["links"][0]["relation"] == "supports"
    assert len(bundle["events"]) == 4


def test_conflicting_claims_remain_reviewable():
    ledger = EvidenceLedger()
    source = ledger.add_source("Counterpoint", "https://example.test/counterpoint", "An opposing result.")
    claim = ledger.add_claim("The result is safe.")
    ledger.link(claim.id, source.id, "contradicts")
    assert claim.id in [item.id for item in ledger.review_queue()]


def test_input_validation():
    ledger = EvidenceLedger()
    with pytest.raises(ValueError, match="between"):
        ledger.add_claim("Claim", confidence=2)
    with pytest.raises(ValueError, match="required"):
        ledger.add_source("", "uri", "excerpt")
