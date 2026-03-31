from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import NoteCreateRequest, NoteOut


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("")
def create_note(payload: NoteCreateRequest) -> NoteOut:
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=500, detail="failed to fetch created note")
    return NoteOut(id=note["id"], content=note["content"], created_at=note["created_at"])


@router.get("/{note_id}")
def get_single_note(note_id: int) -> NoteOut:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteOut(id=row["id"], content=row["content"], created_at=row["created_at"])


