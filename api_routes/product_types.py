from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database_core import get_db
from models.db_models.db_user_models import User
from models.api_models.api_catalog_models import (
    ProductTypeCreate,
    ProductTypeRead,
    ProductTypeUpdate
)
from core.crud.crud_catalog import (
    create_product_type,
    list_product_types,
    get_product_type_by_id,
    update_product_type,
    delete_product_type)
from core.auth_core import get_current_user

router = APIRouter(tags=["Product Types"])



@router.post("/product-types", response_model=ProductTypeRead)
async def create_product_type_endpoint(
    data: ProductTypeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return await create_product_type(db, data)


@router.get("/product-types", response_model=list[ProductTypeRead])
async def list_product_types_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return await list_product_types(db)


@router.get("/product-types/{product_type_id}", response_model=ProductTypeRead)
async def get_product_type_endpoint(
    product_type_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    pt = await get_product_type_by_id(db, product_type_id)
    if not pt:
        raise HTTPException(status_code=404, detail=f"Product type with id={product_type_id} was not found!")
    return pt


@router.patch("/product-types/{product_type_id}", response_model=ProductTypeRead)
async def update_product_type_endpoint(
    product_type_id: int,
    data: ProductTypeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    pt = await get_product_type_by_id(db, product_type_id)
    if not pt:
        raise HTTPException(status_code=404, detail=f"Product type with id={product_type_id} was not found!")

    return await update_product_type(db, pt, data)


@router.delete("/product-types/{product_type_id}")
async def delete_product_type_endpoint(
    product_type_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    pt = await get_product_type_by_id(db, product_type_id)
    if not pt:
        raise HTTPException(status_code=404, detail=f"Product type with id={product_type_id} was not found!")

    await delete_product_type(db, pt)
    return {"detail": f"Product type with id={product_type_id} was successfully deleted"}