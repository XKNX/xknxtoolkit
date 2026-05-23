from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from xknxmono.catalog.db import get_db
from xknxmono.catalog.models import CatalogSection, Manufacturer
from xknxmono.catalog.schemas import CatalogSectionOut

router = APIRouter(prefix="/manufacturers", tags=["Manufacturers"])

_cache: dict[str, list[CatalogSectionOut]] = {}


def collect_section_ids(db: Session, section_id: str) -> list[str]:
    result = db.execute(text("""
        WITH RECURSIVE subtree(id) AS (
            SELECT id FROM catalog_sections WHERE id = :sid
            UNION ALL
            SELECT s.id FROM catalog_sections s JOIN subtree st ON s.parent_id = st.id
        )
        SELECT id FROM subtree
    """), {"sid": section_id})
    return [row[0] for row in result]


def _build_tree(sections: list[CatalogSection]) -> list[CatalogSectionOut]:
    by_parent: dict[str | None, list[CatalogSection]] = defaultdict(list)
    for s in sections:
        by_parent[s.parent_id].append(s)

    def build(parent_id: str | None) -> list[CatalogSectionOut]:
        return [
            CatalogSectionOut(
                id=s.id,
                name=s.name,
                number=s.number,
                manufacturer_id=s.manufacturer_id,
                parent_id=s.parent_id,
                children=build(s.id),
            )
            for s in sorted(by_parent.get(parent_id, []), key=lambda x: x.name)
        ]

    return build(None)


@router.get("/{manufacturer_id}/catalog-sections", response_model=list[CatalogSectionOut])
def list_catalog_sections(manufacturer_id: str, db: Session = Depends(get_db)):
    if not db.get(Manufacturer, manufacturer_id):
        raise HTTPException(404, "Manufacturer not found")
    if manufacturer_id not in _cache:
        sections = db.scalars(
            select(CatalogSection).where(CatalogSection.manufacturer_id == manufacturer_id)
        ).all()
        _cache[manufacturer_id] = _build_tree(list(sections))
    return _cache[manufacturer_id]
