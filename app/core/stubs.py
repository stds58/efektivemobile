from uuid import uuid4
from app.core.enums import Permission
from app.schemas.permission import AccessContext


def create_fake_access_context():
    fake_uuid = uuid4()
    access = AccessContext(
        user_id=fake_uuid,
        permissions=[Permission.READ_ALL.value, Permission.CREATE.value]
    )
    return access
