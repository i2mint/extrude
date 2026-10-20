# extrude.multi_app

Entrypoint for dispatching multiple child applications with a navigation root.

How to prepare an application for dispatch:

### Functions

| [`dispatch_child_apps`](#extrude.multi_app.dispatch_child_apps)(pathnames[, configs])      | Recurses through a Python module to collect objects that can be dispatched to a streamlit app.   |
|-------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| [`dispatch_child_apps_from_module`](#extrude.multi_app.dispatch_child_apps_from_module)(root_module)   | Takes a root Python module and scans through its immediate children to dispatch functions.       |
| [`dispatch_child_apps_from_root`](#extrude.multi_app.dispatch_child_apps_from_root)(root_dir[, ...]) | Lists the contents of a directory and passes the list to dispatch_child_apps_from_paths.         |
| [`dispatch_raw_module`](#extrude.multi_app.dispatch_raw_module)(spec)                      | Creates a callable that will execute a module when called.                                       |
| [`execute_module_spec`](#extrude.multi_app.execute_module_spec)(spec)                      | Imports a module into the current environment from a module spec and returns the module          |
| [`get_module_spec_from_pathname`](#extrude.multi_app.get_module_spec_from_pathname)(pathname)        | Creates an instance of importlib.machinery.ModuleSpec from a path.                               |
| `mk_dflt_dispatch`(module, configs)                                                             |                                                                                                  |
| `render_root_nav`(app_name_mapping)                                                             |                                                                                                  |
| `set_current_module`(app_name)                                                                  |                                                                                                  |

### extrude.multi_app.dispatch_child_apps(pathnames, configs=None)

Recurses through a Python module to collect objects that can be dispatched to a streamlit app.

* **Parameters:**
  * **pathnames** ([`Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]) – An iterable of files and/or directory to scan through. If a filename
    points to a directory (a package), will look for \_\_init_\_.py within that directory.
  * **configs** ([`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)) – (Optional) A dict that maps package names with configuration settings,
    allowing you to specify which object to import from the package and what function
    to use to dispatch that object to streamlit.

Example config:
: {“child_pkg_1”: {“import_name”: “funcs_to_dispatch”, “dispatcher”: my_dispatcher}}
  config[pkgname][‘dispatch’] can be a string to refer to a dispatcher within the module,
  or a reference to a callable from the root app. The default dispatcher will be
  streamlitfront.base.dispatch_funcs.

### extrude.multi_app.dispatch_child_apps_from_module(root_module, configs=None)

Takes a root Python module and scans through its immediate children to dispatch functions.

* **Parameters:**
  * **root_module** ([`ModuleType`](https://docs.python.org/3/library/types.html#types.ModuleType)) – A module that contains one or more child packages to dispatch.
  * **configs** ([`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)) – (Optional) See dispatch_child_apps.

```pycon
>>> import streamlit as st
>>> import extrude.examples.example_apps_simple as example_apps
>>>
>>> # this function call won't work correctly in the test environment
>>> # dispatch_child_apps_from_module(example_apps)
```

### extrude.multi_app.dispatch_child_apps_from_root(root_dir, configs=None)

Lists the contents of a directory and passes the list to dispatch_child_apps_from_paths.

* **Parameters:**
  * **root_dir** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – A path to a directory that contains one or more children to dispatch.
  * **configs** ([`dict`](https://docs.python.org/3/builtins/stdtypes.html#dict)) – (Optional) See dispatch_child_apps.

### extrude.multi_app.dispatch_raw_module(spec)

Creates a callable that will execute a module when called.
Used to run a streamlit app without needing to modify it.

* **Parameters:**
  **spec** – importlib.machinery.ModuleSpec

### extrude.multi_app.execute_module_spec(spec)

Imports a module into the current environment from a module spec and returns the module

### extrude.multi_app.get_module_spec_from_pathname(pathname)

Creates an instance of importlib.machinery.ModuleSpec from a path.
