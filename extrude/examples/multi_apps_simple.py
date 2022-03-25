"""Multi apps example."""

from extrude.multi_app import dispatch_child_apps_from_module

import example_apps_simple


dispatch_child_apps_from_module(example_apps_simple)
