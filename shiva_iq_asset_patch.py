"""Locked Shiva IQ asset patch.

Scope: replace only the Shiva IQ artwork in the bottom nav and Home Screen.
The approved repository asset is used directly; no generated/recreated artwork.
"""
from __future__ import annotations

import builtins

_PREVIOUS_COMPILE = builtins.compile
_ASSET_URL = "https://raw.githubusercontent.com/cmhart13-boop/OneMoreShiva/main/FDBBC710-B60A-4DA4-9582-F52D6210DB18.png"


def _patch(source: str) -> str:
    # sitecustomize injects the current generated SVG into app_core at compile time.
    # Replace only that SVG markup with the locked approved image asset.
    svg_start = '<span class="nav-icon shiva-iq-navicon"><svg class="shiva-iq-mark"'
    pos = source.find(svg_start)
    if pos >= 0:
        end = source.find('</svg></span>', pos)
        if end >= 0:
            end += len('</svg></span>')
            source = source[:pos] + (
                '<span class="nav-icon shiva-iq-navicon">'
                f'<img class="shiva-iq-mark" src="{_ASSET_URL}" alt="Shiva IQ">'
                '</span>'
            ) + source[end:]

    # Home Screen: preserve the existing container/layout and replace only its artwork.
    # The existing .home-shiva-brain element remains in place so no surrounding layout changes.
    locked_css = f'''\n<style id="locked-shiva-iq-asset">
.home-shiva-brain{{
  background-image:url("{_ASSET_URL}")!important;
  background-size:contain!important;
  background-position:center!important;
  background-repeat:no-repeat!important;
  opacity:1!important;
}}
.home-shiva-brain svg,.home-shiva-brain img:not(.approved-shiva-iq),.home-shiva-brain>*{{visibility:hidden!important;opacity:0!important;}}
.bottom-nav .shiva-iq-navicon{{overflow:visible!important;}}
.bottom-nav .shiva-iq-mark{{
  display:block!important;
  width:31px!important;
  height:31px!important;
  object-fit:contain!important;
  object-position:center!important;
  filter:none!important;
  opacity:.72!important;
}}
.bottom-nav a.active .shiva-iq-mark{{filter:none!important;opacity:1!important;}}
</style>\n'''
    anchor = "st.markdown(CSS, unsafe_allow_html=True)"
    if anchor in source:
        source = source.replace(anchor, anchor + "\nst.markdown(" + repr(locked_css) + ", unsafe_allow_html=True)", 1)
    return source


def _compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kwargs):
    if isinstance(source, str) and str(filename).endswith("app_core.py"):
        # Run the prior sitecustomize patch first, then lock the approved Shiva IQ asset.
        patched = _PREVIOUS_COMPILE(source, filename, mode, flags, dont_inherit, optimize, **kwargs)
        # The previous compiler returns code, so to guarantee ordering we instead patch source
        # before it reaches the previous compiler; sitecustomize's generated SVG is also matched
        # by a source-level replacement added below through its known literal.
        return patched
    return _PREVIOUS_COMPILE(source, filename, mode, flags, dont_inherit, optimize, **kwargs)

# Wrap the sitecustomize source patch itself by replacing its compile hook with a lightweight
# pre-transform. This is intentionally limited to app_core.py.
def _ordered_compile(source, filename, mode, flags=0, dont_inherit=False, optimize=-1, **kwargs):
    if isinstance(source, str) and str(filename).endswith("app_core.py"):
        # First apply the existing sitecustomize transformation by calling its patch function
        # directly when available, then apply the locked-asset transform and compile normally.
        import sitecustomize
        transformed = sitecustomize._patch_app_core(source)
        transformed = _patch(transformed)
        return sitecustomize._ORIGINAL_COMPILE(transformed, filename, mode, flags, dont_inherit, optimize, **kwargs)
    return _PREVIOUS_COMPILE(source, filename, mode, flags, dont_inherit, optimize, **kwargs)

builtins.compile = _ordered_compile
