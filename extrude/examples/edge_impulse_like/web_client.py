from streamlitfront.examples.edge_impulse_like import funcs, config_

from extrude.base import mk_web_app_from_funcs

if __name__ == '__main__':
    app = mk_web_app_from_funcs(
        funcs,
        api_url='http://localhost:3030',
        config=config_
    )
    app()