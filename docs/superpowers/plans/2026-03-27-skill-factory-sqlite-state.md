# Skill Factory SQLite State DB Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the SQLite state database (`compiler/db.py`) with schema creation, export/import commands, and a Python API for recording compilations, publications, advice, platform checks, and reconciliations.

**Architecture:** A single `compiler/db.py` module with CLI subcommands (`init`, `export`, `import`) and a `FactoryDB` class that the compiler and publish toolchain will use. TDD with pytest.

**Tech Stack:** Python 3.12+, sqlite3 (stdlib), pytest, uv

**Spec:** `~/repos/skills/docs/superpowers/specs/2026-03-25-skill-factory-design.md` (section: SQLite State Database)

**Depends on:** Plan 1 (scaffolding) — completed, tagged `v0.1.0-scaffold`

---

## File Structure

```
~/repos/skill-factory/
├── compiler/
│   ├── db.py                    # SQLite state DB: schema, CLI, FactoryDB class
│   └── __init__.py              # (exists)
└── tests/
    └── test_db.py               # Tests for db.py
```

---

### Task 1: Write failing tests for schema initialization

**Files:**
- Create: `tests/test_db.py`

- [ ] **Step 1: Write test file with schema init tests**

```python
"""Tests for compiler.db — SQLite state database."""

import json
import sqlite3
from pathlib import Path

import pytest

from compiler.db import FactoryDB


@pytest.fixture
def db_path(tmp_path):
    """Provide a temporary database path."""
    return tmp_path / "state.db"


@pytest.fixture
def db(db_path):
    """Provide an initialized FactoryDB instance."""
    return FactoryDB(db_path)


class TestInit:
    def test_creates_database_file(self, db, db_path):
        assert db_path.exists()

    def test_creates_all_tables(self, db):
        tables = db.list_tables()
        expected = {
            "intents",
            "compilations",
            "publications",
            "advice_log",
            "platform_checks",
            "reconciliations",
        }
        assert expected == set(tables)

    def test_creates_all_views(self, db):
        views = db.list_views()
        expected = {
            "stale_compilations",
            "stale_platforms",
            "compilation_history",
        }
        assert expected == set(views)

    def test_idempotent_init(self, db_path):
        """Running init twice should not error or lose data."""
        db1 = FactoryDB(db_path)
        db1.record_platform_check("claude", None, "2026.03.1", [], "manual")
        db2 = FactoryDB(db_path)
        checks = db2.query("SELECT * FROM platform_checks")
        assert len(checks) == 1

    def test_wal_mode_enabled(self, db):
        result = db.query("PRAGMA journal_mode")
        assert result[0][0] == "wal"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_db.py -v
```

Expected: ImportError — `compiler.db` doesn't exist yet.

- [ ] **Step 3: Commit**

```bash
git add tests/test_db.py
git commit -m "test: add schema initialization tests for state DB"
```

---

### Task 2: Implement schema initialization

**Files:**
- Create: `compiler/db.py`

- [ ] **Step 1: Write the FactoryDB class with schema**

```python
"""SQLite state database for the skill factory.

Usage:
    # As a library
    from compiler.db import FactoryDB
    db = FactoryDB(Path(".factory/state.db"))

    # As a CLI
    python compiler/db.py init
    python compiler/db.py export
    python compiler/db.py import state-export.json
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

TABLES_SQL = """
CREATE TABLE IF NOT EXISTS intents (
    name TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    path TEXT NOT NULL,
    component_count INTEGER,
    shared_ref_count INTEGER,
    stack_aware BOOLEAN DEFAULT FALSE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS compilations (
    id INTEGER PRIMARY KEY,
    intent_name TEXT NOT NULL REFERENCES intents(name),
    intent_version TEXT NOT NULL,
    platform TEXT NOT NULL,
    caps_version TEXT NOT NULL,
    rules_version TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,
    components_emitted TEXT,
    components_skipped TEXT,
    warnings TEXT,
    duration_ms INTEGER
);

CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY,
    version TEXT NOT NULL UNIQUE,
    timestamp TEXT NOT NULL,
    root_hash TEXT NOT NULL,
    factory_commit TEXT NOT NULL,
    published_commit TEXT,
    platform_hashes TEXT NOT NULL,
    manifest TEXT NOT NULL,
    intents_included TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS advice_log (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    intent_name TEXT NOT NULL,
    component_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    model TEXT NOT NULL,
    accepted BOOLEAN,
    override_reason TEXT
);

CREATE TABLE IF NOT EXISTS platform_checks (
    id INTEGER PRIMARY KEY,
    platform TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    previous_version TEXT,
    new_version TEXT,
    changes_found TEXT,
    verified_by TEXT
);

CREATE TABLE IF NOT EXISTS reconciliations (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    platform TEXT NOT NULL,
    published_repo_path TEXT NOT NULL,
    drifted_files TEXT,
    action_taken TEXT
);
"""

VIEWS_SQL = """
CREATE VIEW IF NOT EXISTS stale_compilations AS
SELECT i.name, i.version, c.platform, c.timestamp AS last_compiled,
       i.updated_at AS intent_updated
FROM intents i
LEFT JOIN compilations c ON c.intent_name = i.name
    AND c.id = (SELECT MAX(c2.id) FROM compilations c2
                WHERE c2.intent_name = i.name AND c2.platform = c.platform)
WHERE i.updated_at > COALESCE(c.timestamp, '1970-01-01') OR c.id IS NULL;

CREATE VIEW IF NOT EXISTS stale_platforms AS
SELECT p.platform, p.new_version AS current_version, p.timestamp AS last_checked,
       julianday('now') - julianday(p.timestamp) AS days_since_check
FROM platform_checks p
WHERE p.id = (SELECT MAX(p2.id) FROM platform_checks p2
              WHERE p2.platform = p.platform)
  AND julianday('now') - julianday(p.timestamp) > 30;

CREATE VIEW IF NOT EXISTS compilation_history AS
SELECT c.*, i.version AS current_intent_version,
       CASE WHEN c.intent_version = i.version THEN 'current' ELSE 'outdated' END AS freshness
FROM compilations c
JOIN intents i ON i.name = c.intent_name
ORDER BY c.timestamp DESC;
"""


class FactoryDB:
    """SQLite state database for the skill factory."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(TABLES_SQL)
        self._conn.executescript(VIEWS_SQL)
        self._conn.commit()

    def query(self, sql: str, params: tuple = ()) -> list[tuple]:
        return self._conn.execute(sql, params).fetchall()

    def list_tables(self) -> list[str]:
        rows = self.query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [r[0] for r in rows]

    def list_views(self) -> list[str]:
        rows = self.query("SELECT name FROM sqlite_master WHERE type='view'")
        return [r[0] for r in rows]

    def close(self) -> None:
        self._conn.close()
```

- [ ] **Step 2: Run tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_db.py::TestInit -v
```

Expected: all 5 tests pass.

- [ ] **Step 3: Commit**

```bash
git add compiler/db.py
git commit -m "feat: implement SQLite schema initialization"
```

---

### Task 3: Write failing tests for record methods

**Files:**
- Modify: `tests/test_db.py`

- [ ] **Step 1: Add record method tests**

Append to `tests/test_db.py`:

```python
class TestRecordIntents:
    def test_register_intent(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 2, True)
        rows = db.query("SELECT name, version, stack_aware FROM intents")
        assert rows == [("plan", "1.0.0", True)]

    def test_update_intent(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 2, True)
        db.register_intent("plan", "1.1.0", "intents/plan/intent.md", 4, 2, True)
        rows = db.query("SELECT version FROM intents WHERE name='plan'")
        assert rows == [("1.1.0",)]

    def test_register_intent_sets_timestamps(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 2, True)
        rows = db.query("SELECT created_at, updated_at FROM intents WHERE name='plan'")
        assert rows[0][0] is not None
        assert rows[0][1] is not None


class TestRecordCompilations:
    def test_record_compilation(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 0, False)
        comp_id = db.record_compilation(
            intent_name="plan",
            intent_version="1.0.0",
            platform="claude",
            caps_version="2026.03.1",
            rules_version="2026.03.1",
            status="success",
            components_emitted=["orchestrator", "validator"],
            components_skipped=[],
            warnings=[],
            duration_ms=150,
        )
        assert comp_id > 0
        rows = db.query("SELECT platform, status FROM compilations WHERE id=?", (comp_id,))
        assert rows == [("claude", "success")]

    def test_record_compilation_stores_json_arrays(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 1, 0, False)
        comp_id = db.record_compilation(
            intent_name="plan",
            intent_version="1.0.0",
            platform="vscode",
            caps_version="2026.03.1",
            rules_version="2026.03.1",
            status="warning",
            components_emitted=["prompt"],
            components_skipped=["agent"],
            warnings=["Stale capabilities"],
            duration_ms=80,
        )
        row = db.query("SELECT components_emitted, components_skipped, warnings FROM compilations WHERE id=?", (comp_id,))
        assert json.loads(row[0][0]) == ["prompt"]
        assert json.loads(row[0][1]) == ["agent"]
        assert json.loads(row[0][2]) == ["Stale capabilities"]


class TestRecordPublications:
    def test_record_publication(self, db):
        pub_id = db.record_publication(
            version="2026.03.27.1",
            root_hash="abc123",
            factory_commit="def456",
            platform_hashes={"claude": "aaa", "vscode": "bbb"},
            manifest={"version": "2026.03.27.1"},
            intents_included={"plan": "1.0.0"},
        )
        assert pub_id > 0
        rows = db.query("SELECT version, root_hash FROM publications WHERE id=?", (pub_id,))
        assert rows == [("2026.03.27.1", "abc123")]


class TestRecordAdvice:
    def test_record_advice(self, db):
        adv_id = db.record_advice(
            intent_name="plan",
            component_id="orchestrator",
            platform="copilot-native",
            question="Skip or thin-wrap?",
            response="Thin-wrap recommended",
            model="qwen2.5:14b",
            accepted=True,
        )
        assert adv_id > 0


class TestRecordPlatformCheck:
    def test_record_platform_check(self, db):
        check_id = db.record_platform_check(
            platform="claude",
            previous_version="2026.02.1",
            new_version="2026.03.1",
            changes_found=["Added streaming support"],
            verified_by="manual",
        )
        assert check_id > 0


class TestRecordReconciliation:
    def test_record_reconciliation(self, db):
        rec_id = db.record_reconciliation(
            platform="claude",
            published_repo_path="~/repos/skills",
            drifted_files=["claude/plan/SKILL.md"],
            action_taken="backported",
        )
        assert rec_id > 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_db.py -v -k "not TestInit"
```

Expected: AttributeError — methods don't exist yet.

- [ ] **Step 3: Commit**

```bash
git add tests/test_db.py
git commit -m "test: add record method tests for state DB"
```

---

### Task 4: Implement record methods

**Files:**
- Modify: `compiler/db.py`

- [ ] **Step 1: Add record methods to FactoryDB class**

Add these methods to the `FactoryDB` class in `compiler/db.py`:

```python
    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def register_intent(
        self,
        name: str,
        version: str,
        path: str,
        component_count: int,
        shared_ref_count: int,
        stack_aware: bool,
    ) -> None:
        now = self._now()
        self._conn.execute(
            """INSERT INTO intents (name, version, path, component_count,
               shared_ref_count, stack_aware, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET
               version=excluded.version, path=excluded.path,
               component_count=excluded.component_count,
               shared_ref_count=excluded.shared_ref_count,
               stack_aware=excluded.stack_aware, updated_at=excluded.updated_at""",
            (name, version, path, component_count, shared_ref_count, stack_aware, now, now),
        )
        self._conn.commit()

    def record_compilation(
        self,
        intent_name: str,
        intent_version: str,
        platform: str,
        caps_version: str,
        rules_version: str,
        status: str,
        components_emitted: list[str],
        components_skipped: list[str],
        warnings: list[str],
        duration_ms: int,
    ) -> int:
        cursor = self._conn.execute(
            """INSERT INTO compilations
               (intent_name, intent_version, platform, caps_version, rules_version,
                timestamp, status, components_emitted, components_skipped, warnings, duration_ms)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                intent_name, intent_version, platform, caps_version, rules_version,
                self._now(), status,
                json.dumps(components_emitted), json.dumps(components_skipped),
                json.dumps(warnings), duration_ms,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def record_publication(
        self,
        version: str,
        root_hash: str,
        factory_commit: str,
        platform_hashes: dict,
        manifest: dict,
        intents_included: dict,
        published_commit: str | None = None,
    ) -> int:
        cursor = self._conn.execute(
            """INSERT INTO publications
               (version, timestamp, root_hash, factory_commit, published_commit,
                platform_hashes, manifest, intents_included)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                version, self._now(), root_hash, factory_commit, published_commit,
                json.dumps(platform_hashes), json.dumps(manifest),
                json.dumps(intents_included),
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def record_advice(
        self,
        intent_name: str,
        component_id: str,
        platform: str,
        question: str,
        response: str,
        model: str,
        accepted: bool | None = None,
        override_reason: str | None = None,
    ) -> int:
        cursor = self._conn.execute(
            """INSERT INTO advice_log
               (timestamp, intent_name, component_id, platform,
                question, response, model, accepted, override_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                self._now(), intent_name, component_id, platform,
                question, response, model, accepted, override_reason,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def record_platform_check(
        self,
        platform: str,
        previous_version: str | None,
        new_version: str,
        changes_found: list[str],
        verified_by: str,
    ) -> int:
        cursor = self._conn.execute(
            """INSERT INTO platform_checks
               (platform, timestamp, previous_version, new_version,
                changes_found, verified_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                platform, self._now(), previous_version, new_version,
                json.dumps(changes_found), verified_by,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def record_reconciliation(
        self,
        platform: str,
        published_repo_path: str,
        drifted_files: list[str],
        action_taken: str,
    ) -> int:
        cursor = self._conn.execute(
            """INSERT INTO reconciliations
               (timestamp, platform, published_repo_path, drifted_files, action_taken)
               VALUES (?, ?, ?, ?, ?)""",
            (
                self._now(), platform, published_repo_path,
                json.dumps(drifted_files), action_taken,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid
```

- [ ] **Step 2: Run all tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_db.py -v
```

Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add compiler/db.py
git commit -m "feat: implement record methods for state DB"
```

---

### Task 5: Write failing tests for CLI commands

**Files:**
- Modify: `tests/test_db.py`

- [ ] **Step 1: Add CLI tests**

Append to `tests/test_db.py`:

```python
import subprocess


class TestCLI:
    def test_init_creates_database(self, tmp_path):
        db_file = tmp_path / "state.db"
        result = subprocess.run(
            [sys.executable, "compiler/db.py", "init", "--db", str(db_file)],
            capture_output=True, text=True, cwd=str(Path(__file__).parent.parent),
        )
        assert result.returncode == 0
        assert db_file.exists()
        assert "initialized" in result.stdout.lower() or "exists" in result.stdout.lower()

    def test_init_idempotent(self, tmp_path):
        db_file = tmp_path / "state.db"
        for _ in range(2):
            result = subprocess.run(
                [sys.executable, "compiler/db.py", "init", "--db", str(db_file)],
                capture_output=True, text=True, cwd=str(Path(__file__).parent.parent),
            )
            assert result.returncode == 0

    def test_export_creates_json(self, tmp_path):
        db_file = tmp_path / "state.db"
        export_file = tmp_path / "export.json"
        # Init first
        subprocess.run(
            [sys.executable, "compiler/db.py", "init", "--db", str(db_file)],
            capture_output=True, cwd=str(Path(__file__).parent.parent),
        )
        # Export
        result = subprocess.run(
            [sys.executable, "compiler/db.py", "export", "--db", str(db_file), "--output", str(export_file)],
            capture_output=True, text=True, cwd=str(Path(__file__).parent.parent),
        )
        assert result.returncode == 0
        assert export_file.exists()
        data = json.loads(export_file.read_text())
        assert "intents" in data
        assert "compilations" in data

    def test_import_restores_data(self, tmp_path):
        db_file = tmp_path / "state.db"
        export_file = tmp_path / "export.json"
        # Init and add data
        db = FactoryDB(db_file)
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 2, True)
        db.close()
        # Export
        subprocess.run(
            [sys.executable, "compiler/db.py", "export", "--db", str(db_file), "--output", str(export_file)],
            capture_output=True, cwd=str(Path(__file__).parent.parent),
        )
        # Delete and reimport
        db_file.unlink()
        result = subprocess.run(
            [sys.executable, "compiler/db.py", "import", str(export_file), "--db", str(db_file)],
            capture_output=True, text=True, cwd=str(Path(__file__).parent.parent),
        )
        assert result.returncode == 0
        db2 = FactoryDB(db_file)
        rows = db2.query("SELECT name, version FROM intents")
        assert ("plan", "1.0.0") in rows
        db2.close()
```

- [ ] **Step 2: Run to verify failure**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_db.py::TestCLI -v
```

Expected: failures — CLI argument parsing not implemented yet.

- [ ] **Step 3: Commit**

```bash
git add tests/test_db.py
git commit -m "test: add CLI command tests for state DB"
```

---

### Task 6: Implement CLI commands

**Files:**
- Modify: `compiler/db.py`

- [ ] **Step 1: Add export and import methods to FactoryDB**

Add to the `FactoryDB` class:

```python
    def export_to_json(self) -> dict:
        data = {}
        for table in self.list_tables():
            columns = [
                row[1] for row in self.query(f"PRAGMA table_info({table})")
            ]
            rows = self.query(f"SELECT * FROM {table}")
            data[table] = [dict(zip(columns, row)) for row in rows]
        return data

    def import_from_json(self, data: dict) -> int:
        total = 0
        for table, rows in data.items():
            if not rows:
                continue
            columns = list(rows[0].keys())
            placeholders = ", ".join(["?"] * len(columns))
            col_names = ", ".join(columns)
            for row in rows:
                self._conn.execute(
                    f"INSERT OR REPLACE INTO {table} ({col_names}) VALUES ({placeholders})",
                    tuple(row[c] for c in columns),
                )
                total += 1
        self._conn.commit()
        return total
```

- [ ] **Step 2: Add CLI entry point at bottom of db.py**

Add at the end of `compiler/db.py`:

```python
def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Skill factory state database")
    parser.add_argument("--db", default=".factory/state.db", help="Database path")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize the database schema")

    export_p = sub.add_parser("export", help="Export database to JSON")
    export_p.add_argument("--output", default=".factory/state-export.json", help="Output file")

    import_p = sub.add_parser("import", help="Import database from JSON")
    import_p.add_argument("file", help="JSON file to import")

    args = parser.parse_args()
    db_path = Path(args.db)

    if args.command == "init":
        db = FactoryDB(db_path)
        print(f"Database initialized at {db_path}")
        db.close()

    elif args.command == "export":
        db = FactoryDB(db_path)
        data = db.export_to_json()
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, indent=2))
        print(f"Exported {sum(len(v) for v in data.values())} records to {output}")
        db.close()

    elif args.command == "import":
        import_file = Path(args.file)
        if not import_file.exists():
            print(f"Error: {import_file} not found", file=sys.stderr)
            sys.exit(1)
        data = json.loads(import_file.read_text())
        db = FactoryDB(db_path)
        count = db.import_from_json(data)
        print(f"Imported {count} records into {db_path}")
        db.close()


if __name__ == "__main__":
    _cli()
```

- [ ] **Step 3: Run all tests**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_db.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add compiler/db.py
git commit -m "feat: implement CLI commands (init, export, import) for state DB"
```

---

### Task 7: Write failing tests for view queries

**Files:**
- Modify: `tests/test_db.py`

- [ ] **Step 1: Add view query tests**

Append to `tests/test_db.py`:

```python
class TestViews:
    def test_stale_compilations_shows_never_compiled(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 0, False)
        rows = db.query("SELECT name FROM stale_compilations")
        names = [r[0] for r in rows]
        assert "plan" in names

    def test_stale_compilations_shows_outdated(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 0, False)
        db.record_compilation(
            "plan", "1.0.0", "claude", "2026.03.1", "2026.03.1",
            "success", ["a"], [], [], 100,
        )
        # Update intent to newer version
        db.register_intent("plan", "1.1.0", "intents/plan/intent.md", 4, 0, False)
        rows = db.query("SELECT name FROM stale_compilations")
        names = [r[0] for r in rows]
        assert "plan" in names

    def test_stale_compilations_excludes_current(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 0, False)
        db.record_compilation(
            "plan", "1.0.0", "claude", "2026.03.1", "2026.03.1",
            "success", ["a"], [], [], 100,
        )
        rows = db.query("SELECT name FROM stale_compilations WHERE platform='claude'")
        assert len(rows) == 0

    def test_compilation_history_shows_freshness(self, db):
        db.register_intent("plan", "1.0.0", "intents/plan/intent.md", 3, 0, False)
        db.record_compilation(
            "plan", "1.0.0", "claude", "2026.03.1", "2026.03.1",
            "success", ["a"], [], [], 100,
        )
        rows = db.query("SELECT freshness FROM compilation_history")
        assert rows[0][0] == "current"

        # Update intent version, old compilation becomes outdated
        db.register_intent("plan", "2.0.0", "intents/plan/intent.md", 3, 0, False)
        rows = db.query("SELECT freshness FROM compilation_history")
        assert rows[0][0] == "outdated"
```

- [ ] **Step 2: Run to verify they pass** (views already created in Task 2)

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_db.py::TestViews -v
```

Expected: all pass (views were created in schema init). If any fail, the view SQL needs fixing.

- [ ] **Step 3: Commit**

```bash
git add tests/test_db.py
git commit -m "test: add view query tests for state DB"
```

---

### Task 8: Manual integration test and tag

- [ ] **Step 1: Run the full test suite**

```bash
cd ~/repos/skill-factory && uv run pytest tests/test_db.py -v
```

Expected: all tests pass.

- [ ] **Step 2: Test CLI end-to-end manually**

```bash
cd ~/repos/skill-factory
python compiler/db.py init
python compiler/db.py export
cat .factory/state-export.json
```

Expected: database created, JSON export with empty tables.

- [ ] **Step 3: Clean up test artifacts**

```bash
rm -f .factory/state.db .factory/state-export.json
```

- [ ] **Step 4: Final commit and tag**

```bash
git add -A
git status
git commit -m "chore: complete state DB implementation" --allow-empty
git tag v0.2.0-state-db -m "SQLite state database complete"
```
