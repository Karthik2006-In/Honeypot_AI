def mock_scammer_api(agent_message):
    msg = agent_message.lower()

    if "confused" in msg or "not understand" in msg:
        return "Use UPI scammer123@upi to verify"

    if "upi" in msg:
        return "Visit http://fakebank-login.in"

    return "Do it fast or account will be blocked"
