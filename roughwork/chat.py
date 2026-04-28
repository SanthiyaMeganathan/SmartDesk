

def chatbot():
    
    # we  got the data from the frontend and we are sending to llm and it will generate the response:
    
    
    data = request.get_json() --> here we get the data from the frontend and we will pass to the llm to generate the response
    user_message = data.get('message')
    
    #since the chatbot may need the previous messages to generate the response , so what we do is we create the 
    #table for the convo history , that will have the message of the particular session
    #when comes out of the session then we will delete the convo history of that session
    
    
    #model for convo history:
    
    class ConversationHistory(db.Model):
        id=db.Column(db.Integer,primary_key=True)
        session_id=db.Column(db.String(100),nullable=False)
        user_message=db.Column(db.Text,nullable=False)
        bot_response=db.column(db.Text,nullable=False)
        
    #now we have the model in which we have the convo history ,
    # from this table , we will get the user_msg and bot_response , if the message exist and pass to the llm to generate the response
    
    
    session_id=session.get('session_id') # we will get the session id from the session variable
    
    #get the convo history of that session id
    user_msg=ConversationHistory.query.filter_by(session_id=session_id).user_message.all()
    bot_response=ConversationHistory.query.filter_by(session_id=session_id).bot_response.all()
    
    #now we have the user_msg and bot_response of that session id , we will pass to the llm to generate the response
    
    implement the logic to pass the user_msg and bot_response to the llm and get the response from the llm
    
    #after getting the response from the llm , we will save the user_msg and bot_response in the convo history table
    
    new_convo=ConversationHistory(session_id=session_id,user_message=user_message,bot_response=bot_response)
    db.session.add(new_convo)
    db.session.commit()
    
    #now we need to return the response that we got from the llm to the frontend:
    
    return  jsonify({'response':bot_response})

    
    
    
    
    System prompt ="
    
    1. You are a helpful assistant for the employees of SmartDesk, a company that provides smart office solutions.
    2. You can assist employees with various tasks such as:
    ->This smartdesk application helps the employee to resolve the issuse 
    related :
    software issues, hardware issues, network issues, access issues.
    
    3.if the employee has any issue realed to the above mentioned issue you just go and get the answer from the rag.
    4. If the employee has any other issue that is not related to the above mentioned issue, you can provide general assistance and guidance.
    
    5. if you are not able to resolve the issuse using the rag , then suggest the employee to raise the ticket to admin
    if the employee says okay ,then you can raise the ticket to the admin and inform the employee that the ticket has been raised and the admin will get back to them soon.
    
    
    flow:
    
    1.Bot: Hello! I'm your SmartDesk assistant. How can I help you today?
    2.Employee: Hi! I'm having trouble with my computer. It's running very slow.
    3.Bot:Could you please brefily describe the issue you are facing with your computer?
    4.Employee: Yes, my computer is running very slow and it's taking a long time to open applications.
    5.bot : is the issue related to software, hardware, network or access?
    6.Employee: I think it's a software issue.
    //here the bot will go and get the answer from the rag and provide the solution to the employee
    7.bot: Based on the information you provided, it seems like there might be some software issues causing your computer to run slow. Here are a few steps you can try to resolve the issue:
    
    if the employee says it worked :
    8.Employee: I have tried all the steps , its worked thank you!
    10.Bot : You're welcome! I'm glad I could help. If you have any other issues or questions, feel free to ask. Have a great day!
    
    if the employee says it didn't work:
    8.Employee: I have tried all the steps , but it's still running slow.,still i hve the same issue.
    9.Bot : I'm sorry to hear that the issue is still persisting. It seems like the steps I provided did not resolve the issue. In this case, I would recommend raising a ticket to the admin so that they can further investigate and assist you with the issue. Would you like me to raise a ticket for you?
    10.Employee: Yes, please raise a ticket for me.
    11.Bot: I have raised a ticket for you. The admin will get back to you soon. In the meantime, if you have any other questions or need further assistance, feel free to ask. I'm here to help!
    
    "
    
    
         
    

    //rag , function call:{
        "type":"function",
        "function": {
            "name": "search_knowledge_base",
            "description": "search the knowledge base for the issues related to software, hardware, network and access and return the result as a json string",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_query": {"type": "string", "description": "The patient's question."}
                },
                "required": ["user_query"]
            }
        }
        
    }
    
    def search_knowledge_base(user_query):
    """ Search the vector database and return result as a Json String""" 
    try:
        client = chromadb.PersistentClient(path="./chromadb")

        ollama_ef = embedding_functions.OllamaEmbeddingFunction(
            model_name="nomic-embed-text",
            url=f"{OLLAMA_BASE_URL}/api/embeddings",
        )
        
        collection = client.get_collection(
            name="SmartDesk_KnowledgeBase",
        )
        question_embedding = ollama_ef(user_query)

        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=2
        )

        documents = results.get('documents', [[]])[0]

        if not documents:
            return json.dumps({
                "status": "no_results",
                "message": "No specific information found in the knowledge base.",
                "context": ""
            })
            
        return json.dumps({
            "status": "success",
            "query": user_query,
            "context": "\n".join(documents)
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
        
#consider that user was not able to resoleve the qiery using the rag and the bot suggested to raise a ticket to the admin
"""
when raising the ticket we need to sent the some of the details to the admin
so that from the conversation itself we need to store that in the db .

lets create the db model for the ticket:

the contents of the db model will be taken from the conversation history of that session id and we will store in the ticket table and we will also store the status of the ticket whether it is open or closed and we will also store the response of the admin to that ticket and we will also store the timestamp of when the ticket was raised and when the ticket was closed.
"""

class Ticket(db.Model):
    ticket_id=db.Column(db.Integer,primary_key=True)
    employee_email=db.Column(db.String(100),nullable=False)
    title=db.Column(db.String(200),nullable=False)
    description=db.Column(db.Text,nullable=False)
    category=db.Column(db.String(50),nullable=False)
    priority=db.Column(db.String(20),nullable=False)
    status=db.Column(db.String(20),nullable=False,default='open')
    

# we should store the employee name and email in db , we will get it using the session id:
employee_email=session.get('email')
employee_name=session.get('name')


we should sent the details from here to the admin and employee dashboard:
