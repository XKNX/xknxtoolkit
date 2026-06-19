"""SQLAlchemy ORM models for a project's SQLite document — one database is one project.

These are the project package's *own* models (no IR import), shaped as a subset of the KNX IR
(`xknxmono.models.intermediate`) so a later `.knxproj` import/export converter is a plain field
mapping. Identity is internal autoincrement integers; ETS `id`/`puid` strings are a boundary
concern, not stored here.

Tree: ``Installation → Area → Line → Segment → Device``; group addresses live in a separate
recursive ``GroupRange`` tree. ``Event`` is the undo/redo history (see :mod:`.core.event_store`);
the live state is the other tables.
"""

import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all project ORM models."""


class Project(Base):
    """The single project metadata row for this database."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    group_address_style: Mapped[str] = mapped_column(
        String, nullable=False, default="ThreeLevel"
    )


class Installation(Base):
    """One installation (= IR ``installation_id``, maps to ETS ``N.xml``). ``index`` is user-facing."""

    __tablename__ = "installations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, default="")

    areas: Mapped[list["Area"]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )
    group_ranges: Mapped[list["GroupRange"]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )


class Area(Base):
    """A topology area (KNX address bits 12-15)."""

    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    installation_id: Mapped[int] = mapped_column(
        ForeignKey("installations.id"), nullable=False, index=True
    )
    address: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False, default="")

    installation: Mapped["Installation"] = relationship(back_populates="areas")
    lines: Mapped[list["Line"]] = relationship(
        back_populates="area", cascade="all, delete-orphan"
    )


class Line(Base):
    """A topology line (KNX address bits 8-11). Individual addresses are unique within a line."""

    __tablename__ = "lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    area_id: Mapped[int] = mapped_column(
        ForeignKey("areas.id"), nullable=False, index=True
    )
    address: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False, default="")

    area: Mapped["Area"] = relationship(back_populates="lines")
    segments: Mapped[list["Segment"]] = relationship(
        back_populates="line", cascade="all, delete-orphan"
    )


class Segment(Base):
    """A media segment within a line (carries the medium type, e.g. ``MT-0`` TP / ``MT-5`` IP)."""

    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    line_id: Mapped[int] = mapped_column(
        ForeignKey("lines.id"), nullable=False, index=True
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    medium_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False, default="")

    line: Mapped["Line"] = relationship(back_populates="segments")
    devices: Mapped[list["Device"]] = relationship(
        back_populates="segment", cascade="all, delete-orphan"
    )


class Device(Base):
    """A device instance. ``address`` is the 0-255 individual-address octet (unique within its line).

    ``product_ref_id`` is the catalog product (what was bought); ``hardware2program_ref_id`` is the
    loaded ``HP-…`` program (= catalog ``HardwareProgram.id``), through which the application —
    and thus parameter/com-object definitions — is resolved.
    """

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    segment_id: Mapped[int] = mapped_column(
        ForeignKey("segments.id"), nullable=False, index=True
    )
    address: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    product_ref_id: Mapped[str] = mapped_column(String, nullable=False)
    hardware2program_ref_id: Mapped[str | None] = mapped_column(String)

    segment: Mapped["Segment"] = relationship(back_populates="devices")
    module_instances: Mapped[list["ModuleInstance"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    parameters: Mapped[list["Parameter"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    com_objects: Mapped[list["ComObject"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )


class ModuleInstance(Base):
    """A module instance: ``instance_id`` is the key used during eval (e.g. ``M-100_MI-1``);
    ``ref_id`` is the module definition ref (e.g. ``M-100``). Only top-level instances are stored."""

    __tablename__ = "module_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id"), nullable=False, index=True
    )
    instance_id: Mapped[str] = mapped_column(String, nullable=False)
    ref_id: Mapped[str] = mapped_column(String, nullable=False)

    device: Mapped["Device"] = relationship(back_populates="module_instances")


class Parameter(Base):
    """A parameter instance: ``ref_id`` points into the application's parameter refs; ``value`` is set."""

    __tablename__ = "parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id"), nullable=False, index=True
    )
    ref_id: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False, default="")

    device: Mapped["Device"] = relationship(back_populates="parameters")


class ComObject(Base):
    """A com-object instance ref: ``ref_id`` points into the application's com-object refs.

    ``channel_id`` references the ApplicationProgramChannel the instance lives in (``None`` when it
    is in the channel-independent block). The flags are *overrides* (``None`` = inherit from the
    product/application definition; a value forces ``Enabled``/``Disabled``). Defaults and lock state
    live on the product, not here.
    """

    __tablename__ = "com_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id"), nullable=False, index=True
    )
    ref_id: Mapped[str] = mapped_column(String, nullable=False)
    channel_id: Mapped[str | None] = mapped_column(String)

    read_flag: Mapped[bool | None] = mapped_column(Boolean)
    write_flag: Mapped[bool | None] = mapped_column(Boolean)
    communication_flag: Mapped[bool | None] = mapped_column(Boolean)
    transmit_flag: Mapped[bool | None] = mapped_column(Boolean)
    update_flag: Mapped[bool | None] = mapped_column(Boolean)
    read_on_init_flag: Mapped[bool | None] = mapped_column(Boolean)

    device: Mapped["Device"] = relationship(back_populates="com_objects")
    links: Mapped[list["ComObjectLink"]] = relationship(
        back_populates="com_object", cascade="all, delete-orphan"
    )


class GroupRange(Base):
    """A node in the group-address range tree (recursive: main → middle in ThreeLevel)."""

    __tablename__ = "group_ranges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    installation_id: Mapped[int] = mapped_column(
        ForeignKey("installations.id"), nullable=False, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("group_ranges.id"), index=True
    )
    range_start: Mapped[int] = mapped_column(Integer, nullable=False)
    range_end: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False, default="")

    installation: Mapped["Installation"] = relationship(back_populates="group_ranges")
    parent: Mapped["GroupRange | None"] = relationship(
        back_populates="children", remote_side="GroupRange.id"
    )
    children: Mapped[list["GroupRange"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    group_addresses: Mapped[list["GroupAddress"]] = relationship(
        back_populates="group_range", cascade="all, delete-orphan"
    )


class GroupAddress(Base):
    """A group address inside a (leaf) group range."""

    __tablename__ = "group_addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_range_id: Mapped[int] = mapped_column(
        ForeignKey("group_ranges.id"), nullable=False, index=True
    )
    address: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    datapoint_type: Mapped[str | None] = mapped_column(String)

    group_range: Mapped["GroupRange"] = relationship(back_populates="group_addresses")
    links: Mapped[list["ComObjectLink"]] = relationship(
        back_populates="group_address", cascade="all, delete-orphan"
    )


class ComObjectLink(Base):
    """A link between a com-object instance and a group address. ``is_sending`` marks the (single)
    group address this object transmits to; the rest are receive-only. (The IR encodes this
    positionally as the first entry of its ``Links`` list; we store the bit directly.)"""

    __tablename__ = "com_object_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    com_object_id: Mapped[int] = mapped_column(
        ForeignKey("com_objects.id"), nullable=False, index=True
    )
    group_address_id: Mapped[int] = mapped_column(
        ForeignKey("group_addresses.id"), nullable=False, index=True
    )
    is_sending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    com_object: Mapped["ComObject"] = relationship(back_populates="links")
    group_address: Mapped["GroupAddress"] = relationship(back_populates="links")


class Event(Base):
    """The undo/redo history. ``data`` is the serialized command payload (incl. before-values)."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    reverted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
