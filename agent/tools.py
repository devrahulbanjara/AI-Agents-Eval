import sys
from datetime import date, datetime

from agents import function_tool
from loguru import logger

from .data import users_data

TODAY = date(2026, 10, 24)

# Keep diagnostic logs on stderr so they never become part of the chat response.
logger.remove()
logger.add(
    sys.stderr,
    colorize=None,
    format="<cyan>[{level}]</cyan> {message}",
    level="INFO",
)


@function_tool
def get_user_purchase_history(user: str) -> dict:
    """Fetch purchase history and explicitly report whether the username exists."""
    logger.info("tool=get_user_purchase_history user={}", user)
    purchases = users_data.get(user)
    if purchases is None:
        return {
            "user_exists": False,
            "user": user,
            "purchases": {},
            "message": f"We couldn't find an account for username '{user}'. Please check the username and try again.",
        }
    return {
        "user_exists": True,
        "user": user,
        "purchases": purchases,
        "message": "Purchase history found.",
    }


def _refund_assessment(user: str, items: list[str]) -> dict:
    purchases = users_data.get(user)
    if purchases is None:
        return {
            "status": "rejected",
            "amount": 0,
            "eligible_items": [],
            "reasons": [f"The username '{user}' does not exist."],
        }

    requested_names = items
    unique_names = list(dict.fromkeys(requested_names))
    reasons = []
    eligible_items = []
    amount = 0

    if len(unique_names) < len(requested_names):
        reasons.append(
            "Each item can only be refunded once; duplicate requests were collapsed."
        )

    for item_name in unique_names:
        purchase = purchases.get(item_name)
        if purchase is None:
            reasons.append(f"{item_name} was not found in the user's purchase history.")
            continue

        purchase_date = datetime.strptime(purchase["date"], "%Y-%m-%d").date()
        if purchase_date > TODAY:
            reasons.append(
                f"{item_name} was purchased in the future and is not refundable."
            )
            continue
        if (TODAY - purchase_date).days > 30:
            reasons.append(
                f"{item_name} was purchased more than 30 days ago and is not refundable."
            )
            continue

        eligible_items.append(item_name)
        amount += purchase["price"]

    if eligible_items and len(eligible_items) == len(unique_names):
        status = "eligible"
    elif eligible_items:
        status = "partial"
    else:
        status = "rejected"

    return {
        "status": status,
        "amount": amount,
        "eligible_items": eligible_items,
        "reasons": reasons,
    }


@function_tool
def calculate_right_refund(user: str, items: list[str]) -> dict:
    """Validate requested items against policy and calculate the refund amount."""

    logger.info("tool=calculate_right_refund user={}", user)

    return _refund_assessment(user, items)


@function_tool
def issue_refund_ticket(user: str, items: list[str], refund_amount: int) -> dict:
    """Issue a ticket only when every requested item and amount are eligible."""

    logger.info("tool=issue_refund_ticket user={} amount={}", user, refund_amount)
    assessment = _refund_assessment(user, items)
    if assessment["status"] != "eligible":
        return {
            "status": "rejected",
            "refund_amount": 0,
            "message": "Refund ticket rejected because the requested items are not all eligible.",
            "reasons": assessment["reasons"],
        }
    if refund_amount != assessment["amount"]:
        return {
            "status": "rejected",
            "refund_amount": 0,
            "message": "Refund ticket rejected because the amount does not match the eligible items.",
            "reasons": [f"Expected amount: {assessment['amount']}"],
        }
    return {
        "status": "issued",
        "user": user,
        "items": assessment["eligible_items"],
        "refund_amount": refund_amount,
        "message": f"Refund ticket issued successfully for ${refund_amount}.",
    }
