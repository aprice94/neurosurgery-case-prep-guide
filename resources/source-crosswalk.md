---
title: "Source Crosswalk & Copyright-Safe Use"
description: "How to use textbook, PubMed, board-card, and open-media sources in the case-prep guide without re-hosting copyrighted material."
category: "Resources"
tags:
  - "sources"
  - "copyright"
  - "textbooks"
  - "pubmed"
---

# Source Crosswalk & Copyright-Safe Use

This page is the source discipline layer for the guide. It captures what can be learned from textbook/RAG tools, PubMed, board-review cards, and open-media collections while keeping the public site clean: cite copyrighted works, summarize in original language, and embed only material with a license that permits reuse.

> Practical rule: **download and embed open-license material; link and cite copyrighted material; never re-host textbook pages, textbook figures, SANS/ABNS cards, or proprietary operative atlases.**

---

## Evidence lanes to use for every guide

| Lane | Best use | Public-site handling |
|---|---|---|
| Textbook corpus | Operative anatomy, exposure logic, standard steps, complication avoidance | Cite book/chapter/page when available; summarize in original words; do not copy text, tables, or figures |
| Contemporary literature | Outcomes, indications, comparative data, modern technique updates | Link PubMed/DOI; embed figures only from PMC Open Access articles with compatible license |
| Open media | Anatomy plates, open-access diagrams, selected operative/anatomic figures | Download and embed only if PD/CC license permits reuse; include attribution/license |
| Board cards | High-yield recall points, common exam framing, pitfalls | Use as a private study signal only; do not copy questions, explanations, or card images |
| Operative atlases/videos | Step sequencing, anatomy-in-action, technical nuance | Link to source pages/videos; do not re-host copyrighted media |

---

## What is safe to download and embed

| Source type | Download/embed? | Notes |
|---|---:|---|
| PMC Open Access Subset, CC0 / CC BY / CC BY-SA | Yes | Keep article title, journal, year, URL/PMCID, author attribution when available, and license |
| PMC Open Access Subset, CC BY-NC / CC BY-NC-SA | Usually for noncommercial education only | Avoid commercial reuse; keep full attribution and license |
| Public-domain anatomy plates | Yes | Gray's, Sobotta, and other historical works are useful; cite original work and repository |
| Wikimedia Commons PD/CC media | Yes, if license allows | Check the file page, not just the article page |
| U.S. government public-domain material | Usually yes | Still check whether images inside the article are third-party copyrighted |
| PubMed citations and abstracts | Link/cite, do not bulk-copy abstracts | PubMed metadata and links are safe; article text/figures depend on publisher license |
| Your own diagrams or photos | Yes | Best option when you need reusable, shareable teaching visuals |

## What not to re-host

- Textbook PDFs, textbook pages, textbook figures, or cropped screenshots.
- Rhoton, Youmans/Winn, Greenberg, Schmidek/Sweet, Benzel, Neuroangiography, AO, Neurosurgical Atlas, and similar proprietary plates unless the source explicitly grants reusable rights.
- SANS/ABNS question stems, explanations, and associated images.
- Radiopaedia images unless the specific license and noncommercial terms fit the intended use.
- Any “free PDF” found by search unless the publisher, author, or repository clearly licenses redistribution.

---

## Textbook crosswalk

Use these as **check sources**, not copy sources.

| Domain | First textbooks to check | What to extract into the guide |
|---|---|---|
| Cranial microsurgical anatomy | Rhoton Cranial Anatomy; Brain Anatomy and Neurosurgical Approaches; Youmans and Winn | Surgical corridors, cisterns, nerves/vessels at risk, safe entry zones |
| Aneurysm / vascular surgery | Rhoton; Decision Making in Neurovascular Disease; Youmans and Winn; Schmidek and Sweet; Practical Neuroangiography | Proximal control, perforator anatomy, clip/reconstruction strategy, bypass/rescue options |
| Skull base / tumor | Youmans and Winn; Schmidek and Sweet; Rhoton; Brain Anatomy and Neurosurgical Approaches; CNS Radiation Oncology Principles and Practice | Approach selection, neurovascular relationships, reconstruction, adjuvant-therapy context |
| Spine degenerative / trauma / deformity | Benzel Spine; Youmans and Winn; Textbook of Spinal Surgery; Surgical Anatomy and Techniques to the Spine; Greenberg | Indications, positioning, exposure, decompression/fusion sequence, biomechanical rationale |
| Functional / epilepsy / pain | Schmidek and Sweet; Youmans and Winn; Greenberg | Targets, trajectories, mapping, monitoring, programming/follow-up concepts |
| CSF / shunts / ETV | Greenberg; Youmans and Winn; Schmidek and Sweet | Entry points, hardware choices, failure modes, revision algorithm |
| Endovascular / angiography | Practical Neuroangiography; Decision Making in Neurovascular Disease; Greenberg | Angioanatomy, access strategy, device class, complication rescue |
| Imaging review | Neuroradiology Core Requisites; Radiopaedia links; disease-specific literature | Imaging signs, differentials, vascular/tract relationships |

---

## How to summarize copyrighted textbook material

Use this pattern inside any guide:

1. Read the textbook section privately.
2. Close the source.
3. Write the operative implication in your own words.
4. Add a short citation such as: `Rhoton Cranial Anatomy, cerebellar arteries chapter; Youmans and Winn, posterior fossa approach chapter.`
5. If a figure is essential, link the source or replace it with an open-license figure or original diagram.

Good public phrasing:

- “Key cross-checks: review the relationship of the PICA tonsillomedullary segment to the lower cranial nerves in Rhoton and Youmans before a telovelar/posterior fossa case.”
- “Textbook synthesis: standard references emphasize early proximal control, perforator visualization, and avoidance of blind bipolar work around the aneurysm neck.”

Avoid:

- Copying a textbook paragraph with minor word changes.
- Cropping a figure and adding a citation.
- Copying board-card answers or proprietary explanations.
- Reproducing tables, algorithms, or checklists from a copyrighted source.

---

## Incorporate into each guide

Each procedure page should eventually have:

- **Case / approach snapshot:** an upfront synthesis of anatomy at risk, operative steps, rescue plans, figures, papers, and textbook cross-checks.
- **Textbook cross-checks:** 3-6 source families to review before the case.
- **Open figures:** 10+ unique PD/CC/open-access figures when possible.
- **Primary literature:** seminal papers plus modern reviews/trials/guidelines.
- **Private-board prompts:** topic keywords only, not copied stems or answers.
- **Operative atlas/video links:** links only for copyrighted sources.

Suggested snapshot block:

```markdown
## Case / Approach Snapshot
- **Anatomy at risk:** [patient- and corridor-specific structures]
- **Operative steps:** [positioning, exposure, key maneuver, verification, closure]
- **Rescue plans:** [bleeding, neurologic change, CSF leak, reconstruction/device failure, staged alternate plan]
- **Figures:** [open-license figures and linked videos/atlases]
- **Papers:** [seminal and modern evidence]
- **Textbook cross-checks:** [copyrighted sources to cite and summarize, not copy]
```

Suggested textbook block:

```markdown
## Textbook Cross-Checks
- **Microsurgical anatomy:** [book/chapter/page if available] — summarize the anatomy at risk in your own words.
- **Operative technique:** [book/chapter/page if available] — summarize exposure, sequence, and pitfalls.
- **Complication rescue:** [book/chapter/page if available] — summarize bailout options and postoperative concerns.
```

---

## Verified open-source routes

- [PMC Open Access Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/) — articles and media with reuse licenses; terms vary by article.
- [PMC Copyright Notice](https://pmc.ncbi.nlm.nih.gov/about/copyright/) — explains why most PMC content still needs article-level license review.
- [PubMed open-access filter](https://pubmed.ncbi.nlm.nih.gov/?term=pubmed+pmc+open+access%5Bfilter%5D) — search lane for reuse-candidate articles.
- [Wikimedia Commons](https://commons.wikimedia.org/) — use file-page license, not just search result.
- [Wellcome Collection](https://wellcomecollection.org/works) — many historical medical images with clear rights statements.
- [Internet Archive](https://archive.org/) — useful for public-domain historical anatomy books; verify publication date and rights status.
- [U.S. Copyright Office fair-use resources](https://www.copyright.gov/fair-use/) — fair use is contextual, not a blanket permission.

---

## Lessons from Neuro-Caseboard-style tools

The useful idea is not to copy the private corpus. The useful idea is the **workflow**:

- Treat every answer as a snapshot built from separate lanes: textbooks, literature, figures, and cards.
- Keep citation anchors close to every claim.
- Show when a lane is unavailable rather than inventing filler.
- Preserve figures as evidence objects with source, page/article, caption, license, and URL.
- Let users rehearse: mark “important,” “wrong,” or “missing” claims, then feed that back into the next prep pass.

Those patterns can be added to this site without importing protected source material.
