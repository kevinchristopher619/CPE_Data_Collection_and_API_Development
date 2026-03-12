from flask import Flask, request, jsonify, send_file
import json
import os
from database import get_cpes_paginated, get_total_cpes_count, search_cpes

app = Flask(__name__)


def format_cpe_response(cpe_tuple):
    
    id_, title, reference_links_json, cpe_22_uri, cpe_23_uri, cpe_22_depr_date, cpe_23_depr_date = cpe_tuple
    
    try:
        reference_links = json.loads(reference_links_json) if reference_links_json else []
    except (json.JSONDecodeError, TypeError):
        reference_links = []
    
    return {
        "id": id_,
        "cpe_title": title,
        "cpe_22_uri": cpe_22_uri,
        "cpe_23_uri": cpe_23_uri,
        "reference_links": reference_links,
        "cpe_22_deprecation_date": cpe_22_depr_date,
        "cpe_23_deprecation_date": cpe_23_depr_date
    }



@app.route('/', methods=['GET'])
def index():
    
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend.html')
    try:
        return send_file(frontend_path)
    except FileNotFoundError:
        return jsonify({"message": "Frontend UI not found. Open frontend.html in your browser.", "api_endpoints": ["/api/health", "/api/cpes", "/api/cpes/search"]}), 200


@app.route('/api/health', methods=['GET'])
def health():
    
    return jsonify({"status": "ok"}), 200


@app.route('/api/cpes', methods=['GET'])
def get_cpes():
   
    try:
        # Get query parameters with defaults
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Validate parameters
        if page < 1:
            return jsonify({"error": "page must be >= 1"}), 400
        if limit < 1 or limit > 100:
            return jsonify({"error": "limit must be between 1 and 100"}), 400
        
        # Get total count
        total = get_total_cpes_count()
        
        # Get paginated CPEs
        cpes = get_cpes_paginated(page, limit)
        
        # Format response
        data = [format_cpe_response(cpe) for cpe in cpes]
        
        return jsonify({
            "page": page,
            "limit": limit,
            "total": total,
            "data": data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/cpes/search', methods=['GET'])
def search_cpes_endpoint():
    
    try:
        cpe_title = request.args.get('cpe_title', None)
        cpe_22_uri = request.args.get('cpe_22_uri', None)
        cpe_23_uri = request.args.get('cpe_23_uri', None)
        deprecation_date = request.args.get('deprecation_date', None)
        
        # At least one filter should be provided (optional validation)
        if not any([cpe_title, cpe_22_uri, cpe_23_uri, deprecation_date]):
            return jsonify({"error": "At least one search parameter required"}), 400
        
        # Search CPEs
        cpes = search_cpes(
            cpe_title=cpe_title,
            cpe_22_uri=cpe_22_uri,
            cpe_23_uri=cpe_23_uri,
            deprecation_date=deprecation_date
        )
        
        # Format response
        data = [format_cpe_response(cpe) for cpe in cpes]
        
        return jsonify({"data": data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("Starting CPE API server on http://localhost:5000")
    
    print("  GET /api/health - Health check")
    print("  GET /api/cpes?page=1&limit=10 - Get paginated CPEs")
    print("  GET /api/cpes/search?cpe_title=example - Search CPEs")
    app.run(debug=True, host='localhost', port=5000)