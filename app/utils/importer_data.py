from typing import List
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Role, BusinessElement, AccessRule, User, Category, Product, Order, UserRole
from app.utils.sample_data import (
    BUSINESS_ELEMENTS_DATA,
    ROLES_DATA,
    ACCESS_RULES_DATA,
    USERS_DATA,
    CATEGORY_DATA,
    PRODUCT_DATA,
    ORDER_DATA,
)
from app.core.config import settings
from app.db.session import create_session_factory
from app.services.auth.password import get_password_hash


logger = structlog.get_logger()

async_session_maker = create_session_factory(settings.DATABASE_URL)


async def seed_roles(session: AsyncSession):
    existing_names = {
        name async for name in await session.stream_scalars(select(Role.name))
    }

    for role_data in ROLES_DATA:
        if role_data["name"] not in existing_names:
            session.add(Role(**role_data))
    await session.commit()


async def seed_business_elements(session: AsyncSession):
    existing_names = {
        name
        async for name in await session.stream_scalars(select(BusinessElement.name))
    }

    for business_element_data in BUSINESS_ELEMENTS_DATA:
        if business_element_data["name"] not in existing_names:
            session.add(BusinessElement(**business_element_data))
    await session.commit()


async def seed_access_rules(session: AsyncSession):
    roles = {
        role.name: role.id async for role in await session.stream_scalars(select(Role))
    }
    elements = {
        element.name: element.id
        async for element in await session.stream_scalars(select(BusinessElement))
    }

    result = await session.execute(
        select(AccessRule.role_id, AccessRule.businesselement_id)
    )
    existing_pairs = {(row.role_id, row.businesselement_id) for row in result}

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
    existing_emails = {
        email async for email in await session.stream_scalars(select(User.email))
    }

    for user_data in USERS_DATA:
        if user_data["email"] in existing_emails:
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            user = result.scalar_one_or_none()
            session.add(user)
            continue

        user = User(
            email=user_data["email"],
            password=get_password_hash(user_data["password"]),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            is_active=user_data.get("is_active", True),
        )
        session.add(user)
    await session.commit()


async def seed_role_user(session: AsyncSession):
    from app.models.user_role import UserRole

    # 1. Получаем всех пользователей из БД по email
    result = await session.execute(select(User.email, User.id))
    user_email_to_id = {email: user_id for email, user_id in result}

    # 2. Получаем все роли по имени
    result = await session.execute(select(Role.name, Role.id))
    role_name_to_id = {name: role_id for name, role_id in result}

    # 3. Получаем уже существующие связи (user_id, role_id)
    result = await session.execute(select(UserRole.user_id, UserRole.role_id))
    existing_pairs = {(row.user_id, row.role_id) for row in result}

    # 4. Для каждого пользователя из USERS_DATA — назначаем недостающие роли
    for user_data in USERS_DATA:
        email = user_data["email"]
        if email not in user_email_to_id:
            logger.warning("User not found in DB, skipping roles", email=email)
            continue

        user_id = user_email_to_id[email]

        for role_name in user_data["role_names"]:
            if role_name not in role_name_to_id:
                logger.warning("Role not found", role=role_name, email=email)
                continue

            role_id = role_name_to_id[role_name]
            if (user_id, role_id) in existing_pairs:
                continue  # уже есть — пропускаем

            # Добавляем новую связь
            session.add(UserRole(user_id=user_id, role_id=role_id))
            existing_pairs.add((user_id, role_id))  # чтобы не дублировать в рамках одного запуска

    await session.commit()

async def seed_categories(session: AsyncSession):
    existing_names = {
        name async for name in await session.stream_scalars(select(Category.name))
    }

    for category_data in CATEGORY_DATA:
        if category_data["name"] not in existing_names:
            session.add(Category(**category_data))
    await session.commit()


async def seed_products(session: AsyncSession):
    categories = {
        category.name: category.id
        async for category in await session.stream_scalars(select(Category))
    }
    existing_names = {
        name async for name in await session.stream_scalars(select(Product.name))
    }

    for product_data in PRODUCT_DATA:
        if product_data["name"] in existing_names:
            continue

        category_name = product_data["category"]
        if category_name not in categories:
            logger.error(
                "Error while creating category",
                error=f"Категория '{category_name}' не найдена при импорте продукта '{product_data['name']}'",
            )
            raise ValueError(
                f"Категория '{category_name}' не найдена при импорте продукта '{product_data['name']}'"
            )

        product = Product(
            category_id=categories[category_name],
            name=product_data["name"],
            price=product_data["price"],
        )
        session.add(product)
    await session.commit()


async def seed_orders(session: AsyncSession):
    users = {
        user.email: user.id async for user in await session.stream_scalars(select(User))
    }
    products = {
        product.name: product.id
        async for product in await session.stream_scalars(select(Product))
    }

    # Получаем уже существующие заказы как множество кортежей (user_id, product_id, quantity)
    result = await session.execute(
        select(Order.user_id, Order.product_id, Order.quantity)
    )
    existing_orders = {(row.user_id, row.product_id, row.quantity) for row in result}

    for order_data in ORDER_DATA:
        user_email = order_data["user"]
        product_name = order_data["product"]
        quantity = order_data["quantity"]

        if user_email not in users:
            continue
        if product_name not in products:
            continue

        user_id = users[user_email]
        product_id = products[product_name]
        order_key = (user_id, product_id, quantity)

        if order_key in existing_orders:
            continue

        order = Order(
            user_id=users[user_email],
            product_id=products[product_name],
            quantity=order_data["quantity"],
            is_paid=order_data.get("is_paid", False),
        )
        session.add(order)
    await session.commit()


async def seed_all():
    async with async_session_maker() as session:
        try:
            await seed_business_elements(session)
        except Exception as e:
            await session.rollback()
            logger.error("Error while creating business elements", error=str(e))

        try:
            await seed_roles(session)
        except Exception as e:
            await session.rollback()
            logger.error("Error while creating seed_roles", error=str(e))

        try:
            await seed_access_rules(session)
        except Exception as e:
            await session.rollback()
            logger.error("Error while creating seed_access_rules", error=str(e))

        try:
            await seed_users(session)
        except Exception as e:
            await session.rollback()
            logger.error("Error while creating users", error=str(e))

        try:
            await seed_role_user(session)
        except Exception as e:
            await session.rollback()
            logger.error("Error while role_user", error=str(e))

        try:
            await seed_categories(session)
        except Exception as e:
            await session.rollback()
            logger.error("Error while creating categories", error=str(e))

        try:
            await seed_products(session)
        except Exception as e:
            await session.rollback()
            logger.error("Error while creating products", error=str(e))

        try:
            await seed_orders(session)
        except Exception as e:
            await session.rollback()
            logger.error("Error while creating orders", error=str(e))
