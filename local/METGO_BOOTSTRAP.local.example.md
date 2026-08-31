# METGO — Bootstrap en otro PC (plantilla)

> Copiar a `local/METGO_BOOTSTRAP.local.md`, rellenar y **nunca** commitear.
> Empaquetar cifrado: `python scripts/ops/vault_crypto.py pack`

## 1. Clonar y Python/Node

```powershell
git clone <URL_PRIVADA_DEL_REPO>
cd METGO_3D_Quillota_60GB
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Node 18+: `cd frontend\vue; npm install`

## 2. Restaurar secretos + docs internos

Opción A — archivo cifrado (USB / nube privada):

```powershell
# Traer METGO_VAULT.local.enc → carpeta local\
python scripts/ops/vault_crypto.py unpack
# Introduce la misma passphrase que usaste en pack
# Restaura: vault, .env, docs/, site-web/, templates/, loadtests/, …
copy local\METGO_VAULT.local.env .env
```

Detalle del bundle: `local/METGO_BUNDLE.local.example.md`

Opción B — a mano desde Render Dashboard + WP Application Password (sin docs).

## 3. Arranque local

```powershell
$env:METGO_ML_AUTO_TRAIN='0'
python backend\10_Deployment_Produccion\scripts\iniciar_api_rest.py
# otra terminal:
cd frontend\vue; npm run dev
```

- API: http://127.0.0.1:8080/api/health  
- Vue: http://127.0.0.1:5173  
Detalle: `docs/DESARROLLO_LOCAL.md`

## 4. Accesos (rellenar en tu copia .local)

| Qué | URL / dónde | Usuario / nota |
|-----|-------------|----------------|
| API prod | https://metgo-api.onrender.com | Render env |
| Streamlit | https://metgo-streamlit.onrender.com | |
| WordPress | https://metgo3d.com | WP_USER + app password |
| Formspree | https://formspree.io/f/mjybkaon | Email destino: **miguel.lucero@metgo3d.com** |
| cron-job.org | https://cron-job.org | ver §5 |
| Cloudflare | dash.cloudflare.com | Pages Quillota/SPATI/… |
| Supabase | app.supabase.com | service_role solo en API |
| GitHub | repo Actions | secret CRON_SECRET = Render |
| Zoho Mail | mail.zoho.com | SMTP app password |

## 5. Cron desactivado (503) — reactivar bien

Render free **duerme**: cron-job.org pegó `/api/cron/sync` → **503** ×41 → auto-off.

**Preferido:** dejar el ETL en GitHub Actions (`.github/workflows/etl-meteo-cron.yml`), que hace wake de `/api/health` + reintentos.

Si reactivas cron-job.org:

1. Job 1 (wake): `GET https://metgo-api.onrender.com/api/health` — timeout ≥120 s, 1 vez
2. Job 2 (sync, 2–3 min después): `GET https://metgo-api.onrender.com/api/cron/sync?token=CRON_SECRET` — timeout ≥180 s  
   Header opcional: `X-Cron-Token: CRON_SECRET`
3. No spamear cada minuto; alinear con 00/06/12/18 UTC como Actions

Comprobar: `Invoke-RestMethod https://metgo-api.onrender.com/api/health` (puede tardar 1–2 min en cold start).

## 6. Formspree

Endpoint WP: `https://formspree.io/f/mjybkaon`.  
Notificaciones al mail **miguel.lucero@metgo3d.com** (configurar en dashboard Formspree si aún apunta a otro buzón).  
Los envíos quedan en el dashboard aunque falle el correo puntual.

## 7. Checklist seguridad (DT-4)

- [ ] `.env` / `local/METGO_VAULT.local.*` no aparecen en `git status`
- [ ] Tras rotar secretos, actualizar vault y volver a `pack`
- [ ] No subir `.enc` a GitHub (solo USB / canal cifrado)
