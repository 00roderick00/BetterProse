# Research foundations and design rationale

BetterProse is a research-informed system for assessing, explaining, and
improving prose. It combines:

- rhetoric and composition theory;
- writing pedagogy used at highly selective universities;
- research on analytic rubrics and writing assessment;
- evidence on formative, peer, and automated feedback;
- current work on generative AI, automated essay scoring, and detector bias;
- explicit safeguards for source integrity, language diversity, and human
  judgment.

It is not an AI-authorship detector, a grammar score, a readability formula, or
a prompt that asks a model whether a passage “sounds good.” Its central claim
is that prose quality is multidimensional and contextual:

> Good prose uses trustworthy, purposeful, and deliberately arranged language
> to produce an intended intellectual, practical, aesthetic, or emotional
> effect on a particular reader.

That definition explains the architecture of the project. BetterProse asks
about the writer's rhetorical situation, motive, controlling idea,
development, evidence, counterpressure, structure, cohesion, sentences,
diction, voice, and conventions. It requires evidence for every judgment,
keeps integrity separate from prose quality, and treats automated assessment as
a formative second reader rather than an autonomous final authority.

## What “research-informed” means here

BetterProse was not copied from one university rubric or derived from one
statistical model. It is a synthesis across four evidence layers:

1. **Established disciplinary guidance** from organizations responsible for
   writing instruction and assessment.
2. **Convergent teaching practice** from university writing programs and
   tutorial systems.
3. **Empirical research** on rubrics, feedback, automated writing evaluation,
   and AI-assisted scoring.
4. **AI-era risk research** on detector reliability, linguistic bias, score
   compression, prompt sensitivity, and style-over-substance effects.

These sources do not prove that BetterProse itself is valid in every setting.
They establish the rationale for its construct and safeguards. BetterProse
still requires direct validation against trained human readers, anchor texts,
genres, institutions, and writer outcomes. The project therefore distinguishes
three claims:

- **Research-grounded:** yes. Its criteria and workflow are traceable to
  established scholarship and practice.
- **Software-validated:** yes, within the scope of its automated checks. The
  application tests schema conformance, criterion coverage, evidence
  locations, quotation fidelity, score calculation, session handling, and
  fact-lock behavior.
- **Psychometrically validated for high-stakes grading:** no. That work remains
  a stated research program, not a completed claim.

## 1. Rhetorical situation rather than universal style rules

The first foundation is the rhetorical view that writing succeeds in relation
to a purpose, audience, genre, and situation.

The [Stanford Program in Writing and Rhetoric's evaluation
criteria](https://pwr.stanford.edu/about-pwr/pwr-policies/pwr-evaluation-grading-criteria)
describe effective writing as an interaction among purpose, audience, persona,
content, organization, style, and form. Stanford explicitly says rhetorically
effective writing cannot be reduced to a formula. The current [WPA Statement on
the Five Knowledge Domains of First-Year
Composition](https://www.wpacouncil.org/aws/CWPA/asset_manager/get_file/948056?ver=0)
similarly treats genre as social action: a purposeful response to recurring
situations and communities, not merely a container with fixed surface
features.

BetterProse implements that principle in four ways:

- every assessment may specify audience, purpose, and genre profile;
- `rhetorical_fit` asks whether the prose is doing the right work for that
  situation;
- academic, professional, and narrative profiles change criterion weights;
- no isolated device—passive voice, first person, long sentences, fragments,
  semicolons, contractions, or em dashes—automatically raises or lowers the
  score.

This is why BetterProse rejects “humanizer” systems built around banned words,
punctuation quotas, sentence-length targets, or deliberate irregularity. Those
features can be effective or ineffective depending on what the writer is
trying to accomplish.

## 2. Motive, thesis, evidence, analysis, and structure

The center of the academic-argument profile reflects a striking convergence
among university writing programs.

The [Princeton Writing Program's
lexicon](https://writing.princeton.edu/faculty/writing-seminar-experience/writing-lexicon)
defines:

- **motive** as the consequential problem, puzzle, or question that makes an
  argument worth reading;
- **thesis** as the central, non-obvious claim that responds to that motive;
- **analysis** as the interpretation of evidence rather than its summary;
- **evidence** as material that must be selected fairly and analyzed rather
  than treated as self-explanatory;
- **structure** as the sequence required by the argument, not a five-paragraph
  template imposed in advance.

The [Harvard College Writing Center's thesis
guide](https://writingcenter.fas.harvard.edu/thesis) likewise requires an
arguable, appropriately scoped central claim supported by a logically
constructed argument. Harvard's [counterargument
guide](https://writingcenter.fas.harvard.edu/counterargument) treats serious
objections as part of developing and refining a thesis, while its [organization
guide](https://writingcenter.fas.harvard.edu/tips-organizing-your-essay)
focuses on moving a reader through claims, evidence, and counterarguments.

BetterProse translates this shared instructional vocabulary into separate,
inspectable dimensions:

| BetterProse criterion | Research and teaching construct |
| --- | --- |
| `motive` | The problem, puzzle, need, or stakes that generate the piece |
| `controlling_idea` | Thesis, recommendation, governing tension, or line of direction |
| `development` | Claims, warrants, analysis, causal links, implications, or narrative movement |
| `support` | Evidence, sources, examples, scenes, data, and concrete particulars |
| `complexity` | Qualification, scope, uncertainty, alternatives, and counterargument |
| `macrostructure` | An order generated by the work the piece must perform |
| `cohesion` | Functional paragraphs and intelligible movement between ideas |

Separating these dimensions matters. A fluent essay may have weak reasoning. A
rough draft may contain a strong controlling insight. A single holistic score
can hide that difference; an analytic report makes it visible.

## 3. Sentence craft is reader management, not error counting

BetterProse's sentence and diction criteria draw on rhetorical instruction
rather than on a list of prohibited constructions.

Stanford's criteria connect strong style with purposeful diction, varied
sentences, nuanced tone, ethos, and audience engagement. The [Harvard guide to
transitions](https://writingcenter.fas.harvard.edu/transitions) explains
cohesion in terms of conceptual relationships and the movement from familiar
to new information, not the insertion of stock transition words.

Accordingly:

- `sentence_craft` considers clarity, clause relationships, emphasis, rhythm,
  and complexity proportional to the idea;
- `diction` considers precision, register, preserved distinctions, and economy;
- `voice` concerns accountable judgment and ethos, not mandatory informality,
  first person, jokes, or manufactured imperfections;
- `conventions` grades the consequences of linguistic and presentational
  choices for the intended reader, not raw error counts.

The system may report descriptive patterns—repetition, paragraph length, or
sentence shape—but those measurements cannot independently establish prose
quality.

## 4. Analytic rubrics, transparency, and calibration

BetterProse uses a visible analytic rubric because research suggests that
explicit criteria can support scoring consistency and learning, especially
when paired with exemplars, rater training, and local calibration.

Jönsson and Svingby's review, [“The Use of Scoring Rubrics: Reliability,
Validity and Educational
Consequences”](https://doi.org/10.1016/j.edurev.2007.05.002), found evidence
that rubrics can improve scoring reliability, while also showing that rubric
quality, criterion clarity, rater support, and task context matter. A rubric is
not self-validating merely because it contains numbers.

The [Conference on College Composition and Communication position statement on
writing
assessment](https://cccc.ncte.org/cccc/resources/positions/writingassessment)
goes further. It says writing assessments should serve articulated learning
goals, should be grounded in current research, and should account for inclusion
and language diversity. It warns that sole reliance on machine scoring or
prescriptive grammar provides a restricted view of writing and has
disproportionately penalized marginalized writers.

These findings produce concrete design choices:

- rubric definitions and weights live in version-controlled YAML rather than
  being hidden in a model prompt;
- every profile totals 100 points and records a version;
- the application, not the language model, calculates weighted totals;
- every criterion requires a rationale, confidence, revision action, and exact
  textual evidence;
- reports preserve sub-scores instead of presenting only a total;
- institutions are told to calibrate against local anchor texts before mapping
  scores to grades;
- scores are explicitly not treated as admissions, employment, publication, or
  disciplinary decisions.

## 5. Feedback should lead to revision

BetterProse is designed as a formative system because the strongest educational
case for writing assessment is not classification; it is better subsequent
writing.

Graham, Hebert, and Harris's meta-analysis, [“Formative Assessment and
Writing”](https://doi.org/10.1086/681947), found that feedback from adults,
peers, the writer, and computers improved writing quality in the included
school-age studies, though effect sizes differed by source. Vuogan and Li's
[meta-analysis of peer feedback in second-language
writing](https://doi.org/10.1002/tesq.3178), aggregating 26 empirical studies,
also found a positive overall effect and identified important moderating
conditions. Research comparing trained and untrained peer feedback further
suggests that shared criteria and feedback training improve usefulness.

Highly selective tutorial systems embody a related instructional cycle.
[Oxford](https://www.ox.ac.uk/admissions/undergraduate/courses/learning-at-oxford/personalised-learning)
describes tutorials as opportunities to test thinking for clarity, precision,
depth, breadth, and relevance through individual feedback. [Cambridge
supervision guidance](https://www.seniortutors.admin.cam.ac.uk/academic-support/undergraduate-supervisions-cambridge)
emphasizes repeated, small-group work in which students structure arguments,
question assumptions, and incorporate feedback.

BetterProse therefore produces:

- a reader account describing the experience of the piece;
- principal strengths to retain;
- no more than three priority revisions;
- a specific action for every criterion;
- coaching that addresses global problems before sentence polishing;
- comparison reports that show what improved, regressed, or merely changed;
- separate candidate revisions, never silent replacement of the original.

The design goal is feedback that the writer can use, reject, or revise—not a
verdict that asks for obedience.

## 6. What automated feedback can and cannot support

Research on automated writing evaluation is promising but mixed.

A [multi-level meta-analysis of automated writing
feedback](https://doi.org/10.3389/frai.2023.1162454) found a positive average
effect on writing performance alongside substantial variation among systems,
settings, learners, and study designs. A [systematic review of automated
writing evaluation in school
settings](https://doi.org/10.1111/jcal.12635) likewise found positive outcomes
in many studies but pointed to the value of combining system and teacher
feedback.

This supports bounded formative use. It does not establish that a general
language model should issue an unsupported final grade.

The 2026 University of Cambridge-led [evaluation of frontier models on 761
authentic undergraduate
essays](https://www.cam.ac.uk/stories/ai-university-essay-grading) is especially
important. Depending on the institution, AI matched the human-awarded degree
classification only 35–63 percent of the time. The systems compressed scores
toward the middle and were oversensitive to essay length, vocabulary range, and
sentence complexity while missing argumentative and conceptual merit,
particularly at the strongest, weakest, and boundary performances.

BetterProse responds by treating the model as a constrained qualitative reader:

1. `prepare_assessment` returns the versioned rubric and numbered prose.
2. The host model evaluates all twelve criteria.
3. `finalize_assessment` rejects missing criteria and invalid quotations,
   validates locations, and calculates the canonical weighted total.
4. The report records the provider, model when supplied, and uncertainty.

The validation layer can prove that the cited quotation exists and that every
criterion was considered. It cannot prove that the model's interpretation is
correct. The report therefore remains inspectable and contestable.

BetterProse also provides an optional independent model-backed engine and a
deterministic offline mode. Offline results are deliberately labeled low
confidence because document statistics cannot judge insight, truth,
originality, rhetorical effect, or literary quality.

## 7. Why BetterProse does not detect AI authorship

Writing quality and authorship are different constructs.

Liang and colleagues found that GPT detectors [systematically misclassified
non-native English
writing](https://doi.org/10.1016/j.patter.2023.100779). Other evaluations have
shown detector performance degrades under paraphrasing and other
transformations. The resulting false positives are particularly dangerous in
education because surface predictability may reflect language background,
genre, editing, disability-related composing practices, or an intentionally
plain style—not machine authorship.

Detector optimization also creates the wrong educational target. Removing em
dashes, adding first-person anecdotes, randomizing sentence lengths, or
replacing ordinary words with unusual synonyms may change a detector score
without improving accuracy, reasoning, structure, or effect. Some
“humanization” techniques introduce fake specificity or invented experience,
directly damaging epistemic integrity.

BetterProse therefore:

- never reports a “human score” or AI probability;
- never treats polished grammar, sentence regularity, or punctuation as proof
  of authorship;
- never recommends artificial mistakes or fabricated personal detail;
- treats suspected AI-policy violations as a separate process and disclosure
  question requiring appropriate evidence;
- uses detector-oriented rewrites only as adversarial tests of whether the
  prose score is responding to superficial changes.

## 8. Integrity, process, and prose quality are separate

One of BetterProse's most important design choices is refusing to collapse
different judgments.

| Layer | Question | Current output |
| --- | --- | --- |
| Prose quality | How effective is the finished piece for its reader, purpose, and genre? | Twelve criterion ratings and a weighted total |
| Epistemic integrity | Are claims, quotations, numbers, and sources traceable and trustworthy? | Separate status and warnings |
| Authorial agency | Can the writer explain decisions, revision, and use of assistance? | Future process-evidence layer; never inferred from style |
| AI-use compliance | Was assistance permitted and disclosed under the governing policy? | External policy decision; never folded into prose points |

A passage can be fluent and false. A disclosed AI-assisted report can be
accurate but badly organized. An unaided draft can be insightful but
mechanically rough. These cases require different evidence and different
responses.

The revision system's fact lock is a limited safeguard, not a fact checker. It
compares numbers, URLs, quotations, citation-like tokens, and other locked
surfaces before and after revision. It flags possible changes and blocks a
strict rewrite when protected material moves unexpectedly. It does not certify
that the original claim was true or that an unchanged paraphrase preserved
meaning.

## 9. Language diversity, accessibility, and fairness

BetterProse follows the CCCC position that assessment criteria help construct
what writers and institutions understand writing to be. Treating one prestige
dialect as synonymous with intelligence or correctness is therefore both
invalid and consequential.

The current WPA statement recognizes multiple Englishes, contextually situated
outcomes, accessibility, disability, genre variation, composing technologies,
and the social conditions of writing. [UNESCO's guidance on generative AI in
education and
research](https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research)
similarly calls for a human-centered approach attentive to agency, inclusion,
equity, cultural and linguistic diversity, privacy, and pedagogical purpose.

BetterProse applies those principles by:

- grading the reader effect and communicative consequence of conventions, not
  counting departures from a single dialect;
- keeping rhetorical context explicit;
- changing weights by genre;
- exposing evidence and rationale so biased judgments can be challenged;
- rejecting authorship inference from language patterns;
- requiring fairness testing before consequential deployment.

The current software architecture supports these commitments, but fairness has
not been established merely by stating them. Direct testing across dialects,
multilingual writers, disabilities, genres, disciplines, topics, and document
lengths remains necessary.

## 10. Research-to-product traceability

| Research principle | BetterProse implementation |
| --- | --- |
| Writing is rhetorical and contextual | Audience, purpose, genre profiles, `rhetorical_fit` |
| Strong arguments have motive, thesis, evidence, analysis, and counterpressure | Separate analytic criteria and evidence-backed findings |
| Structure follows intellectual or practical purpose | Macrostructure and cohesion assessed independently of templates |
| Rubrics should be explicit and calibrated | Versioned YAML, visible weights, local anchor-text roadmap |
| Feedback should support learning and revision | Three priorities, criterion actions, coaching and draft comparison |
| Machine scores are incomplete and bias-prone | Human-readable evidence, confidence, model/provider records, no autonomous high-stakes use |
| Language difference is not defective reasoning | Consequence-based conventions criterion and fairness requirements |
| Authorship cannot be inferred reliably from prose style | No AI detector or “humanizer” score |
| Revision can corrupt facts | Separate candidate files, diffs, and fact-lock audit |
| Quality, integrity, process, and policy are different constructs | Separate report layers and statuses |

## 11. Validation already present

The repository's automated tests currently verify software properties,
including:

- all rubric profiles contain the canonical twelve criteria;
- profile weights total 100;
- model output cannot add, remove, or reorder the scoring construct;
- every finding includes exact quotation evidence at a valid location;
- invalid ranges and fabricated quotations are rejected;
- the application calculates weighted points;
- assessment sessions expire, are bounded, and cannot be finalized twice;
- embedded prompt-like text is treated as prose rather than an instruction;
- reports preserve confidence, warnings, and integrity status;
- revision never overwrites the source;
- fact-lock audits identify changes to protected surfaces;
- the MCP server works through packaged standard input/output transport.

These are meaningful guarantees about execution and auditability. They are not
evidence that the qualitative ratings are universally accurate.

## 12. The empirical validation program

Moving from a research-grounded formative tool to a validated assessment system
requires a staged program.

### Phase 1: construct and content review

Recruit experienced teachers, writing-program administrators, editors,
rhetoricians, assessment researchers, and specialists in academic,
professional, and narrative prose. Ask them to challenge the twelve criteria,
anchors, genre weights, and every proposed automatic diagnostic.

### Phase 2: genre-diverse anchor corpus

Build a consented corpus spanning multiple levels of performance, language
backgrounds, disciplines, genres, lengths, and composing processes. Product
quality raters should not know whether a piece was written without AI,
AI-assisted, or AI-intensive.

### Phase 3: criterion-level reliability

Train human raters using exemplars and rationales. Double-score a substantial
sample. Measure agreement by criterion, not only correlation between total
scores. Analyze disagreements qualitatively and report uncertainty at score
boundaries.

### Phase 4: convergent, discriminant, and consequential validity

Test whether BetterProse aligns with relevant human judgments while remaining
distinct from irrelevant proxies such as length, vocabulary rarity, and
sentence complexity. Then test whether its feedback improves revision and
later independent writing. Agreement on one essay is not enough; the ultimate
question is whether writers make better decisions.

### Phase 5: fairness audit

Examine score errors and rationales across dialect, multilingual status,
disability-related tool use, genre, discipline, topic, and length. Do not
assume every group difference is either true performance or model bias; inspect
the text, criterion, and decision process.

### Phase 6: adversarial invariance

Apply surface-only transformations associated with detector gaming:
punctuation substitution, random short sentences, synonym inflation,
first-person insertion, paragraph reshaping, and detector-guided paraphrase.
Scores should remain broadly stable unless an assessed quality actually
changes.

### Phase 7: local calibration and governance

Institutions adopting BetterProse should establish local learning outcomes,
anchor texts, rater procedures, appeal paths, data-retention rules, and
human-authority requirements. No universal score boundary should silently
become an institutional grade.

## Conclusion

BetterProse is deep by design, not because it has a long prompt or many
criteria, but because it preserves distinctions that writing research says
matter:

- rhetorical success is contextual;
- substance and polish are not the same;
- evidence must be interpreted, not merely present;
- feedback should lead to revision;
- language diversity is not intellectual deficiency;
- AI can provide bounded assistance without becoming the final authority;
- authorship, integrity, agency, policy compliance, and prose quality require
  different evidence.

The project makes those principles operational through transparent rubrics,
exact textual evidence, application-calculated scores, uncertainty, controlled
revision, and explicit limitations. Its ambition is not to automate taste. It
is to make high-quality second-reader feedback more systematic, inspectable,
and useful while preserving responsibility for judgment where it belongs.

## Selected sources

### Disciplinary and institutional guidance

- Conference on College Composition and Communication. [Writing Assessment: A
  Position
  Statement](https://cccc.ncte.org/cccc/resources/positions/writingassessment).
- Council of Writing Program Administrators. [WPA Statement on the Five
  Knowledge Domains of First-Year Composition,
  v4](https://www.wpacouncil.org/aws/CWPA/asset_manager/get_file/948056?ver=0).
- Stanford Program in Writing and Rhetoric. [Evaluation and Grading
  Criteria](https://pwr.stanford.edu/about-pwr/pwr-policies/pwr-evaluation-grading-criteria).
- Princeton Writing Program. [A Writing
  Lexicon](https://writing.princeton.edu/faculty/writing-seminar-experience/writing-lexicon).
- Harvard College Writing Center. [Strategies for Essay
  Writing](https://writingcenter.fas.harvard.edu/pages/strategies-essay-writing).
- University of Oxford. [Personalised
  Learning](https://www.ox.ac.uk/admissions/undergraduate/courses/learning-at-oxford/personalised-learning).
- University of Cambridge. [Undergraduate
  Supervisions](https://www.seniortutors.admin.cam.ac.uk/academic-support/undergraduate-supervisions-cambridge).
- UNESCO. [Guidance for Generative AI in Education and
  Research](https://www.unesco.org/en/articles/guidance-generative-ai-education-and-research).

### Rubrics and feedback research

- Jönsson, A., and Svingby, G. (2007). [The use of scoring rubrics:
  reliability, validity and educational
  consequences](https://doi.org/10.1016/j.edurev.2007.05.002).
- Graham, S., Hebert, M., and Harris, K. R. (2015). [Formative assessment and
  writing: a meta-analysis](https://doi.org/10.1086/681947).
- Vuogan, A., and Li, S. (2023). [Examining the effectiveness of peer feedback
  in second language writing: a
  meta-analysis](https://doi.org/10.1002/tesq.3178).
- [Automated feedback and writing: a multi-level meta-analysis of effects on
  students'
  performance](https://doi.org/10.3389/frai.2023.1162454) (2023).
- Nunes, A., Cordeiro, C., Limpo, T., and Castro, S. L. (2022).
  [Effectiveness of automated writing evaluation systems in school
  settings](https://doi.org/10.1111/jcal.12635).

### AI-era assessment and fairness

- University of Cambridge OpRaise team. (2026). [AI not yet good enough to
  mark university essays, rewarding “style over
  substance”](https://www.cam.ac.uk/stories/ai-university-essay-grading).
- Liang, W., et al. (2023). [GPT detectors are biased against non-native
  English writers](https://doi.org/10.1016/j.patter.2023.100779).
- Çelik, Ö. (2026). [Lost in the middle? Examining scoring reliability and
  position bias in LLM-based automated essay
  scoring](https://doi.org/10.1007/s10639-026-14019-8).
- [Comparing GPT and human raters in essay assessment: variability, bias, and
  the potential of LLM-based
  scoring](https://doi.org/10.1016/j.caeo.2026.100341) (2026).
