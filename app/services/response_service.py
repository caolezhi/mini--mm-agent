from app.db import (
    clear_session,
    get_previous_response_id,
    save_message,
    set_previous_response_id,
)
from app.llm import create_model_response, create_model_stream


async def respond(session_id: str, user_input: str):
    """Create a normal, non-streaming model response for one session."""
    previous_response_id = get_previous_response_id(session_id)

    response = await create_model_response(
        user_input,
        previous_response_id=previous_response_id,
    )

    reply = response.output_text

    save_message(session_id, "user", user_input)
    save_message(session_id, "assistant", reply)
    set_previous_response_id(session_id, response.id)

    return reply


async def stream_respond(session_id: str, user_input: str):
    """Yield text deltas while also saving the completed response locally."""
    previous_response_id = get_previous_response_id(session_id)

    save_message(session_id, "user", user_input)

    stream = await create_model_stream(
        user_input,
        previous_response_id=previous_response_id,
    )

    full_reply = ""
    completed_response_id = None

    async for event in stream:
        if event.type == "response.output_text.delta":
            full_reply += event.delta
            yield event.delta

        elif event.type == "response.completed":
            completed_response_id = event.response.id

    save_message(session_id, "assistant", full_reply)

    if completed_response_id:
        set_previous_response_id(
            session_id,
            completed_response_id,
        )


def reset_response_session(session_id: str):
    clear_session(session_id)
