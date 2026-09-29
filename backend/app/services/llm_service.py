import httpx

from app.config import settings
from app.routing.api_key_manager import APIKeyManager


class LLMService:

    def __init__(self):
        self.key_manager = APIKeyManager()
        self.model = settings.llm_model

    async def generate_response(self, question: str) -> str:

        if not self.model:
            raise RuntimeError(
                "LLM_MODEL is not configured in the .env file."
            )

        key_count = self.key_manager.get_key_count()

        if key_count == 0:
            raise RuntimeError(
                "No LLM API keys are configured."
            )

        last_error = None

        for attempt in range(key_count):

            api_key = self.key_manager.get_next_key()

            url = (
                "https://generativelanguage.googleapis.com/"
                f"v1beta/models/{self.model}:generateContent"
            )

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
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

            try:

                async with httpx.AsyncClient(
                    timeout=30.0
                ) as client:

                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload
                    )

                if response.status_code == 200:

                    data = response.json()

                    return data[
                        "candidates"
                    ][0][
                        "content"
                    ][
                        "parts"
                    ][0]["text"]

                # These errors can trigger fallback
                if response.status_code in {
                    429,
                    500,
                    502,
                    503,
                    504
                }:

                    last_error = (
                        f"API returned "
                        f"{response.status_code}: "
                        f"{response.text}"
                    )

                    continue

                # Non-retryable error
                raise RuntimeError(
                    f"LLM API error "
                    f"{response.status_code}: "
                    f"{response.text}"
                )

            except httpx.RequestError as exc:

                last_error = (
                    f"Network error: {str(exc)}"
                )

                continue

        raise RuntimeError(
            f"All configured API keys failed. "
            f"Last error: {last_error}"
        )