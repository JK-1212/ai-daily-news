from unittest.mock import patch, MagicMock
from src.email.sender import send_email


def test_send_email_via_smtp():
    with patch("src.email.sender.smtplib.SMTP_SSL") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)
        with patch.dict("os.environ", {"GMAIL_APP_PASSWORD": "fake-password"}):
            result = send_email(
                subject="AI 日报 - 2026年03月11日 (30条)",
                html_body="<p>Test</p>",
                to_email="test@example.com",
                from_email="bot@gmail.com",
            )
    mock_server.login.assert_called_once_with("bot@gmail.com", "fake-password")
    mock_server.sendmail.assert_called_once()
    assert result is True


def test_send_email_handles_error():
    with patch("src.email.sender.smtplib.SMTP_SSL") as mock_smtp_cls:
        mock_smtp_cls.side_effect = Exception("Connection failed")
        with patch.dict("os.environ", {"GMAIL_APP_PASSWORD": "fake-password"}):
            result = send_email(
                subject="Test",
                html_body="<p>Test</p>",
                to_email="test@example.com",
                from_email="bot@gmail.com",
            )
    assert result is False


def test_send_email_missing_password():
    with patch.dict("os.environ", {}, clear=True):
        result = send_email(
            subject="Test",
            html_body="<p>Test</p>",
            to_email="test@example.com",
            from_email="bot@gmail.com",
        )
    assert result is False
