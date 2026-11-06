"""Tool argument correctness eval for the refund agent.

Usage (from the repo root):
    uv run python -m evaluations.tool_argument_correctness
"""

import os
from uuid import uuid4

from deepeval import evaluate
from deepeval.evaluate import CacheConfig
from deepeval.metrics import ArgumentCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage

from agent.agent import create_refund_agent
from agent.llm import gemini_llm

from .dataset import REFERENCE_DATE, goldens
from .model import eval_model

load_dotenv()

# Pin the agent's date so date-based goldens stay valid.
os.environ["AGENT_TODAY"] = REFERENCE_DATE

test_cases = []
agent = create_refund_agent(llm=gemini_llm)

for golden in goldens:
    print(f"\nRunning: {golden.input}")

    response = agent.invoke(
        {"messages": [{"role": "user", "content": golden.input}]},
        config={"configurable": {"thread_id": str(uuid4())}},
    )

    messages = response["messages"]

    tools_called = []

    for index, message in enumerate(messages):
        if not isinstance(message, AIMessage):
            continue

        for tool_call in message.tool_calls:
            print(f"{index + 1} th message says it needs {tool_call['name']} tool call")
            tool_output = None

            # After this AI decision to tool call lets check all messages to find the tool output (because tool is called actually after this message)
            for later_message in messages[index + 1 :]:
                if (
                    isinstance(later_message, ToolMessage)
                    and later_message.tool_call_id == tool_call["id"]
                ):
                    tool_output = later_message.content
                    break

            tools_called.append(
                ToolCall(
                    name=tool_call["name"],
                    input_parameters=tool_call["args"],
                    output=tool_output,
                )
            )

    actual_output = response["structured_response"].answer

    test_cases.append(
        LLMTestCase(
            input=golden.input,
            actual_output=actual_output,
            tools_called=tools_called,
            expected_tools=golden.expected_tools,
        )
    )


metric = ArgumentCorrectnessMetric(
    threshold=1.0, include_reason=True, model=eval_model, verbose_mode=True
)

evaluate(
    test_cases=test_cases,
    metrics=[metric],
    cache_config=CacheConfig(use_cache=False, write_cache=False),
)
