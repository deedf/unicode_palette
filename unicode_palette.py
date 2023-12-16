#!/usr/bin/python3
"""Generate palette of Unicode characters of a specific class."""

import argparse
import base64
import sys
from typing import FrozenSet, Generator
import unicodedata
import urllib.parse


def _create_arg_parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Generate data: URL with Unicode symbol palette."
    )
    result.add_argument(
        "--add-name",
        type=bool,
        help="Add character name",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    result.add_argument(
        "--html",
        type=bool,
        help="HTML format",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    result.add_argument(
        "--add-combining",
        type=bool,
        help="Add combining class to HTML output",
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
        "--category",
        type=str,
        help="Unicode categories to dump",
        nargs="*",
        default=["So"],
    )
    result.add_argument(
        "--name-font-size",
        type=str,
        help="Font size for character name in HTML",
        default="6",
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
                char
                + UNICODE_ZWS
                + (
                    f"<span>{unicodedata.name(char).title()} {unicodedata.combining(char)if args.add_combining else ''}</span>"
                    if args.add_name
                    else ""
                )
                for char in _char_gen(frozenset(args.category))
            ]
        )
        out = (
            "<html><head><title>Unicode Palette</title><style> span {font-size:"
            + args.name_font_size
            + ";} </style></head><body>"
            + html_fragment
            + "</body></html>"
        )
    else:
        sys.stdout.write("data:text/plain;charset=UTF-8;")
        out = "".join(
            [
                char
                + UNICODE_ZWS
                + (unicodedata.name(char).title() if args.add_name else "")
                for char in _char_gen(frozenset(args.category))
            ]
        )
    if args.base64:
        sys.stdout.write("base64,")
        b = base64.b64encode(out.encode("utf-8"))
        sys.stdout.write(b.decode("ascii"))
    else:
        sys.stdout.write(urllib.parse.quote_plus(out))


if __name__ == "__main__":
    _main()
