# Nexus OS

**Sovereign, verifiable and composable operating system for AI agents.**

Nexus OS is a **documentation-and-contracts** repository: it holds the canonical
public **Vision**, the system-wide **Architecture**, the OSS component
specifications, the Architecture Decision Records (ADR), RFCs, and the
machine-readable **contracts** (`v1alpha1` / `v1alpha2` JSON Schemas with valid
and negative examples) that let independent implementations interoperate.

> **This repository is documentation and contracts only.** It does **not** ship
> runtime code, tests, or binary artifacts. Inline references to `console/...`,
> `web/...` or `tools/...` paths point to the **upstream** implementation
> (Runtime / Console / Hub), not to files in this repo.

## Status: TARGET-STATE

Except where a document is explicitly marked **ACTUAL**, everything here
describes an **approved-but-not-yet-implemented** design (TARGET-STATE). The
contracts are in **alpha** (`v1alpha1`/`v1alpha2`, field
`x-nexus-contract-version`) and may change before implementation. This
repository does **not** claim that Runtime/Operator code exists here — it is the
authoritative specification these components will be built against.

## The Personal OSS promise

The **Personal edition is free and open-source, forever**, for a single owner,
with **no Hub account required**. Nexus OS never withholds **security,
export, or portability** behind a paywall:

- A self-hoster can verify pack signatures, export the entire instance, and
  audit their own system without any paid component.
- `docker compose up` self-hosted operation stays intact; the Operator is
  optional.
- No data is ever held hostage: the owner keeps access and full export in
  **every** subscription state (graceful degradation pauses premium capabilities,
  it never deletes data).

What is charged for is **operational convenience** (managed provisioning,
curated catalog, coordinated fleet updates, support/SLA), never sovereignty or
basic security. See [product/OSS boundary](docs/architecture/product-oss-boundary.md).

## Responsibilities of this repo

| Area | In this repo |
|---|---|
| Vision & Architecture | Canonical public [Vision](docs/vision/nexus-os-vision.md) and [system-wide Architecture](docs/architecture/nexus-os-architecture.md) |
| Personal Runtime (OSS) | [Spec A](docs/specs/a-personal-runtime.md) |
| Operator / reconciliation | [Spec D](docs/specs/d-operator-instance-lifecycle.md) — enrollment, signed desired-state reconciliation, health |
| Package / artifact model | [Spec F](docs/specs/f-package-artifact-model.md), [Spec E](docs/specs/e-registry-catalog-distribution.md), [Spec I](docs/specs/i-studio-authoring-publishing.md) |
| Entitlement verification & degradation | [Spec G](docs/specs/g-entitlements-subscriptions-degradation.md) (public **verifier** contract; Hub billing is out of scope) |
| Security / trust / signing / secrets | [Spec H](docs/specs/h-security-trust-signing-secrets.md) |
| Deployment modalities | [Spec J](docs/specs/j-deployment-modalities.md) |
| CLI / SDK / installer / handoff | [Spec K](docs/specs/k-cli-sdk-installer-handoff.md) |
| Observability / audit / ops | [Spec L](docs/specs/l-observability-audit-ops.md) |
| Local inference / voice / edge | [Spec M](docs/specs/m-local-inference-voice-edge.md) |
| Team / Organization contracts | [Spec C](docs/specs/c-team-organization.md) |
| Hub **boundary** (proprietary internals excluded) | [Spec B](docs/specs/b-nexus-hub.md) |
| Contracts | [`docs/schemas/`](docs/schemas/README.md) — `v1alpha1`/`v1alpha2` + examples |

**Out of scope (proprietary):** the Nexus Hub web-development implementation
(billing, managed provisioning, secret orchestration at scale, curated catalog,
portal/site). [Spec B](docs/specs/b-nexus-hub.md) documents only the Hub's
**public boundary** and the contracts it emits/consumes, and links to the
proprietary implementation.

## The four-part architecture

Nexus OS is a control/data-plane split with explicit trust boundaries
(see [ADR-0001](docs/adr/0001-hub-operator-runtime-registry-split.md)):

- **Nexus Hub** — hosted, **proprietary** control plane (issues signed
  entitlements, catalog, managed setup). Not in this repo.
- **Nexus Operator** — OSS outbound agent, no arbitrary shell; reconciles signed
  desired state.
- **NexusOS Runtime / Platform** — OSS sovereign data plane; operates without the
  Hub.
- **Nexus Registry** — signed, versioned catalog of packs (four distribution
  lanes; open lanes are mirrorable without a Hub account).

## Repository relationships

| Repo | Role | Link |
|---|---|---|
| **nexus-os** (this repo) | Public Vision, Architecture, OSS specs & contracts | — |
| **nexus-hub** | Proprietary hosted control plane (Hub web app) | <https://github.com/ironbat-digital/nexus-hub> |
| **nexus-packs** | Pack catalog / sector packs | <https://github.com/ironbat-digital/nexus-packs> |
| **nexus-real-estate** | Real-estate 3D PoC (sector vertical) | <https://github.com/ironbat-digital/nexus-real-estate> |

## Documentation — recommended reading order

1. [Vision](docs/vision/nexus-os-vision.md) — mission, users, editions, Personal OSS, Hub subscription, trust, monetization, license, roadmap, non-goals.
2. [System-wide Architecture](docs/architecture/nexus-os-architecture.md) — components, trust boundaries, control/data planes, reconciliation, end-to-end flows.
3. [Documentation map / index](docs/README.md) — the canonical index of everything.
4. [Glossary & naming](docs/architecture/glossary.md).
5. [Component specs](docs/specs/README.md) — `a`–`m` (Hub `b` is a public-boundary stub).
6. [Schemas & examples](docs/schemas/README.md) — `v1alpha1`/`v1alpha2` contracts with valid and `invalid/` fixtures.
7. [ADRs](docs/adr/) `0001`–`0011` and [RFC-002](docs/rfc/002-console-platform-protocol.md).
8. Support: [product/OSS boundary](docs/architecture/product-oss-boundary.md), [migration & compatibility](docs/architecture/migration-and-compatibility.md), [changelog](docs/CHANGELOG.md).

Provenance of this material is recorded in [docs/SOURCE_PROVENANCE.md](docs/SOURCE_PROVENANCE.md).

## Naming note

`Nexus OS` is the **display product name** used in prose and user-facing
material. Stable **technical identifiers** are preserved verbatim and are **not**
renamed to insert a space: `NexusOS`, `nexus`, schema `$id`s, repository names,
packages, APIs and code symbols. Formal rule in the
[glossary](docs/architecture/glossary.md#nomenclatura).

## Contributing

This is an **initial public population** of the canonical documentation and
contracts. A formal contribution process (CLA/DCO decision) is **pending the
ownership/contribution legal audit** described in
[ADR-0008](docs/adr/0008-oss-commercial-boundary-and-license.md); until it lands,
please open issues for discussion rather than large PRs. The contracts are alpha
and may change.

## License

This repository is currently licensed **MIT** (see [LICENSE](LICENSE)).

The **approved target** is a per-component model
([ADR-0008](docs/adr/0008-oss-commercial-boundary-and-license.md)): **Apache-2.0**
for Runtime, Operator, CLI, SDK, public schemas/contracts, pack
verifier/installer and community Registry client; **proprietary** for the hosted
Hub and managed operations. The relicense is **not yet in effect** and is
**blocked pending a legal ownership/contribution audit** — no claim is made that
licenses have already changed. Packs are licensed per package with mandatory SPDX
metadata.

---

*Powered by Ironbat Digital LLC.*
