import os

from flask import Flask, request, jsonify
from odoo_service import create_portal_user
from odoo_service import get_quotation_stats

app = Flask(__name__)

@app.route('/quotation-stats', methods=['POST'])
def quotation_stats():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email required"}), 400

    result = get_quotation_stats(email)

    return jsonify(result)

@app.route('/smartarch/webhook/employee', methods=['POST'])
def create_employee():
    data = request.json

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and Email required"}), 400

    result = create_portal_user(name, email)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))