from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.links import inspect_links
from backend.app.services.rules import RuleContext, run_rules
from contracts.schemas import Signal


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def signals_for(text: str, channel: str = "sms", sender: str | None = None) -> list[Signal]:
    return run_rules(RuleContext(text, channel, sender, inspect_links(text)))


def codes_for(text: str, channel: str = "sms", sender: str | None = None) -> set[str]:
    return {s.code for s in signals_for(text, channel, sender)}
