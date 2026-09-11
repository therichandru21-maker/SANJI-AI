# backend/app/tools/research.py

import logging
from typing import Any

from groq import Groq

from app.config import GROQ_API_KEY


logger = logging.getLogger("sanji.tool.research")


client = Groq(
    api_key=GROQ_API_KEY,
    timeout=90.0,
)


MODEL = "groq/compound"


def research(query: str) -> dict[str, Any]:
    """
    Live web research tool using Groq Compound.

    Groq Compound provides server-side web search and
    returns the final researched answer.
    """

    if not query or not query.strip():

        return {
            "success": False,
            "error": "Research query cannot be empty.",
        }

    query = query.strip()

    if len(query) > 2000:

        return {
            "success": False,
            "error": "Research query is too long.",
        }

    logger.info(
        "Groq web research started | query=%s",
        query,
    )

    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "user",
                    "content": (
                        "Research the following topic using "
                        "the web and provide an accurate, "
                        "concise answer.\n\n"
                        f"Research request:\n{query}\n\n"
                        "Instructions:\n"
                        "- Use current web information when relevant.\n"
                        "- Prefer reliable sources.\n"
                        "- Cross-check important facts when possible.\n"
                        "- Clearly explain the findings.\n"
                        "- Do not mention internal tool execution."
                    ),
                }
            ],

            compound_custom={
                "tools": {
                    "enabled_tools": [
                        "web_search",
                        "visit_website",
                    ]
                }
            },
        )

        message = response.choices[0].message

        result_text = (
            message.content
            or ""
        ).strip()

        if not result_text:

            return {
                "success": False,
                "query": query,
                "error": (
                    "The Groq web research service "
                    "returned no readable result."
                ),
            }

        logger.info(
            "Groq web research completed | query=%s",
            query,
        )

        return {
            "success": True,
            "query": query,
            "result": result_text,
            "source": "Groq Web Search",
        }

    except Exception as exc:

        logger.exception(
            "Groq web research failed | query=%s",
            query,
        )

        return {
            "success": False,
            "query": query,
            "error": (
                "Web research failed: "
                f"{str(exc)}"
            ),
        }