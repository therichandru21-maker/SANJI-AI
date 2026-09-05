from app.tools.registry import execute_tool


result = execute_tool(
    "research",
    {
        "query": "Artificial intelligence"
    }
)

print("\n==============================")
print("SANJI AI RESEARCH TOOL")
print("==============================")

print(result)