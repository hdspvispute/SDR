document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    function addMessage(message, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        if (isError) {
            messageDiv.classList.add('error-message'); // General error styling
        } else {
            messageDiv.classList.add(sender === 'user' ? 'user-message' : 'agent-message');
        }
        messageDiv.textContent = message; // Using textContent for security
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
    }

    async function sendMessage() {
        const messageText = userInput.value.trim();
        if (messageText === '') return;

        addMessage(messageText, 'user');
        userInput.value = '';
        userInput.focus(); // Keep focus on input

        try {
            const response = await fetch('http://localhost:5000/chat', { // Agent server
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText }),
            });

            if (!response.ok) {
                let errorMessage = `HTTP error ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = `Error: ${errorData.error || errorData.message || response.statusText}`;
                } catch (e) {
                    // If response is not JSON, use the status text
                    errorMessage = `Error: ${response.statusText}`;
                }
                addMessage(errorMessage, 'agent', true); // True for isError
                return;
            }

            const data = await response.json();
            if (data.response) {
                addMessage(data.response, 'agent');
            } else if (data.error) { // Handle cases where server returns a JSON with an error key but 200 OK
                addMessage(`Agent error: ${data.error}`, 'agent', true);
            } else {
                addMessage("Received an unexpected response from the agent.", 'agent', true);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            // Check if it's a connection error
            let displayError = 'Error connecting to the AI Sales Assistant. Please ensure the agent server is running on port 5000.';
            if (error instanceof TypeError && error.message.includes('fetch')) { // Often indicates network failure
                 displayError = 'Network error. Could not reach the AI Sales Assistant. Check your connection and if the server is running.';
            } else if (error.message) {
                displayError = `Connection Error: ${error.message}`;
            }
            addMessage(displayError, 'agent', true);
        }
    }

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Optional: Initial greeting or prompt from agent
    // To make this dynamic, you might have an initial "load" call or just let user initiate.
    // addMessage("Hello! I'm your AI Sales Assistant. Type 'hi' to start.", 'agent');
});
