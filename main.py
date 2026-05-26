import uuid
import requests
from datetime import datetime, date, timedelta
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
    created_at = db.Column(db.DateTime, default=datetime.now)
    proceeding_started = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    session_id = db.Column(db.String(100), nullable=True) 

class ConversationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)    


with app.app_context():
    db.create_all()
    
    if not Admin_loginDetails.query.filter_by(email='admin@smartdesk.com').first():
        admin_user = Admin_loginDetails(
            email='admin@smartdesk.com',                
            password=generate_password_hash('admin123')
        )  
        db.session.add(admin_user)
        
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

@app.route('/employee-dashboard')
def employee_dashboard():
    if 'email' not in session:
        return redirect(url_for('employee_login'))
    
    user_email = session['email']
    my_tickets = Ticket.query.filter_by(email=user_email).all()
    open_count=sum(1 for ticket in my_tickets if ticket.status== 'Open')
    in_progress_count=sum(1 for ticket in my_tickets if ticket.status== 'In Progress')
    closed_count=sum(1 for ticket in my_tickets if ticket.status == 'Resolved')
    return render_template(
        'EmployeeDashboard.html', 
        tickets=my_tickets,
        open_count=open_count,
        in_progress_count=in_progress_count,
        closed_count=closed_count
        )


@app.route('/chat-bot')
def render_chatbot():
    if 'email' not in session:
        return redirect(url_for('employee_login'))
    
    user_email = session['email']
    my_tickets = Ticket.query.filter_by(email=user_email).order_by(Ticket.created_at.desc()).all()
    today = date.today()
    yesterday = today - timedelta(days=1)
    tickets_today = []
    tickets_yesterday = []
    tickets_earlier = []

    for ticket in my_tickets:
        ticket_date = ticket.created_at.date()
        if ticket_date == today:
            tickets_today.append(ticket)
        elif ticket_date == yesterday:
            tickets_yesterday.append(ticket)
        else:
            tickets_earlier.append(ticket)
 
    return render_template(
        'ChatBot.html', 
        tickets=my_tickets,
        tickets_today=tickets_today,
        tickets_yesterday=tickets_yesterday,
        tickets_earlier=tickets_earlier
    )



@app.route('/api/new-chat', methods=['POST'])
def new_chat():
    new_session = str(uuid.uuid4())
  
    return jsonify({"session_id": new_session})


@app.route('/logout')
def logout():
    role = session.get('role')  
    session.clear()  
    if role == 'admin':
        flash("You have been logged out of the Admin portal.")
        return redirect(url_for('admin_login'))
    else:
        flash("You have been logged out of the Employee portal.")
        return redirect(url_for('employee_login'))


@app.route("/admin-dashboard")
def admin_dashboard():    
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    priority_filter = request.args.get('priority')
    
    query = Ticket.query

    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    if category_filter:
        query = query.filter(Ticket.category == category_filter)
    if priority_filter:
        query = query.filter(Ticket.priority == priority_filter)
        
    filtered_tickets = query.all()
    
    global_total = Ticket.query.count()
    global_open = Ticket.query.filter_by(status='Open').count()
    global_progress = Ticket.query.filter_by(status='In Progress').count()
    global_resolved = Ticket.query.filter_by(status='Resolved').count()

    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_raised_count = Ticket.query.filter(Ticket.created_at >= seven_days_ago).count()
  
    open_pct = round((global_open / global_total * 100), 1) if global_total > 0 else 0
    progress_pct = round((global_progress / global_total * 100), 1) if global_total > 0 else 0

    categories_to_track = [
        ('Network', 'network'),
        ('Software', 'software'),
        ('Hardware', 'hardware'),
        ('Access', 'access')
    ]
      
    cat_analytics = {}
    for display_name, key in categories_to_track:
        count = Ticket.query.filter_by(category=display_name).count()
        percentage = (count / global_total * 100) if global_total > 0 else 0
        cat_analytics[key] = {
            'count': count,
            'pct': round(percentage, 1)
        }
   
    resolved_list = Ticket.query.filter(Ticket.status == 'Resolved', Ticket.resolved_at != None).all()
    if resolved_list:
        total_seconds = sum([(t.resolved_at - t.created_at).total_seconds() for t in resolved_list])
        avg_seconds = total_seconds / len(resolved_list)
        avg_days = round(avg_seconds / 86400, 1) 
        avg_res_time = f"{avg_days} days"
    else:
        avg_res_time = "0.0 days"

    top_five = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()

    return render_template (
        "AdminDashBoard.html",
        total=global_total,
        open=global_open,
        progress=global_progress,
        resolved=global_resolved,
        open_pct=open_pct,
        progress_pct=progress_pct,
        recent_count=recent_raised_count,
        avg_res_time=avg_res_time,
        cat_stats=cat_analytics,
        tickets=filtered_tickets,  
        recent_tickets=top_five   )
    
    
@app.route("/update-ticket-status/<int:ticket_id>", methods=['POST'])
def update_ticket_status(ticket_id):
    new_status = request.form.get('new_status')
    ticket = Ticket.query.get_or_404(ticket_id)
    now = datetime.now()
    
    if new_status in ['Open', 'In Progress', 'Resolved']:
   
        if new_status == 'Open':
            ticket.proceeding_started = None
            ticket.resolved_at = None

        elif new_status == 'In Progress':
            ticket.proceeding_started = now
            ticket.resolved_at = None 

        elif new_status == 'Resolved':
            ticket.resolved_at = now
            if not ticket.proceeding_started:
                ticket.proceeding_started = now 
            
        ticket.status = new_status
        db.session.commit()
        
    # Redirect back to the All Tickets page instead of jumping to the dashboard
    return redirect(request.referrer or url_for('admin_dashboard'))
    

@app.route("/view-tickets")
def admin_summary():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

   
    open_count = Ticket.query.filter_by(status='Open').count()
    progress_count = Ticket.query.filter_by(status='In Progress').count()
    resolved_count = Ticket.query.filter_by(status='Resolved').count()
    total_count = Ticket.query.count()

    return render_template(
        "AdminDashBoard.html", 
        open=open_count, 
        progress=progress_count, 
        resolved=resolved_count, 
        total=total_count
    )
    
@app.route('/chatbot', methods=['POST'])
def chatbot_api():
    data = request.get_json()
    user_message = data.get('message')
    
    current_session_id = data.get('session_id')
    
    if not current_session_id:
        current_session_id = str(uuid.uuid4()) # Fallback safeguard

    rag_context = search_knowledge_base(user_message)
    
    system_prompt = f"""
    
    Role: You are the SMARTDESK IT Assistant. Your goal is to resolve issues using {rag_context} or gather data to trigger a ticket GUI.

Strict Formatting Rules:

Keep responses concise (max 4-5 sentences).

NO MARKDOWN: Do not use bolding, italics, or lists. Use plain text only.

Never hallucinate: If data is missing (Priority, Category, etc.), you must ask for it.

Always ask the Questions one at a time. Do not ask for multiple pieces of information in the same message. If you need to ask for multiple pieces of information, ask for them sequentially, one at a time, and wait for the user's response before asking the next question.

Phase 1: Diagnosis & Fix (STRICT SEQUENCE)

Greeting: If the user's first message is vague, ask for a clear title/summary of the issue. Do this only once.

RAG Check: Once you understand the basic issue, check {rag_context} immediately. 
- If a solution exists: Provide it and ask: "Did that resolve the issue?"
- If no solution exists: YOU MUST STOP TROUBLESHOOTING. Do not ask for more details, server names, or descriptions. You must explicitly acknowledge the missing data by saying EXACTLY: "I don't have access to the info that you are asking for in my knowledge base. So can we raise a ticket to the admin?" 
- You must wait for the user to explicitly say "yes" before moving to Phase 2.

Escalation: If a RAG solution was provided but the user says it did not resolve the issue, ask: "Would you like me to raise a ticket to the admin?"

Phase 2: Ticket Data Gathering (Only initiate if user says Yes in Phase 1)

Category: Identify if the issue is Network, Hardware, Software, or Access. Try to infer from the conversation first before asking. Maximum avoid asking and you try to find out by your own!

Description: Ask the user to describe what they are experiencing in more detail.

Priority: Explicitly ask for Low, Medium, or High.

Phase 3: GUI Trigger & User Voice

When constructing the description field for the JSON, you must write in the first-person voice of the user.

DIRECT START RULE: The description must start immediately with the problem or the action taken.

FORBIDDEN FRONTIER: Do not start the description with phrases like "I see a message saying...", "The user said...", "There is an error...", or "I am told that...".

User Voice Example: I cannot use my personal device with the office network. It used to work, but today it stopped and I cannot connect my phone to the hotspot. I need help to resolve this connection issue.

Constraint: Never use bot-speak like "The user is reporting..." in the JSON description.
    
Phase 4: Final Trigger

You must have: Title, Description, Category, and Priority.

The [RAISE_TICKET] tag and JSON must appear only once at the very end of the final confirmation.

Format: Final confirmation text. [RAISE_TICKET] {{"title": "...", "description": "...", "category": "...", "priority": "..."}}

Closures:

If the user says "Thank you," respond: "You are welcome! Have a great day!"

If the user says "Bye," end gracefully.

    
    """
    

    
    history_records = ConversationHistory.query.filter_by(session_id=current_session_id).all()
    messages = [{"role": "system", "content": system_prompt}]
    for record in history_records[-10:]:
        # Prevent appending empty user messages (used for backend GUI triggers) to the LLM prompt
        if record.user_message.strip() != "":
            messages.append({"role": "user", "content": record.user_message})
            messages.append({"role": "assistant", "content": record.bot_response})
    messages.append({"role": "user", "content": user_message})

    try:
        ollama_response = requests.post(f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": "gpt-oss:120b-cloud", "messages": messages, "stream": False})
        
        # MODIFICATION: Capture the raw response to save to the DB later
        raw_bot_response = ollama_response.json().get('message', {}).get('content', 'Error.')
    except:
        return jsonify({'response': 'AI engine unreachable.'})
    
    bot_response_text = raw_bot_response
    form_data = None
    if "[RAISE_TICKET]" in bot_response_text:
        try:
            parts = bot_response_text.split("[RAISE_TICKET]")
            bot_response_text = parts[0].strip()
            json_match = re.search(r'\{.*\}', parts[1].strip(), re.DOTALL)
            if json_match:
                form_data = json.loads(json_match.group(0))
                bot_response_text += "\n\nPlease review and edit the ticket details below before submitting."
        except Exception as e:
            print(f"Extraction Error: {e}")

    # MODIFICATION: Save the RAW response (with the JSON) to the DB so history can rebuild it
    db.session.add(ConversationHistory(session_id=current_session_id, user_message=user_message, bot_response=raw_bot_response))
    db.session.commit()
    return jsonify({'response': bot_response_text, 'show_form': form_data})


@app.route('/api/chat-history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    if 'email' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    history = ConversationHistory.query.filter_by(session_id=session_id).all()
    
    
    ticket_exists = Ticket.query.filter_by(session_id=session_id).first() is not None
    
    result = []
    for h in history:
       
        if h.user_message.strip() != "":
            result.append({"sender": "user", "text": h.user_message})
        
       
        bot_text = h.bot_response
        form_data = None
        if "[RAISE_TICKET]" in bot_text:
            try:
                parts = bot_text.split("[RAISE_TICKET]")
                bot_text = parts[0].strip()
                json_match = re.search(r'\{.*\}', parts[1].strip(), re.DOTALL)
                if json_match:
                    form_data = json.loads(json_match.group(0))
                    bot_text += "\n\nPlease review and edit the ticket details below before submitting."
            except Exception as e:
                pass
                
        result.append({
            "sender": "bot", 
            "text": bot_text, 
            "show_form": form_data, 
            "ticket_submitted": ticket_exists
        })
    
    return jsonify({"history": result})


@app.route('/submit-ticket-gui', methods=['POST'])
def submit_ticket_gui():
    if 'email' not in session:
        return jsonify({'status': 'error', 'message': 'Session expired.'}), 401
    data = request.get_json()
    try:
        new_ticket = Ticket(
            email=session.get('email'),
            title=data.get("title"),
            description=data.get("description"),
            category=data.get("category"),
            priority=data.get("priority"),
            status="Open",
           
            session_id=data.get("session_id")
        )
        db.session.add(new_ticket)
        
        
        success_msg = "Your ticket has been raised successfully. The IT team will get back to you shortly."
        
        
        history_entry = ConversationHistory(
            session_id=data.get("session_id"), 
            user_message="", 
            bot_response=success_msg
        )
        db.session.add(history_entry)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Ticket raised successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/admin-side-macron')
def adminSideMacron():
    return render_template("AdminSideMacron.html")  

@app.route('/employee-side-base')
def employeeSideBase():
    if 'email' not in session:
        return redirect(url_for('employee_login'))
    
    user_email = session['email']
    my_tickets = Ticket.query.filter_by(email=user_email).all()
    return render_template(
        'EmployeeSidease.html', 
        tickets=my_tickets,
        )
    
@app.route('/mytickeadminside')
def myticketadminside():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    # 1. Capture filter parameters from the request (defaults to 'All')
    status_filter = request.args.get('status', 'All')
    category_filter = request.args.get('category', 'All')
    priority_filter = request.args.get('priority', 'All')
    date_filter = request.args.get('date', 'All')

    # 2. Start with a base query
    query = Ticket.query

    # 3. Apply filters if a specific option is selected
    if status_filter != 'All':
        query = query.filter(Ticket.status == status_filter)
    if category_filter != 'All':
        query = query.filter(Ticket.category == category_filter)
    if priority_filter != 'All':
        query = query.filter(Ticket.priority == priority_filter)

    # 4. Apply Date filtering
    if date_filter != 'All':
        now = datetime.now()
        if date_filter == 'This week':
            start_date = now - timedelta(days=7)
            query = query.filter(Ticket.created_at >= start_date)
        elif date_filter == 'This Month':
            start_date = now - timedelta(days=30)
            query = query.filter(Ticket.created_at >= start_date)
        elif date_filter == 'Within 3 months':
            start_date = now - timedelta(days=90)
            query = query.filter(Ticket.created_at >= start_date)

    # 5. Execute query and order by latest
    filtered_tickets = query.order_by(Ticket.created_at.desc()).all()
    total_tickets = Ticket.query.count() # Keeps global count intact if needed elsewhere

    return render_template(
        'MyTicketAdminSide.html', 
        tickets=filtered_tickets,
        total=total_tickets
    )
    
@app.route('/admin-export')
def admin_export():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    # Passing total so the sidebar badge stays populated
    total_tickets = Ticket.query.count()
    
    return render_template('AdminExport.html', total=total_tickets)    

@app.route('/admin-analytics')
def admin_analytics():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))

    all_tickets = Ticket.query.all()
    total_tickets = len(all_tickets)

    # 1. Top Reporters Calculation
    reporters = {}
    for t in all_tickets:
        if t.email not in reporters:
            reporters[t.email] = {
                'email': t.email,
                'name': t.email.split('@')[0].capitalize() + " " + t.email.split('@')[0][-1].upper(),
                'initials': t.email[:2].upper(),
                'total': 0,
                'resolved': 0
            }
        reporters[t.email]['total'] += 1
        if t.status in ['Resolved', 'Closed']:
            reporters[t.email]['resolved'] += 1

    top_reporters = sorted(reporters.values(), key=lambda x: x['total'], reverse=True)[:5]
    max_tickets = top_reporters[0]['total'] if top_reporters else 1

    # 2. Avg Resolution Time Calculation
    resolved_list = [t for t in all_tickets if t.status == 'Resolved' and t.resolved_at]
    if resolved_list:
        total_seconds = sum([(t.resolved_at - t.created_at).total_seconds() for t in resolved_list])
        avg_days = round((total_seconds / len(resolved_list)) / 86400, 1)
    else:
        avg_days = 0.0

    # 3. AI Resolved Sessions Calculation
    total_chat_sessions = db.session.query(ConversationHistory.session_id).distinct().count()
    ticket_sessions = db.session.query(Ticket.session_id).filter(Ticket.session_id != None).distinct().count()
    ai_resolved_count = max(0, total_chat_sessions - ticket_sessions)
    ai_resolved_pct = round((ai_resolved_count / total_chat_sessions * 100)) if total_chat_sessions > 0 else 0

    # 4. Peak Ticket Day Calculation
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = {day: 0 for day in days}
    for t in all_tickets:
        day_name = days[t.created_at.weekday()]
        day_counts[day_name] += 1
    peak_day = max(day_counts, key=day_counts.get) if all_tickets else "N/A"
    peak_day_avg = round(day_counts[peak_day] / 4, 1)

    # 5. Category Breakdown Calculation
    categories = ['Network', 'Access', 'Software', 'Hardware']
    cat_counts = {c: 0 for c in categories}
    for t in all_tickets:
        if t.category in cat_counts:
            cat_counts[t.category] += 1

    cat_pct = {c: round((count / total_tickets * 100)) if total_tickets > 0 else 0 for c, count in cat_counts.items()}
    donut_data = [cat_counts['Network'], cat_counts['Access'], cat_counts['Software'], cat_counts['Hardware']]

    # 6. Weekly Trend Data (Last 6 Weeks)
    now = datetime.now()
    weeks_labels = []
    bar_data = []
    line_open_data = []
    line_resolved_data = []

    for i in range(5, -1, -1):
        start_date = now - timedelta(days=(i * 7) + 7)
        end_date = now - timedelta(days=i * 7)
        weeks_labels.append(end_date.strftime('%d %b'))

        week_tickets = [t for t in all_tickets if start_date <= t.created_at < end_date]
        bar_data.append(len(week_tickets))
        line_open_data.append(sum(1 for t in week_tickets if t.status == 'Open'))
        line_resolved_data.append(sum(1 for t in week_tickets if t.status == 'Resolved'))

    # Package all chart data to send to Javascript
    chart_data = {
        'labels': weeks_labels,
        'barData': bar_data,
        'donutData': donut_data,
        'lineOpen': line_open_data,
        'lineResolved': line_resolved_data,
        'catCounts': cat_counts,
        'catPct': cat_pct
    }

    return render_template(
        'AdminAnalytical.html',
        total=total_tickets,
        top_reporters=top_reporters,
        max_tickets=max_tickets,
        avg_days=avg_days,
        ai_resolved_count=ai_resolved_count,
        ai_resolved_pct=ai_resolved_pct,
        peak_day=peak_day,
        peak_day_avg=peak_day_avg,
        chart_data=chart_data
    )      
    

if __name__ == "__main__":
    app.run(debug=True)