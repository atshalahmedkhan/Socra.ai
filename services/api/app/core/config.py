import re
from enum import StrEnum
from functools import lru_cache
from urllib.parse import urlparse

from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


SUPABASE_URL_PATTERN = re.compile(r"^https://([a-z0-9-]+)\.supabase\.co$")
POSTGRES_SCHEME_PATTERN = re.compile(r"postgres(?:ql)?://", re.IGNORECASE)


def _secret_value(value: SecretStr | None) -> str | None:
    return value.get_secret_value() if value else None


def _resolve_compatible_secret(
    modern_name: str,
    modern: SecretStr | None,
    legacy_name: str,
    legacy: SecretStr | None,
) -> SecretStr | None:
    modern_value = _secret_value(modern)
    legacy_value = _secret_value(legacy)
    if modern_value and legacy_value and modern_value != legacy_value:
        raise ValueError(f"Conflicting configuration: {modern_name} and {legacy_name}")
    return modern or legacy


def _supabase_project_ref(url: str, variable_name: str) -> tuple[str, str]:
    normalized = url.rstrip("/")
    match = SUPABASE_URL_PATTERN.fullmatch(normalized)
    if not match:
        raise ValueError(f"Invalid {variable_name}: expected https://<project-ref>.supabase.co")
    return normalized, match.group(1)


def _database_project_ref(database_url: str) -> str | None:
    if "DATABASE_URL=" in database_url.upper():
        raise ValueError("Invalid DATABASE_URL: duplicated variable assignment")
    if len(POSTGRES_SCHEME_PATTERN.findall(database_url)) != 1:
        raise ValueError("Invalid DATABASE_URL: expected exactly one PostgreSQL URI")
    try:
        parsed = urlparse(database_url)
        hostname = parsed.hostname
        username = parsed.username
        password = parsed.password
    except ValueError:
        raise ValueError("Invalid DATABASE_URL: expected a PostgreSQL URI") from None
    if (
        parsed.scheme not in {"postgres", "postgresql"}
        or not hostname
        or not parsed.path
        or username is None
        or password is None
    ):
        raise ValueError("Invalid DATABASE_URL: expected a PostgreSQL URI")
    lowered = database_url.lower()
    if any(
        marker in lowered
        for marker in (
            "[your-password]",
            "<your-password>",
            "your_actual_database_password",
            "your_url_encoded_password",
        )
    ):
        raise ValueError("Invalid DATABASE_URL: unresolved password placeholder")
    hostname = hostname.lower()
    direct = re.fullmatch(r"db\.([a-z0-9-]+)\.supabase\.co", hostname)
    if direct:
        return direct.group(1)
    if username:
        pooler = re.fullmatch(r"postgres\.([a-z0-9-]+)", username.lower())
        if pooler and hostname.endswith(".pooler.supabase.com"):
            return pooler.group(1)
    return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        hide_input_in_errors=True,
    )

    app_env: AppEnvironment = Field(
        AppEnvironment.DEVELOPMENT,
        validation_alias=AliasChoices("APP_ENV", "app_env"),
    )
    app_name: str = "Socra"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "console"
    api_v1_prefix: str = "/api/v1"
    request_id_header: str = "X-Request-ID"
    internal_routes_enabled: bool = False
    internal_service_token: SecretStr | None = None
    frontend_url: str = "http://localhost:3000"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]
    database_url: SecretStr | None = None
    supabase_url: str | None = None
    supabase_publishable_key: SecretStr | None = None
    supabase_anon_key: SecretStr | None = None
    supabase_secret_key: SecretStr | None = None
    supabase_service_role_key: SecretStr | None = None
    supabase_storage_bucket: str | None = None
    supabase_jwt_issuer: str | None = None
    supabase_jwt_audience: str = "authenticated"
    supabase_jwks_url: str | None = None
    supabase_jwt_secret: SecretStr | None = None
    internal_smoke_token: SecretStr | None = None
    research_data_collection_enabled: bool = False

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value):
        return value.split(",") if isinstance(value, str) else value

    @field_validator(
        "database_url",
        "supabase_url",
        "supabase_publishable_key",
        "supabase_anon_key",
        "supabase_secret_key",
        "supabase_service_role_key",
        "supabase_storage_bucket",
        "supabase_jwt_issuer",
        "supabase_jwks_url",
        "supabase_jwt_secret",
        mode="before",
    )
    @classmethod
    def empty_optional_value_is_none(cls, value):
        return None if value == "" else value

    model_client_enabled: bool = True
    model_provider: str = "vllm"
    model_mock_scenario: str = "success"
    base_model_name: str = "google/gemma-3-4b-it"
    model_primary_name: str = "gemma-3-4b-base"
    model_stable_name: str = "socra-gemma-v0"
    model_version: str = "socra-gemma-v1"
    prompt_version: str = "socra-v1"
    model_primary_url: str = "http://model-primary:8001"
    model_primary_api_key: SecretStr | None = None
    model_fallback_enabled: bool = False
    model_fallback_url: str = "http://model-fallback:8002"
    model_fallback_api_key: SecretStr | None = None
    model_fallback_name: str = "socra-gemma-v0"
    model_primary_adapter_enabled: bool = False
    model_stable_adapter_enabled: bool = False
    model_connect_timeout_seconds: float = 5
    model_read_timeout_seconds: float = 30
    model_write_timeout_seconds: float = 5
    model_pool_timeout_seconds: float = 5
    model_total_deadline_seconds: float = 35
    model_max_retries: int = Field(1, ge=0, le=1)
    model_retry_base_delay_ms: int = 250
    model_circuit_breaker_failure_threshold: int = 3
    model_circuit_breaker_reset_seconds: float = 30
    model_max_output_tokens: int = Field(128, ge=1, le=2048)
    model_temperature: float = Field(0.4, ge=0, le=2)
    model_top_p: float = Field(0.9, gt=0, le=1)
    model_max_concurrency: int = Field(1, ge=1)
    model_health_timeout_seconds: float = 3
    model_deep_health_enabled: bool = False

    @model_validator(mode="after")
    def validate_secrets(self):
        publishable_key = _resolve_compatible_secret(
            "SUPABASE_PUBLISHABLE_KEY",
            self.supabase_publishable_key,
            "SUPABASE_ANON_KEY",
            self.supabase_anon_key,
        )
        secret_key = _resolve_compatible_secret(
            "SUPABASE_SECRET_KEY",
            self.supabase_secret_key,
            "SUPABASE_SERVICE_ROLE_KEY",
            self.supabase_service_role_key,
        )
        if _secret_value(publishable_key) and _secret_value(publishable_key).startswith("sb_secret_"):
            raise ValueError("Invalid publishable-key configuration: privileged key supplied")
        if _secret_value(secret_key) and _secret_value(secret_key).startswith("sb_publishable_"):
            raise ValueError("Invalid privileged-key configuration: publishable key supplied")
        object.__setattr__(self, "supabase_publishable_key", publishable_key)
        object.__setattr__(self, "supabase_secret_key", secret_key)

        project_refs: dict[str, str] = {}
        if self.supabase_url:
            normalized_url, project_ref = _supabase_project_ref(self.supabase_url, "SUPABASE_URL")
            object.__setattr__(self, "supabase_url", normalized_url)
            project_refs["SUPABASE_URL"] = project_ref
            object.__setattr__(
                self,
                "supabase_jwt_issuer",
                self.supabase_jwt_issuer or f"{normalized_url}/auth/v1",
            )
            object.__setattr__(
                self,
                "supabase_jwks_url",
                self.supabase_jwks_url or f"{normalized_url}/auth/v1/.well-known/jwks.json",
            )

        for name, value, expected_path in (
            ("SUPABASE_JWT_ISSUER", self.supabase_jwt_issuer, "/auth/v1"),
            (
                "SUPABASE_JWKS_URL",
                self.supabase_jwks_url,
                "/auth/v1/.well-known/jwks.json",
            ),
        ):
            if value:
                parsed = urlparse(value)
                match = re.fullmatch(r"([a-z0-9-]+)\.supabase\.co", parsed.hostname or "")
                if not match and self.supabase_url:
                    raise ValueError(f"Invalid {name}: expected a Supabase project URL")
                if self.supabase_url and (
                    parsed.scheme != "https"
                    or parsed.path.rstrip("/") != expected_path
                    or parsed.params
                    or parsed.query
                    or parsed.fragment
                ):
                    raise ValueError(f"Invalid {name}: expected Supabase path {expected_path}")
                if match:
                    project_refs[name] = match.group(1)

        if self.database_url:
            database_ref = _database_project_ref(self.database_url.get_secret_value())
            if database_ref:
                project_refs["DATABASE_URL"] = database_ref

        if len(set(project_refs.values())) > 1:
            raise ValueError("Supabase project reference mismatch between: " + ", ".join(sorted(project_refs)))

        if self.app_env == AppEnvironment.PRODUCTION and self.model_provider == "mock":
            raise ValueError("MODEL_PROVIDER=mock is not allowed in production")
        if self.app_env in {AppEnvironment.STAGING, AppEnvironment.PRODUCTION}:
            if self.debug or "*" in self.cors_allowed_origins or self.internal_routes_enabled:
                raise ValueError("Unsafe application settings for staging/production")
            missing = []
            for name, value in (
                ("SUPABASE_SECRET_KEY or SUPABASE_SERVICE_ROLE_KEY", secret_key),
                ("DATABASE_URL", self.database_url),
                ("SUPABASE_JWT_ISSUER", self.supabase_jwt_issuer),
            ):
                if not value:
                    missing.append(name)
            if not (self.supabase_jwks_url or self.supabase_jwt_secret):
                missing.append("SUPABASE_JWKS_URL or SUPABASE_JWT_SECRET")
            if missing:
                raise ValueError("Missing required configuration: " + ", ".join(missing))
        if self.app_env == AppEnvironment.PRODUCTION and self.model_client_enabled:
            if not self.model_primary_api_key:
                raise ValueError("MODEL_PRIMARY_API_KEY is required in production")
            if self.model_fallback_enabled and not self.model_fallback_api_key:
                raise ValueError("MODEL_FALLBACK_API_KEY is required when fallback is enabled")
        return self

    @property
    def environment(self) -> str:
        return self.app_env.value

    @property
    def service_version(self) -> str:
        return self.app_version

    def missing_required(self) -> list[str]:
        """Return canonical environment names that are not configured."""
        values = {
            "SUPABASE_URL": self.supabase_url,
            "SUPABASE_SERVICE_ROLE_KEY": self.supabase_effective_secret_key,
            "DATABASE_URL": self.database_url,
            "MODEL_SERVER_URL": self.model_primary_url,
            "MODEL_NAME": self.model_primary_name,
            "MODEL_VERSION": self.model_version,
        }
        return [name for name, value in values.items() if not value]

    def validate_required(self) -> None:
        """Keep the canonical scaffold's development/production validation contract."""
        missing = self.missing_required()
        if missing and self.app_env != AppEnvironment.DEVELOPMENT:
            raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

    @property
    def supabase_effective_publishable_key(self) -> SecretStr | None:
        return self.supabase_publishable_key

    @property
    def supabase_effective_secret_key(self) -> SecretStr | None:
        return self.supabase_secret_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
