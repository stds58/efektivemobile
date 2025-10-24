from app.services.auth.blacklist_inmemory import TokenBlacklist, InMemoryTokenBlacklist


token_blacklist: TokenBlacklist = InMemoryTokenBlacklist()
