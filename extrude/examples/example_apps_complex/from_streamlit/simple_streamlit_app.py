"""Example of a streamlit app with a callable named "app" that will be found
by extrude's multi app runner."""

import streamlit as st


def app():
    st.write('this app doesn\'t do anything')
