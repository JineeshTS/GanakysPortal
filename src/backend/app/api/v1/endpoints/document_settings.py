"""
Document Settings Endpoints
Manage document categories and types
"""
from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, text
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData

router = APIRouter()


# ==================== SCHEMAS ====================

class CategoryBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = '#3B82F6'
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: UUID
    sort_order: int
    is_system: bool
    is_active: bool

    class Config:
        from_attributes = True

class TypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    category_id: UUID

class TypeCreate(TypeBase):
    pass

class TypeResponse(TypeBase):
    id: UUID
    sort_order: int
    is_system: bool
    is_active: bool
    category_code: Optional[str] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


# ==================== CATEGORY ENDPOINTS ====================

@router.get("/categories", response_model=List[CategoryResponse])
async def list_categories(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    active_only: bool = True
):
    """List all document categories (system + company-specific)."""
    query = """
        SELECT id, code, name, description, color, icon, sort_order, is_system, is_active
        FROM document_categories
        WHERE (company_id IS NULL OR company_id = :company_id)
    """
    if active_only:
        query += " AND is_active = TRUE"
    query += " ORDER BY sort_order, name"

    result = await db.execute(text(query), {"company_id": str(current_user.company_id)})
    rows = result.fetchall()

    return [
        CategoryResponse(
            id=row.id,
            code=row.code,
            name=row.name,
            description=row.description,
            color=row.color,
            icon=row.icon,
            sort_order=row.sort_order,
            is_system=row.is_system,
            is_active=row.is_active
        )
        for row in rows
    ]


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new document category for the company."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can create categories")

    # Check if code already exists
    check_query = """
        SELECT id FROM document_categories
        WHERE code = :code AND (company_id IS NULL OR company_id = :company_id)
    """
    result = await db.execute(
        text(check_query),
        {"code": data.code, "company_id": str(current_user.company_id)}
    )
    if result.fetchone():
        raise HTTPException(status_code=400, detail="Category code already exists")

    # Get max sort_order
    max_order_result = await db.execute(
        text("SELECT COALESCE(MAX(sort_order), 0) + 1 as next_order FROM document_categories")
    )
    next_order = max_order_result.fetchone().next_order

    # Insert new category
    insert_query = """
        INSERT INTO document_categories (company_id, code, name, description, color, icon, sort_order, is_system, is_active)
        VALUES (:company_id, :code, :name, :description, :color, :icon, :sort_order, FALSE, TRUE)
        RETURNING id, code, name, description, color, icon, sort_order, is_system, is_active
    """
    result = await db.execute(
        text(insert_query),
        {
            "company_id": str(current_user.company_id),
            "code": data.code,
            "name": data.name,
            "description": data.description,
            "color": data.color,
            "icon": data.icon,
            "sort_order": next_order
        }
    )
    await db.commit()
    row = result.fetchone()

    return CategoryResponse(
        id=row.id,
        code=row.code,
        name=row.name,
        description=row.description,
        color=row.color,
        icon=row.icon,
        sort_order=row.sort_order,
        is_system=row.is_system,
        is_active=row.is_active
    )


# ==================== TYPE ENDPOINTS ====================

@router.get("/types", response_model=List[TypeResponse])
async def list_types(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    category_id: Optional[UUID] = None,
    active_only: bool = True
):
    """List all document types, optionally filtered by category."""
    query = """
        SELECT dt.id, dt.code, dt.name, dt.description, dt.category_id,
               dt.sort_order, dt.is_system, dt.is_active,
               dc.code as category_code, dc.name as category_name
        FROM document_types dt
        JOIN document_categories dc ON dt.category_id = dc.id
        WHERE (dt.company_id IS NULL OR dt.company_id = :company_id)
    """
    params = {"company_id": str(current_user.company_id)}

    if category_id:
        query += " AND dt.category_id = :category_id"
        params["category_id"] = str(category_id)

    if active_only:
        query += " AND dt.is_active = TRUE"

    query += " ORDER BY dc.sort_order, dt.sort_order, dt.name"

    result = await db.execute(text(query), params)
    rows = result.fetchall()

    return [
        TypeResponse(
            id=row.id,
            code=row.code,
            name=row.name,
            description=row.description,
            category_id=row.category_id,
            sort_order=row.sort_order,
            is_system=row.is_system,
            is_active=row.is_active,
            category_code=row.category_code,
            category_name=row.category_name
        )
        for row in rows
    ]


@router.post("/types", response_model=TypeResponse, status_code=status.HTTP_201_CREATED)
async def create_type(
    data: TypeCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new document type for the company."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can create document types")

    # Check if code already exists
    check_query = """
        SELECT id FROM document_types
        WHERE code = :code AND (company_id IS NULL OR company_id = :company_id)
    """
    result = await db.execute(
        text(check_query),
        {"code": data.code, "company_id": str(current_user.company_id)}
    )
    if result.fetchone():
        raise HTTPException(status_code=400, detail="Document type code already exists")

    # Get max sort_order for this category
    max_order_result = await db.execute(
        text(
            "SELECT COALESCE(MAX(sort_order), 0) + 1 as next_order FROM document_types WHERE category_id = :category_id"
        ),
        {"category_id": str(data.category_id)}
    )
    next_order = max_order_result.fetchone().next_order

    # Insert new type
    insert_query = """
        INSERT INTO document_types (company_id, category_id, code, name, description, sort_order, is_system, is_active)
        VALUES (:company_id, :category_id, :code, :name, :description, :sort_order, FALSE, TRUE)
        RETURNING id, code, name, description, category_id, sort_order, is_system, is_active
    """
    result = await db.execute(
        text(insert_query),
        {
            "company_id": str(current_user.company_id),
            "category_id": str(data.category_id),
            "code": data.code,
            "name": data.name,
            "description": data.description,
            "sort_order": next_order
        }
    )
    await db.commit()
    row = result.fetchone()

    # Get category info
    cat_result = await db.execute(
        text("SELECT code, name FROM document_categories WHERE id = :id"),
        {"id": str(data.category_id)}
    )
    cat_row = cat_result.fetchone()

    return TypeResponse(
        id=row.id,
        code=row.code,
        name=row.name,
        description=row.description,
        category_id=row.category_id,
        sort_order=row.sort_order,
        is_system=row.is_system,
        is_active=row.is_active,
        category_code=cat_row.code if cat_row else None,
        category_name=cat_row.name if cat_row else None
    )


# ==================== CATEGORY UPDATE/DELETE ====================

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a document category."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can update categories")

    # Check if category exists and is not system category
    check_query = """
        SELECT id, is_system, company_id FROM document_categories
        WHERE id = :id AND (company_id IS NULL OR company_id = :company_id)
    """
    result = await db.execute(
        text(check_query),
        {"id": str(category_id), "company_id": str(current_user.company_id)}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    if row.is_system and row.company_id is None:
        raise HTTPException(status_code=403, detail="Cannot modify system categories")

    # Build update query
    updates = []
    params = {"id": str(category_id)}
    if data.name is not None:
        updates.append("name = :name")
        params["name"] = data.name
    if data.description is not None:
        updates.append("description = :description")
        params["description"] = data.description
    if data.color is not None:
        updates.append("color = :color")
        params["color"] = data.color
    if data.icon is not None:
        updates.append("icon = :icon")
        params["icon"] = data.icon
    if data.is_active is not None:
        updates.append("is_active = :is_active")
        params["is_active"] = data.is_active

    if updates:
        updates.append("updated_at = NOW()")
        update_query = f"""
            UPDATE document_categories
            SET {', '.join(updates)}
            WHERE id = :id
            RETURNING id, code, name, description, color, icon, sort_order, is_system, is_active
        """
        result = await db.execute(text(update_query), params)
        await db.commit()
        row = result.fetchone()

    return CategoryResponse(
        id=row.id,
        code=row.code,
        name=row.name,
        description=row.description,
        color=row.color,
        icon=row.icon,
        sort_order=row.sort_order,
        is_system=row.is_system,
        is_active=row.is_active
    )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a document category (soft delete by setting is_active=false)."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can delete categories")

    # Check if category exists and is not system category
    check_query = """
        SELECT id, is_system, company_id FROM document_categories
        WHERE id = :id AND (company_id IS NULL OR company_id = :company_id)
    """
    result = await db.execute(
        text(check_query),
        {"id": str(category_id), "company_id": str(current_user.company_id)}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Category not found")
    if row.is_system and row.company_id is None:
        raise HTTPException(status_code=403, detail="Cannot delete system categories")

    # Soft delete
    await db.execute(
        text("UPDATE document_categories SET is_active = FALSE, updated_at = NOW() WHERE id = :id"),
        {"id": str(category_id)}
    )
    await db.commit()


# ==================== TYPE UPDATE/DELETE ====================

class TypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    is_active: Optional[bool] = None


@router.put("/types/{type_id}", response_model=TypeResponse)
async def update_type(
    type_id: UUID,
    data: TypeUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a document type."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can update document types")

    # Check if type exists and is not system type
    check_query = """
        SELECT id, is_system, company_id FROM document_types
        WHERE id = :id AND (company_id IS NULL OR company_id = :company_id)
    """
    result = await db.execute(
        text(check_query),
        {"id": str(type_id), "company_id": str(current_user.company_id)}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document type not found")
    if row.is_system and row.company_id is None:
        raise HTTPException(status_code=403, detail="Cannot modify system document types")

    # Build update query
    updates = []
    params = {"id": str(type_id)}
    if data.name is not None:
        updates.append("name = :name")
        params["name"] = data.name
    if data.description is not None:
        updates.append("description = :description")
        params["description"] = data.description
    if data.category_id is not None:
        updates.append("category_id = :category_id")
        params["category_id"] = str(data.category_id)
    if data.is_active is not None:
        updates.append("is_active = :is_active")
        params["is_active"] = data.is_active

    if updates:
        updates.append("updated_at = NOW()")
        update_query = f"""
            UPDATE document_types
            SET {', '.join(updates)}
            WHERE id = :id
            RETURNING id, code, name, description, category_id, sort_order, is_system, is_active
        """
        result = await db.execute(text(update_query), params)
        await db.commit()
        row = result.fetchone()

    # Get category info
    cat_result = await db.execute(
        text("SELECT code, name FROM document_categories WHERE id = :id"),
        {"id": str(row.category_id)}
    )
    cat_row = cat_result.fetchone()

    return TypeResponse(
        id=row.id,
        code=row.code,
        name=row.name,
        description=row.description,
        category_id=row.category_id,
        sort_order=row.sort_order,
        is_system=row.is_system,
        is_active=row.is_active,
        category_code=cat_row.code if cat_row else None,
        category_name=cat_row.name if cat_row else None
    )


@router.delete("/types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_type(
    type_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a document type (soft delete by setting is_active=false)."""
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can delete document types")

    # Check if type exists and is not system type
    check_query = """
        SELECT id, is_system, company_id FROM document_types
        WHERE id = :id AND (company_id IS NULL OR company_id = :company_id)
    """
    result = await db.execute(
        text(check_query),
        {"id": str(type_id), "company_id": str(current_user.company_id)}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document type not found")
    if row.is_system and row.company_id is None:
        raise HTTPException(status_code=403, detail="Cannot delete system document types")

    # Soft delete
    await db.execute(
        text("UPDATE document_types SET is_active = FALSE, updated_at = NOW() WHERE id = :id"),
        {"id": str(type_id)}
    )
    await db.commit()
