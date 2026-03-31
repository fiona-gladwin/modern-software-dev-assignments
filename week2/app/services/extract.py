from __future__ import annotations

import os
import re
import json
from typing import Any, List
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)
LLM_MODEL_NAME = os.getenv("OLLAMA_ACTION_ITEMS_MODEL", "llama3.1:8b")
LLM_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "action_items": {
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["action_items"],
}


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    return _dedupe_items(extracted)


def extract_action_items_llm(text: str) -> List[str]:
    if not text or not text.strip():
        return []

    try:
        response = chat(
            model=LLM_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract actionable todo items from notes. "
                        "Return only valid JSON matching the schema."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Extract action items from the following text. "
                        "Keep each item concise and imperative.\n\n"
                        f"Text:\n{text}"
                    ),
                },
            ],
            format=LLM_RESPONSE_SCHEMA,
            options={"temperature": 0},
        )
        raw_content = response.message.content or ""
        candidates = _parse_llm_action_items(raw_content)
        extracted = [str(item).strip() for item in candidates if str(item).strip()]
        return _dedupe_items(extracted)
    except Exception as exc:
        print(
            f"LLM extraction failed; falling back to rule-based extraction: {exc}"
        )
        # Fallback to deterministic extractor when model output is unavailable/invalid.
        return extract_action_items(text)


def _parse_llm_action_items(raw_content: str) -> list[Any]:
    parsed = json.loads(raw_content)
    if isinstance(parsed, dict):
        items = parsed.get("action_items", [])
        return items if isinstance(items, list) else []
    if isinstance(parsed, list):
        # Graceful handling if model returns a plain array.
        return parsed
    return []


def _dedupe_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
