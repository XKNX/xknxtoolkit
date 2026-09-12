"""Regression tests pinning down load_xml()'s resistance to XXE-class attacks.

xsdata's default parser sits on Python's stdlib xml.etree.ElementTree (pyexpat). Unlike
lxml, pyexpat never wires up a handler for external entity resolution and enforces an
entity-expansion amplification limit - so classic XXE (file/SSRF exfiltration via a
SYSTEM entity), external-DTD-as-SSRF, and billion-laughs-style entity bombs all fail
closed by construction, not because we configured anything defensively.

These tests exist to catch a future regression - e.g. switching to an lxml-backed
xsdata handler, or explicitly enabling DTD/xinclude processing - that would silently
reopen one of these holes.
"""

from __future__ import annotations

import http.server
import threading

import pytest
from xsdata.exceptions import ParserError

from xknxmono.models import load_xml

_ROOT_OPEN = '<KNX xmlns="http://knx.org/xml/project/23">'


def test_external_entity_is_not_resolved() -> None:
    """A SYSTEM entity pointing at a local file must never be expanded into the document."""
    payload = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE KNX [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
{_ROOT_OPEN}&xxe;</KNX>""".encode()
    with pytest.raises(ParserError, match="undefined entity"):
        load_xml(payload, version="23")


def test_external_dtd_subset_is_never_fetched() -> None:
    """A DOCTYPE pointing its external DTD at an attacker-controlled URL must not be
    requested - not even to load the DTD itself, before any entity is referenced."""
    hits = 0

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            nonlocal hits
            hits += 1
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'<!ENTITY x "leaked">')

        def log_message(self, format: str, *args: object) -> None:
            pass  # silence request logging in test output

    server = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        payload = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE KNX SYSTEM "http://127.0.0.1:{server.server_port}/evil.dtd">
{_ROOT_OPEN}</KNX>""".encode()
        load_xml(payload, version="23")
    finally:
        server.shutdown()
        thread.join()

    assert hits == 0


def test_billion_laughs_is_rejected() -> None:
    """Deeply nested internal entities must hit an amplification limit, not expand
    unbounded - the classic 9-level "lolz" bomb, capped at 10x growth per level."""
    payload = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE KNX [
<!ENTITY lol "lol">
<!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
<!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
<!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
<!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
<!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
<!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
<!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
<!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
{_ROOT_OPEN}&lol9;</KNX>""".encode()
    with pytest.raises(ParserError, match="amplification factor"):
        load_xml(payload, version="23")


def test_small_internal_entity_still_expands() -> None:
    """A harmless, non-external, non-amplifying internal entity is still valid XML and
    must keep parsing - proving the above rejections are specific, not "any DOCTYPE fails".
    """
    payload = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE KNX [<!ENTITY greeting "hello">]>
{_ROOT_OPEN}</KNX>""".encode()
    result = load_xml(payload, version="23")
    assert result is not None
