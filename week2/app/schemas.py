from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class NoteCreateRequest(BaseModel):
    content: str = Field(min_length=1)


class NoteOut(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemOut(BaseModel):
    id: int
    text: str


class ActionItemListOut(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str


class ExtractActionItemsRequest(BaseModel):
    text: str = Field(min_length=1)
    save_note: bool = False
    use_llm: bool = False


class ExtractActionItemsResponse(BaseModel):
    note_id: Optional[int]
    items: List[ActionItemOut]


class MarkActionItemDoneRequest(BaseModel):
    done: bool = True


class MarkActionItemDoneResponse(BaseModel):
    id: int
    done: bool
