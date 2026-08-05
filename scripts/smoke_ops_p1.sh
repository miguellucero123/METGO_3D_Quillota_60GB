#!/usr/bin/env bash
# Wrapper del smoke ops (contratos reales). Preferí el Python:
#   python scripts/smoke_ops_p1.py
#   python scripts/smoke_ops_p1.py --public-only
#
# Credenciales (no hardcodear en el repo):
#   export CRON_SECRET=...
#   export METGO_SMOKE_USER=admin
#   export METGO_SMOKE_PASS=...
#   export METGO_SMOKE_SITIO=spati
#   export METGO_SMOKE_FAENA=escondida
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/smoke_ops_p1.py" "$@"
