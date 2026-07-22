#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persistencia histórica local (módulo 08 + 01) para complementar OpenMeteo."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


def _db_path() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p / "metgo_paths.py").exists():
            gd = p / "backend" / "08_Gestion_Datos" / "datos_runtime"
            gd.mkdir(parents=True, exist_ok=True)
            return gd / "meteo_historico.db"
    return Path("meteo_historico.db")


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estacion_id TEXT NOT NULL,
            fecha TEXT NOT NULL,
            temperatura_max REAL,
            temperatura_min REAL,
            humedad REAL,
            precipitacion REAL,
            viento REAL,
            presion REAL,
            fuente TEXT,
            UNIQUE(estacion_id, fecha)
        )
        """
    )
    conn.commit()


def guardar_registros(estacion_id: str, filas: list[dict[str, Any]], fuente: str = "openmeteo") -> int:
    import os
    import sys
    import importlib
    
    if not filas:
        return 0

    try:
        sys.path.append(str(_db_path().parent.parent.parent.parent))
        meteo_repository = importlib.import_module("backend.08_Gestion_Datos.supabase_db.meteo_repository")
        client_module = importlib.import_module("backend.08_Gestion_Datos.supabase_db.client")
        if client_module.get_supabase_client():
            return meteo_repository.guardar_registros(estacion_id, filas, fuente)
    except ImportError as e:
        print(f"Error al importar módulos de Supabase: {e}")
    except Exception as e:
        print(f"Error al guardar en Supabase: {e}")
        
    print(f"Advertencia: No se guardaron los registros en Supabase para {estacion_id}")
    return 0


def leer_registros(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    import sys
    import importlib
    try:
        sys.path.append(str(_db_path().parent.parent.parent.parent))
        meteo_repository = importlib.import_module("backend.08_Gestion_Datos.supabase_db.meteo_repository")
        client_module = importlib.import_module("backend.08_Gestion_Datos.supabase_db.client")
        if client_module.get_supabase_client():
            return meteo_repository.leer_registros(estacion_id, dias)
    except ImportError as e:
        print(f"Error al importar módulos de Supabase: {e}")
    except Exception as e:
        print(f"Error al leer de Supabase: {e}")

    print(f"Advertencia: No se pudieron leer los registros de Supabase para {estacion_id}")
    return []


def _repositorio():
    """Devuelve (meteo_repository, client_activo) o (None, False) si Supabase no está disponible."""
    import sys
    import importlib

    try:
        sys.path.append(str(_db_path().parent.parent.parent.parent))
        meteo_repository = importlib.import_module("backend.08_Gestion_Datos.supabase_db.meteo_repository")
        client_module = importlib.import_module("backend.08_Gestion_Datos.supabase_db.client")
        return meteo_repository, bool(client_module.get_supabase_client())
    except ImportError as e:
        print(f"Error al importar módulos de Supabase: {e}")
        return None, False


def guardar_pronostico(estacion_id: str, filas: list[dict[str, Any]], fuente: str = "openmeteo_pronostico") -> int:
    if not filas:
        return 0
    repo, activo = _repositorio()
    if repo and activo:
        try:
            return repo.guardar_pronostico(estacion_id, filas, fuente)
        except Exception as e:
            print(f"Error al guardar pronostico en Supabase: {e}")
    return 0


def leer_pronostico(estacion_id: str, dias: int = 7) -> list[dict[str, Any]]:
    repo, activo = _repositorio()
    if repo and activo:
        try:
            return repo.leer_pronostico(estacion_id, dias)
        except Exception as e:
            print(f"Error al leer pronostico de Supabase: {e}")
    return []


def guardar_serie(estacion_id: str, tipo: str, payload: dict[str, Any]) -> bool:
    if not payload:
        return False
    repo, activo = _repositorio()
    if repo and activo:
        try:
            return repo.guardar_serie(estacion_id, tipo, payload)
        except Exception as e:
            print(f"Error al guardar serie en Supabase: {e}")
    return False


def leer_serie(estacion_id: str, tipo: str, max_edad_horas: int = 48) -> dict[str, Any] | None:
    repo, activo = _repositorio()
    if repo and activo:
        try:
            return repo.leer_serie(estacion_id, tipo, max_edad_horas)
        except Exception as e:
            print(f"Error al leer serie de Supabase: {e}")
    return None


def guardar_helada_pronostico(
    estacion_id: str,
    filas: list[dict[str, Any]],
    cultivo: str = "palto",
    fuente: str = "modelo_helada_radiativa",
) -> int:
    if not filas:
        return 0
    repo, activo = _repositorio()
    if repo and activo:
        try:
            return repo.guardar_helada_pronostico(estacion_id, filas, cultivo, fuente)
        except Exception as e:
            print(f"Error al guardar helada en Supabase: {e}")
    return 0


def leer_helada_pronostico(
    estacion_id: str, dias: int = 7, cultivo: str = "palto"
) -> list[dict[str, Any]]:
    repo, activo = _repositorio()
    if repo and activo:
        try:
            return repo.leer_helada_pronostico(estacion_id, dias, cultivo)
        except Exception as e:
            print(f"Error al leer helada de Supabase: {e}")
    return []


def estadisticas_store() -> dict[str, Any]:
    import sys
    import importlib
    try:
        sys.path.append(str(_db_path().parent.parent.parent.parent))
        meteo_repository = importlib.import_module("backend.08_Gestion_Datos.supabase_db.meteo_repository")
        client_module = importlib.import_module("backend.08_Gestion_Datos.supabase_db.client")
        if client_module.get_supabase_client():
            return meteo_repository.estadisticas_store()
    except ImportError as e:
        print(f"Error al importar módulos de Supabase: {e}")
    except Exception as e:
        print(f"Error al obtener estadísticas de Supabase: {e}")

    return {"registros": 0, "estaciones": 0, "db": "supabase_error"}
