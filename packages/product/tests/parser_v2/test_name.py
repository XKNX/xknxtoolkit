"""Regression tests for parser_v2._name.apply_text_args.

A text-arg value containing backslashes must be substituted literally into the
template — re.sub must not interpret it as replacement escapes / backreferences.
Guards against reverting from the callable ``repl`` (which inserts its return
value verbatim) back to a string ``repl``, which raised ``re.error`` on values
like ``C:\\Users\\me`` / ``\\1`` and silently mangled ``C:\\temp`` (``\\t`` -> TAB).
"""

from __future__ import annotations

import pytest

from xknxmono.product.parser_v2._name import (  # pyright: ignore[reportPrivateUsage]
    apply_text_args,
)


def test_basic_placeholder_substituted() -> None:
    assert apply_text_args("Channel {{ChNo}}", {"ChNo": "1"}) == "Channel 1"


@pytest.mark.parametrize(
    "value",
    [
        r"C:\Users\me",  # crash: bad escape \U
        r"\1",  # crash: invalid group reference
        r"C:\temp",  # cosmetic: \t -> TAB, silently mangled
        r"C:\new",  # cosmetic: \n -> newline
        "trailing\\",  # trailing backslash
    ],
)
def test_backslash_value_substituted_literally(value: str) -> None:
    assert apply_text_args("{{A}}", {"A": value}) == value
