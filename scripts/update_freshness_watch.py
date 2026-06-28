#!/usr/bin/env python3
"""Generate a weekly PubMed/CNS/Atlas candidate-watch page.

This intentionally writes a review queue rather than editing clinical guide text.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resources" / "freshness-updates.md"
GUIDES = ROOT / "cases"
USER_AGENT = "PterionPrepFreshness/1.0 (https://pterionprep.com)"
MAX_GUIDES = int(os.environ.get("PTERION_FRESHNESS_MAX_GUIDES", "126"))
CNS_CHANNEL_ID = "UCzKAjY4k-vl-MvrRO9ghSRQ"

STOPWORDS = {
    "case", "prep", "operative", "approach", "resection", "placement",
    "surgery", "surgical", "neurosurgery", "neurosurgical", "guide",
    "reference", "open", "with", "and", "for", "the", "of", "to",
}


def fetch(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        allow_insecure = os.environ.get("PTERION_FRESHNESS_ALLOW_INSECURE_TLS") == "1"
        if not allow_insecure or "CERTIFICATE_VERIFY_FAILED" not in str(exc):
            raise
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
            return resp.read().decode("utf-8", errors="replace")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def front_matter_title(text: str, fallback: str) -> str:
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', text, re.M)
    if match:
        return match.group(1).strip()
    h1 = re.search(r"^#\s+(.+)$", text, re.M)
    return h1.group(1).strip() if h1 else fallback


def guides() -> list[tuple[Path, str]]:
    items: list[tuple[Path, str]] = []
    for path in sorted(GUIDES.rglob("*.md")):
        if path.name == "index.md":
            continue
        text = read_text(path)
        title = front_matter_title(text, path.stem.replace("-", " "))
        title = re.sub(r"^(Case Prep:|Operative Approach:)\s*", "", title).strip()
        items.append((path, title))
    return items[:MAX_GUIDES]


def existing_pmids() -> set[str]:
    ids: set[str] = set()
    for path in ROOT.rglob("*.md"):
        if "_site" in path.parts:
            continue
        ids.update(re.findall(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)/?", read_text(path)))
    return ids


def topic_terms(title: str) -> list[str]:
    raw = re.findall(r"[A-Za-z][A-Za-z0-9]+", title.lower())
    terms = [t for t in raw if len(t) > 3 and t not in STOPWORDS]
    return terms[:7]


def pubmed_candidates(path: Path, title: str, known_pmids: set[str]) -> list[dict[str, str]]:
    terms = topic_terms(title)
    if not terms:
        return []
    phrase = re.sub(r"[^A-Za-z0-9 /-]", " ", title).strip()
    joined = " AND ".join(f"{term}[Title/Abstract]" for term in terms[:4])
    query = (
        f'("{phrase}"[Title/Abstract] OR ({joined})) '
        'AND (neurosurgery[Title/Abstract] OR neurosurgical[Title/Abstract] '
        'OR craniotomy[Title/Abstract] OR spine[Title/Abstract] OR skull base[Title/Abstract])'
    )
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "retmode": "json",
        "sort": "pub+date",
        "retmax": "5",
        "term": query,
    })
    try:
        search = json.loads(fetch(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}"))
    except Exception as exc:
        return [{"error": f"PubMed search failed for {title}: {exc}"}]
    ids = [pmid for pmid in search.get("esearchresult", {}).get("idlist", []) if pmid not in known_pmids]
    if not ids:
        return []
    time.sleep(0.35)
    summary_params = urllib.parse.urlencode({
        "db": "pubmed",
        "retmode": "json",
        "id": ",".join(ids[:3]),
    })
    try:
        summary = json.loads(fetch(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{summary_params}"))
    except Exception as exc:
        return [{"error": f"PubMed summary failed for {title}: {exc}"}]
    out: list[dict[str, str]] = []
    result = summary.get("result", {})
    for pmid in ids[:3]:
        item = result.get(pmid)
        if not item:
            continue
        out.append({
            "title": item.get("title", "").rstrip("."),
            "journal": item.get("fulljournalname") or item.get("source", ""),
            "date": item.get("pubdate", ""),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "guide": str(path.relative_to(ROOT)),
            "guide_title": title,
        })
    return out


def youtube_channel_id() -> str | None:
    try:
        text = fetch("https://www.youtube.com/@cnsvideolibrary", timeout=20)
    except Exception:
        return None
    patterns = [
        r'"channelId":"(UC[^"]+)"',
        r'<meta itemprop="channelId" content="(UC[^"]+)">',
        r'https://www.youtube.com/channel/(UC[^"?/]+)',
        r'/channel/(UC[^"?/]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return CNS_CHANNEL_ID


def cns_videos() -> list[dict[str, str]]:
    channel_id = youtube_channel_id()
    if not channel_id:
        return []
    try:
        xml = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
    except Exception:
        return []
    root = ET.fromstring(xml)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
    }
    videos: list[dict[str, str]] = []
    for entry in root.findall("atom:entry", ns)[:15]:
        title = entry.findtext("atom:title", default="", namespaces=ns)
        video_id = entry.findtext("yt:videoId", default="", namespaces=ns)
        published = entry.findtext("atom:published", default="", namespaces=ns)[:10]
        if title and video_id:
            videos.append({
                "title": title,
                "date": published,
                "url": f"https://www.youtube.com/watch?v={video_id}",
            })
    return videos


def relevant_guides_for_video(title: str, guide_items: list[tuple[Path, str]]) -> list[tuple[Path, str]]:
    video_terms = set(topic_terms(title))
    if not video_terms:
        return []
    scored: list[tuple[int, Path, str]] = []
    for path, guide_title in guide_items:
        overlap = video_terms.intersection(topic_terms(guide_title))
        if overlap:
            scored.append((len(overlap), path, guide_title))
    scored.sort(reverse=True, key=lambda item: item[0])
    return [(path, guide_title) for _, path, guide_title in scored[:5]]


def atlas_links(guide_items: list[tuple[Path, str]]) -> list[tuple[str, str, str]]:
    links = []
    for path, title in guide_items[:40]:
        query = urllib.parse.quote_plus(title)
        links.append((title, str(path.relative_to(ROOT)), f"https://www.neurosurgicalatlas.com/search?q={query}"))
    return links


def md_link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def write_page() -> None:
    guide_items = guides()
    known = existing_pmids()
    pubmed_rows: list[dict[str, str]] = []
    errors: list[str] = []
    for idx, (path, title) in enumerate(guide_items):
        rows = pubmed_candidates(path, title, known)
        for row in rows:
            if "error" in row:
                errors.append(row["error"])
            else:
                pubmed_rows.append(row)
        time.sleep(0.35)

    videos = cns_videos()
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "---",
        'title: "Weekly Freshness Watch"',
        'description: "Auto-generated PubMed, CNS video, and Atlas candidates for guide updates."',
        'category: "Resources"',
        "tags:",
        '  - "freshness"',
        '  - "PubMed"',
        '  - "CNS"',
        '  - "Atlas"',
        "---",
        "",
        "# Weekly Freshness Watch",
        "",
        f"_Last generated: {now}._",
        "",
        "This page is generated automatically. It surfaces candidate literature, CNS Video Library videos, and Atlas search targets for human review before clinical guide text is changed.",
        "",
        "## New PubMed Candidates Not Already Cited",
        "",
    ]
    if pubmed_rows:
        lines.extend(["| Candidate | Possible guide | Source |", "| --- | --- | --- |"])
        for row in pubmed_rows[:120]:
            guide = md_link(html.escape(row["guide_title"]), "../" + row["guide"].replace(".md", ".html"))
            source = f"{html.escape(row['journal'])} {html.escape(row['date'])}".strip()
            lines.append(f"| {md_link(html.escape(row['title']), row['url'])} | {guide} | {source} |")
    else:
        lines.append("No new PubMed candidates found outside the currently cited PMID set.")

    lines.extend(["", "## Recent CNS Video Library Candidates", ""])
    if videos:
        lines.extend(["| Video | Date | Possible local targets |", "| --- | --- | --- |"])
        for video in videos:
            targets = relevant_guides_for_video(video["title"], guide_items)
            if targets:
                target_text = ", ".join(md_link(html.escape(t), "../" + str(p.relative_to(ROOT)).replace(".md", ".html")) for p, t in targets)
            else:
                target_text = "No obvious guide match - triage manually"
            lines.append(f"| {md_link(html.escape(video['title']), video['url'])} | {video['date']} | {target_text} |")
    else:
        lines.append("Could not resolve the CNS Video Library feed this run.")

    lines.extend(["", "## Neurosurgical Atlas Search Targets", ""])
    lines.append("Atlas pages do not expose a simple public freshness API, so the workflow keeps high-yield search targets here for review.")
    lines.extend(["", "| Guide | Atlas search |", "| --- | --- |"])
    for title, guide, url in atlas_links(guide_items):
        lines.append(f"| {md_link(html.escape(title), '../' + guide.replace('.md', '.html'))} | {md_link('Atlas search', url)} |")

    if errors:
        lines.extend(["", "## Fetch Warnings", ""])
        for err in errors[:20]:
            lines.append(f"- {html.escape(err)}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    write_page()
