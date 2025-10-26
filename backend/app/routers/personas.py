from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import PersonaSchema
from ..services.personas import add_persona, ensure_seed_personas, list_personas

router = APIRouter(tags=["personas"])


@router.get("/personas", response_model=list[PersonaSchema])
async def get_personas() -> list[PersonaSchema]:
    return list_personas()


@router.post("/personas", response_model=PersonaSchema, status_code=201)
async def create_persona(payload: PersonaSchema) -> PersonaSchema:
    add_persona(payload)
    return payload


@router.get("/personas/{persona_id}", response_model=PersonaSchema)
async def get_persona(persona_id: str) -> PersonaSchema:
    for persona in list_personas():
        if persona.id == persona_id:
            return persona
    raise HTTPException(status_code=404, detail="persona not found")
