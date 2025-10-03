from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Role, BusinessElement, AccessRule, User
from app.utils.sample_data import BUSINESS_ELEMENTS_DATA, ROLES_DATA, ACCESS_RULES_DATA, USERS_DATA
from app.core.security import get_password_hash
from app.core.config import settings
from app.db.session import create_session_factory


async_session_maker = create_session_factory(settings.DATABASE_URL)


async def seed_roles(session: AsyncSession):
    existing_names = {name async for name in await session.stream_scalars(select(Role.name))}

    for role_data in ROLES_DATA:
        if role_data["name"] not in existing_names:
            session.add(Role(**role_data))
    await session.commit()


async def seed_business_elements(session: AsyncSession):
    existing_names = {name async for name in await session.stream_scalars(select(BusinessElement.name))}

    for be_data in BUSINESS_ELEMENTS_DATA:
        if be_data["name"] not in existing_names:
            session.add(BusinessElement(**be_data))
    await session.commit()


async def seed_access_rules(session: AsyncSession):
    roles = {r.name: r.id async for r in await session.stream_scalars(select(Role))}
    elements = {e.name: e.id async for e in await session.stream_scalars(select(BusinessElement))}

    result = await session.execute(
        select(AccessRule.role_id, AccessRule.businesselement_id)
    )
    existing_pairs = {
        (row.role_id, row.businesselement_id) for row in result
    }

    for rule in ACCESS_RULES_DATA:
        role_id = roles[rule["role_name"]]
        element_id = elements[rule["businesselement_name"]]
        if (role_id, element_id) not in existing_pairs:
            access_rule = AccessRule(
                role_id=role_id,
                businesselement_id=element_id,
                read_permission=rule["read_permission"],
                read_all_permission=rule["read_all_permission"],
                create_permission=rule["create_permission"],
                update_permission=rule["update_permission"],
                update_all_permission=rule["update_all_permission"],
                delete_permission=rule["delete_permission"],
                delete_all_permission=rule["delete_all_permission"],
            )
            session.add(access_rule)
    await session.commit()


async def seed_users(session: AsyncSession):
    existing_emails = {email async for email in await session.stream_scalars(select(User.email))}
    roles = {r.name: r async for r in await session.stream_scalars(select(Role))}

    for user_data in USERS_DATA:
        if user_data["email"] in existing_emails:
            result = await session.execute(select(User).where(User.email == user_data["email"]))
            user = result.scalar_one_or_none()
            if not user.roles:
                user.roles = [roles[name] for name in user_data["role_names"]]
                session.add(user)
            continue

        user = User(
            email=user_data["email"],
            password=get_password_hash(user_data["password"]),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            is_active=user_data.get("is_active", True),
        )
        user.roles = [roles[name] for name in user_data["role_names"]]
        session.add(user)
    await session.commit()


async def seed_all():
    async with async_session_maker() as session:
        await seed_business_elements(session)
        await seed_roles(session)
        await seed_access_rules(session)
        await seed_users(session)
