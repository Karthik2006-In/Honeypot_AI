import re
from typing import Dict, Any, List

# ----------------------------
# Scam keyword dictionary
# ----------------------------
SCAM_KEYWORDS = {
    "Bank Phishing": [
        "bank", "account", "blocked", "verify", "kyc", "debit", "credit",
        "suspend", "freeze", "update", "otp", "netbanking"
    ],
    "UPI Scam": [
        "upi", "collect", "request", "pin", "scan", "qr", "pay", "transaction"
    ],
    "Lottery Scam": [
        "lottery", "won", "prize", "gift", "lucky", "claim"
    ],
    "Job Scam": [
        "job", "work from home", "salary", "interview", "selection",
        "registration fee", "deposit"
    ]
}

# ----------------------------
# Personas
# ----------------------------
PERSONAS = {
    "senior_citizen": {
        "system": (
            "You are Ramesh Rao, 68 years old, retired. "
            "You are slow with smartphones and very trusting. "
            "Never reveal you are an AI. "
            "Your goal is to make the other person reveal UPI IDs, "
            "bank account numbers, or phishing links."
        )
    },
    "college_student": {
        "system": (
            "You are Karthik, a college student who is busy and slightly confused. "
            "You ask for details and pretend you want to complete the process quickly. "
            "Never reveal you are an AI. "
            "Your goal is to extract UPI IDs, bank account numbers, or phishing links."
        )
    }
}

# ----------------------------
# Regex extractors
# ----------------------------
UPI_REGEX = re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b")
BANK_ACC_REGEX = re.compile(r"\b\d{9,18}\b")
URL_REGEX = re.compile(r"https?://[^\s]+")


def extract_intel(text: str) -> Dict[str, List[str]]:
    upi_ids = list(set(UPI_REGEX.findall(text)))
    urls = list(set(URL_REGEX.findall(text)))

    # Bank accounts: 9–18 digits
    accounts = list(set(BANK_ACC_REGEX.findall(text)))
    accounts = [a for a in accounts if len(a) >= 9]

    return {
        "upi_ids": upi_ids,
        "bank_accounts": accounts,
        "phishing_links": urls
    }


# ----------------------------
# Scam classification
# ----------------------------
def classify_scam(message: str) -> str:
    msg = message.lower()
    scores = {}

    for scam_type, words in SCAM_KEYWORDS.items():
        scores[scam_type] = sum(1 for w in words if w in msg)

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "Unknown Scam"

    return best


def threat_score(message: str) -> int:
    msg = message.lower()
    score = 0

    if any(w in msg for w in ["blocked", "suspend", "freeze", "urgent", "immediately"]):
        score += 15
    if any(w in msg for w in ["otp", "pin", "password"]):
        score += 20
    if "http" in msg or "www" in msg:
        score += 15
    if "upi" in msg:
        score += 10

    return min(score, 100)


# ----------------------------
# Agent reply generator
# ----------------------------
def generate_agent_reply(persona: str, scam_type: str, last_user_msg: str, turn: int) -> str:
    if persona == "senior_citizen":
        if turn == 1:
            return "I'm a bit slow with these new smartphones... can you guide me step by step? What should I click exactly?"
        if "link" in last_user_msg.lower() or "http" in last_user_msg.lower():
            return "Oh dear. Can you send the full link again? I cannot see properly. Also is it safe?"
        if "upi" in last_user_msg.lower():
            return "Okay beta, do I need to send money or receive? Please tell the UPI ID clearly."
        if "otp" in last_user_msg.lower():
            return "I got an OTP message. Should I share it with you to verify? Please confirm."
        return "I am confused. Can you tell me the exact UPI ID or account details I should use to verify?"

    # college_student persona
    if turn == 1:
        return "Bro I'm in a hurry. Send the exact verification link or UPI ID to finish fast."
    if "upi" in last_user_msg.lower():
        return "Okay send the UPI ID properly (like name@upi). Also what should I write in remarks?"
    if "account" in last_user_msg.lower() or "bank" in last_user_msg.lower():
        return "Send your bank account number and IFSC so I can confirm it's official."
    return "Send full details quickly: link / UPI ID / account number. I need to verify now."


# ----------------------------
# MAIN FLOW FUNCTION
# ----------------------------
def run_honeypot_flow(initial_message: str) -> Dict[str, Any]:
    scam_type = classify_scam(initial_message)
    score = threat_score(initial_message)

    scam_detected = scam_type != "Unknown Scam" or score >= 20

    # Persona selection
    persona_used = "senior_citizen" if scam_detected else "college_student"
    system_prompt = PERSONAS[persona_used]["system"]

    # Conversation log
    conversation_log = []
    conversation_log.append({"role": "system", "content": system_prompt})
    conversation_log.append({"role": "user", "content": initial_message})

    # Mock scammer replies (simulated)
    mock_scammer_msgs = [
        "Do it fast or account will be blocked",
        "Send your UPI to verify",
        "Use UPI scammer123@upi to verify",
        "Click https://fake-bank-verify.com/login to verify your KYC",
        "Account number 123456789012"
    ]

    extracted = {"upi_ids": [], "bank_accounts": [], "phishing_links": []}

    turns_taken = 0
    max_turns = 6
    last_user_msg = initial_message

    # Agentic loop
    for t in range(1, max_turns + 1):

        # Agent reply
        agent_reply = generate_agent_reply(persona_used, scam_type, last_user_msg, t)
        conversation_log.append({"role": "assistant", "content": agent_reply})

        # Scammer reply
        scammer_reply = mock_scammer_msgs[min(t - 1, len(mock_scammer_msgs) - 1)]
        conversation_log.append({"role": "user", "content": scammer_reply})

        turns_taken += 1
        last_user_msg = scammer_reply

        # Extract intelligence
        intel = extract_intel(scammer_reply)
        for k in extracted:
            extracted[k].extend(intel[k])
            extracted[k] = list(sorted(set(extracted[k])))

        # Stop early if extracted something useful
        if t >= 3 and (extracted["upi_ids"] or extracted["phishing_links"] or extracted["bank_accounts"]):
            break

    # Final JSON
    return {
        "scam_detected": scam_detected,
        "scam_type": scam_type,
        "persona_used": persona_used,
        "turns_taken": turns_taken,
        "threat_score": score,
        "extracted_intelligence": extracted,
        "conversation_log": conversation_log
    }
