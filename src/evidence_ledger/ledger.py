"""SQLite-backed claims, sources, and auditable evidence links."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    uri: str
    excerpt: str
    captured_at: str


@dataclass(frozen=True)
class Claim:
    id: str
    text: str
    confidence: float
    status: str
    created_at: str


class EvidenceLedger:
    """Store claims and their source references without overwriting history."""

    def __init__(self, path: str | Path = ":memory:"):
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS claims (
                id TEXT PRIMARY KEY, text TEXT NOT NULL, confidence REAL NOT NULL,
                status TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, uri TEXT NOT NULL,
                excerpt TEXT NOT NULL, captured_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS evidence_links (
                claim_id TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
                source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                relation TEXT NOT NULL, note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                PRIMARY KEY (claim_id, source_id, relation)
            );
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL,
                entity_id TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL
            );
            """
        )

    def close(self) -> None:
        self.connection.close()

    def add_source(self, title: str, uri: str, excerpt: str) -> Source:
        title, uri, excerpt = title.strip(), uri.strip(), excerpt.strip()
        if not title or not uri or not excerpt:
            raise ValueError("source title, URI, and excerpt are required")
        captured_at = self._now()
        source = Source(uuid4().hex, title, uri, excerpt, captured_at)
        self.connection.execute(
            "INSERT INTO sources VALUES (?, ?, ?, ?, ?)",
            (source.id, source.title, source.uri, source.excerpt, source.captured_at),
        )
        self._event("source.created", source.id, asdict(source))
        self.connection.commit()
        return source

    def add_claim(self, text: str, confidence: float = 0.5) -> Claim:
        text = text.strip()
        if not text:
            raise ValueError("claim text is required")
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        claim = Claim(uuid4().hex, text, confidence, "unreviewed", self._now())
        self.connection.execute("INSERT INTO claims VALUES (?, ?, ?, ?, ?)", tuple(asdict(claim).values()))
        self._event("claim.created", claim.id, asdict(claim))
        self.connection.commit()
        return claim

    def link(self, claim_id: str, source_id: str, relation: str = "supports", note: str = "") -> None:
        self._require("claims", claim_id, "claim")
        self._require("sources", source_id, "source")
        if relation not in {"supports", "contradicts", "context"}:
            raise ValueError("relation must be supports, contradicts, or context")
        created_at = self._now()
        self.connection.execute(
            "INSERT OR IGNORE INTO evidence_links VALUES (?, ?, ?, ?, ?)",
            (claim_id, source_id, relation, note.strip(), created_at),
        )
        self._event("evidence.linked", claim_id, {"source_id": source_id, "relation": relation, "note": note.strip()})
        self.connection.commit()

    def review(self, claim_id: str, status: str) -> Claim:
        if status not in {"unreviewed", "supported", "contested", "rejected"}:
            raise ValueError("invalid review status")
        self._require("claims", claim_id, "claim")
        self.connection.execute("UPDATE claims SET status = ? WHERE id = ?", (status, claim_id))
        self._event("claim.reviewed", claim_id, {"status": status})
        self.connection.commit()
        return self.claim(claim_id)

    def claim(self, claim_id: str) -> Claim:
        row = self.connection.execute("SELECT * FROM claims WHERE id = ?", (claim_id,)).fetchone()
        if row is None:
            raise KeyError(f"claim {claim_id} does not exist")
        return Claim(**dict(row))

    def review_queue(self) -> list[Claim]:
        rows = self.connection.execute(
            """
            SELECT claims.* FROM claims
            LEFT JOIN evidence_links ON evidence_links.claim_id = claims.id
            GROUP BY claims.id
            HAVING COUNT(CASE WHEN evidence_links.relation = 'supports' THEN 1 END) = 0
                OR COUNT(CASE WHEN evidence_links.relation = 'contradicts' THEN 1 END) > 0
                OR claims.status = 'unreviewed'
            ORDER BY claims.created_at
            """
        ).fetchall()
        return [Claim(**dict(row)) for row in rows]

    def export_bundle(self) -> dict[str, Any]:
        claims = [dict(row) for row in self.connection.execute("SELECT * FROM claims ORDER BY created_at")]
        sources = [dict(row) for row in self.connection.execute("SELECT * FROM sources ORDER BY captured_at")]
        links = [dict(row) for row in self.connection.execute("SELECT * FROM evidence_links ORDER BY created_at")]
        events = [dict(row) for row in self.connection.execute("SELECT * FROM events ORDER BY id")]
        return {"format": "evidence-ledger/v1", "claims": claims, "sources": sources, "links": links, "events": events}

    def export_json(self) -> str:
        return json.dumps(self.export_bundle(), indent=2, sort_keys=True)

    def _event(self, kind: str, entity_id: str, payload: dict[str, Any]) -> None:
        self.connection.execute(
            "INSERT INTO events(kind, entity_id, payload, created_at) VALUES (?, ?, ?, ?)",
            (kind, entity_id, json.dumps(payload, sort_keys=True), self._now()),
        )

    def _require(self, table: str, entity_id: str, label: str) -> None:
        if self.connection.execute(f"SELECT 1 FROM {table} WHERE id = ?", (entity_id,)).fetchone() is None:
            raise KeyError(f"{label} {entity_id} does not exist")

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
