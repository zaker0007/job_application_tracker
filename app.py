

from flask import Flask, render_template, request, flash,redirect, url_for, session
from werkzeug.security import check_password_hash,generate_password_hash
import psycopg2
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv((Path(__file__).parent / '.env'))

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv("DATABASE_URL")
conn=psycopg2.connect(DATABASE_URL,sslmode='require')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS application (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    job_role VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    applied_date DATE NOT NULL
)
""")
cursor.execute("""
    create table if not exists users(
        id serial primary key,
        username varchar(100) unique not null,
        email varchar(100) unique not null,
        password_hashed varchar(100) not null)""")


conn.commit()
cursor.close()

print("Application table created successfully!")


print("database connected successfully")
print(os.getenv("SECRET_KEY"))
print(app.config["SECRET_KEY"])


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, username, password_hashed FROM users WHERE username = %s",
            (username,)
        )

        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect('/dashboard')

        else:
            return render_template(
                'login.html',
                error="Invalid username or password!"
            )

    return render_template('login.html')


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        password_hash = generate_password_hash(password) # type: ignore
        cursor=conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, email,  password_hashed)
                VALUES (%s, %s, %s)
            """, (username, email, password_hash))

            conn.commit()

            return redirect("/login")

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return "Username ya email already registered hai!"

        finally:
            cursor.close()
    return render_template("registration.html")

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

    cursor =conn.cursor()
    cursor.execute("insert into application(company_name,job_role,status,applied_date) values (%s,%s,%s,%s)",(company,role,status,apply_date))
    conn.commit()
    cursor.close()
    flash("application added","success")
    return redirect(url_for("view"))

@app.route('/view',methods=["GET"])
def view():
   cursor = conn.cursor()
   cursor.execute("select * from application")
   applications_list = cursor.fetchall()
   cursor.close()
   return render_template("view_applications.html",applications_list=applications_list)


@app.route('/app_details/<int:id>')
def app_details(id):
    cursor = conn.cursor()
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
    cursor = conn.cursor()
    cursor.execute('update application set company_name=%s,job_role=%s,status=%s,applied_date=%s where id=%s',(company,role,status,apply_date,id))
    conn.commit()
    cursor.close()
    flash("application updated","success")
    return redirect(url_for("view"))

@app.route('/delete_application')
def delete_application():
    id = request.args.get('id')
    cursor = conn.cursor()
    cursor.execute("delete from application where id=%s",(id,))
    conn.commit()
    cursor.close()
    flash("application deleted","danger")
    return redirect(url_for("view"))

@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    # if request.method == "POST":
    #     username = request.form['username']
    #     password = request.form['password']
    #     if username == 'admin' and password == 'admin123':
    #         session["use"] = username
    #         return render_template("dashboard.html")

    #     else:
    #         return render_template("login.html")


     # cheack whether use is logged in
    if "user_id" not in session:
         return redirect("/login")
    cursor = conn.cursor()

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

@app.route('/fix-db')
def fix_db():

    cursor = conn.cursor()

    try:
        conn.rollback()  # Purani failed transaction clear

        cursor.execute("""
            ALTER TABLE users
            ALTER COLUMN password_hashed TYPE VARCHAR(255);
        """)

        conn.commit()
        return "Password hash column updated!"

    except Exception as e:
        conn.rollback()
        print(e)
        return f"Database error: {e}"

    finally:
        cursor.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
if __name__ == "__main__":
    app.run(debug=True)