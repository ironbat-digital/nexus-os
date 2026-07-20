# Spec B: Nexus Hub — frontera pública (control plane propietario)

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha1` (infraestructura) + `v1alpha2` (producto)
- **Fecha:** 2026-07-20
- **Naturaleza:** El **Nexus Hub es el plano de control hospedado y propietario**. Su especificación
  detallada de desarrollo web (journeys, setup gestionado, onboarding, frontend/BFF, RBAC, criterios de
  aceptación) **no forma parte de este repositorio OSS**. Este documento describe únicamente su
  **frontera pública** y los **contratos** que emite o consume, para que los componentes OSS (Runtime,
  Operator, CLI/SDK, cliente de Registry) puedan interoperar con él sin conocer sus internals.
- **Implementación propietaria:** <https://github.com/ironbat-digital/nexus-hub>
- **Contratos (públicos, en este repo):** [`entitlement`](../schemas/v1alpha2/entitlement.schema.json), [`subscription-state`](../schemas/v1alpha2/subscription-state.schema.json), [`package-download-grant`](../schemas/v1alpha2/package-download-grant.schema.json), [`edition.declaration`](../schemas/v1alpha2/edition.declaration.schema.json), [`organization-policy`](../schemas/v1alpha2/organization-policy.schema.json), [`deployment-modality`](../schemas/v1alpha2/deployment-modality.schema.json), [`nexus.blueprint`](../schemas/v1alpha1/nexus.blueprint.schema.json), [`setup.plan`](../schemas/v1alpha1/setup.plan.schema.json), [`setup.task`](../schemas/v1alpha1/setup.task.schema.json), [`desired-state`](../schemas/v1alpha1/desired-state.schema.json), [`status-report`](../schemas/v1alpha1/status-report.schema.json), [`secrets-bundle-manifest`](../schemas/v1alpha1/secrets-bundle-manifest.schema.json).
- **Relacionadas:** [arquitectura system-wide](../architecture/nexus-os-architecture.md), [visión](../vision/nexus-os-vision.md), [frontera OSS/comercial](../architecture/product-oss-boundary.md), [ADR-0001](../adr/0001-hub-operator-runtime-registry-split.md), [ADR-0003](../adr/0003-blueprint-and-setup-plan-contracts.md), [ADR-0005](../adr/0005-secrets-bundle-and-oauth.md), [ADR-0009](../adr/0009-editions-entitlements-and-subscription-degradation.md), [Spec D](d-operator-instance-lifecycle.md), [Spec E](e-registry-catalog-distribution.md), [Spec G](g-entitlements-subscriptions-degradation.md), [Spec H](h-security-trust-signing-secrets.md), [Spec K](k-cli-sdk-installer-handoff.md).

> **Por qué este documento es un stub de frontera y no la spec completa.** El desarrollo web del Hub es
> el componente **propietario** del sistema (facturación, provisioning gestionado, orquestación de
> secretos a escala, catálogo curado, sitio y portal). Exponer su spec de implementación no es necesario
> para la interoperabilidad y queda fuera del alcance OSS. Lo que **sí** es público —y vive en este
> repositorio— son los contratos firmados que el Hub emite y los artefactos que entrega al Operator y al
> Runtime. Ver [ADR-0008](../adr/0008-oss-commercial-boundary-and-license.md) y
> [frontera producto/OSS](../architecture/product-oss-boundary.md).

## 1. Rol y contexto

El Hub es la **cara pública de la aplicación web** del sistema gestionado. Habilita las capacidades
oficiales de Team/Organization y los paquetes premium/privados que requieren un plano de control
hospedado: emite entitlements firmados, gestiona cuentas, guía la creación y el setup de instancias, y
sirve el catálogo curado. El Hub **no** custodia datos de negocio ni memoria (principio de soberanía);
hoy no existe como código.

## 2. Responsabilidades (frontera pública)

- Emitir **entitlements firmados** (Ed25519) por capacidad, con expiry/gracia/nonce/revision
  ([`entitlement`](../schemas/v1alpha2/entitlement.schema.json)).
- Publicar el **SubscriptionState** declarativo que gobierna la degradación graciosa
  ([`subscription-state`](../schemas/v1alpha2/subscription-state.schema.json)).
- Servir el **catálogo curado** y emitir **grants de descarga** de vida corta para carriles
  premium/privados ([`package-download-grant`](../schemas/v1alpha2/package-download-grant.schema.json)).
- Generar artefactos de **handoff** para ejecución por Operator, cowork o usuario:
  [`nexus.blueprint`](../schemas/v1alpha1/nexus.blueprint.schema.json),
  [`setup.plan`](../schemas/v1alpha1/setup.plan.schema.json), `SETUP.md` y un bundle de secretos cifrado
  opcional ([`secrets-bundle-manifest`](../schemas/v1alpha1/secrets-bundle-manifest.schema.json)).
- Declarar **ediciones** y **modalidades de despliegue**
  ([`edition.declaration`](../schemas/v1alpha2/edition.declaration.schema.json),
  [`deployment-modality`](../schemas/v1alpha2/deployment-modality.schema.json)) y aplicar
  **políticas de organización** ([`organization-policy`](../schemas/v1alpha2/organization-policy.schema.json)).
- Gestionar **flota** (solo metadatos y salud), miembros, roles, actualizaciones y soporte.

## 3. No-objetivos (invariantes de frontera)

- **No** custodia memoria, conversaciones ni datos de negocio.
- **No** ejerce shell remoto ni control imperativo de instancias: solo **estado deseado firmado**
  reconciliado por el Operator ([Spec D](d-operator-instance-lifecycle.md)).
- **No** hardcodea precios ni planes: la facturación es una abstracción; la habilitación se expresa por
  entitlements de capacidad ([ADR-0009](../adr/0009-editions-entitlements-and-subscription-degradation.md)).
- **No** retiene fuera del OSS nada de seguridad, exportación o portabilidad
  ([frontera producto/OSS](../architecture/product-oss-boundary.md)).

## 4. Interfaz con los componentes OSS

| Contraparte OSS | Dirección | Contrato |
|---|---|---|
| **Operator** ([Spec D](d-operator-instance-lifecycle.md)) | Hub → Operator | `desired-state`, `nexus.blueprint`, `setup.plan`, `setup.task`; Operator responde con `status-report` |
| **Entitlement Verifier** ([Spec G](g-entitlements-subscriptions-degradation.md)) | Hub → Runtime | `entitlement`, `subscription-state` (verificación offline en runtime) |
| **Cliente/instalador de Registry** ([Spec E](e-registry-catalog-distribution.md)) | Hub → cliente | `package-download-grant` para carriles cerrados; carriles abiertos no requieren Hub |
| **CLI/SDK y handoff** ([Spec K](k-cli-sdk-installer-handoff.md)) | Hub → herramientas OSS | artefactos de handoff (blueprint, setup plan, `SETUP.md`, bundle de secretos) |

Todos estos contratos son **públicos** y viven en [`docs/schemas/`](../schemas/README.md). La lógica
interna del Hub que los produce (UI, BFF, motor de facturación, orquestación) es propietaria y se
desarrolla en <https://github.com/ironbat-digital/nexus-hub>.

## 5. Enrolamiento e identidad

El canal Hub ↔ Operator, el enrolamiento y la identidad del Operator se especifican en
[Spec D](d-operator-instance-lifecycle.md) y [ADR-0004](../adr/0004-operator-enrollment-and-identity.md),
con antecedente en [RFC-002](../rfc/002-console-platform-protocol.md). La custodia y el bundle de
secretos siguen [ADR-0005](../adr/0005-secrets-bundle-and-oauth.md) y
[Spec H](h-security-trust-signing-secrets.md).
