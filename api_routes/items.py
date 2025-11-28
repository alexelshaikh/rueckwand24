from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database_core import get_db
from models.db_models.db_user_models import User
from models.api_models.api_catalog_models import (
    ItemCreate,
    ItemRead,
    ItemUpdate
)
from core.crud.crud_catalog import (
    get_material_by_id,
    get_product_type_by_id,
    create_item,
    list_items,
    get_item_by_id,
    update_item,
    delete_item
)
from core.auth_core import get_current_user

router = APIRouter(tags=["Items"])



@router.post("/items", response_model=ItemRead)
async def create_item_endpoint(
    data: ItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    material = await get_material_by_id(db, data.material_id)
    if not material:
        raise HTTPException(status_code=404, detail=f"Material with id={data.material_id} was not found!")

    product_type = await get_product_type_by_id(db, data.product_type_id)
    if not product_type:
        raise HTTPException(status_code=404, detail=f"Product type with id={data.product_type_id} was not found!")

    item = await create_item(db, data)
    return item


@router.get("/items", response_model=list[ItemRead])
async def list_items_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return await list_items(db)


@router.get("/items/{item_id}", response_model=ItemRead)
async def get_item_endpoint(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    item = await get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id={item_id} was not found!")
    return item


@router.patch("/items/{item_id}", response_model=ItemRead)
async def update_item_endpoint(
    item_id: int,
    data: ItemUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    item = await get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id={item_id} was not found!")

    if data.material_id is not None:
        material = await get_material_by_id(db, data.material_id)
        if not material:
            raise HTTPException(status_code=404, detail=f"Material with id={data.material_id} was not found! Warning: materials have been manually modified/changed!")

    if data.product_type_id is not None:
        pt = await get_product_type_by_id(db, data.product_type_id)
        if not pt:
            raise HTTPException(status_code=404, detail=f"Product type with id={data.product_type_id} was not found! Warning: product types have been manually modified/changed!")

    item = await update_item(db, item, data)
    return item


@router.delete("/items/{item_id}")
async def delete_item_endpoint(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    item = await get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id={item_id} was not found!")

    await delete_item(db, item)
    return {"detail": "Item deleted"}
