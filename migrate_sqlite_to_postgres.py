"""把 CareerAgent SQLite 数据一次性迁移到 PostgreSQL + pgvector。

默认仅在目标业务表为空时迁移，避免重复导入。迁移前复制一份 SQLite 备份；
向量 BLOB 会转换为 pgvector，原 BLOB 不再写入 PostgreSQL。
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sqlite3
from array import array
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, JSON, Integer, func, select, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.db.base import Base
from database_bootstrap import normalize_async_database_url
from app.modules.collection import models as _collection_models  # noqa: F401
from app.modules.transcription import models as _transcription_models  # noqa: F401
from app.modules.refinement import models as _refinement_models  # noqa: F401
from app.modules.knowledge_base import models as _knowledge_models  # noqa: F401

BATCH_SIZE = 500
CHECK_TABLES = (
    "creators",
    "content_items",
    "transcription_jobs",
    "knowledge_preparations",
    "embedding_index_profiles",
)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
    return None


def _parse_date(value: Any) -> date | None:
    if value is None or isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def _parse_json(value: Any) -> Any:
    if value is None or isinstance(value, (dict, list, int, float, bool)):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _blob_vector(value: Any) -> list[float] | None:
    if value is None:
        return None
    values = array("f")
    try:
        values.frombytes(bytes(value))
    except Exception:
        return None
    return [float(item) for item in values]


def _convert_value(column, value: Any) -> Any:
    if value is None:
        return None
    column_type = column.type
    # Variant 在 PostgreSQL 上会解析为 pgvector；这里只处理普通字段。
    if isinstance(column_type, JSON):
        return _parse_json(value)
    if isinstance(column_type, DateTime):
        parsed = _parse_datetime(value)
        if parsed is not None and bool(getattr(column_type, "timezone", False)) and parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    if isinstance(column_type, Date):
        return _parse_date(value)
    if isinstance(column_type, Boolean):
        return bool(value)
    if isinstance(column_type, Integer) and isinstance(value, bool):
        return int(value)
    return value


def _sqlite_tables(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {str(row[0]) for row in rows}


def _sqlite_columns(connection: sqlite3.Connection, table_name: str) -> list[str]:
    safe = table_name.replace('"', '""')
    rows = connection.execute(f'PRAGMA table_info("{safe}")').fetchall()
    return [str(row[1]) for row in rows]


def _backup_sqlite(source: Path, source_connection: sqlite3.Connection) -> Path:
    """使用 SQLite 在线备份 API，确保 WAL 中已提交数据也进入备份。"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = source.with_name(f"{source.stem}_before_postgres_{timestamp}{source.suffix}")
    destination = sqlite3.connect(backup)
    try:
        source_connection.backup(destination)
    finally:
        destination.close()
    return backup



def _foreign_key_specs() -> dict[str, list[dict[str, Any]]]:
    """按 SQLAlchemy 元数据整理迁移时需要检查的外键。

    SQLite 历史版本可能没有启用 PRAGMA foreign_keys，因而会留下父记录已删除、
    子记录仍存在的孤儿数据。PostgreSQL 会严格拒绝这类记录，因此迁移前必须按
    已实际接收的父键进行修复或隔离。
    """
    specs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for table in Base.metadata.sorted_tables:
        for constraint in table.foreign_key_constraints:
            elements = list(constraint.elements)
            if not elements:
                continue
            local_columns = tuple(element.parent.name for element in elements)
            remote_table = elements[0].column.table.name
            remote_columns = tuple(element.column.name for element in elements)
            nullable = all(bool(table.c[name].nullable) for name in local_columns)
            specs[table.name].append(
                {
                    "local_columns": local_columns,
                    "remote_table": remote_table,
                    "remote_columns": remote_columns,
                    "nullable": nullable,
                    "constraint": constraint.name or "",
                }
            )
    return dict(specs)


def _referenced_keysets(
    specs: dict[str, list[dict[str, Any]]],
) -> dict[str, set[tuple[str, ...]]]:
    result: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for table_specs in specs.values():
        for spec in table_specs:
            result[spec["remote_table"]].add(tuple(spec["remote_columns"]))
    return dict(result)


def _json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"__blob_bytes__": len(value)}
    if isinstance(value, memoryview):
        return {"__blob_bytes__": len(value)}
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


class _QuarantineWriter:
    """把无法满足外键的历史孤儿行完整保存到本地 JSONL。"""

    def __init__(self, path: Path):
        self.path = path
        self._file = None
        self.count = 0

    def write(self, *, table: str, reason: str, row: dict[str, Any]) -> None:
        if self._file is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._file = self.path.open("w", encoding="utf-8")
        payload = {"table": table, "reason": reason, "row": _json_safe(row)}
        self._file.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self._file.flush()
        self.count += 1

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None


def _repair_foreign_keys(
    *,
    table_name: str,
    row: dict[str, Any],
    specs: dict[str, list[dict[str, Any]]],
    accepted_keys: dict[tuple[str, tuple[str, ...]], set[tuple[Any, ...]]],
) -> tuple[dict[str, Any] | None, list[str]]:
    """返回修复后的行；不可修复的非空外键返回 None。

    - 可空外键缺少父记录：清空为 NULL，保留主记录；
    - 非空外键缺少父记录：该行已经无法关联到业务主体，隔离而不是让整次迁移失败。
    """
    repaired = dict(row)
    notes: list[str] = []
    for spec in specs.get(table_name, []):
        local_columns = tuple(spec["local_columns"])
        values = tuple(repaired.get(name) for name in local_columns)
        if all(value is None for value in values):
            continue
        remote_key = (str(spec["remote_table"]), tuple(spec["remote_columns"]))
        if values in accepted_keys.get(remote_key, set()):
            continue
        local_label = ",".join(local_columns)
        remote_label = f'{spec["remote_table"]}({",".join(spec["remote_columns"])})'
        detail = f"{local_label}={values!r} 找不到父记录 {remote_label}"
        if bool(spec["nullable"]):
            for name in local_columns:
                repaired[name] = None
            notes.append("已清空可空外键：" + detail)
            continue
        notes.append("已隔离非空外键孤儿行：" + detail)
        return None, notes
    return repaired, notes


def _remember_reference_keys(
    *,
    table_name: str,
    row: dict[str, Any],
    referenced_keysets: dict[str, set[tuple[str, ...]]],
    accepted_keys: dict[tuple[str, tuple[str, ...]], set[tuple[Any, ...]]],
) -> None:
    for columns in referenced_keysets.get(table_name, set()):
        values = tuple(row.get(name) for name in columns)
        if any(value is None for value in values):
            continue
        accepted_keys[(table_name, tuple(columns))].add(values)


async def _target_has_business_data(connection) -> bool:
    for table_name in CHECK_TABLES:
        if table_name not in Base.metadata.tables:
            continue
        table = Base.metadata.tables[table_name]
        count = int((await connection.execute(select(func.count()).select_from(table))).scalar_one())
        if count > 0:
            return True
    return False


async def _reset_sequences(connection) -> None:
    for table in Base.metadata.sorted_tables:
        pk_columns = list(table.primary_key.columns)
        if len(pk_columns) != 1:
            continue
        column = pk_columns[0]
        if not isinstance(column.type, Integer):
            continue
        table_name = table.name.replace('"', '""')
        column_name = column.name.replace('"', '""')
        await connection.execute(text(f'''
            SELECT setval(
                pg_get_serial_sequence('"{table_name}"', '{column_name}'),
                COALESCE((SELECT MAX("{column_name}") FROM "{table_name}"), 1),
                (SELECT COUNT(*) > 0 FROM "{table_name}")
            )
            WHERE pg_get_serial_sequence('"{table_name}"', '{column_name}') IS NOT NULL
        '''))


_SAFE_INDEX_RE = re.compile(r"[^a-zA-Z0-9_]+")


def _ann_index_name(profile_id: int) -> str:
    return _SAFE_INDEX_RE.sub("_", f"ix_kce_profile_{int(profile_id)}_ann")[:60]


def _ann_index_ddl(
    profile_id: int,
    dimensions: int,
    *,
    m: int = 16,
    ef_construction: int = 64,
) -> str | None:
    if dimensions <= 0 or dimensions > 4000:
        return None
    if dimensions <= 2000:
        vector_type = f"vector({int(dimensions)})"
        opclass = "vector_cosine_ops"
    else:
        vector_type = f"halfvec({int(dimensions)})"
        opclass = "halfvec_cosine_ops"
    index_name = _ann_index_name(profile_id)
    return f"""
        CREATE INDEX "{index_name}"
        ON knowledge_chunk_embeddings
        USING hnsw ((embedding::{vector_type}) {opclass})
        WITH (
            m = {max(4, min(int(m), 64))},
            ef_construction = {max(16, min(int(ef_construction), 512))}
        )
        WHERE profile_id = {int(profile_id)} AND dimensions = {int(dimensions)}
    """


async def _rebuild_ann_indexes(engine) -> dict[str, Any]:
    """迁移提交后逐 Profile 建索引；单个索引失败不回滚业务数据。"""
    async with engine.connect() as connection:
        rows = (
            await connection.execute(
                text(
                    """
                    SELECT p.id, p.dimensions, COUNT(c.id) AS chunk_count
                    FROM embedding_index_profiles AS p
                    LEFT JOIN knowledge_chunk_embeddings AS c ON c.profile_id = p.id
                    WHERE p.dimensions > 0
                    GROUP BY p.id, p.dimensions
                    ORDER BY p.id
                    """
                )
            )
        ).mappings().all()
    built = 0
    exact = 0
    failures: list[str] = []
    for row in rows:
        if int(row["chunk_count"] or 0) <= 0:
            continue
        profile_id = int(row["id"])
        dimensions = int(row["dimensions"])
        ddl = _ann_index_ddl(profile_id, dimensions)
        if ddl is None:
            exact += 1
            continue
        try:
            async with engine.begin() as connection:
                await connection.execute(text("SET LOCAL statement_timeout = 0"))
                await connection.execute(
                    text(f'DROP INDEX IF EXISTS "{_ann_index_name(profile_id)}"')
                )
                await connection.execute(text(ddl))
            built += 1
        except Exception as exc:
            failures.append(f"Profile {profile_id}: {type(exc).__name__}: {exc}")
    return {"built": built, "exact_profiles": exact, "failures": failures}


async def migrate(source: Path, target_url: str, *, only_if_empty: bool = True) -> dict[str, Any]:
    if not source.is_file() or source.stat().st_size <= 0:
        return {"status": "skipped", "reason": "SQLite 文件不存在或为空", "source": str(source)}
    if not target_url.lower().startswith(("postgresql", "postgres")):
        raise RuntimeError("目标 DATABASE_URL 必须是 PostgreSQL。")
    target_url = normalize_async_database_url(target_url)

    source_connection = sqlite3.connect(source)
    source_connection.row_factory = sqlite3.Row
    source_tables = _sqlite_tables(source_connection)
    if not source_tables.intersection(CHECK_TABLES):
        source_connection.close()
        return {"status": "skipped", "reason": "SQLite 中没有业务表", "source": str(source)}

    backup: Path | None = None
    engine = create_async_engine(target_url, pool_pre_ping=True)
    totals: dict[str, int] = {}
    repaired_fk_counts: dict[str, int] = defaultdict(int)
    skipped_orphan_counts: dict[str, int] = defaultdict(int)
    orphan_samples: list[str] = []
    fk_specs = _foreign_key_specs()
    reference_keysets = _referenced_keysets(fk_specs)
    accepted_keys: dict[tuple[str, tuple[str, ...]], set[tuple[Any, ...]]] = defaultdict(set)
    quarantine: _QuarantineWriter | None = None
    ann_indexes: dict[str, Any] = {"built": 0, "exact_profiles": 0, "failures": []}
    try:
        async with engine.begin() as target:
            await target.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await target.run_sync(Base.metadata.create_all)
            if only_if_empty and await _target_has_business_data(target):
                return {
                    "status": "skipped",
                    "reason": "PostgreSQL 已有业务数据，为避免重复导入已跳过",
                }

            backup = _backup_sqlite(source, source_connection)
            quarantine = _QuarantineWriter(
                backup.with_name(f"{source.stem}_postgres_migration_quarantine_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
            )
            # sorted_tables 会按外键依赖顺序排列。
            for table in Base.metadata.sorted_tables:
                if table.name not in source_tables:
                    continue
                source_columns = _sqlite_columns(source_connection, table.name)
                transferable = [name for name in source_columns if name in table.c]
                if not transferable:
                    continue
                safe_table = table.name.replace('"', '""')
                quoted_columns = ", ".join(f'"{name.replace(chr(34), chr(34)*2)}"' for name in transferable)
                cursor = source_connection.execute(
                    f'SELECT {quoted_columns} FROM "{safe_table}" ORDER BY rowid'
                )
                inserted = 0
                while True:
                    raw_rows = cursor.fetchmany(BATCH_SIZE)
                    if not raw_rows:
                        break
                    payload: list[dict[str, Any]] = []
                    for raw_row in raw_rows:
                        row: dict[str, Any] = {}
                        for name in transferable:
                            if table.name == "knowledge_chunk_embeddings" and name == "vector_blob":
                                continue
                            row[name] = _convert_value(table.c[name], raw_row[name])
                        if table.name == "knowledge_chunk_embeddings":
                            blob = raw_row["vector_blob"] if "vector_blob" in raw_row.keys() else None
                            vector = _blob_vector(blob)
                            row["embedding"] = vector
                            row["vector_blob"] = None
                            if vector and not row.get("dimensions"):
                                row["dimensions"] = len(vector)
                        repaired_row, repair_notes = _repair_foreign_keys(
                            table_name=table.name,
                            row=row,
                            specs=fk_specs,
                            accepted_keys=accepted_keys,
                        )
                        if repaired_row is None:
                            skipped_orphan_counts[table.name] += 1
                            reason = "; ".join(repair_notes) or "缺少外键父记录"
                            if len(orphan_samples) < 20:
                                orphan_samples.append(f"{table.name}: {reason}")
                            assert quarantine is not None
                            quarantine.write(
                                table=table.name,
                                reason=reason,
                                row={name: raw_row[name] for name in raw_row.keys()},
                            )
                            continue
                        if repair_notes:
                            repaired_fk_counts[table.name] += 1
                        payload.append(repaired_row)
                        _remember_reference_keys(
                            table_name=table.name,
                            row=repaired_row,
                            referenced_keysets=reference_keysets,
                            accepted_keys=accepted_keys,
                        )
                    if payload:
                        await target.execute(table.insert(), payload)
                        inserted += len(payload)
                totals[table.name] = inserted
            await _reset_sequences(target)
        ann_indexes = await _rebuild_ann_indexes(engine)
    finally:
        if quarantine is not None:
            quarantine.close()
        source_connection.close()
        await engine.dispose()

    return {
        "status": "migrated",
        "source": str(source),
        "backup": str(backup) if backup else "",
        "tables": totals,
        "rows": sum(totals.values()),
        "foreign_key_repairs": dict(repaired_fk_counts),
        "orphan_rows_skipped": dict(skipped_orphan_counts),
        "orphan_samples": orphan_samples,
        "quarantine": (
            str(quarantine.path)
            if quarantine is not None and quarantine.count > 0
            else ""
        ),
        "ann_indexes": ann_indexes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="SQLite → PostgreSQL + pgvector 数据迁移")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", default=os.environ.get("DATABASE_URL", ""))
    parser.add_argument("--force", action="store_true", help="目标非空时仍尝试迁移（不推荐）")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    if not args.target:
        raise SystemExit("缺少 --target 或 DATABASE_URL。")
    result = asyncio.run(migrate(args.source.expanduser().resolve(), args.target, only_if_empty=not args.force))
    if not args.quiet:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
