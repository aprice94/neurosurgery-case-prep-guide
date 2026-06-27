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
LIT_BEGIN = "<!-- BEGIN CURATED LITERATURE -->"
LIT_END = "<!-- END CURATED LITERATURE -->"
IMG_BEGIN = "<!-- BEGIN CURATED IMAGE SET -->"
IMG_END = "<!-- END CURATED IMAGE SET -->"
SNAPSHOT_BEGIN = "<!-- BEGIN CASE SNAPSHOT -->"
SNAPSHOT_END = "<!-- END CASE SNAPSHOT -->"
SNAPSHOT_LABELS = (
    "Anatomy at risk",
    "Operative steps",
    "Rescue plans",
    "Figures",
    "Papers",
)
CASE_LOGISTICS_HEADER = "### Case Logistics, OR Needs & Orders"
APPROACH_LOGISTICS_HEADER = "## Logistics, OR Setup & Orders"

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

def guide_sources() -> list[Path]:
    return [p for p in (ROOT / "cases").rglob("*.md") if p.name != "index.md"]

def validate_rendered_pages() -> None:
    case_sources = guide_sources()
    missing_html = []
    for src in case_sources:
        rel = src.relative_to(ROOT).with_suffix(".html")
        if not (SITE / rel).exists():
            missing_html.append(str(rel))
    if missing_html:
        fail(f"{len(missing_html)} case guides did not render as HTML, e.g. {missing_html[:8]}")
    print(f"Rendered guide pages: {len(case_sources)}")

def extract_block(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end)
    if start == -1 or stop == -1 or stop < start:
        return ""
    return text[start + len(begin):stop]

def markdown_images(text: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)

def normalize_image_ref(src: Path, target: str) -> str:
    if target.startswith(("http://", "https://")):
        return target
    return str((src.parent / target).resolve())

def validate_guide_enrichment() -> None:
    low_lit = []
    low_img = []
    missing = []
    missing_snapshots = []
    incomplete_snapshots = []
    camera_placeholders = []
    orphan_captions = []
    duplicate_images: dict[str, list[str]] = {}
    image_seen: dict[str, str] = {}
    curated_refs: set[str] = set()

    for src in guide_sources():
        text = read_text(src)
        lit = extract_block(text, LIT_BEGIN, LIT_END)
        imgs = extract_block(text, IMG_BEGIN, IMG_END)
        snapshot = extract_block(text, SNAPSHOT_BEGIN, SNAPSHOT_END)
        if not lit or not imgs:
            missing.append(str(src.relative_to(ROOT)))
            continue
        if not snapshot:
            missing_snapshots.append(str(src.relative_to(ROOT)))
        else:
            missing_labels = [label for label in SNAPSHOT_LABELS if label not in snapshot]
            if missing_labels:
                incomplete_snapshots.append((str(src.relative_to(ROOT)), missing_labels))
        if "📷" in text or "📸" in text:
            camera_placeholders.append(str(src.relative_to(ROOT)))

        pmids = re.findall(r"https://pubmed\.ncbi\.nlm\.nih\.gov/\d+/", lit)
        curated = [img for img in markdown_images(imgs) if "figures/curated/" in img]
        if len(pmids) < 10:
            low_lit.append((str(src.relative_to(ROOT)), len(pmids)))
        if len(curated) < 10:
            low_img.append((str(src.relative_to(ROOT)), len(curated)))

        lines = text.splitlines()
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not (stripped.startswith("*") and stripped.endswith("*")):
                continue
            if not re.search(r"(Source:|CC BY|public domain|Gray's Anatomy|Sobotta|Cureus|Frontiers|PMC|via Wikimedia)", stripped, re.I):
                continue
            prev = ""
            for prior in reversed(lines[:idx]):
                if prior.strip():
                    prev = prior.strip()
                    break
            if not prev.startswith("!["):
                orphan_captions.append((str(src.relative_to(ROOT)), idx + 1, stripped[:120]))

        for image in markdown_images(text):
            key = normalize_image_ref(src, image)
            prior = image_seen.get(key)
            rel = str(src.relative_to(ROOT))
            if prior and prior != rel:
                duplicate_images.setdefault(key, [prior]).append(rel)
            else:
                image_seen[key] = rel
            if "figures/curated/" in image:
                curated_refs.add(image[image.index("figures/curated/"):])

    if missing:
        fail(f"guides missing curated literature/image blocks, e.g. {missing[:8]}")
    if missing_snapshots:
        fail(f"guides missing case/approach snapshot blocks, e.g. {missing_snapshots[:8]}")
    if incomplete_snapshots:
        fail(f"guides with incomplete case/approach snapshot blocks, e.g. {incomplete_snapshots[:8]}")
    if camera_placeholders:
        fail(f"guides still containing camera emoji placeholders, e.g. {camera_placeholders[:8]}")
    if low_lit:
        fail(f"guides with fewer than 10 PubMed literature entries, e.g. {low_lit[:8]}")
    if low_img:
        fail(f"guides with fewer than 10 curated images, e.g. {low_img[:8]}")
    if orphan_captions:
        fail(f"orphaned source/caption lines not attached to images, e.g. {orphan_captions[:8]}")
    if duplicate_images:
        examples = [(k, v[:4]) for k, v in list(duplicate_images.items())[:8]]
        fail(f"duplicate image targets across guide pages, e.g. {examples}")

    curated_files = {
        str(p.relative_to(ROOT))
        for p in (ROOT / "figures" / "curated").rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    }
    missing_files = sorted(curated_refs - curated_files)
    unreferenced = sorted(curated_files - curated_refs)
    if missing_files:
        fail(f"curated image references missing files, e.g. {missing_files[:8]}")
    if unreferenced:
        fail(f"unreferenced curated image files, e.g. {unreferenced[:8]}")

    print(f"Guide enrichment: {len(guide_sources())} guides, {len(curated_refs)} unique curated images")

def validate_logistics_sections() -> None:
    missing_case = []
    missing_approach = []
    for src in guide_sources():
        text = read_text(src)
        rel = str(src.relative_to(ROOT))
        if "## Surgical Planning" in text and CASE_LOGISTICS_HEADER not in text:
            missing_case.append(rel)
        is_approach = rel.startswith("cases/approaches/") and src.name != "approach-selection.md"
        if is_approach and APPROACH_LOGISTICS_HEADER not in text:
            missing_approach.append(rel)
    if missing_case:
        fail(f"guides with Surgical Planning missing logistics/orders section, e.g. {missing_case[:8]}")
    if missing_approach:
        fail(f"approach chapters missing logistics/orders section, e.g. {missing_approach[:8]}")
    print("Logistics/orders sections: ok")

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
    validate_guide_enrichment()
    validate_logistics_sections()
    validate_rendered_pages()
    validate_links()
    validate_images()
    validate_search_index()
    print("Site validation passed")
