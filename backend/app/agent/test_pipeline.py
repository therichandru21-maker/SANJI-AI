from app.agent.planner import create_plan
from app.agent.executor import execute_plan
from app.agent.context import AgentContext
from app.agent.verifier import AgentVerifier


goal = "Calculate 18% of 250"

print("\n==============================")
print("        SANJI AI")
print("==============================")

# 1. Create context
context = AgentContext(goal)

# 2. Planning
print("\n🧠 PLANNING...")

plan = create_plan(goal)

print("\n📋 PLAN:")
print(plan)

# 3. Execution
print("\n⚙️ EXECUTING...")

execution_result = execute_plan(
    plan,
    context
)

print("\n📊 EXECUTION RESULT:")
print(execution_result)

# 4. Context
print("\n🧠 CONTEXT:")
print(context.build_context())

# 5. Verification
print("\n🔎 VERIFYING...")

verifier = AgentVerifier()

verification = verifier.verify(
    execution_result
)

print("\n✅ VERIFICATION:")
print(verification)

print("\n==============================")
print("     SANJI AI COMPLETE")
print("==============================")