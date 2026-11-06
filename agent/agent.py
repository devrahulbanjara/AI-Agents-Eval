from uuid import uuid4

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langfuse.langchain import CallbackHandler
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from .llm import gemini_llm, openai_llm
from .prompts import agent_system_prompt
from .schemas import Answer
from .tools import (
    calculate_right_refund,
    get_today_date,
    get_user_purchase_history,
    issue_refund_ticket,
)


def create_refund_agent(llm: BaseChatModel = openai_llm):
    return create_agent(
        model=llm,
        system_prompt=agent_system_prompt,
        tools=[
            calculate_right_refund,
            get_user_purchase_history,
            issue_refund_ticket,
            get_today_date,
        ],
        response_format=Answer,
        checkpointer=InMemorySaver(
            serde=JsonPlusSerializer(allowed_msgpack_modules=[Answer])
        ),
    )


def run_conversation():
    agent = create_refund_agent(gemini_llm)

    langfuse_handler = CallbackHandler()

    config: RunnableConfig = {
        "configurable": {"thread_id": str(uuid4())},
        "callbacks": [langfuse_handler],
    }

    text = "I would like to request a refund"
    print(f"You: {text}", flush=True)

    question = HumanMessage(content=text)
    conversation = True

    while conversation:
        response = agent.invoke({"messages": [question]}, config=config)
        structured_response = response["structured_response"]

        print(f"\nAgent: {structured_response.answer}\n", flush=True)

        conversation = structured_response.conversation

        if conversation:
            user_input = input("You: ")
            question = HumanMessage(content=user_input)

    print("the job is done!")


if __name__ == "__main__":
    run_conversation()
