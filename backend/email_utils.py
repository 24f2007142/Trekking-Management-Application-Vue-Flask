import smtplib
from email.message import EmailMessage


def send_email(to_email, subject, body, html_body=None, attachment=None,
    filename=None,):

    message = EmailMessage()
    message["From"] = "noreply@hi-trek.test"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    if attachment is not None:
        message.add_attachment(
            attachment,
            maintype="text",
            subtype="csv",
            filename=filename,
        )

    with smtplib.SMTP("127.0.0.1", 1025, timeout=10) as server:
        server.send_message(message)
