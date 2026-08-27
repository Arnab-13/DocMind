import httpx

from app.config import OPENROUTER_API_KEY, LLM_MODEL


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def generate_answer(
    system_prompt: str,
    user_prompt: str,
) -> str:

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    }

    async with httpx.AsyncClient(timeout=90) as client:

        response = await client.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

    return data["choices"][0]["message"]["content"]