create table Employee_loginDetails(
    id int primary key auto_increment,
    name varchar(255) not null,
    phoneNumber varchar(20) not null,
    email varchar(255) not null,
    password varchar(255) not null
    role varchar(50) not null
)

create table Admin_loginDetails(
    id int primary key auto_increment,
    name varchar(255) not null,
    email varchar(255) not null,
    password varchar(255) not null
)

@app.route('/employee/login', methods=['POST'])
def employee_login():
    data = request.get_json()
    email=data.get('email')
    password=data.get('password')
    
    #i am going to check if the email and password that we got from the user already present in the database or not:
    select query = "SELECT * FROM Employee_loginDetails WHERE email = %s AND password = %s"
    
    #if the email not found in database then we will return a message that email not found
    
    if not email_found:
        return jsonify({'message':'Email not found'}), 404
    
    #if email found but the password is incorrect then we will return a message that password is incorrect
    
    if email_found and not password_correct:
        return jsonify({'message':'Password is incorrect'}), 401
    
    #if email and password both are correct then we will return a message that login successful
    
    if email_found and password_correct:
        return jsonify({'message':'Login successful'}), 200  #here we can also return the route to the dashboard page of employee
    
 # route for the employee signup.
 
 
 @app.route('/employee/signup' , methods=['POST'])
 def employee_signup():
     
     data=request.get_json()
     name=data.get('name')
     phoneNumber =data.get('phoneNumber')
     email=data.get('email')
     password=data.get('password')
     role=data.get('role')
     
     #check whether the email already exist in the database or not
     
     select query = "SELECT * FROM Employee_loginDetails WHERE email = %s"
     
     # if email already exist in database then we will return a message that email already exist
     
     if email_found:
         return jsonify({'message':'Email already exist'}), 409
     
     if not email_found:
         
         insert_query= "INSERT INTO Employee_loginDetails (name, phoneNumber, email, password, role) VALUES (%s, %s, %s, %s, %s)"
            #here we will insert the data into the database
         return jsonify({'message':'Signup successful'}), 201  #here we can also return the route to the dashboard page of employee
     
#admin login route 

@app.route('/admin/login', methods=['POST'])
def admin_login():
    
    data=request.get_json()
    email=data.get('email')
    password=data.get('password')
    
    # we need to check if the email and password that we got from the admin must match with 
    # the email and password that we have in the database for the admin login details
    
    select query = "SELECT * FROM Admin_loginDetails WHERE email = %s AND password = %s"
    
    if not email_found:
        return jsonify({"message":"Email that you enetered does not match with our records"}), 404
    
    if email_found and not password_correct:
        return jsonify({"message":"Password that you entered does not match with our records"}), 401
    
    if email_found and password_correct:
        return jsonify({"message":"Login successful"}), 200  #here we can also return the route to the dashboard page of admin
    
    
#user dashboard route

@app.route('/employee/dashboard', methods=['GET'])
def employee_dashboard():
    # here we will return the data that we want to show on the dashboard page of employee
    return jsonify({"message":"Welcome to the employee dashboard"}) 

@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    # here we will return the data that we want to show on the dashboard page of admin
    return jsonify({"message":"Welcome to the admin dashboard"}) 


#when the user go to dashboard page , this is what user will see on dashboard page:

# user will see a tickets he raised and the status of those tickets so that we need the 
#table to store the tickets details and the status of those tickets

create table Tickets(
    id int primary key auto_increment,
    employee_id int not null,
    title varchar(255) not null,
    description text not null,
    category varchar(50) not null,
    priority varchar(50) not null,
    status varchar(50) not null,-->#by default the status of the ticket will be open when the user raise the ticket and then when the admin resolve the ticket then we will update the status of the ticket to resolved
    created_at timestamp default current_timestamp,
)

@app.route('/employee_id/dashboard',methods=['GET'])
def employee_dashboard():
    
    #here we will get all the tickets of the particular employess and show that in the dashboard page of employee
    
    select query = "SELECT * FROM Tickets WHERE employee_id = %s"
    
    #here we will return the data that we want to show on the dashboard page of employee
    return jsonify({"message":"Welcome to the employee dashboard", "tickets":tickets_data})

# we have the RaiseTicket button in the top right corner of the
#user dashboad page when the user clicks it ,it will shows two things:
#1.Did you Tired to resolve the issue by yourself? Yes/No
#if no then it route to chatbot page where ai answers to the user query from the rag model
#if yes then it route to the ticket raising form page
#once form submitted then it will insert the data into the database and show the ticket details in the dashboard page of employee 


/* this is when the tried to resolve is true/yes*/  

@app.route('/employee_id/dashboard/raise_ticket/ticket_id/<int:ticket_id>/tried_to_resolve-<bool:tried_to_resolve>', methods=['POST'])

def raise_ticket():
    
    data.get_json()
    title=data.get('title')
    description=data.get('description')
    category=data.get('category')
    priority=data.get('priority')
    
    #click the submit button then we will insert the data into the database and show the ticket details in the dashboard page of employee4
    
    insert_query = "INSERT INTO Tickets (employee_id, title, description, category, priority, status) VALUES (%s, %s, %s, %s, %s, %s)"
    #here we will insert the data into the database and then we will return the data that we want to show on the dashboard page of employee
    return jsonify({"message":"Ticket raised successfully", "ticket_details":ticket_details}), 201  #here we can also return the dashboard page of employee with the updated ticket details


/* this is when the tries to resolve is No/false*/
#open the chatbot page  where ai ans the user query from the rag model and then if the user still want to raise the ticket then we will route
# to the ticket raising form page and then once form submitted then it will insert the data into the database
# and show the ticket details in the dashboard page of employee


@app.route('/employee_id/dashboard/raise_ticket/ticket_id/<int:ticket_id>/tried_to_resolve-<bool:tried_to_resolve>', methods=['POST']) #Tried to resolve is false.

def chatbot():
    
    #here we need to implement the rag model and then we will pass the user query to the rag model and get the response from the rag model and then we will return that response to the user in the chatbot page
    
    data=request.get_json()
    user_query=data.get('user_query')
    #here we will pass the user query to the rag model and get the response from the rag model
    
    return jsonify({"message":"This is the response from the chatbot", "chatbot_response":chatbot_response})
#here we can also return the route to the ticket raising form page
# if the user still want to raise the ticket after getting the response from the chatbot.

   if chatbot_response is not helpful for the user:
         return jsonify({"message":"If you still want to raise the ticket please click the link below", "link_to_ticket_form":"/employee_id/dashboard/raise_ticket/ticket_id/<int:ticket_id>/tried_to_resolve-true"})
     
#there will be the text in the chatbot page that say "if your issue is not resolved by the chatbot then you can raise the ticket by clicking the Raise ticket button."


@app.route('/admin/dashboard', methods=['GET'])
def admin_dashboard():
    
    #all the tickets that are raised by employee will be shown in the dashboard page of admin and 

    select query = "SELECT * FROM Tickets"
    
    #here we will return the data that we want to show on the dashboard page of the admin
    
    return jsonify({"message":"Welcome to the admin dashboard", "tickets":tickets_data})

#viewing the one ticket in detailed manner 

@app.route('/admin/dashboard/ticket_id/<int:ticket_id>', methods=['GET'])
def view_ticket_details(ticket_id):
    # we will select all the details of the particular ticket that we can show in the detailed page of that ticket
    
    
    select query = "SELECT * FROM Tickets WHERE id = %s"
    
    #here we will return the data that we want to show on the detailed page of that ticket
    return jsonify({"message":"This is the detailed page of the ticket", "ticket_details":ticket_details})

#admin should be able to update the status of the ticket to progress or resolved based on the action taken 
#by default that status of the ticket will be open when the user raise the ticket

@app.route('/admin/dashboard/ticket_id/<int:ticket_id>/update_status', methods=['PUT'])

def update_ticket_status(ticket_id):
    
    data=request.get_json()
    new_status=data.get('new_status') #the new status that admin want to update the ticket to that we will get from the request body
    
    #we will update the status of the ticket in the database based on the ticket id and then we will return the updated ticket details that we want to show on the detailed page of that ticket
    update query = "UPDATE Tickets SET status = %s WHERE id = %s"
    #here we will update the status of the ticket in the database and then we will return the data that we want to show on the detailed page of that ticket
    return jsonify({"message":"Ticket status updated successfully", "updated_ticket_details":updated_ticket_details}) # here we can also return the route to the admin dashboard page with the updated ticket details

#admin should be able to filter the tickets based on the status as well as priority:

@app.route('/admin/dashboard/filter_tickets', methods=['GET'])

def filter_tickets():
    
    status=request.args.get('status') #the status that admin want to filter the tickets based on that we will get from the query parameters
    priority=request.args.get('priority') #the priority that admin want to filter the tickets based on that we will get from the query parameters
    
    #we will filter the tickets in the database based on the status and priority and then we will return the filtered tickets details that we want to show on the dashboard page of admin
    select query = "SELECT * FROM Tickets WHERE status = %s AND priority = %s"
    
    #here we will return the data that we want to show on the dashboard page of admin with the filtered tickets details
    return jsonify({"message":"This is the filtered tickets based on your criteria", "filtered_tickets":filtered_tickets})











    
    



    
    
    