import uuid
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import chromadb
from chromadb.utils import embedding_functions

app = Flask(__name__)
app.secret_key = 'my_secret_key'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartdesk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

OLLAMA_BASE_URL = "http://localhost:11434"

#emp model

class Employee_loginDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    
 

#admin model    
    
class Admin_loginDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    

#Ticket model to Raise ticket.    
    
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

#coversation history model to store the conversation history of the user and bot in the db    

class ConversationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)    
    


with app.app_context():
    db.create_all()
    
    #if admin user doesn't exist, create one
    if not Admin_loginDetails.query.filter_by(email='admin@smartdesk.com').first():
        admin_user = Admin_loginDetails(
            email='admin@smartdesk.com',                
            password=generate_password_hash('admin123')
        )  
        db.session.add(admin_user)
        
    # Employee creation
    emp_names = ['harish', 'santhiya', 'sathish', 'priya', 'karthik']
    for emp in emp_names:
        # We use 'emp' here because that is the variable in your loop!
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
    



@app.route('/', methods=['GET', 'POST'])
@app.route('/employee-login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = Employee_loginDetails.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
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
        
        # If the user exists, check the password
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = 'admin'
            session['email'] = user.email # Good practice to save this here too
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid Admin Credentials! Please try again.")
            return render_template('AdminLogin.html')
            
    return render_template('AdminLogin.html') 


@app.route("/admin-dashboard")
def admin_dashboard():    
    return render_template("AdminDashBoard.html")


@app.route('/employee-dashboard')
def employee_dashboard():
    return render_template('EmployeeDashboard.html')


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
    
    # Get RAG Context
    rag_context = search_knowledge_base(user_message)
    
    # Construct System Prompt
    system_prompt = f"""
    You are a helpful IT assistant for the employees of SmartDesk.
    Use the following Knowledge Base context to solve the issue: {rag_context}
    
    If you are not able to resolve the issue using the context, politely suggest raising a ticket to the admin. 
    If the employee explicitly agrees to raise a ticket, you MUST include the exact tag "[RAISE_TICKET]" in your response, followed by a brief summary.
    """
    
    # Load History
    history_records = ConversationHistory.query.filter_by(session_id=current_session_id).all()
    messages = [{"role": "system", "content": system_prompt}]
    
    for record in history_records[-5:]: 
        messages.append({"role": "user", "content": record.user_message})
        messages.append({"role": "assistant", "content": record.bot_response})
        
    messages.append({"role": "user", "content": user_message})

    # Call Ollama
    try:
        ollama_response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": "gpt-oss:120b-cloud ", 
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
        bot_response_text = bot_response_text.replace("[RAISE_TICKET]", "").strip()
        
        new_ticket = Ticket(
            email=session.get('email', 'unknown@smartdesk.com'),
            title="AI Escalated Ticket",
            description=f"Automated ticket raised from chat. Last user message: {user_message}",
            category="General", 
            priority="Medium",
            status="Open"
        )
        db.session.add(new_ticket)
        db.session.commit()
        
        bot_response_text += "\n\n(A support ticket has been automatically created for you. You can track it on your dashboard.)"


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