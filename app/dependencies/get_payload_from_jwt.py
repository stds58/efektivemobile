from typing import List
from uuid import UUID, uuid4
import structlog
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.stubs import create_fake_access_context
from app.services.auth_service import AuthService
from app.services.user import ensure_user_is_active
from app.schemas.permission import AccessContext
from app.schemas.user import SchemaUserFilter
from app.services.user_role import find_one_user_role, find_many_user_role
from app.services.access_rule import get_user_access_rules_for_business_element


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
    fake_access = create_fake_access_context()
    user_roles = await find_one_user_role(
        business_element="user_roles",
        access=fake_access,
        filters=filters,
        session=session,
    )

    role_ids = [role.id for role in user_roles.roles]

    all_items = set()
    for role_id in role_ids:
        rule = await get_user_access_rules_for_business_element(
            access=fake_access, session=session, role_id=role_id, search_businesselement=business_element
        )
        all_items.update(rule)
    list_permissions = list(all_items)

    return AccessContext(user_id=user_id, permissions=list_permissions)
