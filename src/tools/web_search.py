from __future__ import annotations

import re
import urllib.parse
import urllib.request


def web_search(query: str) -> str:
    """Search DuckDuckGo for the query and return the top 3 snippet results."""
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0.0.0 Safari/537.36"
            )
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode("utf-8")

        # Find results container and pull text snippets.
        # DDG HTML structures results in class="result__snippet"
        snippets = re.findall(
            r'<a class="result__snippet"[^>]*>(.*?)</a>',
            html,
            re.DOTALL,
        )
        titles = re.findall(
            r'<a class="result__url"[^>]*>(.*?)</a>',
            html,
            re.DOTALL,
        )

        if not snippets:
            return "No results found."

        results = []
        for i, snippet in enumerate(snippets[:3]):
            # Clean HTML tags and entities
            clean_snippet = re.sub(r"<[^>]+>", "", snippet).strip()
            clean_snippet = (
                clean_snippet.replace("&amp;", "&")
                .replace("&quot;", '"')
                .replace("&#x27;", "'")
            )
            title = titles[i] if i < len(titles) else "Result"
            clean_title = re.sub(r"<[^>]+>", "", title).strip()
            results.append(f"{i+1}. {clean_title}\n   {clean_snippet}")

        return "\n\n".join(results)

    except Exception as e:
        return f"Error performing search: {e}"


# Ollama schema definition
WEB_SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "Search the web for up-to-date information, news, facts, "
            "or detailed answers to questions."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up on the web.",
                }
            },
            "required": ["query"],
        },
    },
}
