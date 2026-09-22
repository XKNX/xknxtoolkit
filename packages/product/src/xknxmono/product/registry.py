"""`Registry` — the queryable index over a loaded .knxprod.

Everything is keyed by id (as in KNX itself): flat object stores (`id → object`) plus relationship
edges (`parent id → [child ids]`). Nothing is mutated or pre-linked onto the objects; helpers
resolve refs on demand against the stores and return `id → object` dicts (never lists to scan).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .application import Application
from .catalog import CatalogItem, CatalogSection
from .hardware import DeviceProgram, Hardware, Product
from .master import MasterData


@dataclass(slots=True)
class Registry:
    master: MasterData

    # id → object
    hardware: dict[str, Hardware] = field(default_factory=dict[str, Hardware])
    products: dict[str, Product] = field(default_factory=dict[str, Product])
    programs: dict[str, DeviceProgram] = field(default_factory=dict[str, DeviceProgram])
    applications: dict[str, Application] = field(default_factory=dict[str, Application])
    catalog_sections: dict[str, CatalogSection] = field(
        default_factory=dict[str, CatalogSection]
    )
    catalog_items: dict[str, CatalogItem] = field(
        default_factory=dict[str, CatalogItem]
    )

    # relationship edges: parent id → [child ids]
    manufacturer_to_hardware: dict[str, list[str]] = field(
        default_factory=dict[str, list[str]]
    )
    manufacturer_to_section: dict[str, list[str]] = field(
        default_factory=dict[str, list[str]]
    )
    hardware_to_product: dict[str, list[str]] = field(
        default_factory=dict[str, list[str]]
    )
    hardware_to_program: dict[str, list[str]] = field(
        default_factory=dict[str, list[str]]
    )
    program_to_application: dict[str, list[str]] = field(
        default_factory=dict[str, list[str]]
    )
    section_to_subsection: dict[str, list[str]] = field(
        default_factory=dict[str, list[str]]
    )
    section_to_item: dict[str, list[str]] = field(default_factory=dict[str, list[str]])

    # --- ergonomic resolvers (all return id → object) ------------------------
    def products_for_hardware(self, hardware_id: str) -> dict[str, Product]:
        return {
            p: self.products[p] for p in self.hardware_to_product.get(hardware_id, [])
        }

    def programs_for_hardware(self, hardware_id: str) -> dict[str, DeviceProgram]:
        return {
            p: self.programs[p] for p in self.hardware_to_program.get(hardware_id, [])
        }

    def items_for_section(self, section_id: str) -> dict[str, CatalogItem]:
        return {
            i: self.catalog_items[i] for i in self.section_to_item.get(section_id, [])
        }
