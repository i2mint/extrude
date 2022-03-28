"""Entrypoint for dispatching multiple child applications with a navigation root.

How to prepare an application for dispatch:

"""

import os
from functools import partial
from pathlib import Path
import streamlit as st
from typing import Iterable
import importlib.util
import sys
import types

from streamlitfront.base import dispatch_funcs

ROOT_APP = '__extrude_root__'
EXTRUDE_FUNCS = 'extrude_funcs'


def execute_module_spec(spec):
    """Imports a module into the current environment from a module spec and returns the module"""
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)
    return module


def dispatch_raw_module(spec):
    """Creates a callable that will execute a module when called.
    Used to run a streamlit app without needing to modify it.

    :param spec: importlib.machinery.ModuleSpec
    """

    def app():
        return execute_module_spec(spec)

    return app


def get_module_spec_from_pathname(pathname: str):
    """Creates an instance of importlib.machinery.ModuleSpec from a path."""
    module_name = os.path.basename(os.path.normpath(pathname))
    if os.path.isdir(pathname):
        pathname = os.path.join(pathname, '__init__.py')
    return importlib.util.spec_from_file_location(module_name, pathname)


def set_current_module(app_name):
    st.session_state['current_app'] = app_name


def render_root_nav(app_name_mapping: dict):
    st.set_page_config(layout='centered')
    st.header('Choose an app')
    for app_name, display_name in app_name_mapping.items():
        st.button(
            key=app_name,
            label=display_name,
            on_click=partial(set_current_module, app_name),
        )


def mk_dflt_dispatch(module, configs):
    funcs = getattr(module, configs.get('funcs_to_dispatch', EXTRUDE_FUNCS), [])

    def dispatch():
        return dispatch_funcs(funcs, configs=configs)

    return dispatch


def dispatch_child_apps(pathnames: Iterable[str], configs: dict = None):
    """Recurses through a Python module to collect objects that can be dispatched to a streamlit app.

    :param pathnames: An iterable of files and/or directory to scan through. If a filename
        points to a directory (a package), will look for __init__.py within that directory.
    :param configs: (Optional) A dict that maps package names with configuration settings,
        allowing you to specify which object to import from the package and what function
        to use to dispatch that object to streamlit.

    Example config:
        {"child_pkg_1": {"import_name": "funcs_to_dispatch", "dispatcher": my_dispatcher}}
        config[pkgname]['dispatch'] can be a string to refer to a dispatcher within the module,
        or a reference to a callable from the root app. The default dispatcher will be
        streamlitfront.base.dispatch_funcs.
    """
    if not configs:
        configs = {}

    module_specs = [get_module_spec_from_pathname(pathname) for pathname in pathnames]

    def get_display_name(spec):
        module_config = configs.get(spec.name, configs)
        return module_config.get('display_name', spec.name)

    app_name_mapping = {spec.name: get_display_name(spec) for spec in module_specs}
    module_mapping = {spec.name: spec for spec in module_specs}
    if 'current_app' not in st.session_state:
        st.session_state['current_app'] = ROOT_APP

    current_app_name = st.session_state['current_app']
    if current_app_name == ROOT_APP:
        return render_root_nav(app_name_mapping)

    current_module_spec = module_mapping[current_app_name]
    config_for_module = configs.get(current_app_name, configs)
    app = config_for_module.get('app', None)
    if not app:
        app = dispatch_raw_module(current_module_spec)
    current_module = execute_module_spec(current_module_spec)
    if isinstance(app, str):
        app = getattr(current_module, app, config_for_module.get(app, None))
    if not callable(app):
        dispatch = config_for_module.get(
            'dispatch', mk_dflt_dispatch(current_module, config_for_module)
        )
        if isinstance(dispatch, str):
            dispatch = getattr(current_module, dispatch)
        app = dispatch()
    try:
        app()
    except Exception as error:
        st.error(str(error))
    st.sidebar.button(
        label='Back to root',
        key='backtoroot',
        on_click=lambda: set_current_module(ROOT_APP),
    )


def dispatch_child_apps_from_root(root_dir: str, configs: dict = None):
    """Lists the contents of a directory and passes the list to dispatch_child_apps_from_paths.

    :param root_dir: A path to a directory that contains one or more children to dispatch.
    :param configs: (Optional) See dispatch_child_apps.
    """
    root_pathname = os.path.abspath(root_dir)
    if not os.path.isdir(root_pathname):
        raise ValueError(f'{root_dir} is not a path to a directory.')
    children = [path for path in os.listdir(root_pathname) if not path.startswith('__')]
    child_paths = [os.path.join(root_pathname, child) for child in children]
    return dispatch_child_apps(child_paths, configs)


def dispatch_child_apps_from_module(
    root_module: types.ModuleType, configs: dict = None
):
    """Takes a root Python module and scans through its immediate children to dispatch functions.

    :param root_module: A module that contains one or more child packages to dispatch.
    :param configs: (Optional) See dispatch_child_apps.

    >>> import streamlit as st
    >>> import extrude.examples.example_apps_simple as example_apps
    >>>
    >>> # this function call won't work correctly in the test environment
    >>> # dispatch_child_apps_from_module(example_apps)
    """
    root_filename = root_module.__file__
    root_dir = Path(root_filename).parent.absolute()
    return dispatch_child_apps_from_root(
        str(root_dir).replace('__pycache__/', ''), configs
    )
