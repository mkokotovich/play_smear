import logging
import os
from urllib.parse import quote

import requests
import resend


LOG = logging.getLogger(__name__)
resend.api_key = os.environ.get("RESEND_API_KEY", "default")


def send_password_reset_email(to, reset_token):
    LOG.info(f"Sending password reset email to: {to}")
    return send_password_reset_email_resend(to, reset_token)


def send_password_reset_email_resend(to, reset_token):
    encoded_email = quote(to)
    url = f"https://playsmear.com/#/reset?email={encoded_email}&token={reset_token}"
    html_content = f"""
<html>
<head></head>
<body>
<h2>
Play Smear Password Reset
</h2>
<p>
<a href="{url}">Click Here</a> to reset your password, or copy and paste {url} into your browser
</p>
<br/><br/>
</body>
</html>
    """

    params: resend.Emails.SendParams = {
        "from": "Playsmear Support <support@playsmear.com>",
        "to": [to],
        "subject": "Password Reset for playsmear.com",
        "html": html_content,
    }

    try:
        email = resend.Emails.send(params)
        LOG.info(f"successfully sent password reset: {email}")
    except Exception as e:
        LOG.exception(f"Unable to send password reset email: {email}")
        raise
    return True


def send_password_reset_email_brevo(to, reset_token):
    brevo_url = "https://api.brevo.com/v3/smtp/email"
    url = f"https://playsmear.com/#/reset?email={to}&token={reset_token}"
    html_content = f"""
<html>
<head></head>
<body>
<h2>
Play Smear Password Reset
</h2>
<p>
<a href="{url}">Click Here</a> to reset your password, or copy and paste {url} into your browser
</p>
<br/><br/>
</body>
</html>
    """

    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "Playsmear Support",
            "email": "support@playsmear.com"
        },
        "to": [{"email": to}],
        "subject": "Password Reset for playsmear.com",
        "htmlContent": html_content,
    }

    try:
        response = requests.post(brevo_url, headers=headers, json=payload)
        response.raise_for_status()
    except Exception as ex:
        body = getattr(ex, "body", "unknown error")
        LOG.exception(f"Unable to send password reset email: {body}")
        raise

    return True


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
