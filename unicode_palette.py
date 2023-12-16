#!/usr/bin/python3
"""Generate palette of Unicode characters of a specific class."""

import argparse
import base64
import sys
from typing import Generator, TextIO, Tuple
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
        "--add-hover",
        type=bool,
        help="Add character name as hover",
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
) -> Generator[Tuple[str, str], None, None]:
    categories = frozenset(args.category)
    for code in range(UNICODE_END):
        u = chr(code)
        if unicodedata.category(u) in categories:
            yield (
                u,
                unicodedata.name(u).title(),
            )


def _html_string(t: Tuple[str, str], add_name: bool, add_hover: bool) -> str:
    return (f"<span title='{t[1]}'>{t[0]}</span>" if add_hover else t[0]) + (
        f"<span class='n'>{t[1]}</span>" if add_name else ""
    )


def _text_string(t: Tuple[str, str], add_name: bool) -> str:
    return t[0] + (UNICODE_ZWS + t[1]) if add_name else ""


def _write_output(args: argparse.Namespace, out: TextIO):
    if args.html:
        out.write("data:text/html;charset=UTF-8;")
        out_str = (
            "<html><head><title>Unicode Palette</title><style> .n {font-size:"
            + args.name_font_size
            + ";} </style></head><body>"
            + "".join(
                [
                    _html_string(t, args.add_name, args.add_hover)
                    for t in _char_gen(args)
                ]
            )
            + "</body></html>"
        )
    else:
        out.write("data:text/plain;charset=UTF-8;")
        out_str = UNICODE_ZWS.join(
            [_text_string(t, args.add_name) for t in _char_gen(args)]
        )
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
