#!/usr/bin/env python3
"""Self-contained validator for the Nexus OS TARGET-STATE contracts.

This harness is intentionally dependency-light (jsonschema + referencing + pyyaml)
and does NOT require any Nexus OS runtime code to exist. It:

  1. Loads every JSON Schema under docs/schemas/v1alpha1 and docs/schemas/v1alpha2
     into a referencing.Registry keyed by each schema's absolute ``$id`` so that
     cross-version ``$ref`` (absolute) and same-directory ``$ref`` (relative) both
     resolve.
  2. Asserts every schema is itself a valid Draft 2020-12 schema.
  3. Validates every positive fixture in examples/index.json against its schema.
  4. Asserts every negative fixture in examples/invalid/index.json is REJECTED.
  5. Asserts the Personal Local Stack v1 product invariants approved for v1:
       - no Hub dependency
       - fixed stack identity (personal-local-v1)
       - one-or-both provider secret refs (anthropic/openai, by reference only)
       - no plaintext secret values anywhere in the contracts
       - public packs accessible without a Hub account / entitlement
       - the assistant handoff Markdown is never the machine source of truth

Run: python3 tests/validate_contracts.py
Exit code 0 = all checks passed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = REPO_ROOT / "docs" / "schemas"
EXAMPLES = SCHEMA_ROOT / "examples"
INVALID = EXAMPLES / "invalid"

FORBIDDEN_SECRET_KEYS = {"value", "secret", "plaintext", "ciphertext", "api_key", "token", "key"}

failures: list[str] = []
passes = 0


def record_pass(msg: str) -> None:
    global passes
    passes += 1
    print(f"  ok   {msg}")


def record_fail(msg: str) -> None:
    failures.append(msg)
    print(f"  FAIL {msg}")


def load_doc(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return json.loads(text)


def build_registry() -> tuple[Registry, dict[str, dict]]:
    """Register every schema by its $id; return the registry and an id->schema map."""
    registry = Registry()
    by_id: dict[str, dict] = {}
    for schema_path in sorted(SCHEMA_ROOT.glob("v1alpha*/*.schema.json")):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        sid = schema["$id"]
        resource = Resource(contents=schema, specification=DRAFT202012)
        registry = registry.with_resource(uri=sid, resource=resource)
        by_id[sid] = schema
    return registry.crawl(), by_id


def schema_id_for(version: str, schema_file: str) -> str:
    return f"https://schemas.nexusos.dev/{version}/{schema_file}"


def validator_for(version: str, schema_file: str, registry: Registry) -> Draft202012Validator:
    sid = schema_id_for(version, schema_file)
    schema = registry.get_or_retrieve(sid).value.contents
    return Draft202012Validator(schema, registry=registry)


def check_schemas_are_valid(by_id: dict[str, dict]) -> None:
    print("[1] schemas are valid Draft 2020-12")
    for sid, schema in sorted(by_id.items()):
        try:
            Draft202012Validator.check_schema(schema)
            record_pass(sid.rsplit("/", 1)[-1])
        except SchemaError as exc:
            record_fail(f"{sid}: {exc.message}")


def check_positive(registry: Registry) -> None:
    print("[2] positive fixtures validate")
    index = load_doc(EXAMPLES / "index.json")
    for case in index["cases"]:
        version = case.get("version", "v1alpha1")
        validator = validator_for(version, case["schema"], registry)
        doc = load_doc(EXAMPLES / case["example"])
        errors = sorted(validator.iter_errors(doc), key=lambda e: e.path)
        if errors:
            record_fail(f"{case['example']} :: {errors[0].message}")
        else:
            record_pass(case["example"])


def check_negative(registry: Registry) -> None:
    print("[3] negative fixtures are rejected")
    index = load_doc(INVALID / "index.json")
    for case in index["cases"]:
        version = case.get("version", "v1alpha1")
        validator = validator_for(version, case["schema"], registry)
        doc = load_doc(INVALID / case["example"])
        if validator.is_valid(doc):
            record_fail(f"{case['example']} unexpectedly VALIDATED (should fail: {case['reason']})")
        else:
            record_pass(f"{case['example']} rejected")


def _walk(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield path, k, v
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")


def check_invariants() -> None:
    print("[4] Personal Local Stack v1 product invariants")
    stack = load_doc(EXAMPLES / "personal-stack.personal-local-v1.example.json")
    spec = stack["spec"]

    # fixed stack identity
    (record_pass if stack["metadata"]["stack_id"] == "personal-local-v1" else record_fail)(
        "fixed stack identity == personal-local-v1"
    )

    # no Hub dependency
    no_hub = (
        spec["hub"] == "none"
        and spec["operator"] == "absent"
        and spec["packs"]["requires_hub_account"] is False
    )
    (record_pass if no_hub else record_fail)("no Hub dependency (hub=none, operator=absent, requires_hub_account=false)")

    # one-or-both provider refs, providers restricted to anthropic/openai, by reference only
    providers = spec["llm"]["providers"]
    names = {p["provider"] for p in providers}
    one_or_both = 1 <= len(providers) <= 2 and names <= {"anthropic", "openai"}
    (record_pass if one_or_both else record_fail)("one-or-both provider secret refs (anthropic/openai)")
    ref_only = all(
        isinstance(p.get("secret_ref"), str) and not (FORBIDDEN_SECRET_KEYS & set(p.keys()))
        for p in providers
    )
    (record_pass if ref_only else record_fail)("providers carry secret_ref only, never a value")

    # public packs without entitlement
    packs_ok = spec["packs"]["public_lanes_enabled"] is True and spec["packs"]["requires_hub_account"] is False
    (record_pass if packs_ok else record_fail)("public packs accessible without entitlement")

    # boundaries all false
    boundaries_ok = all(v is False for v in spec["boundaries"].values())
    (record_pass if boundaries_ok else record_fail)("all Personal boundaries pinned false")

    # single runtime process embeds API + reconciliation operator + Console
    components_ok = spec["runtime"]["components"] == ["api", "reconciliation_operator", "console"]
    (record_pass if components_ok else record_fail)(
        "one runtime process embeds [api, reconciliation_operator, console]"
    )

    # loopback bind fixed at 127.0.0.1:8787
    ports = spec["runtime"]["ports"]
    bind_ok = (
        len(ports) == 1
        and ports[0]["bind_host"] == "127.0.0.1"
        and ports[0]["container_port"] == 8787
        and ports[0]["host_port"] == 8787
    )
    (record_pass if bind_ok else record_fail)("runtime bound exactly to 127.0.0.1:8787")

    # SQLite WAL at exactly /data/nexus.db
    pers = spec["persistence"]
    db_ok = (
        pers["engine"] == "sqlite"
        and pers["encryption_at_rest"] is True
        and pers["db_path"] == "/data/nexus.db"
        and pers["journal_mode"] == "WAL"
    )
    (record_pass if db_ok else record_fail)("SQLite WAL at exactly /data/nexus.db")

    # artifact storage at exactly /data/artifacts
    storage_ok = spec["storage"]["blobs"] == "local_filesystem" and spec["storage"]["path"] == "/data/artifacts"
    (record_pass if storage_ok else record_fail)("artifact storage at exactly /data/artifacts")

    # deterministic provider order, one retry, no provider fallback, distinct providers
    llm = spec["llm"]
    order_ok = llm["priority"] == ["anthropic", "openai"]
    (record_pass if order_ok else record_fail)("deterministic provider order == [anthropic, openai]")
    provider_names = [p["provider"] for p in providers]
    unique_ok = len(provider_names) == len(set(provider_names))
    (record_pass if unique_ok else record_fail)("each configured provider appears at most once")
    retry_ok = llm["retry"]["max_retries"] == 1
    (record_pass if retry_ok else record_fail)("exactly one retry per provider request (max_retries == 1)")
    fallback_ok = llm["provider_fallback"] is False
    (record_pass if fallback_ok else record_fail)("no fallback to a different provider (provider_fallback == false)")

    # no plaintext secret values anywhere in the Personal bootstrap contracts.
    # Scope: the secret-carrying Personal fixtures (LLM connector keys / secret bundle).
    # Public cryptographic signatures (signature.value) are intentionally public and out of scope.
    secret_bearing = [
        "personal-stack.personal-local-v1.example.json",
        "assistant-handoff.personal-local.example.json",
        "secret-bundle-ref.personal.example.json",
    ]
    leaks: list[str] = []
    for name in secret_bearing:
        doc = load_doc(EXAMPLES / name)
        for path, key, val in _walk(doc):
            if key in FORBIDDEN_SECRET_KEYS and isinstance(val, str) and val:
                leaks.append(f"{name}{path}.{key}")
    (record_pass if not leaks else record_fail)(
        "no plaintext secret values in Personal bootstrap fixtures" + (f" (leaks: {leaks})" if leaks else "")
    )

    # handoff markdown is never the source of truth
    handoff = load_doc(EXAMPLES / "assistant-handoff.personal-local.example.json")
    md = handoff["spec"]["setup_md"]
    md_ok = md["is_source_of_truth"] is False and md["contains_plaintext_secrets"] is False
    (record_pass if md_ok else record_fail)("handoff SETUP.md is not source of truth and holds no plaintext secrets")


def main() -> int:
    registry, by_id = build_registry()
    check_schemas_are_valid(by_id)
    check_positive(registry)
    check_negative(registry)
    check_invariants()
    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s) failed, {passes} passed")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASSED: {passes} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
