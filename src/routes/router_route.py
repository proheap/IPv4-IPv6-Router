from flask import Blueprint, jsonify, request

from src.controllers.router_controller import Router

router_bp = Blueprint('router', __name__, url_prefix='/api/router')
router = Router()

@router_bp.route('route/add', methods=['PUT'])
def add_route():
    data = request.get_json()
    if router.addRoute(data['ip'], data['mask'], data['nextHop'], data['metric']):
        return jsonify({"success": True}), 201
    return jsonify({"error": "Could not create"}), 404

@router_bp.route('route/delete', methods=['PUT'])
def delete_route():
    data = request.get_json()
    if router.deleteRoute(data['ip'], data['mask'], data['nextHop']):
        return jsonify({"success": True}), 201
    return jsonify({"error": "Could not create"}), 404