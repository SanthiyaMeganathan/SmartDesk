
@app.route('/',methods=['GET', 'POST'])
@app.route('/employee-login',methods=['GET', 'POST'])
def employee_login():
    
    if request.method =='POST':
        email=request.form['email']
        password=request.form['password']
        
        #we got the email and password from the form and we will check if the name exist in the db
        
        user = Employee_loginDetails.query.filter_by(email=email).first()
        
        #if the user exist then we will check the password
        
        if user and check_password_hash(user.password, password):
            session['user_id']=user.id
            session['role']='employee'
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
        
        # Check if the admin user exists in the database
        user = Admin_loginDetails.query.filter_by(email=email).first()
        
        # If the user exists, check the password
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            
            flash("Invalid Admin Credentials! Please try again.")
            return render_template('AdminLogin.html')
        

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("AdminDashBoard.html")

@app.route('/employee-dashboard')
def employee_dashboard():
    return render_template('EmployeeDashboard.html')


this is my current code for employee login and employee dashboard and admin login and admin dashboard

#implementing the rag:def search_knowledge_base(user_query):
    """ Search the vector database and return result as a String""" 
    try:
        client = chromadb.PersistentClient(path="./chromadb")
        ollama_ef = embedding_functions.OllamaEmbeddingFunction(
            model_name="nomic-embed-text",
            url=f"{OLLAMA_BASE_URL}/api/embeddings",
        )
        
        collection = client.get_collection(name="SmartDesk_KnowledgeBase")
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