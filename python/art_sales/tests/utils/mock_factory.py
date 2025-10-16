from unittest.mock import MagicMock

def make_auth_mocks():
    """Mocks specific to AuthService dependencies."""
    return {
        "user_repo": MagicMock(name="UserRepositoryMock"),
        "verification_repo": MagicMock(name="VerificationRepositoryMock"),
        "password_hasher": MagicMock(name="PasswordHasherMock"),
        "email_service": MagicMock(name="EmailServiceMock"),
    }


def make_buyer_mocks():
    """Mocks specific to BuyerService dependencies."""
    return {
        "buyer_repo": MagicMock(name="BuyerRepositoryMock"),
        "auth_service": MagicMock(name="AuthServiceMock"),
    }


def make_artist_mocks():
    """Mocks specific to ArtistService dependencies."""
    return {
        "artist_repo": MagicMock(name="ArtistRepositoryMock"),
        "auth_service": MagicMock(name="AuthServiceMock"),
    }


def make_common_mock(name: str):
    """Utility to quickly generate a single generic mock with a readable name."""
    return MagicMock(name=name)
