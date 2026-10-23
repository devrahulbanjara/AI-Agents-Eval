from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

try:
    # Make a simple completion call using a standard model
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a one-sentence greeting."},
        ],
        max_tokens=30,
    )

    # Print the response text
    print("\n--- API Response Success ---")
    print(response.choices[0].message.content)
except Exception as e:  # noqa: BLE001
    print("\n--- An Error Occurred ---")
    print(e)
