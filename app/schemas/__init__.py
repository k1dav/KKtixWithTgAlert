from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class Detail(BaseModel):
    detail: str


class BooleanMixin(BaseModel):
    value: bool


class IDMixin(BaseModel):
    id: UUID


class IDs(BaseModel):
    ids: List[UUID]


class UpdateMixin(BaseModel):
    updated_at: datetime


class CreateMixin(BaseModel):
    created_at: datetime
