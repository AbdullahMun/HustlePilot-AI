"""Shared runner: try Gemini, fall back to demo data, never raise to the UI."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Generic, Optional, Type, TypeVar

from pydantic import BaseModel

from config import settings
from prompts.agent_prompts import SYSTEM_PROMPT
from services.gemini_service import GeminiError, generate_structured

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

LIVE = "live"
DEMO = "demo"


@dataclass
class AgentResult(Generic[T]):
    data: T
    source: str = LIVE            # "live" (Gemini) or "demo" (fallback)
    notice: Optional[str] = None  # friendly reason when source == "demo"


def run_agent(
    prompt: str,
    schema: Type[T],
    fallback: Callable[[], T],
    *,
    temperature: float = 0.7,
) -> AgentResult[T]:
    if settings.force_demo_mode():
        return AgentResult(fallback(), DEMO, "Demo mode is switched on, so no Gemini call was made.")
    if not settings.has_api_key():
        return AgentResult(fallback(), DEMO, "No Gemini API key found, so demo data is shown.")
    try:
        data = generate_structured(prompt, schema, system_instruction=SYSTEM_PROMPT, temperature=temperature)
        return AgentResult(data, LIVE)
    
    # except GeminiError as exc:
    #     return AgentResult(fallback(), DEMO, f"{exc.user_message} Showing demo data instead.")

    except GeminiError as exc:
        return AgentResult(
        fallback(),
        DEMO,
        f"Gemini error [{exc.kind}]: {exc.user_message}"
    )

    except Exception:  # never let an unexpected error reach the UI as a traceback
        logger.exception("Unexpected agent failure")
        return AgentResult(fallback(), DEMO, "Something unexpected went wrong. Showing demo data instead.")
