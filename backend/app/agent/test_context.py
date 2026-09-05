from app.agent.context import AgentContext


context = AgentContext(
    "Research AI and calculate a percentage"
)

context.add_result(
    task_id=1,
    description="Research artificial intelligence",
    tool="research",
    result="AI is the capability of computational systems..."
)

context.add_result(
    task_id=2,
    description="Calculate percentage",
    tool="calculator",
    result=45
)

print("\n==============================")
print("SANJI AI CONTEXT")
print("==============================")

print("\n📌 Full Context:")
print(context.build_context())

print("\n📌 Last Result:")
print(context.get_last_result())