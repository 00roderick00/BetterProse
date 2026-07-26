from __future__ import annotations

import os
from importlib.resources import files

from betterprose.document import Document
from betterprose.models import AssessmentDraft, RevisionDraft, Rubric


class OpenAIProvider:
    name = "openai"

    def __init__(self, model: str | None = None) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The OpenAI provider is optional. Install it with: "
                'python -m pip install -e ".[openai]"'
            ) from exc
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for --provider openai.")
        self.model = model or os.getenv("BETTERPROSE_MODEL", "gpt-5.6")
        self._client = OpenAI()

    def assess(
        self,
        document: Document,
        rubric: Rubric,
        *,
        audience: str | None,
        purpose: str | None,
    ) -> AssessmentDraft:
        system_prompt = _prompt("assessment.md")
        rubric_text = "\n".join(
            (
                f"- {criterion.id} ({criterion.weight} points): {criterion.question}\n"
                f"  Rating 4: {criterion.rating_4}\n"
                f"  Rating 2: {criterion.rating_2}\n"
                f"  Rating 0: {criterion.rating_0}"
            )
            for criterion in rubric.criteria
        )
        user_prompt = (
            f"Profile: {rubric.name} v{rubric.version}\n"
            f"Audience: {audience or 'not supplied'}\n"
            f"Purpose: {purpose or 'not supplied'}\n\n"
            f"Rubric:\n{rubric_text}\n\n"
            f"Numbered document:\n{document.numbered_text()}"
        )
        response = self._client.responses.parse(
            model=self.model,
            reasoning={"effort": "medium"},
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=AssessmentDraft,
        )
        if response.output_parsed is None:
            raise RuntimeError("The model did not return a parsed assessment.")
        return response.output_parsed

    def revise(
        self,
        document: Document,
        *,
        focus: list[str],
        audience: str | None,
        purpose: str | None,
    ) -> RevisionDraft:
        response = self._client.responses.parse(
            model=self.model,
            reasoning={"effort": "medium"},
            input=[
                {"role": "system", "content": _prompt("controlled_rewrite.md")},
                {
                    "role": "user",
                    "content": (
                        f"Focus: {', '.join(focus) or 'clarity'}\n"
                        f"Audience: {audience or 'not supplied'}\n"
                        f"Purpose: {purpose or 'not supplied'}\n\n"
                        f"Source text:\n{document.text}"
                    ),
                },
            ],
            text_format=RevisionDraft,
        )
        if response.output_parsed is None:
            raise RuntimeError("The model did not return a parsed revision.")
        return response.output_parsed


def _prompt(name: str) -> str:
    return files("betterprose").joinpath("prompts", name).read_text(encoding="utf-8")
