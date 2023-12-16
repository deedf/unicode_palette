#!/usr/bin/python3
"""Generate palette of Unicode characters of a specific class."""

import argparse
import base64
import sys
from typing import FrozenSet, Generator, Optional, TextIO, Tuple
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


def _char_gen(
    args: argparse.Namespace,
) -> Generator[Tuple[str, Optional[str]], None, None]:
    categories = frozenset(args.category)
    for code in range(UNICODE_END):
        u = chr(code)
        if unicodedata.category(u) in categories:
            yield (
                u,
                unicodedata.name(u).title() if args.add_name else None,
            )


def _html_string(t: Tuple[str, Optional[str], Optional[str]]) -> str:
    return t[0] + "".join(
        [
            f"<span class='{i}'>{t[i]}</span>"
            for i in range(1, len(t))
            if t[i] is not None
        ]
    )


def _text_string(t: Tuple[str, Optional[str], Optional[str]]) -> str:
    return " ".join([s for s in t if s is not None])


def _write_output(args: argparse.Namespace, out: TextIO):
    if args.html:
        out.write("data:text/html;charset=UTF-8;")
        out_str = (
            "<html><head><title>Unicode Palette</title><style> span {font-size:"
            + args.name_font_size
            + ";} </style></head><body>"
            + "".join([_html_string(t) for t in _char_gen(args)])
            + "</body></html>"
        )
    else:
        out.write("data:text/plain;charset=UTF-8;")
        out_str = "".join([_text_string(t) for t in _char_gen(args)])
    if args.base64:
        out.write("base64,")
        b = base64.b64encode(out_str.encode("utf-8"))
        out.write(b.decode("ascii"))
    else:
        out.write(urllib.parse.quote_plus(out_str))


def _main() -> None:
    arg_parser = _create_arg_parser()
    args = arg_parser.parse_args()
    _write_output(args, sys.stdout)


if __name__ == "__main__":
    _main()
