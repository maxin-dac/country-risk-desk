# -*- coding: utf-8 -*-
"""Tests unitaires pour le module version."""

from src import version as ver


def test_get_project_version():
    v = ver.get_project_version()
    assert isinstance(v, str)
    assert len(v.split(".")) >= 3


def test_get_build_info():
    h, d = ver.get_build_info()
    assert isinstance(h, str)
    assert isinstance(d, str)


def test_version_string():
    vs = ver.version_string()
    assert vs.startswith("v")
    assert ver.get_project_version() in vs
