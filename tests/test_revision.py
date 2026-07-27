from betterprose.revision import audit_fact_lock, extract_locked_items


def test_extract_locked_items_finds_claim_surface() -> None:
    items = extract_locked_items(
        "The 2024 report says “results improved” (Jones, 2023). See https://example.com/report."
    )
    kinds = {item.kind for item in items}
    assert kinds == {"number", "quotation", "citation", "url"}


def test_strict_fact_lock_blocks_changed_number() -> None:
    audit = audit_fact_lock("Costs rose 12%.", "Costs rose 21%.", mode="strict")
    assert not audit.approved
    assert [item.value for item in audit.removed] == ["12%"]
    assert [item.value for item in audit.added] == ["21%"]


def test_advisory_fact_lock_reports_but_allows_change() -> None:
    audit = audit_fact_lock("Costs rose 12%.", "Costs rose 21%.", mode="advisory")
    assert audit.approved
    assert audit.warnings
