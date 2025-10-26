#!/usr/bin/env python
"""Personas router."""

from fastapi import APIRouter, HTTPException

from app.schemas import CreatePersonaRequest, Persona
from app.services.personas import persona_registry

router = APIRouter(prefix="/v1/personas", tags=["personas"])


@router.get("", response_model=list[Persona])
async def list_personas(limit: int = 100, offset: int = 0) -> list[Persona]:
    """List all personas."""
    all_personas = persona_registry.get_all_personas()
    return all_personas[offset : offset + limit]


@router.get("/{persona_id}", response_model=Persona)
async def get_persona(persona_id: str) -> Persona:
    """Get a specific persona."""
    persona = persona_registry.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.post("", response_model=Persona, status_code=201)
async def create_persona(request: CreatePersonaRequest) -> Persona:
    """Create a new custom persona."""
    persona = persona_registry.create_persona(request)
    return persona
