from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Role, BusinessElement, AccessRule, User, Category, Product, Order
from app.utils.sample_data import (
    BUSINESS_ELEMENTS_DATA,
    ROLES_DATA,
    ACCESS_RULES_DATA,
    USERS_DATA,
    CATEGORY_DATA,
    PRODUCT_DATA,
    ORDER_DATA,
)
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

    for business_element_data in BUSINESS_ELEMENTS_DATA:
        if business_element_data["name"] not in existing_names:
            session.add(BusinessElement(**business_element_data))
    await session.commit()


async def seed_access_rules(session: AsyncSession):
    roles = {role.name: role.id async for role in await session.stream_scalars(select(Role))}
    elements = {element.name: element.id async for element in await session.stream_scalars(select(BusinessElement))}

    result = await session.execute(select(AccessRule.role_id, AccessRule.businesselement_id))
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
    existing_emails = {email async for email in await session.stream_scalars(select(User.email))}
    roles = {role.name: role async for role in await session.stream_scalars(select(Role))}

    for user_data in USERS_DATA:
        if user_data["email"] in existing_emails:
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
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


async def seed_categories(session: AsyncSession):
    existing_names = {name async for name in await session.stream_scalars(select(Category.name))}

    for category_data in CATEGORY_DATA:
        if category_data["name"] not in existing_names:
            session.add(Category(**category_data))
    await session.commit()


async def seed_products(session: AsyncSession):
    categories = {category.name: category.id async for category in await session.stream_scalars(select(Category))}
    existing_names = {name async for name in await session.stream_scalars(select(Product.name))}

    for product_data in PRODUCT_DATA:
        if product_data["name"] in existing_names:
            continue

        category_name = product_data["category"]
        if category_name not in categories:
            raise ValueError(f"Категория '{category_name}' не найдена при импорте продукта '{product_data['name']}'")

        product = Product(
            category_id=categories[category_name],
            name=product_data["name"],
            price=product_data["price"],
        )
        session.add(product)
    await session.commit()


async def seed_orders(session: AsyncSession):
    users = {user.email: user.id async for user in await session.stream_scalars(select(User))}
    products = {product.name: product.id async for product in await session.stream_scalars(select(Product))}

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
        await seed_business_elements(session)
        await seed_roles(session)
        await seed_access_rules(session)
        await seed_users(session)
        await seed_categories(session)
        await seed_products(session)
        await seed_orders(session)
