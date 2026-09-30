import json

import httpx

from app.config import settings
from app.routing.api_key_manager import APIKeyManager


class LLMService:

    def __init__(self):
        self.key_manager = APIKeyManager()
        self.model = settings.llm_model

    def _build_contents(
        self,
        question: str,
        history: list | None = None,
        summary: str | None = None,
    ) -> list:

        contents = []

        # Add previous conversation summary
        if summary:
            contents.append(
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": (
                                "Here is a summary of the "
                                "earlier conversation. "
                                "Use it as context for the "
                                "current conversation:\n\n"
                                f"{summary}"
                            )
                        }
                    ],
                }
            )

        # Add conversation history
        if history:
            for message in history:

                role = (
                    "model"
                    if message.role == "assistant"
                    else "user"
                )

                contents.append(
                    {
                        "role": role,
                        "parts": [
                            {
                                "text": message.content
                            }
                        ],
                    }
                )

        # Add current question
        contents.append(
            {
                "role": "user",
                "parts": [
                    {
                        "text": question
                    }
                ],
            }
        )

        return contents

    async def generate_response(
        self,
        question: str,
        history: list | None = None,
        summary: str | None = None,
    ) -> str:

        if not self.model:
            raise RuntimeError(
                "LLM_MODEL is not configured in the .env file."
            )

        key_count = self.key_manager.get_key_count()

        if key_count == 0:
            raise RuntimeError(
                "No LLM API keys are configured."
            )

        contents = self._build_contents(
            question=question,
            history=history,
            summary=summary,
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
                "contents": contents,
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

    async def generate_response_stream(
        self,
        question: str,
        history: list | None = None,
        summary: str | None = None,
    ):

        if not self.model:
            raise RuntimeError(
                "LLM_MODEL is not configured in the .env file."
            )

        key_count = self.key_manager.get_key_count()

        if key_count == 0:
            raise RuntimeError(
                "No LLM API keys are configured."
            )

        contents = self._build_contents(
            question=question,
            history=history,
            summary=summary,
        )

        last_error = None

        for attempt in range(key_count):

            api_key = self.key_manager.get_next_key()

            url = (
                "https://generativelanguage.googleapis.com/"
                f"v1beta/models/{self.model}:streamGenerateContent"
                "?alt=sse"
            )

            headers = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "x-goog-api-key": api_key,
            }

            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": settings.llm_temperature
                }
            }

            try:

                async with httpx.AsyncClient(
                    timeout=60.0
                ) as client:

                    async with client.stream(
                        "POST",
                        url,
                        headers=headers,
                        json=payload,
                    ) as response:

                        if response.status_code != 200:

                            error_text = await response.aread()

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
                                    f"{error_text.decode()}"
                                )

                                continue

                            raise RuntimeError(
                                f"LLM streaming API error "
                                f"{response.status_code}: "
                                f"{error_text.decode()}"
                            )

                        buffer = ""

                        async for raw_chunk in response.aiter_bytes():

                            if not raw_chunk:
                                continue

                            buffer += raw_chunk.decode(
                                "utf-8",
                                errors="ignore"
                            )

                            while "\n\n" in buffer:

                                event, buffer = buffer.split(
                                    "\n\n",
                                    1
                                )

                                for line in event.splitlines():

                                    line = line.strip()

                                    if not line.startswith("data:"):
                                        continue

                                    data_text = line[
                                        5:
                                    ].strip()

                                    if data_text == "[DONE]":
                                        return

                                    try:

                                        data = json.loads(
                                            data_text
                                        )

                                    except json.JSONDecodeError:
                                        continue

                                    candidates = data.get(
                                        "candidates",
                                        []
                                    )

                                    if not candidates:
                                        continue

                                    content = candidates[0].get(
                                        "content",
                                        {}
                                    )

                                    parts = content.get(
                                        "parts",
                                        []
                                    )

                                    if not parts:
                                        continue

                                    text = parts[0].get(
                                        "text",
                                        ""
                                    )

                                    if text:
                                        yield text

                        return

            except httpx.RequestError as exc:

                last_error = (
                    f"Network error: {str(exc)}"
                )

                continue

        raise RuntimeError(
            f"All configured API keys failed "
            f"during streaming. "
            f"Last error: {last_error}"
        )