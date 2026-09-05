# -*- coding: utf-8 -*-
"""Verificación rápida de flags S5 / E12 / OM vía /api/health (sin secretos).

Uso:
  python scripts/ops/check_prod_health_flags.py
  python scripts/ops/check_prod_health_flags.py --url https://metgo-api.onrender.com/api/health
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--url",
        default="https://metgo-api.onrender.com/api/health",
        help="URL health",
    )
    args = p.parse_args()
    with urllib.request.urlopen(args.url, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    s5 = data.get("s5_ops") or {}
    e12 = data.get("e12_ops") or {}
    print(f"status={data.get('status')} version={data.get('version')}")
    print(
        "om: usable={u} live={live} ciclo={c} lastgood_age_s={age} fuente={f} cooldown={cd}".format(
            u=data.get("openmeteo"),
            live=data.get("openmeteo_live"),
            c=data.get("ciclo_utc"),
            age=data.get("lastgood_age_s"),
            f=data.get("fuente_activa"),
            cd=data.get("openmeteo_cooldown_s"),
        )
    )
    print(f"supabase_ok={data.get('supabase_client_ok')} store_regs={data.get('meteo_store_registros')}")
    print(
        "s5: smtp={smtp} stripe={stripe} turnstile={ts} pii_kek={kek} pendiente={pend}".format(
            smtp=s5.get("smtp_configurado"),
            stripe=s5.get("stripe_configurado"),
            ts=s5.get("turnstile_configured"),
            kek=s5.get("pii_kek_configurado"),
            pend=s5.get("pendiente"),
        )
    )
    print(
        "e12: sinca={s} agromet={a} dmc={d} fuente_obs={fo} pendiente={pend}".format(
            s=e12.get("sinca_estado"),
            a=e12.get("agromet_disponible"),
            d=e12.get("dmc_disponible"),
            fo=e12.get("fuente_observado"),
            pend=e12.get("pendiente"),
        )
    )
    if data.get("status") != "ok":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
