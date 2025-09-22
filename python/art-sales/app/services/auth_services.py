from app.dtos.requests.user_signup_request import UserSignupRequest
from app.dtos.responses.user_signup_response import UserSignupResponse
from app.exceptions.custom_exceptions import ValidationException, ResourceExistsException
from app.mappers.user_mapper import UserMapper
from app.persistence.user_repository import UserRepository
from app.utilities.password_hasher import PasswordHasher
from app.validators.user_validator import UserValidator


class AuthService:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def signup_user(self, request_dto: UserSignupRequest) -> UserSignupResponse:

        try:
            UserValidator.validate_signup(request_dto)
        except ValueError as ve:
            raise ValidationException(str(ve))

        if self.user_repository.find_by_email(request_dto.email):
            raise ResourceExistsException("Email already in use.")

        hashed_pw = self.password_hasher.hash_password(request_dto.password)

        user = UserMapper.dto_to_model(request_dto, hashed_pw)

        inserted_id = self.user_repository.insert_user(user)

        return UserSignupResponse(
            success=True,
            message="Account created successfully.",
            user_id=str(inserted_id)
        )
