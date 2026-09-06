# Research blog figure contracts

These figures are conceptual diagrams for public research notes. They contain no experimental observations, simulated results, performance claims, or private project data.

## Data knowledge loop

- Core conclusion: prior knowledge can enter several stages of a learning system and should be revised through evaluation.
- Results-level question: where can knowledge constrain the machine-learning pipeline without replacing empirical validation?
- Archetype: single-panel schematic.
- Target output: web PNG with editable SVG and PDF companions.
- Backend and size: Python, 183 mm × 98 mm.
- Evidence: conceptual information flow only.
- Reviewer risk: the map is deliberately practical rather than an exhaustive taxonomy.

## Missing class evaluation

- Core conclusion: generated samples are useful only when fidelity, downstream utility, cross-domain robustness, and leakage control are evaluated separately.
- Results-level question: what must be checked before synthetic missing-class data can support recognition?
- Archetype: single-panel workflow schematic.
- Target output: web PNG with editable SVG and PDF companions.
- Backend and size: Python, 183 mm × 98 mm.
- Evidence: evaluation logic only; no unpublished method details or numerical results.
- Reviewer risk: “disease-region cue” names a generic conditioning signal and must not be read as disclosure of a submitted method.

## Semantic 3D architecture

- Core conclusion: a versioned semantic intermediate layer separates intent from rendering and makes a 3D-generation system auditable and maintainable.
- Results-level question: which system boundaries prevent semantic edits from becoming untracked scene mutations?
- Archetype: single-panel system schematic.
- Target output: web PNG with editable SVG and PDF companions.
- Backend and size: Python, 183 mm × 98 mm.
- Evidence: architecture and data-flow logic only.
- Reviewer risk: the diagram describes the public system pattern, not confidential deployment details or a claim of fully automatic 3D generation.

## Leakage-safe experiment pipeline

- Core conclusion: leakage prevention starts before model training by grouping related observations, freezing the split manifest, and fitting every learned transform on training data only.
- Results-level question: which checkpoints keep a small-sample vision benchmark independent and reproducible?
- Archetype: single-panel workflow schematic.
- Target output: web PNG with editable SVG and PDF companions.
- Backend and size: Python, 183 mm × 98 mm.
- Evidence: procedural safeguards only; no experimental observations or performance claims.
- Reviewer risk: perceptual hashes and metadata checks reduce accidental duplication but do not prove semantic independence.

## Cross-domain evaluation matrix

- Core conclusion: cross-domain recognition should separate crop, acquisition, background, and time shifts, then hold out a complete domain for final evaluation.
- Results-level question: how can an evaluation matrix distinguish in-domain fitting from transfer to a genuinely unseen plant-disease domain?
- Archetype: single-panel workflow schematic.
- Target output: web PNG with editable SVG and PDF companions.
- Backend and size: Python, 183 mm × 98 mm.
- Evidence: benchmark design logic only; no unpublished model details or numerical results.
- Reviewer risk: domain labels are task-dependent and must be defined from collection provenance rather than inferred only from pixels.

## Foundation-model adaptation ladder

- Core conclusion: adaptation should begin with the smallest trainable surface and escalate only when a fixed validation protocol shows that additional flexibility is needed.
- Results-level question: how should a small scientific-vision project choose among probing, prompting, adapters, LoRA, and full fine-tuning?
- Archetype: single-panel decision schematic.
- Target output: web PNG with editable SVG and PDF companions.
- Backend and size: Python, 183 mm × 98 mm.
- Evidence: method-selection logic only; no claim that one adaptation method universally performs best.
- Reviewer risk: trainable-parameter count is not a substitute for measuring memory, runtime, calibration, or out-of-domain performance.

## Calibrated selective prediction

- Core conclusion: a probability becomes operationally useful only after validation-set calibration and an explicit accept, review, or reject policy.
- Results-level question: how should a scientific image classifier translate uncertain probabilities into auditable decisions?
- Archetype: single-panel decision workflow schematic.
- Target output: web PNG with editable SVG and PDF companions.
- Backend and size: Python, 183 mm × 98 mm.
- Evidence: conceptual decision logic only; no empirical performance or safety claim.
- Reviewer risk: a confidence threshold does not detect every distribution shift and must not be presented as a substitute for external validation.
