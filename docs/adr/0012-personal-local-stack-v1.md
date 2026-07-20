# ADR-0012: Stack local único de Nexus OS Personal v1

- **Estado:** Aceptada (contrato de producto `v1alpha2`, TARGET-STATE)
- **Fecha:** 2026-07-20
- **Versión de arquitectura:** `v1alpha2`
- **Relacionadas:** [ADR-0005](0005-secrets-bundle-and-oauth.md), [ADR-0008](0008-oss-commercial-boundary-and-license.md), [ADR-0009](0009-editions-entitlements-and-subscription-degradation.md), [ADR-0010](0010-edition-vs-deployment-modality.md), [Spec A](../specs/a-personal-runtime.md), [Spec J](../specs/j-deployment-modalities.md), [Spec K](../specs/k-cli-sdk-installer-handoff.md), [Spec N](../specs/n-personal-local-stack.md), [Visión de Nexus OS](../vision/nexus-os-vision.md)

## Contexto

Nexus OS Personal es la edición gratuita, de un solo dueño e independiente del Hub
([ADR-0009](0009-editions-entitlements-and-subscription-degradation.md)). Hasta ahora la documentación
describía capacidades del runtime Personal ([Spec A](../specs/a-personal-runtime.md)) y la ortogonalidad
edición/modalidad ([ADR-0010](0010-edition-vs-deployment-modality.md)), pero **no fijaba una arquitectura
de despliegue concreta** para el primer arranque. Sin una decisión bloqueada, un asistente de instalación
—o el propio dueño— podría creer que Personal debe **evaluar arquitecturas, elegir proveedor de nube,
base de datos o topología**, lo que contradice la promesa de producto: Personal es opinado y de fricción
mínima.

El único fragmento contradictorio era el ejemplo `blueprint.self-hosted-offline.yaml`, que usa inferencia
totalmente local (ollama). No es el arranque por defecto de Personal, sino un perfil offline avanzado; se
conserva sin cambios para no inventar un segundo stack en conflicto.

## Decisión

Personal v1 tiene **exactamente un stack de despliegue local, predefinido y opinado**, identificado de
forma fija como `personal-local-v1`. Queda bloqueado como el stack más pequeño y coherente posible,
compatible con la documentación existente (Docker Compose como base canónica, SQLite como memoria de
Personal en [Spec A](../specs/a-personal-runtime.md), cifrado de secretos age/X25519 en
[ADR-0005](0005-secrets-bundle-and-oauth.md)).

Componentes fijados (TARGET-STATE; ver [Spec N](../specs/n-personal-local-stack.md) para el detalle):

- **Orquestación:** un único proyecto Docker Compose (`docker compose up` como camino base).
- **Runtime:** un servicio contenedor `runtime`. La imagen se declara con `resolved: false` — es un
  marcador TARGET-STATE, **no** se afirma que exista una imagen descargable; el digest inmutable se fija
  en el release.
- **Persistencia:** SQLite embebido, cifrado en reposo, en un volumen local. Sin Postgres/pgvector/qdrant.
- **Almacenamiento:** sistema de ficheros local para blobs/exports. Sin S3/MinIO.
- **Red:** enlace a `127.0.0.1` por defecto, sin escucha entrante pública.
- **LLM:** conectores **Anthropic y/o OpenAI**. Al menos uno debe configurarse; ambos se permiten. Ningún
  otro proveedor forma parte del bootstrap por defecto. Las claves se aportan **solo por referencia**
  (nombre lógico), nunca por valor.
- **Secretos:** esquema age, vault local, importados por un bundle cifrado
  ([ADR-0005](0005-secrets-bundle-and-oauth.md)); referenciados por `secret-bundle-ref`.
- **Packs:** carriles públicos/community habilitados **sin cuenta ni entitlement** de Hub.

El **fichero de bloqueo `personal-stack.schema.json` (kind `PersonalStack`) es la única fuente de verdad
máquina**. El `SETUP.md` entregado al asistente de código es un **render** de esa fuente más el `SetupPlan`;
`AssistantHandoff` lo marca `is_source_of_truth: false` y `contains_plaintext_secrets: false`.

**Prohibiciones de Personal (fijadas `false` por construcción en `spec.boundaries`):** evaluación de
arquitectura, selección de proveedor cloud, elección de modalidad de despliegue, proveedor LLM no-default,
multiusuario, packs premium/privados de Hub, facturación y operación de flota gestionada. Todas ellas son
capacidades de **suscripción a Hub**, nunca de Personal.

## Consecuencias

- El bootstrap Personal no hace preguntas de arquitectura: preflight → hardware → elegir Anthropic/OpenAI →
  capturar secreto de forma segura → validar conector → generar ficheros → handoff al asistente → desplegar
  → verificar salud → instalar packs públicos ([Spec K](../specs/k-cli-sdk-installer-handoff.md),
  [Spec N](../specs/n-personal-local-stack.md)).
- Los invariantes se validan por contrato y por el harness `tests/validate_contracts.py`: sin dependencia
  de Hub, identidad de stack fija, uno-o-ambos proveedores por referencia, sin valores de secreto en claro,
  packs públicos sin entitlement.
- Coste: tres esquemas nuevos (`personal-stack`, `assistant-handoff`, `secret-bundle-ref`) y sus fixtures.
  A cambio, la frontera Personal/Hub queda inequívoca y verificable.
- No se toca la licencia: el repo sigue MIT hoy; el objetivo por componente (Apache-2.0/propietario) sigue
  bloqueado por auditoría legal ([ADR-0008](0008-oss-commercial-boundary-and-license.md)).

## Alternativas consideradas

- **Dejar la arquitectura abierta / preguntar al usuario:** rechazado; contradice la promesa de Personal
  (opinado, sin evaluación de arquitectura) y solapa con capacidad de Hub.
- **Inferencia totalmente local por defecto (ollama):** rechazado como *default*; requiere hardware que no
  todos tienen y complica el primer arranque. El perfil offline avanzado se conserva como ejemplo separado,
  no como el stack por defecto.
- **Postgres/pgvector desde el inicio:** rechazado para v1; SQLite embebido cubre al dueño único y evita un
  servicio extra.
- **Que el `SETUP.md` sea la fuente de verdad:** rechazado; un documento legible no puede ser autoritativo
  ni contener secretos. La fuente es el lock `PersonalStack`.
