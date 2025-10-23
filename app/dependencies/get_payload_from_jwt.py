from typing import List
from uuid import UUID, uuid4
import structlog
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserDAO
from app.services.auth_service import AuthService
from app.services.user import ensure_user_is_active
from app.schemas.permission import AccessContext
from app.schemas.user import SchemaUserFilter
from app.services.user_role import find_one_user_role, find_many_user_role
from app.services.access_rule import get_user_access_rules_for_business_element
from app.schemas.base import PaginationParams
from app.services.access_rule import find_many_access_rule
from app.core.enums import BusinessDomain
from app.schemas.access_rule import SchemaAccessRuleFilter


logger = structlog.get_logger()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/swaggerlogin")


async def get_user_id_from_jwt(
    token: str,
    session: AsyncSession,
) -> UUID:
    payload = AuthService.decode_access_token(token=token)
    user_id = payload.sub
    await ensure_user_is_active(user_id=user_id, session=session)
    return user_id


def get_roles_from_jwt(
    token: str,
) -> List[str]:
    payload = AuthService.decode_access_token(token=token)
    list_permissions = payload.role
    return list_permissions


async def get_payload_from_jwt(
    token: str, business_element: str, session: AsyncSession
):
    user_id = await get_user_id_from_jwt(token=token, session=session)

    filters = SchemaUserFilter(id=user_id)
    fake_uuid = uuid4()
    access = AccessContext(
        user_id=fake_uuid, permissions=["read_all_permission", "create_permission"]
    )
    user_roles = await find_one_user_role(
        business_element="user_roles",
        access=access,
        filters=filters,
        session=session,
    )

    role_ids = [role.id for role in user_roles.roles]

    all_items = set()
    for role_id in role_ids:
        rule = await get_user_access_rules_for_business_element(
            access=access, session=session, role_id=role_id, search_businesselement=business_element
        )
        all_items.update(rule)
    list_permissions = list(all_items)

    return AccessContext(user_id=user_id, permissions=list_permissions)
