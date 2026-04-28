from flask import Flask, render_template, request, redirect, url_for, session , flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# db config:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartdesk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



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
    
    
    return render_template('AdminLogin.html')

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("AdminDashBoard.html")

@app.route('/employee-dashboard')
def employee_dashboard():
    return render_template('EmployeeDashboard.html')

@app.route('/chat-bot')
def raise_ticket():
    return render_template('ChatBot.html')

if __name__ == "__main__":
    app.run(debug=True)