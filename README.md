# Quick Notes
## Video Demo: https://youtu.be/1DHAi41Fbcs
## This is a simple note taking web application
####
#### The Project contains the following files.
#### 7 x html file (+1 layout page) To display info to the user. Some styling done with bootstrap.
#### 3 x python applications to handle various tasks within the app.
#### 1 x database file.
#### A static folder contains an image for the background and some CSS styling of the web app.

## HTML pages
#### 1. Login. This is the login page for the user to log into the web app
#### 2. Register. This is where the user will register to use the web application. The user's login data is saved to a database (Username, email address used for login, hash of the users password)
#### 3. Index. This page will greet the user by name and this is where the users notes will be displayed and where they can add new notes. Notes can also be removed by clicking the x button inline with the note.
#### 4. History. This is just a page for the user to see removed notes. This may not be neccesary but I thought this would be a nice touch for users to be able to see past notes if they so choose.
#### 5. Password reset request. Should the user have forgotten their password the can request a password reset. The mail.py will handle this by creating a random time stamped token and send it to the users email address provided the email address is one the user used to register. The user will then be sent a clickable link to reset their passwords.
#### 6. password Reset. Once the user clicks on the link that was sent the webapp will validate the token and the time to ensure it has been clicked before the timer has expired (10 Minutes) Should the timer have expired the user will need to submit a new password reset request. If the validation passes the user will be directed to the password reset page where they can enter a new password. After this they will be redirected to the login page to login with their new password.
#### 7. Error. This page displays any errors when the validation has failed with a short descriptive error message such as failed login, passwords missmatch or invalid email address (e.g if user entered peter.com this would be considered invalid email address).
#### 8. Layout. This is the general layout of the website and these extends to the other pages using Jinja syntax.
####
### Python Files
#### 1. app.py. This is the main application handling the routes & most validation checks
#### 2. helpers.py. This file also helps with validation and also helps to display pages only to users that are logged in where applicable. This also assist with displaying the error messages on the error.html page
#### 3. mail.py. This app deals with the links that need to be sent to a user whan a password is forgotten.
####
### Database file
#### 1. notes.db contains 2 tables. one table (users) for user login details with reset tokens and timer to reset password if forgotten and one table (notes) for the users notes.
