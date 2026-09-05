from app.tools.registry import execute_tool


result = execute_tool(
    "calculator",
    {
        "expression": "250 * 0.18"
    }
)

print(result)