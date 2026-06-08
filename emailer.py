"""
Emailer — sends the HTML digest via Gmail SMTP.
Uses environment variables for credentials (set as GitHub Secrets).

Setup:
  1. Enable 2FA on your Gmail account
  2. Go to Google Account → Security → App Passwords
  3. Create an App Password for "Mail"
  4. Add to GitHub Secrets:
       SMTP_USER = your.email@gmail.com
       SMTP_PASS = your-16-char-app-password
       EMAIL_TO  = recipient@example.com  (can be same as SMTP_USER)
"""

import smtplib
import os
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_digest(html_path: str, md_path: str) -> bool:
    """
    Send the HTML digest as an email.
    Returns True on success, False on failure.
    """
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    email_to  = os.environ.get("EMAIL_TO", smtp_user)

    if not smtp_user or not smtp_pass:
        print("[Email] SMTP_USER or SMTP_PASS not set — skipping email.")
        return False

    today = datetime.date.today().isoformat()

    # Read the HTML body
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_body = f.read()
    except FileNotFoundError:
        print(f"[Email] HTML file not found: {html_path}")
        return False

    # Read the plain-text fallback
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            text_body = f.read()
    except FileNotFoundError:
        text_body = "See attached HTML digest."

    # Build email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"💊 Pharma Digest — {today}"
    msg["From"]    = smtp_user
    msg["To"]      = email_to

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html",  "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"[Email] Sent digest to {email_to}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[Email] Authentication failed — check SMTP_USER and SMTP_PASS (use App Password, not account password)")
        return False
    except Exception as e:
        print(f"[Email] Failed to send: {e}")
        return False
