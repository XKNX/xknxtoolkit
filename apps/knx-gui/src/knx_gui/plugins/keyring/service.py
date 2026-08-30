"""Keyring service: load a password-protected ETS ``.knxkeys`` keyring and hold it in memory.

Uses xknx's own keyring loader (which decrypts), not the toolkit's plaintext-only ``xknx-keyring``
package. The keyring is runtime-only state (never persisted into the project document)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from xknx.secure.keyring import Keyring, sync_load_keyring

if TYPE_CHECKING:
    from knx_gui.plugins.base import Logger


class KeyringService:
    def __init__(self) -> None:
        self._log: Logger
        self._keyring: Keyring | None = None
        self._path: Path | None = None

    def set_logger(self, log: Logger) -> None:
        self._log = log

    @property
    def keyring(self) -> Keyring | None:
        return self._keyring

    @property
    def path(self) -> Path | None:
        return self._path

    def load(self, path: Path, password: str) -> None:
        """Decrypt and load a keyring. Raises on a wrong password / invalid file."""
        keyring = sync_load_keyring(path, password)
        self._keyring = keyring
        self._path = path
        self._log.info("keyring loaded", path=str(path))

    def clear(self) -> None:
        self._keyring = None
        self._path = None
