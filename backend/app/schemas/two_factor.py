from pydantic import BaseModel


class TwoFactorStatusResponse(BaseModel):
    enabled: bool


class TwoFactorSetupResponse(BaseModel):
    enabled: bool
    secret: str
    provisioning_uri: str


class TwoFactorCodeRequest(BaseModel):
    code: str


class TwoFactorMessageResponse(BaseModel):
    detail: str
    enabled: bool
