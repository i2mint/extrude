"""Entrypoint for dispatching multiple child applications with a navigation root."""

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


def set_current_module(app_name):
    print(f'goto app_name: {app_name}')
    st.session_state['current_app'] = app_name


def render_root_nav(app_name_mapping: dict):
    st.set_page_config(layout='centered')
    st.header('Choose an app')
    for app_name, display_name in app_name_mapping.items():
        st.button(key=app_name, label=display_name, on_click=partial(set_current_module, app_name))


def mk_dflt_dispatch(module, configs):
    funcs = getattr(module, configs.get('funcs_to_dispatch', EXTRUDE_FUNCS), [])

    def dispatch():
        return dispatch_funcs(funcs, configs=configs)
    return dispatch


def dispatch_child_apps(modules: Iterable[types.ModuleType], configs: dict = None):
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

    def get_display_name(module):
        module_config = configs.get(module.__name__, getattr(module, 'extrude_configs', configs))
        return getattr(module, 'display_name', module_config.get('display_name', module.__name__))

    app_name_mapping = {module.__name__: get_display_name(module) for module in modules}
    module_mapping = {module.__name__: module for module in modules}
    if 'current_app' not in st.session_state:
        st.session_state['current_app'] = ROOT_APP

    current_app_name = st.session_state['current_app']
    if current_app_name == ROOT_APP:
        return render_root_nav(app_name_mapping)

    current_module = module_mapping[current_app_name]
    config_for_module = configs.get(current_app_name, getattr(current_module, 'extrude_configs', configs))
    app = getattr(current_module, 'app', config_for_module.get('app', None))
    print(f'app: {app}')
    if isinstance(app, str):
        app = getattr(current_module, app, config_for_module.get(app, None))
    if not callable(app):
        dispatch = config_for_module.get('dispatch', mk_dflt_dispatch(current_module, config_for_module))
        if isinstance(dispatch, str):
            dispatch = getattr(current_module, dispatch)
        app = dispatch()
    app()
    st.footer()
    st.button(label='Back to root', on_click=lambda: set_current_module(ROOT_APP))


def get_module_from_pathname(pathname):
    module_name = os.path.basename(os.path.normpath(pathname))
    if os.path.isdir(pathname):
        pathname = os.path.join(pathname, '__init__.py')
    spec = importlib.util.spec_from_file_location(module_name, pathname)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)
    print(f'module: {module}')
    return module


def dispatch_child_apps_from_paths(pathnames: Iterable[str],
                                   configs: dict = None):
    """Maps an iterable of pathnames to Python modules and calls dispatch_child_apps.

    :param pathnames: An iterable of paths to scan through. If a path
        points to a directory (a package), will look for __init__.py within that directory.
    :param configs: (Optional) See dispatch_child_apps.
    """
    modules = [get_module_from_pathname(pathname) for pathname in pathnames]
    return dispatch_child_apps(modules, configs)


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
    return dispatch_child_apps_from_paths(child_paths, configs)


def dispatch_child_apps_from_module(root_module: types.ModuleType, configs: dict = None):
    """Takes a root Python module and scans through its immediate children to dispatch functions.

    :param root_module: A module that contains one or more child packages to dispatch.
    :param configs: (Optional) See dispatch_child_apps.

    >>> import extrude.examples.example_apps as example_apps

    >>> dispatch_child_apps_from_module(example_apps)
    """
    root_filename = root_module.__file__
    root_dir = Path(root_filename).parent.absolute()
    return dispatch_child_apps_from_root(str(root_dir).replace('__pycache__/', ''), configs)
