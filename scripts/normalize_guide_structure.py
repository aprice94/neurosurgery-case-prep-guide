#!/usr/bin/env python3
"""Normalize guide structure and spine OR-table language."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "cases"

SNAP_BEGIN = "<!-- BEGIN CASE SNAPSHOT -->"
SNAP_END = "<!-- END CASE SNAPSHOT -->"
LIT_BEGIN = "<!-- BEGIN CURATED LITERATURE -->"
LIT_END = "<!-- END CURATED LITERATURE -->"
IMG_BEGIN = "<!-- BEGIN CURATED IMAGE SET -->"
IMG_END = "<!-- END CURATED IMAGE SET -->"
COMMON_BEGIN = "<!-- BEGIN COMMON PIMP QUESTIONS -->"
COMMON_END = "<!-- END COMMON PIMP QUESTIONS -->"
PREF_BEGIN = "<!-- BEGIN ATTENDING PREFERENCE VARIABLES -->"
PREF_END = "<!-- END ATTENDING PREFERENCE VARIABLES -->"
FIG_BEGIN = "<!-- BEGIN FIGURE USE ATTRIBUTION -->"
FIG_END = "<!-- END FIGURE USE ATTRIBUTION -->"

AO_SPINE = "https://www.aofoundation.org/spine"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def guide_paths() -> list[Path]:
    return sorted(p for p in CASES.rglob("*.md") if p.name != "index.md")


def fm_title(text: str, fallback: str) -> str:
    m = re.search(r'^title:\s*"?([^"\n]+)"?', text, re.M)
    return m.group(1).strip() if m else fallback


def is_spine_path(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("cases/spine-"):
        return True
    return rel in {
        "cases/approaches/anterior-cervical-approach.md",
        "cases/approaches/posterior-cervical-approach.md",
        "cases/approaches/posterior-thoracolumbar-approach.md",
        "cases/approaches/transpsoas-approach.md",
        "cases/approaches/transthoracic-approach.md",
    }


def table_note(path: Path, title: str) -> str:
    blob = f"{path.as_posix()} {title}".lower()
    if any(k in blob for k in ["acdf", "cervical disc", "anterior cervical", "cervical-dis", "cervical-disc"]):
        return "standard supine radiolucent OR table, often reversed for C-arm access; tape shoulders caudally for lower-cervical lateral fluoroscopy."
    if "alif" in blob:
        return "supine radiolucent table with C-arm access and vascular/retroperitoneal exposure setup."
    if any(k in blob for k in ["xlif", "olif", "transpsoas", "lateral interbody", "llif"]):
        return "radiolucent lateral-decubitus table with iliac crest near the table break, true AP/lateral fluoroscopy, hips/knees flexed, and secure taping."
    if any(k in blob for k in ["microdiscectomy", "laminectomy", "foraminotomy"]):
        return "Wilson frame, Andrews/knee-chest frame, or Jackson/open-frame table by surgeon preference; flexion opens the interlaminar window and the abdomen must hang free."
    if any(k in blob for k in ["tlif", "plif", "fusion", "deformity", "osteotomy", "trauma", "fracture", "corpectomy", "intradural", "intramedullary", "dural avf", "spinal avm", "cord cavernoma"]):
        return "Jackson/Allen/open-frame radiolucent table, or ProAxis/hinged table when sagittal alignment adjustment is useful; keep abdomen free for venous decompression."
    if any(k in blob for k in ["kyphoplasty", "vertebroplasty", "si-joint", "sacroiliac"]):
        return "radiolucent table with unobstructed AP/lateral fluoroscopy; Jackson/open-frame setup if prone access or navigation is needed."
    if any(k in blob for k in ["transthoracic", "thoracic"]):
        return "radiolucent table configured for lateral or anterior thoracic exposure, with C-arm access and chest/vascular exposure needs coordinated before positioning."
    if any(k in blob for k in ["pump", "stimulator", "baclofen"]):
        return "standard OR table or radiolucent spine table depending on percutaneous versus paddle/intrathecal access; confirm fluoroscopy and tunneling access before prep."
    return "radiolucent spine-capable table selected for approach, imaging, instrumentation, patient size, and alignment goals; keep abdomen free for prone cases."


def replace_ao_links(text: str) -> str:
    text = re.sub(r"https://surgeryreference\.aofoundation\.org/?", AO_SPINE, text)
    text = text.replace("AO Surgery Reference", "AO Spine / Surgery Reference")
    text = text.replace("[AO Surgery Reference]", "[AO Spine / Surgery Reference]")
    return text


def extract_marker(text: str, begin: str, end: str) -> tuple[str, str]:
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    m = pattern.search(text)
    if not m:
        return "", text
    return m.group(0).strip(), (text[:m.start()] + text[m.end():]).strip()


def extract_heading(text: str, heading: str) -> tuple[str, str]:
    pattern = re.compile(rf"(?ms)^## {re.escape(heading)}\n.*?(?=^## |^<!-- BEGIN |\Z)")
    m = pattern.search(text)
    if not m:
        return "", text
    return m.group(0).strip(), (text[:m.start()] + text[m.end():]).strip()


def extract_about_figures(text: str) -> tuple[list[str], str]:
    blocks: list[str] = []
    lines = text.splitlines()
    keep: list[str] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if line.startswith("> **About the figures"):
            block = [line]
            idx += 1
            while idx < len(lines) and lines[idx].startswith(">"):
                block.append(lines[idx])
                idx += 1
            blocks.append("\n".join(block).strip())
            continue
        keep.append(line)
        idx += 1
    return blocks, "\n".join(keep)


def insert_figure_note(text: str, blocks: list[str]) -> str:
    if not blocks:
        return text
    note = f"""{FIG_BEGIN}

## Figure Use & Attribution

{blocks[0]}

{FIG_END}"""
    text = re.sub(re.escape(FIG_BEGIN) + r".*?" + re.escape(FIG_END), "", text, flags=re.S).strip()
    anchors = ["\n## References", "\n<!-- BEGIN COMMON PIMP QUESTIONS -->", "\n<!-- BEGIN ATTENDING PREFERENCE VARIABLES -->"]
    positions = [text.find(a) for a in anchors if text.find(a) != -1]
    pos = min(positions) if positions else -1
    if pos == -1:
        return text.rstrip() + "\n\n" + note + "\n"
    return text[:pos].rstrip() + "\n\n" + note + "\n" + text[pos:]


def normalize_top_order(text: str) -> str:
    if "\n---\n" not in text:
        return text
    fm_end = text.find("\n---", 4) + 4 if text.startswith("---\n") else 0
    prefix = text[:fm_end].strip() if fm_end else ""
    body = text[fm_end:].strip() if fm_end else text.strip()

    h1 = ""
    m = re.match(r"(?s)^(# .+?)(?:\n{2,}|\Z)(.*)$", body)
    if m:
        h1 = m.group(1).strip()
        body = m.group(2).strip()
    body = re.sub(r"^\s*---\s*", "", body).strip()

    snap, body = extract_marker(body, SNAP_BEGIN, SNAP_END)
    one, body = extract_heading(body, "One-Liner")
    fig, body = extract_heading(body, "Figures, Imaging & Video")
    lit, body = extract_marker(body, LIT_BEGIN, LIT_END)
    img, body = extract_marker(body, IMG_BEGIN, IMG_END)
    common, body = extract_marker(body, COMMON_BEGIN, COMMON_END)
    pref, body = extract_marker(body, PREF_BEGIN, PREF_END)

    top = [part for part in [prefix, h1, snap, one, fig, lit, img] if part]
    bottom = body.strip()
    extras = [part for part in [common, pref] if part]
    if extras:
        anchors = ["\n## References", "\n<!-- BEGIN REVERSE APPROACH LINKS -->"]
        positions = [bottom.find(a) for a in anchors if bottom.find(a) != -1]
        pos = min(positions) if positions else -1
        extra_text = "\n\n".join(extras)
        if pos == -1:
            bottom = bottom.rstrip() + "\n\n" + extra_text
        else:
            bottom = bottom[:pos].rstrip() + "\n\n" + extra_text + "\n" + bottom[pos:]
    return "\n\n".join([p for p in top + [bottom] if p]).strip() + "\n"


def update_logistics_and_positioning(path: Path, text: str) -> str:
    title = fm_title(text, path.stem)
    note = table_note(path, title)
    lines = text.splitlines()
    out: list[str] = []
    for line in lines:
        if line.startswith("- **Typical bed:**"):
            if is_spine_path(path):
                out.append(f"- **OR table/bed:** {note}")
            continue
        out.append(line)
    text = "\n".join(out)
    if not is_spine_path(path):
        return text
    bullet = f"- **OR table/bed:** {note}"
    # Insert the same OR table choice under the first positioning section.
    pattern = re.compile(r"(?m)^(## (?:\d+\.\s*)?Positioning|### (?:Patient )?Position)\s*$")
    m = pattern.search(text)
    if not m:
        return text
    after_heading = text[m.end(): text.find("\n## ", m.end()) if text.find("\n## ", m.end()) != -1 else len(text)]
    if "- **OR table/bed:**" in after_heading:
        return text
    insert = m.end()
    return text[:insert] + "\n" + bullet + text[insert:]


def cleanup_spacing(text: str) -> str:
    text = re.sub(r"(?m)^---\n\s*\n---$", "---", text)
    text = re.sub(r"\n{3,}---\n(?:\s*\n---\n)+", "\n\n---\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    for path in guide_paths():
        text = read(path)
        text = replace_ao_links(text)
        about, text = extract_about_figures(text)
        text = normalize_top_order(text)
        text = insert_figure_note(text, about)
        text = update_logistics_and_positioning(path, text)
        text = cleanup_spacing(text)
        write(path, text)
    media = ROOT / "resources" / "media-sources.md"
    if media.exists():
        text = replace_ao_links(read(media))
        write(media, text)
    print(f"Normalized {len(guide_paths())} guide pages.")


if __name__ == "__main__":
    main()
