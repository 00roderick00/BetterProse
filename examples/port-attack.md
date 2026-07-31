# Worked example — Register B

## The draft

> In today's rapidly evolving security landscape, experts argue that the recent cyberattack on a major European port represents a pivotal moment in the history of maritime logistics. It is important to note that the attackers did not target the ships themselves but the scheduling software that assigns berths, highlighting the increasingly interconnected nature of global trade. Observers have noted that ports, pipelines and payment systems face similar risks through what this piece calls the "soft perimeter", the layer of commercial software that states depend on but do not control. This layer could potentially possibly grow in importance. The future remains uncertain, but one thing is certain: challenging times lie ahead for all stakeholders.

## The ledger

| # | Quoted span | Pattern | Proposed rewrite | Why this is better prose |
|---|-------------|---------|------------------|--------------------------|
| 1 | "In today's rapidly evolving security landscape" | BP-06 | cut | Announces a subject instead of starting the argument. |
| 2 | "experts argue that" | BP-01 | cut; assert directly | The source names no expert; the claim must stand on its own or go. |
| 3 | "represents a pivotal moment in the history of maritime logistics" | BP-10 | state what the attackers did | Asserts importance; the target selection demonstrates it. |
| 4 | "It is important to note that" | BP-05 | cut | Six words, no meaning. |
| 5 | "highlighting the increasingly interconnected nature of global trade" | BP-12 | cut | Participial gesture at depth; the shared-risk point is already made concretely in the next sentence. |
| 6 | "Observers have noted that" | BP-01 | cut; assert directly | Ownerless attribution. |
| 7 | "soft perimeter" | BPV-01, P-1 | no edit | Coinage: survives verbatim and anchors the close. |
| 8 | "could potentially possibly grow" | BPV-04, P-2 | "will probably widen" | One placed hedge where the uncertainty lives, not three pads. |
| 9 | "The future remains uncertain... lie ahead for all stakeholders" | BP-07, BPV-06 | end on the open problem | Could close any piece on any subject; the piece has earned a harder question. |

## The final

> The cyberattack on a major European port never touched a ship. It went for the scheduling software that assigns berths. Ports, pipelines and payment systems share the exposure, because each depends on the soft perimeter: the layer of commercial software that states depend on but do not control. That layer will probably widen. The open question is who defends the soft perimeter when no state controls it.

Self-check: read aloud, the lengths vary and nothing clusters; every fact in the final is in the draft; Register B throughout, and "soft perimeter" appears verbatim, twice, closing the piece. Run against its own ledger, the final returns zero findings.
