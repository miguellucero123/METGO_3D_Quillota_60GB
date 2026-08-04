# Arreglar login demo (Supabase) — histórico

> **2026-08:** la cuenta fija `demo@ventora.demo` fue **retirada**.  
> No usar ni documentar claves de demostración públicas.  
> Para acceso temporal: `POST /api/auth/preview-hora` (clave aleatoria).  
> Para borrar la demo restante: aplicar `20260804160000_remove_demo_ventora.sql` o `DELETE /api/auth/preview-demo`.

## Diagnóstico (histórico: grants)

`GET /api/health` reportaba:

```text
permission denied for table usuarios_app
Grant SELECT ON public.usuarios_app TO service_role
```

Sin ese GRANT, la API no podía leer `usuarios_app`.

## Qué hacer hoy

1. Abrir [Supabase SQL Editor](https://supabase.com/dashboard) → proyecto METGO.
2. Aplicar grants si aún faltan: `supabase/migrations/20260731020000_preview_grants_demo_fijo.sql` (secciones 1–2; **omitir** el seed demo de la sección 3, o aplicar después el remove).
3. Aplicar `supabase/migrations/20260804160000_remove_demo_ventora.sql`.
4. En Render: no definir `METGO_SEED_DEMO_PREVIEW=1` (default off).
5. Verificar que el login demo falla:

```powershell
Invoke-RestMethod https://metgo-api.onrender.com/api/auth/login `
  -Method POST -ContentType "application/json" `
  -Body '{"username":"demo@ventora.demo","password":"x","sitio":"spati","faena":"quebrada_blanca"}'
# debe ser 401
```

## Fase

**Ops / S1 identidad** — grants + retiro demo fija.
