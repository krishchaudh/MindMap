from twilio.rest import Client
from dotenv import load_dotenv
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os

# Load environment variables
load_dotenv()
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Google Sheets setup   
def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("WORK").sheet1  # Replace with your Google Sheet name
    return sheet

# Function to get today's schedule 
def get_schedule():
    schedules = {
        "Monday": (
            "*Monday:*\n"
            "408D Discussion 9am - 10am\n"
            "UGS 303 10am - 11am\n"
            "ECE 306 12pm - 1:30pm\n"
            "ECE 302 1:30pm - 3pm\n" 
            "Zoom - 4:15pm\n"
        ),
        "Tuesday": (
            "*Tuesday:*\n"
            "408D Lecture 11am - 12:30pm\n"
            "Zoom - 4:15pm\n"
            "IM Basketball Game 5pm - 6pm"
        ),   
        "Wednesday": (
            "*Wednesday:*\n"
            "408D Discussion 9am - 10am\n"
            "UGS 303 10am - 11am\n"
            "ECE 306 12pm - 1:30pm\n"
            "ECE 302 1:30pm - 3pm\n"
            "Zoom - 4:15pm\n" 
        ),
        "Thursday": (
            "*Thursday:*\n"
            "408D Lecture 11am - 12:30pm\n"
            "ECE 302 Lab 1pm - 3pm\n"
            "ECE 306 Recitation 5pm - 6pm\n"
            "Zoom - 4:15pm\n"
        ),
        "Friday": (
            "*Friday:*\n"
            "UGS 303 Discussion 9am - 10am (MANDATORY)\n"
            "Zoom - 4:15pm\n"
        ),
    }
    today = datetime.now().strftime("%A")
    return schedules.get(today, "No classes scheduled for today!")

# Function to check and send assignments due today
def send_today_assignments():
    sheet = get_google_sheet()
    data = sheet.get_all_records()
    today = datetime.now().date()
    
    # Prepare a message with all assignments due today
    assignments_due_today = []
    for row in data:
        assignment = row["Assignment Name"]
        due_str = row["Due Date and Time"]
        due_date = datetime.strptime(due_str, "%Y-%m-%d %H:%M").date()

        # If the assignment is due today, add it to the list
        if due_date == today:
            due_time = datetime.strptime(due_str, "%Y-%m-%d %H:%M").strftime("%I:%M %p")
            assignments_due_today.append(f"{assignment} due at {due_time}")
    
    # Send a message if there are any assignments due today
    if assignments_due_today:
        message = "*Assignments due today:*\n" + "\n".join(assignments_due_today)
    else:
        message = "No assignments due today."
    
    twilio_client.messages.create(
        body=message,
        from_='whatsapp:+14155238886',  # Twilio Sandbox WhatsApp number
        to='whatsapp:' + os.getenv("YOUR_PHONE_NUMBER")
    )

# Main function to send daily schedule and today's assignments
def send_daily_whatsapp():
    # Send today's schedule
    schedule_message = get_schedule()
    twilio_client.messages.create(
        body=schedule_message,
        from_='whatsapp:+14155238886',  # Twilio Sandbox WhatsApp number
        to='whatsapp:' + os.getenv("YOUR_PHONE_NUMBER")
    )
    
    # Check and send today's assignments
    send_today_assignments()

# Run the function to test
send_daily_whatsapp()

