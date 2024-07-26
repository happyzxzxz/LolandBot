def handle_response(message) -> str:
    """Custom message handling and responding"""
    p_message = message.lower()

    if p_message == "hello bot":
        return "Online"
