# Arquitectura operativa objetivo METGO 3D

## Estado actual validado
- Netlify aloja la SPA Vue y redirige /api/* hacia Render.
- Streamlit funciona como portal ejecutivo y soporte controlado.
- La API REST concentra auth, salud, modelos, ETL e integración.
- El manifest y el registry confirman 43/43 modelos servibles con datos reales.

## Flujo objetivo
| Capa | Rol | Fuente de verdad |
|---|---|---|
| Netlify/Vue | Frontend oficial | UI de negocio, navegación, módulos |
| Streamlit | Consola ejecutiva | Salud, KPIs, modelos, legacy controlado |
| API REST | Backend técnico | Datos reales, registry, health, auth |
| Legacy/Archive | Historial y soporte | Backups, scripts viejos, demos |

## Decisiones clave
- Los datos sintéticos quedan restringidos a fallback explícito o CI.
- Los dashboards antiguos no forman parte de la experiencia principal.
- Los backups y archivos obsoletos se consideran archivo, no runtime.
- El portal Streamlit muestra estado operacional en vez de una lista de scripts.

## Próximas tareas recomendadas
1. Mover backups y duplicados a una carpeta de archivo fuera del runtime.
2. Retirar referencias de navegación a dashboards obsoletos.
3. Añadir health de dashboards y data freshness si se quiere más control ejecutivo.
4. Crear un comando o checklist de despliegue único para producción.

## Riesgo si no se limpia
- Confusión entre versión oficial y legacy.
- Mayor probabilidad de ejecutar scripts de prueba por accidente.
- Deuda técnica acumulada en carpetas de respaldo.