#app/validators/user_validator for sign up requests
import re


class UserValidator:

    @staticmethod
    def validate_signup(request_dto):
        errors = []

        request_dto.validate()

        if not request_dto.email or not re.match(r"[^@]+@[^@]+\.[^@]+", request_dto.email):
            errors.append("Invalid email format.")

        if not request_dto.password or len(request_dto.password) < 6:
            errors.append("Password must be at least 6 characters long.")

        if request_dto.role not in ("artist", "buyer"):
            errors.append("Role must be either 'artist' or 'buyer'.")


        if errors:
            raise ValueError("; ".join(errors))
