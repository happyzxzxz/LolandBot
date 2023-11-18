import responses
import openai


async def get_chat_response(session, result, messages):

    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    async with session.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json={
            "model": "gpt-3.5-turbo-0301",
            "messages": [{"role": "system", "content": result}] + messages
        },
    ) as response:
        response_data = await response.json()
        return response_data


async def get_image_response(session, result, size, model):

    headers = {
        "Authorization": f"Bearer {openai.api_key}",
        "Content-Type": "application/json"
    }

    async with session.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json={
            "model": model,
            "prompt": result,
            "n": 1,
            "size": size
        },
    ) as response:
        response_data = await response.json()
        return response_data


async def send_message(message, user_message, is_private):
    try:
        response = responses.handle_response(user_message)
        if response:
            await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)
