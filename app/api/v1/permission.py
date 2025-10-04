from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user import (
    add_role_to_user,
    remove_role_from_user,
    get_all_user_roles,
)
from app.dependencies.get_db import connection
from app.dependencies.permissions import require_permission
from app.schemas.permission import (
    AccessContext,
    SchemaUserRolesBase,
    SchemaUserRolesCreate,
    SchemaUserRolesFilter,
)


router = APIRouter()


@router.get("", response_model=List[dict], summary="Get roles")
async def get_users(
    filters: SchemaUserRolesFilter = Depends(),
    session: AsyncSession = Depends(connection()),
    access: AccessContext = Depends(require_permission("user_roles")),
):
    return await get_all_user_roles(filters=filters, access=access, session=session)


@router.post("", summary="Add role", response_model=SchemaUserRolesBase)
async def edit_user(
    data: SchemaUserRolesCreate = Depends(),
    session: AsyncSession = Depends(connection()),
    access: AccessContext = Depends(require_permission("user_roles")),
):
    updated_user = await add_role_to_user(access=access, session=session, data=data)
    return updated_user


@router.delete("", summary="Delete role", response_model=dict)
async def unactivate_user(
    data: SchemaUserRolesCreate = Depends(),
    session: AsyncSession = Depends(connection()),
    access: AccessContext = Depends(require_permission("user_roles")),
):
    removed_user = await remove_role_from_user(
        access=access, session=session, data=data
    )
    return removed_user
