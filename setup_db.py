import sqlite3
from cryptography.fernet import Fernet

def setup_database():
    conn = sqlite3.connect('email_credentials.db')
    c = conn.cursor()

    # Create table
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_encrypted BLOB NOT NULL
        )
    ''')

    c.execute('''
        delete from email_credentials
    ''')

    # Ask user for email and password
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    
    # Encrypt the password using Fernet
    key = b'zNrfAzwA9_Nlg4ghGb9_aZ6ftkn1rTEgb6vCz7-Oy3c='  # Replace with your actual generated key
    cipher_suite = Fernet(key)
    password_encrypted = cipher_suite.encrypt(password.encode())

    # Insert the email and encrypted password into the database
    c.execute('INSERT INTO email_credentials (email, password_encrypted) VALUES (?, ?)', (email, password_encrypted))
    conn.commit()
    conn.close()

    print("Database setup complete and email credentials added.")

if __name__ == "__main__":
    setup_database()
