from app.tools.calculator import calculator
from app.tools.research import research


TOOLS = {
    "calculator": calculator,
    "research": research,
}


def execute_tool(
    tool_name: str,
    arguments: dict,
) -> dict:

    tool = TOOLS.get(tool_name)


    if not tool:

        return {
            "success": False,
            "error": (
                f"Unknown tool: {tool_name}"
            ),
        }


    try:

        result = tool(**arguments)

        return {
            "success": True,
            "tool": tool_name,
            "result": result,
        }


    except Exception as exc:

        return {
            "success": False,
            "tool": tool_name,
            "error": str(exc),
        }