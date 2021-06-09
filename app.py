from flask import Flask, Blueprint

from configs.app_config import HTTP_API
from src.routes.entrance_route import entrance

def create_app():
    app = Flask(__name__, template_folder=HTTP_API.get('template_folder'))
    app.register_blueprint(entrance)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(HTTP_API.get('host'), HTTP_API.get('port'), HTTP_API.get('debug'))