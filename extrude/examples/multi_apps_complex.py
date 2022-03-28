"""Multi apps example with more complex inline configuration."""

from extrude.multi_app import dispatch_child_apps_from_module

import example_apps_complex

config = {
    'from_func_list': {'display_name': 'From_a_list_of_functions',},
}

dispatch_child_apps_from_module(example_apps_complex, config)
