#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Separación producto VENTORA (alta) vs ventora_mar (Izaje Mar)."""

from __future__ import annotations

from api_rest.identity.product_codes import (
    es_izaje_mar,
    es_ventora_alta,
    es_familia_ventora,
)
from api_rest.identity import identity_routes as ir


def test_product_codes_no_mezclar():
    assert es_izaje_mar("ventora_mar")
    assert es_izaje_mar("izaje-mar")
    assert not es_izaje_mar("ventora")
    assert es_ventora_alta("ventora")
    assert not es_ventora_alta("ventora_mar")
    assert es_familia_ventora("ventora")
    assert es_familia_ventora("ventora_mar")


def test_spa_bases_distintas():
    mar = ir._public_spa_base("spati", producto="ventora_mar")
    alta = ir._public_spa_base("spati", producto="ventora")
    assert "ventora-izaje-mar" in mar
    assert "metgo-spati" in alta
    assert mar != alta


def test_verify_paths():
    mar = ir._verify_email_url("spati", "iqq", "tok", producto="ventora_mar")
    alta = ir._verify_email_url("spati", "quebrada_blanca", "tok", producto="ventora")
    assert "/p/iqq/verificar?token=tok" in mar
    assert "/f/quebrada_blanca/verificar?token=tok" in alta
