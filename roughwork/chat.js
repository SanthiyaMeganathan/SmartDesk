// we need to sent the data from the frontend to the backend :

// here we are writing the code in js:

//create the varible for the sentbutton , so that we can add the event listener to it:

const sendButton = document.getElementById('sendButton');
const userInput = document.getElementById('userInput');
const chatDisplay = document.getElementById('chatDisplay');

// we will create a function to send the message to the backend:

async function sendMessage(){
    const userMessage = userInput.value.trim();

    //we got the user message , now we need to check if the message is empty or not , if it is empty we will return it:

    if(userMessage==='') return;

    //if the message is not empty we will display it to the user:

    addMessageToChat('user', userMessage);

    //after displaying the user message we will clear the input field for the next message:

    userInput.value = '';

    //now we will send the user message to the server and wait for the response:

    try{
        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({message: userMessage})
        });
    }

    // if some error occurs we will catch it and display it to the user:

    catch(error){
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, something went wrong. Please try again later.');
    }

    //we need to add the different styles to the user message and bot message ,
    //  so we will create a function to add the message to the chat display:

function addMessageToChat(sender, message){
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.textContent = message;
    chatDisplay.appendChild(messageElement);
    chatDisplay.scrollTop = chatDisplay.scrollHeight; // Scroll to the bottom


}

//function to handle the click event of the send button:

function handleSendButtonClick(){
    sendMessage();
}

// we will add the event listener to the send button:

sendButton.addEventListener('click', handleSendButtonClick);
// sent button should work when the user presses the enter key as well:
userInput.addEventListener('keypress', function(event){
    if(event.key === 'Enter'){
        event.preventDefault(); // prevent the default action of the enter key
        handleSendButtonClick();
    }
