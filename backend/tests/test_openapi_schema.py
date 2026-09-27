"""The generated OpenAPI contract stays warning-free and committed (ADS-TECH-001-01).

These support TECH-001; its test case, TC-TECH-001-01, is the contract test in
test_contract.py.
"""

from pathlib import Path

from django.core.management import call_command

COMMITTED_SCHEMA = Path(__file__).resolve().parents[1] / "openapi.yaml"


def test_openapi_schema_generates_without_warnings_and_matches_the_committed_file(tmp_path):
    generated = tmp_path / "openapi.yaml"

    # --fail-on-warn turns any undocumented or unresolvable endpoint into an error.
    call_command("spectacular", "--file", str(generated), "--validate", "--fail-on-warn")

    assert generated.read_text() == COMMITTED_SCHEMA.read_text(), (
        "backend/openapi.yaml is stale: run "
        "`python manage.py spectacular --file openapi.yaml` and commit the result."
    )
