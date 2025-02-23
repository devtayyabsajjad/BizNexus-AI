import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import json
from supabase import create_client, Client
import requests
import io
from dotenv import load_dotenv
import re
import pdfplumber

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Initialize IBM Granite
GRANITE_API_KEY = os.getenv('GRANITE_API_KEY')
GRANITE_API_URL = os.getenv('GRANITE_API_URL')

# Set page configuration
st.set_page_config(page_title="HRMS Dashboard", layout="wide")

# Dark Mode CSS for HRMS page
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background-color: #121212; color: #E0E0E0; }
        .stButton>button { background-color: #BB86FC; color: white; border-radius: 5px; }
        .stButton>button:hover { background-color: #3700B3; }
        .dataframe { background-color: #1E1E1E; color: #E0E0E0; }
    </style>
""", unsafe_allow_html=True)

class EmployeeManagement:
    @staticmethod
    def create_employee(data):
        return supabase.table('employees').insert(data).execute()
    
    @staticmethod
    def get_employees():
        return supabase.table('employees').select("*").execute()
    
    @staticmethod
    def update_employee(employee_id, data):
        return supabase.table('employees').update(data).eq('id', employee_id).execute()
    
    @staticmethod
    def delete_employee(employee_id):
        return supabase.table('employees').delete().eq('id', employee_id).execute()

class PayrollManagement:
    @staticmethod
    def calculate_salary(basic_pay, bonuses, deductions):
        return basic_pay + sum(bonuses) - sum(deductions)
    
    @staticmethod
    def generate_payslip(employee_id, month, year):
        employee = supabase.table('employees').select("*").eq('id', employee_id).execute()
        if not employee.data:
            raise ValueError(f"No employee found with ID {employee_id}")
        
        salary_details = supabase.table('salary_details').select("*").eq('employee_id', employee_id).execute()
        if not salary_details.data:
            raise ValueError(f"No salary details found for employee ID {employee_id}")
        
        prompt = f"""Generate a detailed payslip for:
        Employee: {employee.data[0]['name']}
        Month: {month} {year}
        Basic Pay: {salary_details.data[0]['basic_pay']}
        """
        return generate_document(prompt, "payslip")

class AttendanceManagement:
    @staticmethod
    def clock_in(employee_id):
        data = {
            'employee_id': employee_id,
            'clock_in': datetime.now().isoformat(),
            'date': date.today().isoformat()
        }
        return supabase.table('attendance').insert(data).execute()
    
    @staticmethod
    def clock_out(employee_id):
        current_time = datetime.now().isoformat()
        return supabase.table('attendance').update({'clock_out': current_time}).eq('employee_id', employee_id).eq('date', date.today().isoformat()).execute()
    
    @staticmethod
    def get_attendance(employee_id=None, start_date=None, end_date=None):
        query = supabase.table('attendance').select("*, employees(name)").order('date', desc=True)
        if employee_id:
            query = query.eq('employee_id', employee_id)
        if start_date:
            query = query.gte('date', start_date)
        if end_date:
            query = query.lte('date', end_date)
        return query.execute()

class GraniteAI:
    @staticmethod
    def process_chat_query(query):
        prompt = f"""You are an HR assistant. Please respond to this HR-related question:
        Question: {query}
        Provide a professional and helpful response."""
        return generate_document(prompt, "chat")
    
    @staticmethod
    def analyze_sentiment(text):
        prompt = f"""Analyze the sentiment of this text and provide a score (-1 to 1) and label (positive/negative/neutral):
        Text: {text}
        Format the response as JSON with 'score' and 'label' fields."""
        response = generate_document(prompt, "sentiment")
        try:
            import json
            return json.loads(response)
        except:
            return {"score": 0, "label": "neutral"}
    
    @staticmethod
    def parse_resume(pdf_file):
        try:
            with pdfplumber.open(pdf_file) as pdf_reader:
                extracted_text = ""
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
                cleaned_text = " ".join(extracted_text.split())
                cleaned_text = ''.join(char for char in cleaned_text if char.isalnum() or char.isspace())
                if not cleaned_text.strip():
                    return "Error: No text could be extracted from the PDF"
                prompt = f"""Please analyze this resume and provide the key information in a clear format:

                Resume Text:
                {cleaned_text}

                Please extract and organize:
                1. Personal Information
                2. Professional Summary
                3. Skills
                4. Work Experience
                5. Education

                Make necessary corrections to words for example: Llama3370b should be written as Llama-3.3-70b.
                """
                response = generate_document(prompt, "resume")
                if response:
                    return response
                else:
                    return "Error: Could not extract information from resume"
        except Exception as e:
            return f"Error: Failed to process resume - {str(e)}"

class SalaryManagement:
    @staticmethod
    def add_salary_details(data):
        return supabase.table('salary_details').insert(data).execute()
    
    @staticmethod
    def get_salary_details(employee_id=None):
        query = supabase.table('salary_details').select("*, employees(name)")
        if employee_id:
            query = query.eq('employee_id', employee_id)
        return query.execute()
    
    @staticmethod
    def update_salary(employee_id, basic_pay):
        data = {
            'basic_pay': basic_pay,
            'effective_date': date.today().isoformat()
        }
        return supabase.table('salary_details').update(data).eq('employee_id', employee_id).execute()

def get_iam_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get IAM token: {response.text}")

def generate_document(prompt, doc_type):
    iam_token = get_iam_token(GRANITE_API_KEY)
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    system_prompt = """You are Granite, an AI language model developed by IBM in 2024. 
    You provide accurate, helpful, and ethical responses."""
    full_prompt = f"""<|start_of_role|>system<|end_of_role|>{system_prompt}<|end_of_text|>
<|start_of_role|>user<|end_of_role|>{prompt}<|end_of_text|>
<|start_of_role|>assistant<|end_of_role|>"""
    body = {
        "input": full_prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 900,
            "min_new_tokens": 0,
            "repetition_penalty": 1
        },
        "model_id": "ibm/granite-3-8b-instruct",
        "project_id": "0d802a37-ca64-420e-864e-e7cdd8b8b006",
        "moderations": {
            "hap": {
                "input": {"enabled": True, "threshold": 0.5, "mask": {"remove_entity_value": True}},
                "output": {"enabled": True, "threshold": 0.5, "mask": {"remove_entity_value": True}}
            },
            "pii": {
                "input": {"enabled": True, "threshold": 0.5, "mask": {"remove_entity_value": True}},
                "output": {"enabled": True, "threshold": 0.5, "mask": {"remove_entity_value": True}}
            }
        }
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}"
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        raise Exception(f"API Error: {response.text}")
    data = response.json()
    return data.get('results', [{}])[0].get('generated_text', '')

def chat_interface():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    if prompt := st.chat_input("Ask your HR related question..."):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        response = GraniteAI.process_chat_query(prompt)
        with st.chat_message("assistant"):
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    st.title("HRMS Dashboard")
    
    page = st.sidebar.selectbox(
        "Select Module",
        ["Employee Management", "Salary Management", "Payroll", "Attendance", "HR Chatbot", "Sentiment Analysis", "Resume Screening"]
    )
    
    if page == "Employee Management":
        st.header("Employee Management")
        tab1, tab2, tab3 = st.tabs(["Add Employee", "View Employees", "Update/Delete"])
        with tab1:
            with st.form("new_employee"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                department = st.selectbox("Department", ["HR", "IT", "Finance", "Marketing"])
                role = st.text_input("Role")
                hire_date = st.date_input("Hire Date")
                if st.form_submit_button("Add Employee"):
                    EmployeeManagement.create_employee({
                        'name': name,
                        'email': email,
                        'department': department,
                        'role': role,
                        'hire_date': hire_date.isoformat()
                    })
                    st.success("Employee added successfully!")
        with tab2:
            employees = EmployeeManagement.get_employees()
            st.dataframe(pd.DataFrame(employees.data))
        with tab3:
            employee_id = st.number_input("Employee ID", min_value=1)
            if st.button("Delete Employee"):
                EmployeeManagement.delete_employee(employee_id)
                st.success("Employee deleted successfully!")
    
    elif page == "Payroll":
        st.header("Payroll Management")
        employee_id = st.number_input("Employee ID", min_value=1)
        month = st.selectbox("Month", ["January", "February", "March", "April", "May", "June",
                                     "July", "August", "September", "October", "November", "December"])
        year = st.number_input("Year", min_value=2020, max_value=2025, value=2024)
        if st.button("Generate Payslip"):
            try:
                payslip = PayrollManagement.generate_payslip(employee_id, month, year)
                st.text_area("Generated Payslip", payslip, height=300)
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error("An error occurred while generating the payslip")
    
    elif page == "Attendance":
        st.header("Attendance Management")
        tab1, tab2 = st.tabs(["Clock In/Out", "View Attendance"])
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                employee_id = st.number_input("Employee ID", min_value=1)
                if st.button("Clock In"):
                    AttendanceManagement.clock_in(employee_id)
                    st.success("Clocked in successfully!")
            with col2:
                if st.button("Clock Out"):
                    AttendanceManagement.clock_out(employee_id)
                    st.success("Clocked out successfully!")
        with tab2:
            col1, col2, col3 = st.columns(3)
            with col1:
                employees = EmployeeManagement.get_employees()
                employee_df = pd.DataFrame(employees.data)
                if not employee_df.empty:
                    employee_dict = dict(zip(employee_df['id'], employee_df['name']))
                    employee_dict[0] = "All Employees"
                    selected_employee = st.selectbox(
                        "Select Employee",
                        options=[0] + list(employee_df['id']),
                        format_func=lambda x: employee_dict[x]
                    )
            with col2:
                start_date = st.date_input("Start Date", value=date.today().replace(day=1))
            with col3:
                end_date = st.date_input("End Date", value=date.today())
            try:
                attendance = AttendanceManagement.get_attendance(
                    employee_id=selected_employee if selected_employee != 0 else None,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat()
                )
                if attendance.data:
                    df = pd.DataFrame(attendance.data)
                    df['employee_name'] = df['employees'].apply(lambda x: x['name'])
                    display_df = pd.DataFrame()
                    display_df['Employee ID'] = df['employee_id']
                    display_df['Employee Name'] = df['employee_name']
                    display_df['Date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                    display_df['Clock In'] = pd.to_datetime(df['clock_in']).dt.strftime('%I:%M %p')
                    display_df['Clock Out'] = pd.to_datetime(df['clock_out']).dt.strftime('%I:%M %p')
                    st.dataframe(display_df)
                else:
                    st.info("No attendance records found for the selected criteria")
            except Exception as e:
                st.error(f"Error fetching attendance data: {str(e)}")
    
    elif page == "HR Chatbot":
        st.header("HR Chatbot")
        chat_interface()
    
    elif page == "Sentiment Analysis":
        st.header("Sentiment Analysis")
        feedback = st.text_area("Enter feedback text:")
        if st.button("Analyze Sentiment"):
            sentiment = GraniteAI.analyze_sentiment(feedback)
            st.write("Sentiment Score:", sentiment['score'])
            st.write("Sentiment Label:", sentiment['label'])
    
    elif page == "Resume Screening":
        st.header("Resume Screening")
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=['pdf'])
        if uploaded_file is not None:
            try:
                results = GraniteAI.parse_resume(uploaded_file)
                if results and not results.startswith("Error"):
                    st.write("Resume Analysis Results:")
                    st.write(results)
                else:
                    st.error(results)
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    elif page == "Salary Management":
        st.header("Salary Management")
        tab1, tab2 = st.tabs(["Add/Update Salary", "View Salary Details"])
        with tab1:
            employees = EmployeeManagement.get_employees()
            employee_df = pd.DataFrame(employees.data)
            if not employee_df.empty:
                employee_dict = dict(zip(employee_df['id'], employee_df['name']))
                with st.form("salary_form"):
                    selected_employee = st.selectbox(
                        "Select Employee",
                        options=employee_df['id'],
                        format_func=lambda x: f"{x} - {employee_dict[x]}"
                    )
                    basic_pay = st.number_input("Basic Pay", min_value=0.0, value=0.0, step=1000.0)
                    if st.form_submit_button("Save Salary Details"):
                        try:
                            existing_salary = SalaryManagement.get_salary_details(selected_employee)
                            if existing_salary.data:
                                SalaryManagement.update_salary(selected_employee, basic_pay)
                                st.success("Salary details updated successfully!")
                            else:
                                SalaryManagement.add_salary_details({
                                    'employee_id': selected_employee,
                                    'basic_pay': basic_pay,
                                    'effective_date': date.today().isoformat()
                                })
                                st.success("Salary details added successfully!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.warning("No employees found. Please add employees first.")
        with tab2:
            salary_details = SalaryManagement.get_salary_details()
            if salary_details.data:
                df = pd.DataFrame(salary_details.data)
                df['employee_name'] = df['employees'].apply(lambda x: x['name'])
                display_df = df[['employee_id', 'employee_name', 'basic_pay', 'effective_date']].copy()
                display_df.columns = ['Employee ID', 'Name', 'Basic Pay', 'Effective Date']
                st.dataframe(display_df)
            else:
                st.info("No salary details found")

if __name__ == "__main__":
    main()
