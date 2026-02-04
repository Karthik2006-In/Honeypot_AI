from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

from scam_detector import detect_scam, classify_scam
from ai_agent import ai_reply
from mock_scammer import mock_scammer_api
from extractor import extract_upi, extract_links, extract_bank_accounts
from config import PERSONAS

# API key to share with evaluators
API_KEY = "hackathon123"

app = FastAPI(title="Agentic HoneyPot API")
@app.get("/")
def root():
    return {
        "status": "API is running",
        "message": "Go to /docs for Swagger UI"
    }

class ScamRequest(BaseModel):
    message: str

@app.post("/agentic-honeypot")
def agentic_honeypot(
    request: ScamRequest,
    x_api_key: Optional[str] = Header(None)
):
    # Authentication
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Scam detection
    if not detect_scam(request.message):
        return {"scam_detected": False}

    scam_type = classify_scam(request.message)

    # Persona selection
    def choose_persona(text):
        if "bank" in text.lower():
            return "senior_citizen"
        if "upi" in text.lower():
            return "shop_owner"
        return "student"

    persona_type = choose_persona(request.message)

    conversation = [
        {"role": "system", "content": PERSONAS[persona_type]},
        {"role": "user", "content": request.message}
    ]

    upi_ids, links, banks = [], [], []

    for turn in range(5):
        ai_msg = ai_reply(conversation)
        conversation.append({"role": "assistant", "content": ai_msg})

        scammer_reply = mock_scammer_api(ai_msg)
        conversation.append({"role": "user", "content": scammer_reply})

        upi_ids += extract_upi(scammer_reply)
        links += extract_links(scammer_reply)
        banks += extract_bank_accounts(scammer_reply)

        if upi_ids or links or banks:
            break

    threat_score = min(
        (40 if upi_ids else 0) +
        (40 if links else 0) +
        (50 if banks else 0),
        100
    )

    return {
        "scam_detected": True,
        "scam_type": scam_type,
        "persona_used": persona_type,
        "turns_taken": turn + 1,
        "threat_score": threat_score,
        "extracted_intelligence": {
            "upi_ids": list(set(upi_ids)),
            "bank_accounts": list(set(banks)),
            "phishing_links": list(set(links))
        },
        "conversation_log": conversation
    }
