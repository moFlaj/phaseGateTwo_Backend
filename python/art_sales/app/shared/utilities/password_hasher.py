import bcrypt

class PasswordHasher:
    @staticmethod
    def hash_password(plain_password: str) -> str:
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
