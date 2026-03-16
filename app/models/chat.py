from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(..., min_length=8, max_length=64)

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Apa yang harus dilakukan saat gempa bumi?",
                "session_id": "user-abc123",
            }
        }
    }


class ChatResponse(BaseModel):
    token: Optional[str] = None
    done: Optional[bool] = None
    error: Optional[str] = None