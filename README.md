# AI Sales Assistant with Salesforce MCP Integration

## Overview/Description

This project demonstrates an agentic AI solution designed to simulate an AI Sales Assistant that interacts with users via a chat interface. The assistant can understand user intent to create a sales lead and, upon confirmation, communicate with a Master Control Program (MCP) server. The MCP server is responsible for (simulating) the creation of this lead in a Salesforce environment.

This system showcases:
- Basic natural language understanding and conversational flow.
- Separation of concerns between an AI agent, a chat UI, and a backend service (MCP).
- A simulated integration with a CRM like Salesforce, highlighting how such an integration could be structured.

## Features

-   **AI Sales Agent** (`agent/`):
    -   A conversational agent that understands queries related to lead creation.
    -   Extracts lead details (name, email, company) from chat messages.
    -   Confirms extracted details with the user before proceeding.
    -   Communicates with the MCP server to request lead creation.
-   **Chat Interface** (`chat_interface/`):
    -   A simple web-based UI for users to chat with the AI Sales Assistant.
    -   Sends user messages to the agent and displays responses.
-   **MCP Server** (`mcp_server/`):
    -   Acts as a bridge between the AI agent and the (simulated) Salesforce service.
    -   Exposes an API endpoint (`/create_lead`) for the agent to call.
-   **Simulated Salesforce Integration** (`mcp_server/salesforce_api.py` & `config/`):
    -   Mimics the process of authenticating with Salesforce and creating a lead.
    -   Uses a configuration file (`config/salesforce_config.json`) for placeholder credentials.
-   **Lead Detail Extraction**: Basic NLP techniques (regex) to identify and extract lead information from unstructured text.

## Directory Structure

-   `agent/`: Contains the AI Sales Assistant logic, including its Flask server and NLP components.
-   `mcp_server/`: Houses the MCP server code, including the simulated Salesforce API interaction.
-   `chat_interface/`: Contains the HTML, CSS, and JavaScript for the user-facing chat window.
-   `config/`: Intended for configuration files. Currently holds `salesforce_config.json` (which should be gitignored and populated with placeholders locally).
-   `tests/`: Placeholder for future unit and integration tests.
-   `README.md`: This file.
-   `.gitignore`: Specifies files intentionally untracked by Git (e.g., `config/salesforce_config.json`, `__pycache__/`).

## Prerequisites

-   Python (3.8+ recommended)
-   Flask (`pip install Flask`)
-   Requests (`pip install requests`)
-   A modern web browser (e.g., Chrome, Firefox, Edge)

## Setup and Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create Salesforce Configuration File**:
    The MCP server expects a configuration file for Salesforce credentials. This file is ignored by Git for security reasons.
    -   Create a file named `salesforce_config.json` inside the `config/` directory.
    -   Populate it with the following JSON structure, using your placeholder Salesforce developer account details if you were to connect to a real instance (for this simulation, the placeholder values are fine):
        ```json
        {
            "salesforce": {
                "username": "YOUR_SF_USERNAME",
                "password": "YOUR_SF_PASSWORD",
                "security_token": "YOUR_SF_SECURITY_TOKEN",
                "consumer_key": "YOUR_SF_CONSUMER_KEY",
                "consumer_secret": "YOUR_SF_CONSUMER_SECRET",
                "instance_url": "https://your_instance.my.salesforce.com"
            }
        }
        ```

3.  **Set up a Virtual Environment (Recommended)**:
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    -   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    -   On Windows:
        ```bash
        venv\Scripts\activate
        ```

4.  **Install Dependencies**:
    ```bash
    pip install Flask requests
    ```

## Running the Application

To run the application, you need to start both the MCP Server and the Agent Server in separate terminals.

1.  **Terminal 1: Start the MCP Server**:
    Navigate to the project root directory and run:
    ```bash
    python mcp_server/main.py
    ```
    The MCP server will start, typically on `http://localhost:5001`.

2.  **Terminal 2: Start the Agent Server**:
    Navigate to the project root directory and run:
    ```bash
    python agent/main.py
    ```
    The Agent server will start, typically on `http://localhost:5000`.

3.  **Open the Chat Interface**:
    Open the `chat_interface/index.html` file in your web browser.

## How to Use

1.  Once the chat interface is open, you can start interacting with the AI Sales Assistant.
2.  **Greet the agent**: Type "Hello" or "Hi".
3.  **Express intent to create a lead**: For example, type "I want to create a new lead" or "Can you help me add a contact?".
4.  **Provide lead details**: The agent will ask for the name, email, and company of the lead. Provide these details in a single message (e.g., "The lead is John Doe, email john.doe@example.com, company Example Corp").
5.  **Confirm details**: The agent will show you the extracted details and ask for confirmation ("yes/no").
    -   If you type "yes", the agent will attempt to send the details to the MCP server, which will then simulate creating a lead in Salesforce. You'll receive a confirmation or an error message.
    -   If you type "no", the agent will ask you to provide the details again.

## Testing

-   **End-to-End Manual Testing**: The application has been tested manually by running both servers and interacting through the chat interface to ensure the workflow (chat -> agent -> MCP -> simulated Salesforce) functions correctly.
-   **Unit Tests**: The files `tests/test_agent.py` and `tests/test_mcp_server.py` are placeholders. In a production environment, these would be populated with comprehensive unit tests for each module.
