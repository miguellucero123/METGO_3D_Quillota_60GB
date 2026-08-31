#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rellena local/METGO_VAULT.local.* desde .env (gitignored). No imprime secretos."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env"
VAULT_PATH = ROOT / "local" / "METGO_VAULT.local.env"
BOOT_PATH = ROOT / "local" / "METGO_BOOTSTRAP.local.md"


def parse_env(path: Path) -> dict[str, str]:
    vals: dict[str, str] = {}
    if not path.is_file():
        return vals
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def main() -> None:
    vals = parse_env(ENV_PATH)
    filled: dict[str, str] = {
        "METGO_OWNER": "miguel.lucero@metgo3d.com",
        "METGO_REPO_ROOT": str(ROOT),
        "METGO_API_PORT": vals.get("METGO_API_PORT") or "8080",
        "METGO_API_AUTH_REQUIRED": vals.get("METGO_API_AUTH_REQUIRED") or "1",
        "METGO_ALLOW_SELF_REGISTER": vals.get("METGO_ALLOW_SELF_REGISTER") or "0",
        "METGO_ENV": vals.get("METGO_ENV") or "development",
        "METGO_JWT_EXPIRATION_SECONDS": vals.get("METGO_JWT_EXPIRATION_SECONDS") or "3600",
        "RENDER_API_URL": "https://metgo-api.onrender.com",
        "RENDER_STREAMLIT_URL": vals.get("METGO_STREAMLIT_RENDER_URL")
        or "https://metgo-streamlit.onrender.com",
        "WP_URL": vals.get("WP_URL") or "https://metgo3d.com",
        "METGO_SMTP_HOST": vals.get("METGO_SMTP_HOST") or "smtp.zoho.com",
        "METGO_SMTP_PORT": vals.get("METGO_SMTP_PORT") or "587",
        "METGO_SMTP_USER": vals.get("METGO_SMTP_USER") or "miguel.lucero@metgo3d.com",
        "METGO_NOTIFY_EMAIL": vals.get("METGO_NOTIFY_EMAIL") or "miguel.lucero@metgo3d.com",
        "FORMSPREE_FORM_ID": "mjybkaon",
        "FORMSPREE_ENDPOINT": "https://formspree.io/f/mjybkaon",
        "FORMSPREE_EMAIL": "miguel.lucero@metgo3d.com",
        "URL_QUILLOTA": "https://metgo-quillota.pages.dev",
        "URL_SPATI": "https://metgo-spati.pages.dev",
        "URL_COPIAPO": "https://metgo-copiapo.pages.dev",
        "URL_MANTOS": "https://metgo-mantos.pages.dev",
        "URL_PAINE": "https://metgo-paine.pages.dev",
        "URL_WP": "https://metgo3d.com",
        "CRONJOB_ORG_URL": "https://metgo-api.onrender.com/api/cron/sync",
    }

    secret_keys = [
        "METGO_JWT_SECRET",
        "METGO_PII_KEK",
        "CRON_SECRET",
        "METGO_PASSWORD_ADMIN",
        "METGO_PASSWORD_USER",
        "METGO_PASSWORD_METGO",
        "METGO_PASSWORD_AGRONOMO",
        "METGO_PASSWORD_OPERADOR",
        "METGO_PASSWORD_LECTOR",
        "METGO_PASSWORD_COPIAPO",
        "METGO_PASSWORD_MANTOS",
        "METGO_PASSWORD_PAINE",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "WP_USER",
        "WP_APP_PASSWORD",
        "METGO_SMTP_PASSWORD",
        "METGO_CORS_ORIGINS",
        "METGO_STREAMLIT_RENDER_URL",
        "STRIPE_SECRET_KEY",
        "METGO_TURNSTILE_SECRET",
        "METGO_TURNSTILE_SITE_KEY",
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_ACCOUNT_ID",
        "GITHUB_PAT",
    ]
    for k in secret_keys:
        if vals.get(k):
            filled[k] = vals[k]

    if vals.get("METGO_STREAMLIT_RENDER_URL"):
        filled["RENDER_STREAMLIT_URL"] = vals["METGO_STREAMLIT_RENDER_URL"]
    if vals.get("CRON_SECRET"):
        filled["CRONJOB_ORG_TOKEN_QUERY"] = vals["CRON_SECRET"]

    def g(key: str, default: str = "") -> str:
        return filled.get(key, default)

    lines = [
        "# METGO vault local — rellenado desde .env + defaults del sistema",
        "# NO COMMITEAR. Formspree email: miguel.lucero@metgo3d.com",
        "# Regenerar: python scripts/ops/fill_vault_from_env.py",
        "",
        "# --- Identidad ---",
        f"METGO_OWNER={g('METGO_OWNER')}",
        f"METGO_REPO_ROOT={g('METGO_REPO_ROOT')}",
        "",
        "# --- API local ---",
        f"METGO_API_PORT={g('METGO_API_PORT')}",
        f"METGO_JWT_SECRET={g('METGO_JWT_SECRET')}",
        f"METGO_PII_KEK={g('METGO_PII_KEK')}",
        f"METGO_JWT_EXPIRATION_SECONDS={g('METGO_JWT_EXPIRATION_SECONDS')}",
        f"METGO_API_AUTH_REQUIRED={g('METGO_API_AUTH_REQUIRED')}",
        f"METGO_ALLOW_SELF_REGISTER={g('METGO_ALLOW_SELF_REGISTER')}",
        f"METGO_ENV={g('METGO_ENV')}",
        f"METGO_CORS_ORIGINS={g('METGO_CORS_ORIGINS')}",
        "",
        "# Break-glass",
        f"METGO_PASSWORD_ADMIN={g('METGO_PASSWORD_ADMIN')}",
        f"METGO_PASSWORD_USER={g('METGO_PASSWORD_USER')}",
        f"METGO_PASSWORD_METGO={g('METGO_PASSWORD_METGO')}",
        f"METGO_PASSWORD_AGRONOMO={g('METGO_PASSWORD_AGRONOMO')}",
        f"METGO_PASSWORD_OPERADOR={g('METGO_PASSWORD_OPERADOR')}",
        f"METGO_PASSWORD_LECTOR={g('METGO_PASSWORD_LECTOR')}",
        f"METGO_PASSWORD_COPIAPO={g('METGO_PASSWORD_COPIAPO')}",
        f"METGO_PASSWORD_MANTOS={g('METGO_PASSWORD_MANTOS')}",
        f"METGO_PASSWORD_PAINE={g('METGO_PASSWORD_PAINE')}",
        "",
        "# --- Render ---",
        f"RENDER_API_URL={g('RENDER_API_URL')}",
        f"RENDER_STREAMLIT_URL={g('RENDER_STREAMLIT_URL')}",
        f"CRON_SECRET={g('CRON_SECRET')}",
        "",
        "# --- Supabase ---",
        f"SUPABASE_URL={g('SUPABASE_URL')}",
        f"SUPABASE_KEY={g('SUPABASE_KEY')}",
        "",
        "# --- WordPress ---",
        f"WP_URL={g('WP_URL')}",
        f"WP_USER={g('WP_USER')}",
        f"WP_APP_PASSWORD={g('WP_APP_PASSWORD')}",
        "",
        "# --- SMTP / Formspree (destino: miguel.lucero@metgo3d.com) ---",
        f"METGO_SMTP_HOST={g('METGO_SMTP_HOST')}",
        f"METGO_SMTP_PORT={g('METGO_SMTP_PORT')}",
        f"METGO_SMTP_USER={g('METGO_SMTP_USER')}",
        f"METGO_SMTP_PASSWORD={g('METGO_SMTP_PASSWORD')}",
        f"METGO_NOTIFY_EMAIL={g('METGO_NOTIFY_EMAIL')}",
        f"FORMSPREE_EMAIL={g('FORMSPREE_EMAIL')}",
        f"FORMSPREE_FORM_ID={g('FORMSPREE_FORM_ID')}",
        f"FORMSPREE_ENDPOINT={g('FORMSPREE_ENDPOINT')}",
        "",
        "# --- Cloudflare / GitHub / Stripe ---",
        f"CLOUDFLARE_API_TOKEN={g('CLOUDFLARE_API_TOKEN')}",
        f"CLOUDFLARE_ACCOUNT_ID={g('CLOUDFLARE_ACCOUNT_ID')}",
        f"GITHUB_PAT={g('GITHUB_PAT')}",
        f"STRIPE_SECRET_KEY={g('STRIPE_SECRET_KEY')}",
        f"METGO_TURNSTILE_SECRET={g('METGO_TURNSTILE_SECRET')}",
        f"METGO_TURNSTILE_SITE_KEY={g('METGO_TURNSTILE_SITE_KEY')}",
        "",
        "# --- cron-job.org ---",
        f"CRONJOB_ORG_URL={g('CRONJOB_ORG_URL')}",
        f"CRONJOB_ORG_TOKEN_QUERY={g('CRONJOB_ORG_TOKEN_QUERY')}",
        "",
        "# --- URLs publicas ---",
        f"URL_QUILLOTA={g('URL_QUILLOTA')}",
        f"URL_SPATI={g('URL_SPATI')}",
        f"URL_COPIAPO={g('URL_COPIAPO')}",
        f"URL_MANTOS={g('URL_MANTOS')}",
        f"URL_PAINE={g('URL_PAINE')}",
        f"URL_WP={g('URL_WP')}",
        "",
    ]
    VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VAULT_PATH.write_text("\n".join(lines), encoding="utf-8")

    port = g("METGO_API_PORT", "8080")
    streamlit = g("RENDER_STREAMLIT_URL")
    wp = g("WP_URL")
    boot = f"""# METGO — Bootstrap local (RELLENADO — NO COMMITEAR)

> Secretos en `local/METGO_VAULT.local.env` (desde `.env`).
> Formspree notifica a: **miguel.lucero@metgo3d.com**
> Endpoint Formspree: https://formspree.io/f/mjybkaon

## Arranque

```powershell
cd {ROOT}
copy local\\METGO_VAULT.local.env .env
$env:METGO_ML_AUTO_TRAIN='0'
python backend\\10_Deployment_Produccion\\scripts\\iniciar_api_rest.py
# otra terminal:
cd frontend\\vue; npm run dev
```

- API: http://127.0.0.1:{port}/api/health
- Vue: http://127.0.0.1:5173

## Accesos

| Que | URL | Nota |
|-----|-----|------|
| API prod | https://metgo-api.onrender.com | CRON_SECRET en vault |
| Streamlit | {streamlit} | |
| WordPress | {wp} | WP_USER / WP_APP_PASSWORD en vault |
| Formspree form | https://formspree.io/f/mjybkaon | Email: miguel.lucero@metgo3d.com |
| Formspree dashboard | https://formspree.io | Revisar submissions / spam |
| Contacto | mailto:miguel.lucero@metgo3d.com | Mail canonico comercial |
| cron-job.org | https://cron-job.org | Wake /api/health luego sync?token= |
| Supabase | app.supabase.com | SUPABASE_* en vault |
| Quillota | https://metgo-quillota.pages.dev | |
| SPATI | https://metgo-spati.pages.dev | |
| Copiapo | https://metgo-copiapo.pages.dev | |
| Mantos | https://metgo-mantos.pages.dev | |
| Paine | https://metgo-paine.pages.dev | |

## Formspree

En el dashboard Formspree → formulario `mjybkaon` → Email / Notifications →
destino **miguel.lucero@metgo3d.com** (unico buzon comercial).

## Empaquetar otro PC

```powershell
python scripts\\ops\\vault_crypto.py pack
```

## Cron 503

Preferir GitHub Actions ETL. cron-job.org: wake health + `?token=CRON_SECRET` del vault/Render.
"""
    BOOT_PATH.write_text(boot, encoding="utf-8")

    from_env = sorted(k for k in secret_keys if vals.get(k))
    empty = sorted(k for k in secret_keys if not filled.get(k))
    print(f"OK vault -> {VAULT_PATH} (gitignored)")
    print(f"OK boot  -> {BOOT_PATH} (gitignored)")
    print(f"keys_from_env={len(from_env)} empty={len(empty)}")
    print("formspree_email=miguel.lucero@metgo3d.com form_id=mjybkaon")
    if empty:
        print("still_empty:", ",".join(empty))


if __name__ == "__main__":
    main()
