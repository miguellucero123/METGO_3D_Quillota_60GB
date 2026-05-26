# Desarrollo local METGO

## Opción A — scripts habituales (Windows)

1. API: `backend\10_Deployment_Produccion\scripts\iniciar_metgo_desarrollo.bat`
2. Vue: `cd frontend\vue && npm run dev`
3. Abrir http://127.0.0.1:5173

## Opción B — Docker Compose (Fase 2.5)

```bash
docker compose -f docker-compose.dev.yml up --build
```

- API: http://127.0.0.1:8080/api/health
- Vue: http://127.0.0.1:5173 (proxy a API vía `VITE_METGO_API`)

## Usuarios demo (Fase 2 RBAC)

| Usuario   | Contraseña | Rol      |
|-----------|------------|----------|
| admin     | admin123   | admin    |
| agronomo  | agro123    | agronomo |
| operador  | op123      | operador |
| lector    | lec123     | lectura  |
| user      | user123    | operador |
| metgo     | metgo2025  | agronomo |

## Tests

```powershell
python -m pytest tests/ -q
```

## Rutas Vue nuevas (Fase 2)

- `/meteo/historico` — histórico 30 días
- `/meteo/comparativo` — tabla multi-estación
- `/metricas` — KPIs globales
- `/alertas/config` — umbrales personalizados (roles operador+)
