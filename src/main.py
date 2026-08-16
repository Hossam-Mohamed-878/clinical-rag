import re

from agent.client import OllamaClient
from tools.web_search import WEB_SEARCH_TOOL_SCHEMA, web_search


def main() -> None:
    agent = OllamaClient()
    tools = [WEB_SEARCH_TOOL_SCHEMA]
    tool_map = {
        "web_search": web_search,
    }
    MAX_ITERATIONS = 10

    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Keep your answers short, concise and to the point. "
                "Dont think more than 10 seconds. "
            ),
        },
    ]

    print("Agent ready. Ask about weather or time. Type 'exit' to quit.")

    while True:
        user_input = input("\nYou >>> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        messages.append({"role": "user", "content": user_input})

        # Keep going until the model stops asking for tools.
        for _ in range(MAX_ITERATIONS):
            last_message = None

            content_buffer = ""
            thinking_buffer = ""

            full_content = ""
            full_thinking = ""

            try:
                for msg in agent.chat_stream(messages, tools=tools):
                    thinking = getattr(msg, "thinking", None)
                    if thinking:
                        full_thinking += thinking
                        thinking_buffer += thinking.replace("\r", "")

                        while "\n" in thinking_buffer:
                            line, thinking_buffer = thinking_buffer.split("\n", 1)
                            line = line.strip()
                            if line:
                                print(f"Agent >>> [thinking] {line}", flush=True)

                    content = getattr(msg, "content", None)
                    if content:
                        full_content += content
                        content_buffer += content

                        parts = re.split(r"(?<=[.!?])\s+", content_buffer)
                        if len(parts) > 1:
                            for sentence in parts[:-1]:
                                sentence = sentence.strip()
                                if sentence:
                                    print(f"Agent >>> {sentence}", flush=True)
                            content_buffer = parts[-1]

                    last_message = msg

                if thinking_buffer.strip():
                    print(f"Agent >>> [thinking] {thinking_buffer.strip()}", flush=True)

                if content_buffer.strip():
                    print(f"Agent >>> {content_buffer.strip()}", flush=True)

            except Exception as exc:
                print(f"\nAgent stream error: {exc}")
                break

            if last_message is None and not full_content and not full_thinking:
                print("Agent >>> (no response)")
                break

            assistant_message = {
                "role": "assistant",
                "content": full_content,
            }

            if full_thinking:
                assistant_message["thinking"] = full_thinking

            tool_calls = getattr(last_message, "tool_calls", None) if last_message else None
            if tool_calls:
                assistant_message["tool_calls"] = tool_calls

            messages.append(assistant_message)

            if not tool_calls:
                break

            for call in tool_calls:
                func = tool_map.get(call.function.name)

                if func is None:
                    result = f"Error: unknown tool {call.function.name}"
                else:
                    try:
                        result = func(**call.function.arguments)
                    except Exception as error:
                        result = f"Tool error: {error}"

                print(f"[tool] {call.function.name}({call.function.arguments}) -> {result}")

                messages.append(
                    {
                        "role": "tool",
                        "name": call.function.name,
                        "content": str(result),
                    }
                )
        else:
            print("Agent >>> (stopped: too many tool rounds)")


if __name__ == "__main__":
    main()