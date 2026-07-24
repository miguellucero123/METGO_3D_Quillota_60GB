# Runbook ops A1–A3 (producción METGO)

Checklist operativa para desbloquear API + datos E12 en Render/Supabase.
Frontends: ver también [`docs/manuales/DESPLIEGUE_VUE_CLOUDFLARE.md`](../manuales/DESPLIEGUE_VUE_CLOUDFLARE.md) (migración Netlify → Cloudflare Pages).

---

## A1 — Revisar y subir código (API en Render)

Render despliega desde **`master`**. Si trabajas en `main`, sincroniza ambas.

### PowerShell (repo raíz)

```powershell
cd D:\METGO_3D_Quillota_60GB

git status
git log -5 --oneline

# Cuando el usuario pida commit: staging + mensaje (no automatizar aquí).
# Tras commit:
git push origin HEAD:master
# Si también usas main:
# git push origin HEAD:main
```

### Esperar deploy

1. Render Dashboard → servicio **`metgo-api`** → Events → deploy verde.
2. Health:

```powershell
Invoke-RestMethod https://metgo-api.onrender.com/api/health
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/datos/fuentes?sitio=copiapo"
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/ml/dominios?sitio=copiapo"
```

**OK si:** `health` responde 200; `fuentes.total >= 1`; `ml/dominios.servibles >= 1`.

> Nota free tier: el primer request puede tardar (cold start). Reintentar a los ~30–60 s.

---

## A2 — Migración Supabase `fuentes` (E12)

Archivo:

`supabase/migrations/20260724170000_e12_fuentes_gobernanza.sql`

### Pasos

1. Supabase → proyecto METGO → **SQL Editor**.
2. Pegar y ejecutar el contenido del archivo (completo).
3. Verificar:

```sql
select id, sitio, proveedor, tipo_dato, estado
from public.fuentes
order by id;
```

4. Desde API:

```powershell
$r = Invoke-RestMethod "https://metgo-api.onrender.com/api/public/datos/fuentes?sitio=copiapo"
$r | ConvertTo-Json -Depth 4
# Preferible: origen = supabase (no solo seed_memoria)
```

Si la migración no está aplicada, la API puede seguir sirviendo seed en memoria: el endpoint no debe 500, pero la gobernanza no estará persistida.

---

## A3 — Secrets y cron en Render

### 3.1 Environment (servicio `metgo-api`)

| Variable | Acción |
|----------|--------|
| `CRON_SECRET` | Valor fuerte nuevo (no demo). Mismo valor en GitHub Actions secret `CRON_SECRET` si usas `.github/workflows/etl-meteo-cron.yml`. |
| `SUPABASE_URL` / `SUPABASE_KEY` | Ya requeridos (service role para writes). |
| `METGO_SMTP_*` | Opcional ahora; checklist en `.env.example`. |
| `METGO_SINCA_*` / `METGO_DMC_*` / `METGO_AGROMET_*` | Cuando haya CSV/keys (E12 resto). |
| `METGO_CORS_ORIGINS` | Incluir URLs reales de Netlify **y** Cloudflare `*.pages.dev` tras migrar front. |

Generar secret (ejemplo):

```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 40 | ForEach-Object { [char]$_ })
```

### 3.2 Cron externo (wake + sync)

**URL:**

```text
https://metgo-api.onrender.com/api/cron/sync?token=TU_CRON_SECRET
```

- Proveedor sugerido: [cron-job.org](https://cron-job.org) (o GitHub Actions ya cableado).
- Frecuencia: cada **6–12 h** (suficiente para free + wake).
- Método: GET (o el que espere la ruta; el workflow usa query `token=`).

### 3.3 Probar a mano

```powershell
$token = "PEGAR_CRON_SECRET"
Invoke-RestMethod "https://metgo-api.onrender.com/api/cron/sync?token=$token" |
  ConvertTo-Json -Depth 5
```

**OK si:** respuesta con bloques relevantes (`aire`, `dispersion`, `operaciones`, `sinca`/`oficiales` según código desplegado) y sin 401/403.

Cola de reintentos ETL:

```powershell
Invoke-RestMethod "https://metgo-api.onrender.com/api/public/datos/etl/retry-queue"
```

---

## A4 (siguiente) — Frontends Cloudflare

Con Netlify en pausa por créditos:

1. Seguir `docs/manuales/DESPLIEGUE_VUE_CLOUDFLARE.md`.
2. Crear 3 proyectos Pages (Quillota / Copiapó / Mantos).
3. Actualizar `METGO_CORS_ORIGINS` + smoke login.
4. Dejar Netlify en **Stop builds**.

Credenciales demo:

| Sitio | Usuario | Password |
|-------|---------|----------|
| Quillota | `admin` | `admin123` |
| Copiapó | `copiapo` | `copiapo123` |
| Mantos | `mantos` | `mantos123` |

---

## Orden mínimo (hoy)

1. [ ] Commit + `git push origin HEAD:master`
2. [ ] SQL `fuentes` en Supabase
3. [ ] `CRON_SECRET` en Render (+ GitHub si aplica) + 1 sync manual
4. [ ] Smoke health / fuentes / ml/dominios
5. [ ] Crear proyectos Cloudflare Pages y CORS

## Fase

Ops producción · E12 gobernanza · plataforma hosting.
