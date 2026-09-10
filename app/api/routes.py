import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.agent_service import run_agent
from app.services.response_service import (
    reset_response_session,
    respond,
    stream_respond,
)


router = APIRouter()
logger = logging.getLogger(__name__)


class ResponseRequest(BaseModel):
    session_id: str
    input: str


class ResetRequest(BaseModel):
    session_id: str


@router.get("/")
def home():
    return {"message": "Mini Agent is running"}


@router.post("/responses")
async def create_response(request: ResponseRequest):
    try:
        reply = await respond(
            request.session_id,
            request.input,
        )
        return {"output": reply}

    except Exception:
        logger.exception(
            "Responses API调用失败 session_id=%s",
            request.session_id,
        )
        raise HTTPException(
            status_code=500,
            detail="模型调用失败",
        )


@router.post("/responses/stream")
async def create_streaming_response(request: ResponseRequest):
    async def event_generator():
        try:
            async for chunk in stream_respond(
                request.session_id,
                request.input,
            ):
                data = json.dumps(
                    {"delta": chunk},
                    ensure_ascii=False,
                )
                yield f"data: {data}\n\n"

            yield "data: [DONE]\n\n"

        except Exception:
            logger.exception(
                "流式Responses调用失败 session_id=%s",
                request.session_id,
            )
            yield (
                'event: error\n'
                'data: {"message":"模型调用失败"}\n\n'
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )


@router.post("/responses/reset")
def reset_response(request: ResetRequest):
    reset_response_session(request.session_id)
    return {"message": "session reset"}


@router.post("/agent")
async def agent(request: ResponseRequest):
    try:
        reply = await run_agent(
            request.session_id,
            request.input,
        )
        return {"output": reply}

    except Exception:
        logger.exception(
            "Agent执行失败 session_id=%s",
            request.session_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Agent执行失败",
        )
