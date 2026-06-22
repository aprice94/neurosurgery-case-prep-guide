# Reference: Brain Biopsy Systems and Stereotactic Platforms

A comparison reference for choosing a brain biopsy technique and platform. See individual procedure files for framed, frameless, robotic, and open biopsy.

---

## 1. When to Biopsy (Indications)
- Diagnosis of a lesion that is **not safely or beneficially resectable**, or where tissue diagnosis changes management:
  - Deep/eloquent lesions (basal ganglia, thalamus, brainstem, pineal)
  - Multifocal disease, suspected **CNS lymphoma** (do NOT give steroids before biopsy if lymphoma suspected — can vanish/obscure diagnosis), infection vs tumor
  - Suspected high-grade glioma in non-resectable location
  - Immunocompromised (toxoplasmosis vs lymphoma), unclear etiology
- **Open biopsy** when a larger sample, decompression, or accessible superficial lesion makes open approach preferable

---

## 2. Stereotactic Platforms (Closed/Needle Biopsy)

### A. Frame-Based Stereotaxy
- **Systems:** Leksell (Elekta), CRW (Cosman-Roberts-Wells, Integra), ZD
- **Method:** rigid stereotactic frame fixed to skull → stereotactic CT/MRI → arc/coordinate system (x, y, z + arc/ring angles) directs the needle to target
- **Pros:** highest accuracy and rigidity (sub-millimeter), gold standard for deep/small targets, no reliance on intraoperative registration drift
- **Cons:** frame application (uncomfortable, awake placement), less flexible trajectory planning, separate imaging step, cumbersome for multiple targets
- See [stereotactic-brain-biopsy-framed](stereotactic-brain-biopsy-framed.md)

### B. Frameless Stereotaxy (Navigation-Based)
- **Systems:** Medtronic StealthStation, Brainlab (with skull fiducials or surface/mask registration), VarioGuide, navigation + biopsy needle guide/arm
- **Method:** preop thin-cut MRI/CT → intraoperative registration (fiducials/surface) → navigated trajectory with an aiming device/arm; needle passed along the planned trajectory
- **Pros:** no frame (more comfortable, often GA), flexible planning, integrates with image guidance, good for convexity/lobar targets
- **Cons:** registration error/brain shift, slightly less rigid than frame for very deep small targets (mitigated by skull-mounted devices)
- See [stereotactic-brain-biopsy-frameless](stereotactic-brain-biopsy-frameless.md)

### C. Robot-Assisted Stereotaxy
- **Systems:** **ROSA (Zimmer Biomet), Mazor Renaissance/X, Neuromate, iSYS, Cirq (Brainlab)**
- **Method:** robotic arm aligns to the planned trajectory after registration (frame/frameless/skull fiducials/surface/intraop CT like O-arm); rigid robotic guide for needle
- **Pros:** highly accurate and efficient, **ideal for multiple trajectories** (SEEG, multiple biopsy targets), reproducible, fast for many electrodes/passes
- **Cons:** capital cost, setup/registration, learning curve
- See [robotic-brain-biopsy](robotic-brain-biopsy.md)

### D. Intraoperative MRI-Guided (e.g., ClearPoint)
- Real-time MRI-guided trajectory (also used for laser ablation/DBS); near-real-time confirmation, no brain-shift error

---

## 3. Biopsy Needle Types
- **Sedan side-cutting cannula** (most common) — aspiration side-cutting needle; samples along the trajectory
- **Nashold**, **Backlund** needles
- Technique: take **serial specimens at staged depths** (e.g., every few mm through the target), and from multiple radial directions if needed; **frozen section / smear confirmation** that diagnostic tissue is obtained before finishing

---

## 4. Platform Selection Summary
| Scenario | Preferred |
|----------|-----------|
| Deep, small, single target (thalamus, brainstem, pineal) | Frame-based or robotic |
| Lobar/convexity target, want GA & comfort | Frameless navigation |
| Multiple targets / combined with SEEG | Robotic |
| Real-time confirmation, ablation combo | iMRI (ClearPoint) |
| Need larger sample / accessible lesion / decompression | Open biopsy |

---

## 5. Universal Safety Principles (All Biopsy Techniques)
1. **Plan an avascular trajectory** — review MRI/CTA/contrast; avoid sulci, vessels, ventricles (unless intended), eloquent cortex
2. **Target the enhancing/representative portion** (avoid central necrosis — non-diagnostic); for ring-enhancing lesions sample the enhancing rim
3. **Correct coagulopathy**, stop antiplatelets/anticoagulants (hemorrhage is the principal risk, ~1-3% symptomatic)
4. **If lymphoma suspected — avoid steroids pre-biopsy** if clinically safe (can render tissue non-diagnostic)
5. **Frozen section / intraoperative smear** to confirm diagnostic (not just necrotic/gliotic) tissue before concluding
6. **Hemostasis** — observe the tract; post-biopsy bleeding from the cannula → irrigate, wait, re-image if concern
7. **Postop CT** to exclude hemorrhage
