# Arreglar login demo (Supabase)

## Diagnóstico

`GET /api/health` reporta:

```text
permission denied for table usuarios_app
Grant SELECT ON public.usuarios_app TO service_role
```

Sin ese GRANT, la API **no puede leer ni crear** `demo@ventora.demo` → login **401**.

## Qué hacer (5 minutos)

1. Abrir [Supabase SQL Editor](https://supabase.com/dashboard) → proyecto METGO.
2. Pegar y **Run** el archivo:

`supabase/migrations/20260731020000_preview_grants_demo_fijo.sql`

3. Verificar:

```powershell
(Invoke-RestMethod "https://metgo-api.onrender.com/api/health").supabase_error
# debe quedar vacío / null

Invoke-RestMethod https://metgo-api.onrender.com/api/auth/login `
  -Method POST -ContentType "application/json" `
  -Body '{"username":"demo@ventora.demo","password":"DemoVentora1!","sitio":"spati","faena":"quebrada_blanca"}'
# access_token presente
```

4. SPA: https://metgo-spati.pages.dev/login?faena=quebrada_blanca

| Campo | Valor |
|-------|--------|
| Usuario | `demo@ventora.demo` |
| Clave | `DemoVentora1!` |

## Fase

**Ops / S1 identidad** — grants + seed demo.
