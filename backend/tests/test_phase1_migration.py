import re
from pathlib import Path

MIGRATIONS = Path(__file__).parents[2] / "backend" / "database" / "migrations"


def test_phase1_migrations_are_ordered_and_unique():
    names = sorted(path.name for path in MIGRATIONS.glob("*.sql"))
    assert names
    prefixes = [name.split("_", 1)[0] for name in names]
    assert prefixes == sorted(prefixes)
    assert len(prefixes) == len(set(prefixes))


def test_forward_migration_contains_all_phase1_tables_and_rls():
    sql = (MIGRATIONS / "202608020001_create_phase1_domain_schema.sql").read_text().lower()
    tables = {
        "learning_materials",
        "tutoring_sessions",
        "messages",
        "feedback",
        "research_participants",
        "anonymized_event_logs",
    }
    for table in tables:
        assert f"create table if not exists public.{table}" in sql
        assert f"alter table public.{table} enable row level security" in sql
    assert "create policy" not in sql


def test_forward_migration_links_model_telemetry_without_prompt_columns():
    sql = (MIGRATIONS / "202608020001_create_phase1_domain_schema.sql").read_text().lower()
    for column in ("session_id", "student_message_id", "assistant_message_id", "classroom_id"):
        assert re.search(rf"foreign key \({column}\) references public\.", sql)
    model_sql = (MIGRATIONS / "202607190001_create_model_requests.sql").read_text().lower()
    assert "prompt text" not in model_sql
    assert "response text" not in model_sql
