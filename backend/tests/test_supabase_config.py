import pytest
from pydantic import ValidationError

from app.core.config import Settings

PROJECT = "alpha-project"
OTHER_PROJECT = "beta-project"
URL = f"https://{PROJECT}.supabase.co"
PUBLISHABLE = "sb_publishable_test_placeholder"
SECRET = "sb_secret_test_placeholder"
DATABASE = f"postgresql://postgres:test-password@db.{PROJECT}.supabase.co:5432/postgres"


def settings(**values):
    return Settings(_env_file=None, supabase_url=URL, **values)


def test_modern_variables_only():
    result = settings(
        supabase_publishable_key=PUBLISHABLE,
        supabase_secret_key=SECRET,
        database_url=DATABASE,
    )
    assert result.supabase_effective_publishable_key.get_secret_value() == PUBLISHABLE
    assert result.supabase_effective_secret_key.get_secret_value() == SECRET


def test_legacy_variables_only():
    result = settings(
        supabase_anon_key=PUBLISHABLE,
        supabase_service_role_key=SECRET,
    )
    assert result.supabase_effective_publishable_key.get_secret_value() == PUBLISHABLE
    assert result.supabase_effective_secret_key.get_secret_value() == SECRET


def test_matching_modern_and_legacy_variables_are_accepted():
    result = settings(
        supabase_publishable_key=PUBLISHABLE,
        supabase_anon_key=PUBLISHABLE,
        supabase_secret_key=SECRET,
        supabase_service_role_key=SECRET,
    )
    assert result.supabase_effective_publishable_key.get_secret_value() == PUBLISHABLE
    assert result.supabase_effective_secret_key.get_secret_value() == SECRET


@pytest.mark.parametrize(
    ("values", "expected_names"),
    [
        (
            {"supabase_publishable_key": PUBLISHABLE, "supabase_anon_key": "legacy-different"},
            ("SUPABASE_PUBLISHABLE_KEY", "SUPABASE_ANON_KEY"),
        ),
        (
            {"supabase_secret_key": SECRET, "supabase_service_role_key": "legacy-different"},
            ("SUPABASE_SECRET_KEY", "SUPABASE_SERVICE_ROLE_KEY"),
        ),
    ],
)
def test_conflicting_modern_and_legacy_variables_fail_safely(values, expected_names):
    with pytest.raises(ValidationError) as caught:
        settings(**values)
    message = str(caught.value)
    assert all(name in message for name in expected_names)
    assert PUBLISHABLE not in message
    assert SECRET not in message
    assert "legacy-different" not in message


def test_mismatched_supabase_project_references_are_rejected():
    with pytest.raises(ValidationError, match="project reference mismatch") as caught:
        settings(
            supabase_jwt_issuer=f"https://{OTHER_PROJECT}.supabase.co/auth/v1",
            supabase_jwks_url=f"https://{OTHER_PROJECT}.supabase.co/auth/v1/.well-known/jwks.json",
        )
    assert PROJECT not in str(caught.value)
    assert OTHER_PROJECT not in str(caught.value)


def test_jwt_settings_are_derived_from_normalized_supabase_url():
    result = Settings(_env_file=None, supabase_url=URL + "/")
    assert result.supabase_url == URL
    assert result.supabase_jwt_issuer == f"{URL}/auth/v1"
    assert result.supabase_jwt_audience == "authenticated"
    assert result.supabase_jwks_url == f"{URL}/auth/v1/.well-known/jwks.json"


@pytest.mark.parametrize(
    ("field", "value", "expected_path"),
    [
        ("supabase_jwt_issuer", URL, "/auth/v1"),
        ("supabase_jwks_url", f"{URL}/auth/v1", "/auth/v1/.well-known/jwks.json"),
    ],
)
def test_jwt_urls_require_their_exact_safe_paths(field, value, expected_path):
    with pytest.raises(ValidationError, match=expected_path.replace("/", r"\/")):
        settings(**{field: value})


@pytest.mark.parametrize(
    "database_url",
    [
        "https://example.invalid/postgres",
        "DATABASE_URL=DATABASE_URL=postgresql://postgres:password@db.alpha-project.supabase.co/postgres",
        "postgresql://postgres:[YOUR-PASSWORD]@db.alpha-project.supabase.co/postgres",
        "postgresql://postgres:your_url_encoded_password@db.alpha-project.supabase.co/postgres",
        "postgresql://db.alpha-project.supabase.co/postgres",
        "postgresql://one/postgres postgresql://two/postgres",
    ],
)
def test_malformed_or_duplicated_database_url_is_rejected_without_echo(database_url):
    with pytest.raises(ValidationError) as caught:
        settings(database_url=database_url)
    assert database_url not in str(caught.value)


def test_public_and_privileged_key_roles_cannot_be_reversed():
    with pytest.raises(ValidationError, match="privileged key supplied"):
        settings(supabase_publishable_key=SECRET)
    with pytest.raises(ValidationError, match="publishable key supplied"):
        settings(supabase_secret_key=PUBLISHABLE)
