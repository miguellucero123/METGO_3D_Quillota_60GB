#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Health extendido para operación y dashboard /estado."""

from __future__ import annotations

import os
import subprocess
import time
from typing import Any

_APP_START = time.time()


def _git_sha() -> str:
    sha = os.getenv("METGO_GIT_SHA", "").strip()
    if sha:
        return sha[:7]
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if out.returncode == 0:
            return out.stdout.strip()[:7]
    except Exception:
        pass
    return "dev"


def build_health_payload(services_health_fn) -> dict[str, Any]:
    base = dict(services_health_fn())
    base["version"] = _git_sha()
    base["uptime_s"] = int(time.time() - _APP_START)
    base["servicio"] = "METGO API REST"
    return base
