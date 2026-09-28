#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heladas METGO 3D — operación diaria de alertas por predio.

Datos de clientes (privados, fuera de git): data/heladas/predios.json
  (copiar scripts/heladas/predios.example.json y completar).

Uso:
  python scripts/heladas/alertas_heladas.py tarde              # boletín de la tarde (todos)
  python scripts/heladas/alertas_heladas.py tarde --email      # + envío por correo (SMTP u outbox)
  python scripts/heladas/alertas_heladas.py noche              # solo si el riesgo subió vs. la tarde
  python scripts/heladas/alertas_heladas.py validar            # compara con data/heladas/observado.csv

Salida para envío manual por WhatsApp: data/heladas/salida/<fecha>_<modo>.md
(cada predio trae un enlace wa.me con el texto precargado).
Registro de todo lo emitido: data/heladas/registro_pronosticos.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend" / "05_APIs_Externas"))

from metgo.paths import PROJECT_ROOT  # noqa: E402
from api_rest.heladas_predio_service import (  # noqa: E402
    TZ,
    PronosticoNoDisponibleError,
    debe_escalar,
    link_whatsapp,
    mensaje_whatsapp,
    pronostico_predio,
    validar_contra_observado,
)
from api_rest.integracion.openmeteo_multimodelo import MultiModeloNoDisponibleError  # noqa: E402

DIR = PROJECT_ROOT / "data" / "heladas"
PREDIOS = DIR / "predios.json"
ESTADO = DIR / "estado_ultimo.json"
REGISTRO = DIR / "registro_pronosticos.csv"
OBSERVADO = DIR / "observado.csv"
SALIDA = DIR / "salida"

CAMPOS_REGISTRO = [
    "emitido", "modo", "predio_id", "noche", "cultivo", "tmin_c", "sigma_c",
    "spread_modelos_c", "hora_min", "prob_helada_pct", "prob_accion_pct",
    "umbral_accion_c", "ajuste_tmin_c", "nivel", "n_modelos", "enviado",
]


def _leer_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def cargar_predios() -> list[dict]:
    if not PREDIOS.exists():
        sys.exit(
            f"No existe {PREDIOS}.\n"
            "Copia scripts/heladas/predios.example.json a esa ruta y completa tus clientes."
        )
    data = _leer_json(PREDIOS, [])
    return [p for p in data if p.get("activo", True)]


def _registrar(r: dict, modo: str, enviado: bool) -> None:
    nuevo = not REGISTRO.exists()
    with REGISTRO.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS_REGISTRO)
        if nuevo:
            w.writeheader()
        w.writerow({
            "emitido": r["emitido"], "modo": modo, "predio_id": r["predio_id"],
            "noche": r["noche_inicio"][:10], "cultivo": r["cultivo"], "tmin_c": r["tmin_c"],
            "sigma_c": r["sigma_c"], "spread_modelos_c": r["spread_modelos_c"],
            "hora_min": r["hora_min"], "prob_helada_pct": r["prob_helada_pct"],
            "prob_accion_pct": r["prob_accion_pct"], "umbral_accion_c": r["umbral_accion_c"],
            "ajuste_tmin_c": r["ajuste_tmin_c"], "nivel": r["nivel"],
            "n_modelos": r["n_modelos"], "enviado": int(enviado),
        })


def _enviar_email(predio: dict, texto: str, nivel: str) -> str:
    if not predio.get("email"):
        return "sin email"
    from api_rest.integracion.notificaciones import enviar_notificacion

    asunto = {
        "rojo": "🔴 Helada: prende control esta noche",
        "amarillo": "🟡 Heladas: atento esta noche",
    }.get(nivel, "🟢 Heladas: noche tranquila")
    res = enviar_notificacion(texto, asunto=f"{asunto} — {predio.get('nombre')}", destino=predio["email"])
    return "email ok" if res.get("ok") else f"email: {res.get('mensaje') or res.get('errores')}"


def cmd_boletin(modo: str, email: bool) -> int:
    DIR.mkdir(parents=True, exist_ok=True)
    SALIDA.mkdir(exist_ok=True)
    estado = _leer_json(ESTADO, {})
    ahora = datetime.now(TZ)
    bloques: list[str] = []
    errores = 0

    for predio in cargar_predios():
        pid = predio["id"]
        try:
            r = pronostico_predio(predio, ahora)
        except (MultiModeloNoDisponibleError, PronosticoNoDisponibleError) as exc:
            errores += 1
            bloques.append(f"## {predio.get('nombre', pid)}\n\n❌ SIN DATOS — NO ENVIAR ({exc})\n")
            continue

        anterior = estado.get(pid)
        if anterior and anterior.get("noche_inicio") != r["noche_inicio"]:
            anterior = None
        enviar = modo == "tarde" or debe_escalar(anterior, r)
        _registrar(r, modo, enviar)
        if not enviar:
            continue

        texto = mensaje_whatsapp(r, actualizacion=(modo == "noche"))
        link = link_whatsapp(predio.get("telefono"), texto)
        nota_email = _enviar_email(predio, texto, r["nivel"]) if email else ""
        estado[pid] = r
        bloques.append(
            f"## {r['predio_nombre']} — nivel {r['nivel'].upper()}\n\n"
            f"Modelos: {r['tmin_por_modelo_c']} · σ={r['sigma_c']} °C · "
            f"psicrómetro: {r['criterio_psicrometro'] or 'n/d'}\n"
            + (f"Factores: {'; '.join(r['factores'])}\n" if r["factores"] else "")
            + (f"{nota_email}\n" if nota_email else "")
            + (f"\n[Abrir WhatsApp]({link})\n" if link else "\n(sin teléfono)\n")
            + f"\n```\n{texto}\n```\n"
        )

    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
    archivo = SALIDA / f"{ahora:%Y-%m-%d_%H%M}_{modo}.md"
    cab = (
        f"# Heladas METGO 3D — {modo} {ahora:%Y-%m-%d %H:%M}\n\n"
        "Revisa cada pronóstico con tu criterio antes de enviarlo.\n\n"
    )
    if not bloques:
        bloques.append("Sin cambios de riesgo: no hay alertas extra que enviar.\n")
    archivo.write_text(cab + "\n".join(bloques), encoding="utf-8")
    print(f"Boletín escrito en {archivo}")
    return 1 if errores else 0


def cmd_validar() -> int:
    """observado.csv: predio_id,noche(YYYY-MM-DD),tmin_obs_c — lectura del termómetro del cliente."""
    if not OBSERVADO.exists() or not REGISTRO.exists():
        sys.exit(f"Faltan {OBSERVADO} y/o {REGISTRO}.")
    pron: dict[tuple[str, str], dict] = {}
    with REGISTRO.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["modo"] == "tarde":
                pron[(row["predio_id"], row["noche"])] = row  # queda el último boletín de la tarde
    pares: dict[str, list[tuple[float, float]]] = {}
    aciertos: dict[str, list[tuple[bool, bool]]] = {}
    with OBSERVADO.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p = pron.get((row["predio_id"], row["noche"]))
            if not p:
                continue
            pred, obs = float(p["tmin_c"]), float(row["tmin_obs_c"])
            pares.setdefault(row["predio_id"], []).append((pred, obs))
            aciertos.setdefault(row["predio_id"], []).append(
                (p["nivel"] == "rojo", obs <= float(p["umbral_accion_c"]))
            )
    predios = {p["id"]: p for p in _leer_json(PREDIOS, [])}
    for pid, lista in pares.items():
        v = validar_contra_observado(lista, float(predios.get(pid, {}).get("ajuste_tmin_c") or 0))
        a = aciertos[pid]
        falsas = sum(1 for alerta, ocurrio in a if alerta and not ocurrio)
        perdidas = sum(1 for alerta, ocurrio in a if ocurrio and not alerta)
        print(
            f"{pid}: n={v['n']} sesgo={v['sesgo_c']:+} °C MAE={v['mae_c']} °C · "
            f"falsas alarmas={falsas} · eventos no alertados={perdidas} · "
            + (f"→ fija ajuste_tmin_c={v['ajuste_sugerido_c']}" if v["aplicar"] else "→ junta ≥3 noches")
        )
    if not pares:
        print("No hay noches observadas que coincidan con boletines de la tarde.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modo", choices=["tarde", "noche", "validar"])
    ap.add_argument("--email", action="store_true", help="enviar además por correo (METGO_SMTP_* u outbox)")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # consola Windows (cp1252)
    if args.modo == "validar":
        return cmd_validar()
    return cmd_boletin(args.modo, args.email)


if __name__ == "__main__":
    raise SystemExit(main())
