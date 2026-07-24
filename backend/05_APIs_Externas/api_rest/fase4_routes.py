#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rutas Fase 4-5 — integración módulos 01-11."""

from __future__ import annotations

import os
from flask import Flask, g, jsonify, request

from api_rest.auth_routes import auth_required
from api_rest import services
from api_rest.integracion.estado_integracion import estado_modulos
from api_rest.integracion import (
    alertas_store,
    meteo_store,
    reportes_bridge,
    etl_sync,
    agricola_extra,
    notificaciones,
    drones_bridge,
    deploy_info,
    docs_index,
    testing_info,
    ml_registry,
)
from api_rest import ml_services


def register_fase4_routes(app: Flask) -> None:
    @app.get("/api/integracion/estado")
    def integracion_estado():
        """Público: grado de integración por módulo (checks dinámicos)."""
        return jsonify(estado_modulos())

    @app.get("/api/agricola/<estacion_id>/avanzado")
    @auth_required
    def agricola_avanzado(estacion_id: str):
        return jsonify(services.reporte_agricola_avanzado(estacion_id))

    @app.get("/api/agricola/cultivos")
    @auth_required
    def agricola_cultivos():
        return jsonify(agricola_extra.listar_cultivos())

    @app.get("/api/agricola/<estacion_id>/riego")
    @auth_required
    def agricola_riego(estacion_id: str):
        cultivo = request.args.get("cultivo", "palto")
        resumen = services.resumen_meteo(estacion_id)
        return jsonify(agricola_extra.recomendacion_riego(resumen, cultivo, estacion_id))

    @app.get("/api/agricola/<estacion_id>/economico")
    @auth_required
    def agricola_economico(estacion_id: str):
        return jsonify(agricola_extra.analisis_economico(estacion_id))

    @app.get("/api/agricola/<estacion_id>/<cultivo>/cronograma")
    @auth_required
    def agricola_cronograma(estacion_id: str, cultivo: str):
        """Cronograma de riego dinámico 7 días por cultivo."""
        try:
            return jsonify(services.cronograma_riego(estacion_id, cultivo))
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.get("/api/alertas/historial")
    @auth_required
    def alertas_historial():
        estacion = request.args.get("estacion")
        limite = request.args.get("limite", 50, type=int)
        return jsonify(alertas_store.listar_historial(estacion, limite))

    @app.get("/api/datos/meteo/store")
    @auth_required
    def datos_meteo_store():
        return jsonify(meteo_store.estadisticas_store())

    @app.get("/api/datos/fuentes")
    @auth_required
    def datos_fuentes():
        sitio = (request.args.get("sitio") or "").strip().lower() or None
        body = etl_sync.fuentes_datos()
        if sitio:
            try:
                from api_rest.integracion import fuentes_store

                body["gobernanza"] = fuentes_store.resumen_gobernanza(sitio)
            except Exception as exc:
                body["gobernanza"] = {"error": str(exc)}
        return jsonify(body)

    @app.get("/api/public/datos/fuentes")
    def public_datos_fuentes():
        """Catálogo de gobernanza de fuentes (E12), sin JWT."""
        sitio = (request.args.get("sitio") or "").strip().lower() or None
        try:
            from api_rest.integracion import fuentes_store

            return jsonify(fuentes_store.resumen_gobernanza(sitio))
        except Exception as exc:
            return jsonify({"error": str(exc)}), 503

    @app.get("/api/public/datos/oficiales/estado")
    def public_oficiales_estado():
        """Estado Agromet/DMC (códigos env + CSV)."""
        try:
            from api_rest import oficiales_service

            return jsonify(oficiales_service.estado_fuentes())
        except Exception as exc:
            return jsonify({"error": str(exc)}), 503

    @app.post("/api/datos/etl/sync")
    @auth_required
    def datos_etl_sync():
        body = request.get_json(silent=True) or {}
        dias = body.get("dias", 14)
        incluir_csv = body.get("incluir_csv", True)
        incluir_archive = body.get("incluir_archive", False)
        anios_archive = body.get("anios_archive", 5)
        return jsonify(
            etl_sync.sincronizar_estaciones(
                dias=int(dias),
                incluir_csv=bool(incluir_csv),
                incluir_archive=bool(incluir_archive),
                anios_archive=int(anios_archive),
                origen="rest",
            )
        )

    @app.get("/api/cron/sync")
    def cron_sync():
        secret = request.args.get("token")
        # El cron secret es obligatorio para que nadie sature la API externamente
        if not secret or secret != os.getenv("CRON_SECRET"):
            return jsonify({"error": "No autorizado"}), 401

        # Sync ligero 00/12 UTC; Archive opcional vía query (p. ej. cron semanal).
        raw_arch = (request.args.get("incluir_archive") or "false").strip().lower()
        incluir_archive = raw_arch in ("1", "true", "yes", "on")
        anios_archive = request.args.get("anios_archive", default=5, type=int) or 5
        res = etl_sync.sincronizar_estaciones(
            dias=3,
            incluir_csv=False,
            incluir_archive=incluir_archive,
            anios_archive=int(anios_archive),
            origen="cron",
        )
        # E7: ETL calidad del aire (CAMS → aire_registros) en el mismo cron.
        try:
            from api_rest import aire_service

            res["aire"] = aire_service.sincronizar_aire()
        except Exception as exc:
            res.setdefault("errores", []).append(f"aire: {exc}")
        # E7: ETL dispersión (inversión/viento/niebla → aire_dispersion).
        try:
            from api_rest import dispersion_service

            res["dispersion"] = dispersion_service.sincronizar_dispersion()
        except Exception as exc:
            res.setdefault("errores", []).append(f"dispersion: {exc}")
        # E8: ETL ventanas operacionales (faena → operaciones_ventanas).
        try:
            from api_rest import operaciones_service

            res["operaciones"] = operaciones_service.sincronizar_operaciones()
        except Exception as exc:
            res.setdefault("errores", []).append(f"operaciones: {exc}")
        # E7/E12: SINCA observado (CSV/códigos).
        try:
            from api_rest import sinca_service

            res["sinca"] = sinca_service.sincronizar_sinca()
        except Exception as exc:
            res.setdefault("errores", []).append(f"sinca: {exc}")
        # E12: Agromet/DMC observados (CSV / IDs env).
        try:
            from api_rest import oficiales_service

            res["oficiales"] = oficiales_service.sincronizar_oficiales()
        except Exception as exc:
            res.setdefault("errores", []).append(f"oficiales: {exc}")
        return jsonify(res)

    @app.get("/api/datos/etl/status")
    def datos_etl_status():
        """Público: último ETL sin secretos (monitoreo / cron smoke)."""
        m = etl_sync.leer_etl_metrics()
        fuentes = etl_sync.fuentes_datos()
        return jsonify({
            "ultimo": m.get("ultimo"),
            "runs_en_historial": len(m.get("historial") or []),
            "fuentes": {k: v for k, v in fuentes.items() if k != "sqlite_meteo"},
            "sqlite_meteo_presente": bool(fuentes.get("sqlite_meteo")),
        })

    @app.get("/api/reportes/ultimos")
    @auth_required
    def reportes_ultimos():
        limite = request.args.get("limite", 10, type=int)
        return jsonify(reportes_bridge.listar_ultimos_reportes(limite))

    @app.get("/api/reportes/<nombre>")
    @auth_required
    def reporte_detalle(nombre: str):
        return jsonify(reportes_bridge.leer_reporte(nombre))

    @app.get("/api/reportes/tecnico/generar")
    def generar_reporte_tecnico():
        import sys
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        scripts_dir = os.path.join(backend_dir, "01_Sistema_Meteorologico", "scripts")
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)
            
        try:
            from ensemble_model import EnsembleMeteorologico
            from generador_informes import GeneradorInformesTecnicos
            
            # Obtener datos reales
            motor = EnsembleMeteorologico()
            datos = motor.obtener_ensemble_diario(dias=1)
            
            mediana_lluvia = 0.0
            if datos and len(datos) > 0:
                mediana_lluvia = datos[0]['precipitacion']['mediana']
                
            # Observación mockeada por ahora (luego se conectará a BD)
            observacion_hoy = mediana_lluvia + 2.3 
            
            generador = GeneradorInformesTecnicos()
            informe_txt = generador.generar_informe_precipitacion(
                observacion=observacion_hoy, 
                pronostico_mediana=mediana_lluvia, 
                modelos_count=5
            )
            return jsonify({"informe": informe_txt})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.get("/api/notificaciones/config")
    @auth_required
    def notif_config_get():
        return jsonify(notificaciones.leer_config())

    @app.put("/api/notificaciones/config")
    @auth_required
    def notif_config_put():
        body = request.get_json(silent=True) or {}
        return jsonify(notificaciones.guardar_config(body))

    @app.post("/api/notificaciones/probar")
    @auth_required
    def notif_probar():
        msg = (request.get_json(silent=True) or {}).get("mensaje", "Prueba METGO")
        return jsonify(notificaciones.enviar_prueba(msg))

    @app.get("/api/iot/drones")
    @auth_required
    def iot_drones():
        return jsonify(drones_bridge.resumen_drones())

    @app.get("/api/iot/satelital")
    @auth_required
    def iot_satelital():
        return jsonify(drones_bridge.info_satelital())

    @app.get("/api/ml/registry")
    @auth_required
    def ml_registry_get():
        return jsonify(ml_registry.leer_registro())

    @app.post("/api/ml/registry/sync")
    @auth_required
    def ml_registry_sync():
        return jsonify(ml_registry.sincronizar_registro())

    @app.post("/api/ml/predict/batch")
    @auth_required
    def ml_predict_batch():
        body = request.get_json(silent=True) or {}
        vars_ = body.get("variables")
        estacion = body.get("estacion_id", "quillota")
        return jsonify(ml_registry.prediccion_batch(vars_, estacion))

    @app.get("/api/testing/resumen")
    def testing_resumen():
        return jsonify(testing_info.resumen_tests())

    @app.get("/api/deploy/info")
    def deploy_info_route():
        return jsonify(deploy_info.resumen_deploy_publico())

    @app.get("/api/docs/indice")
    def docs_indice():
        return jsonify(docs_index.indice_documentacion())

    @app.get("/api/modulos/streamlit/cobertura")
    def streamlit_cobertura():
        from api_rest.catalog import MODULOS_SISTEMA

        st = [m for m in MODULOS_SISTEMA if m.get("tipo_acceso") == "streamlit"]
        migrados = [m for m in st if m.get("migrado_vue") or m.get("ruta_vue_alternativa")]
        return jsonify({
            "total_streamlit": len(st),
            "con_ruta_vue": len(migrados),
            "cobertura_pct": round(100 * len(migrados) / len(st)) if st else 100,
            "modulos": st,
        })

    @app.get("/api/ensemble")
    def get_ensemble():
        """Consenso multi-modelo (OpenMeteo) con caché y fallback a pronóstico.

        Orden: caché TTL/last-good → OpenMeteo ensemble → pronóstico/meteo_store
        (misma fuente que ya sirve /api/meteo cuando OpenMeteo falla en Render).
        """
        import sys
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        scripts_dir = os.path.join(backend_dir, "01_Sistema_Meteorologico", "scripts")
        if scripts_dir not in sys.path:
            sys.path.append(scripts_dir)

        try:
            from ensemble_model import EnsembleMeteorologico
            from api_rest import services

            def _desde_pronostico(estacion_id="quillota", dias=7):
                """Degrada a pronóstico diario real (OpenMeteo cache / Supabase)."""
                rows = services.pronostico_meteo(estacion_id, dias)
                if not rows:
                    return None
                out = []
                for r in rows:
                    precip = float(r.get("precipitacion") or 0)
                    tmin = r.get("temperatura_min")
                    try:
                        tmin_f = float(tmin) if tmin is not None else None
                    except (TypeError, ValueError):
                        tmin_f = None
                    pop = r.get("probabilidad_lluvia", r.get("pop"))
                    if pop is None:
                        probabilidad = 100.0 if precip > 0.5 else (40.0 if precip > 0 else 0.0)
                    else:
                        probabilidad = float(pop)
                    alerta = tmin_f is not None and tmin_f <= 2.5
                    if tmin_f is not None and tmin_f < 0:
                        tipo_helada = "Helada Radiativa (Alta Severidad)"
                    elif alerta:
                        tipo_helada = "Riesgo de Helada en Suelo"
                    else:
                        tipo_helada = "Ninguna"
                    out.append({
                        "fecha": r.get("fecha"),
                        "precipitacion": {
                            "mediana": round(precip, 1),
                            "best_match": round(precip, 1),
                            "minimo": round(precip, 1),
                            "maximo": round(precip, 1),
                            "probabilidad": round(probabilidad, 0),
                        },
                        "temperatura": {
                            "min_mediana": round(tmin_f, 1) if tmin_f is not None else None,
                            "alerta_helada": alerta,
                            "tipo_helada": tipo_helada,
                        },
                        "fuente": "pronostico_degradado",
                        "desde_cache": bool(r.get("desde_cache")),
                        "origen_fallback": r.get("origen_fallback") or "pronostico_meteo",
                    })
                return out if out else None

            def _fetch_multi():
                try:
                    from datos_reales_openmeteo import openmeteo_en_cooldown
                    if openmeteo_en_cooldown():
                        print("[ENSEMBLE] OpenMeteo en cooldown → saltando multi-modelo")
                        return None
                except ImportError:
                    pass
                motor = EnsembleMeteorologico()
                return motor.obtener_ensemble_diario(dias=7)

            # 1) Multi-modelo (con caché TTL / last-good). get_json_cached
            #    traga excepciones → el fallback a pronóstico va FUERA.
            datos = None
            try:
                gd = os.path.join(backend_dir, "08_Gestion_Datos")
                if gd not in sys.path:
                    sys.path.insert(0, gd)
                from cache_openmeteo import get_json_cached

                datos = get_json_cached(
                    "ensemble|quillota|7",
                    _fetch_multi,
                    es_valido=lambda x: isinstance(x, list) and len(x) > 0,
                )
            except ImportError:
                try:
                    datos = _fetch_multi()
                except Exception as exc:
                    app.logger.warning("ensemble multi: %s", exc)
                    datos = None

            # 2) Si OpenMeteo multi-modelo no responde (típico en Render free),
            #    degradar al mismo pronóstico/store que ya sirve /api/meteo.
            if not datos:
                try:
                    datos = _desde_pronostico("quillota", 7)
                    if datos:
                        try:
                            from cache_openmeteo import get_json_cached

                            # Sembrar last-good para no repetir el camino lento.
                            get_json_cached(
                                "ensemble|quillota|7",
                                lambda: datos,
                                es_valido=lambda x: isinstance(x, list) and len(x) > 0,
                            )
                        except Exception:
                            pass
                except Exception as exc:
                    app.logger.warning("ensemble fallback pronostico: %s", exc)
                    datos = None

            if not datos:
                return jsonify({
                    "error": "Sin datos de ensemble ni pronóstico de respaldo disponible"
                }), 503
            return jsonify(datos)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

