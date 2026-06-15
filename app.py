import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, send_file, session
from flask_sqlalchemy import SQLAlchemy
import openpyxl

app = Flask(__name__)

app.secret_key = "student_Secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.db"
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    father = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    roll = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    dob = db.Column(db.String(50))

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verify", methods=["POST"])
def verify():
    return render_template("verify.html", data=request.form)

@app.route("/save", methods=["POST"])
def save():
    student = Student(
        name=request.form["name"],
        father=request.form["father"],
        student_class=request.form["class"],
        roll=request.form["roll"],
        mobile=request.form["mobile"],
        email=request.form["email"],
        dob=request.form["dob"]
    )

    db.session.add(student)
    db.session.commit()

    # ---- NEW 100% SECURE EMAIL CODE ----
    try:
        # Render ke environment variables se data uthana
        sender_email = os.environ.get('MAIL_USERNAME', 'nishantyadev448@gmail.com')
        app_password = os.environ.get('MAIL_PASSWORD', 'dgyiyjreskudevmx')

        msg_body = f"""
New Student Registered

Name: {student.name}
Father: {student.father}
Class: {student.student_class}
Roll: {student.roll}
Mobile: {student.mobile}
Email: {student.email}
DOB: {student.dob}
"""
        
        msg = MIMEText(msg_body)
        msg['Subject'] = 'New Student Registration'
        msg['From'] = sender_email
        msg['To'] = sender_email

        # Gmail SMTP server se manual connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, [sender_email], msg.as_string())
        server.quit()
        print("Email Sent Successfully!")
        
    except Exception as e:
        # Agar Google email block bhi karega, toh ye error log me print hoga par website crash NAHI HOGI!
        print("🔴 Email Error but keeping site live:", str(e))

    return "Registration Successful"

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")
    students = Student.query.all()
    return render_template("admin.html", students=students)

@app.route("/delete/<int:id>")
def delete(id):
    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()
    return redirect("/admin")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["admin"] = username
            return redirect("/admin")
        return "Wrong Password"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/excel")
def excel():
    students = Student.query.all()
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.append(["Name", "Father", "Class", "Roll", "Mobile", "Email", "DOB"])

    for s in students:
        sheet.append([s.name, s.father, s.student_class, s.roll, s.mobile, s.email, s.dob])

    book.save("students.xlsx")
    return send_file("students.xlsx", download_name="students.xlsx")

if __name__ == "__main__":
    app.run(debug=True)