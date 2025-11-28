from models.db_models.db_catalog_models import Material, ProductType, ItemConfiguration
from models.api_models.api_catalog_models import MaterialCreate,MaterialUpdate, ProductTypeCreate,ProductTypeUpdate, ItemCreate, ItemUpdate
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.image_core import generate_item_pdf


async def create_item(db: AsyncSession, data: ItemCreate) -> ItemConfiguration:
    item = ItemConfiguration(
        material_id=data.material_id,
        product_type_id=data.product_type_id,
        width=data.width,
        height=data.height,
        pdf_path=None
    )
    db.add(item)

    await db.flush()

    try:
        pdf_path = generate_item_pdf(
            cropped_width=item.width,
            cropped_height=item.height,
            item_id=item.id
        )
    except Exception:
        await db.rollback()
        raise

    item.pdf_path = pdf_path

    await db.commit()
    await db.refresh(item)
    return item



async def list_items(db: AsyncSession) -> Sequence[ItemConfiguration]:
    result = await db.execute(select(ItemConfiguration))
    return result.scalars().all()


async def get_item_by_id(
        db: AsyncSession,
        item_id: int
) -> Optional[ItemConfiguration]:
    result = await db.execute(select(ItemConfiguration).where(ItemConfiguration.id == item_id))
    return result.scalar_one_or_none()


async def update_item(
        db: AsyncSession,
        item: ItemConfiguration,
        data: ItemUpdate
) -> ItemConfiguration:
    if data.material_id is not None:
        item.material_id = data.material_id
    if data.product_type_id is not None:
        item.product_type_id = data.product_type_id
    if data.width is not None:
        item.width = data.width
    if data.height is not None:
        item.height = data.height

    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(
        db: AsyncSession,
        item: ItemConfiguration
) -> None:
    await db.delete(item)
    await db.commit()




#############################################################################################
################################# Materials CRUD operations #################################
#############################################################################################


async def create_material(
        db: AsyncSession,
        data: MaterialCreate
) -> Material:
    material = Material(
        name=data.name,
        description=data.description,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material


async def list_materials(db: AsyncSession) -> Sequence[Material]:
    material_list = await db.execute(select(Material))
    return material_list.scalars().all()


async def get_material_by_id(
        db: AsyncSession,
        material_id: int
) -> Optional[Material]:
    material = await db.execute(select(Material).where(Material.id == material_id))
    return material.scalar_one_or_none()


async def get_material_by_name(
        db: AsyncSession,
        name: str
) -> Sequence[Material]:
    material_list = await db.execute(select(Material).where(Material.name.ilike(f"%{name}%")))
    return material_list.scalars().all()


async def update_material(
        db: AsyncSession,
        material: Material,
        data: MaterialUpdate
) -> Material:
    if data.name is not None:
        material.name = data.name
    if data.description is not None:
        material.description = data.description

    await db.commit()
    await db.refresh(material)
    return material


async def delete_material(db: AsyncSession, material: Material) -> None:
    await db.delete(material)
    await db.commit()




#############################################################################################
################################# Product Types CRUD operations #############################
#############################################################################################

async def create_product_type(
        db: AsyncSession,
        data: ProductTypeCreate
) -> ProductType:
    pt = ProductType(name=data.name, description=data.description)
    db.add(pt)
    await db.commit()
    await db.refresh(pt)
    return pt


async def list_product_types(db: AsyncSession) -> Sequence[ProductType]:
    result = await db.execute(select(ProductType))
    return result.scalars().all()


async def get_product_type_by_id(
        db: AsyncSession,
        product_type_id: int
) -> Optional[ProductType]:
    result = await db.execute(select(ProductType).where(ProductType.id == product_type_id))
    return result.scalar_one_or_none()


async def get_product_type_by_name(
        db: AsyncSession,
        name: str
) -> Optional[ProductType]:
    result = await db.execute(select(ProductType).where(ProductType.name.ilike(f"%{name}%")))
    return result.scalar_one_or_none()


async def update_product_type(
        db: AsyncSession,
        pt: ProductType,
        data: ProductTypeUpdate
) -> ProductType:
    if data.name is not None:
        pt.name = data.name
    if data.description is not None:
        pt.description = data.description

    await db.commit()
    await db.refresh(pt)
    return pt


async def delete_product_type(
        db: AsyncSession,
        pt: ProductType
) -> None:
    await db.delete(pt)
    await db.commit()
