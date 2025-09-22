from app.models.user_model import User


class UserMapper:
    @staticmethod
    def dto_to_model(dto, hashed_password: str) -> User:
        return User(
            name=dto.name,
            email=dto.email,
            password=hashed_password,
            role=dto.role
        )
