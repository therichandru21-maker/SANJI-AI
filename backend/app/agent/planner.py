"""
SANJI AI - Workflow Planner

Converts a user's goal into a structured multi-step workflow.
Local intent detection is used temporarily while external LLM
credits are unavailable.
"""


def create_plan(goal: str) -> dict:
    """
    Analyze the user's goal and create an executable workflow.
    """

    goal_lower = goal.lower().strip()

    # ============================================================
    # 1. RESEARCH + CALCULATION WORKFLOW
    #    IMPORTANT: This must come BEFORE standalone workflows.
    # ============================================================

    has_research = any(keyword in goal_lower for keyword in [
        "research",
        "find information",
        "learn about",
        "tell me about",
        "information about",
        "explain"
    ])

    has_calculation = any(keyword in goal_lower for keyword in [
        "calculate",
        "percentage",
        "percent",
        "multiply",
        "divide",
        "addition",
        "add",
        "subtract",
        "minus",
        "plus"
    ])

    if has_research and has_calculation:

        tasks = []

        # Task 1 — Research
        research_query = extract_research_query(goal)

        tasks.append({
            "id": 1,
            "description": f"Research information about {research_query}",
            "tool": "research",
            "arguments": {
                "query": research_query
            }
        })

        # Task 2 — Calculation
        expression = detect_calculation(goal_lower)

        if expression:
            tasks.append({
                "id": 2,
                "description": "Calculate the requested value",
                "tool": "calculator",
                "arguments": {
                    "expression": expression
                }
            })

        # Final task
        tasks.append({
            "id": len(tasks) + 1,
            "description": "Combine the workflow results into a final response",
            "tool": "none",
            "arguments": {}
        })

        return {
            "goal": goal,
            "strategy": "research_and_calculation",
            "tasks": tasks
        }

    # ============================================================
    # 2. CALCULATOR WORKFLOW
    # ============================================================

    if has_calculation:

        expression = detect_calculation(goal_lower)

        if expression:

            return {
                "goal": goal,
                "strategy": "calculation_workflow",
                "tasks": [
                    {
                        "id": 1,
                        "description": "Calculate the requested value",
                        "tool": "calculator",
                        "arguments": {
                            "expression": expression
                        }
                    },
                    {
                        "id": 2,
                        "description": "Prepare the final response using the calculated result",
                        "tool": "none",
                        "arguments": {}
                    }
                ]
            }

    # ============================================================
    # 3. RESEARCH WORKFLOW
    # ============================================================

    if has_research:

        query = extract_research_query(goal)

        return {
            "goal": goal,
            "strategy": "research_workflow",
            "tasks": [
                {
                    "id": 1,
                    "description": f"Research information about {query}",
                    "tool": "research",
                    "arguments": {
                        "query": query
                    }
                },
                {
                    "id": 2,
                    "description": "Analyze and summarize the research findings",
                    "tool": "none",
                    "arguments": {}
                }
            ]
        }

    # ============================================================
    # 4. GENERIC WORKFLOW
    # ============================================================

    return {
        "goal": goal,
        "strategy": "general_workflow",
        "tasks": [
            {
                "id": 1,
                "description": "Understand and analyze the user's request",
                "tool": "none",
                "arguments": {}
            },
            {
                "id": 2,
                "description": "Prepare a structured response",
                "tool": "none",
                "arguments": {}
            }
        ]
    }


# ================================================================
# CALCULATION DETECTOR
# ================================================================

def detect_calculation(goal: str):
    """
    Detect common percentage calculations.
    """

    import re

    # Example:
    # 18% of 250
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*%\s*(?:of)\s*(\d+(?:\.\d+)?)",
        goal
    )

    if match:

        percentage = float(match.group(1))
        number = float(match.group(2))

        return f"{number} * {percentage / 100}"


    # Example:
    # 20 percent of 500
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*percent\s*(?:of)\s*(\d+(?:\.\d+)?)",
        goal
    )

    if match:

        percentage = float(match.group(1))
        number = float(match.group(2))

        return f"{number} * {percentage / 100}"


    return None


# ================================================================
# RESEARCH QUERY EXTRACTOR
# ================================================================

def extract_research_query(goal: str) -> str:
    """
    Extract a useful research topic from the user's goal.
    """

    prefixes = [
        "research",
        "find information about",
        "learn about",
        "tell me about",
        "information about",
        "explain"
    ]

    cleaned = goal.strip()

    for prefix in prefixes:

        if cleaned.lower().startswith(prefix):

            cleaned = cleaned[len(prefix):].strip()

            cleaned = cleaned.lstrip(":")
            cleaned = cleaned.strip()

            # Remove calculation portion when present
            calculation_markers = [
                " and calculate",
                " and find",
                ", calculate",
                " calculate"
            ]

            for marker in calculation_markers:

                marker_index = cleaned.lower().find(marker)

                if marker_index != -1:
                    cleaned = cleaned[:marker_index].strip()

            if cleaned:
                return cleaned

    return cleaned