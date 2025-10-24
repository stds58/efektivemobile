from uuid import uuid4
from app.core.enums import Permission
from app.schemas.permission import AccessContext


FAKE_ACCESS_CONTEXT = AccessContext(
    user_id=uuid4(),
    permissions=[
        Permission.CREATE.value,
        Permission.READ_ALL.value,
        Permission.UPDATE_ALL.value,
        Permission.DELETE_ALL.value,
    ],
)
