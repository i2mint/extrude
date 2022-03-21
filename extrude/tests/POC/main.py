# from functools import partial
# import json
# import os
# from plunk.tw.py2py_front_example.simple_pycode import foo, bar, confuser
# import streamlit.bootstrap
# from py2http import mk_app, run_app
# from py2http.util import run_process
#
# run_streamlit = partial(streamlit.bootstrap.run, command_line='', flag_options={})
# funcs = [foo, bar, confuser]
#
# if __name__ == '__main__':
#     with run_process(
#         func=run_app,
#         func_kwargs=dict(
#             app_obj=funcs,
#             publish_openapi=True,
#         ),
#         is_ready=3
#     ):
#         app = mk_app(funcs)
#         openapi_spec = json.dumps(app.openapi_spec)
#         dirname = os.path.dirname(__file__)
#         filename = os.path.join(dirname, 'run_streamlitfront.py')
#         run_streamlit(filename, args=[openapi_spec])
