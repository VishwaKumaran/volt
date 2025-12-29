from typing import Optional
from pydantic import BaseModel


class __MODEL_NAME__Base(BaseModel):
    name: str
    description: Optional[str] = None


class __MODEL_NAME__Create(__MODEL_NAME__Base):
    pass


class __MODEL_NAME__Update(__MODEL_NAME__Base):
    name: Optional[str] = None


class __MODEL_NAME__Read(__MODEL_NAME__Base):
    id: int
