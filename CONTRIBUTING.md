# Contributing & Style Guide

This is primarily a personal knowledge base, but these conventions keep it consistent and easy to extend.

## Adding a new case guide
1. Copy [`templates/case-prep-template.md`](templates/case-prep-template.md) into the correct category folder under `cases/`.
2. Name the file in `kebab-case.md` (e.g., `thoracic-discectomy.md`).
3. Keep the standard section order:
   - One-Liner → HPI → PMH → Imaging Review → Labs → Neurological Examination → Surgical Planning (Diagnosis/Indication · Position · Incision · Approach · Key Surgical Steps · Critical Anatomy & Structures at Risk · Equipment · Monitoring · Anesthesia · Potential Complications) → Operative Note → Postoperative Plan
4. Write the **Operative Note** in the full dictation-ready format: Preoperative/Postoperative Diagnosis, header block (surgeon, anesthesia, EBL, adjuncts, implants, monitoring, complications), an indications paragraph, and a step-by-step description — with bracketed `[ ]` placeholders for patient-specific values.
5. Add the new guide to [`INDEX.md`](INDEX.md) (table row + update the category count and the summary table).

## Style
- Bold the **critical safety points** (structures at risk, "never" steps, danger zones).
- Prefer concise clinical phrasing over prose; bullet lists and numbered steps.
- Cite source frameworks/classifications by name (e.g., Spetzler-Martin, SINS, TLICS, Koos, Simpson).
- Keep every guide self-contained.

## Categories
`cranial-vascular`, `cranial-tumor`, `cranial-trauma`, `cranial-csf` (+ `shunts/`), `cranial-functional`, `biopsy`, `radiosurgery`, `endovascular`, `spine-degenerative`, `spine-tumor`, `spine-trauma`, `spine-vascular`, `spine-congenital`, `spine-infection`, `spine-deformity`, `spine-functional`, `peripheral-nerve`, `pediatric`.

## Medical accuracy
All content must be verifiable against standard references (see [`resources/neurosurgery-resources.json`](resources/neurosurgery-resources.json)). When in doubt, flag uncertainty rather than assert. Remember the [DISCLAIMER](DISCLAIMER.md): this is a study aid, not a clinical authority.
