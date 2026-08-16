from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class Message(BaseModel):
    """A single turn in the conversation."""

    role: Literal["user", "assistant", "system", "tool"]
    content: str
    thinking: Optional[str] = None


class ChatRequest(BaseModel):
    """Incoming payload for POST /api/chat."""

    messages: list[Message]


class StreamEvent(BaseModel):
    """One SSE event sent to the client."""

    type: Literal["thinking", "content", "done", "error"]
    data: Optional[str] = None
