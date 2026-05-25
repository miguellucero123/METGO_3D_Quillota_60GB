#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Swagger UI y spec OpenAPI para la API METGO."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from flask import Response, render_template_string

_SPEC_PATH = Path(__file__).resolve().parent / "openapi.yaml"

_SWAGGER_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <title>METGO API — Documentación</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"/>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
  window.onload = () => {
    SwaggerUIBundle({
      url: "{{ spec_url }}",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout",
    });
  };
</script>
</body>
</html>"""


def _load_spec() -> dict:
    with open(_SPEC_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def register_docs_routes(app) -> None:
    @app.get("/api/openapi.json")
    def openapi_json():
        return Response(
            json.dumps(_load_spec(), ensure_ascii=False),
            mimetype="application/json",
        )

    @app.get("/api/docs")
    def swagger_ui():
        return render_template_string(_SWAGGER_HTML, spec_url="/api/openapi.json")
