import streamlit as st
import json
import os
import pandas as pd
import plotly as px

# Directory where user folders and JSON files are saved
user_directory = "users"

# Ensure the user directory exists
if not os.path.exists(user_directory):
    try:
        os.makedirs(user_directory)
    except PermissionError:
        st.error("Permission denied: Unable to create the user directory. Please check permissions.")
        st.stop()

# Function to check if email is already registered
def is_email_registered(email):
    try:
        for user_file in os.listdir(user_directory):
            st.write(f"Checking file: {user_file}")
            with open(os.path.join(user_directory, user_file), 'r') as f:  
                user_data = json.load(f)
                if user_data['Email'] == email:
                    return True
    except Exception as e:
        st.error(f"Error: {e}")
    return False

# Function to create a new user
def create_user(name, phone, dob, email, password):
    if is_email_registered(email):
        st.error("A user with this email address already exists. Please use a different email.")
        return False

    # Create a new directory for the user
    user_folder = os.path.join(user_directory, email)
    try:
        os.makedirs(user_folder, exist_ok=True)
    except PermissionError:
        st.error(f"Permission denied: Unable to create directory for {email}.")
        return False
    
    # Create a JSON file with user details
    user_data = {
        "Name": name,
        "Phone": phone,
        "DOB": dob,
        "Email": email,
        "Password": password
    }
    user_file = os.path.join(user_directory, f"{email}.json")
    try:
        with open(user_file, 'w') as f:
            json.dump(user_data, f)
    except PermissionError:
        st.error(f"Permission denied: Unable to write data for {email}.")
        return False

    st.success(f"User {name} created successfully!")
    return True

# Function to validate login credentials
def validate_login(email, password):
    st.write(f"Attempting login for: {email}")
    if is_email_registered(email):
        user_file = os.path.join(user_directory, f"{email}.json")
        try:
            with open(user_file, 'r') as f:
                user_data = json.load(f)
                st.write(f"User data loaded for: {email}")
                if user_data["Password"] == password:
                    st.success("Password matched!")
                    return True, user_data
                else:
                    st.error("Incorrect password")
                    return False, None
        except Exception as e:
            st.error(f"Error reading user file: {e}")
    else:
        st.error("Email not registered")
    return False, None

# Function to save marks as CSV
def save_marks(email, marks_dict):
    user_folder = os.path.join(user_directory, email)
    csv_file = os.path.join(user_folder, "marks.csv")

    # Convert marks dict to dataframe
    df = pd.DataFrame(list(marks_dict.items()), columns=["Subject", "Marks"])
    
    # Save to CSV
    df.to_csv(csv_file, index=False)
    st.success("Marks saved successfully!")

# Function to load marks
def load_marks(email):
    user_folder = os.path.join(user_directory, email)
    csv_file = os.path.join(user_folder, "marks.csv")

    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        return None

# Streamlit UI
st.title("Welcome to the App")

# Sidebar for login/signup
menu = ["Log In", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if st.session_state.logged_in_user:
    st.sidebar.write(f"Welcome, {st.session_state.logged_in_user['Name']}!")
    if st.sidebar.button("Sign out"):
        st.session_state.logged_in_user = None
        st.experimental_rerun()

if choice == "Sign Up":
    st.subheader("Create a New Account")

    # Create form for sign up
    with st.form(key='signup_form'):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        dob = st.date_input("Date of Birth")
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        signup_button = st.form_submit_button(label="Sign Up")

        # On form submission
        if signup_button:
            if name and phone and dob and email and password:
                create_user(name, phone, str(dob), email, password)
            else:
                st.error("Please fill in all fields.")

elif choice == "Log In":
    st.subheader("Login to Your Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type='password')
    login_button = st.button("Login")

    if login_button:
        valid, user_data = validate_login(email, password)
        if valid:
            st.session_state.logged_in_user = user_data
            st.success(f"Logged in successfully as {user_data['Name']}!")
        else:
            st.error("Invalid credentials. Please try again.")

if st.session_state.logged_in_user:
    user_email = st.session_state.logged_in_user["Email"]
    st.subheader(f"Welcome, {st.session_state.logged_in_user['Name']}!")

    # Take marks input for 7 subjects
    marks = {}
    subjects = ["AAI", "ATSA", "FOML", "DBMS", "Algo Trading", "Predictive Analytics", "IMAP"]

    with st.form(key='marks_form'):
        for subject in subjects:
            marks[subject] = st.slider(f"Choose your marks for {subject}", 0, 100, 50)
        submit_button = st.form_submit_button(label="Submit Marks")

        if submit_button:
            save_marks(user_email, marks)

    # Load marks if available
    df_marks = load_marks(user_email)

    if df_marks is not None:
        st.subheader("Your Reports are Ready!")

        # Bar chart for average marks
        st.write("**Average Marks**")
        avg_marks = df_marks["Marks"].mean()
        st.write(f"Your average marks: {avg_marks}")

        # Bar graph
        bar_fig = px.bar(df_marks, x="Subject", y="Marks", title="Marks per Subject (Bar Graph)")
        st.plotly_chart(bar_fig)

        # Line graph
        line_fig = px.line(df_marks, x="Subject", y="Marks", title="Marks per Subject (Line Graph)")
        st.plotly_chart(line_fig)

        # Pie chart
        pie_fig = px.pie(df_marks, values="Marks", names="Subject", title="Marks Distribution (Pie Chart)")
        st.plotly_chart(pie_fig)
