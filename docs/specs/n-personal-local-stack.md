# Spec N: Stack local de Personal v1 y contrato de bootstrap

- **Estado:** Diseño aprobado, no implementado (TARGET-STATE)
- **Versión de arquitectura:** `v1alpha2`
- **Fecha:** 2026-07-20
- **Contratos:** [`personal-stack.schema.json`](../schemas/v1alpha2/personal-stack.schema.json), [`assistant-handoff.schema.json`](../schemas/v1alpha2/assistant-handoff.schema.json), [`secret-bundle-ref.schema.json`](../schemas/v1alpha2/secret-bundle-ref.schema.json)
- **Relacionadas:** [ADR-0012](../adr/0012-personal-local-stack-v1.md), [ADR-0005](../adr/0005-secrets-bundle-and-oauth.md), [ADR-0010](../adr/0010-edition-vs-deployment-modality.md), [Spec A](a-personal-runtime.md), [Spec J](j-deployment-modalities.md), [Spec K](k-cli-sdk-installer-handoff.md), [Spec M](m-local-inference-voice-edge.md), [Spec H](h-security-trust-signing-secrets.md)

## 1. Problema y contexto

Personal es la edición gratuita, de un único dueño e independiente del Hub. Necesita **un** despliegue
local concreto y opinado que arranque sin pedir al dueño que evalúe arquitecturas, proveedores de nube,
bases de datos ni topologías. Esta spec fija ese stack (`personal-local-v1`) y el contrato de bootstrap
que lo instala. Es la contraparte de detalle de [ADR-0012](../adr/0012-personal-local-stack-v1.md).

## 2. Objetivos

- Definir el **único** stack local de Personal v1: componentes, red, persistencia, salud, backup, updates,
  comportamiento offline, logs y valores de seguridad por defecto.
- Definir el **contrato de bootstrap/CLI**: preflight, hardware, elección Anthropic/OpenAI, captura segura
  del secreto, validación, generación de ficheros, handoff al asistente, despliegue, verificación de salud
  e instalación de packs públicos.
- Fijar que el **lock `PersonalStack` es la fuente de verdad máquina** y que el `SETUP.md` es un render sin
  secretos en claro.

## 3. No-objetivos (prohibiciones de Personal)

Personal **nunca** hace, y el bootstrap **nunca** ofrece:

- Recomendación/evaluación de arquitectura.
- Selección de proveedor cloud / BYOC / managed.
- Elección de modalidad de despliegue (siempre `self_hosted` local).
- Proveedor LLM fuera de Anthropic/OpenAI en el arranque por defecto.
- Multiusuario.
- Packs premium/privados de Hub.
- Facturación.
- Operación de flota gestionada.

Todas son capacidades de **suscripción a Hub**. En el contrato se fijan `false` en `spec.boundaries` y el
harness lo verifica.

## 4. Componentes del stack `personal-local-v1` (TARGET-STATE)

| Área | Decisión fija | Notas |
|------|---------------|-------|
| Orquestación | un proyecto **Docker Compose** | `docker compose up` como camino base ([Spec K](k-cli-sdk-installer-handoff.md)) |
| Runtime | un servicio `runtime` | imagen con `resolved:false` (marcador TARGET-STATE; **no** hay imagen descargable afirmada) |
| Puertos | `127.0.0.1:8787` (http) | `bind_host` fijado a loopback |
| Persistencia | **SQLite** embebido, cifrado en reposo | `data_dir` en volumen local; `journal_mode: WAL`; migraciones `auto_on_start` |
| Almacenamiento | sistema de ficheros local | blobs/exports; sin S3/MinIO |
| Red | enlace `127.0.0.1`, sin escucha pública | `inbound_public:false`; TLS opcional en loopback |
| LLM | conectores **Anthropic y/o OpenAI** | al menos uno; ambos permitidos; claves **por referencia** |
| Secretos | esquema **age**, vault local | importados por bundle cifrado ([ADR-0005](../adr/0005-secrets-bundle-and-oauth.md)) |
| Voz | sidecar opcional (Voicebox, [Spec M](m-local-inference-voice-edge.md)) | apagado por defecto; su ausencia degrada solo la voz |
| Packs | carriles public/community | sin cuenta ni entitlement de Hub |

### 4.1 Pin de versiones

`pin_policy: digest` — en el release la imagen se fija por digest inmutable (`sha256:...`). Mientras no
exista imagen, `resolved:false` y no se declara `digest`: esto distingue el **contrato de despliegue
objetivo** de un **instalador ejecutable**.

### 4.2 Perfiles de hardware

Advisory. `minimum` y `recommended` en `spec.hardware`. La GPU **no** es requisito: el stack por defecto
usa inferencia hospedada Anthropic/OpenAI. El perfil totalmente offline (ollama) es un ejemplo avanzado
separado, no el arranque por defecto.

### 4.3 Salud, backup, updates, offline, logs, seguridad

- **Salud:** `liveness_path` (`/healthz`) y `readiness_path` (`/readyz`); el bootstrap verifica readiness
  antes de instalar packs.
- **Backup/export:** export completo de la instancia en cualquier momento (SQLite + blobs del volumen
  local), coherente con [Spec A](a-personal-runtime.md).
- **Updates/rollback:** cambio de digest de la imagen del runtime; rollback = digest anterior. Sin canal
  de control de Hub.
- **Offline:** el stack corre sin Hub; solo los conectores LLM salen a la red del proveedor elegido.
- **Logs:** locales al volumen; sin telemetría a Hub.
- **Seguridad por defecto:** loopback-only, cifrado en reposo, secretos por referencia y en vault local,
  sin escucha pública.

## 5. Modelo LLM (uno o ambos, por referencia)

- `spec.llm.providers`: `minItems 1`, `maxItems 2`; `provider ∈ {anthropic, openai}`.
- `secret_ref` es el **nombre** del secreto (p. ej. `ANTHROPIC_API_KEY`), nunca un valor. El esquema
  prohíbe `value/secret/plaintext/api_key/token/key` en la entrada del proveedor.
- `priority` (opcional): orden de preferencia cuando ambos están configurados; por defecto
  `[anthropic, openai]`. Es **routing**, no fija SKU, plan ni compra de modelos.
- `allow_fallback`: si el proveedor prioritario no está disponible, cae al siguiente configurado (solo
  tiene sentido con ambos).

## 6. Fuente de verdad y handoff

- **`PersonalStack` (lock) = única fuente de verdad máquina.**
- `AssistantHandoff` referencia el lock + `Blueprint` + `SetupPlan`, marca `setup_md.is_source_of_truth:
  false` y `contains_plaintext_secrets: false`, y `secret_handling.plaintext_in_prompt: false`.
- El asistente (Claude / OpenClaw / genérico) actúa con rol `setup_executor` y **nunca** recibe un secreto
  en claro en su prompt. Preferencia de adquisición: OAuth/device flow y, como último recurso, pegado
  manual en un formulario cifrado ([ADR-0005](../adr/0005-secrets-bundle-and-oauth.md)).

## 7. Contrato de bootstrap / CLI

Secuencia (mapea 1:1 a `setup.plan.personal-local.yaml`):

1. **preflight** — comprobar Docker/Compose y prerequisitos locales.
2. **hardware_check** — comparar con `spec.hardware.minimum` (advisory).
3. **select_llm_providers** — elegir Anthropic y/o OpenAI (al menos uno).
4. **capture_secrets** — captura segura (OAuth/device flow o formulario cifrado); produce el bundle age.
5. **validate_connector** — llamada de validación al proveedor con el secreto ya importado.
6. **generate_files** — emitir `PersonalStack` (fuente de verdad), `Blueprint`, `SetupPlan`,
   `AssistantHandoff` y el `SETUP.md` (render, sin secretos).
7. **deploy** — `docker compose up` del proyecto único.
8. **health_verify** — esperar readiness (`/readyz`).
9. **install_public_packs** — instalar packs public/community sin cuenta ni entitlement.

## 8. Invariantes verificados

`tests/validate_contracts.py` comprueba, además de la validez de esquemas y fixtures:

- **Sin dependencia de Hub:** `hub=none`, `operator=absent`, `requires_hub_account=false`.
- **Identidad de stack fija:** `stack_id == personal-local-v1`.
- **Uno o ambos proveedores por referencia:** `providers` 1–2, `anthropic/openai`, solo `secret_ref`.
- **Sin valores de secreto en claro** en los fixtures de bootstrap Personal.
- **Packs públicos sin entitlement.**
- **El `SETUP.md` no es fuente de verdad** y no contiene secretos.

Fixtures negativos (uno por motivo): `hub-dependency`, `wrong-stack-id`, `no-provider`,
`foreign-provider`, `plaintext-secret`, `multi-user` (PersonalStack); `with-value`
(secret-bundle-ref); `setup-md-source-of-truth` (AssistantHandoff).

## 9. Licencia y estado

El repositorio es **MIT** hoy; el objetivo por componente (Apache-2.0/propietario) sigue bloqueado por
auditoría legal ([ADR-0008](../adr/0008-oss-commercial-boundary-and-license.md)). Todo en esta spec es
**TARGET-STATE**: contrato de despliegue objetivo, no instalador ejecutable ni afirmación de imágenes
existentes. Nombre de display: **Nexus OS**; identificadores estables: `NexusOS`/`nexus`.
