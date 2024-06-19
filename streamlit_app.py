import streamlit as st
import calendar
from datetime import datetime
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
from streamlit_pandas_profiling import st_profile_report
import sqlite3

conn = sqlite3.connect('studentmonitor.db', check_same_thread=False)
cur = conn.cursor()

names = ["Johniel Babiera", "Daisy Polestico"]
usernames = ["jbabiera","dpolestico"]

file_path = Path(__file__).parent/"hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names,usernames,hashed_passwords, "application_system", "abcdef", cookie_expiry_days=0)

name, authentication_status, username = authenticator.login("Login","main")

# Initialize session state variables
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Main app
if st.session_state.logged_in and st.session_state.authentication_status:
    name, authentication_status, username = authenticator.login("Login", "main")
    if authentication_status:
        st.session_state.logged_in = True
        st.session_state.authentication_status = authentication_status
        st.rerun()
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')

if authentication_status:
    st.title="Student Monitoring System"
    st.sidebar.success("Succesfully Logged in!")
    with st.sidebar:
        selected = option_menu(
            menu_title="Main Menu",
            options=["Home", "Student Registration", "Prospectus", "Course Assignment and Enrollment", "Grade Report"],
            icons=["house-fill", "person-lines-fill", "book-fill", "list-columns-reverse", "bar-chart-line-fill"],
            menu_icon = "cast",
            default_index=0,
        )

        # Initialize session state variable if it doesn't exist
        if 'refresh' not in st.session_state:
            st.session_state.refresh = 0

        # Function to increment the state
        def refresh_state():
            st.session_state.refresh += 1

        # Refresh button
        st.button('Navigation', on_click=refresh_state)

        def logout():
            st.session_state.logged_in = False
            st.session_state.authentication_status = None
            st.info("Logged out successfully!")
            st.experimental_rerun()

        if st.button("Log out"):
                logout()

    st.markdown("# Student Monitoring System")
    st.write(f'Welcome *{name}*')

    if selected == "Home":
        st.line_chart(np.random.randn(30, 3))
        chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
        st.bar_chart(chart_data)

        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode("utf-8")

        csv = convert_df(chart_data)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name="large_df.csv",
            mime="text/csv",
        )
        
    if selected == "Student Registration":
        def addStudent(StudentID, Name, YearLevel, Sex, ScholasticStatus, ScholarshipStatus, ContactNumber):
            cur.execute(
                """CREATE TABLE IF NOT EXISTS student (
                StudentID TEXT NOT NULL UNIQUE,
                Name TEXT NOT NULL,
                YearLevel INTEGER NOT NULL,
                Sex TEXT,
                ScholasticStatus TEXT,
                ScholarshipStatus TEXT,
                ContactNumber TEXT,
                PRIMARY KEY(StudentID))"""
            )
            cur.execute("INSERT INTO student(StudentID, Name, YearLevel, Sex, ScholasticStatus, ScholarshipStatus, ContactNumber) VALUES (?,?,?,?,?,?,?)",
                        (StudentID, Name, YearLevel, Sex, ScholasticStatus, ScholarshipStatus, ContactNumber))
            conn.commit()
            conn.close()

            # ------------ SETTINGS ------------
        yrlvl = ["1", "2", "3", "4"]
        sex = ["Male", "Female"]
        scholastic = ["Rizal's Lister", "Chancellor's Lister", "Dean's Lister"]
        program = ["BS Mathematics", "BS Statistics"]
        page_title = "Student Registration"
        page_icon = ":green_book:"
        layout = "centered"

        # ------------ NAVIGATION ------------
        selected = option_menu(
            menu_title=None,
            options=["Student Registration", "Student Directory"],
            icons=["person-circle", "folder-fill"],
            orientation="horizontal",
        )

        # ------------ INPUT AND SAVE ------------
        if selected == "Student Registration":
            st.header("Demographics")
            with st.form("entry_form", clear_on_submit=True):
                idnum = st.text_input("ID Number", placeholder="####-####")
                fname = st.text_input("Firstname", placeholder="Sana")
                lname = st.text_input("Lastname", placeholder="Minatozaki")

                col1, col2, col3, col4 = st.columns(4)
                year_level = col1.selectbox("Year Level", yrlvl)
                prog = col2.selectbox("Program", program)
                gender = col3.selectbox("Sex", sex)
                schol_status = col4.selectbox("Scholastic Status", scholastic)

                scholarship = st.text_input("Scholarship Status", placeholder="DOST")
                number = st.text_input("Phone Number", placeholder="09#########")
                "---"
                submitted = st.form_submit_button("Register")
                if submitted:
                    addStudent(idnum, fname + " " + lname, year_level, gender, schol_status, scholarship, number)
                    st.success("Data saved successfully.")

         # ------------ STUDENT LIST ------------
        elif selected == "Student Directory":
            st.header("Student Directory")
            conn = sqlite3.connect('studentmonitor.db')
            df = pd.read_sql_query("SELECT * FROM student", conn)
            conn.close()
            st.dataframe(df)

        # ------------------------------
    if selected == "Prospectus":
        def addProspectus(CourseCode, CourseDesc, Units, Semester, AcadYear):
            cur.execute(
                """CREATE TABLE IF NOT EXISTS prospectus (
                CourseCode TEXT NOT NULL UNIQUE,
                CourseDesc TEXT NOT NULL,
                Units INTEGER NOT NULL,
                Semester TEXT NOT NULL,
                AcadYear TEXT NOT NULL,
                PRIMARY KEY(CourseCode))"""
            )

            cur.execute("INSERT INTO prospectus(CourseCode, CourseDesc, Units, Semester, AcadYear) VALUES (?,?,?,?,?)",
                        (CourseCode, CourseDesc, Units, Semester, AcadYear))
            conn.commit()
            conn.close()

        # ------------ NAVIGATION ------------
        selected = option_menu(
            menu_title=None,
            options=["Course Registration", "Prospectus"],
            icons=["clipboard-fill", "folder-fill"],
            orientation="horizontal",
        )

        # ------------ SETTINGS ------------
        units = ["1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "4.5", "5.0", "5.5"]
        semester = ["1st Sem", "2nd Sem", "Summer"]
        yearlevel = ["1", "2", "3", "4"]
        page_icon = ":green_book:"
        layout = "centered"

        if selected == "Course Registration":
            # ------------ INPUT AND SAVE PERIODS ------------
            st.header("Course Registration")
            with st.form("entry_form", clear_on_submit=True):
                coursecode = st.text_input("Course Code", placeholder="STT155")
                coursedescription = st.text_input("Course Description", placeholder="Categorical Data Analysis")
                
                col1, col2, col3 = st.columns(3)
                selected_units = col1.selectbox("Input Units", units, key="units")
                selected_yearlevel = col2.selectbox("Year Level", yearlevel, key="yrlvl")
                selected_semester = col3.selectbox("Semester", semester, key="sem")

                submitted = st.form_submit_button("Register")
                if submitted:
                    addProspectus(coursecode, coursedescription, selected_units, selected_semester, selected_yearlevel)
                    st.success("Data saved successfully.")
        # ------------ PROSPECTUS ------------
        elif selected == "Prospectus":
            st.header("Prospectus")
            conn = sqlite3.connect('studentmonitor.db')
            df = pd.read_sql_query("SELECT * FROM prospectus", conn)
            conn.close()
            st.dataframe(df)

    if selected == "Course Assignment and Enrollment":
        # Function to add course assignment
        def addCourseAssignment(EnrollID, StudentID, CourseCode, Grade, GradeStatus, Semester, Year, Remarks):
            cur.execute(
                """CREATE TABLE IF NOT EXISTS courseassignment (
                    EnrollID TEXT,
                    StudentID TEXT ,
                    CourseCode TEXT ,
                    Grade TEXT,
                    GradeStatus TEXT,
                    Semester TEXT ,
                    Year TEXT ,
                    Remarks TEXT,
                    FOREIGN KEY(StudentID) REFERENCES student(StudentID),
                    FOREIGN KEY(CourseCode) REFERENCES prospectus(CourseCode)
                )"""
            )
            cur.execute("INSERT INTO courseassignment (EnrollID, StudentID, CourseCode, Grade, GradeStatus, Semester, Year, Remarks) VALUES (?,?,?,?,?,?,?,?)",
                        (EnrollID, StudentID, CourseCode, Grade, GradeStatus, Semester, Year, Remarks))
            conn.commit()

        # Settings
        semester = ["1st Term", "2nd Term", "Summer Term"]
        current_year = datetime.today().year
        school_year = [f"{year}-{year+1}" for year in range(current_year, current_year + 10)]

        # Fetching student IDs
        cur.execute("SELECT StudentID FROM student")
        students = cur.fetchall()
        student_ids = [student[0] for student in students]

        # Fetching course codes (assuming course codes are present in the 'prospectus' table)
        cur.execute("SELECT CourseCode FROM prospectus")
        courses = cur.fetchall()
        course_codes = [course[0] for course in courses]

    
        # Navigation
        # --- NAVIGATION MENU ---
        selected = option_menu(
            menu_title=None,
            options=["Course Assignment", "Course Directory"],  
            orientation="horizontal",)

        # Course Assignment Page
        if selected == "Course Assignment":
            st.header("Course Assignment")
            with st.form("Course Assignment", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                selected_year = col1.selectbox("Select Academic Year:", school_year, key="year")
                selected_semester = col2.selectbox("Select Semester:", semester, key="sem")
                    
                "---"
                selected_student_id = st.selectbox("Select Student:", student_ids)
                selected_course = st.multiselect("Enrolled Course", course_codes)

                remarks = st.text_input("Input count taken:")
                "---"
                submit = st.form_submit_button("Assign")

                if submit:
                    for course in selected_course:
                        course_str = ",".join(selected_course)
                        addCourseAssignment(None,selected_student_id, course_str, None, None, selected_semester, selected_year, remarks)
                    st.success('Course assignment has been successful')

        # Course Directory Page
        elif selected == "Course Directory":
            st.header("Course Directory")
            df = pd.read_sql_query("SELECT StudentID, CourseCode, Semester, Year, Remarks  FROM courseassignment", conn)
            conn.close()
            st.dataframe(df)

    if selected == "Grade Report":
        with st.sidebar:
            selected = option_menu(
                menu_title="Class Record",
                options=["Alingas, Lavina Grace", "Ayop, Kyla", "Bahian, Ken Andrea", "Balcita, Jolia Keziah", "Cagula, Angel Dunamis", "Garridos, Charlene"],
                menu_icon = "pen-fill",
                default_index=0,
            )
        
        current_year = datetime.today().year
        school_year = [f"{year}-{year+1}" for year in range(current_year, current_year+10)]
        semester = ["1st Sem", "2nd Sem", "Summer"]

        col1, col2 = st.columns(2)
        col1.selectbox("Select Academic Year", school_year, key="sch.yr")
        col2.selectbox("Semester", semester, key="sem")
