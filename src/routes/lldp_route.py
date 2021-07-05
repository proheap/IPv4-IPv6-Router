from flask import Blueprint, jsonify, request

from src.routes.router_route import router

lldp_bp = Blueprint('lldp', __name__, url_prefix='/api/router/lldp')

@lldp_bp.route('run', methods=['GET'])
def lldp_run():
    if router.runLLDP():
        return jsonify({"success": True}), 201
    return jsonify({"error": "Running LLDP has been failed"}), 404

@lldp_bp.route('table', methods=['GET'])
def lldp_table():
    if router.enableLLDP:
        entries = router.getLLDPTable()
        jsonEntries = []
        index = 0
        for entry in entries:
            routeDict = entry.getJSON()
            routeDict['id'] = index
            jsonEntries.append(routeDict)
            index += 1
        return jsonify(jsonEntries), 201
    return jsonify({"error": "LLDP is not running"}), 404