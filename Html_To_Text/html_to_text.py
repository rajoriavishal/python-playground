"""Utilities for converting HTML transcripts to plain text.

This module provides a small CLI that accepts an HTML transcript, strips
all markup, removes timestamp cues such as ``0:01`` or ``12:34:56``, and
normalises whitespace so the resulting plain-text transcript is easy to
reuse.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser
from typing import Iterable, List


_TIMESTAMP_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")


class TranscriptHTMLParser(HTMLParser):
    """Extracts text from transcript HTML while keeping logical breaks.

    The parser keeps track of block-level elements so we can reintroduce
    newline characters between segments without carrying over the raw HTML
    markup.
    """

    _BLOCK_TAGS = {
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "fieldset",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hgroup",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self) -> None:
        super().__init__()
        self._chunks: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        if tag in self._BLOCK_TAGS:
            self._maybe_add_newline()

    def handle_startendtag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        if tag in self._BLOCK_TAGS:
            self._maybe_add_newline()

    def handle_endtag(self, tag: str) -> None:
        if tag in self._BLOCK_TAGS:
            self._maybe_add_newline()

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self._chunks.append(text)

    def get_text(self) -> str:
        return "".join(self._chunks)

    def _maybe_add_newline(self) -> None:
        if self._chunks and self._chunks[-1] != "\n":
            self._chunks.append("\n")


def strip_html_transcript(html: str) -> str:
    """Return a cleaned-up transcript from raw HTML input."""

    parser = TranscriptHTMLParser()
    parser.feed(html)
    text = parser.get_text()
    parser.close()

    text = _TIMESTAMP_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)

    return text.strip()


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return pathlib.Path(path).read_text(encoding="utf-8")


def _write_output(text: str, path: str | None) -> None:
    if path:
        pathlib.Path(path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text + ("" if text.endswith("\n") else "\n"))


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert an HTML transcript into plain text by removing all HTML "
            "markup and timestamp cues."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="HTML input file (defaults to stdin)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional output file (defaults to stdout)",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    html_text = _read_input(args.input)
    cleaned = strip_html_transcript(html_text)
    _write_output(cleaned, args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
