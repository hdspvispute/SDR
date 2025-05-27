import json
import os
import random

# Construct the path to config/salesforce_config.json
# This assumes mcp_server is a subdirectory of the project root, and config is also a subdirectory of the project root.
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'salesforce_config.json')

def load_salesforce_config() -> dict | None:
    try:
        abs_config_path = os.path.abspath(CONFIG_FILE_PATH)
        # print(f"SF API (simulated): Attempting to load config from: {abs_config_path}") # For debugging path issues
        with open(abs_config_path, 'r') as f:
            config = json.load(f)
        return config.get('salesforce')
    except FileNotFoundError:
        print(f"SF API (Error): Configuration file not found at {abs_config_path}")
        return None
    except json.JSONDecodeError:
        print(f"SF API (Error): Invalid JSON in configuration file at {abs_config_path}")
        return None
    except Exception as e:
        print(f"SF API (Error): Unexpected error loading config: {e}")
        return None

def create_lead_in_salesforce(name: str, email: str, company: str) -> tuple[bool, str]:
    config = load_salesforce_config()
    if not config:
        return False, "Salesforce configuration missing or invalid."

    print(f"SF API (simulated): Using instance URL {config.get('instance_url', 'N/A')}")
    print(f"SF API (simulated): Authenticating with username {config.get('username', 'N/A')}")

    # Comment: In a real scenario, you would initialize simple-salesforce here:
    # from simple_salesforce import Salesforce
    # try:
    #     sf = Salesforce(
    #         username=config.get('username'),
    #         password=config.get('password'),
    #         security_token=config.get('security_token'),
    #         consumer_key=config.get('consumer_key'), # Or use session_id / instance_url for OAuth2
    #         consumer_secret=config.get('consumer_secret'),
    #         instance_url=config.get('instance_url')
    #     )
    #     print("SF API (simulated): Successfully authenticated with Salesforce.")
    # except Exception as e:
    #     print(f"SF API (simulated): Salesforce authentication failed: {e}")
    #     return False, f"Salesforce authentication failed: {e}"

    print(f"SF API (simulated): Attempting to create lead for Name: {name}, Email: {email}, Company: {company} using configured instance.")

    if not name or not email or not company:
        return False, "Missing required lead details for Salesforce."

    # Simulate API call (actual call would use 'sf.Lead.create(...)')
    if random.random() < 0.9:  # 90% success rate
        simulated_lead_id = f"SF_LEAD_{random.randint(10000, 99999)}"
        # print(f"SF API (simulated): Lead.create({{'LastName': name, 'Company': company, 'Email': email}}) successful.")
        print(f"SF API (simulated): Lead created successfully (authenticated). ID: {simulated_lead_id}")
        return True, simulated_lead_id
    else:
        error_msg = "SF API (simulated): Failed to create lead (authenticated) due to a simulated error."
        # print(f"SF API (simulated): Lead.create(...) failed.")
        print(error_msg)
        return False, error_msg

if __name__ == '__main__':
    # Test config loading
    conf = load_salesforce_config()
    if conf:
       print("SF Config loaded successfully (from __main__)")
    else:
       print("SF Config loading failed (from __main__)")
    
    print(create_lead_in_salesforce("Test User SF", "test-sf@example.com", "Test SF Company"))
    print(create_lead_in_salesforce("No Detail User", "", "")) # Test failure for missing details after config load
