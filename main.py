import json
from scam_detector import detect_scam, classify_scam
from ai_agent import ai_reply
from mock_scammer import mock_scammer_api
from extractor import extract_upi, extract_links, extract_bank_accounts
from config import PERSONAS

MAX_TURNS = 5

# Mock Scammer API initial message
incoming_message = {
    "text": "Your bank account is blocked. Click to verify."
}

# Scam detection
if not detect_scam(incoming_message["text"]):
    print({"scam_detected": False})
    exit()

scam_type = classify_scam(incoming_message["text"])

# Persona selection (agentic)
def choose_persona(text):
    if "bank" in text.lower():
        return "senior_citizen"
    if "upi" in text.lower():
        return "shop_owner"
    return "student"

persona_type = choose_persona(incoming_message["text"])

conversation = [
    {"role": "system", "content": PERSONAS[persona_type]},
    {"role": "user", "content": incoming_message["text"]}
]

upi_ids, links, banks = [], [], []

# Autonomous conversation loop
for turn in range(MAX_TURNS):
    ai_msg = ai_reply(conversation)
    conversation.append({"role": "assistant", "content": ai_msg})

    scammer_reply = mock_scammer_api(ai_msg)
    conversation.append({"role": "user", "content": scammer_reply})

    upi_ids += extract_upi(scammer_reply)
    links += extract_links(scammer_reply)
    banks += extract_bank_accounts(scammer_reply)

    if upi_ids or links or banks:
        break

# Threat score
threat_score = 0
if upi_ids:
    threat_score += 40
if links:
    threat_score += 40
if banks:
    threat_score += 50
threat_score = min(threat_score, 100)

# Final structured JSON
final_output = {
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

with open("scam_output.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=4)

print("✅ Output saved to scam_output.json")

