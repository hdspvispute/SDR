from flask import Flask, request, jsonify

app = Flask(__name__)

# Import the salesforce_api module
# To make this work as a package, ensure __init__.py exists in mcp_server
# and use relative import if running as module, or direct if script
try:
    from . import salesforce_api 
except ImportError:
    import salesforce_api # Fallback for running script directly for now

@app.route('/create_lead', methods=['POST'])
def create_lead_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    name = data.get('name')
    email = data.get('email')
    company = data.get('company')

    if not all([name, email, company]):
        return jsonify({"status": "error", "message": "Missing name, email, or company"}), 400

    print(f"MCP Server: Received lead - Name: {name}, Email: {email}, Company: {company}")
    
    # Actual call to Salesforce API (simulated for now)
    success, message_or_id = salesforce_api.create_lead_in_salesforce(name, email, company)
    
    if success:
        print(f"MCP Server: Lead creation in Salesforce successful (simulated). ID: {message_or_id}")
        return jsonify({"status": "success", "message": "Lead processed by MCP and (simulated) Salesforce.", "salesforce_lead_id": message_or_id})
    else:
        print(f"MCP Server: Lead creation in Salesforce failed (simulated). Reason: {message_or_id}")
        return jsonify({"status": "error", "message": f"Salesforce simulation error: {message_or_id}"}), 500

if __name__ == '__main__':
    # Ensure there's an __init__.py in mcp_server for package context if needed
    # For Flask CLI (flask run), it might pick up app from file named app.py or wsgi.py
    # or by setting FLASK_APP=mcp_server.main:app environment variable.
    # Running directly `python mcp_server/main.py` should work with this.
    app.run(debug=True, port=5001)
