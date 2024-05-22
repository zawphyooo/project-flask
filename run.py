# run.py
from app import app
from app.email import send_email

@app.route('/send-email')
def send_test_email():
    message, status_code = send_email(
        'Test Email 2',
        recipients=['achemede@gmail.com'],
        text_body='This is a test email sent from a Flask application!',
        html_body='<p>This is a <b>test</b> email sent from a Flask application!</p>'
    )
    return message, status_code

if __name__ == '__main__':
    app.run(debug=False)
