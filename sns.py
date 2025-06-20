def send_sns_message(email: str, message: str):
    print(f"[MOCK SNS] Sending message to {email}: {message}")
    return True 