from __future__ import annotations

import os
from typing import Any
import httpx

from google import genai
from google.genai import errors, types

from .agent import LLMProviderError
from .models import AssistantTurn, ToolCall


class GeminiLLM:
    mode = "gemini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        client: Any | None = None,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if client is None and not key:
            raise ValueError("GEMINI_API_KEY is required for live mode")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
        self.client = client or genai.Client(
            api_key=key,
            http_options=types.HttpOptions(
                timeout=30_000,
                retry_options=types.HttpRetryOptions(
                    attempts=1,
                    http_status_codes=[429, 500, 502, 503, 504],
                ),
            ),
        )

    def complete(self, messages: list[dict], tools: list[dict]) -> AssistantTurn:
        system_instruction = next(
            (message["content"] for message in messages if message["role"] == "system"),
            None,
        )
        contents = [
            content
            for message in messages
            if message["role"] != "system"
            for content in [self._to_content(message)]
        ]
        declarations = [
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters_json_schema=tool["parameters"],
            )
            for tool in tools
        ]
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0,
                    max_output_tokens=512,
                    thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
                    tools=[types.Tool(function_declarations=declarations)],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
        except errors.APIError as exc:
            if exc.code == 429:
                reason = "provider quota or rate limit reached"
            else:
                reason = f"provider returned HTTP {exc.code}"
            raise LLMProviderError(reason) from exc
        except (httpx.TransportError, TimeoutError, ConnectionError) as exc:
            raise LLMProviderError("network unavailable or request timed out") from exc

        candidates = response.candidates or []
        if not candidates or not candidates[0].content or not candidates[0].content.parts:
            raise LLMProviderError("empty or blocked model response")
        parts = candidates[0].content.parts
        text = "".join(part.text or "" for part in parts).strip() or None
        calls = [
            ToolCall(
                id=part.function_call.id or f"gemini-call-{index}",
                name=part.function_call.name,
                arguments=dict(part.function_call.args or {}),
                thought_signature=part.thought_signature,
            )
            for index, part in enumerate(parts, start=1)
            if part.function_call is not None
        ]
        return AssistantTurn(content=text, tool_calls=calls)

    @staticmethod
    def _to_content(message: dict) -> types.Content:
        if message["role"] == "user":
            return types.Content(role="user", parts=[types.Part.from_text(text=message["content"])])
        if message["role"] == "tool":
            import json

            return types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=message["name"], response=json.loads(message["content"])
                    )
                ],
            )

        parts: list[types.Part] = []
        if message.get("content"):
            parts.append(types.Part.from_text(text=message["content"]))
        for call in message.get("tool_calls", []):
            part = types.Part.from_function_call(name=call["name"], args=call["arguments"])
            part.thought_signature = call.get("thought_signature")
            parts.append(part)
        return types.Content(role="model", parts=parts)
