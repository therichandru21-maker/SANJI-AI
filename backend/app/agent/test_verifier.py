from app.agent.verifier import AgentVerifier

verifier = AgentVerifier()

execution_result = {
    "status": "completed",
    "total_tasks": 2,
    "results": [
        {
            "task_id": 1,
            "description": "Calculate percentage",
            "tool": "calculator",
            "status": "completed",
            "result": 45
        },
        {
            "task_id": 2,
            "description": "Prepare final response",
            "tool": "none",
            "status": "completed",
            "result": "No tool required."
        }
    ]
}

print("\n==============================")
print("SANJI AI VERIFIER")
print("==============================")

verification = verifier.verify(execution_result)

print("\n🔎 Verification Result:")
print(verification)