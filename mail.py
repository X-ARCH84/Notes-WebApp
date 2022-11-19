import requests
import uuid
import datetime
from flask import request
from cs50 import SQL


db = SQL("sqlite:///note.db")

# Make random uuid
token = str(uuid.uuid4())
#print(uuid.uuid4())

def send_mail():
	"""Send mail to user"""

	url = "https://rapidprod-sendgrid-v1.p.rapidapi.com/mail/send"

	# Database query to get username
	email = request.form.get('email')
	# Get username
	username_query = db.execute("SELECT username FROM users WHERE email = ?", email)
	username = username_query[0]["username"]
	# date time stamp to set timer on reset link
	timer = datetime.datetime.now()

	# Update DB set token & timestamp created
	db.execute("UPDATE users SET reset_token = ?, token_timer = ? WHERE username = ?", token, timer, username)

	payload = {
		"personalizations": [
			{
				"to": [{"email": email}],
				"subject": "Password reset request!"
			}
		],
		"from": {"email": "note.app.mg@gmail.com"},
		"content": [
			{
				"type": "text/plain",
				# Text to user stating request was made to reset password
				"value": """Hi """ + username + """,

You have requested a password reset. Please follow this link!

http://127.0.0.1:5000/password-reset?token=""" + token + """

This link is valid for 10 minutes!

Quick Note App Team"""
			}
		]
	}
	headers = {
		"content-type": "application/json",
		"X-RapidAPI-Key": "3925aba566mshefa758aa0046c1fp10fd42jsnbdd5ab5540f3",
		"X-RapidAPI-Host": "rapidprod-sendgrid-v1.p.rapidapi.com"
	}

	response = requests.request("POST", url, json=payload, headers=headers)

	print(response.text)