# ElderScreen: 3-Minute Live Demonstration Script

**Target Audience:** Healthcare Innovators, Clinical Officers, Hackathon Judges, and Community Health Workers (ASHA/ANM).  
**Time Limit:** 180 seconds (3:00)

---

### [0:00 - 0:30] Scene 1: The Problem & The Senior Persona
- **Presenter Action:** Open the ElderScreen web application on mobile viewport (or simulated mobile browser).
- **Spoken Narrative:**
  > *"Meet Ramesh-ji, a 70-year-old living in a Tier-3 town in Uttar Pradesh. His family noticed he's been unusually fatigued and skipping his morning walks. But getting Ramesh-ji to an overburdened district hospital takes a full day of travel and 500 rupees in bus fares. So they wait. Too often, waiting turns treatable conditions like severe jaundice, chronic anemia, or sudden mini-strokes into life-threatening emergencies. 
  > This is **ElderScreen** — an accessible, multimodal early screening aid built from the ground up for Indian seniors."*

---

### [0:30 - 1:00] Scene 2: High Accessibility, Zero Friction Sign-In
- **Presenter Action:** 
  1. Highlight the persistent amber disclaimer banner: *"Screening aid only. Not a medical diagnosis."*
  2. Click the language toggle: switch seamlessly between **English** and **हिंदी (Hindi)**.
  3. Toggle the **"A+"** button to show high-contrast, enlarged senior font sizing.
  4. Tap the **"Quick Demo Profile"** button (Ramesh Kumar Sharma, 70y) to sign in instantly with zero password friction.
- **Spoken Narrative:**
  > *"ElderScreen works on cheap Android smartphones over patchy 3G/4G networks. Seniors don't remember passwords or complex multi-step forms. With one tap, Ramesh-ji is authenticated. The interface speaks both English and Hindi, with 48px touch targets and high-contrast typography."*

---

### [1:00 - 1:45] Scene 3: Multimodal Capture & Voice Input
- **Presenter Action:**
  1. Click **"🟡 2. Jaundice & Pallor (Medium Risk)"** preset (or upload face & eye photo directly).
  2. Point out the live photo previews of the face and macro eye conjunctiva.
  3. Click the **Microphone** icon (Web Speech API) and speak symptoms: *"3 din se bahut kamzori lag rahi hai aur peshab peela aa raha hai."* (Notice real-time speech-to-text transcript).
  4. Click **"Run Screening Check / जांच रिपोर्ट तैयार करें"**.
- **Spoken Narrative:**
  > *"ElderScreen combines visual biomarker analysis with natural voice symptoms. Seniors don't need to type — they tap the microphone and speak in Hindi or English using browser-native Web Speech API. 
  > When we tap 'Run Screening', classical computer vision analyzes palpebral conjunctiva redness in CIELAB space for anemia, segments the sclera to detect yellow chromatic shifts for jaundice, and calculates bilateral cranial asymmetry for stroke detection."*

---

### [1:45 - 2:25] Scene 4: The Result — Safe, Guardrailed, and Bilingual
- **Presenter Action:**
  1. Result appears in **under 1 second**!
  2. Display the **Medium Risk Warning Badge** (Amber).
  3. Click **"Read Out Loud (Listen) / रिपोर्ट बोलकर सुनें"** to play the Web Speech synthesis reading the patient summary out loud in Hindi/English.
  4. Review the Visual Cue breakdown cards:
     - *Pallor score: 58%*
     - *Scleral Yellowing: 68%*
     - *Facial Asymmetry: 11% (Normal)*
  5. Show the clinical Next Steps checklist (e.g., PHC visit within 48 hours, basic CBC and LFT tests).
- **Spoken Narrative:**
  > *"In under 1 second — well beneath our 15-second benchmark — Ramesh-ji receives a kind, 8th-grade plain language explanation. If Ramesh-ji cannot read, he taps the speaker button and the phone reads the report out loud. 
  > Notice our medical safety guardrails: the AI **never** claims a definitive diagnosis; it explicitly indicates 'possible signs of' and guides him to standard Primary Health Center diagnostic tests."*

---

### [2:25 - 2:45] Scene 5: Emergency Escalation (The FAST Stroke Trigger)
- **Presenter Action:**
  1. Quickly tap **"🔴 3. Facial Droop / Stroke Signs"** preset and submit.
  2. The UI immediately transforms into an **Urgent Red Emergency Alert**.
  3. An animated **"CALL 108 / 112 EMERGENCY NOW"** button appears prominently at the top.
- **Spoken Narrative:**
  > *"When an acute danger is detected — like unilateral facial droop with asymmetric nasolabial crease — ElderScreen immediately escalates to Red Flag protocol. The app provides a 1-tap direct dial to 108/112 ambulance dispatch and urges family members not to administer oral fluids."*

---

### [2:45 - 3:00] Scene 6: The Caregiver & Doctor Hand-off
- **Presenter Action:**
  1. Click **"Share with Caregiver or Doctor"**.
  2. Display the structured clinical summary with FAST protocol status, differential diagnostic risk, and recommended labs (CBC, LFT, non-contrast CT).
  3. Click **"Share on WhatsApp"** and copy shareable web link.
- **Spoken Narrative:**
  > *"ElderScreen bridges the gap between home and clinic. With one click, the caregiver sends a structured clinical briefing to the family doctor or ASHA worker via WhatsApp. ElderScreen is early detection where India needs it most: in the hands of our seniors."*
