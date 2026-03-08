from datetime import datetime, timezone
from typing import Optional, Literal

from pydantic import BaseModel, Field, model_validator
from uuid_utils import uuid7


def generate_message_id() -> str:
    """Generate a UUID7 string for message IDs."""
    return str(uuid7())


def generate_timestamp() -> str:
    """Generate an ISO 8601 UTC timestamp string (frontend-compatible)."""
    return datetime.now(timezone.utc).isoformat()


# --- Nested content models ---


class HITLApprovalItem(BaseModel):
    """An item in the user's HITL approval list."""

    function_id: str
    function_name: str
    confirmed: bool = True
    payload: Optional[dict] = None


class HITLRequestedItem(BaseModel):
    """An item in the assistant's HITL request list."""

    function_id: str
    function_name: str
    confirmed: bool = False
    payload: dict
    hint: Optional[str] = None


class ChatRequestContent(BaseModel):
    """
    Content block of a user chat request.

    Conditional logic:
    - If `hitl_approval` is provided and non-empty, `message` is optional (can be None).
    - If `hitl_approval` is absent/empty, `message` is required.
    """

    message: Optional[str] = None
    metadata: Optional[dict] = None
    hitl_approval: Optional[list[HITLApprovalItem]] = None

    @model_validator(mode="after")
    def validate_message_or_hitl(self) -> "ChatRequestContent":
        """Enforce that message is required when hitl_approval is empty or absent."""
        if not self.hitl_approval and not self.message:
            raise ValueError("message is required when hitl_approval is not provided")
        return self


class ChatResponseContent(BaseModel):
    """
    Content block of an assistant chat response.

    Conditional logic:
    - If `hitl_requested` is provided and non-empty, `message` is optional (can be None).
    - If `hitl_requested` is absent/empty, `message` is required.
    """

    message: Optional[str] = None
    metadata: Optional[dict] = None
    hitl_requested: Optional[list[HITLRequestedItem]] = None

    @model_validator(mode="after")
    def validate_message_or_hitl(self) -> "ChatResponseContent":
        """Enforce that message is required when hitl_requested is empty or absent."""
        if not self.hitl_requested and not self.message:
            raise ValueError("message is required when hitl_requested is not provided")
        return self


# --- Top-level request / response models ---


class ChatRequest(BaseModel):
    """
    Incoming user message to POST /chat/.

    Auto-generated fields:
    - message_id: generated server-side via uuid7 (NOT supplied by client)
    - timestamp: generated server-side as ISO 8601 string (NOT supplied by client)

    Client-supplied fields:
    - user_id: str (will come from JWT in Phase 3; for now accept from body)
    - session_id: mandatory str
    - role: must always be "human"
    - content: ChatRequestContent
    """

    user_id: str
    message_id: str = Field(default_factory=generate_message_id)
    session_id: str
    role: Literal["human"] = "human"
    content: ChatRequestContent
    timestamp: str = Field(default_factory=generate_timestamp)


class ChatResponse(BaseModel):
    """
    Outgoing assistant response from POST /chat/.

    Auto-generated fields:
    - message_id: generated server-side via uuid7
    - timestamp: generated server-side as ISO 8601 string

    Populated from request context:
    - user_id: echoed from request
    - session_id: echoed from request

    Hardcoded:
    - role: always "assistant"
    """

    user_id: str
    message_id: str = Field(default_factory=generate_message_id)
    session_id: str
    role: Literal["assistant"] = "assistant"
    content: ChatResponseContent
    timestamp: str = Field(default_factory=generate_timestamp)
