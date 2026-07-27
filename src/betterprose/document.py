from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from betterprose.models import DocumentStats

SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“‘])")
WORD = re.compile(r"\b[\w’'-]+\b", re.UNICODE)


@dataclass(frozen=True)
class Sentence:
    location: str
    text: str


@dataclass(frozen=True)
class Paragraph:
    location: str
    text: str
    sentences: tuple[Sentence, ...]


@dataclass(frozen=True)
class Document:
    name: str
    text: str
    paragraphs: tuple[Paragraph, ...]

    @property
    def sentences(self) -> tuple[Sentence, ...]:
        return tuple(sentence for paragraph in self.paragraphs for sentence in paragraph.sentences)

    @property
    def stats(self) -> DocumentStats:
        return DocumentStats(
            words=len(WORD.findall(self.text)),
            sentences=len(self.sentences),
            paragraphs=len(self.paragraphs),
            characters=len(self.text),
        )

    def numbered_text(self) -> str:
        return "\n\n".join(
            f"[{paragraph.location}] {paragraph.text}" for paragraph in self.paragraphs
        )


def split_paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", text.strip())
    return [re.sub(r"\s*\n\s*", " ", block).strip() for block in blocks if block.strip()]


def map_document(text: str, name: str = "document") -> Document:
    paragraphs: list[Paragraph] = []
    for paragraph_index, paragraph_text in enumerate(split_paragraphs(text), start=1):
        sentence_texts = [
            sentence.strip()
            for sentence in SENTENCE_BOUNDARY.split(paragraph_text)
            if sentence.strip()
        ]
        if not sentence_texts:
            sentence_texts = [paragraph_text]
        sentences = tuple(
            Sentence(
                location=f"P{paragraph_index}.S{sentence_index}",
                text=sentence_text,
            )
            for sentence_index, sentence_text in enumerate(sentence_texts, start=1)
        )
        paragraphs.append(
            Paragraph(
                location=f"P{paragraph_index}",
                text=paragraph_text,
                sentences=sentences,
            )
        )
    return Document(name=name, text=text, paragraphs=tuple(paragraphs))


def load_document(path: Path) -> Document:
    if path.suffix.lower() not in {".md", ".markdown", ".txt"}:
        raise ValueError("MVP input must be Markdown or plain text (.md, .markdown, .txt).")
    return map_document(path.read_text(encoding="utf-8"), name=path.name)
