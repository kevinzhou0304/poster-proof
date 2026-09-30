# Changelog

Notable changes to Poster Proof are recorded here.

## 0.1.0 — 2026-09-30

First public release.

- Check image dimensions, color mode, and embedded ICC profile metadata.
- Test QR readability at the source size and optional reduced preview widths.
- Optionally compare decoded QR content with an expected value without writing
  the QR payload to the JSON report.
- Keep image processing local; input files are not changed or uploaded.
