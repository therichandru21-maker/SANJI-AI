TOOLS = [

    # =========================================================
    # CALCULATOR
    # =========================================================

    {
        "type": "function",

        "name": "calculator",

        "description": (
            "Perform accurate mathematical calculations safely. "
            "Use this tool whenever arithmetic, percentages, "
            "equations or numerical calculations need reliable results."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "expression": {

                    "type": "string",

                    "description": (
                        "A mathematical expression such as "
                        "'250 * 0.18', "
                        "'(50 + 20) / 2', "
                        "or '1000 * 1.18'."
                    ),
                }
            },

            "required": [
                "expression"
            ],

            "additionalProperties": False,
        },

        "strict": True,
    },


    # =========================================================
    # RESEARCH
    # =========================================================

    {
        "type": "function",

        "name": "research",

        "description": (
            "Research a topic using an external information source. "
            "Use this when the user asks to research something or "
            "when external information is useful for answering the goal."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "query": {

                    "type": "string",

                    "description": (
                        "The exact topic or question that should be researched."
                    ),
                }
            },

            "required": [
                "query"
            ],

            "additionalProperties": False,
        },

        "strict": True,
    },

]