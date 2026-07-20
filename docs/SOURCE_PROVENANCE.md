# Source provenance

This repository's documentation and contracts were selected and adapted from the
canonical Nexus OS documentation package. This file records where the material
came from and what was included, excluded, or rewritten during extraction.

## Origin

| Field | Value |
|---|---|
| Source repository | `royramosparaiso/nexus-console` |
| Source branch | `docs/nexus-os-canonical-reorg` |
| Source commit | `bf437473c4bf55a4724890ff6c3a634fa8ddb331` |
| Source PR | **#5** (draft) — <https://github.com/royramosparaiso/nexus-console/pull/5> |
| Packaged | 2026-07-20 |
| Populated into `nexus-os` | 2026-07-20 |

The canonical package carried exactly **one** authoritative document per role
(one Vision, one system-wide Architecture) and excluded all `SUPERADO`
(superseded) redirect stubs and competing historical visions/architectures.

## Status

All material is **TARGET-STATE** (approved design, not implemented) except where
a document is explicitly marked **ACTUAL**. Contracts are alpha
(`v1alpha1`/`v1alpha2`, field `x-nexus-contract-version`). This repository
contains **documentation and contracts only** — no runtime code, tests, or
binary artifacts.

## Included (public OSS scope)

- **Vision** — `docs/vision/nexus-os-vision.md` (single canonical vision).
- **Architecture** — `docs/architecture/` (system-wide architecture, glossary,
  product/OSS boundary, migration & compatibility).
- **Component specs** — `docs/specs/a,c,d,e,f,g,h,i,j,k,l,m` (Personal Runtime,
  Team/Org contracts, Operator lifecycle, Registry/distribution, package/artifact
  model, entitlements & degradation, security/trust/signing/secrets, Studio
  authoring, deployment modalities, CLI/SDK/installer/handoff, observability/audit,
  local inference/voice/edge).
- **ADR** — `docs/adr/0001`–`0011` (all active).
- **RFC** — `docs/rfc/002-console-platform-protocol.md`.
- **Contracts** — `docs/schemas/v1alpha1/` (10 schemas), `docs/schemas/v1alpha2/`
  (8 schemas), and `docs/schemas/examples/` (valid fixtures + `invalid/` negative
  fixtures + index maps).
- **Doc indexes & changelog** — `docs/README.md`, `docs/specs/README.md`,
  `docs/schemas/README.md`, `docs/CHANGELOG.md`.

## Excluded / adapted for this public repo

| Item | Action | Reason |
|---|---|---|
| `docs/specs/b-nexus-hub.md` (full Hub web-development spec) | **Replaced** with a public-boundary stub | The Hub web app is the **proprietary** control plane; its implementation spec is out of OSS scope. The stub describes only the public boundary and links to <https://github.com/ironbat-digital/nexus-hub>. |
| `00_LEEME_PRIMERO.md`, `MANIFEST.md`, `SHA256SUMS.txt` | **Dropped** | Package-only artifacts (archive manifest/checksums/readme); their relevant content is folded into this file and the root README. |
| Archive root `README.md` (Nexus Console readme) | **Dropped** | Replaced by a new professional root README for the public `nexus-os` repo. |
| Archive `LICENSE` (MIT) | **Not copied** | The repository's existing MIT `LICENSE` is preserved unchanged. |
| `tools/vad-conversion/README.md`, `web/public/models/silero-vad/README.md` | **Not copied** | Upstream implementation docs referencing code/binaries that do not live in a docs/contracts repo; Spec M now references them as upstream instead of via broken relative links. |
| `SUPERADO` redirect stubs (managed-portal / personal-hub-subscription visions, managed-platform-architecture) | **Already excluded** by the canonical package | Superseded by the single canonical Vision + Architecture. |

## Link fixes applied during extraction

- **Spec B** (`docs/specs/b-nexus-hub.md`): rewritten as a public-boundary
  document; all outbound links point to in-repo contracts/specs or the
  proprietary `nexus-hub` repo.
- **Spec M** (`docs/specs/m-local-inference-voice-edge.md`): the three
  `../../` links to the archive's root README / `tools/` / `web/` READMEs were
  replaced with an upstream-implementation reference (those files are not part of
  this docs/contracts repo).
- **Indexes** (`docs/README.md`, `docs/specs/README.md`,
  `docs/schemas/README.md`): the Hub entries were updated to reflect the
  public-boundary stub, and references to the `test_managed_platform_schemas.py`
  validation harness were clarified as living in the **upstream** implementation,
  not in this repo.

Historical, point-in-time records (ADRs, `docs/CHANGELOG.md`, example
`index.json` descriptions) retain their original inline references to upstream
`console/...` paths as accurate historical context; they are not clickable
relative links and do not break.
