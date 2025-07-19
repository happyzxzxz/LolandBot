def handle_response(message) -> str:
    """Processes text and gives response"""
    p_message = message.lower()

    if p_message == "hello loland":
        return "Online"
    
