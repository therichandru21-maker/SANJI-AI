class AgentVerifier:
    """
    Verifies whether SANJI AI completed its workflow successfully.

    The verifier checks:
    - Task completion
    - Task failures
    - Execution consistency
    - Workflow duration
    - Individual tool execution
    """

    def verify(self, execution_result: dict) -> dict:
        """
        Validate the complete workflow execution.
        """

        results = execution_result.get("results", [])

        total_tasks = execution_result.get(
            "total_tasks",
            len(results)
        )

        executed_tasks = execution_result.get(
            "executed_tasks",
            len(results)
        )

        completed_tasks = execution_result.get(
            "completed_tasks",
            0
        )

        failed_tasks = execution_result.get(
            "failed_tasks",
            0
        )

        duration_ms = execution_result.get(
            "duration_ms",
            0
        )

        # ========================================================
        # NO TASKS
        # ========================================================

        if not results:

            return {
                "verified": False,
                "status": "failed",
                "message": "No tasks were executed.",
                "checks": {
                    "tasks_executed": False,
                    "tasks_completed": False,
                    "no_failures": False,
                    "execution_consistent": False,
                },
                "metrics": {
                    "total_tasks": total_tasks,
                    "executed_tasks": executed_tasks,
                    "completed_tasks": completed_tasks,
                    "failed_tasks": failed_tasks,
                    "duration_ms": duration_ms,
                },
                "failed_tasks": [],
            }

        # ========================================================
        # FIND FAILED TASKS
        # ========================================================

        failed_task_details = [
            result
            for result in results
            if result.get("status") != "completed"
        ]

        # ========================================================
        # CHECKS
        # ========================================================

        tasks_executed = executed_tasks > 0

        tasks_completed = (
            completed_tasks == executed_tasks
        )

        no_failures = (
            failed_tasks == 0
            and len(failed_task_details) == 0
        )

        execution_consistent = (
            executed_tasks <= total_tasks
            and completed_tasks + failed_tasks == executed_tasks
        )

        all_verified = (
            tasks_executed
            and tasks_completed
            and no_failures
            and execution_consistent
        )

        # ========================================================
        # TOOL VERIFICATION
        # ========================================================

        tool_checks = []

        for result in results:

            tool_name = result.get(
                "tool",
                "unknown"
            )

            status = result.get(
                "status",
                "unknown"
            )

            tool_checks.append({
                "task_id": result.get("task_id"),
                "tool": tool_name,
                "status": status,
                "verified": status == "completed",
            })

        # ========================================================
        # OVERALL STATUS
        # ========================================================

        if all_verified:

            status = "verified"

            message = (
                "All workflow tasks completed successfully "
                "and passed verification."
            )

        elif failed_tasks > 0:

            status = "failed"

            message = (
                "Workflow verification failed because "
                "one or more tasks failed."
            )

        else:

            status = "partial"

            message = (
                "Workflow completed partially and requires "
                "further verification."
            )

        # ========================================================
        # FINAL VERIFICATION REPORT
        # ========================================================

        return {
            "verified": all_verified,
            "status": status,
            "message": message,

            "checks": {
                "tasks_executed": tasks_executed,
                "tasks_completed": tasks_completed,
                "no_failures": no_failures,
                "execution_consistent": execution_consistent,
            },

            "metrics": {
                "total_tasks": total_tasks,
                "executed_tasks": executed_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "duration_ms": duration_ms,
            },

            "tool_checks": tool_checks,

            "failed_tasks": failed_task_details,
        }