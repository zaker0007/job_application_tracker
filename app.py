

from flask import Flask, render_template, request, flash,redirect, url_for, session
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv((Path(__file__).parent / '.env'))

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

app.config["MYSQL_HOST"] = os.getenv('DB_HOST')
app.config["MYSQL_USER"] = os.getenv('DB_USER')
app.config["MYSQL_PASSWORD"] = os.getenv('DB_PASSWORD')
app.config["MYSQL_DB"] = os.getenv('DB_DATABASE')
app.config["MYSQL_PORT"] = int(os.getenv('DB_PORT'))



mysql = MySQL(app)

print("database connected successfully")
print(os.getenv("SECRET_KEY"))
print(app.config["SECRET_KEY"])


@app.route('/')
def home():
    return render_template("home.html")
@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/add')
def add():
    return render_template("add_application.html")

@app.route('/save', methods=['POST'])
def save():
    company = request.form['company']
    role = request.form['role']
    apply_date = request.form['applied_date']
    status = request.form['status']

    cursor = mysql.connection.cursor()
    cursor.execute("insert into application(company_name,job_role,status,applied_date) values (%s,%s,%s,%s)",(company,role,status,apply_date))
    mysql.connection.commit()
    cursor.close()
    return "<h1>successfully added</h1>"

@app.route('/view')
def view():
   cursor = mysql.connection.cursor()
   cursor.execute("select * from application")
   applications_list = cursor.fetchall()
   return render_template("view_applications.html",applications_list=applications_list)

@app.route('/app_details/<int:id>')
def app_details(id):
    cursor = mysql.connection.cursor()
    cursor.execute("select * from application where id=%s",(id,))
    app_list = cursor.fetchall()
    print(app_list)
    return render_template("application_details.html",app_list=app_list)

@app.route('/update_application',methods=['POST'])
def update_application():
    id = request.form['id']
    company = request.form['company_name']
    role = request.form['job_role']
    apply_date = request.form['applied_date']
    status = request.form['status']
    cursor = mysql.connection.cursor()
    cursor.execute('update application set company_name=%s,job_role=%s,status=%s,applied_date=%s where id=%s',(company,role,status,apply_date,id))
    mysql.connection.commit()
    cursor.close()
    return "<h1>successfully updated</h1>"

@app.route('/delete_application')
def delete_application():
    id = request.args.get('id')
    cursor = mysql.connection.cursor()
    cursor.execute("delete from application where id=%s",(id,))
    mysql.connection.commit()
    cursor.close()
    return "<h1>successfully deleted</h1>"

@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session["use"] = username
            return render_template("dashboard.html")

        else:
            return render_template("login.html")


    cursor = mysql.connection.cursor()

    cursor.execute("select count(*) from application")
    total = cursor.fetchone()[0]

    cursor.execute("select count(*) from application where status='Applied'")
    applied = cursor.fetchone()[0]

    cursor.execute("select count(*) from application where status='Interview'")
    interview = cursor.fetchone()[0]

    cursor.execute("select count(*) from application where status='Selected'")
    selected = cursor.fetchone()[0]

    cursor.execute("select count(*) from application where status='Rejected'")
    rejected = cursor.fetchone()[0]

    print(total,applied,interview,selected,rejected)
    return render_template("dashboard.html",t=total,a=applied,i=interview,s=selected,r=rejected)



@app.route('/logout')
def logout():
    session.pop("use")
    return redirect(url_for('/login'))

app.run(debug=True)