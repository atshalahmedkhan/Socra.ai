import os
import shutil
import subprocess
from pathlib import Path

import pytest

NODE = shutil.which("node")
SCRIPT = Path(__file__).parents[3] / "scripts" / "generate-config.js"
URL = "https://example-project.supabase.co"
KEY = "sb_publishable_test_placeholder"


def run_build(tmp_path, **variables):
    if not NODE:
        pytest.skip("Node.js is not installed")
    env = {
        key: value for key, value in os.environ.items() if "SUPABASE" not in key and not key.startswith("NEXT_PUBLIC_")
    }
    env.update(variables)
    return subprocess.run(
        [NODE, str(SCRIPT)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_frontend_modern_variables_only(tmp_path):
    result = run_build(
        tmp_path,
        NEXT_PUBLIC_SUPABASE_URL=URL,
        NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=KEY,
    )
    assert result.returncode == 0
    assert (tmp_path / "config.js").exists()


def test_frontend_legacy_variables_only(tmp_path):
    result = run_build(
        tmp_path,
        NEXT_PUBLIC_SUPABASE_URL=URL,
        NEXT_PUBLIC_SUPABASE_ANON_KEY=KEY,
    )
    assert result.returncode == 0


def test_frontend_matching_modern_and_legacy_values(tmp_path):
    result = run_build(
        tmp_path,
        NEXT_PUBLIC_SUPABASE_URL=URL,
        NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=KEY,
        NEXT_PUBLIC_SUPABASE_ANON_KEY=KEY,
    )
    assert result.returncode == 0


def test_frontend_conflicting_aliases_fail_without_values(tmp_path):
    modern = "sb_publishable_modern_test"
    legacy = "sb_publishable_legacy_test"
    result = run_build(
        tmp_path,
        NEXT_PUBLIC_SUPABASE_URL=URL,
        NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=modern,
        NEXT_PUBLIC_SUPABASE_ANON_KEY=legacy,
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY" in combined
    assert "NEXT_PUBLIC_SUPABASE_ANON_KEY" in combined
    assert modern not in combined
    assert legacy not in combined


def test_frontend_rejects_privileged_key(tmp_path):
    privileged = "sb_secret_test_placeholder"
    result = run_build(
        tmp_path,
        NEXT_PUBLIC_SUPABASE_URL=URL,
        NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=privileged,
    )
    assert result.returncode != 0
    assert privileged not in result.stdout + result.stderr
