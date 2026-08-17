from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import ReorderRequest
from app.schemas.ui import UITabCreate, UITabRead, UITabUpdate
from app.services import ConflictError, NotFoundError
from app.services.ui import UITabService

router = APIRouter(prefix="/ui-tabs", tags=["settings"])


@router.post("", response_model=UITabRead, status_code=status.HTTP_201_CREATED)
def create_tab(payload: UITabCreate, db: Session = Depends(get_db)) -> UITabRead:
    try:
        tab = UITabService(db).create(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return UITabRead.model_validate(tab)


@router.get("", response_model=list[UITabRead])
def list_tabs(db: Session = Depends(get_db)) -> list[UITabRead]:
    tabs = UITabService(db).list()
    return [UITabRead.model_validate(t) for t in tabs]


@router.patch("/{tab_id}", response_model=UITabRead)
def update_tab(tab_id: uuid.UUID, payload: UITabUpdate, db: Session = Depends(get_db)) -> UITabRead:
    try:
        tab = UITabService(db).update(tab_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return UITabRead.model_validate(tab)


@router.post("/{tab_id}/show", response_model=UITabRead)
def show_tab(tab_id: uuid.UUID, db: Session = Depends(get_db)) -> UITabRead:
    try:
        tab = UITabService(db).set_visible(tab_id, True)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return UITabRead.model_validate(tab)


@router.post("/{tab_id}/hide", response_model=UITabRead)
def hide_tab(tab_id: uuid.UUID, db: Session = Depends(get_db)) -> UITabRead:
    try:
        tab = UITabService(db).set_visible(tab_id, False)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return UITabRead.model_validate(tab)


@router.post("/reorder", response_model=list[UITabRead])
def reorder_tabs(payload: ReorderRequest, db: Session = Depends(get_db)) -> list[UITabRead]:
    try:
        tabs = UITabService(db).reorder(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [UITabRead.model_validate(t) for t in tabs]


@router.delete("/{tab_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def delete_tab(tab_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    try:
        UITabService(db).delete(tab_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
