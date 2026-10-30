"""
ElderScreen LLM & Summarization Service (FastAPI)
Conforms to docs/contracts.md: POST /summarize
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from fusion import RiskFusionEngine

app = FastAPI(
    title="ElderScreen LLM & Summarization Service",
    description="Multimodal risk fusion and guardrailed summarization for geriatric screening",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RiskFusionEngine()


class SummarizeRequest(BaseModel):
    vision_result: Dict[str, Any]
    symptoms_text: Optional[str] = ""
    age: Optional[int] = 65
    lang: Optional[str] = "en"


class SummarizeResponse(BaseModel):
    risk_level: str
    urgency: str
    reasons: List[str]
    patient_summary: str
    clinical_summary: str
    next_steps: List[str]
    emergency_warning: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok", "service": "llm", "version": "1.0.0"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    try:
        result = engine.generate_summary(
            vision_result=req.vision_result,
            symptoms_text=req.symptoms_text or "",
            age=req.age or 65,
            lang=req.lang or "en"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fusion / summarization failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
