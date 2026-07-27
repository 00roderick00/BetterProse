# Methodology

BetterProse separates four questions that writing systems often collapse:

1. How effective is the finished prose for this reader, purpose, and genre?
2. Are factual claims, quotations, and sources trustworthy?
3. Does available process evidence demonstrate authorial judgment?
4. Was AI use permitted and adequately disclosed?

The MVP assesses the first question and reports limited integrity warnings. It
does not infer process or policy compliance from style.

## Quality score

Each profile defines twelve criteria with visible weights totaling 100. A
provider returns a rating from 0 to 4, evidence, rationale, confidence, and a
revision action for each criterion. The application calculates:

```text
points = criterion weight × rating ÷ 4
```

The provider cannot alter weights or directly set the overall total.

## Evidence before score

A useful assessment identifies what in the text supports and limits a
judgment. BetterProse requires a location, quotation, and explanation for each
evidence item. A provider result with missing or unknown criteria is rejected.

## Genre profiles

Academic argument, professional prose, and narrative nonfiction use the same
construct but different weights. This prevents professional and narrative
writing from being graded as defective academic essays.

## Offline mode

The local provider uses transparent document measurements and conservative
heuristics. It can identify paragraphing, repeated language, concrete support
signals, and sentence-shape patterns. It cannot reliably judge insight,
originality, factual truth, rhetorical effect, or literary quality, so its
findings are always marked low confidence.

## Model-assisted mode

The optional OpenAI adapter requests a schema-conforming report with the
Responses API. It uses versioned prompts and Pydantic models. BetterProse still
validates criterion coverage, clamps ratings, and calculates all points
locally.

## Validation direction

Future validation should use blinded human raters, genre-diverse anchor texts,
criterion-level agreement, fairness audits, adversarial surface-only
rewrites, and longitudinal evidence that writers make better decisions after
using the feedback.
