from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from sqlmodel import Field, Session, SQLModel, create_engine, select


class PersonaModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    payload: str


class TopicModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    payload: str


class PostModel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    payload: str


def init_engine(path: str | Path = "hurl.db"):
    engine = create_engine(f"sqlite:///{path}", echo=False, future=True)
    SQLModel.metadata.create_all(engine)
    return engine


def upsert(session: Session, model: type[SQLModel], *, id: str, payload: str) -> None:
    instance = session.get(model, id)
    if instance is None:
        instance = model(id=id, payload=payload)  # type: ignore[call-arg]
        session.add(instance)
    else:
        instance.payload = payload  # type: ignore[attr-defined]
    session.commit()


def load_all(session: Session, model: type[SQLModel]) -> List[str]:
    statement = select(model)
    return [row.payload for row in session.exec(statement)]
