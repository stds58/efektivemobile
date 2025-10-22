from fastapi import Depends
from app.dependencies.get_db import auth_db_context
from app.core.enums import BusinessDomain, IsolationLevel


def private_route_dependency(
    business_element: BusinessDomain,
    isolation_level: str = IsolationLevel.READ_COMMITTED,
):
    """
    Унифицированная зависимость для приватных ручек.
    Обеспечивает:
        авторизацию по JWT,
        сессию БД с нужным уровнем изоляции,
        контекст доступа (user_id, permissions),
    """
    return Depends(
        auth_db_context(
            business_element=business_element,
            isolation_level=isolation_level,
        )
    )
