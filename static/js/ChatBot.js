const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatDisplay = document.getElementById('chat-box');


let activeSessionId = null;


document.addEventListener('DOMContentLoaded', async () => {
    await createNewSession();
});

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


async function createNewSession() {
    chatDisplay.innerHTML = ''; 
    
    try {
        const response = await fetch('/api/new-chat', { method: 'POST' });
        const data = await response.json();
        
        activeSessionId = data.session_id; 
        
        const sessionInfoText = document.querySelector('.chat-session-info span');
        if (sessionInfoText) {
            sessionInfoText.textContent = `Session Active · New Chat`;
        }
    } catch (e) {
        console.error("Error creating new chat: ", e);
    }
}


document.getElementById('new-chat-btn').addEventListener('click', createNewSession);

document.querySelectorAll('.history-item').forEach(item => {
    item.addEventListener('click', async function() {
        const sessionId = this.getAttribute('data-session-id');
        
        if (!sessionId || sessionId === "None") {
            alert("No chat history was saved for this older ticket.");
            return;
        }

       
        activeSessionId = sessionId;

        try {
            const response = await fetch(`/api/chat-history/${activeSessionId}`);
            const data = await response.json();

            chatDisplay.innerHTML = '';

    
            data.history.forEach(msg => {

                if (msg.sender === 'user' && msg.text === "") return;
                
                addMessageToChat(msg.sender, msg.text);
                
            
                if (msg.sender === 'bot' && msg.show_form) {
                    renderTicketForm(msg.show_form, msg.ticket_submitted);
                }
            });
            
            const sessionInfoText = document.querySelector('.chat-session-info span');
            if (sessionInfoText) {
               
                sessionInfoText.textContent = `Archived Chat · History Loaded`;
            }
        } catch(e) {
            console.error("Error fetching history: ", e);
        }
    });
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
           
            body: JSON.stringify({ message: userMessage, session_id: activeSessionId })
        });

        const data = await response.json();
        
        addMessageToChat('bot', data.response);

        if (data.show_form) {
          
            renderTicketForm(data.show_form, false);
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



function renderTicketForm(formData, isSubmitted = false) {
    const formContainer = document.createElement('div');
    formContainer.classList.add('gui-form-card');
    
    formContainer.id = isSubmitted ? 'submitted-form-archived' : 'active-gui-form';

    const disabledAttr = isSubmitted ? 'disabled' : '';

    let buttonsHtml = '';
    if (isSubmitted) {
        buttonsHtml = `
            <button class="btn-submit" disabled style="background-color: #e5e7eb; color: #374151; cursor: not-allowed;">
                Ticket Submitted ✓
            </button>
        `;
    } else {
        buttonsHtml = `
            <button id="gui-submit-btn" class="btn-submit" onclick="submitFinalTicket()">
                <i class="ri-send-plane-fill"></i> Submit ticket
            </button>
            <button class="btn-discard" onclick="discardForm(this)">Discard</button>
        `;
    }

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
                <input type="text" id="gui-title" value="${formData.title || ''}" ${disabledAttr}>
            </div>
            <div class="gui-field">
                <label>Description</label>
                <textarea id="gui-desc" ${disabledAttr}>${formData.description || ''}</textarea>
            </div>
            <div class="gui-row">
                <div class="gui-field">
                    <label>Category</label>
                    <select id="gui-category" ${disabledAttr}>
                        <option value="Network" ${formData.category === 'Network' ? 'selected' : ''}>Network</option>
                        <option value="Hardware" ${formData.category === 'Hardware' ? 'selected' : ''}>Hardware</option>
                        <option value="Software" ${formData.category === 'Software' ? 'selected' : ''}>Software</option>
                        <option value="Access" ${formData.category === 'Access' ? 'selected' : ''}>Access</option>
                    </select>
                </div>
                <div class="gui-field">
                    <label>Priority</label>
                    <select id="gui-priority" ${disabledAttr}>
                        <option value="Low" ${formData.priority === 'Low' ? 'selected' : ''}>Low</option>
                        <option value="Medium" ${formData.priority === 'Medium' ? 'selected' : ''}>Medium</option>
                        <option value="High" ${formData.priority === 'High' ? 'selected' : ''}>High</option>
                    </select>
                </div>
            </div>
            <div class="gui-actions">
                ${buttonsHtml}
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
        category: document.getElementById('gui-category').value,
        // MODIFICATION: Pass the active ID along with the ticket payload
        session_id: activeSessionId 
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