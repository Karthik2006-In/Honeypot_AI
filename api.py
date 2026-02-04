from fastapi import FastAPI, Header, HTTPException, Request, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any
from main import run_honeypot_flow

app = FastAPI(title="Agentic Honey-Pot API")

API_KEY = "hackathon123"


# ---------- Pydantic Model ----------
class ScamRequest(BaseModel):
    message: str


# ---------- Root ----------
@app.get("/")
def root():
    return {"status": "API is running", "message": "Go to /docs for Swagger UI"}


# ---------- Honeypot Endpoint ----------
@app.post("/agentic-honeypot")
async def agentic_honeypot(
    request: Request,
    x_api_key: Optional[str] = Header(None),
    message: Optional[str] = Form(None)  # <-- allows form-data
) -> Dict[str, Any]:

    # 1) API Key check
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 2) Try to read JSON
    body_message = None
    try:
        data = await request.json()
        if isinstance(data, dict) and "message" in data:
            body_message = data["message"]
    except:
        pass

    # 3) If not JSON, try form-data
    if body_message is None and message:
        body_message = message

    # 4) If still not, try query param
    if body_message is None:
        query_message = request.query_params.get("message")
        if query_message:
            body_message = query_message

    # 5) If still not found, throw error
    if not body_message:
        raise HTTPException(
            status_code=422,
            detail="Missing 'message'. Send JSON {\"message\": \"...\"} or form-data message=..."
        )

    # 6) Run honeypot
    result = run_honeypot_flow(body_message)
    return result
