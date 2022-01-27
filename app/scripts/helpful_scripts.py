import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import re
import math, random
from jinja2 import Template
import secrets

from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client["EmailAPIDB"]
users = db.users
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")


def validatation_email(email_id):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if re.fullmatch(regex, email_id):
        return True
    else:
        return False


def send_email(from_, to_, api_key):
    parent_dir = "C:/Users/hp13-ay0045AU/Desktop/email_validator_rest_api/"
    dirct = "templates/email_html.html"
    path = os.path.join(parent_dir, dirct)
    msg = EmailMessage()
    msg["Subject"] = "Test email"
    msg["From"] = from_
    msg["To"] = to_
    msg.set_content("this is test email")
    html_file = open(path)
    html = html_file.read()
    tm = Template(html)
    otp = generateOTP()
    final_html = tm.render(otp=otp)
    newObject = {"email": to_, "otp": otp}
    users.update_one({"user_key": api_key}, {"$push": {"unverfied_emails": newObject}})
    msg.add_alternative(final_html, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_, EMAIL_PASSWORD)
        smtp.send_message(msg)


def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


def generateAPIkey():
    generated_key = secrets.token_urlsafe(16)
    return generated_key


def present_in_users(api_key):
    user = users.find_one({"user_key": api_key})
    try:
        if user["user_key"] == api_key:
            return True
    except TypeError:
        return False
