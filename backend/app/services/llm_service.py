import httpx

from app.config import settings


class LLMService:

    def __init__(self):
        self.api_key = settings.llm_api_key_1
        self.model = settings.llm_model

    async def generate_response(self, question: str) -> str:

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/{self.model}:generateContent"
        )

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": question
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": settings.llm_temperature
            }
        }

        params = {
            "key": self.api_key
        }

        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.post(
                url,
                headers=headers,
                params=params,
                json=payload
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"LLM API error {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]