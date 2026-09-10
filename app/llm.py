from openai import AsyncOpenAI

from app.config import API_KEY, BASE_URL, MODEL_NAME


client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


DEFAULT_INSTRUCTIONS = (
    "你是一个简洁、清楚的AI助手。"
    "如果涉及代码，请解释为什么这样写。"
)


async def create_model_response(
    input_data,
    *,
    instructions: str = DEFAULT_INSTRUCTIONS,
    previous_response_id: str | None = None,
    tools=None,
):
    """Create one Responses API response.

    This file acts as a tiny LLM gateway: the rest of the project does not need
    to know how the SDK is initialized or which base URL is used.
    """
    kwargs = {
        "model": MODEL_NAME,
        "instructions": instructions,
        "input": input_data,
    }

    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id

    if tools:
        kwargs["tools"] = tools

    return await client.responses.create(**kwargs)


async def create_model_stream(
    input_data,
    *,
    instructions: str = DEFAULT_INSTRUCTIONS,
    previous_response_id: str | None = None,
):
    """Create a streaming Responses API request."""
    kwargs = {
        "model": MODEL_NAME,
        "instructions": instructions,
        "input": input_data,
        "stream": True,
    }

    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id

    return await client.responses.create(**kwargs)
