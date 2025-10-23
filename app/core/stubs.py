from uuid import uuid4
from app.core.enums import Permission
from app.schemas.permission import AccessContext


def create_fake_access_context():
    fake_uuid = uuid4()
    access = AccessContext(
        user_id=fake_uuid,
        permissions=[
            Permission.CREATE.value,
            Permission.READ_ALL.value,
            Permission.UPDATE_ALL.value,
            Permission.DELETE_ALL.value
        ]
    )
    return access
