import bcrypt


def make_password(raw_password: str) -> str:
    """Хеширование пароля"""
    # Переводим пароль в байты
    password_bytes = raw_password.encode('utf-8')
    # Генерируем соль и хеш
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    # Декодируем в строку для хранения в CharField
    return hashed_password.decode('utf-8')


def check_password(raw_password, hashed_password: str) -> bool:
    """Проверка соответствия пароля хешу"""
    password_bytes = raw_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # bcrypt.checkpw сам извлечет соль из хеша и проверит совпадение
    return bcrypt.checkpw(password_bytes, hashed_bytes)