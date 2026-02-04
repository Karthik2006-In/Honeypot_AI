import re

def extract_upi(text):
    return re.findall(r"[a-zA-Z0-9.\-_]+@[a-zA-Z]+", text)

def extract_links(text):
    return re.findall(r"https?://[^\s]+", text)

def extract_bank_accounts(text):
    return re.findall(r"\b\d{9,18}\b", text)
