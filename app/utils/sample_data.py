
BUSINESS_ELEMENTS_DATA = [
        {"name": "user", "description": "Управление пользователями"},
        {"name": "product", "description": "Управление товарами"},
        {"name": "order", "description": "Управление заказами"},
        {"name": "category", "description": "Управление категориями"},
        {"name": "access_rule", "description": "Управление правами доступа"},
        {"name": "user_roles", "description": "Управление ролями"},
    ]

ROLES_DATA = [
    {"name": "admin", "description": "администратор"},
    {"name": "manager", "description": "манагер"},
    {"name": "user", "description": "пользователь"},
]

ACCESS_RULES_DATA = [
    {
        "role_name": "admin",
        "businesselement_name": "user",
        "read_permission": True,
        "read_all_permission": True,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": True,
        "delete_permission": True,
        "delete_all_permission": True
     },
    {
        "role_name": "admin",
        "businesselement_name": "product",
        "read_permission": True,
        "read_all_permission": True,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": True,
        "delete_permission": True,
        "delete_all_permission": True
    },
    {
        "role_name": "admin",
        "businesselement_name": "order",
        "read_permission": True,
        "read_all_permission": True,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": True,
        "delete_permission": True,
        "delete_all_permission": True
    },
    {
        "role_name": "admin",
        "businesselement_name": "category",
        "read_permission": True,
        "read_all_permission": True,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": True,
        "delete_permission": True,
        "delete_all_permission": True
    },
    {
        "role_name": "admin",
        "businesselement_name": "access_rule",
        "read_permission": True,
        "read_all_permission": True,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": True,
        "delete_permission": True,
        "delete_all_permission": True
    },
    {
        "role_name": "admin",
        "businesselement_name": "user_roles",
        "read_permission": True,
        "read_all_permission": True,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": True,
        "delete_permission": True,
        "delete_all_permission": True
    },

    {
        "role_name": "manager",
        "businesselement_name": "user",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": True,
        "delete_all_permission": False
    },
    {
        "role_name": "manager",
        "businesselement_name": "product",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": True,
        "delete_all_permission": False
    },
    {
        "role_name": "manager",
        "businesselement_name": "order",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": True,
        "delete_all_permission": False
    },
    {
        "role_name": "manager",
        "businesselement_name": "category",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": True,
        "delete_all_permission": False
    },
    {
        "role_name": "manager",
        "businesselement_name": "access_rule",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": True,
        "delete_all_permission": False
    },
    {
        "role_name": "manager",
        "businesselement_name": "user_roles",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": True,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": True,
        "delete_all_permission": False
    },

    {
        "role_name": "user",
        "businesselement_name": "user",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": False,
        "update_permission": False,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False
    },
    {
        "role_name": "user",
        "businesselement_name": "product",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": False,
        "update_permission": False,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False
    },
    {
        "role_name": "user",
        "businesselement_name": "order",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": False,
        "update_permission": True,
        "update_all_permission": False,
        "delete_permission": True,
        "delete_all_permission": False
    },
    {
        "role_name": "user",
        "businesselement_name": "category",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": False,
        "update_permission": False,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False
    },
    {
        "role_name": "user",
        "businesselement_name": "access_rule",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": False,
        "update_permission": False,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False
    },
    {
        "role_name": "user",
        "businesselement_name": "user_roles",
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": False,
        "update_permission": False,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False
    },
]

USERS_DATA = [
    {
        "email": "admin@example.com",
        "password": "admin@example.com",
        "first_name": "Админ",
        "last_name": "Системный",
        "role_names": ["admin"]
    },
    {
        "email": "manager@example.com",
        "password": "manager@example.com",
        "first_name": "manager",
        "last_name": "manager",
        "role_names": ["manager"]
    },
    {
        "email": "user@example.com",
        "password": "user@example.com",
        "first_name": "Обычный",
        "last_name": "Пользователь",
        "role_names": ["user"]
    },
]
