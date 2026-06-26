#!/usr/bin/env python3
"""Add source-backed literature and open-access image sets to guide pages.

The script uses NCBI E-utilities against PubMed/PMC, stores downloaded open
figures under figures/curated/<page-slug>/, and writes deterministic Markdown
blocks guarded by BEGIN/END markers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "enrichment"
FIG_ROOT = ROOT / "figures" / "curated"
EMAIL = "anthonyprice.neurosurgery.caseprep@example.com"
UA = "neurosurgery-case-prep-guide/1.0 (educational curation; contact via GitHub)"
PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
PMC_ARTICLE_BASE = "https://pmc.ncbi.nlm.nih.gov/articles"
PMC_S3_BASE = "https://pmc-oa-opendata.s3.amazonaws.com"
XLINK = "{http://www.w3.org/1999/xlink}href"

LIT_BEGIN = "<!-- BEGIN CURATED LITERATURE -->"
LIT_END = "<!-- END CURATED LITERATURE -->"
IMG_BEGIN = "<!-- BEGIN CURATED IMAGE SET -->"
IMG_END = "<!-- END CURATED IMAGE SET -->"

SKIP_FILES = {"index.md"}

TOPIC_OVERRIDES = {
    "shunt-revision.md": {
        "tokens": {"shunt", "malfunction", "revision", "infection", "valve", "catheter", "obstruction"},
        "queries": [
            "CSF shunt malfunction revision valve catheter",
            "ventriculoperitoneal shunt revision infection obstruction catheter",
            "cerebrospinal fluid shunt malfunction imaging catheter valve",
        ],
    },
    "shunt-systems-reference.md": {
        "tokens": {"shunt", "valve", "catheter", "programmable", "antisiphon", "reservoir"},
        "queries": [
            "CSF shunt valve programmable catheter reservoir",
            "ventriculoperitoneal shunt valve catheter programmable antisiphon",
            "cerebrospinal fluid shunt valve design trial Drake",
            "programmable valve hydrocephalus shunt trial",
            "antisiphon device shunt hydrocephalus valve",
            "ventriculoperitoneal shunting devices hydrocephalus Cochrane",
            "pediatric hydrocephalus valve type guideline shunt efficacy",
            "gravitational shunt valve idiopathic normal pressure hydrocephalus trial",
        ],
    },
    "ventriculopleural-shunt.md": {
        "tokens": {"ventriculopleural", "pleural", "shunt", "catheter", "effusion"},
        "queries": [
            "ventriculopleural shunt pleural catheter effusion",
            "ventriculopleural shunt hydrocephalus pleural cavity",
        ],
    },
    "lumboperitoneal-shunt.md": {
        "tokens": {"lumboperitoneal", "lumbar", "peritoneal", "shunt", "catheter"},
        "queries": [
            "lumboperitoneal shunt catheter hydrocephalus",
            "lumbar peritoneal shunt idiopathic intracranial hypertension",
        ],
    },
    "subduroperitoneal-shunt.md": {
        "tokens": {"subdural", "subduroperitoneal", "hygroma", "shunt", "catheter"},
        "queries": [
            "subduroperitoneal shunt subdural hygroma catheter",
            "subdural peritoneal shunt chronic subdural hygroma",
        ],
    },
}


@dataclass
class Page:
    path: Path
    title: str
    description: str
    category: str
    tags: list[str]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"&", " and ", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:88] or "guide"


def clean_title(title: str) -> str:
    title = re.sub(r"^(Case Prep|Operative Approach):\s*", "", title)
    title = re.sub(r"\([^)]*\)", " ", title)
    title = re.sub(r"[/–—:]", " ", title)
    title = re.sub(r"\b(with|and|or|for|the|to|of|a|an)\b", " ", title, flags=re.I)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def topic_phrase(title: str) -> str:
    phrase = clean_title(title)
    phrase = re.sub(
        r"\b(resection|placement|surgery|surgical|management|approach|craniotomy|"
        r"craniectomy|fusion|decompression|repair|release|revision|treatment|"
        r"operative|endoscopic|microsurgical|stereotactic)\b",
        " ",
        phrase,
        flags=re.I,
    )
    phrase = re.sub(r"\s+", " ", phrase).strip()
    return phrase or clean_title(title)


def topic_tokens(title: str) -> set[str]:
    stop = {
        "case", "prep", "reference", "system", "systems", "type", "types", "open",
        "operative", "approach", "surgical", "surgery", "placement", "resection",
        "repair", "fixation", "decompression", "drainage", "management", "guide",
        "with", "for", "and", "the", "shunt", "tumor", "tumour", "craniotomy",
        "spine", "spinal", "cranial", "brain", "cervical", "lumbar", "thoracic",
    }
    tokens = set(re.findall(r"[a-z0-9]+", topic_phrase(title).lower()))
    tokens = {t for t in tokens if len(t) >= 4 and t not in stop}
    if "ventriculopleural" in title.lower():
        tokens.update({"ventriculopleural", "pleural"})
    if "ventriculoatrial" in title.lower():
        tokens.update({"ventriculoatrial", "atrial"})
    if "epidural abscess" in title.lower():
        tokens.update({"epidural", "abscess"})
    return tokens


def page_override(page: Page) -> dict[str, set[str] | list[str]]:
    return TOPIC_OVERRIDES.get(page.path.name, {})


def parse_front_matter(path: Path) -> Page | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fm = text[4:end].splitlines()
    data: dict[str, str | list[str]] = {"tags": []}
    current_key = ""
    for line in fm:
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_key == "tags":
                data.setdefault("tags", [])
                assert isinstance(data["tags"], list)
                data["tags"].append(line[4:].strip().strip('"'))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            if value:
                data[current_key] = value.strip('"')
            elif current_key == "tags":
                data[current_key] = []
    title = str(data.get("title", path.stem.replace("-", " ").title()))
    return Page(
        path=path,
        title=title,
        description=str(data.get("description", "")),
        category=str(data.get("category", "")),
        tags=list(data.get("tags", [])) if isinstance(data.get("tags"), list) else [],
    )


def guide_pages() -> list[Page]:
    pages: list[Page] = []
    for path in sorted((ROOT / "cases").rglob("*.md")):
        if path.name in SKIP_FILES:
            continue
        page = parse_front_matter(path)
        if page:
            pages.append(page)
    return pages


def request_url(url: str, *, binary: bool = False, retries: int = 3) -> bytes | str:
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(url.encode("utf-8")).hexdigest() + (".bin" if binary else ".txt")
    cache_path = CACHE / key
    if cache_path.exists():
        data = cache_path.read_bytes()
        return data if binary else data.decode("utf-8", errors="ignore")
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(req, timeout=18, context=context) as resp:
                data = resp.read()
            cache_path.write_bytes(data)
            time.sleep(0.35)
            return data if binary else data.decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as exc:
            if exc.code in {403, 404, 410}:
                raise RuntimeError(f"HTTP {exc.code}: {url}") from exc
            last_exc = exc
            time.sleep(1.0 + attempt)
        except (urllib.error.URLError, TimeoutError) as exc:
            last_exc = exc
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"failed URL after retries: {url}: {last_exc}")


def ncbi_json(endpoint: str, params: dict[str, str | int]) -> dict:
    full = dict(params)
    full["retmode"] = "json"
    full["tool"] = "neurosurgery_case_prep_guide"
    full["email"] = EMAIL
    url = f"{PUBMED_BASE}/{endpoint}.fcgi?{urllib.parse.urlencode(full)}"
    text = request_url(url)
    return json.loads(text)


def ncbi_xml(endpoint: str, params: dict[str, str | int]) -> ET.Element:
    full = dict(params)
    full["tool"] = "neurosurgery_case_prep_guide"
    full["email"] = EMAIL
    url = f"{PUBMED_BASE}/{endpoint}.fcgi?{urllib.parse.urlencode(full)}"
    text = request_url(url)
    return ET.fromstring(text)


def page_queries(page: Page) -> list[str]:
    base = clean_title(page.title)
    topic = topic_phrase(page.title)
    compact_tags = " ".join(t for t in page.tags if t not in {"case", "prep", "operative", "approach"})
    override = page_override(page)
    queries = list(override.get("queries", [])) if override else []
    queries.extend([
        f'"{topic}"',
        f'"{topic}" neurosurgery',
        f'{topic} review',
        f'{topic} history',
        f'{topic} anatomy technique',
        f'("{base}"[Title/Abstract] OR {base}) neurosurgery surgery',
        f'{base} {compact_tags} operative management',
        f'{base} {page.category} outcomes surgical',
    ])
    if "Approach" in page.title:
        queries.insert(0, f'{base} microsurgical anatomy surgical approach')
    return [re.sub(r"\s+", " ", q).strip() for q in queries if q.strip()]


def literature_for_page(page: Page, count: int = 8) -> list[dict[str, str]]:
    seen: set[str] = set()
    ids: list[str] = []
    candidate_target = max(count * 5, count)
    for query in page_queries(page):
        data = ncbi_json("esearch", {
            "db": "pubmed",
            "term": query,
            "retmax": max(30, count * 4),
            "sort": "relevance",
        })
        for pmid in data.get("esearchresult", {}).get("idlist", []):
            if pmid not in seen:
                seen.add(pmid)
                ids.append(pmid)
            if len(ids) >= candidate_target:
                break
        if len(ids) >= candidate_target:
            break
    if not ids:
        return []
    summary_ids = ids[: max(count * 5, count)]
    summary = ncbi_json("esummary", {"db": "pubmed", "id": ",".join(summary_ids)})
    result = summary.get("result", {})
    items: list[dict[str, str]] = []
    for pmid in summary_ids:
        item = result.get(pmid, {})
        if not item:
            continue
        authors = item.get("authors") or []
        first_author = authors[0]["name"] if authors else ""
        pubdate = str(item.get("pubdate", "")).split(" ")[0]
        journal = item.get("fulljournalname") or item.get("source") or ""
        title = re.sub(r"\s+", " ", item.get("title", "")).strip().rstrip(".")
        if title:
            items.append({
                "pmid": pmid,
                "title": title,
                "journal": journal,
                "year": pubdate,
                "author": first_author,
            })
        if len(items) >= count:
            break
    return items


def text_content(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return re.sub(r"\s+", " ", "".join(node.itertext())).strip()


def pmc_ids_for_page(page: Page, retmax: int = 90) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for query in page_queries(page):
        term = f"({query}) AND open access[filter]"
        data = ncbi_json("esearch", {
            "db": "pmc",
            "term": term,
            "retmax": retmax,
            "sort": "relevance",
        })
        for pmcid in data.get("esearchresult", {}).get("idlist", []):
            if pmcid not in seen:
                seen.add(pmcid)
                ids.append(pmcid)
        if len(ids) >= retmax:
            break
    return ids


LOW_VALUE_FIGURE_TERMS = re.compile(
    r"\b("
    r"flowchart|prisma|forest plot|funnel plot|box and whisker|box-plot|roc curve|"
    r"scatter plot|linear regression|patient selection|study selection|"
    r"trial sequential analysis|search strategy|risk of bias|funnel|"
    r"cohort flow|screening flowchart"
    r")\b",
    re.I,
)


def is_low_value_media(media_url: str, fig: dict[str, str]) -> bool:
    name = Path(urllib.parse.urlparse(s3_https_url(media_url)).path).name.lower()
    if re.search(r"(^|[-_])(table|tbl)\d*", name):
        return True
    blob = " ".join([
        fig.get("label", ""),
        fig.get("caption", ""),
        fig.get("article_title", ""),
    ])
    return bool(LOW_VALUE_FIGURE_TERMS.search(blob))


def article_relevant_to_page(page: Page, fig: dict[str, str]) -> bool:
    tokens = topic_tokens(page.title)
    override = page_override(page)
    if override:
        tokens.update(override.get("tokens", set()))
    if not tokens:
        return True
    blob = f"{fig.get('article_title', '')} {fig.get('caption', '')}".lower()
    hits = {t for t in tokens if t in blob}
    if hits:
        return True
    # Allow broad approach anatomy articles when the page is itself an approach.
    if "Operative Approach:" in page.title:
        approach_words = set(re.findall(r"[a-z0-9]+", clean_title(page.title).lower()))
        return bool(approach_words & set(re.findall(r"[a-z0-9]+", blob)))
    return False


def s3_https_url(s3_url: str) -> str:
    if s3_url.startswith("s3://pmc-oa-opendata/"):
        return PMC_S3_BASE + "/" + s3_url[len("s3://pmc-oa-opendata/"):]
    return s3_url


def s3_prefixes_for_pmc(pmcid: str) -> list[str]:
    url = f"{PMC_S3_BASE}/?list-type=2&prefix={urllib.parse.quote(pmcid + '.')}&delimiter=%2F"
    root = ET.fromstring(request_url(url))
    prefixes: list[str] = []
    for node in root.findall(".//{http://s3.amazonaws.com/doc/2006-03-01/}CommonPrefixes/{http://s3.amazonaws.com/doc/2006-03-01/}Prefix"):
        if node.text:
            prefixes.append(node.text.strip("/"))
    return sorted(prefixes, key=lambda p: int(p.rsplit(".", 1)[-1]) if p.rsplit(".", 1)[-1].isdigit() else 0, reverse=True)


def s3_metadata_for_pmc(pmcid: str) -> dict | None:
    for prefix in s3_prefixes_for_pmc(pmcid):
        url = f"{PMC_S3_BASE}/metadata/{prefix}.json"
        try:
            return json.loads(request_url(url))
        except RuntimeError:
            continue
    return None


def iter_article_figures(pmc_numeric_id: str) -> list[dict[str, str]]:
    root = ncbi_xml("efetch", {"db": "pmc", "id": pmc_numeric_id})
    article = root.find(".//article")
    if article is None:
        return []
    pmcid = ""
    for node in article.findall(".//article-id"):
        if node.attrib.get("pub-id-type") == "pmc":
            pmcid = text_content(node)
            break
    if pmcid and not pmcid.startswith("PMC"):
        pmcid = "PMC" + pmcid
    if not pmcid:
        pmcid = "PMC" + pmc_numeric_id
    title = text_content(article.find(".//article-title"))
    journal = text_content(article.find(".//journal-title")) or text_content(article.find(".//journal-id"))
    year = text_content(article.find(".//pub-date/year"))
    license_type = ""
    lic = article.find(".//license")
    if lic is not None:
        license_type = lic.attrib.get("license-type", "") or text_content(lic.find(".//license-p"))[:80]
    figures: list[dict[str, str]] = []
    for fig in article.findall(".//fig"):
        label = text_content(fig.find("label")) or "Figure"
        caption = text_content(fig.find("caption"))
        graphics = fig.findall(".//graphic")
        if not graphics:
            continue
        href = graphics[0].attrib.get(XLINK, "")
        if not href:
            continue
        figures.append({
            "pmcid": pmcid,
            "article_title": title,
            "journal": journal,
            "year": year,
            "license": license_type,
            "label": label,
            "caption": caption,
            "href": href,
        })
    return figures


def image_ext(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return ".gif"
    if data[:64].lower().lstrip().startswith((b"<!doctype html", b"<html")):
        return None
    return None


def download_s3_media(media_url: str, out_base: Path) -> tuple[Path, str] | None:
    url = s3_https_url(media_url)
    try:
        data = request_url(url, binary=True, retries=1)
    except RuntimeError:
        return None
    assert isinstance(data, bytes)
    ext = image_ext(data)
    if not ext:
        return None
    out_path = out_base.with_suffix(ext)
    out_path.write_bytes(data)
    return out_path, url


def match_caption(media_url: str, figures: list[dict[str, str]]) -> dict[str, str] | None:
    media_name = Path(urllib.parse.urlparse(s3_https_url(media_url)).path).name
    media_stem = re.sub(r"\.(jpe?g|png|gif|tiff?)$", "", media_name, flags=re.I)
    for fig in figures:
        href = fig.get("href", "")
        href_stem = re.sub(r"\.(html|jpe?g|png|gif|tiff?)$", "", href, flags=re.I)
        if media_stem == href_stem or media_stem in href_stem or href_stem in media_stem:
            return fig
    return None


def caption_summary(fig: dict[str, str]) -> str:
    cap = fig.get("caption", "")
    cap = re.sub(r"\s+", " ", cap).strip()
    if len(cap) > 190:
        cap = cap[:187].rsplit(" ", 1)[0] + "..."
    return cap


def images_for_page(page: Page, count: int, used_urls: set[str]) -> list[dict[str, str]]:
    page_slug = slugify(page.title)
    out_dir = FIG_ROOT / page_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    selected: list[dict[str, str]] = []
    local_seen: set[str] = set()
    for pmc_id in pmc_ids_for_page(page):
        try:
            figs = iter_article_figures(pmc_id)
        except Exception as exc:
            print(f"WARN {page.path}: failed PMC {pmc_id}: {exc}", file=sys.stderr)
            continue
        pmcid = "PMC" + pmc_id if not str(pmc_id).startswith("PMC") else str(pmc_id)
        metadata = s3_metadata_for_pmc(pmcid)
        if not metadata:
            continue
        license_code = metadata.get("license_code") or "open access"
        media_urls = [
            u for u in metadata.get("media_urls", [])
            if re.search(r"\.(jpe?g|png|gif)(\?|$)", u, flags=re.I)
        ]
        for media_url in media_urls:
            source_key = media_url.split("?", 1)[0]
            if source_key in used_urls or source_key in local_seen:
                continue
            idx = len(selected) + 1
            fig = match_caption(media_url, figs) or {
                "pmcid": pmcid,
                "article_title": metadata.get("title", ""),
                "journal": metadata.get("citation", ""),
                "year": "",
                "license": license_code,
                "label": f"Figure {idx}",
                "caption": "",
                "href": Path(urllib.parse.urlparse(s3_https_url(media_url)).path).name,
            }
            fig["license"] = license_code
            fig["article_title"] = fig.get("article_title") or metadata.get("title", "")
            if is_low_value_media(media_url, fig) or not article_relevant_to_page(page, fig):
                continue
            out_base = out_dir / f"figure-{idx:02d}-{slugify(fig['label'] + '-' + fig.get('href', ''))}"
            downloaded = download_s3_media(media_url, out_base)
            if not downloaded:
                continue
            out_path, source_url = downloaded
            used_urls.add(source_key)
            local_seen.add(source_key)
            selected.append({
                **fig,
                "local": str(out_path.relative_to(ROOT)),
                "source_url": source_url,
            })
            if len(selected) >= count:
                return selected
    return selected


def rel_link(from_md: Path, target: str) -> str:
    rel = Path(target)
    return str(Path("../" * (len(from_md.relative_to(ROOT).parts) - 1)) / rel).replace("\\", "/")


def lit_block(page: Page, items: list[dict[str, str]]) -> str:
    lines = [LIT_BEGIN, "", "## High-Yield Literature", ""]
    for item in items[:10]:
        author = f"{item['author']}. " if item.get("author") else ""
        journal = item.get("journal", "")
        year = item.get("year", "")
        cite = " ".join(x for x in [journal, year] if x).strip()
        lines.append(
            f"- **{item['title']}** — {author}{cite}. "
            f"[PubMed](https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/)"
        )
    lines.extend(["", LIT_END])
    return "\n".join(lines)


def img_block(page: Page, figures: list[dict[str, str]]) -> str:
    lines = [IMG_BEGIN, "", "## Curated Image Set", ""]
    lines.append(
        "Open-access figures are embedded from PubMed Central articles and kept unique to this guide."
    )
    lines.append("")
    for fig in figures[:10]:
        local = rel_link(page.path, fig["local"])
        alt = f"{clean_title(page.title)} — {fig['label']}"
        lines.append(f"![{alt}]({local})")
        caption = caption_summary(fig)
        article = fig.get("article_title") or "PubMed Central article"
        journal_year = " ".join(x for x in [fig.get("journal", ""), fig.get("year", "")] if x)
        license_text = fig.get("license", "open access")
        source = f"https://pmc.ncbi.nlm.nih.gov/articles/{fig['pmcid']}/"
        if caption:
            lines.append(
                f"*{fig['label']}. {caption} Source: [{article}]({source})"
                f"{' — ' + journal_year if journal_year else ''}; {license_text}.*"
            )
        else:
            lines.append(
                f"*{fig['label']}. Source: [{article}]({source})"
                f"{' — ' + journal_year if journal_year else ''}; {license_text}.*"
            )
        lines.append("")
    lines.append(IMG_END)
    return "\n".join(lines)


def replace_block(text: str, begin: str, end: str, block: str) -> str:
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        return pattern.sub(block, text)
    insert_at = text.find("\n## History")
    if insert_at == -1:
        insert_at = text.find("\n## General")
    if insert_at == -1:
        insert_at = text.find("\n## Relevant")
    if insert_at == -1:
        insert_at = text.find("\n## Preoperative")
    if insert_at == -1:
        insert_at = text.find("\n## Imaging")
    if insert_at == -1:
        return text.rstrip() + "\n\n---\n\n" + block + "\n"
    return text[:insert_at].rstrip() + "\n\n" + block + "\n\n---\n" + text[insert_at:]


def remove_old_key_evidence(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("**📑 Key evidence"):
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].lstrip().startswith("-")):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def update_page(page: Page, lit: list[dict[str, str]], figs: list[dict[str, str]]) -> None:
    text = page.path.read_text(encoding="utf-8")
    text = remove_old_key_evidence(text)
    text = replace_block(text, LIT_BEGIN, LIT_END, lit_block(page, lit))
    text = replace_block(text, IMG_BEGIN, IMG_END, img_block(page, figs))
    page.path.write_text(text, encoding="utf-8")


def load_used_sources() -> set[str]:
    used: set[str] = set()
    for meta in FIG_ROOT.rglob("metadata.json"):
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for item in data:
            if "pmcid" in item and "href" in item:
                used.add(f"{item['pmcid']}:{item['href']}")
    return used


def save_metadata(page: Page, figs: list[dict[str, str]]) -> None:
    out_dir = FIG_ROOT / slugify(page.title)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metadata.json").write_text(json.dumps(figs, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--page", action="append", default=[])
    parser.add_argument("--pages-file")
    parser.add_argument("--articles", type=int, default=8)
    parser.add_argument("--images", type=int, default=5)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pages = guide_pages()
    page_args = list(args.page)
    if args.pages_file:
        page_args.extend(
            line.strip()
            for line in Path(args.pages_file).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        )
    if page_args:
        wanted = set(page_args)
        pages = [p for p in pages if str(p.path.relative_to(ROOT)) in wanted or p.path.name in wanted]
    if args.limit:
        pages = pages[: args.limit]

    if args.refresh and not args.dry_run:
        for page in pages:
            out_dir = FIG_ROOT / slugify(page.title)
            if out_dir.exists():
                shutil.rmtree(out_dir)

    used_sources = load_used_sources()
    failures: list[str] = []
    for index, page in enumerate(pages, start=1):
        print(f"[{index}/{len(pages)}] {page.path.relative_to(ROOT)}", flush=True)
        try:
            lit = literature_for_page(page, args.articles)
            figs = images_for_page(page, args.images, used_sources)
        except Exception as exc:
            failures.append(f"{page.path}: {exc}")
            print(f"  ERROR {exc}", file=sys.stderr)
            continue
        print(f"  literature={len(lit)} images={len(figs)}", flush=True)
        if len(lit) < 5:
            failures.append(f"{page.path}: only {len(lit)} literature items")
        if len(figs) < args.images:
            failures.append(f"{page.path}: only {len(figs)} images")
        if not args.dry_run:
            save_metadata(page, figs)
            update_page(page, lit, figs)
    if failures:
        print("\nFailures:", file=sys.stderr)
        for failure in failures[:80]:
            print(f"- {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
