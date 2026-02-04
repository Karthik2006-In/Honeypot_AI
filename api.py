from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Import your existing honeypot flow function
# IMPORTANT: main.py must contain run_honeypot_flow(message: str) -> dict
from main import run_honeypot_flow

app = FastAPI(
    title="Agentic HoneyPot API",
    version="1.0.0",
    description="Agentic honeypot that detects scams, engages scammers, and extracts UPI IDs, bank accounts, and phishing links."
)

# Your hackathon API key
API_KEY = "hackathon123"


# ----------------------------
# Health Check (IMPORTANT)
# ----------------------------
@app.get("/")
def root():
    return {
        "status": "API is running",
        "message": "Go to /docs for Swagger UI"
    }


# ----------------------------
# Request Body Model
# ----------------------------
# Hackathon testers sometimes send different field names.
# So we accept multiple possibilities:
# - message
# - text
# - input
class ScamRequest(BaseModel):
    message: Optional[str] = None
    text: Optional[str] = None
    input: Optional[str] = None


# ----------------------------
# Main Endpoint
# ----------------------------
@app.post("/agentic-honeypot")
def agentic_honeypot(
    req: ScamRequest,
    x_api_key: Optional[str] = Header(None)
) -> Dict[str, Any]:

    # 1) API Key Validation
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 2) Extract message from any supported field
    msg = req.message or req.text or req.input

    if not msg or not msg.strip():
        raise HTTPException(
            status_code=400,
            detail="INVALID_REQUEST_BODY: Provide 'message' or 'text' or 'input' in JSON body."
        )

    # 3) Run your existing honeypot logic
    try:
        result = run_honeypot_flow(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    # 4) Return structured JSON
    return result
