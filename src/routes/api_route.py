from flask import Blueprint, render_template

import src.templates

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('', methods=['GET', 'PUT'])
def default_page():
   return render_template('index.html')