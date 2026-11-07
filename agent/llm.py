import os

from agents import OpenAIChatCompletionsModel
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

cloudflare_account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"]
cloudflare_api_token = os.environ["CLOUDFLARE_API_TOKEN"]

cloudflare_client = AsyncOpenAI(
    api_key=cloudflare_api_token,
    base_url=(
        "https://api.cloudflare.com/client/v4/"
        f"accounts/{cloudflare_account_id}/ai/v1"
    ),
)

cloudflare_model = OpenAIChatCompletionsModel(
    model="@cf/google/gemma-4-26b-a4b-it",
    openai_client=cloudflare_client,
)
