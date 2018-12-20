import sendgrid
import os
from sendgrid.helpers.mail import Email, Content, Mail


def send_password_reset_email(to, reset_token):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("mkokotovich@gmail.com")
    subject = "Password Reset for playsmeartest.herokuapp.com"
    to_email = Email(to)
    url = f"https://playsmeartest.herokuapp.com/#/reset?email={to}&token={reset_token}"
    body = f"""
<a href="{url}">Click Here</a> to reset your password, or copy and paste {url} into your browser

<a href="https://playsmeartest.herokuapp.com">Unsubscribe</a>
"""
    content = Content("text/html", body)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    success_codes = [200, 202]
    if response.status_code not in success_codes:
        # TODO: Add logging
        print(response.status_code)
        print(response.body)
        print(response.headers)
    return response.status_code in success_codes
