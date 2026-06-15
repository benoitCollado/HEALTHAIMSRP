from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=2000)


class ChatImageAttachment(BaseModel):
    object_key: str = Field(min_length=1, max_length=500)
    filename: str | None = Field(default=None, max_length=255)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=10)
    images: list[ChatImageAttachment] = Field(default_factory=list, max_length=4)


class ChatResponse(BaseModel):
    answer: str


class ChatImageResponse(BaseModel):
    object_key: str
    url: str
    content_type: str
    filename: str
