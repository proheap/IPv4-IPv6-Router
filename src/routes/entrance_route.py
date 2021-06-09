from flask import Blueprint, render_template

import src.templates

entrance = Blueprint('entrance', __name__)

@entrance.route('/api', methods=['GET', 'PUT'])
def default_page():
   return render_template('index.html')