import asyncio
import inspect
import json
import logging

from app.db import (
    get_previous_response_id,
    save_message,
    set_previous_response_id,
)
from app.llm import create_model_response
from app.tools import TOOL_DEFINITIONS, TOOL_REGISTRY


logger = logging.getLogger(__name__)


AGENT_INSTRUCTIONS = (
    "你是一个AI Agent。"
    "需要工具时必须使用提供的工具，不要编造工具执行结果。"
    "调用工具时必须提供工具定义中的必需参数。"
    "如果工具返回错误，请根据错误信息修正并继续。"
    "数学计算、数据处理或算法任务可以使用run_python。"
)


async def execute_tool(tool_call):
    """Translate one model function_call into a real Python function call."""
    tool_name = tool_call.name

    try:
        tool_arguments = json.loads(tool_call.arguments or "{}")
    except json.JSONDecodeError:
        return "工具参数不是合法JSON，请重新调用工具。"

    logger.info(
        "执行工具 name=%s arguments=%s",
        tool_name,
        tool_arguments,
    )

    tool_function = TOOL_REGISTRY.get(tool_name)

    if tool_function is None:
        return f"未知工具：{tool_name}"

    # Even with a strict JSON schema, checking required Python parameters here
    # makes the executor more robust when using third-party compatible APIs.
    signature = inspect.signature(tool_function)
    missing_arguments = []

    for name, parameter in signature.parameters.items():
        if (
            parameter.default is inspect.Parameter.empty
            and name not in tool_arguments
        ):
            missing_arguments.append(name)

    if missing_arguments:
        return (
            f"工具 {tool_name} 缺少必需参数："
            f"{missing_arguments}。请补齐参数后重新调用。"
        )

    try:
        # Tool functions are synchronous. Run them in a worker thread so a slow
        # network call such as E2B does not block FastAPI's event loop.
        result = await asyncio.to_thread(
            tool_function,
            **tool_arguments,
        )
    except Exception as error:
        logger.exception("工具执行失败 name=%s", tool_name)
        return f"工具执行失败：{error}"

    logger.info(
        "工具执行完成 name=%s result=%s",
        tool_name,
        result,
    )

    return result


async def run_agent(
    session_id: str,
    user_input: str,
    max_steps: int = 10,
):
    """Minimal Agent Loop: model -> tools -> model until no tool is requested."""
    previous_response_id = get_previous_response_id(session_id)

    response = await create_model_response(
        user_input,
        instructions=AGENT_INSTRUCTIONS,
        previous_response_id=previous_response_id,
        tools=TOOL_DEFINITIONS,
    )

    for step in range(max_steps):
        logger.info("Agent step=%s", step + 1)

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # No function_call means the model believes the task is complete.
        if not tool_calls:
            reply = response.output_text

            save_message(session_id, "user", user_input)
            save_message(session_id, "assistant", reply)
            set_previous_response_id(session_id, response.id)

            return reply

        tool_outputs = []

        for tool_call in tool_calls:
            tool_result = await execute_tool(tool_call)

            # call_id tells the model which function_call this result belongs to.
            tool_outputs.append({
                "type": "function_call_output",
                "call_id": tool_call.call_id,
                "output": str(tool_result),
            })

        # Continue from the response that requested the tools. The model now sees
        # the real tool results and can either call more tools or answer.
        response = await create_model_response(
            tool_outputs,
            instructions=AGENT_INSTRUCTIONS,
            previous_response_id=response.id,
            tools=TOOL_DEFINITIONS,
        )

    set_previous_response_id(session_id, response.id)
    return "任务执行步骤过多，已停止。"
