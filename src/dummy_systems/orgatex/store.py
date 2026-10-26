"""Mutable Dummy OrgaTEX state: batch status write-backs and consumption postings (SQLite)."""

import uuid
from datetime import datetime
from typing import cast

from sqlalchemy import Engine, String, Text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from dummy_systems.orgatex.models import (
    BatchStatus,
    ConsumptionPosting,
    ConsumptionReceipt,
    StoredConsumption,
)


class _Base(DeclarativeBase):
    pass


class _BatchStatusRow(_Base):
    __tablename__ = "orgatex_batch_status"

    batch_id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String)
    updated_at: Mapped[str] = mapped_column(String)


class _ConsumptionRow(_Base):
    __tablename__ = "orgatex_consumption"

    consumption_id: Mapped[str] = mapped_column(String, primary_key=True)
    batch_id: Mapped[str] = mapped_column(String, index=True)
    idempotency_key: Mapped[str] = mapped_column(String, unique=True)
    received_at: Mapped[str] = mapped_column(String)
    payload: Mapped[str] = mapped_column(Text)


class OrgatexStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        _Base.metadata.create_all(engine)

    def status_overrides(self) -> dict[str, BatchStatus]:
        with Session(self._engine) as session:
            rows = session.scalars(select(_BatchStatusRow)).all()
            return {row.batch_id: cast(BatchStatus, row.status) for row in rows}

    def set_status(self, batch_id: str, status: BatchStatus, at: datetime) -> None:
        with Session(self._engine) as session, session.begin():
            session.merge(
                _BatchStatusRow(batch_id=batch_id, status=status, updated_at=at.isoformat())
            )

    def record_consumption(
        self, batch_id: str, posting: ConsumptionPosting, at: datetime
    ) -> ConsumptionReceipt:
        """Store a posting once per idempotency key; a repeat returns the original receipt."""
        existing = self._find_by_key(posting.idempotency_key)
        if existing is not None:
            return existing.model_copy(update={"duplicate": True})
        consumption_id = f"CNS-{uuid.uuid4().hex[:12].upper()}"
        row = _ConsumptionRow(
            consumption_id=consumption_id,
            batch_id=batch_id,
            idempotency_key=posting.idempotency_key,
            received_at=at.isoformat(),
            payload=posting.model_dump_json(by_alias=True),
        )
        try:
            with Session(self._engine) as session, session.begin():
                session.add(row)
        except IntegrityError:
            # A concurrent request stored the same key first.
            raced = self._find_by_key(posting.idempotency_key)
            assert raced is not None
            return raced.model_copy(update={"duplicate": True})
        return ConsumptionReceipt(
            consumption_id=consumption_id, batch_id=batch_id, received_at=at, duplicate=False
        )

    def consumptions(self, batch_id: str) -> list[StoredConsumption]:
        with Session(self._engine) as session:
            rows = session.scalars(
                select(_ConsumptionRow)
                .where(_ConsumptionRow.batch_id == batch_id)
                .order_by(_ConsumptionRow.received_at)
            ).all()
            return [
                StoredConsumption(
                    consumption_id=row.consumption_id,
                    batch_id=row.batch_id,
                    received_at=datetime.fromisoformat(row.received_at),
                    posting=ConsumptionPosting.model_validate_json(row.payload),
                )
                for row in rows
            ]

    def reset(self) -> None:
        with Session(self._engine) as session, session.begin():
            session.query(_BatchStatusRow).delete()
            session.query(_ConsumptionRow).delete()

    def _find_by_key(self, key: str) -> ConsumptionReceipt | None:
        with Session(self._engine) as session:
            row = session.scalars(
                select(_ConsumptionRow).where(_ConsumptionRow.idempotency_key == key)
            ).first()
            if row is None:
                return None
            return ConsumptionReceipt(
                consumption_id=row.consumption_id,
                batch_id=row.batch_id,
                received_at=datetime.fromisoformat(row.received_at),
                duplicate=False,
            )
