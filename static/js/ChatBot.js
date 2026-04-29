
const sendButton = document.getElementById('send-btn');
const userInput = document.getElementById('user-input');
const chatDisplay = document.getElementById('chat-box');


function addMessageToChat(sender, message) {
    const messageElement = document.createElement('div');
    

    messageElement.classList.add('message', sender); 
    messageElement.textContent = message;
    
    chatDisplay.appendChild(messageElement);
    chatDisplay.scrollTop = chatDisplay.scrollHeight; 
}

async function sendMessage() {
    const userMessage = userInput.value.trim();

  
    if (userMessage === '') return;


    addMessageToChat('user', userMessage);
    userInput.value = '';

    try {

        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        });

 
        const data = await response.json();
        

        addMessageToChat('bot', data.response);

    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, the AI engine is currently unreachable. Please try again later.');
    }
}

sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});