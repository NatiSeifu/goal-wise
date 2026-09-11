# Final Demo Deck QA Checklist

## Automated / Agent Checks

- [ ] Generated PPTX opens in PowerPoint, Keynote, or LibreOffice Impress.
- [ ] Slide count is between 8 and 10.
- [ ] No placeholder or TODO text remains.
- [ ] Every factual claim maps to `sources/evidence.md`.
- [ ] Deferred features are not presented as current MVP behavior.
- [ ] AI is described only as explain-only runtime support or development/review assistance.
- [ ] Speaker notes exist for each slide in `deck/slides.json`.
- [ ] Final artifact exists at `dist/goalwise-final-demo.pptx`.

## Human Checks

- [ ] Each slide's main claim is clear in about five seconds.
- [ ] Each decision slide has claim, evidence, alternative, risk, mitigation, and falsifier.
- [ ] Diagrams can be explained by every presenter.
- [ ] The full slide talk fits under eight minutes in rehearsal.
- [ ] The live demo transition is intentional and concise.
- [ ] The app demo is locally runnable with seeded or known-safe data.
