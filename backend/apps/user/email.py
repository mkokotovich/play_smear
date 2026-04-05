import logging
import os

import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

LOG = logging.getLogger(__name__)


def send_password_reset_email(to, reset_token):
    LOG.info(f"Sending password reset email to: {to}")
    return send_password_reset_email_mailgun(to, reset_token)


def send_password_reset_email_mailgun(to, reset_token):
    url = f"https://playsmear.com/#/reset?email={to}&token={reset_token}"
    html_content = f"""
<h2>
Play Smear Password Reset
</h2>
<p>
<a href="{url}">Click Here</a> to reset your password, or copy and paste {url} into your browser
</p>

<p>
<a href="https://playsmear.com">Unsubscribe</a>
</p>
<br/><br/>
    """
    text_content = f"""
Play Smear Password Reset

Copy and paste {url} into your browser to reset your password
"""

    try:
        response = requests.post(
            "https://api.mailgun.net/v3/mg.playsmear.com/messages",
            auth=("api", os.getenv("MAILGUN_API_KEY", "API_KEY")),
            data={
                "from": "support@playsmear.com",
                "to": to,
                "subject": "Password Reset for playsmear.com",
                "text": text_content,
                "html": html_content,
            }
        )
        response.raise_for_status()
    except Exception as ex:
        body = getattr(ex, "body", "unknown error")
        LOG.exception(f"Unable to send password reset email: {body}")
        raise

    return True


def send_password_reset_email_sendgrid(to, reset_token):

    url = f"https://playsmear.com/#/reset?email={to}&token={reset_token}"

    message = Mail(
        from_email="support@playsmear.com",
        to_emails=to,
        subject="Password Reset for playsmear.com",
        html_content=f"""
<h2>
Play Smear Password Reset
</h2>
<p>
<a href="{url}">Click Here</a> to reset your password, or copy and paste {url} into your browser
</p>

<p>
<a href="https://playsmear.com">Unsubscribe</a>
</p>
<br/><br/>
        """,
    )

    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)

    except Exception as ex:
        body = getattr(ex, "body", "unknown error")
        LOG.exception(f"Unable to send password reset email: {body}")
        raise

    success_codes = [200, 202]
    if response.status_code not in success_codes:
        # TODO: Add logging
        LOG.error(f"Unable to send password reset email. Status code: {response.status_code}, body: {response.body}")
        raise Exception("Unable to send password reset email")

    return response.status_code in success_codes
