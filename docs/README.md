# Documentación de Nexus OS — mapa canónico

Índice autoritativo de la documentación del repositorio. `Nexus OS` es el **nombre de producto de
visualización**; los identificadores técnicos (`NexusOS`, `nexus`, `$id` de esquema, nombres de repo,
paquetes y APIs) se preservan sin cambios (ver [nota de nomenclatura](architecture/glossary.md#nomenclatura)).

La documentación es **diseño aprobado, no implementado** (TARGET-STATE) salvo donde se marque ACTUAL.
Versiones de arquitectura: `v1alpha1` (infraestructura de cuatro partes) y `v1alpha2` (capa de producto
Personal + Hub, aditiva sobre `v1alpha1`).

> **Alcance de este repositorio.** `nexus-os` contiene **solo documentación y contratos** (arquitectura,
> specs de componente OSS, ADR/RFC y esquemas `v1alpha1`/`v1alpha2` con ejemplos). **No** incluye código
> de runtime, tests ni artefactos binarios. Las referencias en línea a rutas `console/...` o
> `web/...`/`tools/...` apuntan a la implementación **upstream** (Console/Runtime/Hub), no a este repo.
> El desarrollo web del Hub es **propietario**: la [Spec B](specs/b-nexus-hub.md) documenta solo su
> frontera pública y enlaza a <https://github.com/ironbat-digital/nexus-hub>.

## Jerarquía canónica

Existe **exactamente un** documento canónico por rol. Cada spec de componente es única.

### Visión (única)
| Documento | Alcance | Estado |
|---|---|---|
| [Visión de Nexus OS](vision/nexus-os-vision.md) | Misión, problema, usuarios, ediciones, Personal OSS, suscripción Hub, Team/Org, paquetes, modalidades, confianza, valor, monetización, licencia, roadmap, no-objetivos | Canónica |

### Arquitectura (única, system-wide)
| Documento | Alcance | Estado |
|---|---|---|
| [Especificación de arquitectura de Nexus OS](architecture/nexus-os-architecture.md) | Contexto, componentes, fronteras de confianza, planos, reconciliación, entitlements, modalidades, identidad/tenancy, datos/secretos, eventos, fallo/offline, versionado, secuencias, dependencias | Canónica |

### Nexus Hub — frontera pública (control plane propietario)
| Documento | Alcance | Estado |
|---|---|---|
| [Spec B: Nexus Hub (frontera)](specs/b-nexus-hub.md) | Frontera pública del Hub hospedado **propietario**: rol, responsabilidades, no-objetivos y contratos que emite/consume. La spec de desarrollo web detallada es propietaria → <https://github.com/ironbat-digital/nexus-hub> | Frontera pública |

### Especificaciones por componente (una por componente)
| # | Spec | Componente | Estado |
|---|---|---|---|
| a | [Personal Runtime](specs/a-personal-runtime.md) | Edición Personal libre, un propietario | Canónica |
| b | [Nexus Hub (frontera)](specs/b-nexus-hub.md) | Frontera pública del Hub propietario (ver arriba) | Frontera pública |
| c | [Team / Organization](specs/c-team-organization.md) | Multiusuario, roles, políticas | Canónica |
| d | [Operator y ciclo de vida](specs/d-operator-instance-lifecycle.md) | Enrolamiento, reconciliación, salud | Canónica |
| e | [Registry / distribución](specs/e-registry-catalog-distribution.md) | Cuatro carriles, mirrors, grants | Canónica |
| f | [Modelo de paquetes/artefactos](specs/f-package-artifact-model.md) | Agentes, skills, flows, sidecars, skulls, tareas, packs | Canónica |
| g | [Entitlements y degradación](specs/g-entitlements-subscriptions-degradation.md) | Verificación offline, ciclo de vida | Canónica |
| h | [Seguridad, firma y secretos](specs/h-security-trust-signing-secrets.md) | Ed25519, Cosign, minisign, age/X25519, mTLS | Canónica |
| i | [Studio: autoría y publicación](specs/i-studio-authoring-publishing.md) | Creación verificada, overlays, publicación | Canónica |
| j | [Modalidades de despliegue](specs/j-deployment-modalities.md) | self-hosted / BYOC / managed | Canónica |
| k | [CLI, SDK, instalador y handoff](specs/k-cli-sdk-installer-handoff.md) | Herramientas OSS y automatización de handoff | Canónica |
| l | [Observabilidad, auditoría y ops](specs/l-observability-audit-ops.md) | Telemetría, backup/recuperación, soporte | Canónica |
| m | [Inferencia local, voz y edge](specs/m-local-inference-voice-edge.md) | LiteRT, Voicebox, VAD (ownership + enlaces) | Canónica (parcial ACTUAL) |
| n | [Stack local de Personal v1 y bootstrap](specs/n-personal-local-stack.md) | Stack local único `personal-local-v1` + contrato de bootstrap/handoff | Canónica |

Índice detallado: [`specs/README.md`](specs/README.md).

### Gobernanza y soporte
| Documento | Alcance |
|---|---|
| [Glosario formal](architecture/glossary.md) | Términos normativos + nota de nomenclatura |
| [Migración y compatibilidad](architecture/migration-and-compatibility.md) | Console/Fly, wizard/handoff, transición de versiones |
| [Frontera OSS/comercial](architecture/product-oss-boundary.md) | Qué es OSS y qué hospedado; forma de pricing (sin cifras) |
| [Changelog de docs y contratos](CHANGELOG.md) | Historial de cambios documentales y de contrato |
| [Procedencia de fuentes](SOURCE_PROVENANCE.md) | Origen (repo/branch/commit/PR #5), inclusiones/exclusiones y arreglos de enlaces |
| [RFC-002 — Protocolo Console ↔ Platform](rfc/002-console-platform-protocol.md) | Antecedente del canal Hub ↔ Operator |

### Architecture Decision Records (ADR)
- [ADR-0001 — División Hub/Operator/Runtime/Registry](adr/0001-hub-operator-runtime-registry-split.md)
- [ADR-0002 — Firma y verificación](adr/0002-signing-and-verification.md)
- [ADR-0003 — Contratos Blueprint y SetupPlan](adr/0003-blueprint-and-setup-plan-contracts.md)
- [ADR-0004 — Enrolamiento del Operator e identidad](adr/0004-operator-enrollment-and-identity.md)
- [ADR-0005 — Secrets bundle, OAuth y prohibición en prompts cowork](adr/0005-secrets-bundle-and-oauth.md)
- [ADR-0006 — Formato `nexus.pack.yaml`](adr/0006-nexus-pack-format.md)
- [ADR-0007 — Canales de actualización y rollout](adr/0007-update-channels-and-rollout.md)
- [ADR-0008 — Frontera OSS/comercial y licencia](adr/0008-oss-commercial-boundary-and-license.md)
- [ADR-0009 — Ediciones, entitlements y degradación](adr/0009-editions-entitlements-and-subscription-degradation.md)
- [ADR-0010 — Edición vs modalidad de despliegue](adr/0010-edition-vs-deployment-modality.md)
- [ADR-0011 — Arquitectura de documentación y canonicidad](adr/0011-documentation-architecture.md)
- [ADR-0012 — Stack local único de Personal v1](adr/0012-personal-local-stack-v1.md)

### Esquemas y ejemplos (`v1alpha1` + `v1alpha2`)
- [Índice de esquemas](schemas/README.md) — JSON Schema 2020-12.
- Esquemas: [`v1alpha1/`](schemas/v1alpha1/) · [`v1alpha2/`](schemas/v1alpha2/) · Ejemplos: [`examples/`](schemas/examples/) (válidos e [`invalid/`](schemas/examples/invalid/)).
- Validación y guardas de contrato: el harness autocontenido [`tests/validate_contracts.py`](../tests/validate_contracts.py) (esquemas, ejemplos, fixtures negativos e invariantes del stack Personal) se incluye **en este repo**; la suite de referencia (`test_managed_platform_schemas.py`: sobre de firma, enlaces relativos y unicidad canónica) vive además en la implementación **upstream** (Console/Runtime).

## Documentos superados (conservados como redirección)

| Documento | Superado por |
|---|---|
| [Visión: Portal Gestionado](vision/nexus-os-vision.md) | [Visión de Nexus OS](vision/nexus-os-vision.md) |
| [Visión: Personal + Hub por suscripción](vision/nexus-os-vision.md) | [Visión de Nexus OS](vision/nexus-os-vision.md) |
| [Arquitectura del Portal Gestionado](architecture/nexus-os-architecture.md) | [Arquitectura de Nexus OS](architecture/nexus-os-architecture.md) + [Spec B](specs/b-nexus-hub.md) |

> La Visión histórica de Nexus OS y RFC-001 viven en el repositorio `ironbat-jarvis` (Nexus Platform).
> Un PR compañero incorpora este delta a esa visión. Ver [ADR-0011](adr/0011-documentation-architecture.md)
> sobre la reconciliación de canonicidad.
