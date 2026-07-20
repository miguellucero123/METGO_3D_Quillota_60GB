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
        meteo_repository = importlib.import_module("backend.08_Gestion_Datos.supabase.meteo_repository")
        client_module = importlib.import_module("backend.08_Gestion_Datos.supabase.client")
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
        meteo_repository = importlib.import_module("backend.08_Gestion_Datos.supabase.meteo_repository")
        client_module = importlib.import_module("backend.08_Gestion_Datos.supabase.client")
        if client_module.get_supabase_client():
            return meteo_repository.leer_registros(estacion_id, dias)
    except ImportError as e:
        print(f"Error al importar módulos de Supabase: {e}")
    except Exception as e:
        print(f"Error al leer de Supabase: {e}")

    print(f"Advertencia: No se pudieron leer los registros de Supabase para {estacion_id}")
    return []


def estadisticas_store() -> dict[str, Any]:
    import sys
    import importlib
    try:
        sys.path.append(str(_db_path().parent.parent.parent.parent))
        meteo_repository = importlib.import_module("backend.08_Gestion_Datos.supabase.meteo_repository")
        client_module = importlib.import_module("backend.08_Gestion_Datos.supabase.client")
        if client_module.get_supabase_client():
            return meteo_repository.estadisticas_store()
    except ImportError as e:
        print(f"Error al importar módulos de Supabase: {e}")
    except Exception as e:
        print(f"Error al obtener estadísticas de Supabase: {e}")

    return {"registros": 0, "estaciones": 0, "db": "supabase_error"}
