from flask import Blueprint, jsonify, request

from src.controllers.router_controller import Router

router_bp = Blueprint('router', __name__, url_prefix='/api/router')
router = Router()

@router_bp.route('route/ipv4/add', methods=['POST'])
def add_ipv4_route():
    data = request.get_json()
    if router.addIPv4Route(data['ip'], data['mask'], data['nextHop'], data['metric']):
        return jsonify({"success": True}), 201
    return jsonify({"error": "Could not create"}), 404

@router_bp.route('route/ipv4/delete', methods=['PUT'])
def delete_ipv4_route():
    data = request.get_json()
    if router.deleteIPv4Route(data['ip'], data['mask'], data['nextHop']):
        return jsonify({"success": True}), 201
    return jsonify({"error": "Could not create"}), 404

@router_bp.route('route/ipv6/add', methods=['POST'])
def add_ipv6_route():
    data = request.get_json()
    if router.addIPv6Route(data['ip'], data['prefix'], data['nextHop'], data['metric']):
        return jsonify({"success": True}), 201
    return jsonify({"error": "Could not create"}), 404

@router_bp.route('route/ipv6/delete', methods=['PUT'])
def delete_ipv6_route():
    data = request.get_json()
    if router.deleteIPv6Route(data['ip'], data['prefix'], data['nextHop']):
        return jsonify({"success": True}), 201
    return jsonify({"error": "Could not remove"}), 404
