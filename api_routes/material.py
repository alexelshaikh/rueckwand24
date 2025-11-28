from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database_core import get_db
from models.db_models.db_user_models import User
from models.api_models.api_catalog_models import (
    MaterialCreate,
    MaterialRead,
    MaterialUpdate
)
from core.crud.crud_catalog import (
    create_material,
    list_materials,
    get_material_by_id,
    update_material,
    delete_material
)
from core.auth_core import get_current_user

router = APIRouter(tags=["Materials"])



@router.post("/materials", response_model=MaterialRead)
async def create_material_endpoint(
    data: MaterialCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return await create_material(db, data)


@router.get("/materials", response_model=list[MaterialRead])
async def list_materials_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return await list_materials(db)


@router.get("/materials/{material_id}", response_model=MaterialRead)
async def get_material_endpoint(
    material_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    material = await get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail=f"Material with id={material_id} was not found!")
    return material


@router.patch("/materials/{material_id}", response_model=MaterialRead)
async def update_material_endpoint(
    material_id: int,
    data: MaterialUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    material = await get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail=f"Material with id={material_id} was not found!")

    return await update_material(db, material, data)


@router.delete("/materials/{material_id}")
async def delete_material_endpoint(
    material_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    material = await get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail=f"Material with id={material_id} was not found!")

    await delete_material(db, material)
    return {"detail": f"Material with id={material_id} was successfully deleted"}