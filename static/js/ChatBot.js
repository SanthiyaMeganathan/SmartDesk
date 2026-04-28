// 1. Grab the correct IDs from your ChatBot.html
const sendButton = document.getElementById('send-btn');
const userInput = document.getElementById('user-input');
const chatDisplay = document.getElementById('chat-box');

// 2. Function to draw the message on the screen
function addMessageToChat(sender, message) {
    const messageElement = document.createElement('div');
    
    // This adds two classes: 'message' and either 'user' or 'bot'
    messageElement.classList.add('message', sender); 
    messageElement.textContent = message;
    
    chatDisplay.appendChild(messageElement);
    chatDisplay.scrollTop = chatDisplay.scrollHeight; // Auto-scroll to the bottom
}

// 3. Main function to send and receive data
async function sendMessage() {
    const userMessage = userInput.value.trim();

    // Do nothing if the field is empty
    if (userMessage === '') return;

    // Display the user's message immediately and clear the input
    addMessageToChat('user', userMessage);
    userInput.value = '';

    try {
        // Send the message to your Flask /chatbot route
        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        });

        // EXTRACT THE RESPONSE FROM FLASK! 
        const data = await response.json();
        
        // Display the AI's response in the chat
        addMessageToChat('bot', data.response);

    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, the AI engine is currently unreachable. Please try again later.');
    }
}

// 4. Connect the functions to your buttons
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Stop the enter key from refreshing the page
        sendMessage();
    }
});