import os
import sys
import datetime
from django.core.mail import send_mail


# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MUST.settings')  
import django
django.setup()

from django.conf import settings

def check_email_settings():
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"TLS Enabled: {settings.EMAIL_USE_TLS}")
    print(f"Email User: {settings.EMAIL_HOST_USER}")
    print(f"Admins: {settings.ADMINS}")

check_email_settings()

def test_email():
    print("Testing email sending...")
    try:
        send_mail(
            'Test Email from Django API',
            'This is a test email to verify your Django email configuration is working.',
            settings.EMAIL_HOST_USER,
            [admin[1] for admin in settings.ADMINS],
            fail_silently=False,
        )
        print("Test email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def check_log_file():
    log_file = 'api_requests.log'
    if not os.path.exists(log_file):
        print(f'Warning: Log file {log_file} not found')
        return
    
    print(f"Log file exists at: {os.path.abspath(log_file)}")
    
    # Check file size
    size = os.path.getsize(log_file)
    print(f"Log file size: {size} bytes")
    
    # Check if file has content
    if size == 0:
        print("Log file is empty!")
        return
    
    # Check log file content
    with open(log_file, 'r') as f:
        first_lines = [next(f) for _ in range(5)]
        print("First few lines of log file:")
        for line in first_lines:
            print(f"  {line.strip()}")

# Call this function
check_log_file()
def send_api_report():
    # Get today's date
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    # Read from your log file
    log_file = 'api_requests.log'
    if not os.path.exists(log_file):
        print(f'Warning: Log file {log_file} not found')
        return
    
    # Try to get logs for yesterday first
    yesterday_logs = []
    today_logs = []
    
    with open(log_file, 'r') as f:
        for line in f:
            if yesterday.strftime('%Y-%m-%d') in line:
                yesterday_logs.append(line)
            if today.strftime('%Y-%m-%d') in line:
                today_logs.append(line)
    
    # Decide which logs to use
    logs_to_report = yesterday_logs if yesterday_logs else today_logs
    date_to_report = yesterday if yesterday_logs else today
    
    if not logs_to_report:
        print("No logs found for yesterday or today. Sending empty report.")
    
    # Compile report
    report = f"API Usage Report for {date_to_report}\n\n"
    report += f"Total Requests: {len(logs_to_report)}\n\n"
    
    if logs_to_report:
        report += "Details:\n"
        report += "\n".join(logs_to_report)
    else:
        report += "No API requests logged for this period."
    
    print(f"Sending report with {len(logs_to_report)} log entries")
    
    # Send email
    recipients = ['ondeyostephen0@gmail.com'] 
    try:
        send_mail(
            f'API Usage Report - {date_to_report}',
            report,
            settings.EMAIL_HOST_USER,
            recipients,
            fail_silently=False,
        )
        print('Successfully sent API report')
    except Exception as e:
        print(f"Error sending email: {str(e)}")
if __name__ == "__main__":
    send_api_report()
