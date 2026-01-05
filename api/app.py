from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "up", "message": "Service is running"}), 200

@app.route('/api/resource', methods=['GET'])
def get_resource():
    return jsonify({"data": "sample resource"}), 200

@app.route('/api/resource', methods=['POST'])
def create_resource():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400
    return jsonify({"received": data}), 201

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)