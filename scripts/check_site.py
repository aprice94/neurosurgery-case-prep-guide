#!/usr/bin/env python3
"""Validate the generated Jekyll site without external network checks."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "_site"
BASEURL = "/neurosurgery-case-prep-guide/"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        for key in ("href", "src"):
            val = data.get(key)
            if val:
                self.refs.append((tag, key, val))

def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    sys.exit(1)

def warn(msg: str) -> None:
    print(f"WARN: {msg}")

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def validate_rendered_pages() -> None:
    case_sources = [p for p in (ROOT / "cases").rglob("*.md") if p.name != "index.md"]
    missing_html = []
    for src in case_sources:
        rel = src.relative_to(ROOT).with_suffix(".html")
        if not (SITE / rel).exists():
            missing_html.append(str(rel))
    if missing_html:
        fail(f"{len(missing_html)} case guides did not render as HTML, e.g. {missing_html[:8]}")
    print(f"Rendered guide pages: {len(case_sources)}")

def resolve_local(html_file: Path, url: str) -> Path | None:
    if not url or url.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"}:
        return None
    raw_path = unquote(parsed.path)
    if raw_path.startswith(BASEURL):
        return SITE / raw_path[len(BASEURL):]
    if raw_path.startswith("/"):
        return None
    return (html_file.parent / raw_path).resolve()

def target_exists(target: Path) -> bool:
    if target.exists():
        return True
    if target.suffix == ".md":
        return target.with_suffix(".html").exists()
    if target.suffix == "":
        return (target / "index.html").exists() or target.with_suffix(".html").exists()
    return False

def validate_links() -> None:
    broken = []
    site_root = SITE.resolve()
    for html in SITE.rglob("*.html"):
        parser = LinkParser()
        parser.feed(read_text(html))
        for tag, key, url in parser.refs:
            target = resolve_local(html, url)
            if target is None:
                continue
            try:
                target.resolve().relative_to(site_root)
            except ValueError:
                continue
            if not target_exists(target):
                broken.append((html.relative_to(SITE), tag, key, url))
    if broken:
        for item in broken[:30]:
            print("BROKEN", *item, sep="\t")
        fail(f"{len(broken)} broken internal generated-site links")
    print("Internal links: ok")

def validate_images() -> None:
    bad = []
    for img in ROOT.rglob("*"):
        if img.is_file() and img.suffix.lower() in IMAGE_EXTS and "_site" not in img.parts:
            data = img.read_bytes()[:512]
            lower = data.lower().lstrip()
            if lower.startswith((b"<!doctype html", b"<html")) or b"<title>404" in lower:
                bad.append(str(img.relative_to(ROOT)))
            if img.suffix.lower() in {".jpg", ".jpeg"} and not data.startswith(b"\xff\xd8"):
                bad.append(str(img.relative_to(ROOT)))
            if img.suffix.lower() == ".png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
                bad.append(str(img.relative_to(ROOT)))
    if bad:
        fail(f"Invalid image files: {bad[:20]}")
    print("Image integrity: ok")

def validate_search_index() -> None:
    path = SITE / "assets/search-index.json"
    if not path.exists():
        fail("missing _site/assets/search-index.json")
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"search index is invalid JSON: {exc}")
    if not isinstance(data, list) or len(data) < 100:
        fail(f"search index unexpectedly small or not a list: {type(data).__name__}, {len(data) if isinstance(data, list) else 'n/a'}")
    required = {"t", "u", "c", "d", "g", "x"}
    missing = [item for item in data if not required.issubset(item)]
    if missing:
        fail(f"search index entries missing keys, example: {missing[0]}")
    urls = [item["u"] for item in data]
    if len(urls) != len(set(urls)):
        fail("search index contains duplicate URLs")
    print(f"Search index: {len(data)} entries")

if __name__ == "__main__":
    if not SITE.exists():
        fail("_site does not exist; run `bundle exec jekyll build` first")
    validate_rendered_pages()
    validate_links()
    validate_images()
    validate_search_index()
    print("Site validation passed")
