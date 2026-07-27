from __future__ import annotations

import re
import statistics

from betterprose.document import WORD, Document
from betterprose.models import (
    AssessmentDraft,
    CriterionFinding,
    Evidence,
    RevisionDraft,
    Rubric,
    VoiceProfile,
)

SIGNALS: dict[str, tuple[str, ...]] = {
    "motive": ("problem", "risk", "need", "because", "although", "however", "?"),
    "controlling_idea": ("should", "must", "argue", "therefore", "because", "will"),
    "development": ("because", "therefore", "thus", "so that", "means", "shows", "which"),
    "support": ("according", "for example", "such as", "%", "data", "study", "report"),
    "complexity": ("however", "although", "but", "yet", "may", "might", "critics", "risk"),
    "cohesion": ("this", "these", "that", "because", "however", "therefore", "also"),
}


class LocalProvider:
    name = "local"
    model = None

    def assess(
        self,
        document: Document,
        rubric: Rubric,
        *,
        audience: str | None,
        purpose: str | None,
    ) -> AssessmentDraft:
        findings = [
            self._finding(criterion.id, document, audience=audience, purpose=purpose)
            for criterion in rubric.criteria
        ]
        ranked = sorted(findings, key=lambda item: item.rating)
        strengths = [
            f"{item.criterion_id.replace('_', ' ').title()}: {item.rationale}"
            for item in sorted(findings, key=lambda item: item.rating, reverse=True)[:2]
        ]
        priorities = [
            f"{item.criterion_id.replace('_', ' ').title()}: {item.revision_action}"
            for item in ranked[:3]
        ]
        return AssessmentDraft(
            reader_account=(
                "The offline reader mapped the document's paragraphs, sentences, and visible "
                "support signals. Its judgments are deliberately conservative because local "
                "measurements cannot establish insight, truth, or rhetorical success."
            ),
            principal_strengths=strengths,
            priority_revisions=priorities,
            integrity_status="review_needed",
            integrity_notes=[
                "Offline mode does not retrieve or verify sources.",
                "Factual truth and quotation accuracy require human or source-backed review.",
            ],
            findings=findings,
        )

    def _finding(
        self,
        criterion_id: str,
        document: Document,
        *,
        audience: str | None,
        purpose: str | None,
    ) -> CriterionFinding:
        rating, rationale, action = self._score(
            criterion_id, document, audience=audience, purpose=purpose
        )
        paragraph = self._evidence_paragraph(criterion_id, document)
        evidence = Evidence(
            location=paragraph.location,
            quotation=paragraph.text[:280],
            explanation=(
                "This passage contains the visible features used by the offline diagnostic. "
                "A human reader should verify the inferred effect."
            ),
        )
        return CriterionFinding(
            criterion_id=criterion_id,
            rating=rating,
            confidence="low",
            rationale=rationale,
            supporting_evidence=[evidence] if rating >= 2.5 else [],
            limiting_evidence=[evidence] if rating < 3.0 else [],
            revision_action=action,
        )

    def _score(
        self,
        criterion_id: str,
        document: Document,
        *,
        audience: str | None,
        purpose: str | None,
    ) -> tuple[float, str, str]:
        text_lower = document.text.lower()
        stats = document.stats
        sentence_lengths = [len(WORD.findall(sentence.text)) for sentence in document.sentences]
        paragraph_lengths = [len(WORD.findall(paragraph.text)) for paragraph in document.paragraphs]
        signal_count = sum(text_lower.count(signal) for signal in SIGNALS.get(criterion_id, ()))

        if criterion_id == "rhetorical_fit":
            rating = 3.0 if audience and purpose else 2.0
            return (
                rating,
                "Audience and purpose are explicit."
                if audience and purpose
                else "Rhetorical context was not fully supplied.",
                "State the intended reader and the concrete effect the piece should produce.",
            )
        if criterion_id in SIGNALS:
            rating = min(3.5, 1.75 + min(signal_count, 7) * 0.25)
            label = criterion_id.replace("_", " ")
            return (
                rating,
                f"The document contains {signal_count} visible {label} signal(s).",
                (
                    f"Review whether the visible {label} cues express a real relationship "
                    "rather than a label."
                ),
            )
        if criterion_id == "macrostructure":
            rating = 3.0 if 3 <= stats.paragraphs <= 12 else 2.0
            if paragraph_lengths and max(paragraph_lengths) > 220:
                rating -= 0.5
            return (
                rating,
                f"The document contains {stats.paragraphs} mapped paragraph(s).",
                (
                    "Reverse-outline each paragraph with a functional verb and remove "
                    "duplicated functions."
                ),
            )
        if criterion_id == "sentence_craft":
            if len(sentence_lengths) < 2:
                rating = 1.5
                variation = 0.0
            else:
                variation = statistics.pstdev(sentence_lengths)
                average = statistics.mean(sentence_lengths)
                rating = 3.0 if 8 <= average <= 30 and variation >= 4 else 2.25
            return (
                rating,
                f"Sentence lengths show a standard deviation of {variation:.1f} words.",
                (
                    "Read the draft aloud and inspect clause relationships and emphasis "
                    "in difficult sentences."
                ),
            )
        if criterion_id == "diction":
            words = [word.lower() for word in WORD.findall(document.text)]
            diversity = len(set(words)) / len(words) if words else 0
            rating = 3.0 if diversity >= 0.45 else 2.25
            return (
                rating,
                (
                    f"Visible lexical diversity is {diversity:.2f}; this is descriptive, "
                    "not a quality test."
                ),
                "Replace vague or inflated words only where a more exact term clarifies meaning.",
            )
        if criterion_id == "voice":
            concrete = len(re.findall(r"\b[A-Z][a-z]{2,}\b|\b\d+\b", document.text))
            rating = min(3.25, 2.0 + concrete * 0.1)
            return (
                rating,
                f"The draft contains {concrete} visible proper-name or numeric particular(s).",
                (
                    "Identify three consequential choices and make the reasoning behind "
                    "them more visible."
                ),
            )
        if criterion_id == "conventions":
            suspicious = len(re.findall(r" {2,}|\s+[,.!?;:]", document.text))
            rating = 3.25 if suspicious == 0 else max(1.5, 3.25 - suspicious * 0.25)
            return (
                rating,
                f"The local scan found {suspicious} spacing or punctuation anomaly/anomalies.",
                (
                    "Correct patterns that obstruct meaning or credibility after global "
                    "revision is complete."
                ),
            )
        return (
            2.0,
            "The offline provider has limited evidence for this criterion.",
            "Request a model-assisted or human reading focused on this criterion.",
        )

    @staticmethod
    def _evidence_paragraph(criterion_id: str, document: Document):
        if not document.paragraphs:
            raise ValueError("Cannot assess an empty document.")
        signals = SIGNALS.get(criterion_id, ())
        return max(
            document.paragraphs,
            key=lambda paragraph: sum(paragraph.text.lower().count(signal) for signal in signals),
        )

    def revise(
        self,
        document: Document,
        *,
        focus: list[str],
        audience: str | None,
        purpose: str | None,
        voice_profile: VoiceProfile | None,
        voice_register: str | None,
    ) -> RevisionDraft:
        revised = re.sub(r"[ \t]+", " ", document.text)
        revised = re.sub(r" +\n", "\n", revised)
        revised = re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", revised, flags=re.IGNORECASE)
        revised = revised.strip() + "\n"
        changed = revised != document.text
        unresolved = [
            "Offline mode does not perform substantive rewriting.",
            "Use coaching or a model-assisted provider for developmental revision.",
        ]
        if voice_profile is not None:
            unresolved.append(
                f"Offline mode did not apply the {voice_profile.label} voice profile "
                f"or its {voice_register or 'auto'} register."
            )
        return RevisionDraft(
            revised_text=revised,
            change_summary=(
                ["Normalized repeated whitespace and adjacent duplicate words."]
                if changed
                else ["No safe mechanical cleanup was needed."]
            ),
            unresolved_issues=unresolved,
        )
