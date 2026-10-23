from flask import Flask, render_template, request, jsonify
from Main import fact_check_pipeline

app = Flask(__name__)

# Serve the HTML page
@app.route('/')
def home():
    return render_template('index.html')

# API endpoint to handle the fact-check request from JavaScript
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    claim = data.get('claim', '')
    
    if not claim:
        return jsonify({"error": "Please enter a claim to analyze."}), 400

    try:
        # Call your existing function from Main.py
        report = fact_check_pipeline(claim)
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # use_reloader=False prevents the server from restarting mid-request
    app.run(debug=True, use_reloader=False, port=5000)