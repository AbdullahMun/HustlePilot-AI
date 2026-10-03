"""Thin wrapper around the official Google GenAI SDK (`google-genai`).

Responsibilities: build the client, request JSON, parse + validate it against a
Pydantic schema, and translate every failure into a friendly `GeminiError`.
API keys are never logged or included in error messages.
"""
from __future__ import annotations

import json
import logging
import re
import time
from functools import lru_cache
from typing import Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

from config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

_USER_MESSAGES = {
    "missing_key": "No Gemini API key found. Add GEMINI_API_KEY to your .env file or Streamlit secrets.",
    "invalid_key": "Gemini rejected the API key. Check that the key is correct and enabled, then try again.",
    "rate_limit": "Gemini is rate-limiting requests or the quota is used up. Wait a minute and try again.",
    "network": "Could not reach Gemini (network problem or timeout). Check your connection and try again.",
    "model": "The configured Gemini model was not found. Set GEMINI_MODEL to a model available to your key.",
    "sdk": "The Google GenAI SDK is not installed. Run: pip install -r requirements.txt",
    "empty": "Gemini returned an empty response.",
    "invalid": "Gemini returned a response the app could not read.",
    "api": "Gemini returned an error. Please try again in a moment.",
}


class GeminiError(Exception):
    """Raised for any Gemini-related failure; `user_message` is safe to display."""

    def __init__(self, kind: str, detail: str = ""):
        self.kind = kind
        self.user_message = _USER_MESSAGES.get(kind, _USER_MESSAGES["api"])
        super().__init__(f"{kind}: {detail}" if detail else kind)


@lru_cache(maxsize=2)
def _client(api_key: str):
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover
        raise GeminiError("sdk") from exc
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=settings.REQUEST_TIMEOUT_SECONDS * 1000),
    )


def _classify(exc: Exception) -> str:
    text = f"{type(exc).__name__} {exc}".lower()
    if any(s in text for s in ("api key not valid", "api_key_invalid", "permission_denied", "unauthenticated", " 401", " 403")):
        return "invalid_key"
    if any(s in text for s in ("429", "resource_exhausted", "quota", "rate limit")):
        return "rate_limit"
    if "404" in text or ("model" in text and "not found" in text):
        return "model"
    if any(s in text for s in ("timeout", "timed out", "deadline", "connect", "network", "dns", "unreachable", "503", "unavailable")):
        return "network"
    return "api"


def _extract_text(response) -> str:
    try:
        text = getattr(response, "text", None)
    except Exception:
        text = None
    return (text or "").strip()


def _parse_json(text: str):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                pass
    raise GeminiError("invalid", "malformed JSON")


def _validate(data, schema: Type[T]) -> T:
    if isinstance(data, list) and len(schema.model_fields) == 1:
        data = {next(iter(schema.model_fields)): data}
    try:
        obj = schema.model_validate(data)
    except ValidationError as exc:
        raise GeminiError("invalid", f"{len(exc.errors())} validation errors") from exc
    missing = obj.missing_required() if hasattr(obj, "missing_required") else []
    if missing:
        raise GeminiError("invalid", f"missing fields: {', '.join(missing)}")
    return obj


def _schema_instruction(schema: Type[BaseModel]) -> str:
    return (
        "\n\nReturn ONLY a single valid JSON object (no markdown, no commentary) that matches this JSON Schema. "
        "Fill every field; use empty strings or empty lists only when truly unknown.\n"
        + json.dumps(schema.model_json_schema())
    )


def generate_structured(
    prompt: str,
    schema: Type[T],
    *,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
) -> T:
    """Call Gemini and return a validated Pydantic object, or raise GeminiError."""
    api_key = settings.get_api_key()
    if not api_key:
        raise GeminiError("missing_key")
    try:
        from google.genai import types
    except ImportError as exc:  # pragma: no cover
        raise GeminiError("sdk") from exc

    client = _client(api_key)
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        response_mime_type="application/json",
    )
    base_prompt = prompt + _schema_instruction(schema)
    contents = base_prompt
    last_error: Optional[GeminiError] = None

    for attempt in range(settings.MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=settings.get_model_name(), contents=contents, config=config
            )
        except GeminiError:
            raise
        except Exception as exc:  # SDK/network errors vary widely
            kind = _classify(exc)
            logger.warning("Gemini call failed (%s): %s", kind, type(exc).__name__)
            last_error = GeminiError(kind)
            if kind in {"network", "rate_limit"} and attempt + 1 < settings.MAX_RETRIES:
                time.sleep(2)
                continue
            raise last_error from None

        text = _extract_text(response)
        if not text:
            last_error = GeminiError("empty")
            continue
        try:
            return _validate(_parse_json(text), schema)
        except GeminiError as exc:
            last_error = exc
            contents = base_prompt + "\n\nYour previous reply was not valid or was incomplete. Reply again with ONLY the complete JSON object."

    raise last_error or GeminiError("api")
