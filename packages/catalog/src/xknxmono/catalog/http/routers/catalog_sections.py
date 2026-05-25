"""Catalog sections router: return the hierarchical product catalog for a manufacturer."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from xknxmono.catalog.core.catalog_sections import (
  CatalogSectionNode,
  build_catalog_tree,
  list_catalog_sections,
)
from xknxmono.catalog.core.manufacturers import get_manufacturer
from xknxmono.catalog.db import get_db
from xknxmono.catalog.http.schemas import CatalogSectionResponse

router = APIRouter(prefix="/manufacturers", tags=["Manufacturers"])

DbDep = Annotated[Session, Depends(get_db)]

_cache: dict[str, list[CatalogSectionResponse]] = {}


def _node_to_out(node: CatalogSectionNode) -> CatalogSectionResponse:
  """Convert a :class:`~xknxmono.catalog.core.catalog_sections.CatalogSectionNode` to its API response schema."""
  return CatalogSectionResponse(
    id=node.id,
    name=node.name,
    number=node.number,
    manufacturer_id=node.manufacturer_id,
    parent_id=node.parent_id,
    children=[_node_to_out(child) for child in node.children],
  )


@router.get("/{manufacturer_id}/catalog-sections", response_model=list[CatalogSectionResponse])
def list_catalog_sections_endpoint(manufacturer_id: str, db: DbDep):
  """Return the full catalog section tree for a manufacturer, with results cached in memory."""
  if not get_manufacturer(db, manufacturer_id):
    raise HTTPException(404, "Manufacturer not found")
  if manufacturer_id not in _cache:
    sections = list_catalog_sections(db, manufacturer_id)
    tree = build_catalog_tree(sections)
    _cache[manufacturer_id] = [_node_to_out(node) for node in tree]
  return _cache[manufacturer_id]
