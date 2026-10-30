# 🩺 ElderScreen (एल्डरस्क्रीन)

> **Multimodal Early Health-Screening Aid for Indian Seniors (50+) in Tier-2/3 Towns**  
> *Screening aid only. Not a medical diagnosis.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![React 19](https://img.shields.io/badge/React-19.0-teal.svg)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Vite](https://img.shields.io/badge/Vite-8.3-646CFF.svg)](https://vitejs.dev)

ElderScreen is an accessible, mobile-first progressive web application engineered for low-cost Android phones in Indian Tier-2/3 towns and rural communities. Seniors or frontline ASHA workers upload a frontal face photograph and an eye close-up, and dictate or type symptoms in **Hindi** or **English**. In **under 1 second**, the app delivers an explainable risk stratification with a plain-language summary for the senior and a structured clinical briefing for doctors and caregivers.

---

## ⚡ 3-Command Setup

Get the entire ElderScreen monorepo running locally in 3 commands:

```bash
# 1. Clone repository and navigate
git clone https://github.com/your-org/elderscreen.git && cd elderscreen

# 2. Install dependencies (Python + Node.js)
pip install -r vision/requirements.txt -r llm/requirements.txt -r supabase/requirements.txt && cd web && npm install && cd ..

# 3. Launch all services (Vision, LLM, Backend Orchestrator, Web Frontend)
./start_all.sh
```

Open your browser at **`http://localhost:5173`** to start screening!

---

## 🔬 Visual Cues Detected

| Visual Cue | Clinical Target | Computer Vision Method |
| :--- | :--- | :--- |
| **Pallor** | Possible **Anaemia** / Microvascular Hypoperfusion | CIELAB $a^*$ (vascular erythema) & HSV saturation analysis across palpebral conjunctiva and facial mucosal ROIs. |
| **Scleral Yellowing** | Possible **Jaundice** / Hepatic Strain / Hyperbilirubinemia | Sclera colorimetric segmentation measuring chromatic yellow shift ($b^*$ channel in CIELAB). |
| **Facial Movement Asymmetry** | Possible **Stroke (CVA)** / Bell's Palsy / Facial Nerve Paresis | Bilateral cranial landmark comparison, nasolabial crease variance, and eye level deviation. |

---

## 🛡️ Medical Safety & Guardrails

1. **Mandatory Disclaimer:** Every screen, report, and export displays:  
   *"Screening aid only. Not a medical diagnosis. | यह केवल प्रारंभिक जांच है, डॉक्टरी निदान नहीं।"*
2. **Non-Definitive Phrasing:** The AI never proclaims a disease diagnosis (e.g. *"You have jaundice"* is strictly banned; framed as *"Possible screening signs of mild yellowness in the eyes"*).
3. **Emergency Escalation (FAST Protocol):** When acute cranial asymmetry ($\ge 0.60$) or stroke-related symptoms (unilateral droop, slurred speech) are detected:
   - Risk level escalates to **HIGH EMERGENCY**.
   - Immediate **108 / 112 ambulance call button** is rendered with urgent audio alerts.
   - Caregivers are warned not to administer oral food or water.
4. **Senior-Friendly Accessibility:**
   - 48px+ touch targets and high-contrast color scheme.
   - One-tap **"A+"** font enlargement.
   - Native **English + Hindi** toggle across all workflows.
   - **Web Speech API** voice recognition for typing-free symptom entry.
   - **Text-to-Speech** audio readout for illiterate or low-vision seniors.

---

## 📁 Monorepo Structure

```
elderscreen/
├── web/                  # Agent A: React + Vite + Tailwind v4 (mobile-first senior UI)
│   ├── src/components/   # Header, DisclaimerBanner, Login, NewScreening, Result, Caregiver, History
│   ├── src/translations.js # English & Hindi bilingual dictionaries
│   └── src/api.js        # API client & embedded canonical mock fallbacks
├── supabase/             # Agent B: Schema, migrations, RLS policies, and Orchestrator API
│   ├── schema.sql        # PostgreSQL tables (profiles, caregivers, screenings) & RLS policies
│   ├── orchestrator.py   # FastAPI upload -> analyze -> summarize -> save pipeline (Port 8000)
│   └── test_orchestrator.py # Backend test suite
├── vision/               # Agent C: Classical CV service (FastAPI, Port 8001)
│   ├── analyzer.py       # Pallor, Sclera yellowing, Asymmetry, and Quality Flags
│   ├── generate_samples.py # Synthetic clinical sample generator
│   └── test_vision.py    # Unit & smoke tests
├── llm/                  # Agent D: Explainable risk fusion & guardrailed summarization (Port 8002)
│   ├── fusion.py         # Weighted rule scoring, bilingual templates, and Gemini API bridge
│   └── test_llm.py       # Fusion and safety guardrail tests
├── docs/                 # Agent E: Documentation, contracts, demo scripts, pitch deck
│   ├── contracts.md      # API & Data contracts with canonical mocks
│   ├── e2e_smoke_test.py # End-to-end integration and latency benchmark test suite
│   ├── demo_script.md    # 3-minute live demonstration script
│   └── pitch_deck.md     # 5-slide pitch presentation
├── start_all.sh          # One-command local runner for all services
└── .env.example          # Environment variable template
```

---

## 🧪 Automated Testing & Smoke Verification

Run the test suite across all modules:

```bash
# 1. Vision Service Smoke Tests
python vision/test_vision.py

# 2. LLM & Fusion Guardrail Tests
python llm/test_llm.py

# 3. Supabase Orchestrator Tests
python supabase/test_orchestrator.py

# 4. End-to-End Integration & Latency Benchmark (<15s requirement)
python docs/e2e_smoke_test.py
```

### Verified Benchmark Output
```
[Benchmark] Full E2E screening elapsed time: 0.302 seconds (Constraint: < 15.0s)
Ran 6 tests in 0.376s: OK
```

---

## 🚀 Live Demo Quick Presets

Don't have clinical photos on hand? ElderScreen includes 1-click presets in the UI:
1. **Healthy Senior (Low Risk):** Normal symmetry, clean sclera, baseline vitality.
2. **Jaundice & Pallor (Medium Risk):** Elevated sclera yellowness (0.68) + conjunctival pallor (0.58), dark urine symptoms.
3. **Facial Droop / Stroke Signs (High Risk):** Unilateral nasolabial droop (0.78 asymmetry index), triggers immediate FAST emergency response.

---

## 👥 Caregiver & Doctor Handoff

- **WhatsApp Share:** 1-tap instant WhatsApp link dispatch to adult children or family physicians.
- **Structured Clinical Briefing:** Provides PHC Medical Officers with quantified biomarker indices, differential considerations, and recommended laboratory workups (CBC with peripheral smear, Total/Direct Bilirubin, AST/ALT, non-contrast CT).
