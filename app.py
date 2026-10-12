from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, random
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "interview_prep.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-for-production")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, password TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS attempts(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            category TEXT NOT NULL, score INTEGER NOT NULL, total INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id))""")

QUESTIONS = [
 {"category":"Python","q":"Which keyword defines a function in Python?","options":["func","define","def","function"],"answer":"def","explanation":"Python functions are declared with the def keyword."},
 {"category":"Python","q":"Which data type stores key-value pairs?","options":["list","tuple","dictionary","set"],"answer":"dictionary","explanation":"A dictionary stores key-value pairs."},
 {"category":"Java","q":"Which method is the entry point of a standard Java application?","options":["start()","main()","run()","init()"],"answer":"main()","explanation":"Execution starts from public static void main(String[] args)."},
 {"category":"Java","q":"Which keyword is used to inherit a class in Java?","options":["implements","extends","inherits","super"],"answer":"extends","explanation":"A Java class uses extends to inherit another class."},
 {"category":"DBMS","q":"What does SQL stand for?","options":["Structured Query Language","Simple Question Language","System Query Logic","Structured Queue List"],"answer":"Structured Query Language","explanation":"SQL means Structured Query Language."},
 {"category":"DBMS","q":"Which key uniquely identifies each row in a table?","options":["Foreign key","Primary key","Candidate value","Duplicate key"],"answer":"Primary key","explanation":"A primary key uniquely identifies a table row."},
 {"category":"OOP","q":"Which OOP concept bundles data and methods together?","options":["Inheritance","Polymorphism","Encapsulation","Abstraction"],"answer":"Encapsulation","explanation":"Encapsulation groups data and the methods that operate on it."},
 {"category":"OOP","q":"The ability of one interface to have multiple forms is called:","options":["Inheritance","Polymorphism","Compilation","Iteration"],"answer":"Polymorphism","explanation":"Polymorphism allows the same interface to behave in different ways."},
 {"category":"HR","q":"What is a strong way to answer 'Tell me about yourself'?","options":["Read your entire CV","Give a concise, role-relevant summary","Talk only about hobbies","Say you have no weaknesses"],"answer":"Give a concise, role-relevant summary","explanation":"Connect your education, relevant skills, project experience, and goal to the role."},
 {"category":"HR","q":"In the STAR interview method, what does S stand for?","options":["Solution","Situation","Strength","Summary"],"answer":"Situation","explanation":"STAR stands for Situation, Task, Action, Result."},
 {"category":"Aptitude","q":"A product costs ₹800 after a 20% discount. What was its original price?","options":["₹900","₹960","₹1000","₹1200"],"answer":"₹1000","explanation":"₹800 is 80% of the original price, so 800 ÷ 0.8 = ₹1000."},
 {"category":"Aptitude","q":"What is 15% of 200?","options":["15","20","30","35"],"answer":"30","explanation":"0.15 × 200 = 30."}
]
HR_QUESTIONS = [
 ("Tell me about yourself.","Structure your answer: current education, strongest relevant skills, one project or achievement, and the role you want. Aim for 60–90 seconds."),
 ("What are your strengths?","Choose two job-relevant strengths and support each with a brief example."),
 ("Describe a challenge you faced in a project.","Use STAR: Situation, Task, Action, Result. Explain your own contribution clearly."),
 ("Why should we hire you?","Connect your skills and willingness to learn to the employer's needs; include a specific example."),
 ("Where do you see yourself in five years?","Describe realistic growth in skills and responsibility while showing interest in the field.")
]
TIPS = [
 ("Before the interview","Read the job description, research the company, revise core concepts, and prepare 2–3 project examples."),
 ("During the interview","Listen carefully, clarify questions when needed, think aloud for technical problems, and be honest if you do not know."),
 ("After the interview","Thank the interviewer, reflect on questions that were difficult, and revise those topics.")
]

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if not name or not email or len(password) < 6:
            flash("Enter your name, a valid email, and a password with at least 6 characters.", "danger")
            return render_template("register.html")
        try:
            with db() as con:
                con.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                            (name,email,generate_password_hash(password)))
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("An account with this email already exists.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"], session["name"] = user["id"], user["name"]
            return redirect(url_for("dashboard"))
        flash("Email or password is incorrect.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    with db() as con:
        attempts = con.execute("SELECT * FROM attempts WHERE user_id=? ORDER BY id DESC LIMIT 5",
                               (session["user_id"],)).fetchall()
        stats = con.execute("SELECT COUNT(*) count, COALESCE(AVG(100.0*score/total),0) avg FROM attempts WHERE user_id=?",
                            (session["user_id"],)).fetchone()
    return render_template("dashboard.html", attempts=attempts, stats=stats)

@app.route("/practice")
@login_required
def practice():
    categories = sorted(set(q["category"] for q in QUESTIONS))
    selected = request.args.get("category", "All")
    qs = [q for q in QUESTIONS if selected == "All" or q["category"] == selected]
    qs = qs[:]
    return render_template("practice.html", questions=qs, categories=categories, selected=selected)

@app.route("/submit-quiz", methods=["POST"])
@login_required
def submit_quiz():
    category = request.form.get("category", "All")
    qs = [q for q in QUESTIONS if category == "All" or q["category"] == category]
    score = 0
    for i, q in enumerate(qs):
        if request.form.get(f"q{i}") == q["answer"]:
            score += 1
    with db() as con:
        con.execute("INSERT INTO attempts(user_id,category,score,total) VALUES(?,?,?,?)",
                    (session["user_id"], category, score, len(qs)))
    return render_template("quiz_result.html", score=score, total=len(qs), category=category, questions=qs,
                           answers=[request.form.get(f"q{i}") for i in range(len(qs))])

@app.route("/hr-questions")
@login_required
def hr_questions():
    return render_template("hr_questions.html", questions=HR_QUESTIONS)

@app.route("/resume")
@login_required
def resume():
    return render_template("resume.html")

@app.route("/tips")
@login_required
def tips():
    return render_template("tips.html", tips=TIPS)

@app.route("/health")
def health():
    return jsonify(status="ok", app="Interview Preparation System")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
