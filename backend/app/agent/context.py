"""
SANJI AI - Context Manager

Maintains conversation history, tool results and metadata
for the current agent session.
"""

from typing import Any


class AgentContext:

    def __init__(self, goal: str):
        self.goal = goal

        self.messages: list[dict[str, Any]] = []

        self.results: list[dict[str, Any]] = []

        self.metadata: dict[str, Any] = {}

    # ---------------------------------------------------------
    # Conversation
    # ---------------------------------------------------------

    def add_message(
        self,
        role: str,
        content: str,
    ):
        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    def get_messages(self):
        return self.messages

    # ---------------------------------------------------------
    # Tool results
    # ---------------------------------------------------------

    def add_result(
        self,
        task_id: int | str,
        description: str,
        tool: str,
        result: Any,
    ):
        self.results.append(
            {
                "task_id": task_id,
                "description": description,
                "tool": tool,
                "result": result,
            }
        )

    def get_results(self):
        return self.results

    def get_last_result(self):
        if not self.results:
            return None

        return self.results[-1]

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    def set_metadata(
        self,
        key: str,
        value: Any,
    ):
        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
    ):
        return self.metadata.get(key)

    # ---------------------------------------------------------
    # Full context
    # ---------------------------------------------------------

    def build_context(self):
        return {
            "goal": self.goal,
            "messages": self.messages,
            "results": self.results,
            "metadata": self.metadata,
        }