#!/usr/bin/env python3
"""Remove low-value curated figures that are legal to embed but poor case-prep media.

The original image-harvesting pass overvalued quantity. This script prunes
figures whose captions/titles are overwhelmingly study-methods, plots, models,
animal work, or statistics rather than anatomy, imaging, operative exposure, or
device/procedure visuals.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG_BEGIN = "<!-- BEGIN CURATED IMAGE SET -->"
IMG_END = "<!-- END CURATED IMAGE SET -->"

LOW_VALUE = re.compile(
    r"\b("
    r"algorithmic approach|animal model|bar graph|biomechanical|calibration curve|"
    r"clinical outcome|confusion matrix|decision curve|egger|finite element|"
    r"flow ?chart|flow diagram|forest plot|frequency of|grade summary|"
    r"ground-truth|incidence of|in vitro|kaplan|logistic regression|machine learning|meta-analysis|mouse|"
    r"nomogram|numerical simulation|odds ratio|patient communication|predicted|"
    r"pooled analysis|pooled mean|prisma|prima flow|quality of life|"
    r"questionnaire|rat model|receiver operating|risk ratio|roc curve|"
    r"sensitivity analysis|sleep quality|study protocol|study workflow|summary of findings|"
    r"survey|temporal alignment|time course|transformer architecture|visual analog|workflow|hfs-8 score|"
    r"apoptosis|electron microscopy|expression levels|metabolomic|lipidomic|prevalence \(%\)|"
    r"fetus|fetuses|grhl3cre|rac1"
    r")\b",
    re.I,
)

IMAGE_LINE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def guide_paths() -> list[Path]:
    return sorted(p for p in (ROOT / "cases").rglob("*.md") if p.name != "index.md")


def extract_image_units(block: str) -> tuple[list[str], list[tuple[str, str, str]]]:
    """Return non-image prelude lines and image/caption/rest units."""
    lines = block.splitlines()
    prelude: list[str] = []
    units: list[tuple[str, str, str]] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if not line.strip().startswith("!["):
            prelude.append(line)
            idx += 1
            continue
        image = line
        idx += 1
        caption_lines: list[str] = []
        while idx < len(lines) and lines[idx].strip():
            caption_lines.append(lines[idx])
            idx += 1
        spacer = ""
        while idx < len(lines) and not lines[idx].strip():
            spacer += lines[idx] + "\n"
            idx += 1
        units.append((image, "\n".join(caption_lines).strip(), spacer))
    return prelude, units


def image_target(page: Path, image_line: str) -> Path | None:
    match = IMAGE_LINE.search(image_line)
    if not match:
        return None
    target = match.group(1)
    if target.startswith(("http://", "https://")):
        return None
    return (page.parent / target).resolve()


def prune_text(path: Path, text: str) -> tuple[str, list[Path]]:
    start = text.find(IMG_BEGIN)
    stop = text.find(IMG_END)
    if start == -1 or stop == -1 or stop < start:
        return text, []
    block_start = start + len(IMG_BEGIN)
    block = text[block_start:stop]
    prelude, units = extract_image_units(block)
    keep: list[tuple[str, str, str]] = []
    removed_files: list[Path] = []
    for image, caption, spacer in units:
        if LOW_VALUE.search(caption):
            target = image_target(path, image)
            if target and target.exists() and "figures/curated" in target.as_posix():
                removed_files.append(target)
            continue
        keep.append((image, caption, spacer))
    if len(keep) == len(units):
        return text, []
    rebuilt = "\n".join(prelude).rstrip()
    for image, caption, _spacer in keep:
        rebuilt += f"\n\n{image}\n{caption}\n"
    if not keep:
        rebuilt += "\n\nNo embedded open-license figures passed relevance review for this page yet; use the linked operative/imaging sources above while this page is being curated.\n"
    new_text = text[:block_start] + rebuilt.rstrip() + "\n\n" + text[stop:]
    return new_text, removed_files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write changes and delete pruned local image files")
    args = parser.parse_args()
    changed = 0
    removed: list[Path] = []
    for path in guide_paths():
        text = path.read_text(encoding="utf-8")
        new_text, files = prune_text(path, text)
        if new_text != text:
            changed += 1
            removed.extend(files)
            if args.apply:
                path.write_text(new_text, encoding="utf-8")
    unique_removed = sorted(set(removed))
    if args.apply:
        for image in unique_removed:
            try:
                image.unlink()
            except FileNotFoundError:
                pass
    print(f"Pages changed: {changed}")
    print(f"Curated images pruned: {len(unique_removed)}")
    for image in unique_removed[:80]:
        print(image.relative_to(ROOT))
    if len(unique_removed) > 80:
        print(f"... {len(unique_removed) - 80} more")


if __name__ == "__main__":
    main()
