from __future__ import annotations

from typing import Generator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from agent.client import OllamaClient
from api.core.config import settings
from api.schemas.chat import ChatRequest, StreamEvent
from tools.web_search import WEB_SEARCH_TOOL_SCHEMA, web_search

router = APIRouter(prefix="/api", tags=["chat"])

# Shared client instance (one per worker process).
_client = OllamaClient(model=settings.working_model)

# Register available tools
_tools = [WEB_SEARCH_TOOL_SCHEMA]
_tool_map = {
    "web_search": web_search,
}


def _stream_events(messages: list[dict]) -> Generator[str, None, None]:
    """Synchronous generator that yields SSE-formatted strings.

    Runs in a threadpool (sync route), so blocking ollama I/O is safe.
    Handles tool resolution loops.
    """
    MAX_ITERATIONS = 10
    current_messages = list(messages)

    try:
        for _ in range(MAX_ITERATIONS):
            last_message = None
            full_content = ""
            full_thinking = ""

            # Stream response from Ollama
            for msg in _client.chat_stream(current_messages, tools=_tools):
                thinking = getattr(msg, "thinking", None)
                if thinking:
                    full_thinking += thinking
                    event = StreamEvent(type="thinking", data=thinking)
                    yield f"data: {event.model_dump_json()}\n\n"

                content = getattr(msg, "content", None)
                if content:
                    full_content += content
                    event = StreamEvent(type="content", data=content)
                    yield f"data: {event.model_dump_json()}\n\n"

                last_message = msg

            # Prep message structure for history
            assistant_message = {
                "role": "assistant",
                "content": full_content,
            }
            if full_thinking:
                assistant_message["thinking"] = full_thinking

            tool_calls = getattr(last_message, "tool_calls", None) if last_message else None
            if tool_calls:
                assistant_message["tool_calls"] = tool_calls

            current_messages.append(assistant_message)

            if not tool_calls:
                break

            # Process tool calls
            for call in tool_calls:
                func = _tool_map.get(call.function.name)
                if func is None:
                    result = f"Error: unknown tool {call.function.name}"
                else:
                    # Inform user agent is running a tool inside the thinking block
                    query_arg = call.function.arguments.get("query", "")
                    tool_info = f"\n[Searching the web for: '{query_arg}']\n"
                    yield f"data: {StreamEvent(type='thinking', data=tool_info).model_dump_json()}\n\n"
                    
                    try:
                        result = func(**call.function.arguments)
                    except Exception as error:
                        result = f"Tool error: {error}"

                # Append tool result to the conversation history
                current_messages.append(
                    {
                        "role": "tool",
                        "name": call.function.name,
                        "content": str(result),
                    }
                )

        yield f"data: {StreamEvent(type='done').model_dump_json()}\n\n"

    except Exception as exc:  # noqa: BLE001
        yield f"data: {StreamEvent(type='error', data=str(exc)).model_dump_json()}\n\n"


@router.post("/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    """Stream assistant response as Server-Sent Events.

    Each event line has the shape:
        data: {"type": "thinking"|"content"|"done"|"error", "data": "..."}
    """
    messages = [
        msg.model_dump(exclude_none=True) for msg in request.messages
    ]

    return StreamingResponse(
        _stream_events(messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

