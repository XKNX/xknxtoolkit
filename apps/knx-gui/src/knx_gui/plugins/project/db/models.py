from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reverted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class DeviceModel(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    individual_address: Mapped[str | None] = mapped_column(String, nullable=True)
    template_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    parameters: Mapped[list["ParameterModel"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )
    com_objects: Mapped[list["ComObjectModel"]] = relationship(
        back_populates="device", cascade="all, delete-orphan"
    )


class ParameterModel(Base):
    __tablename__ = "parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False)
    param_id: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)

    device: Mapped["DeviceModel"] = relationship(back_populates="parameters")


class ComObjectModel(Base):
    __tablename__ = "com_objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False)
    co_id: Mapped[str] = mapped_column(String, nullable=False)
    dpt_major: Mapped[int] = mapped_column(Integer, nullable=False)
    dpt_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    flag_communication: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    flag_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    flag_write: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    flag_transmit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    flag_update: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    device: Mapped["DeviceModel"] = relationship(back_populates="com_objects")


class LinkModel(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_pin: Mapped[int] = mapped_column(Integer, nullable=False)
    end_pin: Mapped[int] = mapped_column(Integer, nullable=False)


class AreaModel(Base):
    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    area_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False, default="")

    lines: Mapped[list["LineModel"]] = relationship(
        back_populates="area", cascade="all, delete-orphan"
    )


class LineModel(Base):
    __tablename__ = "lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, default="")

    area: Mapped["AreaModel"] = relationship(back_populates="lines")
