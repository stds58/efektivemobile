from enum import Enum


class BusinessDomain(str, Enum):
    ACCESS_RULES = "access_rules"
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
