import os
import sqlite3
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Retrieve and print API keys for debugging (remove or hide in production)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("SendGrid API Key:", SENDGRID_API_KEY)
print("Gemini API Key:", GEMINI_API_KEY)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Function to send email notifications using SendGrid
def send_deadline_notification(recipient_email, task_title, deadline, additional_message=""):
    message = Mail(
        from_email='sender@email',  # Replace with your verified sender email
        to_emails=recipient_email,
        subject=f"Reminder: Deadline Approaching for {task_title}",
        plain_text_content=(
            f"Hello,\n\nThis is a reminder that the deadline for your task '{task_title}' is approaching on {deadline}.\n\n"
            f"{additional_message}\n\nBest regards,\nTaskBot Team"
        )
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent to {recipient_email} with status code:", response.status_code)
    except Exception as e:
        print("Error sending email:", str(e))

# Function to query the database for tasks with deadlines exactly 2 days from now
def get_tasks_due_in_two_days():
    conn = sqlite3.connect("test.db")  # Adjust the path to your database file if needed
    cursor = conn.cursor()
    
    query = """
    SELECT t.TITLE, t.DEADLINE, c.EMAIL
    FROM TASKS t
    JOIN CONTACTS c ON t.ASSIGNED_TO = c.ID
    WHERE date(t.DEADLINE) = date('now', '+2 days')
    """
    cursor.execute(query)
    tasks = cursor.fetchall()
    conn.close()
    return tasks

# Function to process tasks with LLM (Gemini) for additional message/recommendations
def process_tasks_with_llm(tasks):
    
    prompt =  """You are generating a single email notification for the following task:

                Please create an email notification for the task assigned to the person below, ensuring it is polite, motivating, and encourages them to complete the task on time. The email should not be repetitive, and should include the following structure:
                
                1. A friendly greeting that addresses the person by their name.
                2. A clear mention of the task title and its deadline.
                3. A brief and polite reminder of the task deadline.
                4. A suggestion or recommendation to help them manage the task efficiently.
                5. A closing line offering help or resources if needed.
                
                Your goal is to ensure that the email is helpful, clear, and motivating. Only generate **one email** based on the provided task details. Do not include any additional options or versions.
                The following tasks have deadlines in 2 days:\n
             """ 
    for title, deadline, email in tasks:
        prompt += f"Task: {title}, Deadline: {deadline}, Assigned To: {email}\n"
    prompt += "\nPlease provide an additional message or recommendation to include in the email notifications."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        llm_response = response.text.strip() if response and response.text else ""
        print("LLM Response:", llm_response)
        return llm_response
    except Exception as e:
        print("Error during LLM processing:", str(e))
        return ""

# Main function to check tasks and send notifications
def check_and_notify():
    print("Checking tasks due in 2 days...")
    tasks = get_tasks_due_in_two_days()
    if tasks:
        additional_message = process_tasks_with_llm(tasks)
        for title, deadline, recipient_email in tasks:
            send_deadline_notification(recipient_email, title, deadline, additional_message)
    else:
        print("No tasks with deadlines in 2 days.")

# Scheduler to run the check_and_notify function at a fixed time
scheduler = BlockingScheduler()
scheduler.add_job(check_and_notify, 'cron', hour=10, minute=0)  # Adjust the time as needed

if __name__ == "__main__":
    print("Starting scheduler... (Press Ctrl+C to exit)")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")
