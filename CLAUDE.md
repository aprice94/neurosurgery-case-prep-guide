# CLAUDE.md — Neurosurgery Case Prep Guide

Neurosurgical case-preparation knowledge base (107 case guides + operative-approach chapters), published as a GitHub Pages site. **This folder is the project root** (`/Users/anthonyprice/Documents/Neurosurgery Case Prep Guide`).

## Layout
- `INDEX.md` — homepage (`permalink: /`): filterable bullet-list landing with hero + category cards.
- `cases/<category>/*.md` — 18 categories of case guides (one-liner, HPI, imaging, exam, surgical planning, dictation-ready op note, post-op).
- `cases/approaches/*.md` — detailed operative-approach chapters at full "Atlas" depth. **5/18 done:** pterional, retrosigmoid, orbitozygomatic, subtemporal, far-lateral.
- `figures/` — only public-domain (Gray/Sobotta) + CC-BY images are stored; all credited in `figures/CREDITS.md`.
- Custom Jekyll theme: `_config.yml`, `_layouts/default.html`, `assets/css/style.scss`.

## Conventions
- Every clinical guide has a `## Figures, Imaging & Video` section just before `## History of Present Illness`.
- **Figures policy:** LINK copyrighted operative figures (Neurosurgical Atlas, Rhoton); EMBED only public-domain or CC-BY images, downloaded locally into `figures/`, credited in `CREDITS.md`. **Never** create AI-generated/hand-drawn figures.
- **CC-BY figure pipeline:** Cureus "Immersive Surgical Anatomy of the X Approach" series + Frontiers + MDPI. Download blobs from `cdn.ncbi.nlm.nih.gov/pmc/blobs/...` via `curl`, resize with `sips -Z 1200` (webp → jpg via `sips -s format jpeg -Z 1200`).
- **Atlas links:** use verified clean URLs `https://www.neurosurgicalatlas.com/volumes/...` — do NOT guess `10.18791/nsatlas` DOIs.
- **kramdown tables need a BLANK LINE before them**, or they render as raw `|` pipes on the Pages site.

## GitHub Pages
- Live: https://aprice94.github.io/neurosurgery-case-prep-guide/ (custom theme, kramdown `input: GFM`, `baseurl: /neurosurgery-case-prep-guide`).
- After pushing, verify the build: `gh api repos/aprice94/neurosurgery-case-prep-guide/pages/builds/latest --jq '.status'` and confirm `.commit` == HEAD before trusting `curl` checks (stale-build race).
- `gh` CLI is at `/opt/homebrew/bin/gh`. Network ops (push, gh api) need the sandbox disabled.

## Working style
- Full autonomy: **do not ask permission — proceed and report after.** Build **both** tracks continuously: finish the remaining approach chapters AND deepen the case guides (more depth + more figures each), pushing per item.
