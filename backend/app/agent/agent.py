import json
import logging
import time
import uuid
from typing import Any

from app.agent.context import AgentContext
from app.agent.llm import ask_agent
from app.agent.tools_schema import TOOLS
from app.tools.registry import execute_tool


logger = logging.getLogger("sanji.agent.engine")


MAX_TOOL_ROUNDS = 8


class SanjiAgent:
    """
    Autonomous workflow engine for SANJI AI.

    Flow:

        User Goal
            ↓
        LLM understands goal
            ↓
        Direct answer OR tool call
            ↓
        Tool execution
            ↓
        Result returned to LLM
            ↓
        LLM decides next action
            ↓
        Final answer
    """

    def __init__(self):
        self.agent_version = "3.0.0"


    def run(
        self,
        goal: str,
        conversation: list[dict[str, Any]] | None = None,
    ) -> dict:

        run_id = str(uuid.uuid4())

        started_at = time.perf_counter()

        context = AgentContext(goal)


        # -----------------------------------------------------
        # LOAD PREVIOUS CONVERSATION
        # -----------------------------------------------------

        if conversation:

            for message in conversation:

                role = message.get(
                    "role",
                    "user",
                )

                content = message.get(
                    "content",
                    "",
                )

                if content:
                    context.add_message(
                        role=role,
                        content=content,
                    )


        # -----------------------------------------------------
        # CURRENT USER GOAL
        # -----------------------------------------------------

        context.add_message(
            role="user",
            content=goal,
        )


        logger.info(
            "Agent started | run_id=%s | goal=%s",
            run_id,
            goal,
        )


        execution_log = []


        try:

            messages = list(
                context.get_messages()
            )


            # =================================================
            # AUTONOMOUS WORKFLOW LOOP
            # =================================================

            for round_number in range(
                1,
                MAX_TOOL_ROUNDS + 1,
            ):

                logger.info(
                    "Agent reasoning round | run_id=%s | round=%s",
                    run_id,
                    round_number,
                )


                # -------------------------------------------------
                # ASK LLM
                # -------------------------------------------------

                llm_started = time.perf_counter()


                llm_result = ask_agent(
                    messages=messages,
                    tools=TOOLS,
                )


                llm_duration = round(
                    (
                        time.perf_counter()
                        - llm_started
                    )
                    * 1000,
                    2,
                )


                # -------------------------------------------------
                # LLM FAILURE
                # -------------------------------------------------

                if not llm_result.get(
                    "success"
                ):

                    error = llm_result.get(
                        "error",
                        "LLM request failed.",
                    )


                    logger.error(
                        "LLM failure | run_id=%s | error=%s",
                        run_id,
                        error,
                    )


                    return self._failure_response(
                        run_id=run_id,
                        goal=goal,
                        error=error,
                        execution_log=execution_log,
                        started_at=started_at,
                    )


                tool_calls = (
                    llm_result.get(
                        "tool_calls",
                        [],
                    )
                )


                assistant_text = (
                    llm_result.get(
                        "text",
                        "",
                    )
                )


                # =================================================
                # NO TOOL REQUIRED → FINAL ANSWER
                # =================================================

                if not tool_calls:

                    final_text = (
                        assistant_text.strip()
                    )


                    if not final_text:

                        final_text = (
                            "I completed the request, "
                            "but no response was generated."
                        )


                    context.add_message(
                        role="assistant",
                        content=final_text,
                    )


                    execution_log.append(
                        {
                            "round": round_number,
                            "type": "final_response",
                            "status": "completed",
                            "duration_ms": llm_duration,
                        }
                    )


                    total_duration = round(
                        (
                            time.perf_counter()
                            - started_at
                        )
                        * 1000,
                        2,
                    )


                    logger.info(
                        "Agent completed | run_id=%s | duration=%sms",
                        run_id,
                        total_duration,
                    )


                    return {
                        "run_id": run_id,
                        "status": "completed",
                        "goal": goal,
                        "final_answer": final_text,

                        "execution": {
                            "rounds": round_number,

                            "tool_calls": sum(
                                1
                                for item
                                in execution_log
                                if item.get(
                                    "type"
                                )
                                == "tool_call"
                            ),

                            "duration_ms": total_duration,
                        },

                        "logs": execution_log,

                        "context": context.build_context(),

                        "agent_version": self.agent_version,
                    }


                # =================================================
                # TOOL EXECUTION
                # =================================================

                for tool_call in tool_calls:

                    tool_name = tool_call.get(
                        "name"
                    )

                    arguments = tool_call.get(
                        "arguments",
                        {},
                    )

                    call_id = tool_call.get(
                        "call_id"
                    )


                    # -------------------------------------------------
                    # VALIDATE TOOL NAME
                    # -------------------------------------------------

                    if not tool_name:

                        logger.error(
                            "Tool name missing | run_id=%s",
                            run_id,
                        )

                        continue


                    # -------------------------------------------------
                    # PARSE ARGUMENTS
                    # -------------------------------------------------

                    if isinstance(
                        arguments,
                        str,
                    ):

                        try:

                            parsed_arguments = (
                                json.loads(
                                    arguments
                                )
                            )

                        except json.JSONDecodeError:

                            parsed_arguments = {}

                    elif isinstance(
                        arguments,
                        dict,
                    ):

                        parsed_arguments = arguments

                    else:

                        parsed_arguments = {}


                    logger.info(
                        "Tool requested | run_id=%s | tool=%s",
                        run_id,
                        tool_name,
                    )


                    # -------------------------------------------------
                    # EXECUTE TOOL
                    # -------------------------------------------------

                    tool_started = (
                        time.perf_counter()
                    )


                    try:

                        tool_output = execute_tool(
                            tool_name,
                            parsed_arguments,
                        )

                    except Exception as exc:

                        logger.exception(
                            "Tool execution failed | tool=%s",
                            tool_name,
                        )

                        tool_output = {
                            "success": False,
                            "tool": tool_name,
                            "error": str(exc),
                        }


                    tool_duration = round(
                        (
                            time.perf_counter()
                            - tool_started
                        )
                        * 1000,
                        2,
                    )


                    # -------------------------------------------------
                    # TOOL RESULT
                    # -------------------------------------------------

                    tool_success = bool(
                        tool_output.get(
                            "success"
                        )
                    )


                    tool_result = (
                        tool_output.get(
                            "result"
                        )
                    )


                    tool_error = (
                        tool_output.get(
                            "error"
                        )
                    )


                    # -------------------------------------------------
                    # SAVE CONTEXT
                    # -------------------------------------------------

                    context.add_result(
                        task_id=(
                            call_id
                            or len(
                                execution_log
                            )
                            + 1
                        ),

                        description=(
                            f"Tool call: "
                            f"{tool_name}"
                        ),

                        tool=tool_name,

                        result=(
                            tool_result
                            if tool_success
                            else tool_error
                        ),
                    )


                    # -------------------------------------------------
                    # EXECUTION LOG
                    # -------------------------------------------------

                    execution_log.append(
                        {
                            "round": round_number,
                            "type": "tool_call",
                            "tool": tool_name,

                            "status": (
                                "completed"
                                if tool_success
                                else "failed"
                            ),

                            "duration_ms": tool_duration,

                            "error": tool_error,
                        }
                    )


                    # =================================================
                    # SEND TOOL CALL + RESULT BACK TO LLM
                    # =================================================

                    function_arguments = json.dumps(
                        parsed_arguments,
                        ensure_ascii=False,
                    )


                    messages.append(
                        {
                            "type": "function_call",
                            "call_id": call_id,
                            "name": tool_name,
                            "arguments": function_arguments,
                        }
                    )


                    messages.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": self._serialize_tool_output(
                                tool_output
                            ),
                        }
                    )


                    logger.info(
                        "Tool completed | run_id=%s | tool=%s | success=%s",
                        run_id,
                        tool_name,
                        tool_success,
                    )


            # =================================================
            # MAX ROUNDS EXCEEDED
            # =================================================

            return self._failure_response(
                run_id=run_id,
                goal=goal,
                error=(
                    "The workflow exceeded the "
                    "maximum number of tool rounds."
                ),
                execution_log=execution_log,
                started_at=started_at,
            )


        except Exception as exc:

            logger.exception(
                "Unexpected agent error | run_id=%s",
                run_id,
            )


            return self._failure_response(
                run_id=run_id,
                goal=goal,
                error=str(exc),
                execution_log=execution_log,
                started_at=started_at,
            )


    # =========================================================
    # SERIALIZE TOOL OUTPUT
    # =========================================================

    @staticmethod
    def _serialize_tool_output(
        output: dict,
    ) -> str:

        try:

            return json.dumps(
                output,
                ensure_ascii=False,
            )

        except Exception:

            return str(output)


    # =========================================================
    # FAILURE RESPONSE
    # =========================================================

    @staticmethod
    def _failure_response(
        run_id: str,
        goal: str,
        error: str,
        execution_log: list,
        started_at: float,
    ):

        duration = round(
            (
                time.perf_counter()
                - started_at
            )
            * 1000,
            2,
        )


        return {
            "run_id": run_id,

            "status": "failed",

            "goal": goal,

            "final_answer": (
                "I couldn't complete that request "
                "right now.\n\n"
                f"Reason: {error}"
            ),

            "error": error,

            "execution": {
                "duration_ms": duration,
            },

            "logs": execution_log,

            "agent_version": "3.0.0",
        }