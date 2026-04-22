from flask import Flask, render_template

app = Flask(__name__)

@app.route("/admin-dashboard")
def hello_world():
    return  render_template("AdminDashBoard.html")

@app.route('/Employee-Signup')
def employee_signup():
    return render_template('Employee-Signup.html')

if __name__ == "__main__":    app.run(debug=True)