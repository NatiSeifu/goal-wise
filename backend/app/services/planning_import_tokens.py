"""Signed, short-lived tokens for planning CSV preview confirmation."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import date, datetime, timedelta
from typing import Any

from pydantic import SecretStr

from app.pace_engine import (
    ExpenseClassification,
    IncomeConfidence,
    IncomeSourceInput,
    PlannedExpenseInput,
    RecurrenceFrequency,
)
from app.services.planning_import import PlanningImport, PlanningImportCash, PlanningImportGoal

PREVIEW_TOKEN_TTL = timedelta(minutes=15)
_PURPOSE = b"goalwise:planning-import-preview:v1:"


class InvalidPlanningImportToken(ValueError):
    """Raised when a preview token is invalid, expired, or for another user."""


def create_planning_import_token(
    planning_import: PlanningImport,
    *,
    user_id: str,
    session_secret: SecretStr | str,
    issued_at: datetime,
) -> str:
    payload = {
        "version": 1,
        "user_id": user_id,
        "expires_at": int((issued_at + PREVIEW_TOKEN_TTL).timestamp()),
        "planning_import": _to_payload(planning_import),
    }
    encoded = _encode(json.dumps(payload, separators=(",", ":"), sort_keys=True))
    return f"{encoded}.{_sign(encoded, session_secret)}"


def read_planning_import_token(
    token: str,
    *,
    user_id: str,
    session_secret: SecretStr | str,
    now: datetime,
) -> PlanningImport:
    try:
        encoded, signature = token.split(".", maxsplit=1)
        if not hmac.compare_digest(signature, _sign(encoded, session_secret)):
            raise InvalidPlanningImportToken
        payload = json.loads(_decode(encoded))
        if not isinstance(payload, dict):
            raise InvalidPlanningImportToken
        if payload.get("version") != 1 or payload.get("user_id") != user_id:
            raise InvalidPlanningImportToken
        expires_at = payload.get("expires_at")
        if not isinstance(expires_at, int) or now.timestamp() >= expires_at:
            raise InvalidPlanningImportToken
        return _from_payload(payload["planning_import"])
    except InvalidPlanningImportToken:
        raise
    except (AttributeError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise InvalidPlanningImportToken from exc


def _to_payload(value: PlanningImport) -> dict[str, Any]:
    return {
        "goal": {
            "name": value.goal.name,
            "target_cents": value.goal.target_cents,
            "initial_saved_cents": value.goal.initial_saved_cents,
            "current_saved_cents": value.goal.current_saved_cents,
            "start_date": value.goal.start_date.isoformat(),
            "target_date": value.goal.target_date.isoformat(),
        },
        "cash": {
            "starting_cash_cents": value.cash.starting_cash_cents,
            "balance_as_of_date": value.cash.balance_as_of_date.isoformat(),
            "reserve_buffer_cents": value.cash.reserve_buffer_cents,
        },
        "income_sources": [
            {
                "name": item.name,
                "amount_cents": item.amount_cents,
                "next_date": item.next_date.isoformat(),
                "frequency": item.frequency.value,
                "confidence": item.confidence.value,
            }
            for item in value.income_sources
        ],
        "planned_expenses": [
            {
                "name": item.name,
                "amount_cents": item.amount_cents,
                "next_date": item.next_date.isoformat(),
                "frequency": item.frequency.value,
                "classification": item.classification.value,
            }
            for item in value.planned_expenses
        ],
    }


def _from_payload(value: Any) -> PlanningImport:
    if not isinstance(value, dict):
        raise InvalidPlanningImportToken
    goal = value["goal"]
    cash = value["cash"]
    if not isinstance(goal, dict) or not isinstance(cash, dict):
        raise InvalidPlanningImportToken
    return PlanningImport(
        goal=PlanningImportGoal(
            name=goal["name"],
            target_cents=goal["target_cents"],
            initial_saved_cents=goal["initial_saved_cents"],
            current_saved_cents=goal["current_saved_cents"],
            start_date=date.fromisoformat(goal["start_date"]),
            target_date=date.fromisoformat(goal["target_date"]),
        ),
        cash=PlanningImportCash(
            starting_cash_cents=cash["starting_cash_cents"],
            balance_as_of_date=date.fromisoformat(cash["balance_as_of_date"]),
            reserve_buffer_cents=cash["reserve_buffer_cents"],
        ),
        income_sources=tuple(
            IncomeSourceInput(
                name=item["name"],
                amount_cents=item["amount_cents"],
                next_date=date.fromisoformat(item["next_date"]),
                frequency=RecurrenceFrequency(item["frequency"]),
                confidence=IncomeConfidence(item["confidence"]),
            )
            for item in value["income_sources"]
        ),
        planned_expenses=tuple(
            PlannedExpenseInput(
                name=item["name"],
                amount_cents=item["amount_cents"],
                next_date=date.fromisoformat(item["next_date"]),
                frequency=RecurrenceFrequency(item["frequency"]),
                classification=ExpenseClassification(item["classification"]),
            )
            for item in value["planned_expenses"]
        ),
    )


def _encode(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode().rstrip("=")


def _decode(value: str) -> str:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)).decode()


def _sign(value: str, session_secret: SecretStr | str) -> str:
    secret = (
        session_secret.get_secret_value()
        if isinstance(session_secret, SecretStr)
        else session_secret
    )
    return hmac.new(_PURPOSE + secret.encode(), value.encode(), hashlib.sha256).hexdigest()
