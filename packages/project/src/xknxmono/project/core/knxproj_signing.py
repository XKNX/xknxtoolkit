"""Sign a ``.knxproj`` directory the way the KNX tooling expects on import.

Each folder in a ``.knxproj`` archive (the project folder ``P-XXXX`` and each
manufacturer folder ``M-XXXX``) is accompanied by a ``<folder>.signature`` file
at the archive root. The signature is an RSA-PKCS#1 v1.5 signature over a SHA-1
digest of the folder's contents:

1. for every file in the folder (recursively), compute ``base64(sha1(content))``;
2. build the string ``"relpath:hash,relpath:hash,..."`` with the entries sorted
   by relative path (ordinal) and joined by commas, relative paths being taken
   from the folder root;
3. the digest is ``sha1(utf-8(that string))``;
4. the signature is ``RSA-PKCS#1v1.5(sha1)`` of that digest, base64 encoded.

The signing key is the fixed "converter" RSA key that ships identically with the
KNX tooling (it is not per-installation or secret), so a project folder can be
re-signed offline. This module reproduces the algorithm in pure Python - verified
to produce byte-identical signatures to the reference implementation.

Relative paths use ``/`` as the separator here. Folders exported by this package
are flat (``project.xml``, ``0.xml``), so no separator appears in the digest.
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Mapping

# The converter RSA key (1024 bit, public exponent 65537). Public knowledge - the
# same key ships with the KNX tooling; kept here so folders can be re-signed.
_MODULUS_B64 = (
    "zSjrmVmM+ULXdrFHiSZZo7PEHo/sXBIkjxHkqQbxEI2YE1SBq0dbEfqW3eDSdjLlpMy5Yx9hcMS"
    "nrmVUWh3PgBBQmzMBZpr/yJRny8UzB1pqTPyisWyfg7+NiAd1Ize4r/bQxKE4BaJ2wqEDwH8ggg"
    "2faxJ2/WReGVrrzJL2u00="
)
_PRIVATE_EXPONENT_B64 = (
    "p1DgE8h8uCxTHHGoLaohIOjS4TnvQYdqWWP2YANRRnazt9ALkGw5UYhU0c8w1UTdFHICH1zQUu+"
    "O8SOij3wQZKMGcw4GgsJH8jUtlbSkHCtJVOBe817tNcuVUC1qfSt59uCyR6jKV2pm2+Hy8MCcsZ"
    "kRXqDRcdgcYsiTpIwKcuE="
)

_MODULUS = int.from_bytes(base64.b64decode(_MODULUS_B64), "big")
_PRIVATE_EXPONENT = int.from_bytes(base64.b64decode(_PRIVATE_EXPONENT_B64), "big")
_KEY_SIZE = (_MODULUS.bit_length() + 7) // 8
# ASN.1 DigestInfo prefix for a SHA-1 hash (RFC 3447).
_SHA1_DIGEST_INFO_PREFIX = bytes.fromhex("3021300906052b0e03021a05000414")


def directory_digest(files: Mapping[str, bytes]) -> bytes:
    """Return the SHA-1 folder digest for ``files`` (relative path -> content)."""
    entries = {
        path: base64.b64encode(hashlib.sha1(content).digest()).decode("ascii")
        for path, content in files.items()
    }
    joined = ",".join(f"{path}:{h}" for path, h in sorted(entries.items()))
    return hashlib.sha1(joined.encode("utf-8")).digest()


def directory_signature(files: Mapping[str, bytes]) -> bytes:
    """Return the base64 ``.signature`` bytes for a folder's ``files``.

    ``files`` maps each file's path (relative to the folder, ``/`` separated) to
    its content. Suitable directly as the body of the folder's ``.signature`` file.
    """
    digest = directory_digest(files)
    block = _SHA1_DIGEST_INFO_PREFIX + digest
    padding = b"\xff" * (_KEY_SIZE - 3 - len(block))
    encoded = b"\x00\x01" + padding + b"\x00" + block
    signature = pow(int.from_bytes(encoded, "big"), _PRIVATE_EXPONENT, _MODULUS)
    return base64.b64encode(signature.to_bytes(_KEY_SIZE, "big"))
