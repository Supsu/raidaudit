"""
Test module for all modules the app uses.

Modules should have their own files only if their
testing requires very excessive imports or complicated
code that would warrant their own space.
"""

import app
import bnet
import rio
import wcl
import db


def test_app():
    a = app.app
    assert a is not None


def test_bnet():
    b = bnet.Bnet()
    assert b is not None


def test_rio():
    r = rio.RIO()
    assert r is not None


def test_wcl():
    w = wcl.WCL()
    assert w is not None


def test_db():
    d = db.Database()
    assert d is not None
