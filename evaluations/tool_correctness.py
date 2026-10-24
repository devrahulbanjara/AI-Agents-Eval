"""Tool correctness eval for the refund agent.

Usage (from the repo root):
    uv run python -m evaluations.tool_correctness
"""

import os
from uuid import uuid4

from deepeval import evaluate
from deepeval.evaluate import CacheConfig
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall, ToolCallParams
from dotenv import load_dotenv

from agent.agent import agent
from agent.schemas import Answer

from .dataset import REFERENCE_DATE, goldens
from .model import eval_model

load_dotenv()

# Pin the agent's date so date-based goldens stay valid.
os.environ["AGENT_TODAY"] = REFERENCE_DATE

test_cases = []

for golden in goldens:
    print(f"\nRunning: {golden.input}")

    response = agent.invoke(
        {"messages": [{"role": "user", "content": golden.input}]},
        config={"configurable": {"thread_id": str(uuid4())}},
    )

    tools_called = []
    for message in response["messages"]:
        for tool_call in getattr(message, "tool_calls", []) or []:
            # Skip the structured-output call emitted by ToolStrategy(Answer).
            if tool_call["name"] == Answer.__name__:
                continue
            tools_called.append(
                ToolCall(name=tool_call["name"], input_parameters=tool_call["args"])
            )

    # Fall back to the last message when the model replies without the
    # structured-output tool.
    structured = response.get("structured_response")
    actual_output = (
        structured.answer if structured else str(response["messages"][-1].content)
    )

    test_cases.append(
        LLMTestCase(
            input=golden.input,
            actual_output=actual_output,
            tools_called=tools_called,
            expected_tools=golden.expected_tools,
        )
    )

# Exact match on names, order, and arguments. Non-exact mode ignores extra calls,
# so an unwarranted refund ticket would still pass.
metric = ToolCorrectnessMetric(
    threshold=1.0,
    evaluation_params=[ToolCallParams.INPUT_PARAMETERS],
    should_exact_match=True,
    include_reason=True,
    model=eval_model,
)

evaluate(
    test_cases=test_cases,
    metrics=[metric],
    cache_config=CacheConfig(use_cache=False, write_cache=False),
)
