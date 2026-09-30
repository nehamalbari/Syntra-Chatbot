from dotenv import load_dotenv
import os
import httpx


load_dotenv()


api_key = os.getenv("LLM_API_KEY_1")


url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.8-flash:streamGenerateContent"
    "?alt=sse"
)


headers = {
    "x-goog-api-key": api_key,
    "Content-Type": "application/json",
    "Accept": "text/event-stream",
}


payload = {
    "contents": [
        {
            "role": "user",
            "parts": [
                {
                    "text": "Explain Python in one short sentence."
                }
            ],
        }
    ]
}


print("Starting streaming test...")


try:

    with httpx.Client(timeout=60.0) as client:

        with client.stream(
            "POST",
            url,
            headers=headers,
            json=payload,
        ) as response:

            print("STATUS:", response.status_code)

            for line in response.iter_lines():

                if line:
                    print("CHUNK:", line)


except Exception as exc:

    print("ERROR:", type(exc).__name__)
    print(exc)