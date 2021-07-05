from flask import Flask, Blueprint

from configs.app_config import HTTP_API
from src.routes.api_route import api
from src.routes.router_route import router_bp
from src.routes.lldp_route import lldp_bp

def create_app():
    app = Flask(__name__, template_folder=HTTP_API.get('template_folder'))
    app.register_blueprint(api)
    app.register_blueprint(router_bp)
    app.register_blueprint(lldp_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(HTTP_API.get('host'), HTTP_API.get('port'), HTTP_API.get('debug'))