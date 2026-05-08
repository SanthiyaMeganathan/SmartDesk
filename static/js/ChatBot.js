
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatDisplay = document.getElementById('chat-box');


sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
async function sendMessage() {
    const userMessage = userInput.value.trim();
    if (userMessage === '') return;

   
    addMessageToChat('user', userMessage);
    userInput.value = '';

    try {
        const response = await fetch('/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();
        

        addMessageToChat('bot', data.response);

       
        if (data.show_form) {
            renderTicketForm(data.show_form);
        }

    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, the AI engine is currently unreachable.');
    }
}


function addMessageToChat(sender, text) {
    const messageDiv = document.createElement('div');
    
  
    messageDiv.classList.add('message', `${sender}-message`);
    messageDiv.textContent = text;
    
    chatDisplay.appendChild(messageDiv);
    

    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}


function renderTicketForm(formData) {
    const formContainer = document.createElement('div');
    formContainer.classList.add('gui-form-card');
    formContainer.id = 'active-gui-form';

    formContainer.innerHTML = `
        <input type="text" id="gui-title" value="${formData.title || ''}" placeholder="Title">
        <textarea id="gui-desc" placeholder="Description">${formData.description || ''}</textarea>
        <div class="gui-row">
            <input type="text" id="gui-priority" value="${formData.priority || ''}" placeholder="Priority">
            <input type="text" id="gui-category" value="${formData.category || ''}" placeholder="Category">
        </div>
        <button id="gui-submit-btn" onclick="submitFinalTicket()">Submit Ticket</button>
    `;
    
    chatDisplay.appendChild(formContainer);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}


async function submitFinalTicket() {
    const formCard = document.getElementById('active-gui-form');
    const ticketData = {
        title: document.getElementById('gui-title').value,
        description: document.getElementById('gui-desc').value,
        priority: document.getElementById('gui-priority').value,
        category: document.getElementById('gui-category').value
    };

    try {
        const response = await fetch('/submit-ticket-gui', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(ticketData)
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            // 1. Disable all inputs so they aren't editable anymore
            const inputs = formCard.querySelectorAll('input, textarea');
            inputs.forEach(input => input.disabled = true);

            // 2. Change the button to show success and disable it
            const submitBtn = document.getElementById('gui-submit-btn');
            submitBtn.disabled = true;
            submitBtn.innerText = "Ticket Submitted ✓";
            submitBtn.style.backgroundColor = "#6c757d"; // Grey out the button
            submitBtn.style.cursor = "not-allowed";

            // 3. Remove the ID so a NEW form can be generated later without conflict
            formCard.id = "submitted-form-archived";

            // 4. Show success message in the chat
            addMessageToChat('bot', "✅ Ticket successfully raised! You can track it on your dashboard.");
        }
    } catch (error) {
        alert("Error submitting ticket.");
    }
}