"""SQLAlchemy table mappings. The schema itself is created by Alembic migrations."""

from decimal import Decimal

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from weighingms.infrastructure.persistence.types import DecimalText


class Base(DeclarativeBase):
    pass


class SessionRow(Base):
    __tablename__ = "weighing_sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True)
    batch_id: Mapped[str] = mapped_column(String)
    station_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    started_by: Mapped[str] = mapped_column(String)
    started_at: Mapped[str] = mapped_column(String)
    completed_at: Mapped[str | None] = mapped_column(String, nullable=True)
    sync_status: Mapped[str] = mapped_column(String)
    synced_at: Mapped[str | None] = mapped_column(String, nullable=True)
    consumption_id: Mapped[str | None] = mapped_column(String, nullable=True)
    recipe: Mapped[str] = mapped_column(Text)

    components: Mapped[list["SessionComponentRow"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionComponentRow.sequence",
    )


class SessionComponentRow(Base):
    __tablename__ = "session_components"

    session_id: Mapped[str] = mapped_column(
        ForeignKey("weighing_sessions.session_id", ondelete="CASCADE"), primary_key=True
    )
    component_id: Mapped[str] = mapped_column(String, primary_key=True)
    sequence: Mapped[int]
    state: Mapped[str] = mapped_column(String)
    container_id: Mapped[str | None] = mapped_column(String, nullable=True)
    tare_value: Mapped[Decimal | None] = mapped_column(DecimalText, nullable=True)
    tare_unit: Mapped[str | None] = mapped_column(String, nullable=True)
    activated_at: Mapped[str | None] = mapped_column(String, nullable=True)
    record_id: Mapped[str | None] = mapped_column(String, nullable=True)
    actual_value: Mapped[Decimal | None] = mapped_column(DecimalText, nullable=True)
    actual_unit: Mapped[str | None] = mapped_column(String, nullable=True)

    session: Mapped[SessionRow] = relationship(back_populates="components")


class StationStateRow(Base):
    __tablename__ = "station_state"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(String)


class AuditEventRow(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String)
    actor_id: Mapped[str] = mapped_column(String)
    detail: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[str] = mapped_column(String)


class RecordRow(Base):
    __tablename__ = "weighing_records"

    record_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("weighing_sessions.session_id"))
    batch_id: Mapped[str] = mapped_column(String)
    component_id: Mapped[str] = mapped_column(String)
    dyestuff_code: Mapped[str] = mapped_column(String)
    dyestuff_name: Mapped[str] = mapped_column(String)
    unit: Mapped[str] = mapped_column(String)
    target_value: Mapped[Decimal] = mapped_column(DecimalText)
    actual_value: Mapped[Decimal] = mapped_column(DecimalText)
    tolerance_min: Mapped[Decimal] = mapped_column(DecimalText)
    tolerance_max: Mapped[Decimal] = mapped_column(DecimalText)
    result: Mapped[str] = mapped_column(String)
    surplus_value: Mapped[Decimal | None] = mapped_column(DecimalText, nullable=True)
    operator_id: Mapped[str] = mapped_column(String)
    lot_id: Mapped[str] = mapped_column(String)
    container_id: Mapped[str] = mapped_column(String)
    tare_value: Mapped[Decimal] = mapped_column(DecimalText)
    tare_unit: Mapped[str] = mapped_column(String)
    scale_id: Mapped[str] = mapped_column(String)
    confirmed_at: Mapped[str] = mapped_column(String)


class OverrideRow(Base):
    __tablename__ = "overrides"

    override_id: Mapped[str] = mapped_column(String, primary_key=True)
    record_id: Mapped[str] = mapped_column(ForeignKey("weighing_records.record_id"))
    supervisor_id: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(Text)
    authorised_at: Mapped[str] = mapped_column(String)


class PrintJobRow(Base):
    __tablename__ = "print_jobs"

    print_id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String)
    ticket_id: Mapped[str] = mapped_column(String)
    reprint: Mapped[bool]
    operator_id: Mapped[str] = mapped_column(String)
    printed_at: Mapped[str] = mapped_column(String)
