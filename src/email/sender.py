import logging
import os

import resend

logger = logging.getLogger(__name__)


def send_email(subject: str, html_body: str, to_email: str, from_email: str) -> bool:
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send(
            params={
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_body,
            }
        )
        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
