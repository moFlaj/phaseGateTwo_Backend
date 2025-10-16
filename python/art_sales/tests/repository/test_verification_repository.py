import pytest
from datetime import datetime
from app.auth.domain.verification_model import Verification
from app.auth.persistence.verification_repository import VerificationRepository


@pytest.fixture(autouse=True)
def clear_verification_collection(app):
    """
    Automatically clear the email_verifications collection before and after each test.
    """
    with app.app_context():
        coll = VerificationRepository._get_collection()
        coll.delete_many({})
    yield
    with app.app_context():
        coll = VerificationRepository._get_collection()
        coll.delete_many({})


def test_save_and_find_verification(app):
    """
    Should save a verification record and find it by email.
    """
    with app.app_context():
        verification = Verification(email="alice@example.com", code="123456", created_at=datetime.utcnow())
        VerificationRepository.save(verification)

        found = VerificationRepository.find_by_email("alice@example.com")
        assert found is not None
        assert found["email"] == "alice@example.com"
        assert found["code"] == "123456"


def test_upsert_overwrites_existing_record(app):
    """
    Should replace an existing verification record when saving with the same email.
    """
    with app.app_context():
        v1 = Verification(email="bob@example.com", code="111111")
        v2 = Verification(email="bob@example.com", code="222222")

        VerificationRepository.save(v1)
        VerificationRepository.save(v2)

        found = VerificationRepository.find_by_email("bob@example.com")
        assert found is not None
        assert found["code"] == "222222"  # ✅ confirms replace_one upsert behavior


def test_delete_by_email_removes_record(app):
    """
    Should delete verification record by email.
    """
    with app.app_context():
        v = Verification(email="carol@example.com", code="333333")
        VerificationRepository.save(v)

        VerificationRepository.delete_by_email("carol@example.com")

        assert VerificationRepository.find_by_email("carol@example.com") is None


def test_ttl_and_unique_indexes_exist(app):
    """
    Should ensure TTL (5 minutes) and unique index on 'email' exist.
    """
    with app.app_context():
        coll = VerificationRepository._get_collection()
        indexes = coll.index_information()

        # Find TTL index
        ttl_index = next((idx for idx in indexes.values() if "expireAfterSeconds" in idx), None)
        assert ttl_index is not None, "TTL index missing"
        assert ttl_index["expireAfterSeconds"] == 300

        # Ensure unique index on email
        email_index = next((idx for idx in indexes.values() if idx["key"][0][0] == "email"), None)
        assert email_index is not None, "Unique index on email missing"
        assert email_index.get("unique", False) is True
