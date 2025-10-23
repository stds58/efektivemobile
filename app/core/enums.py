from enum import Enum


class BusinessDomain(str, Enum):
    ACCESS_RULES = "access_rule"
    CATEGORY = "category"
    PRODUCT = "product"
    ORDER = "order"
    USER = "user"
    USER_ROLES = "user_roles"
    FILE_UPLOAD = "fileupload"


class IsolationLevel(str, Enum):
    READ_COMMITTED = "READ COMMITTED"
    REPEATABLE_READ = "REPEATABLE READ"
    SERIALIZABLE = "SERIALIZABLE"


class Permission(str, Enum):
    CREATE = "create_permission"
    READ = "read_permission"
    READ_ALL = "read_all_permission"
    UPDATE = "update_permission"
    UPDATE_ALL = "update_all_permission"
    DELETE = "delete_permission"
    DELETE_ALL = "delete_all_permission"
