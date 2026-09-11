# GoalWise Final Demo Deck

This directory is the source package for the editable PowerPoint final-demo deck.
The generated `.pptx` is an artifact; the narrative, evidence, notes, and
provenance live in text files so they can be reviewed and regenerated.

## Build

```bash
cd docs/final-demo-deck
npm install
npm run build
npm run build:high-end
```

Output:

```text
docs/final-demo-deck/dist/goalwise-final-demo.pptx
docs/final-demo-deck/dist/goalwise-final-demo-high-end.pptx
```

The builder uses PptxGenJS and writes native editable PowerPoint text boxes,
lines, and shapes. Use PPT Master for richer visual iteration when it is
installed; this repo-local builder is the deterministic editable-PPTX fallback.

## Source Files

- `deck/slides.json`: slide content and notes used by the builder.
- `deck/story.md`: approved narrative and timing target.
- `scripts/build-deck.mjs`: deterministic editable-PPTX baseline generator.
- `scripts/build-high-end-deck.mjs`: more polished native-shape deck generator.
- `sources/evidence.md`: claim-to-repo evidence map.
- `sources/provenance.md`: AI, dependency, asset, and IP notes.
- `qa/checklist.md`: final visual, factual, and rehearsal checklist.

## Scope Guardrails

GoalWise financial outputs are backend-owned and deterministic. The deck must not
claim that runtime AI calculates, overrides, or recommends safe-to-spend,
shortfall, pace status, snapshots, or official dashboard metrics.
