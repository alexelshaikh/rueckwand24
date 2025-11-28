from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# Materials
class MaterialBase(BaseModel):
    name: str
    description: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class MaterialRead(MaterialBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Product Types
class ProductTypeBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProductTypeCreate(ProductTypeBase):
    pass


class ProductTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProductTypeRead(ProductTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Item Configuration
class ItemBase(BaseModel):
    material_id: int
    product_type_id: int
    width: int
    height: int


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    material_id: Optional[int] = None
    product_type_id: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class ItemRead(ItemBase):
    id: int
    pdf_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
