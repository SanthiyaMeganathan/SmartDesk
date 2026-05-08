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

    all_tickets = query.all()
    
    Top_five_ticket = query.top(5);
    
    #find how many tickets raised in last 7 days ..
    
    secounds_in_seven_days = 7*24*60*60;
    
    tickets_last_seven_days=query.if(time_between_craetion_and_now <=secounds_in_seven_days)
    
    open_count = Ticket.query.filter_by(status='Open').count()
    progress_count = Ticket.query.filter_by(status='In Progress').count()
    resolved_count = Ticket.query.filter_by(status='Resolved').count()
    total_count = Ticket.query.count()
    
    open_time=never change;
    if(admin converts open to progess or resolved to progress){
        get the time and upadte in the db ..proceeding staterd.
    }
    
    if(admin converts the open to resolved or progress to resolved){
        get the recent time and upadted in the db .
    }
    
    find the percentage of open:
        open percentage = open/total *100
        
    find the percentage of the progress:
        progress percentage =progress/total *100
        
    find the avg time to resolved :
        
       no_of_resolved _tickets= get the resolved tickets number.    
       addition of secounds taken to go from open to resolved for all resolved tickets= sum(rescolved_time)
       avg_time_sec= addition of secounds taken to go from open to resolved for all resolved tickets/no_of resolved tickets
       
       convert the scoundto days:
           avg_time_days=avg_time_sec/24*60*60
             

    return render_template(
        "AdminDashBoard.html", 
        open=open_count, 
        progress=progress_count, 
        resolved=resolved_count, 
        total=total_count,
        
        tickets=all_tickets
    )
    
    


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    //here we have created_at time now we  need add:
        
    proceeding_started = db.Column(db.DateTime , default =null)    
        
    resolved_at=db.Columun(db.DateTime, default=null)
    
    time_bewteen_creation_and_now =db.column(db.dateTime, default=datetime.utcnow-datetime.utcnow(create-at))in secounds
        
        
@app.route("/admin-dashboard")
def admin_dashboard():
    # ... keep your session checks and filter logic (query = Ticket.query ...) ...

    # 1. GLOBAL TOTALS
    global_total = Ticket.query.count()
    global_open = Ticket.query.filter_by(status='Open').count()
    global_progress = Ticket.query.filter_by(status='In Progress').count()
    global_resolved = Ticket.query.filter_by(status='Resolved').count()

    # 2. STATUS PERCENTAGES
    open_pct = round((global_open / global_total * 100), 1) if global_total > 0 else 0
    progress_pct = round((global_progress / global_total * 100), 1) if global_total > 0 else 0

    # 3. CATEGORY CALCULATIONS (The "Missed" part)
    # We fetch counts for specific categories defined in your sketch
    cat_counts = {
        'network': Ticket.query.filter_by(category='Network').count(),
        'software': Ticket.query.filter_by(category='Software').count(),
        'hardware': Ticket.query.filter_by(category='Hardware').count(),
        'access': Ticket.query.filter_by(category='Access').count()
    }
    
    #here we need to calculate the percentage of all things speraly
    
    network_perctengae = network/tot_ticktes *100
    software_perctengae =software/tot_ticktes*100
    hardware_perctengae = hardware/tot_ticktes*100
    access_perctengae = access/tot_ticktes*100
    

    # 4. AVG RESOLUTION TIME
    resolved_list = Ticket.query.filter(Ticket.status == 'Resolved', Ticket.resolved_at != None).all()
    if resolved_list:
        total_seconds = sum([(t.resolved_at - t.created_at).total_seconds() for t in resolved_list])
        avg_days = round(total_seconds / (len(resolved_list) * 86400), 1)
        avg_res_time = f"{avg_days} days"
    else:
        avg_res_time = "0.0 days"

    # 5. RECENT TICKETS (Top 5)
    top_five = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()

    return render_template(
        "AdminDashBoard.html",
        total=global_total,
        open=global_open,
        open_pct=open_pct,
        progress=global_progress,
        progress_pct=progress_pct,
        resolved=global_resolved,
        avg_res_time=avg_res_time,
        categories=cat_counts,  # Passing the dictionary of counts
        tickets=all_tickets,    # For the main table
        recent_tickets=top_five
    )        