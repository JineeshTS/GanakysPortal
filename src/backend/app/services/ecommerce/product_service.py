"""
Product Service - E-commerce Module (MOD-14)
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
import re

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ecommerce import Product, ProductCategory, ProductVariant, ProductStatus
from app.schemas.ecommerce import (
    ProductCreate, ProductUpdate,
    ProductCategoryCreate, ProductCategoryUpdate,
    ProductVariantCreate, ProductVariantUpdate
)


class ProductService:
    """Service for product management operations."""

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-friendly slug from name."""
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        return slug.strip('-')

    # Category Methods
    @staticmethod
    async def create_category(
        db: AsyncSession,
        company_id: UUID,
        data: ProductCategoryCreate
    ) -> ProductCategory:
        """Create a product category."""
        category = ProductCategory(
            id=uuid4(),
            company_id=company_id,
            slug=ProductService.generate_slug(data.name),
            **data.model_dump()
        )
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def get_category(
        db: AsyncSession,
        category_id: UUID,
        company_id: UUID
    ) -> Optional[ProductCategory]:
        """Get category by ID."""
        result = await db.execute(
            select(ProductCategory).where(
                and_(
                    ProductCategory.id == category_id,
                    ProductCategory.company_id == company_id,
                    ProductCategory.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_categories(
        db: AsyncSession,
        company_id: UUID,
        parent_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ProductCategory], int]:
        """List product categories."""
        query = select(ProductCategory).where(
            and_(
                ProductCategory.company_id == company_id,
                ProductCategory.deleted_at.is_(None)
            )
        )

        if parent_id is not None:
            query = query.where(ProductCategory.parent_id == parent_id)
        else:
            query = query.where(ProductCategory.parent_id.is_(None))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(ProductCategory.display_order)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_category(
        db: AsyncSession,
        category: ProductCategory,
        data: ProductCategoryUpdate
    ) -> ProductCategory:
        """Update product category."""
        update_data = data.model_dump(exclude_unset=True)
        if 'name' in update_data:
            update_data['slug'] = ProductService.generate_slug(update_data['name'])
        for field, value in update_data.items():
            setattr(category, field, value)
        category.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(category)
        return category

    # Product Methods
    @staticmethod
    async def create_product(
        db: AsyncSession,
        company_id: UUID,
        data: ProductCreate
    ) -> Product:
        """Create a product."""
        product = Product(
            id=uuid4(),
            company_id=company_id,
            slug=ProductService.generate_slug(data.name),
            status=ProductStatus.DRAFT,
            has_variants=False,
            view_count=0,
            **data.model_dump()
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def get_product(
        db: AsyncSession,
        product_id: UUID,
        company_id: UUID
    ) -> Optional[Product]:
        """Get product by ID."""
        result = await db.execute(
            select(Product).where(
                and_(
                    Product.id == product_id,
                    Product.company_id == company_id,
                    Product.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_product_by_sku(
        db: AsyncSession,
        sku: str,
        company_id: UUID
    ) -> Optional[Product]:
        """Get product by SKU."""
        result = await db.execute(
            select(Product).where(
                and_(
                    Product.sku == sku,
                    Product.company_id == company_id,
                    Product.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_products(
        db: AsyncSession,
        company_id: UUID,
        category_id: Optional[UUID] = None,
        status: Optional[ProductStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Product], int]:
        """List products with filtering."""
        query = select(Product).where(
            and_(
                Product.company_id == company_id,
                Product.deleted_at.is_(None)
            )
        )

        if category_id:
            query = query.where(Product.category_id == category_id)
        if status:
            query = query.where(Product.status == status)
        if search:
            query = query.where(
                Product.name.ilike(f"%{search}%") |
                Product.sku.ilike(f"%{search}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.execute(count_query)
        total_count = total.scalar()

        query = query.offset(skip).limit(limit).order_by(Product.name)
        result = await db.execute(query)

        return result.scalars().all(), total_count

    @staticmethod
    async def update_product(
        db: AsyncSession,
        product: Product,
        data: ProductUpdate
    ) -> Product:
        """Update product."""
        update_data = data.model_dump(exclude_unset=True)
        if 'name' in update_data:
            update_data['slug'] = ProductService.generate_slug(update_data['name'])
        for field, value in update_data.items():
            setattr(product, field, value)
        product.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def delete_product(
        db: AsyncSession,
        product: Product
    ) -> None:
        """Soft delete product."""
        product.deleted_at = datetime.utcnow()
        await db.commit()

    @staticmethod
    async def increment_view_count(
        db: AsyncSession,
        product: Product
    ) -> None:
        """Increment product view count."""
        product.view_count += 1
        await db.commit()

    # Variant Methods
    @staticmethod
    async def create_variant(
        db: AsyncSession,
        data: ProductVariantCreate
    ) -> ProductVariant:
        """Create a product variant."""
        variant = ProductVariant(
            id=uuid4(),
            **data.model_dump()
        )
        db.add(variant)

        # Update product has_variants flag
        result = await db.execute(
            select(Product).where(Product.id == data.product_id)
        )
        product = result.scalar_one_or_none()
        if product:
            product.has_variants = True

        await db.commit()
        await db.refresh(variant)
        return variant

    @staticmethod
    async def get_variant(
        db: AsyncSession,
        variant_id: UUID
    ) -> Optional[ProductVariant]:
        """Get variant by ID."""
        result = await db.execute(
            select(ProductVariant).where(ProductVariant.id == variant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_variants(
        db: AsyncSession,
        product_id: UUID
    ) -> List[ProductVariant]:
        """List variants for a product."""
        result = await db.execute(
            select(ProductVariant).where(
                ProductVariant.product_id == product_id
            ).order_by(ProductVariant.name)
        )
        return result.scalars().all()

    @staticmethod
    async def update_variant(
        db: AsyncSession,
        variant: ProductVariant,
        data: ProductVariantUpdate
    ) -> ProductVariant:
        """Update variant."""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(variant, field, value)
        variant.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(variant)
        return variant

    @staticmethod
    async def update_stock(
        db: AsyncSession,
        product: Product,
        quantity_change: Decimal,
        variant_id: Optional[UUID] = None
    ) -> None:
        """Update stock quantity."""
        if variant_id:
            variant = await ProductService.get_variant(db, variant_id)
            if variant:
                variant.stock_qty += quantity_change
                variant.updated_at = datetime.utcnow()
        else:
            product.stock_qty += quantity_change
            product.updated_at = datetime.utcnow()

        await db.commit()
