"""
ElderScreen LLM & Risk Fusion Engine
Performs explainable multimodal fusion:
- Vision scores (asymmetry, scleral yellowing, pallor)
- Symptom text NLP keyword analysis with positive wellness sentiment awareness
- Quality flags adjustment (low light, unlocalized face)
- Guardrailed clinical & patient summarization in English & Hindi
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
import requests

# Positive wellness keywords indicating patient feels healthy
WELLNESS_KEYWORDS = [
    "good", "very good", "feeling good", "fine", "healthy", "fit", "no problem",
    "no issues", "great", "well", "all good", "theek", "theek hu", "swasth", "badhiya",
    "बहुत अच्छा", "ठीक हूँ", "स्वस्थ", "कोई परेशानी नहीं"
]

# Red flag emergency keywords across English and colloquial Hindi
EMERGENCY_KEYWORDS = [
    "stroke", "droop", "drooping", "slur", "slurred", "paralysis",
    "sudden numbness", "chest pain", "unconscious", "cannot speak", "cannot move",
    "tedha", "paralysed", "hath sunn", "muh tedha", "bol nahi pa rahe", "lakwa",
    "लकवा", "टेढ़ा", "बेहोश", "बोलने में दिक्कत"
]

JAUNDICE_KEYWORDS = [
    "yellow", "jaundice", "dark urine", "pale stool", "itching", "loss of appetite",
    "peela", "peeliya", "peshab peela", "anokha peela", "bhookh na lagna", "पीलिया", "पीला"
]

ANEMIA_KEYWORDS = [
    "pale", "fatigue", "tired", "weakness", "dizziness", "fainting", "breathless",
    "chakkar", "kamzori", "thakan", "kamzor", "khoon ki kami", "कमजोरी", "थकान", "चक्कर"
]


class RiskFusionEngine:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

    def calculate_risk(
        self,
        vision_result: Dict[str, Any],
        symptoms_text: str,
        age: int
    ) -> Dict[str, Any]:
        """
        Calculates explainable risk level and triggers.
        Returns: { risk_level, urgency, weighted_score, reasons, red_flags, emergency_warning }
        """
        pallor = vision_result.get("pallor", {}).get("score", 0.0)
        asymmetry = vision_result.get("facial_asymmetry", {}).get("score", 0.0)
        yellowing = vision_result.get("scleral_yellowing", {}).get("score", 0.0)
        quality_flags = vision_result.get("quality_flags", [])

        symptoms_lower = (symptoms_text or "").lower()

        reasons = []
        red_flags = []

        # Check keyword sentiments
        has_emergency_sym = any(k in symptoms_lower for k in EMERGENCY_KEYWORDS)
        has_jaundice_sym = any(k in symptoms_lower for k in JAUNDICE_KEYWORDS)
        has_anemia_sym = any(k in symptoms_lower for k in ANEMIA_KEYWORDS)
        has_wellness_sym = any(k in symptoms_lower for k in WELLNESS_KEYWORDS) and not (has_emergency_sym or has_jaundice_sym or has_anemia_sym)

        # Quality adjustments
        has_low_light = "low_lighting" in quality_flags or "overexposed" in quality_flags
        has_no_face = "no_face_found" in quality_flags

        # 1. Asymmetry check (Stroke / Bell's Palsy)
        if asymmetry >= 0.60:
            red_flags.append(f"Elevated facial movement asymmetry ({asymmetry:.2f}) indicates possible unilateral cranial nerve deficit or stroke signs.")
            reasons.append(f"Marked facial asymmetry detected (score: {asymmetry:.2f}).")
        elif asymmetry >= 0.40 and not has_no_face:
            reasons.append(f"Mild facial asymmetry observed (score: {asymmetry:.2f}).")

        # 2. Scleral yellowing (Jaundice / Hepatic)
        if yellowing >= 0.52:
            reasons.append(f"Scleral yellow chromatic shift detected (score: {yellowing:.2f}) suggesting possible icterus.")
        elif yellowing >= 0.35 and not has_low_light:
            reasons.append(f"Slight yellow hue detected in scleral region (score: {yellowing:.2f}).")

        # 3. Pallor (Anemia) - only elevate if lighting is adequate and face/mucosa is localized
        if pallor >= 0.52 and not (has_low_light or has_no_face):
            reasons.append(f"Elevated sub-ocular / conjunctival pallor detected (score: {pallor:.2f}) suggesting possible anemia.")
        elif pallor >= 0.38 and not (has_low_light or has_no_face):
            reasons.append(f"Borderline paleness noted (score: {pallor:.2f}).")

        # Symptom correlations
        if has_emergency_sym:
            red_flags.append("Patient-reported acute symptoms (e.g. speech difficulty, unilateral numbness, or sudden droop).")
        if has_jaundice_sym:
            reasons.append("Reported symptoms align with possible hepatic strain or biliary obstruction.")
        if has_anemia_sym:
            reasons.append("Reported weakness or fatigue aligns with potential low hemoglobin / anemia.")

        # Age weighting
        age_factor = 1.05 if age >= 70 else 1.0

        # Weighted calculation
        weighted_score = (
            asymmetry * 0.45 +
            yellowing * 0.30 +
            pallor * 0.25
        ) * age_factor

        weighted_score = round(min(1.0, float(weighted_score)), 2)

        # Risk level determination
        if len(red_flags) > 0 or asymmetry >= 0.60 or has_emergency_sym:
            risk_level = "high"
            urgency = "immediate_emergency"
            emergency_warning = (
                "RED FLAG ALERT: Possible acute neurological or stroke signs detected. "
                "Seek emergency medical evaluation (Dial 108 / 112) immediately."
            )
        elif not has_wellness_sym and (weighted_score >= 0.45 or yellowing >= 0.52 or (pallor >= 0.52 and not has_low_light) or has_jaundice_sym or has_anemia_sym):
            risk_level = "medium"
            urgency = "scheduled_clinic_visit"
            emergency_warning = None
        else:
            risk_level = "low"
            urgency = "routine"
            emergency_warning = None
            if not reasons:
                reasons.append("Visual screening within normal parameters. Patient reports feeling well.")

        return {
            "risk_level": risk_level,
            "urgency": urgency,
            "weighted_score": weighted_score,
            "reasons": reasons,
            "red_flags": red_flags,
            "emergency_warning": emergency_warning
        }

    def generate_summary_prompt(
        self,
        vision_result: Dict[str, Any],
        symptoms_text: str,
        age: int,
        lang: str,
        risk_data: Dict[str, Any]
    ) -> str:
        return f"""You are a specialized medical screening assistant for ElderScreen, a health screening app for elderly Indian citizens.
Screening inputs:
- Patient Age: {age}
- Language: {"Hindi (Devanagari)" if lang == 'hi' else "English"}
- Risk Level: {risk_data['risk_level']} (Urgency: {risk_data['urgency']})
- Vision Findings: Pallor: {vision_result.get('pallor', {}).get('score')}, Asymmetry: {vision_result.get('facial_asymmetry', {}).get('score')}, Scleral Yellowing: {vision_result.get('scleral_yellowing', {}).get('score')}
- Patient Symptoms: "{symptoms_text}"
- Detected Risk Triggers: {", ".join(risk_data['reasons'])}

STRICT GUARDRAILS:
1. NEVER diagnose a disease (do NOT say "You have anemia" or "You have jaundice" or "You had a stroke").
2. ALWAYS say "possible signs of" or "screening indications of".
3. Always include the disclaimer: "Screening aid only. Not a medical diagnosis."
4. If High Risk, emphatically recommend immediate hospital emergency care or dialing 108/112.
5. Patient summary must be in simple, kind 8th-grade language suitable for a senior citizen or village elder.
6. Clinical summary must be concise, professional, structured for a Primary Health Center (PHC) medical officer.

Respond ONLY with valid JSON with these keys:
{{
  "patient_summary": "...",
  "clinical_summary": "...",
  "next_steps": ["step 1", "step 2", "step 3"]
}}"""

    def generate_summary(
        self,
        vision_result: Dict[str, Any],
        symptoms_text: str,
        age: int,
        lang: str = "en"
    ) -> Dict[str, Any]:
        """Generates guardrailed patient & clinical summary."""
        risk_data = self.calculate_risk(vision_result, symptoms_text, age)
        risk_level = risk_data["risk_level"]
        is_hi = (lang == "hi")

        if self.gemini_api_key:
            try:
                llm_output = self._call_gemini_api(vision_result, symptoms_text, age, lang, risk_data)
                if llm_output and "patient_summary" in llm_output:
                    return {
                        "risk_level": risk_level,
                        "urgency": risk_data["urgency"],
                        "reasons": risk_data["reasons"],
                        "patient_summary": llm_output.get("patient_summary"),
                        "clinical_summary": llm_output.get("clinical_summary"),
                        "next_steps": llm_output.get("next_steps", []),
                        "emergency_warning": risk_data["emergency_warning"]
                    }
            except Exception as e:
                print(f"[LLM Warning] Gemini call failed, falling back to rule templates: {e}")

        summary = self._fallback_summary(risk_level, risk_data, symptoms_text, age, is_hi)
        return summary

    def _call_gemini_api(self, vision_result, symptoms_text, age, lang, risk_data) -> Optional[Dict[str, Any]]:
        prompt = self.generate_summary_prompt(vision_result, symptoms_text, age, lang, risk_data)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        res = requests.post(url, json=payload, timeout=8)
        if res.status_code == 200:
            data = res.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw_text)
        return None

    def _fallback_summary(
        self,
        risk_level: str,
        risk_data: Dict[str, Any],
        symptoms_text: str,
        age: int,
        is_hi: bool
    ) -> Dict[str, Any]:
        """Provides verified guardrailed summaries in English and Hindi."""
        reasons = risk_data["reasons"]
        urgency = risk_data["urgency"]
        emergency_warning = risk_data["emergency_warning"]

        if risk_level == "high":
            if is_hi:
                patient_summary = (
                    "अति आवश्यक सूचना: आपके चेहरे या लक्षणों में संभावित कमजोरी अथवा असंतुलन के संकेत दिखाई दे रहे हैं। "
                    "यह किसी गंभीर स्वास्थ्य समस्या (जैसे चेहरे की नस या स्ट्रोक) का संभावित लक्षण हो सकता है। "
                    "कृपया बिना किसी देरी के तुरंत नजदीकी अस्पताल की इमरजेंसी में जाएं या 108 पर कॉल करें। "
                    "यह केवल प्रारंभिक जांच है, डॉक्टरी निदान नहीं।"
                )
                next_steps = [
                    "तुरंत 108 या 112 पर एम्बुलेंस के लिए कॉल करें या नजदीकी अस्पताल जाएं।",
                    "मरीज को अकेला न छोड़ें और डॉक्टर के परीक्षण से पहले कुछ भी खाने-पीने को न दें।",
                    "लक्षण किस समय शुरू हुए, यह समय लिखकर डॉक्टर को बताएं।"
                ]
            else:
                patient_summary = (
                    "URGENT ATTENTION: The screening noticed possible signs of facial drooping or sudden weakness. "
                    "These can be possible warning signs of a neurological event such as a stroke. "
                    "PLEASE SEEK IMMEDIATE EMERGENCY MEDICAL ATTENTION AT THE NEAREST HOSPITAL OR CALL 108/112 RIGHT NOW. "
                    "Screening aid only. Not a medical diagnosis."
                )
                next_steps = [
                    "Call emergency services (108 / 112) or go to the nearest hospital casualty immediately.",
                    "Do not administer oral food, water, or medication until evaluated by a doctor.",
                    "Record the exact time symptoms first appeared for the treating physician."
                ]

            clinical_summary = (
                f"ACUTE EMERGENCY ALERT (Age: {age}):\n"
                f"- High risk findings: {'; '.join(reasons)}.\n"
                f"- Reported symptoms: {symptoms_text or 'Not provided'}.\n"
                f"- Provisional Clinical Flag: High index of suspicion for acute focal neurological deficit / Bell's Palsy / CVA.\n"
                f"- Protocol: Trigger FAST assessment, immediate vitals, urgent neuro consult, and non-contrast CT head."
            )

        elif risk_level == "medium":
            if is_hi:
                patient_summary = (
                    "स्वास्थ्य सूचना: आपकी जांच में आंखों में हल्का पीलापन या शरीर में कमजोरी/खून की कमी के संभावित संकेत दिखे हैं। "
                    "घबराने की कोई बात नहीं है, लेकिन अगले 24 से 48 घंटों में अपने नजदीकी प्राथमिक स्वास्थ्य केंद्र (PHC) या डॉक्टर से मिलकर खून और पेशाब की बुनियादी जांच अवश्य करवा लें। "
                    "यह केवल प्रारंभिक जांच है, डॉक्टरी निदान नहीं।"
                )
                next_steps = [
                    "अगले 1-2 दिनों में अपने नजदीकी सरकारी अस्पताल (PHC/CHC) या पारिवारिक डॉक्टर से मिलें।",
                    "यह रिपोर्ट अपने साथ ले जाएं और डॉक्टर को दिखाएं।",
                    "पर्याप्त पानी पिएं और बिना डॉक्टर की सलाह के कोई भारी दर्द निवारक दवा न लें।"
                ]
            else:
                patient_summary = (
                    "HEALTH NOTICE: The screening noticed possible signs of mild yellowness in the eyes or paleness/tiredness. "
                    "There is no need to panic, but please visit your local Primary Health Center (PHC) or family physician within 24 to 48 hours for standard blood and urine tests. "
                    "Screening aid only. Not a medical diagnosis."
                )
                next_steps = [
                    "Consult your local primary care doctor, ASHA worker, or PHC within 48 hours.",
                    "Carry this digital screening report to show your healthcare provider.",
                    "Stay well hydrated and avoid unprescribed pain relievers or home remedies."
                ]

            clinical_summary = (
                f"SUBACUTE SCREENING ALERT (Age: {age}):\n"
                f"- Visual / clinical flags: {'; '.join(reasons)}.\n"
                f"- Reported symptoms: {symptoms_text or 'Mild malaise/fatigue'}.\n"
                f"- Provisional Risk Differential: Possible mild scleral icterus (hepatobiliary strain) and/or conjunctival pallor (nutritional anemia).\n"
                f"- Recommended Diagnostics: LFTs (Total/Direct Bilirubin, AST/ALT), CBC (Hb, MCV), urine analysis."
            )

        else: # Low risk
            if is_hi:
                patient_summary = (
                    "आपकी स्वास्थ्य जांच सामान्य है: चेहरे और आंखों में किसी भी प्रकार की चिंताजनक समस्या के संकेत नहीं मिले हैं। "
                    "आप स्वस्थ और स्थिर लग रहे हैं। पर्याप्त पानी पीते रहें, समय पर पौष्टिक भोजन लें और अपनी नियमित सैर जारी रखें। "
                    "यह केवल प्रारंभिक जांच है, डॉक्टरी निदान नहीं।"
                )
                next_steps = [
                    "नियमित दिनचर्या, हल्का व्यायाम और संतुलित खानपान जारी रखें।",
                    "समय-समय पर अपना रक्तचाप (BP) और शुगर जांचते रहें।",
                    "यदि कोई नया लक्षण या कमजोरी महसूस हो तो पुनः जांच करें।"
                ]
            else:
                patient_summary = (
                    "SCREENING NORMAL: Your photos and responses look steady and within typical healthy ranges today. "
                    "No sudden signs of paleness, jaundice, or facial drooping were identified. "
                    "Continue drinking plenty of water, eating nutritious meals, and maintaining your daily routine walks. "
                    "Screening aid only. Not a medical diagnosis."
                )
                next_steps = [
                    "Maintain your regular healthy diet, hydration, and daily morning walks.",
                    "Keep up with routine periodic blood pressure and blood sugar checks.",
                    "Repeat this screening if you ever notice fatigue or feeling unwell."
                ]

            clinical_summary = (
                f"GERIATRIC WELLNESS SCREENING (Age: {age}):\n"
                f"- Status: Low risk baseline.\n"
                f"- Visual observations: Perfusion normal, no scleral icterus detected, bilateral facial symmetry maintained.\n"
                f"- Reported symptoms: {symptoms_text or 'None reported'}.\n"
                f"- Clinical Advice: Routine preventative geriatric care and age-appropriate wellness screening."
            )

        return {
            "risk_level": risk_level,
            "urgency": urgency,
            "reasons": reasons,
            "patient_summary": patient_summary,
            "clinical_summary": clinical_summary,
            "next_steps": next_steps,
            "emergency_warning": emergency_warning
        }
