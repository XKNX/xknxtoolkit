"""Client for the anonymous KNX online catalog service.

It is a plain HTTP file-style REST service with no authentication:

- ``GET {base}/Download/Manufacturers`` -> XML, one ``<unsignedShort>`` per manufacturer
- the manufacturer *names* come from the public master data file
  (``https://update.knx.org/data/XML/project-23/knx_master.xml``), the same file ETS ships
  and our ``.knxproj`` export already uses

For now the GUI only needs the manufacturer list; product index / ``.knxprod`` download is
deliberately not implemented yet.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BASE_URL = "https://onlinecatalog.knx.org"
MASTER_DATA_URL = "https://update.knx.org/data/XML/project-23/knx_master.xml"
_CACHE_FILE = "online_catalog_manufacturers.json"
_TIMEOUT_SECONDS = 30.0


class OnlineCatalogError(Exception):
    """Raised when the online catalog service cannot be reached or returns bad data."""


@dataclass(frozen=True)
class OnlineManufacturer:
    id: int
    name: str


def _local_name(tag: object) -> str:
    """The element's tag without its XML namespace (both feeds use namespaces)."""
    return str(tag).rsplit("}", 1)[-1]


def parse_manufacturer_ids(xml_bytes: bytes) -> list[int]:
    """Parse the ``Download/Manufacturers`` XML into a sorted list of manufacturer ids."""
    root = ET.fromstring(xml_bytes)
    ids = [
        int(e.text)
        for e in root
        if _local_name(e.tag) == "unsignedShort" and (e.text or "").strip()
    ]
    if not ids:
        raise OnlineCatalogError("manufacturer list is empty")
    return sorted(ids)


def parse_manufacturer_names(xml_bytes: bytes) -> dict[int, str]:
    """Parse ``knx_master.xml`` into ``{manufacturer_id: name}``."""
    root = ET.fromstring(xml_bytes)
    names: dict[int, str] = {}
    for element in root.iter():
        if _local_name(element.tag) != "Manufacturer":
            continue
        # The numeric KNX manufacturer id is ``KnxManufacturerId``; ``Id`` is ``M-xxxx``.
        mid = element.get("KnxManufacturerId") or (
            element.get("Id") or ""
        ).removeprefix("M-")
        if not mid.isdigit():
            continue
        names[int(mid)] = element.get("Name") or f"M-{int(mid):04d}"
    if not names:
        raise OnlineCatalogError("master data contains no manufacturers")
    return names


def _http_get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "xknxtoolkit/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", None) or exc
        raise OnlineCatalogError(f"{url}: {reason}") from exc


class OnlineCatalogClient:
    """Fetches the manufacturer list, with a small on-disk cache.

    The cache lives next to the catalog database. ``cached_manufacturers`` is a pure read
    (for per-frame UI use); ``refresh_manufacturers`` hits the network and replaces the cache.
    """

    def __init__(self, cache_dir: Path, base_url: str = DEFAULT_BASE_URL) -> None:
        self._cache_path = cache_dir / _CACHE_FILE
        self._base_url = base_url
        self._lock = threading.Lock()

    def _load_cache(self) -> list[OnlineManufacturer] | None:
        try:
            raw = json.loads(self._cache_path.read_text(encoding="utf-8"))
            return [OnlineManufacturer(item["id"], item["name"]) for item in raw]
        except (OSError, ValueError, KeyError):
            return None

    def _save_cache(self, manufacturers: list[OnlineManufacturer]) -> None:
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            self._cache_path.write_text(
                json.dumps(
                    [{"id": m.id, "name": m.name} for m in manufacturers],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass  # a missing cache only costs a re-download, never a failure

    def cached_manufacturers(self) -> list[OnlineManufacturer] | None:
        """Return the manufacturer list from the cache, or None; never touches the network."""
        with self._lock:
            return self._load_cache()

    def refresh_manufacturers(self) -> list[OnlineManufacturer]:
        """Download the manufacturer list and replace the cache."""
        with self._lock:
            return self._fetch_locked()

    def _fetch_locked(self) -> list[OnlineManufacturer]:
        ids = parse_manufacturer_ids(
            _http_get(f"{self._base_url}/Download/Manufacturers")
        )
        names = parse_manufacturer_names(_http_get(MASTER_DATA_URL))
        manufacturers = [
            OnlineManufacturer(mid, names.get(mid, f"M-{mid:04d}")) for mid in ids
        ]
        self._save_cache(manufacturers)
        return manufacturers
