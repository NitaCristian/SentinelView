import uuid
from datetime import datetime
import smtplib
from models import User, Camera, Event, Footage, Notification, db
from email.mime.text import MIMEText

subject = "Alert! SentinelView detected new movement!"

sender = "cristiannita24@gmail.com"

password = "vclc hzqy bzeb brjl"  # Replace with your app-specific password


def get_body(event_id):
    body = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Motion Detected Alert</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f7f7f7;
            margin: 0;
            padding: 0;
            color: #333333;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }

        .header {
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
        }

        .header h1 {
            margin: 0;
            font-size: 24px;
        }

        .content {
            padding: 20px;
        }

        .content h2 {
            font-size: 20px;
            margin-top: 0;
        }

        .content p {
            font-size: 16px;
            line-height: 1.5;
        }

        .content .alert {
            background-color: #ffdddd;
            border-left: 6px solid #f44336;
            padding: 10px;
            margin: 20px 0;
            border-radius: 5px;
        }

        .footer {
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #888888;
        }

        .footer p {
            margin: 0;
        }

        .button {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }

        .button:hover {
            background-color: #45a049;
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <h1>Motion Detected!</h1>
        </div>
        <div class="content">
            <h2>Attention!</h2>
            <p>We have detected motion in your surveillance area at <strong>[TIME]</strong> on <strong>[DATE]</strong>.</p>
            <div class="alert">
                <p><strong>Alert:</strong> Motion has been detected by the camera system. Please review the footage
                    immediately.</p>
            </div>
            <p>You can view the live feed or check the recorded footage by clicking the button below:</p>
            <p><a href="localhost:5000/event/[ID]" class="button">View Surveillance Feed</a></p>
            <p>Stay alert and stay safe.</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 SentinelView. All rights reserved.</p>
        </div>
    </div>
</body>

</html>
"""
    body = body.replace("[DATE]", datetime.now().date().strftime("%Y-%m-%d"))
    body = body.replace("[TIME]", datetime.now().time().strftime("%H:%M:%S"))
    body = body.replace("[ID]", str(event_id))
    return body


def send_email(recipients, event_id):
    msg = MIMEText(get_body(event_id), 'html')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())


def send_notifications(event_id):
    users = User.query.all()
    recipients = [user.email for user in users]
    send_email(recipients, event_id)
