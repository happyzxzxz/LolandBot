def handle_response(message) -> str:
    """Обрабатывает текст и возвращает ответ"""
    p_message = message.lower()

    if p_message == "hello loland":
        return "Fuck you"
