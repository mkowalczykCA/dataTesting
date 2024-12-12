import os
import base64
import functions_framework
from dotenv import load_dotenv
from google.auth import default
from google.cloud import logging
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

### Manual/Local Credentials Injection
## Comment out before Deployment. Cloud Run provides a Service Account.
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv("FILEPWD")



## Test
credentials, project_id = default()
print(f"\nAuthenticated to project: {project_id}\n")


SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_email(subject, body, recipient_email):
    sender_email = SENDER_EMAIL
    sender_password = EMAIL_PASS
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def pull_logs(project_id, filter_query=None, days=1):
    client = logging.Client(project=project_id)
    
    # Time range for logs
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=days)
    start_time_iso = start_time.isoformat("T")
    
    ## Default Time Range
    # start_time = now - timedelta(days=days)
    # start_time_iso = start_time.isoformat("T")

    # Filter
    log_filter = f'timestamp >= "{start_time_iso}"'
    if filter_query:
        log_filter += f" AND {filter_query}"

    error_logs = []
    all_logs = []
    
    # Pull logs
    print(f"Querying logs with filter: {log_filter}")
    for count, entry in enumerate(client.list_entries(filter_=log_filter, order_by=logging.DESCENDING), 1):
        if "ERROR" in entry.severity:
            log_entry = f"🔴 --- Log Entry {count} ---\n"
            log_entry += f"Timestamp: {entry.timestamp}\n"
            log_entry += f"Log Name: {entry.log_name}\n"
            log_entry += f"Severity: {entry.severity}\n"
            log_entry += f"Payload: {entry.payload}\n"
            log_entry += f"Resource: {entry.resource.labels}\n"
            error_logs.append(log_entry)
            all_logs.append(log_entry)
        elif "ERROR" not in entry.severity:
            log_entry = f"🟢 --- Log Entry {count} ---\n"
            log_entry += f"Timestamp: {entry.timestamp}\n"
            log_entry += f"Log Name: {entry.log_name}\n"
            log_entry += f"Severity: {entry.severity}\n"
            log_entry += f"Payload: {entry.payload}\n"
            log_entry += f"Resource: {entry.resource.labels}\n"
            all_logs.append(log_entry)
        
    print(error_logs)
    print(all_logs)
            
    if error_logs:
        subject = f"☹️ Pipeline Failure ☹️: Hey! There's {len(error_logs)} Dataform Error(s)"
        header = "🚨 See errors below: "
        after_body = f"⚠️ All Logs ({len(all_logs)}): "
        body = header + "\n\n" + "\n\n".join(error_logs) + "\n\n\n\n\n" + after_body + "\n\n" + "\n\n".join(all_logs)
        recipient_email = RECIPIENT_EMAIL
        send_email(subject, body, recipient_email)
        print(f"Email sent with {len(error_logs)} error(s)")
    else:
        subject = f"🎉 Pipeline Success 🎉: Hey! There's {len(error_logs)} Dataform Error(s)"
        header_text = "Woot~Woot! Nothing broke! :)"
        subheader_text = f"Anyways, here are the logs for the day ({len(all_logs)}): "
        body = header_text + "\n\n" + subheader_text + "\n\n" + "\n\n".join(all_logs)
        recipient_email = RECIPIENT_EMAIL
        send_email(subject, body, recipient_email)
        print(f"Email sent with {len(error_logs)} error(s) and {len(all_logs)} total logs")
        

# Legit Entry Point
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    print("Pub/Sub Target Function Hit")
    project_id = os.getenv("PROJECTID")
    filter_query = 'resource.type="dataform.googleapis.com/Repository"'
    pull_logs(project_id, filter_query)
    
# # Manual Entry Point
# if __name__ == "__main__":
#     project_id = os.getenv("PROJECTID")
#     filter_query = 'resource.type="dataform.googleapis.com/Repository"'
#     pull_logs(project_id, filter_query)