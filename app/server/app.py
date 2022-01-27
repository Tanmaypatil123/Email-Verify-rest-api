from email import message
from genericpath import exists
from typing import Optional

import os

from fastapi import FastAPI

from server.database import users

from scripts.helpful_scripts import (
    validatation_email,
    send_email,
    generateAPIkey,
    present_in_users,
)

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
app = FastAPI()


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to email verfication rest api"}


@app.put("/api/v1/valid/{api_key}/{email_id}")
def validateEmail(email_id: str, api_key: str):

    p = present_in_users(api_key)

    if p:
        valid = validatation_email(email_id)
        if valid:
            return {"email": "Valid Email Address"}
        else:
            return {
                "email": 'The email address contains invalid characters before the @-sign: ".'
            }
    else:
        return {
            "Authorization": "You are not authorized api user so first get api key by making get request on /get_api_key/ endpoint"
        }


@app.put("/api/v1/email/otp/{api_key}/{email_id}")
def sendOtp_byEmail(email_id: str, api_key: str):
    valid = validatation_email(email_id)
    p = present_in_users(api_key)
    user = users.find_one({"user_key": api_key})
    exists = False
    for i in range(0, len(user["verfied_emails"])):
        if user["verfied_emails"][i]["email"] == email_id:
            exists = True

    if exists == False:
        if p:
            if valid:
                send_email(EMAIL_ADDRESS, email_id, api_key)
                return {"status": "Verfication Email is sent {}".format(email_id)}
            else:
                return {
                    "status": "The email address contains invalid characters before the @-sign "
                }
        else:
            return {
                "Authorization": "You are not authorized api user so first get api key by making get request on /get_api_key/ endpoint"
            }

    else:
        return {"Status": "Your email address is already verified"}


@app.put("/api/v1/email/verify/{api_key}/{email_id}/{otp}")
def VerifyEmail(api_key: str, otp: str, email_id: str):
    user = users.find_one(
        {
            "user_key": api_key,
        }
    )
    # start work from here
    newObject = {
        "email": email_id,
    }
    for i in range(0, len(user["unverfied_emails"])):
        if (
            user["unverfied_emails"][i]["email"] == str(email_id)
            and user["unverfied_emails"][i]["otp"] == otp
        ):
            users.update_one(
                {"user_key": api_key}, {"$push": {"verfied_emails": newObject}}
            )
            users.update_one(
                {"user_key": api_key},
                {"$pull": {"unverfied_emails": {"email": email_id}}},
            )
            return {"Status": "Verfied {}".format(email_id)}

        else:
            return {"Status": "Unable to verify {}".format(email_id)}


@app.get("/get_api_key/")
def getAPIKey():
    api_key = generateAPIkey()
    user = {
        "user_key": "{}".format(api_key),
        "verfied_emails": [],
        "unverfied_emails": [],
    }
    users.insert_one(user).inserted_id
    return {"Api key": "{}".format(api_key)}
