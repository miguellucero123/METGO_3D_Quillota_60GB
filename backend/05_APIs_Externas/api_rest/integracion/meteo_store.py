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
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        try:
            import sys
            import importlib
            sys.path.append(str(_db_path().parent.parent.parent.parent)) # add backend to path if not there
            meteo_repository = importlib.import_module("08_Gestion_Datos.supabase.meteo_repository")
            client_module = importlib.import_module("08_Gestion_Datos.supabase.client")
            if client_module.get_supabase_client():
                return meteo_repository.guardar_registros(estacion_id, filas, fuente)
        except ImportError as e:
            pass
            
    if not filas:
        return 0
    path = _db_path()
    conn = sqlite3.connect(path)
    _init_db(conn)
    n = 0
    for row in filas:
        fecha = str(row.get("fecha") or row.get("actualizado") or "")[:10]
        if not fecha:
            continue
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO registros
                (estacion_id, fecha, temperatura_max, temperatura_min, humedad,
                 precipitacion, viento, presion, fuente)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    estacion_id,
                    fecha,
                    row.get("temperatura_max"),
                    row.get("temperatura_min"),
                    row.get("humedad"),
                    row.get("precipitacion"),
                    row.get("viento"),
                    row.get("presion"),
                    fuente,
                ),
            )
            n += 1
        except sqlite3.Error:
            continue
    conn.commit()
    conn.close()
    return n


def leer_registros(estacion_id: str, dias: int = 30) -> list[dict[str, Any]]:
    import os
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        try:
            import importlib
            meteo_repository = importlib.import_module("08_Gestion_Datos.supabase.meteo_repository")
            client_module = importlib.import_module("08_Gestion_Datos.supabase.client")
            if client_module.get_supabase_client():
                return meteo_repository.leer_registros(estacion_id, dias)
        except ImportError:
            pass
            
    path = _db_path()
    if not path.is_file():
        return []
    conn = sqlite3.connect(path)
    _init_db(conn)
    cur = conn.execute(
        """
        SELECT fecha, temperatura_max, temperatura_min, humedad, precipitacion, viento, presion, fuente
        FROM registros WHERE estacion_id = ?
        ORDER BY fecha DESC LIMIT ?
        """,
        (estacion_id, dias),
    )
    out = []
    for row in cur.fetchall():
        out.append(
            {
                "estacion_id": estacion_id,
                "fecha": row[0],
                "temperatura_max": row[1],
                "temperatura_min": row[2],
                "humedad": row[3],
                "precipitacion": row[4],
                "viento": row[5],
                "presion": row[6],
                "fuente": row[7] or "local_db",
            }
        )
    conn.close()
    return list(reversed(out))


def estadisticas_store() -> dict[str, Any]:
    import os
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
        try:
            import importlib
            meteo_repository = importlib.import_module("08_Gestion_Datos.supabase.meteo_repository")
            client_module = importlib.import_module("08_Gestion_Datos.supabase.client")
            if client_module.get_supabase_client():
                return meteo_repository.estadisticas_store()
        except ImportError:
            pass
            
    path = _db_path()
    if not path.is_file():
        return {"registros": 0, "estaciones": 0, "db": str(path)}
    conn = sqlite3.connect(path)
    _init_db(conn)
    total = conn.execute("SELECT COUNT(*) FROM registros").fetchone()[0]
    est = conn.execute("SELECT COUNT(DISTINCT estacion_id) FROM registros").fetchone()[0]
    conn.close()
    return {"registros": total, "estaciones": est, "db": str(path)}
