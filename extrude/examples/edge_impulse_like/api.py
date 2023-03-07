import os
from py2http import run_app as run_webservice
from meshed import DAG

from streamlitfront.examples.edge_impulse_like import funcs


if __name__ == '__main__':
    port = 3030
    ws_config = dict(
        host='0.0.0.0',
        port=port,
        enable_cors=True,
        publish_openapi=True,
        publish_swagger=True,
        openapi=dict(base_url=f'http://localhost:{port}'),
    )
    run_webservice(funcs, **ws_config)
