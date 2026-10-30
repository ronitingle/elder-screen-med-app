# ElderScreen API & Data Contracts

**Version:** 1.0.0  
**Disclaimer:** *Screening aid only. Not a medical diagnosis.*

---

## 1. Vision Analysis API Contract

- **Endpoint:** `POST /analyze`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `face_image`: File (JPEG / PNG / WebP) - Frontal face photograph.
  - `eye_image`: File (JPEG / PNG / WebP) - Close-up eye / sclera / conjunctiva photo.

### Response Schema (`application/json`)
```json
{
  "pallor": {
    "score": 0.35,
    "confidence": 0.88,
    "details": "Mild paleness detected in palpebral conjunctiva/sub-ocular region."
  },
  "facial_asymmetry": {
    "score": 0.12,
    "confidence": 0.91,
    "details": "Bilateral symmetry within normal physiological tolerance."
  },
  "scleral_yellowing": {
    "score": 0.68,
    "confidence": 0.85,
    "details": "Elevated b* channel yellowness detected across segmented sclera."
  },
  "quality_flags": [
    "adequate_lighting",
    "face_centered"
  ]
}
```

### Potential `quality_flags`
- `adequate_lighting` / `low_lighting` / `overexposed`
- `sharp_focus` / `blur_detected`
- `face_detected` / `no_face_found` / `multiple_faces_found`
- `eye_detected` / `sclera_occluded`

---

## 2. LLM Risk Fusion & Summarization API Contract

- **Endpoint:** `POST /summarize`
- **Content-Type:** `application/json`
- **Request Body:**
```json
{
  "vision_result": {
    "pallor": { "score": 0.35, "confidence": 0.88 },
    "facial_asymmetry": { "score": 0.12, "confidence": 0.91 },
    "scleral_yellowing": { "score": 0.68, "confidence": 0.85 },
    "quality_flags": ["adequate_lighting", "face_centered"]
  },
  "symptoms_text": "Feeling very weak for 3 days and dark urine. Eyes look a bit yellowish.",
  "age": 68,
  "lang": "en" 
}
```
*Note: `lang` can be `"en"` (English) or `"hi"` (Hindi).*

### Response Schema (`application/json`)
```json
{
  "risk_level": "medium",
  "urgency": "scheduled_clinic_visit",
  "reasons": [
    "Elevated scleral yellowness score (0.68) consistent with reported dark urine.",
    "Mild pallor indicators detected alongside reports of general weakness."
  ],
  "patient_summary": "We noticed possible signs of mild yellowing in the eye and mild tiredness. This is NOT a medical diagnosis. Please consult a community doctor or primary health center (PHC) this week for basic blood tests.",
  "clinical_summary": "PATIENT SCREENING RECORD (Age: 68):\n- Clinical presentation: Scleral icterus indicators (score 0.68), mild sub-ocular pallor (0.35).\n- Patient-reported symptoms: 3-day asthenia, choluria.\n- Provisional differential risk: Possible hyperbilirubinemia / hepatic or hemolytic etiology; secondary mild anemia screening flag.\n- Red flag status: No acute facial droop or dysarthria noted.\n- Recommended workup: LFTs, Total/Direct Bilirubin, CBC with peripheral smear, urine analysis.",
  "next_steps": [
    "Visit your nearest Primary Health Center (PHC) or family physician within 48-72 hours.",
    "Stay hydrated and avoid unprescribed over-the-counter painkillers or herbal concoctions.",
    "If you experience sudden severe abdominal pain, high fever, or vomiting, go to emergency care immediately."
  ],
  "emergency_warning": null
}
```

---

## 3. Supabase Schema & Database Contract

### Table: `profiles`
- `id`: `uuid primary key references auth.users(id) on delete cascade`
- `full_name`: `text`
- `phone`: `text`
- `age`: `integer`
- `preferred_lang`: `text default 'en'`
- `created_at`: `timestamp with time zone default now()`

### Table: `caregivers`
- `id`: `uuid primary key default gen_random_uuid()`
- `patient_id`: `uuid references profiles(id) on delete cascade`
- `caregiver_phone`: `text`
- `caregiver_name`: `text`
- `relationship`: `text`
- `created_at`: `timestamp with time zone default now()`

### Table: `screenings`
- `id`: `uuid primary key default gen_random_uuid()`
- `user_id`: `uuid references profiles(id) on delete cascade`
- `face_image_url`: `text`
- `eye_image_url`: `text`
- `symptoms`: `text`
- `vision_json`: `jsonb`
- `result_json`: `jsonb`
- `created_at`: `timestamp with time zone default now()`

### Storage Buckets
- Bucket `screening-images`: Public/authenticated upload policy for face and eye scans.

---

## 4. Canonical Mock Responses for Parallel Development

### Mock A: Low Risk (Normal Senior Check)
```json
{
  "vision_result": {
    "pallor": { "score": 0.15, "confidence": 0.89, "details": "Normal vascular coloration." },
    "facial_asymmetry": { "score": 0.08, "confidence": 0.94, "details": "Symmetric landmarks." },
    "scleral_yellowing": { "score": 0.12, "confidence": 0.87, "details": "Clean sclera tone." },
    "quality_flags": ["adequate_lighting", "sharp_focus"]
  },
  "summary_result": {
    "risk_level": "low",
    "urgency": "routine",
    "reasons": ["All visual cues within typical range. No acute red flag symptoms reported."],
    "patient_summary": "Your photo screening looks steady and normal today. There are no sudden signs of paleness, jaundice, or weakness detected. Remember to drink water and take your daily routine walks. This is a screening aid only, not a medical diagnosis.",
    "clinical_summary": "SCREENING NORMAL: Normal cranial symmetry, baseline conjunctival perfusion, clear sclera. No acute distress reported. Advise routine annual geriatric wellness checkup.",
    "next_steps": [
      "Maintain regular healthy diet and blood pressure monitoring.",
      "Repeat screening in 3 months or if any new symptoms arise."
    ],
    "emergency_warning": null
  }
}
```

### Mock B: Medium Risk (Jaundice / Anemia Suspected)
```json
{
  "vision_result": {
    "pallor": { "score": 0.58, "confidence": 0.86, "details": "Moderate conjunctival pallor detected." },
    "facial_asymmetry": { "score": 0.10, "confidence": 0.92, "details": "No significant asymmetry." },
    "scleral_yellowing": { "score": 0.65, "confidence": 0.84, "details": "Moderate scleral yellow cast." },
    "quality_flags": ["adequate_lighting"]
  },
  "summary_result": {
    "risk_level": "medium",
    "urgency": "scheduled_clinic_visit",
    "reasons": [
      "Significant conjunctival pallor (score 0.58) indicates possible anemia.",
      "Elevated scleral yellowness (score 0.65) suggests possible mild jaundice."
    ],
    "patient_summary": "We noticed possible signs of tiredness/paleness and yellowing around the eyes. Please do not worry, but do see a local doctor at the health center within 2 to 3 days to get basic blood tests done. Screening aid only, not a medical diagnosis.",
    "clinical_summary": "SCREENING ABNORMAL (MEDIUM): Scleral yellow cast (0.65) + conjunctival pallor (0.58). Differential includes nutritional anemia vs hepatic strain. Advised: CBC, Total Bilirubin, SGOT/SGPT, Urine urobilinogen.",
    "next_steps": [
      "Consult primary care doctor or ASHA/ANM worker in next 48 hours.",
      "Bring this digital screening report to the clinic.",
      "Avoid heavy physical exertion until checked."
    ],
    "emergency_warning": null
  }
}
```

### Mock C: High Risk / Red Flag (Acute Asymmetry / Stroke Signs)
```json
{
  "vision_result": {
    "pallor": { "score": 0.22, "confidence": 0.80, "details": "Normal tone." },
    "facial_asymmetry": { "score": 0.78, "confidence": 0.95, "details": "Marked unilateral nasolabial droop and left eyelid lag." },
    "scleral_yellowing": { "score": 0.14, "confidence": 0.85, "details": "Normal sclera." },
    "quality_flags": ["adequate_lighting"]
  },
  "summary_result": {
    "risk_level": "high",
    "urgency": "immediate_emergency",
    "reasons": [
      "Severe facial movement asymmetry (score 0.78) with unilateral facial droop.",
      "Symptom text describes acute weakness or speech difficulty."
    ],
    "patient_summary": "URGENT ATTENTION NEEDED: We noticed possible signs of facial drooping on one side. This could be a sign of a neurological condition such as a stroke. PLEASE SEEK EMERGENCY MEDICAL CARE AT THE NEAREST HOSPITAL IMMEDIATELY. Call 108 or 112 right now. Screening aid only, not a medical diagnosis.",
    "clinical_summary": "ACUTE HIGH RISK ALERT: High unilateral facial asymmetry index (0.78). Acute focal neurological deficit (stroke / Bell's palsy rule-out required). FAST protocol triggered. Immediate CT scan and urgent medical evaluation indicated.",
    "next_steps": [
      "CALL EMERGENCY SERVICES (108/112) OR VISIT HOSPITAL CASUALTY IMMEDIATELY.",
      "Do NOT administer food, water, or aspirin until evaluated by a physician.",
      "Note the exact time symptoms started to inform hospital doctors."
    ],
    "emergency_warning": "HIGH RISK EMERGENCY: Possible acute stroke or nerve injury signs detected. Seek immediate hospital care."
  }
}
```
