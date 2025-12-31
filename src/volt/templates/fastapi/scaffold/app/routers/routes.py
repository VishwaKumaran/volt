from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.db import get_session
from app.services.__MODEL_NAME_LOWER__ import __MODEL_NAME_LOWER__Service as service
from app.schemas.__MODEL_NAME_LOWER__ import (
    __MODEL_NAME__Create,
    __MODEL_NAME__Read,
    __MODEL_NAME__Update,
)

router = APIRouter()


@router.post("/", response_model=__MODEL_NAME__Read)
async def create___MODEL_NAME_LOWER__(
    *, session: Session = Depends(get_session), obj_in: __MODEL_NAME__Create
):
    return service.create___MODEL_NAME_LOWER__(session=session, obj_in=obj_in)


@router.get("/{id}", response_model=__MODEL_NAME__Read)
async def read___MODEL_NAME_LOWER__(
    *, session: Session = Depends(get_session), id: int
):
    db_obj = service.get___MODEL_NAME_LOWER__(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="__MODEL_NAME__ not found")
    return db_obj


@router.get("/", response_model=List[__MODEL_NAME__Read])
async def read_multi___MODEL_NAME_PLURAL__(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
):
    return service.get_multi___MODEL_NAME_PLURAL__(session=session, skip=skip, limit=limit)


@router.patch("/{id}", response_model=__MODEL_NAME__Read)
async def update___MODEL_NAME_LOWER__(
    *, session: Session = Depends(get_session), id: int, obj_in: __MODEL_NAME__Update
):
    db_obj = service.get___MODEL_NAME_LOWER__(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="__MODEL_NAME__ not found")
    return service.update___MODEL_NAME_LOWER__(
        session=session, db_obj=db_obj, obj_in=obj_in
    )


@router.delete("/{id}", response_model=__MODEL_NAME__Read)
async def delete___MODEL_NAME_LOWER__(
    *, session: Session = Depends(get_session), id: int
):
    db_obj = service.get___MODEL_NAME_LOWER__(session=session, id=id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="__MODEL_NAME__ not found")
    return service.delete___MODEL_NAME_LOWER__(session=session, id=id)
