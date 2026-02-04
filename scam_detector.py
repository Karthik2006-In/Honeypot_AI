def detect_scam(text):
    keywords = ["blocked", "verify", "urgent", "click", "otp", "suspend"]
    text = text.lower()
    return any(word in text for word in keywords)

def classify_scam(text):
    text = text.lower()
    if "upi" in text:
        return "UPI Fraud"
    if "bank" in text or "account" in text:
        return "Bank Phishing"
    if "kyc" in text:
        return "KYC Scam"
    return "Unknown Scam"
