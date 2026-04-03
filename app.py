from flask import Flask, render_template, request, redirect, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
import PyPDF2
import sqlite3
import nltk
import string
from werkzeug.security import generate_password_hash, check_password_hash

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# ---------------- APP CONFIG ----------------

app = Flask(__name__)
app.secret_key = "plagiarism_secret"

DATABASE = "database.db"


# ---------------- NLP SETUP ----------------

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


# ---------------- DATABASE ----------------

def get_db():
    return sqlite3.connect(DATABASE)


def init_db():

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- TEXT EXTRACTION ----------------

def extract_text(file):

    if not file:
        return None

    filename = file.filename.lower()

    try:

        if filename.endswith(".txt"):
            return file.read().decode("utf-8", errors="ignore")

        elif filename.endswith(".docx"):

            doc = Document(file)
            return "\n".join(p.text for p in doc.paragraphs)

        elif filename.endswith(".pdf"):

            reader = PyPDF2.PdfReader(file)
            text = ""

            for page in reader.pages:
                text += page.extract_text() or ""

            return text

    except:
        return None

    return None


# ---------------- TEXT PREPROCESS ----------------

def preprocess_text(text):

    text = text.lower()

    text = text.translate(str.maketrans("", "", string.punctuation))

    tokens = word_tokenize(text)

    tokens = [w for w in tokens if w not in stop_words]

    tokens = [lemmatizer.lemmatize(w) for w in tokens]

    return " ".join(tokens)


# ---------------- SIMILARITY ----------------

def calculate_similarity(t1, t2):

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform([t1, t2])

    score = cosine_similarity(vectors)[0][1]

    return score * 100


# ---------------- SENTENCE MATCHING ----------------

def get_similar_sentences(input_text, db_text):

    input_sentences = sent_tokenize(input_text)
    db_sentences = sent_tokenize(db_text)

    unique_matches = {}

    # preprocess database sentences once
    processed_db = [(s, preprocess_text(s)) for s in db_sentences]

    for s1 in input_sentences:

        p1 = preprocess_text(s1)

        for s2, p2 in processed_db:

            score = calculate_similarity(p1, p2)

            if score > 60:

                if s1 not in unique_matches or score > unique_matches[s1]:
                    unique_matches[s1] = round(score, 2)

    matches = [(s, sc) for s, sc in unique_matches.items()]

    matches = sorted(matches, key=lambda x: x[1], reverse=True)[:10]

    return matches


# ---------------- LOGIN ----------------

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login_auth", methods=["POST"])
def login_auth():

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT password FROM users WHERE username=?", (username,))
    user = c.fetchone()

    conn.close()

    if user and check_password_hash(user[0], password):

        session["user"] = username
        return redirect("/")

    return render_template("login.html", error="Invalid username or password")


# ---------------- REGISTER ----------------

@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register_user", methods=["POST"])
def register_user():

    username = request.form["username"]
    password = generate_password_hash(request.form["password"])

    conn = get_db()
    c = conn.cursor()

    try:

        c.execute(
            "INSERT INTO users (username,password) VALUES (?,?)",
            (username, password),
        )

        conn.commit()

    except:
        return "Username already exists"

    conn.close()

    return redirect("/login")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


# ---------------- HOME ----------------

@app.route("/")
def index():

    if "user" not in session:
        return redirect("/login")

    return render_template("index.html")


# ---------------- ADD DOCUMENT ----------------

@app.route("/add", methods=["POST"])
def add_document():

    if "user" not in session:
        return redirect("/login")

    file = request.files["file"]

    text = extract_text(file)

    if text:

        conn = get_db()
        c = conn.cursor()

        c.execute("INSERT INTO documents (content) VALUES (?)", (text,))

        conn.commit()
        conn.close()

    return redirect("/")


# ---------------- CHECK PLAGIARISM ----------------

@app.route("/check", methods=["POST"])
def check():

    if "user" not in session:
        return redirect("/login")

    file = request.files["file"]

    input_text = extract_text(file)

    if not input_text:
        return "Unsupported file format"

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT content FROM documents")

    docs = c.fetchall()

    conn.close()

    if not docs:
        return "No reference documents in database"

    highest_score = 0
    all_matches = []

    processed_input = preprocess_text(input_text)

    for doc in docs:

        processed_doc = preprocess_text(doc[0])

        score = calculate_similarity(processed_input, processed_doc)

        highest_score = max(highest_score, score)

        matches = get_similar_sentences(input_text, doc[0])

        all_matches.extend(matches)

    return render_template(
        "result.html",
        score=round(highest_score, 2),
        matches=all_matches
    )


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)