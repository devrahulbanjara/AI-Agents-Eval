from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()

# Stay under the Gemini free-tier requests-per-minute limit.
rate_limiter = InMemoryRateLimiter(requests_per_second=4 / 60, max_bucket_size=1)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    temperature=0,
    timeout=None,
    max_retries=2,
    rate_limiter=rate_limiter,
)

openai_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    timeout=None,
    max_retries=2,
)
