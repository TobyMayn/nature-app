from pydantic import BaseModel, ConfigDict
from shapely import Polygon
from sqlmodel import DateTime, Field, SQLModel


class Users(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    username: str = Field(max_length=25)
    password_hash: str = Field(max_length=30)
    email: str | None = Field(default=None, max_length=30)
    municipality: str | None = Field(default=None, max_length=40)

class Location(SQLModel, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    location_id: int | None = Field(default=None, primary_key=True)
    polygon: Polygon

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class AnalysisBody(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    analysis_type: str
    start_date: str
    end_date: str
    polygon: Polygon
    requested_at: DateTime

class AnalysisPayload(BaseModel):
    result_id: int

class Results(SQLModel, table=True):
    results_id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key=True)
    location_id: int = Field(foreign_key=True)
    analysis_date: DateTime
    analysis_type: str
    request_params: AnalysisBody
    status: str = Field(default="Pending")
    requested_at: DateTime
    completed_at: DateTime | None = Field(default=None)
    error_message: str | None = Field(default=None)
    result: dict | None = Field(default=None)
