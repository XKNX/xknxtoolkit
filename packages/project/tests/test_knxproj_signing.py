"""Tests for the .knxproj folder signing.

The golden signature is produced by the reference signing implementation for a
folder containing ``project.xml`` = ``b"hello"`` and ``0.xml`` = ``b"world!!"``.
"""

from __future__ import annotations

import base64
import hashlib

from xknxmono.project.core.knxproj_signing import (
    directory_digest,
    directory_signature,
)

_GOLDEN_SIGNATURE = (
    b"WZlt/FbYQ8wulqmLNqwSgfJCjNt33R3AQ+CPAxJyopgmmWG+ghtJ2Nra1zWNSmoo7YLtGWKsvYL"
    b"bT/EzYueNp+PwvKsKfVj2uGN9kY/ldYagcXlgm/gIQKxCOL7847nLFlvkir+MH1ycs1TlnMewTy"
    b"8f7gyCuUJjOXCxwzvWIB0="
)
_FILES = {"project.xml": b"hello", "0.xml": b"world!!"}


def test_directory_signature_matches_reference() -> None:
    assert directory_signature(_FILES) == _GOLDEN_SIGNATURE


def test_directory_digest_is_colon_joined_sorted_sha1() -> None:
    # "0.xml" sorts before "project.xml"; each value is base64(sha1(content)).
    expected_string = (
        f"0.xml:{base64.b64encode(hashlib.sha1(b'world!!').digest()).decode()},"
        f"project.xml:{base64.b64encode(hashlib.sha1(b'hello').digest()).decode()}"
    )
    assert directory_digest(_FILES) == hashlib.sha1(
        expected_string.encode("utf-8")
    ).digest()


def test_signature_is_deterministic() -> None:
    assert directory_signature(_FILES) == directory_signature(dict(_FILES))
