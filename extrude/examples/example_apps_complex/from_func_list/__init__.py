"""Example of a streamlit app with a list of callables named "extrude_funcs"
that will be found by extrude's multi app runner."""

from .funcs import foo, bar, confuser
extrude_funcs = [foo, bar, confuser]
