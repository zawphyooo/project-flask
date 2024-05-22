import sqlite3
from flask_mail import Message, Mail
from app import app
from cryptography.fernet import Fernet

# Define the encryption key directly in the code
key = b'zNrfAzwA9_Nlg4ghGb9_aZ6ftkn1rTEgb6vCz7-Oy3c='  # Replace with your actual generated key
cipher_suite = Fernet(key)

def get_email_credentials():
    conn = sqlite3.connect('email_credentials.db')
    c = conn.cursor()
    
    c.execute('SELECT email, password_encrypted FROM email_credentials LIMIT 1')
    result = c.fetchone()
    conn.close()
    
    if result:
        email, password_encrypted = result
        password = cipher_suite.decrypt(password_encrypted).decode()
        print(f"Admin Email: {email}")
        return email, password
    return None, None

def send_email(subject, recipients, text_body, html_body):
    email, password = get_email_credentials()
    if not email or not password:
        print("Email credentials not found!")
        return "Email credentials not found!", 500

    # Update app config with retrieved credentials
    app.config.update(
        #MAIL_SERVER='smtp.office365.com',
        #MAIL_PORT=587,
        #MAIL_USE_TLS=True,
        #MAIL_USE_SSL=False,
        MAIL_USERNAME=email,
        MAIL_PASSWORD=password
    )

    # Initialize a new Mail instance with the updated app config
    mail_instance = Mail(app)

    with app.app_context():
        try:
            msg = Message(subject, sender=email, recipients=recipients)
            msg.body = text_body
            msg.html = html_body
            mail_instance.send(msg)
            print("Email sent successfully.")
            return "Email sent successfully.", 200
        except Exception as e:
            print("Failed to send email.")
            print("Error:", e)
            return f"Failed to send email. Error: {e}", 500
