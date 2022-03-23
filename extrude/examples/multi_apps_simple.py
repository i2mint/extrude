"""Multi apps example."""

from extrude.multi_app import dispatch_child_apps_from_module

import example_apps_simple

config = {
    'example_app_2.py': {
        'funcs_to_dispatch': 'func_list',
    }
}

dispatch_child_apps_from_module(example_apps_simple)
