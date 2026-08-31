# Bootstrap METGO en otro PC (sin secretos)

Guía pública. Los valores reales van solo en `local/` (gitignored) o en un `.enc` cifrado.

## Qué hay en el repo vs qué es solo local

| En GitHub (OK) | Solo local / cifrado |
|----------------|----------------------|
| `.env.example` | `.env` |
| `local/*.example.*` | `local/METGO_VAULT.local.env` |
| `docs/ops/BOOTSTRAP_OTRO_PC.md` | `local/METGO_BOOTSTRAP.local.md` |
| `scripts/ops/vault_crypto.py` | `local/METGO_VAULT.local.enc` |
| [`INVENTARIO_CLAVES_PLATAFORMAS.md`](../roadmap/INVENTARIO_CLAVES_PLATAFORMAS.md) | Render / WP / Supabase dashboards |

Para regenerar el vault local desde tu `.env` (sin tocar git):

```powershell
python scripts/ops/fill_vault_from_env.py
```

## Primera vez en este PC

```powershell
cd D:\METGO_3D_Quillota_60GB
copy local\METGO_VAULT.local.example.env local\METGO_VAULT.local.env
copy local\METGO_BOOTSTRAP.local.example.md local\METGO_BOOTSTRAP.local.md
# Editar ambos con Notepad / Cursor — pegar secretos desde Render/WP
copy local\METGO_VAULT.local.env .env
```

Arranque: ver [`DESARROLLO_LOCAL.md`](../DESARROLLO_LOCAL.md).

## Llevar accesos a otro PC (cifrado)

En el PC origen (con vault ya rellenado):

```powershell
python scripts/ops/vault_crypto.py pack
# Genera local\METGO_VAULT.local.enc — copia a USB
```

En el PC destino (repo clonado + `pip install cryptography`):

```powershell
# Colocar METGO_VAULT.local.enc dentro de local\
python scripts/ops/vault_crypto.py unpack
copy local\METGO_VAULT.local.env .env
```

La passphrase no se guarda en ningún archivo: memorízala o usa un gestor de contraseñas.

## Cron-job.org → 503 y desactivación

Causa habitual: **Render free en cold start** (health tarda > timeout del cron).  
Este probe reciente: health timeout; el endpoint cron responde **401** sin token (servicio vivo tras despertar).

**Qué hacer:**

1. Preferir **GitHub Actions** ETL (wake + retry ya implementados).
2. Si usas cron-job.org: job de wake a `/api/health` (timeout largo) y luego sync con `?token=CRON_SECRET`.
3. Reactivar el job en https://cron-job.org tras ajustar URL/timeout.
4. Confirmar `CRON_SECRET` idéntico en Render y en la URL/header del cron.

Detalle operativo en la plantilla `local/METGO_BOOTSTRAP.local.example.md` §5.

## Formspree

Los formularios pueden seguir OK aunque falle el mail puntual: envíos quedan en el dashboard Formspree. No sustituye SMTP de la API (verify-email / alertas).

## Rotación de secretos

Ver [`DT-4-ROTACION_SECRETOS.md`](../roadmap/deuda-tecnica/DT-4-ROTACION_SECRETOS.md). Tras rotar en paneles, actualiza el vault local y vuelve a `pack`.
