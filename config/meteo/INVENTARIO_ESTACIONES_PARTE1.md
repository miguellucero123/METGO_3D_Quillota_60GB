# Inventario estaciones — parte 1 (2026-09-04)

**Estado:** integrado al repo · **Parte 2:** pendiente (usuario).  
**JSON env:** [`env_ids_recomendados.json`](env_ids_recomendados.json)

## Hallazgos clave

1. **DMC Quillota confirmado:** código **`320124`** (Liceo Agrícola) — reemplaza el candidato antiguo `330007`.  
2. **agrometeorologia.cl** (~480 estaciones) es la vía práctica CSV/Excel agro; códigos INIA internos a menudo no públicos.  
3. **SINCA Copiapó/Paipote/Tierra Amarilla** confirmados: `223` / `196` / `224`.  
4. **Chuquicamata** DMC `220901` (~1 km faena). Collahuasi / QB / Spence: **sin** estación pública &lt;50 km.  
5. **Torres del Paine:** DMC `510020` Río Serrano (vivo).  
6. Limache/Olmué/Hijuelas/Los Nogales: gaps / `pendiente_confirmacion`.

## P0 listos para env (Render)

```text
METGO_DMC_USAR_CANDIDATOS=1
METGO_DMC_IDS={"quillota":"320124","copiapo_centro":"270009","chuquicamata":"220901"}
METGO_SINCA_IDS={"copiapo_centro":"223","paipote":"196","tierra_amarilla":"224"}
```

## Por zona (resumen)

| Zona | Observado confirmado | Gaps |
|------|----------------------|------|
| Quillota | DMC 320124, FDF 320100 | La Cruz/Limache/Olmue códigos INIA |
| Copiapó | DMC 270002/270009 + SINCA 223/196/224 | — |
| Mantos | SINCA Antofagasta 259 (~39 km) | Sin estación faena pública |
| SPATI | Chuqui 220901; Calama 220002 | Collahuasi/QB/Spence &gt;50 km |
| Paine | DMC 510020 | — |

## Próximo (parte 2)

- Completar coords SINCA pendientes  
- IDs INIA La Cruz  
- Distancia Sierra Gorda 255 → Spence/Mantos  
- ETL: CSV DMC/SINCA automatizado  
- Convenios datos faena (opcional)

Detalle narrativo completo: elaborado 04-sep-2026 (sesión investigación). No mezclar NWP con OBSERVADO.
