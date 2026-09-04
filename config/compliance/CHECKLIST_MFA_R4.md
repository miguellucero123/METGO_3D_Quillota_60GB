# Checklist R4 — MFA admin (controles de acceso)

**Alcance:** cuentas con poder de romper producción (no MFA de usuarios finales del SaaS — backlog aparte).  
**Owner:** DPD + responsable técnico.

## Cuentas obligatorias con MFA

| Sistema | Quién | MFA | Notas |
|---------|-------|-----|-------|
| GitHub org/repo METGO | Admins + quien pushea | TOTP o security key | Settings → Password and authentication |
| Cloudflare (cuenta) | Quien edita Pages/DNS/tokens | TOTP | My Profile → Authentication |
| Render | Quien edita env / redeploy | TOTP | Account Settings → Security |
| Supabase proyecto | Owners | TOTP | Account → Multi-factor |
| Zoho / correo corporativo | Buzón notificaciones | 2FA + app password SMTP | |
| Stripe (cuando exista) | Owner | MFA nativo | |
| WordPress metgo3d.com | Admins | 2FA plugin o host | |

## Cloudflare Zero Trust (opcional P1+)

Si se protegen paneles internos o previews:

1. Cloudflare Zero Trust → Application → self-hosted / SaaS.  
2. Política: email @metgo3d.com + MFA.  
3. No sustituye JWT de producto para clientes.

## Criterio “R4 hecho”

- [ ] MFA activo en GitHub, Cloudflare, Render, Supabase (owners)  
- [ ] Lista de admins actualizada en `INVENTARIO_ENDPOINTS_R12.csv`  
- [ ] Sin cuentas compartidas; cada persona con identidad propia  
- [ ] (Opcional) Access en URLs internas

## Verificación

Cada admin: captura de “MFA enabled” en vault (sin secretos). Revisar trimestralmente.
