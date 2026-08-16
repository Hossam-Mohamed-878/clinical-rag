import os
from dataclasses import dataclass, field

from ollama import Client

DEFAULT_MODEL = os.getenv("WORKING_MODEL", "qwen3.5:9b")
DEFAULT_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

@dataclass
class OllamaClient:
    model: str = DEFAULT_MODEL
    client: Client = field(default=Client(host=DEFAULT_HOST), repr=False)
    
    def __post_init__(self):
        if self.client is None:
            self.client = Client()

    def chat(self, messages, tools=None):
        """Send the message history to the model and return one response.

        The model does not remember previous requests by itself.

        To continue a conversation, we send the message history again
        with every request.
        """

        response = self.client.chat(  
            model=self.model,
            messages=messages,
            tools=tools,
            think= "low",
            options={"temperature": 1},
        )

        return response

    def chat_stream(self, messages, tools=None):
        """Send the message history and yield the response piece by piece.

        Streaming lets us display text as it is generated instead of
        waiting for the complete response.
        """

        stream = self.client.chat(
            model=self.model,
            messages=messages,
            tools= tools,
            think="low",
            stream=True,
        )

        for chunk in stream:
            yield chunk.message     