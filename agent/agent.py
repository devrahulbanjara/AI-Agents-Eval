import logging
import os
from uuid import uuid4

from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv
from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor

from .llm import cloudflare_model
from .prompts import agent_system_prompt
from .tools import (
    calculate_right_refund,
    get_user_purchase_history,
    issue_refund_ticket,
)

load_dotenv()

if os.getenv("LANGFUSE_SECRET_KEY"):
    OpenAIAgentsInstrumentor().instrument()


def create_refund_agent() -> Agent:
    return Agent(
        name="Refund Support Agent",
        instructions=agent_system_prompt,
        model=cloudflare_model,
        tools=[
            calculate_right_refund,
            get_user_purchase_history,
            issue_refund_ticket,
        ],
    )


def run_conversation() -> None:
    logging.basicConfig(level=logging.INFO)
    agent = create_refund_agent()
    session = SQLiteSession(f"refund-conversation-{uuid4()}")

    user_input = "I would like to request a refund"
    while True:
        print(f"You: {user_input}", flush=True)
        result = Runner.run_sync(agent, user_input, session=session)
        print(f"\nAgent: {result.final_output}\n", flush=True)
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit", "done"}:
            break


if __name__ == "__main__":
    run_conversation()
