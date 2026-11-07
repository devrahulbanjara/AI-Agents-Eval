"""Tool correctness evaluation for the refund agent.

Usage from the repository root:
    uv run python -m evaluations.tool_correctness
"""

import json
from uuid import uuid4

import deepeval
from agents import Runner, add_trace_processor
from deepeval import evaluate
from deepeval.evaluate import CacheConfig
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.openai_agents import DeepEvalTracingProcessor
from deepeval.test_case import LLMTestCase, ToolCall, ToolCallParams

from agent.agent import create_refund_agent

from .dataset import goldens
from .model import eval_model

add_trace_processor(DeepEvalTracingProcessor())
agent = create_refund_agent()
test_cases = []

for golden in goldens:
    print(f"\nRunning: {golden.input}")
    result = Runner.run_sync(
        agent,
        golden.input,
        run_config={"workflow_name": f"refund-eval-{uuid4()}"},
    )

    tools_called = []
    for item in result.new_items:
        if item.type != "tool_call_item":
            continue

        tool_name = item.tool_name
        if tool_name not in {
            "get_user_purchase_history",
            "calculate_right_refund",
            "issue_refund_ticket",
        }:
            continue

        raw_arguments = getattr(item.raw_item, "arguments", None)
        if not isinstance(raw_arguments, str):
            continue

        tools_called.append(
            ToolCall(
                name=tool_name,
                input_parameters=json.loads(raw_arguments),
            )
        )

    test_cases.append(
        LLMTestCase(
            input=golden.input,
            actual_output=result.final_output,
            tools_called=tools_called,
            expected_tools=golden.expected_tools,
        )
    )

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

deepeval.flush_traces(timeout=30.0)
