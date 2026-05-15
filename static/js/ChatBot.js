const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatDisplay = document.getElementById('chat-box');


userInput.addEventListener('input', function() {
    this.style.height = 'auto'; 
    this.style.height = (this.scrollHeight) + 'px'; 
    
   
    if(this.scrollHeight > 150) {
        this.style.overflowY = 'auto';
    } else {
        this.style.overflowY = 'hidden';
    }
});

sendBtn.addEventListener('click', sendMessage);


userInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); 
        sendMessage();
    }
});

async function sendMessage() {
    const userMessage = userInput.value.trim();
    if (userMessage === '') return;

    addMessageToChat('user', userMessage);
    

    userInput.value = '';
    userInput.style.height = 'auto'; 

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
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const messageWrapper = document.createElement('div');
    messageWrapper.classList.add('message-wrapper', `${sender}-wrapper`);

    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message-container');

    if (sender === 'bot') {
        const icon = document.createElement('div');
        icon.classList.add('message-icon');
        icon.innerHTML = '<i class="ri-robot-line"></i>';
        messageWrapper.appendChild(icon);
    }

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', `${sender}-message`);
    messageDiv.textContent = text;

    const timeSpan = document.createElement('span');
    timeSpan.classList.add('message-time');
    timeSpan.textContent = timeString;

    messageContainer.appendChild(messageDiv);
    messageContainer.appendChild(timeSpan);
    
    messageWrapper.appendChild(messageContainer);
    
    chatDisplay.appendChild(messageWrapper);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}


function renderTicketForm(formData) {
    const formContainer = document.createElement('div');
    formContainer.classList.add('gui-form-card');
    formContainer.id = 'active-gui-form';

    formContainer.innerHTML = `
        <div class="gui-header">
            <div class="gui-header-left">
                <i class="ri-coupon-2-line"></i> Draft Ticket
            </div>
            <div class="ai-badge">AI generated</div>
        </div>
        <div class="gui-body">
            <div class="gui-field">
                <label>Title</label>
                <input type="text" id="gui-title" value="${formData.title || ''}">
            </div>
            <div class="gui-field">
                <label>Description</label>
                <textarea id="gui-desc">${formData.description || ''}</textarea>
            </div>
            <div class="gui-row">
                <div class="gui-field">
                    <label>Category</label>
                    <select id="gui-category">
                        <option value="Network" ${formData.category === 'Network' ? 'selected' : ''}>Network</option>
                        <option value="Hardware" ${formData.category === 'Hardware' ? 'selected' : ''}>Hardware</option>
                        <option value="Software" ${formData.category === 'Software' ? 'selected' : ''}>Software</option>
                        <option value="Access" ${formData.category === 'Access' ? 'selected' : ''}>Access</option>
                    </select>
                </div>
                <div class="gui-field">
                    <label>Priority</label>
                    <select id="gui-priority">
                        <option value="Low" ${formData.priority === 'Low' ? 'selected' : ''}>Low</option>
                        <option value="Medium" ${formData.priority === 'Medium' ? 'selected' : ''}>Medium</option>
                        <option value="High" ${formData.priority === 'High' ? 'selected' : ''}>High</option>
                    </select>
                </div>
            </div>
            <div class="gui-actions">
                <button id="gui-submit-btn" class="btn-submit" onclick="submitFinalTicket()">
                    <i class="ri-send-plane-fill"></i> Submit ticket
                </button>
                <button class="btn-discard" onclick="discardForm(this)">Discard</button>
            </div>
        </div>
    `;
    
    chatDisplay.appendChild(formContainer);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
}


function discardForm(buttonElement) {
    const form = buttonElement.closest('.gui-form-card');
    form.remove();
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
            const inputs = formCard.querySelectorAll('input, textarea, select');
            inputs.forEach(input => input.disabled = true);

            const submitBtn = document.getElementById('gui-submit-btn');
            submitBtn.disabled = true;
            submitBtn.innerHTML = "Ticket Submitted ✓";
            submitBtn.style.backgroundColor = "#e5e7eb"; 
            submitBtn.style.color = "#374151";
            submitBtn.style.cursor = "not-allowed";

            const discardBtn = formCard.querySelector('.btn-discard');
            if(discardBtn) discardBtn.remove();

            formCard.id = "submitted-form-archived";

            addMessageToChat('bot', "Your ticket has been raised successfully. The IT team will get back to you shortly.");
        }
    } catch (error) {
        alert("Error submitting ticket.");
    }
}