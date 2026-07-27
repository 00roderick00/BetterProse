from __future__ import annotations

import difflib
import re
from collections import Counter
from pathlib import Path

from betterprose.document import Document
from betterprose.models import FactLockAudit, LockedItem, RevisionResult, VoiceProfile
from betterprose.providers.base import AssessmentProvider

LOCK_PATTERNS: dict[str, re.Pattern[str]] = {
    "number": re.compile(r"(?<!\w)(?:\$|£|€)?\d[\d,]*(?:\.\d+)?%?(?!\w)"),
    "url": re.compile(r"https?://[^\s)>]+"),
    "quotation": re.compile(r"[\"“][^\"”\n]{2,}[\"”]"),
    "citation": re.compile(r"\[[A-Za-z0-9][^\]\n]{0,60}\]|\([A-Z][A-Za-z-]+,\s*\d{4}\)"),
}


def extract_locked_items(text: str) -> list[LockedItem]:
    items: list[LockedItem] = []
    for kind, pattern in LOCK_PATTERNS.items():
        items.extend(
            LockedItem(kind=kind, value=match.group(0)) for match in pattern.finditer(text)
        )
    return items


def audit_fact_lock(
    before: str,
    after: str,
    *,
    mode: str = "strict",
) -> FactLockAudit:
    before_items = extract_locked_items(before)
    after_items = extract_locked_items(after)
    before_counts = Counter((item.kind, item.value) for item in before_items)
    after_counts = Counter((item.kind, item.value) for item in after_items)
    removed: list[LockedItem] = []
    added: list[LockedItem] = []
    for (kind, value), count in (before_counts - after_counts).items():
        removed.extend(LockedItem(kind=kind, value=value) for _ in range(count))
    for (kind, value), count in (after_counts - before_counts).items():
        added.extend(LockedItem(kind=kind, value=value) for _ in range(count))
    warnings = []
    if removed:
        warnings.append("One or more locked items were removed or changed.")
    if added:
        warnings.append("One or more new claim-surface items were introduced.")
    if not before_items:
        warnings.append(
            "No numbers, URLs, quotations, or citation-like tokens were available to lock."
        )
    approved = not (mode == "strict" and (removed or added))
    return FactLockAudit(
        mode=mode,
        approved=approved,
        removed=removed,
        added=added,
        warnings=warnings,
    )


def revise_document(
    source_path: Path,
    document: Document,
    provider: AssessmentProvider,
    output_dir: Path,
    *,
    focus: list[str],
    audience: str | None,
    purpose: str | None,
    fact_lock_mode: str,
    voice_profile: VoiceProfile | None = None,
    voice_register: str | None = None,
) -> RevisionResult:
    draft = provider.revise(
        document,
        focus=focus,
        audience=audience,
        purpose=purpose,
        voice_profile=voice_profile,
        voice_register=voice_register,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = output_dir / f"{source_path.stem}.candidate{source_path.suffix}"
    candidate_path.write_text(draft.revised_text, encoding="utf-8")
    audit = audit_fact_lock(document.text, draft.revised_text, mode=fact_lock_mode)
    diff = "".join(
        difflib.unified_diff(
            document.text.splitlines(keepends=True),
            draft.revised_text.splitlines(keepends=True),
            fromfile=str(source_path),
            tofile=str(candidate_path),
        )
    )
    return RevisionResult(
        source_path=str(source_path),
        candidate_path=str(candidate_path),
        provider=provider.name,
        focus=focus,
        voice_profile=voice_profile.name if voice_profile else None,
        voice_version=voice_profile.version if voice_profile else None,
        voice_register=voice_register if voice_profile else None,
        change_summary=draft.change_summary,
        unresolved_issues=draft.unresolved_issues,
        audit=audit,
        diff=diff,
    )
