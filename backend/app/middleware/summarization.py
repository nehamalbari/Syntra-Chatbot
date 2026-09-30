import httpx

from app.config import settings
from app.routing.api_key_manager import APIKeyManager


class SummarizationService:

    def __init__(self):
        self.key_manager = APIKeyManager()
        self.model = settings.llm_model

    async def summarize(
        self,
        messages: list,
    ) -> str:

        if not messages:
            return ""

        if not self.model:
            raise RuntimeError(
                "LLM_MODEL is not configured in the .env file."
            )

        key_count = self.key_manager.get_key_count()

        if key_count == 0:
            raise RuntimeError(
                "No LLM API keys are configured."
            )

        conversation = []

        for message in messages:

            role = (
                "User"
                if message.role == "user"
                else "Assistant"
            )

            conversation.append(
                f"{role}: {message.content}"
            )

        conversation_text = "\n".join(
            conversation
        )

        prompt = f"""
Summarize the following conversation.

Preserve:
- Important facts provided by the user
- User preferences
- Important questions and answers
- Important decisions or instructions
- Information needed to maintain future conversation context

Do not add information that is not present.

Conversation:

{conversation_text}

Provide a concise factual summary.
"""

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{self.model}:generateContent"
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ],
                }
            ],
            "generationConfig": {
                "temperature": 0.0
            },
        }

        last_error = None

        for attempt in range(key_count):

            api_key = self.key_manager.get_next_key()

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            }

            try:

                async with httpx.AsyncClient(
                    timeout=30.0
                ) as client:

                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload,
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

                # Try another key for temporary API failures
                if response.status_code in {
                    429,
                    500,
                    502,
                    503,
                    504
                }:

                    last_error = (
                        f"Summarization API returned "
                        f"{response.status_code}: "
                        f"{response.text}"
                    )

                    continue

                # Non-retryable error
                raise RuntimeError(
                    f"Summarization API error "
                    f"{response.status_code}: "
                    f"{response.text}"
                )

            except httpx.RequestError as exc:

                last_error = (
                    f"Network error: {str(exc)}"
                )

                continue

        raise RuntimeError(
            f"All configured API keys failed "
            f"during summarization. "
            f"Last error: {last_error}"
        )