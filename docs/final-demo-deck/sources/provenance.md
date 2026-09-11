# Provenance and AI Use Notes

## Deck Tooling

- Primary planned generator: PPT Master when installed and pinned.
- Repo-local deterministic fallback: `scripts/build-deck.mjs`.
- The fallback builder uses PptxGenJS and emits native editable PowerPoint text
  boxes, lines, and shapes.
- PDF export is optional and should be done with PowerPoint, Keynote, or
  LibreOffice if available.
- `npm audit --omit=dev` reports two high-severity advisories through
  PptxGenJS's `image-size` dependency chain. The package is overridden to
  `image-size@2.0.2`, the deck builds successfully, and this initial generator
  does not parse untrusted image files. Do not use `npm audit fix --force`
  without review because npm proposes a breaking PptxGenJS downgrade.

## AI Use

AI may assist with:

- drafting slide copy;
- organizing the narrative;
- summarizing repo evidence;
- identifying unsupported claims;
- improving speaker notes.

AI must not be represented as:

- calculating safe-to-spend;
- overriding pace status;
- producing official financial metrics;
- mutating immutable snapshots;
- deciding what the user should do financially.

## Asset and IP Notes

- Current deck uses native PowerPoint shapes and text only.
- Existing repo diagrams in `docs/slides/` may be used as evidence or design
  references.
- Add licensing notes here for any new image, font, icon, template, model, or
  third-party generator used after this initial implementation.
