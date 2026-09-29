from app.config import settings


class APIKeyManager:

    def __init__(self):
        self.api_keys = [
            key
            for key in [
                settings.llm_api_key_1,
                settings.llm_api_key_2,
                settings.llm_api_key_3,
            ]
            if key
        ]

        self.current_index = 0

    def get_next_key(self):
        if not self.api_keys:
            raise RuntimeError("No LLM API keys configured.")

        key = self.api_keys[self.current_index]

        self.current_index = (
            self.current_index + 1
        ) % len(self.api_keys)

        return key

    def get_key_count(self):
        return len(self.api_keys)