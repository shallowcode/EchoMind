from dataclasses import dataclass, field
from typing import Literal
import time
from pydantic import BaseModel, ConfigDict, Field


class BusinessRejection(ValueError):
    """Confirmed business decision, distinct from backend failure."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Principal:
    tenant: str
    user: str
    roles: frozenset[str] = frozenset({"customer"})

    def require(self, role: str):
        if role not in self.roles and "admin" not in self.roles:
            raise PermissionError(f"Required role: {role}")

    @property
    def demo_customer(self):
        return self.tenant == "demo" and "demo_customer" in self.roles


class ChatInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=6000)
    conv_id: str | None = Field(default=None, pattern=r"^[a-zA-Z0-9_-]{1,80}$")
    request_id: str = Field(min_length=8, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")


@dataclass
class Trace:
    request_id: str
    events: list = field(default_factory=list)
    spans: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    model_calls: int = 0
    failures: list = field(default_factory=list)
    usage: list = field(default_factory=list)
    memory: dict = field(default_factory=dict)
    model_inputs: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    started: float = field(default_factory=time.perf_counter, repr=False)


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    arguments: dict = Field(default_factory=dict)


class AgentTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list, max_length=3)


class JudgeScores(BaseModel):
    relevance: float = Field(ge=0, le=1)
    accuracy: float = Field(ge=0, le=1)
    completeness: float = Field(ge=0, le=1)
    helpfulness: float = Field(ge=0, le=1)


class Settings(BaseModel):
    business_url: str = ""
    service_key: str = ""
    db_path: str = "data/supportflow.sqlite3"
    model_backend: Literal["compatible", "anthropic", "fixture"] = "compatible"
    model_url: str = "http://127.0.0.1:8081/v1"
    model_name: str = "qwen3-local"
    model_key: str = ""
    local_chat_template: bool = True
    supports_json_schema: bool = True
    model_thinking: Literal["enabled", "disabled"] | None = None
    public_url: str = "http://localhost:8000"
    model_timeout: float = 90
    request_timeout: float = 180
    max_inflight: int = 4
    max_tool_rounds: int = 3
    storage: Literal["sqlite", "chroma"] = "sqlite"
    chroma_path: str = "data/supportflow-chroma"
    redis_url: str = ""
    skills_dir: str = "skills"
    token_ttl: int = 3600
    model_input_price: float | None = None
    model_output_price: float | None = None
    pricing_profile: Literal["glm-air-20260908"] | None = None
    currency: str = "CNY"
    machine_hourly_cost: float | None = None
    business_mode: Literal["sandbox", "external"] = "sandbox"
    local_demo_access: bool = False
    business_currency: Literal["CNY"] = "CNY"
    payment_url: str = ""
    payment_key: str = ""
    payment_webhook_secret: str = ""

    @classmethod
    def from_env(cls):
        import os
        from dotenv import load_dotenv

        load_dotenv(os.environ.get("SF_ENV_FILE", ".env"))
        return cls(
            **{
                key: os.environ["SF_" + key.upper()]
                for key in cls.model_fields
                if "SF_" + key.upper() in os.environ
            }
        )
