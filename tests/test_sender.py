from unittest.mock import patch, MagicMock
from src.email.sender import send_email


def test_send_email_calls_resend():
    with patch("src.email.sender.resend") as mock_resend:
        mock_resend.Emails.send.return_value = {"id": "email-123"}
        result = send_email(
            subject="AI 日报 - 2026年03月11日 (30条)",
            html_body="<p>Test</p>",
            to_email="test@example.com",
            from_email="bot@example.com",
        )
    mock_resend.Emails.send.assert_called_once()
    call_args = mock_resend.Emails.send.call_args
    assert call_args[1]["params"]["to"] == ["test@example.com"]
    assert result is True


def test_send_email_handles_error():
    with patch("src.email.sender.resend") as mock_resend:
        mock_resend.Emails.send.side_effect = Exception("API error")
        result = send_email(
            subject="Test",
            html_body="<p>Test</p>",
            to_email="test@example.com",
            from_email="bot@example.com",
        )
    assert result is False
