#!/usr/bin/python3
"""Generate palette of Unicode characters of a specific class."""

import argparse
import base64
import sys
from typing import FrozenSet, Generator
import unicodedata


def _create_arg_parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument(
        "--html",
        type=bool,
        help="HTML format",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    result.add_argument(
        "--base64",
        type=bool,
        help="base64 encoding",
        default=True,
        action=argparse.BooleanOptionalAction,
    )
    result.add_argument(
        "--categories",
        type=str,
        help="Unicode categories to dump",
        nargs="*",
        default=["So"],
    )
    return result


UNICODE_END = 0x10FFFF
UNICODE_ZWS = "\u200B"


def _char_gen(categories: FrozenSet[str]) -> Generator[str, None, None]:
    for code in range(UNICODE_END):
        u = chr(code)
        if unicodedata.category(u) in categories:
            yield u


def _main():
    arg_parser = _create_arg_parser()
    args = arg_parser.parse_args()

    if args.html:
        sys.stdout.write("data:text/html;charset=UTF-8;")
        html_fragment = "".join(
            [
                f"<span>{char} {unicodedata.name(char)}</span>"
                for char in _char_gen(frozenset(args.categories))
            ]
        )
        out = f"<html><head><title>Unicode Palette</title></head><body>{html_fragment}</body></html>"
    else:
        sys.stdout.write("data:text/plain;charset=UTF-8;")
        out = "".join(
            [char + UNICODE_ZWS for char in _char_gen(frozenset(args.categories))]
        )
    if args.base64:
        sys.stdout.write("base64,")
        b = base64.b64encode(out.encode("utf-8"))
        sys.stdout.write(b.decode("ascii"))
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    _main()
