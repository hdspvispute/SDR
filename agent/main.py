from flask import Flask, request, jsonify
import requests # For calling MCP server
from agent.nlp import extract_lead_details

class SalesAgent:
    def __init__(self):
        self.awaiting_lead_details = False
        self.confirming_lead_details = False
        self.current_lead_details = None
        self.last_confirmed_lead_details = None # To store details before clearing for MCP call

    def handle_message(self, message: str) -> str:
        message_lower = message.lower()

        if self.confirming_lead_details:
            if "yes" in message_lower:
                self.confirming_lead_details = False
                # Store details for MCP call and clear current_lead_details
                if self.current_lead_details: # Ensure there are details to copy
                    self.last_confirmed_lead_details = self.current_lead_details.copy()
                else: # Should ideally not happen if logic is correct
                    self.last_confirmed_lead_details = None 
                self.current_lead_details = None
                # This response will be potentially overridden by the Flask endpoint after MCP call
                return f"Great! Processing lead for {self.last_confirmed_lead_details.get('name', 'N/A')}..."
            elif "no" in message_lower:
                self.confirming_lead_details = False
                self.awaiting_lead_details = True
                self.current_lead_details = None
                self.last_confirmed_lead_details = None
                return "My apologies. Please provide the details again, trying to clearly separate name, email, and company."
            else:
                return "Please answer 'yes' or 'no'. Are the details correct?"

        if self.awaiting_lead_details:
            extracted_details = extract_lead_details(message)
            # Check if any of the crucial details are "Not found" or None
            if not extracted_details.get("name") or \
               not extracted_details.get("email") or \
               not extracted_details.get("company"):
                # Keep awaiting_lead_details = True
                # Give feedback based on what was extracted
                name = extracted_details.get("name", "Not found")
                email = extracted_details.get("email", "Not found")
                company = extracted_details.get("company", "Not found")
                return f"I gathered: Name: {name}, Email: {email}, Company: {company}. Some details seem to be missing or weren't clear. Could you please provide them again, perhaps more explicitly (e.g., 'Name is John Doe, Email is john.doe@example.com, Company is Example Corp')?"
            else:
                self.current_lead_details = extracted_details
                self.awaiting_lead_details = False
                self.confirming_lead_details = True
                name = self.current_lead_details.get("name")
                email = self.current_lead_details.get("email")
                company = self.current_lead_details.get("company")
                return f"Okay, I have the following details: Name: {name}, Email: {email}, Company: {company}. Is this correct? (yes/no)"

        if "hello" in message_lower or "hi" in message_lower:
            self.awaiting_lead_details = False
            self.confirming_lead_details = False
            self.current_lead_details = None
            self.last_confirmed_lead_details = None
            return "Hello! I'm your AI Sales Assistant. I can help you identify and capture potential leads. How can I assist you today?"
        elif "lead" in message_lower or "contact" in message_lower or "connect" in message_lower or "opportunity" in message_lower:
            self.awaiting_lead_details = True
            self.confirming_lead_details = False
            self.current_lead_details = None
            self.last_confirmed_lead_details = None
            return "Great! I can help with that. Please provide the name, email, and company for the new lead."
        elif "thank you" in message_lower or "thanks" in message_lower:
            return "You're welcome! Let me know if there's anything else."
        elif "bye" in message_lower or "goodbye" in message_lower:
            return "Goodbye! Have a great day."
        else:
            return "I'm sorry, I'm not sure how to help with that. I can assist with capturing new sales leads. Would you like to create a new lead?"

agent_app = Flask(__name__)
sales_agent_instance = SalesAgent()

@agent_app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    user_message = data['message']
    
    # Store if agent was confirming before handling message
    was_confirming_before_handle = sales_agent_instance.confirming_lead_details
    # Get current lead details *before* handle_message might clear them if user says "yes"
    # This is a bit tricky because current_lead_details is cleared *inside* handle_message
    # The 'last_confirmed_lead_details' is set inside handle_message upon 'yes'
    
    agent_response_text = sales_agent_instance.handle_message(user_message)

    # Check if the state transitioned from confirming_lead_details to not confirming,
    # and last_confirmed_lead_details is now populated.
    if was_confirming_before_handle and \
       not sales_agent_instance.confirming_lead_details and \
       sales_agent_instance.last_confirmed_lead_details:
        
        lead_to_send = sales_agent_instance.last_confirmed_lead_details
        # Clear it from agent instance now that we have it locally in the endpoint
        sales_agent_instance.last_confirmed_lead_details = None 

        mcp_url = "http://localhost:5001/create_lead"
        print(f"Agent Endpoint: Attempting to send lead to MCP: {lead_to_send}")
        try:
            # Ensure requests library is installed in the environment where this runs
            mcp_response = requests.post(mcp_url, json=lead_to_send, timeout=10)
            mcp_response.raise_for_status() 
            mcp_data = mcp_response.json()
            print(f"Agent Endpoint: MCP response: {mcp_data}")
            if mcp_data.get("status") == "success":
                agent_response_text = f"Lead for {lead_to_send.get('name')} successfully registered with Salesforce (via MCP)! ID: {mcp_data.get('salesforce_lead_id', 'N/A')}. Can I help with anything else?"
            else:
                agent_response_text = f"Tried to create lead for {lead_to_send.get('name')}, but our sales system reported an error: {mcp_data.get('message', 'Unknown error')}. Please try again later or contact support."
        except requests.exceptions.ConnectionError as e:
            print(f"Agent Endpoint: Error calling MCP server (ConnectionError): {e}")
            agent_response_text = f"Sorry, I couldn't connect to our sales system to create the lead for {lead_to_send.get('name')}. Please ensure the MCP server is running and try again later."
        except requests.exceptions.Timeout as e:
            print(f"Agent Endpoint: Error calling MCP server (Timeout): {e}")
            agent_response_text = f"Sorry, the request to our sales system timed out while trying to create the lead for {lead_to_send.get('name')}. Please try again later."
        except requests.exceptions.HTTPError as e:
            print(f"Agent Endpoint: Error calling MCP server (HTTPError): {e}")
            status_code = e.response.status_code
            try:
                error_details = e.response.json().get("message", "No additional details")
            except ValueError: # Not JSON
                error_details = e.response.text
            agent_response_text = f"Sorry, there was an issue with our sales system (HTTP {status_code}: {error_details}) while creating the lead for {lead_to_send.get('name')}. Please try again."
        except requests.exceptions.RequestException as e: # Catch-all for other requests errors
            print(f"Agent Endpoint: Error calling MCP server (RequestException): {e}")
            agent_response_text = f"Sorry, an unexpected error occurred while trying to connect to our sales system for {lead_to_send.get('name')}. Please try again later."
            
    return jsonify({"response": agent_response_text})

if __name__ == "__main__":
    # Comment out or remove old test prints:
    # agent = SalesAgent()
    # print("--- Test Case 1: Full flow ---")
    # print("User: Hi")
    # print(f"Agent: {agent.handle_message('Hi')}")
    # ... and so on for all previous CLI tests
    
    print("Starting AI Sales Agent Flask server on port 5000...")
    print("MCP Server should be running on port 5001 for full functionality.")
    agent_app.run(debug=True, port=5000, use_reloader=False) # use_reloader=False can be helpful for cleaner logs with Flask
                                                            # especially when also running MCP server. Set to True if preferred.
