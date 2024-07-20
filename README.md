# A Flask Server with Enhanced Security
#### Description

## Overview
#### This project is based on the Week 9 Flask problem set and I have integrated the following additional features to enhance security and allow the user to manage their profile.
+ **User Registration with email verification:**
 Users will register and verify their accounts through a link with token sent to their email, allowing them to complete the registration upon clicking the link.

+ **Two-Factor Authentication (2FA):** A 2FA system is implemented for enhanced security.

+ **User Profile Management:** 
Users will have access to their information and settings to enable OTP and update their passwords.

+ **Forgot Password:**
The landing page will have a "Forgot Password" button. When clicked, it will prompt the user to enter their email address. The system will then send a link with a token to the user's email, allowing them to reset their password upon clicking the link.

## Project File Structure
This project includes the following files.

```
├── README.md
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── email.py
│   ├── helpers.py
│   ├── main.py
│   ├── otp.py
│   ├── static
│   │   ├── I_heart_validator.png
│   │   ├── favicon.ico
│   │   └── styles.css
│   └── templates
│       ├── apology.html
│       ├── buypage.html
│       ├── changepass.html
│       ├── forgetpass.html
│       ├── history.html
│       ├── index.html
│       ├── layout.html
│       ├── login.html
│       ├── mfa.html
│       ├── profile.html
│       ├── quote.html
│       ├── quoted.html
│       ├── register.html
│       ├── reset_password.html
│       ├── sell.html
│       └── verifyMailSent.html
├── email_credentials.db
├── file.txt
├── finance.db
├── flask_session
├── flaskenv
│   ├── bin
│   ├── lib
│   └── pyvenv.cfg
├── requirements.txt
├── run_flask_mac.sh
└── setup_db_for_admin_email
````
## Detailed explaination of implementation

### Flask Application: Py files

**`__init__.py`** - file initialized the Flask application and configures essential extensions like Flask-Mail and Flask-Session. It sets up the basic framework for the app, imports the required libaries and mocules, and configure the app using the config.py file. This make sure that database connections are established and helper functions are registered. By using the seperate file for setup, the project maintains a clean and organized structure, making it easy to manage and scale. 

**`config.py`** - file contains configuration settings for the application including secret keys, database location, and mail server settings. This setup allows easy adjustments to the application settings by keeping the configuration details centralized and easily manageable.

**`email.py`** - file handles email-related functionalities. It includes cryptographic functions to ensure secure email communications. The file connects to an SQLite database "email_credentials.db" to fetch stored email credentials, decrypts the encrypted admin email stored in the database using "fernet" encryption, and updates the Flask app configuration with the received email and password. the "send_email" function sends email within the app context, and the "generate_token" function creates unique tokens for email verification and password reset processes. By seperating email functionalities into it own module, the project follows the "Single responsibility principle", making the code more readable and easier to maintain.

**`helper.py`** - file provides utility functions used across the application. Consolidating these helper functions into one file promotes code reuse and avoids duplication, adhering to the DRY (Don't Repeat Yourself) principle, making codebase more efficient and easier to maintain. I didn't modified this file and used as it was provided in the problem set. 

**`main.py`** - file contains the core routes and logic for user registration, login, email verification, OTP verification, password management and profile management. It defines endpoints for these actions and handles the interaction between the user and the server.
+ Email Verification : There is 'verified' column in the 'users' table for checking if the user email is already verified or not. User needs to verify the email during the registration process. If user haven't verified the registered email and try to login, the application will send the verification email again and ask user to complete the registration.
+ Forgot Password : User can easily reset the password by clicking the "Forgot Password" button in login page. The Application will send the password reset link to user's email to reset the password.

**`otp.py`** - file manages the generation and verification of OTPs (One Time Passwords), adding an extra layer of security to the application. The "generate_otp" function generate the random OTP and then the "store_otp" function store the generated OTP into the database along with the created timestamp. The "validate_otp" function validate the otp generated for specific user with the default expiry_minutes value 5 minutes. If user enter the OTP later than 5 minutes would return False. By handling OTP functionalities in a dedicated module, the project maintains a modulat structure, making it easier to extend or modify the OTP features in the future.

### Flask Application: Frontend

The frontend of the application is built using HTML, JavaScript and CSS.

+ **Html Templates:**
The templates folder contains various HTML files that structure the different pages of the appliation, such as registration, login, OTP Key in, user profile, and password reset pages.

+ **JavaScript:**
JavaScript is used to enhance interactivity on the frontend. For example, it is used to:
    + check if the user input is not empty and using correct format
    + toggle password visibility with an eye button, allowing users to see the password they are typing. 

+ **CSS:**
The style.css file in the static folder contains custom styles to improve the visual appearance of the application.



