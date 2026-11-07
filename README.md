<div align="center">

![Python](https://img.shields.io/badge/Python-3.14%2B-blue?logo=python&logoColor=white)
![Agent](https://img.shields.io/badge/Agent-OpenAI%20Agents%20SDK-grey?logo=openai&logoColor=white)
![Evaluation](https://img.shields.io/badge/Evaluation-DeepEval-teal)
![Models](https://img.shields.io/badge/Models-Cloudflare%20Workers%20AI%20%7C%20OpenAI-purple?logo=openai&logoColor=white)
![Packages](https://img.shields.io/badge/Packages-uv-blueviolet)

# 🤖 AI Agents Evaluation System

**A production-style evaluation framework for a customer support refund agent — testing major things that break an agent in production with DeepEval and a structured golden dataset.**

</div>

---

## 📌 Overview

This project builds and evaluates a **customer support refund agent** that handles natural-language refund requests by orchestrating a sequence of tool calls: looking up purchase history, validating refund eligibility, computing the refund amount, and issuing a refund ticket.

The evaluation layer uses **DeepEval's Tool Correctness Metric** (as of now, adding more , work in progress) to verify that the agent calls exactly the right tools, in the right order, with the right parameters — across a hand-crafted golden dataset of 12 real-world scenarios.

> ⚠️ **Work in progress** — evaluation suite is actively evolving as the agent and dataset are refined.

---

## 🏗️ Architecture

```
AI-Agents-Eval/
├── agent/
│   ├── agent.py        # Agent factory (create_refund_agent)
│   ├── data.py         # In-memory user purchase database
│   ├── llm.py          # Cloudflare OpenAI-compatible model configuration
│   ├── prompts.py      # System prompt with refund business rules
│   ├── schemas.py      # Shared Pydantic schemas
│   └── tools.py        # OpenAI Agents SDK function tools
├── evaluations/
│   ├── dataset.py      # 12 golden test cases with expected tool call sequences
│   ├── model.py        # Evaluation model config (gpt-4o-mini)
│   └── tool_correctness.py  # DeepEval evaluation runner
├── docs/
│   └── tool_correctness.png  # Latest eval results screenshot
└── pyproject.toml
```

---

## 🛠️ Agent Tools

The agent has access to four tools it must orchestrate correctly:

| Tool | Description |
|------|-------------|
| `get_user_purchase_history` | Fetches purchase records for a given username |
| `calculate_right_refund` | Validates policy eligibility and computes the refund value |
| `issue_refund_ticket` | Revalidates eligibility and issues the final refund ticket |

---

## ✅ Evaluation

Evaluations are powered by **[DeepEval](https://github.com/confident-ai/deepeval)** using the `ToolCorrectnessMetric`, which checks:
- Were the right tools called?
- Were they called with the correct input parameters?

The golden dataset covers 12 scenarios including happy paths, expired items, future-dated purchases, partial refunds, unknown users, and adversarial manipulation attempts.

**Generation model:** `@cf/google/gemma-4-26b-a4b-it` via Cloudflare Workers AI
**Evaluation model:** `gpt-4o-mini`

### Latest Results

![Tool Correctness Eval](docs/tool_correctness.png)

---

## ⚙️ Setup

**Prerequisites:** Python 3.14+, [`uv`](https://docs.astral.sh/uv/)

```bash
# Clone the repo
git clone https://github.com/devrahulbanjara/AI-Agents-Eval.git
cd AI-Agents-Eval

# Install dependencies
uv sync

# Configure environment variables
cp .env.example .env
# Add your Cloudflare and OpenAI credentials to .env
```

---

## 🚀 Running the Evaluation

```bash
uv run python -m evaluations.tool_correctness
```

---

## 💬 Running the Agent Interactively

```bash
uv run python -m agent.agent
```

The agent will start a conversation and guide you through the refund process.

---

## 📋 Golden Dataset Scenarios

| # | Scenario | Expected Outcome |
|---|----------|-----------------|
| 0 | Single eligible item (14 days old) | Full refund issued |
| 1 | Partial refund — keep one item | Refund for requested item only |
| 2 | Expired item (91 days old) | Refund denied — outside 30-day window |
| 3 | Boundary case — exactly 30 days old | Refund issued |
| 4 | Future-dated purchase | Refund denied — invalid purchase date |
| 5 | Mixed basket — one eligible, one expired | Partial refund for eligible item only |
| 6 | No username provided | Agent asks for username, no tool calls |
| 7 | Unknown user | Agent rejects username, asks for valid one |
| 8 | Item not in purchase history | Refund denied — item never purchased |
| 9 | Info request only — no refund | Purchase history listed, no refund issued |
| 10 | Social engineering — claimed manager exception | Refund denied, no exceptions |
| 11 | Duplicate item manipulation | Single refund only |

---

## 🔑 Environment Variables

```env
OPENAI_API_KEY=your_openai_key
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
```

