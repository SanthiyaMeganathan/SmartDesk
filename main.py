import uuid
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import chromadb
from chromadb.utils import embedding_functions
import json
import re


app = Flask(__name__)
app.secret_key = 'my_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartdesk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

OLLAMA_BASE_URL = "http://localhost:11434"


class Employee_loginDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Admin_loginDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ConversationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)    


with app.app_context():
    db.create_all()
    
    # if admin user doesn't exist, create one
    if not Admin_loginDetails.query.filter_by(email='admin@smartdesk.com').first():
        admin_user = Admin_loginDetails(
            email='admin@smartdesk.com',                
            password=generate_password_hash('admin123')
        )  
        db.session.add(admin_user)
        
    # Employee creation
    emp_names = ['harish', 'santhiya', 'sathish', 'priya', 'karthik']
    for emp in emp_names:
        emp_email = f"{emp}@smartdesk.com"
        emp_password = f"{emp[:2]}123"
        
        if not Employee_loginDetails.query.filter_by(email=emp_email).first():
            emp_user = Employee_loginDetails(
                email=emp_email,
                password=generate_password_hash(emp_password)
            ) 
            db.session.add(emp_user)
            print(f"Added employee: {emp_email}")

    db.session.commit()
    print("Database initialized successfully.")
    

def search_knowledge_base(user_query):
    """ Search the vector database and return result as a String""" 
    try:
        client = chromadb.PersistentClient(path="./chromadb")
        ollama_ef = embedding_functions.OllamaEmbeddingFunction(
            model_name="nomic-embed-text",
            url=f"{OLLAMA_BASE_URL}/api/embeddings",
        )
        
        collection = client.get_or_create_collection(name="SmartDesk_KnowledgeBase", embedding_function=ollama_ef)
        question_embedding = ollama_ef([user_query])

        results = collection.query(
            query_embeddings=question_embedding,
            n_results=2
        )

        documents = results.get('documents', [[]])[0]
        if not documents:
            return "No specific information found in the knowledge base."
            
        return "\n".join(documents)
        
    except Exception as e:
        print(f"RAG Error: {e}")
        return "Internal Knowledge Base is currently offline."    



@app.route('/', methods=['GET', 'POST'])
@app.route('/employee-login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = Employee_loginDetails.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session.clear()
            session['chat_session_id'] = str(uuid.uuid4())
            
            session['user_id'] = user.id
            session['role'] = 'employee'
            session['email'] = user.email 
            
            return redirect(url_for('employee_dashboard'))
        else:
            flash("Invalid Employee Credentials! Please try again.")
            return render_template('EmployeeLogin.html')
            
    return render_template('EmployeeLogin.html')    


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
       
        user = Admin_loginDetails.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = 'admin'
            session['email'] = user.email 
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid Admin Credentials! Please try again.")
            return render_template('AdminLogin.html')
            
    return render_template('AdminLogin.html') 


@app.route("/admin-dashboard")
def admin_dashboard():    
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    all_tickets = Ticket.query.all()
    return render_template("AdminDashBoard.html", tickets=all_tickets)


@app.route('/employee-dashboard')
def employee_dashboard():
    if 'email' not in session:
        return redirect(url_for('employee_login'))
    
    user_email = session['email']
    my_tickets = Ticket.query.filter_by(email=user_email).all()
    return render_template('EmployeeDashboard.html', tickets=my_tickets)


@app.route('/chat-bot')
def render_chatbot():
    if 'email' not in session:
        return redirect(url_for('employee_login'))
    return render_template('ChatBot.html')

@app.route('/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    user_message = data.get('message')
    
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    current_session_id = session.get('chat_session_id')
  
    rag_context = search_knowledge_base(user_message)
    print(f"--- DEBUG RAG DATA: {rag_context} ---")
    
    
    system_prompt = f"""
    
    Strick Guidelines for the AI Assistant:
1. You are a helpful IT assistant for SMARTDESK.
2. Keep responses concise (max 4-5 sentences). No Markdown formatting like **bolding** or *italics*.
3. PRIORITY: Check {rag_context} first. If a solution exists, provide it immediately.
4. HALLUCINATION: Never assume values. If a user hasn't given the priority, do NOT guess it.

Conversation Flow & Rules:
- GREETING: If vague, ask for a title. If specific, extract the title yourself and help.
- ATTEMPT FIX: Use {rag_context}. If you provide a fix, ask "Did that resolve the issue?"
- ESCALATION INITIATION: If the fix fails or isn't in context, ask: "Would you like me to raise a ticket to the admin?"
- GATHERING DATA: Only if they say "Yes", ask for CATEGORY(Network / Hardware / Software /
Access). Once category is provided, ask for PRIORITY (Low / Medium / High). 
- FINAL TICKET TRIGGER: 
    - You MUST wait until you have the Title, Description, Category, and Priority.
    - Only after the user provides the Priority, confirm you are raising it and append the [RAISE_TICKET] tag.
    - NEVER include [RAISE_TICKET] in a message where you are still asking a question.

CRITICAL TICKET FORMAT:
- The [RAISE_TICKET] tag and JSON must only appear ONCE, at the very end of the final confirmation message.
- Example: I have all the details. I am raising the ticket now. Have a great day! [RAISE_TICKET] {{"title": "...", "description": "...", "category": "...", "priority": "..."}}

ENDINGS:
- If the user says "Thank you" or "Thanks", say "You're welcome! Have a great day!" and DO NOT raise a ticket.
- If the user says "Bye", end gracefully.
    


    """
    
   
    history_records = ConversationHistory.query.filter_by(session_id=current_session_id).all()
    messages = [{"role": "system", "content": system_prompt}]
    
    for record in history_records[-10:]: 
        messages.append({"role": "user", "content": record.user_message})
        messages.append({"role": "assistant", "content": record.bot_response})
        
    messages.append({"role": "user", "content": user_message})

   
    try:
        ollama_response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": "gpt-oss:120b-cloud",
                "messages": messages,
                "stream": False
            }
        )
        ollama_data = ollama_response.json()
        bot_response_text = ollama_data.get('message', {}).get('content', 'Sorry, I encountered an error formatting my response.')
    except Exception as e:
        print(f"Ollama Error: {e}")
        return jsonify({'response': 'Sorry, the AI engine is currently unreachable.'})
    
    if "[RAISE_TICKET]" in bot_response_text:
        try:
         
            parts = bot_response_text.split("[RAISE_TICKET]")
            friendly_bot_message = parts[0].strip()
            json_string_part = parts[1].strip()

    
            json_match = re.search(r'\{.*\}', json_string_part, re.DOTALL)
            
            if json_match:
                ticket_data = json.loads(json_match.group(0))
                
                required_fields = ["title", "description", "category", "priority"]
         
                if all(field in ticket_data for field in required_fields):
                 
                    new_ticket = Ticket(
                        email=session.get('email', 'unknown@smartdesk.com'),
                        title=ticket_data["title"],
                        description=ticket_data["description"],
                        category=ticket_data["category"],
                        priority=ticket_data["priority"],
                        status="Open"
                    )
                    db.session.add(new_ticket)
                    db.session.commit()
                    
                    
                    bot_response_text = friendly_bot_message + "\n\n(✅ Support ticket created. Track it on your dashboard.)"
                else:
           
                    bot_response_text = friendly_bot_message
            else:
                bot_response_text = friendly_bot_message

        except Exception as e:
            print(f"Ticket Logic Error: {e}")

            bot_response_text = bot_response_text.replace("[RAISE_TICKET]", "").strip()


    new_convo = ConversationHistory(
        session_id=current_session_id,
        user_message=user_message,
        bot_response=bot_response_text
    )
    db.session.add(new_convo)
    db.session.commit()
    
    return jsonify({'response': bot_response_text})

 
if __name__ == "__main__":
    app.run(debug=True)