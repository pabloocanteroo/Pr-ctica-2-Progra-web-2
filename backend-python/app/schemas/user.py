from typing import Optional
from pydantic import BaseModel, ConfigDict, model_serializer


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str

    @model_serializer
    def serialize(self) -> dict:
        return {
            "_id": str(self.id),
            "username": self.username,
            "role": self.role,
        }
