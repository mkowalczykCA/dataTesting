import base64
import functions_framework

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



SENDER_EMAIL = "martin@changedapps.com"
RECIPIENT_EMAIL = "martin@changedapps.com"
EMAIL_PASS = "fxzn xeph soeq keom"


def send_test_email():
    sender_email = SENDER_EMAIL  # Your email
    sender_password = EMAIL_PASS  # Your email password (or app-specific password)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    recipient_email = RECIPIENT_EMAIL  # Email to send the test to

    subject = "TESTING SERVICE RAAAAAAAA"
    body = "d-d-d-d-d-dj marten rules number 1 coder"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish a connection to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Log in to your email
            server.sendmail(sender_email, recipient_email, msg.as_string())  # Send email
            print(f"Test email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

        
# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    print(base64.b64decode(cloud_event.data["message"]["data"]))
    print("hello world!!!!!!!!!!!!")
    send_test_email()
    

    

# if __name__ == "__main__":
#     hello_pubsub('data')
