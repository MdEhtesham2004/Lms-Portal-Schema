# services/notification_service.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Content, HtmlContent, PlainTextContent, Email
from typing import Optional
import os 
from dotenv import load_dotenv
load_dotenv()

class EmailService:
    def __init__(self):
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        if not self.api_key:
            raise RuntimeError("SENDGRID_API_KEY not set")
        self.sg = SendGridAPIClient(self.api_key)
        self.from_email = os.environ.get("FROM_EMAIL", "no-reply@example.com")
        self.frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")

    def _send(self, to_email: str, subject: str, plain_text: str, html: Optional[str] = None, template_id: Optional[str] = None, dynamic_data: dict = None):
        """
        Core send wrapper.
        - template_id + dynamic_data: use dynamic template (recommended)
        - otherwise include inline html
        """
        message = Mail(
            from_email=From(self.from_email),
            to_emails=To(to_email),
            subject=subject
        )

        # prefer template if provided
        if template_id:
            message.template_id = template_id
            if dynamic_data:
                message.dynamic_template_data = dynamic_data
        else:
            # add both plain and html content
            message.add_content(PlainTextContent(plain_text))
            if html:
                message.add_content(HtmlContent(html))

        try:
            resp = self.sg.send(message)
            # resp.status_code 202 -> accepted
            return {"status_code": resp.status_code, "body": resp.body, "headers": dict(resp.headers)}
        except Exception as e:
            # log error appropriately in production
            return {"error": str(e)}

    # --- Example convenience methods ---
    def send_welcome_email(self, user):
        subject = "Welcome to AI First Academy!"
        plain = f"Dear {user.first_name},\n\nWelcome to AI First Academy! Your account: {user.email}\n\nBest,\nAI First Team"
        html = f"<p>Dear {user.first_name},</p><p>Welcome to <strong>AI First Academy</strong>! Your account: <strong>{user.email}</strong></p>"
        # If you have a dynamic template, set template_id and dynamic_data instead
        return self._send(user.email, subject, plain, html)

    def send_password_reset(self, user, reset_token):
        subject = "Password Reset - AI First Academy"
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
        plain = f"Hello {user.first_name},\nReset here: {reset_url}\nThis link expires in 1 hour."
        html = f"""<p>Hello {user.first_name},</p>
                   <p>Click <a href="{reset_url}">Reset Password</a>. This link expires in 1 hour.</p>"""
        return self._send(user.email, subject, plain, html)

    def send_enrollment_confirmation(self, user, course):
        subject = f"Enrollment Confirmed: {course.title}"
        plain = f"Hi {user.first_name},\nYou've enrolled in {course.title}."
        html = f"<p>Hi {user.first_name},</p><p>You've enrolled in <strong>{course.title}</strong>.</p>"
        return self._send(user.email, subject, plain, html)


class MockUser:
    def __init__(self, first_name, last_name, email):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

class MockCourse:
    def __init__(self, title):
        self.title = title

if __name__ == "__main__":
    user = MockUser("Ehtesham", "Mohammed", "admin@aimtechnologies.in")
    course = MockCourse("Python for AI and ML")

    email_service = EmailService()

    # Test different messages:
    print(email_service.send_welcome_email(user))
    print(email_service.send_password_reset(user, reset_token="abcd1234"))
    print(email_service.send_enrollment_confirmation(user, course))
