from pydantic import BaseModel


class ToolCreate(BaseModel):
    name: str
    description: str
    price_per_day: float


class ToolResponse(BaseModel):
    id: int
    name: str
    description: str
    price_per_day: float
    is_available: bool
    owner_id: int

    class Config:
        from_attributes = True
