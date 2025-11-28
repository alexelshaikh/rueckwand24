from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.db_models.db_base import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    items: Mapped[List["ItemConfiguration"]] = relationship(back_populates="material", cascade="all, delete-orphan")


class ProductType(Base):
    __tablename__ = "product_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    items: Mapped[List["ItemConfiguration"]] = relationship(back_populates="product_type", cascade="all, delete-orphan")


class ItemConfiguration(Base):
    __tablename__ = "item_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    material_id: Mapped[int] = mapped_column(ForeignKey("materials.id", ondelete="RESTRICT"), index=True)
    product_type_id: Mapped[int] = mapped_column(ForeignKey("product_types.id", ondelete="RESTRICT"), index=True)

    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)

    pdf_path: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    material: Mapped["Material"] = relationship(back_populates="items")
    product_type: Mapped["ProductType"] = relationship(back_populates="items")
