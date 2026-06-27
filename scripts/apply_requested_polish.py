#!/usr/bin/env python3
"""Apply requested Pterion Prep polish and guide-wide teaching blocks."""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "cases"
TODAY = date.today().isoformat()

COMMON_BEGIN = "<!-- BEGIN COMMON PIMP QUESTIONS -->"
COMMON_END = "<!-- END COMMON PIMP QUESTIONS -->"
PREF_BEGIN = "<!-- BEGIN ATTENDING PREFERENCE VARIABLES -->"
PREF_END = "<!-- END ATTENDING PREFERENCE VARIABLES -->"
REV_BEGIN = "<!-- BEGIN REVERSE APPROACH LINKS -->"
REV_END = "<!-- END REVERSE APPROACH LINKS -->"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith("  "):
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip().strip('"')
    return data, text[end + 4 :]


def clean_title(title: str) -> str:
    title = re.sub(r"^(Case Prep|Approach|Operative Approach):\s*", "", title)
    return re.sub(r"\s+", " ", title).strip()


def replace_block(text: str, begin: str, end: str, block: str) -> str:
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        return pattern.sub(block.strip(), text)
    insert_at = text.find("\n## References")
    if insert_at == -1:
        insert_at = text.find("\n<!-- BEGIN CURATED LITERATURE -->")
    if insert_at == -1:
        return text.rstrip() + "\n\n" + block.strip() + "\n"
    return text[:insert_at].rstrip() + "\n\n" + block.strip() + "\n" + text[insert_at:]


def category_family(category: str, title: str) -> str:
    blob = f"{category} {title}".lower()
    if "approach" in category.lower() or title.lower().startswith("approach:"):
        return "approach"
    if "vascular" in blob or "aneurysm" in blob or "avm" in blob or "bypass" in blob:
        return "vascular"
    if "spine" in blob or "cord" in blob or "vertebral" in blob:
        return "spine"
    if "csf" in blob or "shunt" in blob or "evd" in blob or "hydrocephalus" in blob:
        return "csf"
    if "trauma" in blob or "hematoma" in blob or "fracture" in blob or "craniectomy" in blob:
        return "trauma"
    if "endovascular" in blob or "thrombectomy" in blob or "stent" in blob or "embolization" in blob:
        return "endovascular"
    if "functional" in blob or "dbs" in blob or "epilepsy" in blob or "stimulator" in blob:
        return "functional"
    if "pediatric" in blob or "myelomeningocele" in blob or "craniosynostosis" in blob:
        return "pediatric"
    if "peripheral" in blob or "plexus" in blob or "carpal" in blob or "ulnar" in blob:
        return "peripheral"
    if "biopsy" in blob or "radiosurgery" in blob or "litt" in blob:
        return "stereotactic"
    return "tumor"


QUESTION_BANK = {
    "vascular": [
        "What is the proximal-control plan before the lesion is manipulated?",
        "Which branch, perforator, or venous structure is most likely to be injured in this exposure?",
        "What are the intraoperative rupture steps, including temporary clip, suction, BP, and backup clip strategy?",
        "What confirms treatment success: ICG, Doppler, puncture/deflation, DSA, or postoperative CTA?",
        "What postoperative BP, vasospasm, antiplatelet, or anticoagulation issue changes the orders tonight?",
    ],
    "spine": [
        "What neurologic level and root are responsible for the presenting deficit?",
        "What is the decompression target and how will you know it is adequately decompressed?",
        "What instability, deformity, bone-quality, or fusion variable changes the construct?",
        "What vascular, visceral, dural, or neural structure is the main structure at risk?",
        "What postop brace, drain, mobilization, MAP, antibiotic, and DVT plan should be ordered?",
    ],
    "csf": [
        "What is the working CSF physiology problem: obstruction, absorption failure, overdrainage, infection, or catheter failure?",
        "Where exactly is the entry point, target, and backup trajectory?",
        "What valve, catheter, endoscope, or navigation preference does the attending use?",
        "What is the infection-prevention plan and what cultures/CSF studies are needed?",
        "What postop imaging, valve setting, drainage level, and neuro-check plan should be written?",
    ],
    "trauma": [
        "What is the life-threatening mass-effect problem and what is the operative endpoint?",
        "What anticoagulant/antiplatelet reversal and blood-product plan is required before incision?",
        "What exposure gives rapid control while preserving options for expansion?",
        "What ICP, seizure, sodium, ventilation, and blood-pressure targets matter immediately postop?",
        "What injury pattern or associated lesion would change the incision, bone flap, or disposition?",
    ],
    "endovascular": [
        "What is the access plan and bailout access if anatomy is hostile?",
        "What catheter, wire, sheath, embolic, stent, or device sequence is planned?",
        "What antiplatelet/anticoagulation regimen is required before and after treatment?",
        "What defines technical success and what angiographic complication are you watching for?",
        "What ICU checks, BP goal, puncture-site plan, and follow-up imaging should be ordered?",
    ],
    "functional": [
        "What is the symptom target and what finding proves the correct neural structure is being treated?",
        "What imaging, tractography, MER, stimulation, or mapping information changes the trajectory?",
        "What medication adjustments or anesthesia constraints matter on the day of surgery?",
        "What complication would be subtle but important to detect in recovery?",
        "What postop programming, imaging, seizure, swallow, or cranial-nerve plan is needed?",
    ],
    "pediatric": [
        "What age-specific anatomy, blood volume, temperature, and positioning issue changes the plan?",
        "What is the neurologic, developmental, or syndromic baseline?",
        "What skin, wound, CSF, or infection risk is highest in this child?",
        "What family-facing expectation should be clarified before surgery?",
        "What postop bed, feeding, pain, imaging, and activity plan is safest?",
    ],
    "peripheral": [
        "Which nerve fascicles or branches must be identified before releasing or resecting tissue?",
        "What exam finding localizes the lesion and what alternative diagnosis could mimic it?",
        "What stimulation, ultrasound, microscope, tourniquet, or graft option should be ready?",
        "What motor/sensory function is at highest risk and how is it checked in PACU?",
        "What splint, therapy, wound, and neuropathic-pain plan should be written?",
    ],
    "stereotactic": [
        "What target coordinate, trajectory, and no-fly-zone were chosen?",
        "What imaging confirms target accuracy and avoids vessel/ventricle/sulcus violation?",
        "What specimen, pathology, culture, or molecular study must be obtained?",
        "What hemorrhage, edema, seizure, or thermal-injury sign must be watched for tonight?",
        "What postop scan timing and steroid/antiepileptic plan is appropriate?",
    ],
    "approach": [
        "What patient position and head rotation make gravity work for this corridor?",
        "What named nerve, vessel, sinus, or muscle/fascial plane is most commonly injured?",
        "What bone work or soft-tissue step creates the exposure rather than simply using more retraction?",
        "What is the bailout if exposure is inadequate, bleeding occurs, or the brain is tight?",
        "What closure maneuver prevents the signature complication of this approach?",
    ],
    "tumor": [
        "What is the surgical goal: gross-total, maximal safe, decompression, diagnosis, or cytoreduction?",
        "What eloquent cortex, tract, cranial nerve, vessel, or sinus defines the stopping point?",
        "What adjunct changes the case: navigation, mapping, 5-ALA, ultrasound, endoscope, ICG, or neuromonitoring?",
        "What is the edema, steroid, seizure, DVT, and postop imaging plan?",
        "What complication would you check for first in PACU based on this lesion location?",
    ],
}

PREFERENCE_BANK = {
    "vascular": [
        "Preferred approach side, sylvian split style, and cisternal-opening sequence",
        "Temporary clip threshold, burst-suppression preference, and BP during occlusion",
        "Clip manufacturer/shape sequence and whether Doppler, ICG, puncture, or intraop DSA is routine",
        "Antiplatelet/anticoagulation reversal and restart timing",
    ],
    "spine": [
        "Positioning frame, arms, traction, and localization workflow",
        "Navigation/robot/fluoro use, screw system, graft/biologic choice, and drain threshold",
        "Neuromonitoring modality and MAP goal for myelopathy, deformity, or cord-risk cases",
        "Brace, Foley, antibiotics, mobilization, and DVT prophylaxis timing",
    ],
    "csf": [
        "Valve brand/setting, antibiotic catheter use, and tunneling side",
        "Navigation/endoscope/stylet preference and ventricular target",
        "CSF culture/lab routine and perioperative antibiotic duration",
        "Postop scan timing, EVD height or valve verification, and activity restrictions",
    ],
    "trauma": [
        "Bone flap replacement versus decompressive storage threshold",
        "Preferred hemostatic agents, dural substitute, tack-up pattern, and drain use",
        "ICP monitor/EVD threshold, sodium target, seizure prophylaxis, and repeat CT timing",
        "Reversal product sequence and postop anticoagulation/DVT timing",
    ],
    "endovascular": [
        "Access site, sheath size, closure device, and heparinization target",
        "Device family, catheter/wire setup, and bailout inventory",
        "Antiplatelet loading/testing strategy and ICU BP target",
        "Follow-up angiography schedule and activity restrictions after access closure",
    ],
    "functional": [
        "Awake/asleep technique, MER/stimulation thresholds, and imaging confirmation",
        "Medication hold/restart protocol and programming timeline",
        "Hardware brand, tunneling side, battery pocket, and antibiotic envelope preference",
        "Postop CT/MRI timing and symptom-specific neuro checks",
    ],
    "pediatric": [
        "Blood availability threshold, warming strategy, antibiotic dosing, and Foley/drain use",
        "Positioning aids, pinning versus horseshoe, and skin-prep preference",
        "Family update cadence and expected ICU/floor disposition",
        "Postop feeding, pain regimen, wound care, and activity restrictions",
    ],
    "peripheral": [
        "Tourniquet use, loupe versus microscope, stimulator settings, and incision length",
        "External neurolysis versus transposition/reconstruction threshold",
        "Graft/conduit/allograft availability and pathology handling",
        "Splinting position, therapy referral, and activity restrictions",
    ],
    "stereotactic": [
        "Frame versus frameless/robot platform and planning software",
        "Trajectory constraints, number of cores/targets, and frozen/permanent pathology plan",
        "Steroid/antiepileptic prophylaxis and postop scan timing",
        "Admit versus discharge threshold and neuro-check frequency",
    ],
    "approach": [
        "Exact head rotation/flexion/extension and pin placement",
        "Skin incision length, flap type, and muscle/fascial preservation technique",
        "Drill, rongeur, endoscope, microscope, retractor, and navigation preferences",
        "Drain use, closure materials, watertightness threshold, and postop imaging routine",
    ],
    "tumor": [
        "Extent-of-resection goal and functional stopping points",
        "Mapping/monitoring, 5-ALA, ultrasound, ICG, endoscope, or tractography preferences",
        "Steroid, antiepileptic, mannitol/hypertonic saline, and antibiotic plan",
        "Postop MRI timing, ICU/floor threshold, and adjuvant-referral workflow",
    ],
}


def teaching_blocks(title: str, category: str) -> tuple[str, str]:
    family = category_family(category, title)
    short = clean_title(title)
    qs = "\n".join(f"{idx}. {q}" for idx, q in enumerate(QUESTION_BANK[family], 1))
    prefs = "\n".join(f"- **{item}:** [attending-specific]" for item in PREFERENCE_BANK[family])
    common = f"""
{COMMON_BEGIN}

## Common Pimp Questions

Use these to pressure-test preparation for **{short}**:

{qs}

{COMMON_END}
"""
    pref = f"""
{PREF_BEGIN}

## Attending Preference Variables

Items that commonly vary by surgeon or institution:

{prefs}

{PREF_END}
"""
    return common, pref


def guide_paths() -> list[Path]:
    return sorted(p for p in CASES.rglob("*.md") if p.name != "index.md")


def add_teaching_sections() -> None:
    for path in guide_paths():
        text = read(path)
        data, _ = front_matter(text)
        title = data.get("title", path.stem.replace("-", " ").title())
        category = data.get("category", "")
        common, pref = teaching_blocks(title, category)
        text = replace_block(text, COMMON_BEGIN, COMMON_END, common)
        text = replace_block(text, PREF_BEGIN, PREF_END, pref)
        write(path, text)


def build_reverse_links() -> dict[Path, list[Path]]:
    refs: dict[Path, list[Path]] = defaultdict(list)
    approach_root = (CASES / "approaches").resolve()
    for src in guide_paths():
        if src.parent == CASES / "approaches":
            continue
        text = read(src)
        for target in re.findall(r"\(([^)]+approaches/[^)#]+\.md)(?:#[^)]+)?\)", text):
            clean = target.split("#", 1)[0]
            resolved = (src.parent / clean).resolve()
            try:
                resolved.relative_to(approach_root)
            except ValueError:
                continue
            if resolved.exists() and src not in refs[resolved]:
                refs[resolved].append(src)
    return refs


def title_for(path: Path) -> str:
    data, _ = front_matter(read(path))
    return clean_title(data.get("title", path.stem.replace("-", " ").title()))


def rel_link(src: Path, dst: Path) -> str:
    return Path("../" * (len(src.parent.relative_to(ROOT).parts))).joinpath(dst.relative_to(ROOT)).as_posix()


def add_reverse_links() -> None:
    refs = build_reverse_links()
    for approach in sorted((CASES / "approaches").glob("*.md")):
        if approach.name in {"index.md"}:
            continue
        cases = sorted(refs.get(approach, []), key=lambda p: title_for(p))
        if cases:
            links = "\n".join(f"- [{title_for(case)}]({rel_link(approach, case)})" for case in cases)
        else:
            links = "- No case guide currently links directly to this approach."
        block = f"""
{REV_BEGIN}

## Case Guides Using This Approach

{links}

{REV_END}
"""
        text = read(approach)
        text = re.sub(
            r"\n## Pathology guides that use this approach\n(?:.*?)(?=\n## References|\n<!-- BEGIN CURATED LITERATURE -->|\Z)",
            "\n",
            text,
            flags=re.S,
        )
        text = replace_block(text, REV_BEGIN, REV_END, block)
        write(approach, text)


def update_review_dates() -> None:
    lines = ["# Per-guide last-reviewed dates.", f"# Regenerated by scripts/apply_requested_polish.py on {TODAY}."]
    for path in sorted((CASES).rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        lines.append(f'"{rel}": "{TODAY}"')
    write(ROOT / "_data" / "reviewed.yml", "\n".join(lines) + "\n")


def main() -> None:
    add_reverse_links()
    add_teaching_sections()
    update_review_dates()
    print(f"Updated teaching sections, reverse approach links, and review dates for {len(guide_paths())} guides.")


if __name__ == "__main__":
    main()
