from app.agent.planner import create_plan
from app.agent.executor import execute_plan


goal = "Calculate 18% of 250"

print("\n==============================")
print("SANJI AI")
print("==============================")

print("\n🧠 Creating plan...")

plan = create_plan(goal)

print("\n📋 PLAN:")
print(plan)

print("\n⚙️ Executing plan...")

result = execute_plan(plan)

print("\n✅ EXECUTION RESULT:")
print(result)