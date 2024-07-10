import streamlit as st
import sqlite3
from hashlib import sha256
from streamlit_option_menu import option_menu
import Home, Student_Registration, Prospectus, Course_Assignment, Grade_Report
import string
import random

def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Database connection
conn = sqlite3.connect('studentmonitor.db')
cur = conn.cursor()

# Create necessary tables
cur.execute("""
CREATE TABLE IF NOT EXISTS adviser (
    UserName TEXT NOT NULL,
    Password TEXT NOT NULL,
    Random_authenticator TEXT NOT NULL,
    PRIMARY KEY(UserName)
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS student (
    StudentID TEXT NOT NULL UNIQUE,
    Name TEXT NOT NULL,
    BirthDate TEXT NOT NULL,
    Sex TEXT NOT NULL,
    Gender TEXT NOT NULL,
    Religion TEXT NOT NULL,
    Region TEXT NOT NULL,
    Province TEXT NOT NULL,
    Municipality TEXT NOT NULL,
    Barangay TEXT NOT NULL,
    Track TEXT NOT NULL,
    Program TEXT NOT NULL,
    ContactNumber TEXT NOT NULL,
    PGName TEXT NOT NULL,
    PGNumber TEXT NOT NULL,
    PRIMARY KEY(StudentID)
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS academicrecords (
    RecordID INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID TEXT NOT NULL,
    ScholasticStatus TEXT NOT NULL,
    ScholarshipStatus TEXT,
    AcademicYear TEXT NOT NULL,
    YearLevel INTEGER NOT NULL,
    Semester TEXT NOT NULL,
    UNIQUE(StudentID, AcademicYear, Semester),
    FOREIGN KEY(StudentID) REFERENCES student(StudentID)
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS promotion (
                StudentID INTEGER,
                AcademicYear TEXT,
                Semester TEXT,
                PromotionStatus TEXT
            )""")

cur.execute("""
CREATE TABLE IF NOT EXISTS prospectus (
    CourseCode TEXT NOT NULL UNIQUE,
    CourseDesc TEXT NOT NULL,
    Units INTEGER NOT NULL,
    Semester TEXT NOT NULL,
    YearLevel TEXT NOT NULL,
    Classification TEXT NOT NULL,
    PRIMARY KEY(CourseCode)
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS requisite (
    CourseCode TEXT,
    Corequisite TEXT,
    Prerequisite TEXT,
    FOREIGN KEY(CourseCode) REFERENCES prospectus(CourseCode)
)""")

cur.execute("""
CREATE TABLE IF NOT EXISTS courseassignment (
    EnrollID INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID TEXT NOT NULL,
    CourseCode TEXT NOT NULL,
    Grade TEXT,
    FinalGrade TEXT,
    GradeStatus TEXT,
    AcademicYear TEXT,
    YearLevel TEXT,
    Semester TEXT,
    FOREIGN KEY(StudentID) REFERENCES student(StudentID),
    FOREIGN KEY(CourseCode) REFERENCES prospectus(CourseCode)
)""")


def generate_random_authenticator(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

if "create_username" not in st.session_state:
    st.session_state["create_username"] = ""
if "create_password" not in st.session_state:
    st.session_state["create_password"] = ""
if "random_authenticator" not in st.session_state:
    st.session_state["random_authenticator"] = ""
if "remember_me" not in st.session_state:
    st.session_state["remember_me"] = False
if "remembered_username" not in st.session_state:
    st.session_state["remembered_username"] = ""


def login_form():
    tabs = st.tabs(["Login", "Create Account", "Forgot Password"])

    with tabs[0]:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username_input", value=st.session_state.get("remembered_username", ""))
        password = st.text_input("Password", type="password", key="login_password_input")
        remember_me = st.checkbox("Remember Me", value=st.session_state.get("remember_me", False), key="login_remember_me")

        if st.button("Login", key="login_button"):
            hashed_password = hash_password(password)
            cur.execute("SELECT * FROM adviser WHERE Username=? AND Password=?", (username, hashed_password))
            user = cur.fetchone()

            if user:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                if remember_me:
                    st.session_state["remember_me"] = True
                    st.session_state["remembered_username"] = username
                else:
                    st.session_state["remember_me"] = False
                    st.session_state["remembered_username"] = ""
                st.success(f"Welcome {username}")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

    with tabs[1]:
        st.subheader("Create Account")
        create_username = st.text_input("Create a unique username", key="create_username_input")
        create_password = st.text_input("Create a password", type="password", key="create_password_input")

        if st.button("Create Account", key="create_account_button"):
            if create_username and create_password:
                cur.execute("SELECT Username FROM adviser WHERE Username=?", (create_username,))
                if cur.fetchone():
                    st.error("Username already exists")
                else:
                    hashed_password = hash_password(create_password)
                    random_authenticator = generate_random_authenticator()
                    try:
                        cur.execute("INSERT INTO adviser (Username, Password, Random_authenticator) VALUES (?, ?, ?)",
                                    (create_username, hashed_password, random_authenticator))
                        conn.commit()
                        st.success(f"Account created successfully. Your authenticator is: {random_authenticator}. Please keep or memorize it as it will be given only once.")
                    except sqlite3.IntegrityError:
                        st.error("Username already exists")
            else:
                st.error("Please enter a username and password")

    with tabs[2]:
        st.subheader("Forgot Password")
        forgot_username = st.text_input("Username", key="forgot_username_input")
        random_authenticator = st.text_input("Random Authenticator", key="forgot_random_authenticator_input")
        new_password = st.text_input("New Password", type="password", key="forgot_new_password_input")
        repeat_password = st.text_input("Repeat Password", type="password", key="forgot_repeat_password_input")

        if st.button("Reset Password", key="reset_password_button"):
            if new_password != repeat_password:
                st.error("Passwords do not match")
            else:
                cur.execute("SELECT Random_authenticator FROM adviser WHERE Username=? AND Random_authenticator=?",
                            (forgot_username, random_authenticator))
                user = cur.fetchone()

                if user:
                    hashed_new_password = hash_password(new_password)
                    cur.execute("UPDATE adviser SET Password=? WHERE Username=?", (hashed_new_password, forgot_username))
                    conn.commit()
                    st.success("Password reset successfully")
                else:
                    st.error("Invalid username or authenticator")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

conn = sqlite3.connect('studentmonitor.db')
cur = conn.cursor()

adviser_table = """CREATE TABLE IF NOT EXISTS adviser (
                Username TEXT NOT NULL,
                Password TEXT NOT NULL,
                Random_authenticator TEXT NOT NULL,
                PRIMARY KEY(Username))"""
cur.execute(adviser_table)

if st.session_state["authenticated"]:
    if st.session_state["username"]:
        st.success(f"Welcome {st.session_state['username']}")
        st.sidebar.success("Successfully Logged in!")
        with st.sidebar:
            app = option_menu(
                menu_title="Main Menu",
                options=["Home", "Student Registration", "Prospectus", "Course Assignment", "Grade Report"],
                icons=["house-fill", "person-lines-fill", "book-fill", "list-columns-reverse", "bar-chart-line-fill"],
                menu_icon="cast",
                default_index=0,
            )

            def logout():
                st.session_state["authenticated"] = False
                st.session_state["username"] = None
                st.info("Logged out successfully!")
                st.experimental_rerun()

            if st.sidebar.button("Log out"):
                logout()

        st.markdown("# Student Monitoring System")
        if app == "Home":
            Home.app()
        if app == "Student Registration":
            Student_Registration.app()
        if app == "Prospectus":
            Prospectus.app()
        if app == "Course Assignment":
            Course_Assignment.app()
        if app == "Grade Report":
            Grade_Report.app()

else:
    login_form()

conn.close()