"""Authoritative Shiva UI/control contract.

Keep presentation fixes centralized here so legacy page CSS cannot reintroduce old
navigation, oversized controls, radio dots, or trophy backgrounds.
"""
from __future__ import annotations

# Import first so its st.html wrapper becomes the final presentation layer used by the
# runtime when app_header renders the application shell.
import shiva_fixes  # noqa: F401

# Preserve the ESPN-connected Coach extension and Draft Grade implementation.
import shiva_product as _shiva_product
from shiva_product_plus import render_full_product as _render_full_product_plus

_shiva_product.render_full_product = _render_full_product_plus
