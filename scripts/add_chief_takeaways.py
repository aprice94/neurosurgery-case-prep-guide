#!/usr/bin/env python3
"""Add consistent chief/attending-level takeaways to every guide."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- BEGIN CHIEF LEVEL TAKEAWAYS -->"
END = "<!-- END CHIEF LEVEL TAKEAWAYS -->"


def guide_paths() -> list[Path]:
    return sorted(p for p in (ROOT / "cases").rglob("*.md") if p.name != "index.md")


def frontmatter_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*\"?([^\"\n]+)\"?", text, re.M)
    return match.group(1).strip() if match else ""


def title_without_prefix(title: str) -> str:
    return re.sub(r"^(Case Prep:|Operative Approach:)\s*", "", title).strip()


def profile(path: Path, category: str) -> tuple[str, list[str]]:
    rel = path.relative_to(ROOT).as_posix()
    cat = category.lower()
    if rel.startswith("cases/approaches/"):
        return "Chief-Level Corridor Review", [
            "Define the exposure goal before incision: target, working angles, proximal/distal control, and the structure that cannot tolerate retraction.",
            "Know the first irreversible step: bone removal, dural opening, vascular control, or muscle/fascial division that commits the corridor.",
            "Verbalize the bailout: extend exposure, change trajectory, add CSF drainage, obtain proximal control, convert to a larger corridor, or stop for imaging.",
            "Protect closure from the start: vascularized tissue, watertight dural/reconstruction plan, dead-space control, and drain strategy should be chosen before the final intradural step.",
        ]
    if "vascular" in cat:
        return "Chief-Level Case Review", [
            "The operation is won or lost on control: identify inflow, outflow, perforators, collateral options, and the fastest route to temporary control before exposing the lesion itself.",
            "Do not accept a cosmetic result over physiology: ICG/Doppler/DSA, branch patency, perforator preservation, and parent-vessel caliber matter more than how the clip or resection bed looks.",
            "Have a rupture or ischemia script ready: lower pressure, suction strategy, temporary occlusion time, heparin/reversal plan, bypass/reconstruction threshold, and postop BP targets.",
            "Postop danger is delayed: vasospasm, thromboembolism, hyperperfusion, hemorrhage, edema, hydrocephalus, and seizure plans need explicit orders.",
        ]
    if "tumor" in cat or "skull" in cat:
        return "Chief-Level Case Review", [
            "Decide the real endpoint before opening: cure, cytoreduction, diagnosis, decompression, separation from critical structures, or safe maximal resection.",
            "Map what must be left behind: perforators, cranial nerves, venous sinuses, eloquent cortex/tracts, hypothalamus/pituitary axis, and adherent capsule planes.",
            "Sequence matters: devascularize early when safe, create CSF/working space, debulk before traction, and preserve the arachnoid plane unless oncologic goals justify violating it.",
            "The postop plan should match the risk structure: endocrine/vision/swallow/CN checks, steroid taper, seizure plan, MRI timing, CSF-leak watch, and adjuvant-treatment handoff.",
        ]
    if "trauma" in cat:
        return "Chief-Level Case Review", [
            "Treat physiology while preparing the room: airway, reversal, transfusion, ICP/CPP, sodium/osmolality, temperature, and repeat imaging drive timing as much as the scan finding.",
            "Know the operative priority: decompression, hemorrhage control, debridement, dural closure, reconstruction, stabilization, or contamination control.",
            "Plan for swelling and coagulopathy: bone flap decision, duraplasty size, drain/EVD need, hemostatic adjuncts, and ICU handoff should be decided early.",
            "Postop failure modes are predictable: expanding hematoma, malignant edema, seizure, infection, CSF leak, venous sinus injury, and missed associated spine/vascular injury.",
        ]
    if "csf" in cat:
        return "Chief-Level Case Review", [
            "Trajectory and hardware choice should follow the failure mode: obstruction, infection, overdrainage, loculation, slit ventricle, distal failure, or wrong pressure setting.",
            "Document the system: entry point, catheter target/depth, valve type and setting, distal site, antibiotic-impregnated hardware, and what imaging confirms placement.",
            "Rescue plan is practical: poor CSF return, bloody CSF, malposition, distal access failure, abdominal/pleural complication, or inability to safely pass the catheter.",
            "Postop orders must be unambiguous: drain height/rate/max output, valve setting, clamp parameters, imaging, antibiotics, ICP/neuro checks, and overdrainage precautions.",
        ]
    if "endovascular" in cat:
        return "Chief-Level Case Review", [
            "Access is part of the operation: arch anatomy, femoral/radial choice, sheath size, closure device, bailout access, and anticoagulation should be settled before device deployment.",
            "Keep the bailout tools ready: aspiration, balloon, stent, antiplatelet rescue, vasodilators, reversal strategy, and neurosurgical backup when hemorrhage risk is real.",
            "Device success is physiologic, not just angiographic: distal territory perfusion, branch patency, embolic risk, contrast load, ACT, and BP targets all matter.",
            "Postop orders should name the risk: access-site bleed, reperfusion injury, reocclusion, antithrombotic timing, neuro-check cadence, and repeat CTA/DSA/MRI timing.",
        ]
    if "spine" in cat:
        return "Chief-Level Case Review", [
            "Localize twice and instrument once: numbering, transitional anatomy, prior hardware, rib count, navigation dataset, and fluoroscopic level confirmation are mandatory.",
            "Positioning is treatment: table choice, abdomen-free prone setup, alignment goals, shoulders/hips, eyes/plexus pressure, neuromonitoring baselines, and fluoroscopic access all change the case.",
            "Protect neural elements by sequence: decompression before correction when needed, MAP support for cord risk, no long paralytic with MEPs, and immediate response to signal change.",
            "Finish with construct logic: decompression adequacy, screw purchase, alignment, fusion bed/graft, drain plan, brace/activity orders, postop CT/X-rays, and DVT timing.",
        ]
    if "functional" in cat:
        return "Chief-Level Case Review", [
            "Define the symptom physiology: target circuit or offending vessel/nerve must match the history, exam, imaging, and intraoperative monitoring plan.",
            "Small errors matter: trajectory, lead/contact position, arachnoid dissection, cranial-nerve handling, or mapping threshold can be the difference between success and morbidity.",
            "Have a stop rule: unacceptable mapping response, BAER/MEP/SSEP change, hemorrhage, CSF loss, poor target confidence, or patient intolerance should trigger a defined pivot.",
            "Postop success requires programming/follow-up details: neurologic exam, imaging, medication adjustment, device restrictions, wound care, and symptom-specific outcome tracking.",
        ]
    if "biopsy" in cat or "radiosurgery" in cat:
        return "Chief-Level Case Review", [
            "The target must answer the question: choose tissue/trajectory/dose based on diagnostic yield, molecular testing, treatment impact, and safest corridor.",
            "Risk lives along the path: vessels, sulci, ventricles, necrotic center, eloquent tracts, prior radiation, and anticoagulation decide whether the plan is acceptable.",
            "Confirm before committing: frame/robot registration, coordinates, fiducials, trajectory collision, specimen adequacy, and postop scan threshold should be explicit.",
            "Postop plan should anticipate the rare catastrophe: hemorrhage, edema, seizure, steroid need, neurologic checks, pathology handoff, and treatment-board timing.",
        ]
    if "peripheral" in cat:
        return "Chief-Level Case Review", [
            "Localization is everything: symptoms, exam, Tinel point, EMG/NCS, ultrasound/MRI, and provocative maneuvers must agree before incision.",
            "Protect fascicles and blood supply: internal neurolysis, tumor shelling, graft/transfer decisions, tourniquet time, and stimulation thresholds should be deliberate.",
            "Know when not to chase: dense scarring, malignant features, unclear fascicular anatomy, or unexpected motor fascicle involvement may justify biopsy, subtotal resection, or staged reconstruction.",
            "Postop orders should preserve the repair: splint/immobilization interval, therapy timing, sensory protection, pain plan, and expected recovery timeline.",
        ]
    if "pediatric" in cat:
        return "Chief-Level Case Review", [
            "The setup is age-specific: blood volume, warming, positioning pressure, airway, latex risk, family counseling, and ICU/PICU handoff differ from adults.",
            "Preserve future options: growth, shunt dependence, cranioplasty/bone healing, endocrine/neurocognitive trajectory, and adjuvant therapy influence today’s choices.",
            "Have a complication script: blood loss, CSF leak, hydrocephalus, wound breakdown, posterior fossa mutism, infection, and airway/swallow risk should be anticipated.",
            "Postop communication matters: family expectations, neurologic baseline, therapy needs, school/developmental supports, and surveillance imaging/labs should be clear.",
        ]
    return "Chief-Level Case Review", [
        "State the decision that changes management: why this operation, why this timing, why this approach, and what finding would change the plan.",
        "Know the anatomy that can hurt the patient: named vessels, nerves, tracts, venous drainage, hardware landmarks, and closure-critical tissues.",
        "Prepare the bailout before it is needed: exposure extension, hemostasis, monitoring change, wrong-level/wrong-target concern, and conversion strategy.",
        "Translate the operation into orders: focused exam, BP/MAP, imaging, drains/devices, steroids/antibiotics/antithrombotics, activity, and follow-up.",
    ]


def section(path: Path, text: str) -> str:
    title = title_without_prefix(frontmatter_value(text, "title") or path.stem)
    heading, bullets = profile(path, frontmatter_value(text, "category"))
    rendered = "\n".join(f"- **{label}:** {body}" for label, body in [
        ("Decision point", bullets[0]),
        ("Technical lever", bullets[1]),
        ("Bailout", bullets[2]),
        ("Postop watch", bullets[3]),
    ])
    return f"""{BEGIN}

## {heading}

Use these as the senior-level mental model for **{title}**:

{rendered}

{END}"""


def insert_section(path: Path, text: str) -> str:
    text = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n*", "", text, flags=re.S).rstrip() + "\n"
    block = section(path, text)
    anchors = ["\n<!-- BEGIN COMMON PIMP QUESTIONS -->", "\n<!-- BEGIN ATTENDING PREFERENCE VARIABLES -->", "\n## References"]
    positions = [text.find(a) for a in anchors if text.find(a) != -1]
    pos = min(positions) if positions else -1
    if pos == -1:
        return text.rstrip() + "\n\n" + block + "\n"
    return text[:pos].rstrip() + "\n\n" + block + "\n" + text[pos:]


def main() -> None:
    changed = 0
    for path in guide_paths():
        old = path.read_text(encoding="utf-8")
        new = insert_section(path, old)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"Updated {changed} guides.")


if __name__ == "__main__":
    main()
