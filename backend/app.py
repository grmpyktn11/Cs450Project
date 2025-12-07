
from flask import Flask, request, jsonify
from flask_cors import CORS
import ApiFunctionTesting

app = Flask(__name__)
CORS(app)

@app.route("/api/returngame", methods=["POST"])
def answer():
    data = request.json
    gameReq = data.get("search")
    print("User sent:", gameReq)

    if not gameReq:
        return jsonify({"error": "No game specified"}), 400

    try:
        results = ApiFunctionTesting.searchGame(gameReq)
        if not results:
            return jsonify({"error": f"Game '{gameReq}' not found"}), 404
        
        # If it's a paid game, fetch price history
        if not results.get('isFree'):
            priceHistory = ApiFunctionTesting.getPriceHistory(results['id'])
            results['priceHistory'] = priceHistory
        
        return jsonify(results)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": f"Error fetching game '{gameReq}'"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)