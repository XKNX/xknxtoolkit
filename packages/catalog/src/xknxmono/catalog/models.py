import datetime

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str | None] = mapped_column(Text)

    hardware: Mapped[list["Hardware"]] = relationship(back_populates="manufacturer")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    application_number: Mapped[int | None] = mapped_column(Integer)
    application_version: Mapped[int | None] = mapped_column(Integer)
    mask_version: Mapped[str | None] = mapped_column(String)
    is_secure_enabled: Mapped[bool | None] = mapped_column(Boolean)

    programs: Mapped[list["HardwareProgram"]] = relationship(back_populates="application")


class Hardware(Base):
    __tablename__ = "hardware"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    manufacturer_id: Mapped[str] = mapped_column(ForeignKey("manufacturers.id"), nullable=False, index=True)

    name: Mapped[str | None] = mapped_column(Text)
    order_number: Mapped[str | None] = mapped_column(Text, index=True)
    is_rail_mounted: Mapped[bool | None] = mapped_column(Boolean)
    width_mm: Mapped[float | None] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text)
    default_language: Mapped[str | None] = mapped_column(String)

    serial_number: Mapped[str | None] = mapped_column(String)
    version_number: Mapped[int | None] = mapped_column(Integer)
    bus_current: Mapped[float | None] = mapped_column(Float)
    has_application_program: Mapped[bool | None] = mapped_column(Boolean)
    is_coupler: Mapped[bool | None] = mapped_column(Boolean)
    is_power_supply: Mapped[bool | None] = mapped_column(Boolean)
    is_ip_enabled: Mapped[bool | None] = mapped_column(Boolean)
    no_download_without_plugin: Mapped[bool | None] = mapped_column(Boolean)

    manufacturer: Mapped["Manufacturer"] = relationship(back_populates="hardware")
    programs: Mapped[list["HardwareProgram"]] = relationship(back_populates="hardware")


class HardwareProgram(Base):
    __tablename__ = "hardware_programs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    hardware_id: Mapped[str] = mapped_column(ForeignKey("hardware.id"), nullable=False, index=True)
    application_id: Mapped[str | None] = mapped_column(ForeignKey("applications.id"), index=True)
    knxprod_path: Mapped[str] = mapped_column(Text, nullable=False)

    registration_status: Mapped[str | None] = mapped_column(String)
    registration_number: Mapped[str | None] = mapped_column(String)
    registration_date: Mapped[datetime.date | None] = mapped_column(Date)

    hardware: Mapped["Hardware"] = relationship(back_populates="programs")
    application: Mapped["Application | None"] = relationship(back_populates="programs")
    medium_types: Mapped[list["HardwareProgramMediumType"]] = relationship(back_populates="hardware_program")


class HardwareProgramMediumType(Base):
    __tablename__ = "hardware_program_medium_types"

    hardware_program_id: Mapped[str] = mapped_column(ForeignKey("hardware_programs.id"), primary_key=True)
    medium_type: Mapped[str] = mapped_column(String, primary_key=True, index=True)

    hardware_program: Mapped["HardwareProgram"] = relationship(back_populates="medium_types")


class CatalogSection(Base):
    __tablename__ = "catalog_sections"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    manufacturer_id: Mapped[str] = mapped_column(String, index=True)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("catalog_sections.id"), index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    number: Mapped[str | None] = mapped_column(String)

    parent: Mapped["CatalogSection | None"] = relationship(back_populates="children", remote_side="CatalogSection.id")
    children: Mapped[list["CatalogSection"]] = relationship(back_populates="parent")


class CatalogSectionProduct(Base):
    __tablename__ = "catalog_section_products"

    section_id: Mapped[str] = mapped_column(ForeignKey("catalog_sections.id"), primary_key=True, index=True)
    hardware_program_id: Mapped[str] = mapped_column(ForeignKey("hardware_programs.id"), primary_key=True)
