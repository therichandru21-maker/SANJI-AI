import logging
from typing import Any

from openai import OpenAI

from app.config import OPENAI_API_KEY


logger = logging.getLogger("sanji.tool.research")


client = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=90.0,
    max_retries=2,
)


MODEL = "gpt-5.6-luna"


def research(query: str) -> dict[str, Any]:
    """
    Live web research tool.

    Uses OpenAI's built-in web search capability to find
    current information from the internet.
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
        "Web research started | query=%s",
        query,
    )


    try:

        response = client.responses.create(

            model=MODEL,

            tools=[
                {
                    "type": "web_search",
                }
            ],

            input=(
                "Research the following topic using the web.\n\n"
                f"User research request:\n{query}\n\n"
                "Instructions:\n"
                "- Prefer reliable and relevant sources.\n"
                "- Prioritize recent information when the topic is time-sensitive.\n"
                "- Cross-check important facts when possible.\n"
                "- Give a concise factual summary.\n"
                "- Do not mention internal tool execution.\n"
            ),
        )


        result_text = (
            response.output_text or ""
        ).strip()


        if not result_text:

            return {
                "success": False,
                "query": query,
                "error": (
                    "The web research service returned "
                    "no readable result."
                ),
            }


        logger.info(
            "Web research completed | query=%s",
            query,
        )


        return {
            "success": True,
            "query": query,
            "result": result_text,
            "source": "Web Search",
        }


    except Exception as exc:

        logger.exception(
            "Web research failed | query=%s",
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