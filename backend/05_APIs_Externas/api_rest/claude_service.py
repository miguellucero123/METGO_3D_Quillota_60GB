#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cliente Anthropic Claude para asistente operacional VENTORA / METGO."""

from __future__ import annotations

import os
from typing import Any

import requests

_DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
_DEFAULT_MAX_TOKENS = 1024
_TIMEOUT_S = 60

_SYSTEM_VENTORA = """Eres el asistente operacional de VENTORA Izaje Mar (METGO 3D),
plataforma de pronóstico y alerta temprana para operaciones de izaje en terminales
marítimos de Chile.

Reglas:
- Responde en español, claro y accionable para jefes de faena y operadores de grúa.
- Prioriza seguridad: viento en altura, ITE, oleaje, marea y semáforos (verde/amarillo/rojo).
- No inventes mediciones: usa solo el contexto operativo que te entreguen.
- Si faltan datos, dilo y sugiere qué revisar en el panel VENTORA.
- No des consejos legales ni sustituyas protocolos internos del puerto.
- Sé breve: 1–3 párrafos o bullets, salvo que pidan detalle."""


def claude_configured() -> bool:
    return bool((os.getenv("ANTHROPIC_API_KEY") or "").strip())


def _resolve_endpoint() -> str:
    """Anthropic directo o proxy (p. ej. Cloudflare AI Gateway)."""
    base = (os.getenv("METGO_CLAUDE_BASE_URL") or "").strip().rstrip("/")
    if base:
        if base.endswith("/v1/messages"):
            return base
        if base.endswith("/v1"):
            return f"{base}/messages"
        return f"{base}/v1/messages"
    return "https://api.anthropic.com/v1/messages"


def _model() -> str:
    return (os.getenv("METGO_CLAUDE_MODEL") or _DEFAULT_MODEL).strip()


def chat(
    messages: list[dict[str, str]],
    *,
    system: str | None = None,
    contexto: dict[str, Any] | None = None,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """
    Llama a Messages API de Anthropic.

    messages: [{role: user|assistant, content: str}, ...]
    contexto: datos operativos opcionales (puerto, viento, alertas, etc.)
    """
    api_key = (os.getenv("ANTHROPIC_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY no configurada")

    clean: list[dict[str, str]] = []
    for m in messages or []:
        role = str(m.get("role") or "").strip().lower()
        content = str(m.get("content") or "").strip()
        if role not in ("user", "assistant") or not content:
            continue
        clean.append({"role": role, "content": content[:8000]})
    if not clean:
        raise ValueError("messages vacío o inválido")
    if clean[0]["role"] != "user":
        raise ValueError("el primer mensaje debe ser role=user")

    sys_prompt = (system or _SYSTEM_VENTORA).strip()
    if contexto:
        sys_prompt += "\n\nContexto operativo actual (JSON):\n" + _safe_contexto(contexto)

    payload = {
        "model": _model(),
        "max_tokens": int(max_tokens or os.getenv("METGO_CLAUDE_MAX_TOKENS") or _DEFAULT_MAX_TOKENS),
        "system": sys_prompt,
        "messages": clean[-12:],  # límite conversación
    }

    headers = {
        "x-api-key": api_key,
        "anthropic-version": os.getenv("ANTHROPIC_VERSION") or "2023-06-01",
        "content-type": "application/json",
    }
    # Cloudflare AI Gateway (BYOK / unified): token opcional
    aig = (os.getenv("CF_AIG_AUTHORIZATION") or "").strip()
    if aig:
        headers["cf-aig-authorization"] = aig if aig.lower().startswith("bearer ") else f"Bearer {aig}"

    resp = requests.post(_resolve_endpoint(), json=payload, headers=headers, timeout=_TIMEOUT_S)
    if resp.status_code >= 400:
        detail = resp.text[:500]
        raise RuntimeError(f"Anthropic HTTP {resp.status_code}: {detail}")

    data = resp.json()
    text = _extract_text(data)
    return {
        "reply": text,
        "model": data.get("model") or payload["model"],
        "usage": data.get("usage") or {},
        "id": data.get("id"),
        "stop_reason": data.get("stop_reason"),
    }


def _extract_text(data: dict[str, Any]) -> str:
    parts: list[str] = []
    for block in data.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text") or ""))
    return "\n".join(p for p in parts if p).strip() or "(sin respuesta de texto)"


def _safe_contexto(ctx: dict[str, Any]) -> str:
    import json

    # Limitar tamaño para no inflar tokens
    raw = json.dumps(ctx, ensure_ascii=False, default=str)
    if len(raw) > 6000:
        raw = raw[:6000] + "…"
    return raw
