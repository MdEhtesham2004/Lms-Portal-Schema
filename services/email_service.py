import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
load_dotenv()
from services.sms_service import SmsService
# from sms_service import SmsService
from bs4 import BeautifulSoup
sms_service = SmsService()

def html_to_text(html_content: str) -> str:
    """Convert HTML to plain text using BeautifulSoup"""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return text



class EmailService:
    def __init__(self):
        self.sender = os.environ.get('FROM_EMAIL', 'admin@aimtechnologies.in')
        self.SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
     # ✅ Universal SendGrid email function
    def send_email(self, to_email, subject, body, html_body=None,include_whatsapp_msg=False,user=None,whatsapp_msg=None):

        """
        Send an email using SendGrid Web API.
        """
        try:
            html_content = html_body if html_body else f"<pre>{body}</pre>"

            message = Mail(
                from_email=self.sender,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )

            print(f"📤 Sending email from: {self.sender} to: {to_email}")
            print(f"📧 Subject: {subject}")

            sg = SendGridAPIClient(self.SENDGRID_API_KEY)
            response = sg.send(message)
            
            send_response = {
                "email_response":{
            "SendGrid status:": response.status_code,
            "Response headers": response.headers,
            "Response body ": response.body.decode() if response.body else None
                
            }
            }
            print("✅ SendGrid status:", response.status_code)
            print("✅ Response headers:", response.headers)
            print("✅ Response body:", response.body.decode() if response.body else None)
            
            
            if include_whatsapp_msg:
                whatsapp_response = sms_service.send_whatsapp_notification(to_number=user.phone,message_body=html_to_text(whatsapp_msg))
                send_response["whatsapp_response"] = whatsapp_response

            if response.status_code == 202:
                print("✅ Email accepted by SendGrid (queued for delivery)")
                
                return {"response": send_response, "status":True}
            else:
                print("⚠️ SendGrid rejected the email — check logs above")
                return False

        except Exception as e:
            print("❌ SendGrid Exception:", str(e))
            return False

    

    # def send_email(self, recipient, subject, body, html_body=None):
    #     """Send email using Flask-Mail"""
    #     try:
    #         msg = Message(
    #             subject=subject,
    #             sender=self.sender,
    #             recipients=[recipient] if isinstance(recipient, str) else recipient
    #         )
    #         msg.body = body
    #         if html_body:
    #             msg.html = html_body
            
    #         mail.send(msg)
    #         return True
    #     except Exception as e:
    #         print(f"Failed to send email to {recipient}: {str(e)}")
    #         return False
    
    def send_welcome_email(self, user):
        """Send welcome email to new users"""
        subject = "Welcome Python Training Management System!"
        
        body = f"""
Dear {user.first_name},

Welcome to AI First Academy! We're excited to have you join our community of AI enthusiasts and learners.

Your account has been successfully created with the email: {user.email}

What's next?
- Browse our course catalog to find courses that interest you
- Complete your profile to get personalized recommendations
- Join our community forums to connect with other learners

If you have any questions, feel free to reach out to our support team.

Best regards,
The AI First  AI First Academy
"""
        
        html_body = f"""
<html>
<body>
<h2>Welcome to AI First Academy!</h2>

<p>Dear {user.first_name},</p>

<p>Welcome to AI First Academy! We're excited to have you join our community of AI enthusiasts and learners.</p>

<p>Your account has been successfully created with the email: <strong>{user.email}</strong></p>

<h3>What's next?</h3>
<ul>
    <li>Browse our course catalog to find courses that interest you</li>
    <li>Complete your profile to get personalized recommendations</li>
    <li>Join our community forums to connect with other learners</li>
</ul>

<p>If you have any questions, feel free to reach out to our support team.</p>

<p>Best regards,<br>
The AI First Academy</p>
</body>
</html>
"""
        resp_email = self.send_email(user.email, subject, body, html_body,include_whatsapp_msg=True,user=user,whatsapp_msg=html_body)

        return{
            "response":resp_email
        }


    def send_notification_email(self, user, title, message):
        """Send general notification email"""
        subject = f"AI First The AI First Academy: {title}"

        body = f"""
Dear {user.first_name},

{message}

Best regards,
The AI First Academy Team
        """

        html_body = f"""
<html>
<body>
<h2>{title}</h2>

<p>Dear {user.first_name},</p>

<p>{message}</p>

<p>Best regards,<br>
The AI First Academy Team</p>
</body>
</html>
        """

        return self.send_email(user.email, subject, body, html_body,include_whatsapp_msg=True,user=user,whatsapp_msg=html_body)

    def send_password_reset_email(self, user, reset_token):
        """Send password reset email"""
        subject = "Password Reset - AI First Academy"

        reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"

        body = f"""
Dear {user.first_name},

We received a request to reset your password for your AI First Academy account.

If you requested this password reset, please click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you did not request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
The AI First Academy Team
        """

        html_body = f"""
<html>
<body>
<h2>Password Reset Request</h2>

<p>Dear {user.first_name},</p>

<p>We received a request to reset your password for your AI First Academy account.</p>

<p>If you requested this password reset, please click the link below to reset your password:</p>
<p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>

<p>This link will expire in 1 hour for security reasons.</p>

<p>If you did not request a password reset, please ignore this email and your password will remain unchanged.</p>

<p>Best regards,<br>
The AI First Academy Team</p>
</body>
</html>
        """

        return self.send_email(user.email, subject, body, html_body,include_whatsapp_msg=True,user=user,whatsapp_msg=html_body)


    def send_live_session_notification(self, user, course, session):
        """Send email notification for a scheduled live session"""

        subject = f"📢 Live Session Reminder: {session.title} - {course.title}"

        # Format date and time nicely
        session_time = session.start_time.strftime("%A, %d %B %Y at %I:%M %p") if hasattr(session, 'start_time') else "TBA"
        meeting_link = getattr(session, 'meeting_link', '#')

        body = f"""
Dear {user.first_name},

We’re excited to invite you to an upcoming live session for your course **{course.title}**.

🗓 **Session Title:** {session.title}
📅 **Date & Time:** {session_time}
🎯 **Instructor:** {getattr(session, 'instructor_name', 'Your Mentor')}
🔗 **Join Link:** {meeting_link}

Don’t miss this opportunity to learn, interact, and ask your questions live!

Best regards,  
The AI First Academy Team
        """

        html_body = f"""
<html>
<body>
<h2 style="color: #007bff;">Live Session Reminder</h2>

<p>Dear {user.first_name},</p>

<p>We’re excited to invite you to an upcoming live session for your course <strong>{course.title}</strong>.</p>

<table style="border-collapse: collapse; margin-top: 10px;">
<tr><td><strong>🗓 Session Title:</strong></td><td>{session.title}</td></tr>
<tr><td><strong>📅 Date & Time:</strong></td><td>{session_time}</td></tr>
<tr><td><strong>🎯 Instructor:</strong></td><td>{getattr(session, 'instructor_name', 'Your Mentor')}</td></tr>
</table>

<p style="margin-top: 15px;">Join the session here:</p>
<p><a href="{meeting_link}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Join Live Session</a></p>

<p style="margin-top: 20px;">Don’t miss this opportunity to learn, interact, and ask your questions live!</p>

<p>Best regards,<br>
The <strong>AI First Academy Team</strong></p>
</body>
</html>
        """

        return self.send_email(user.email, subject, body, html_body,include_whatsapp_msg=True,user=user,whatsapp_msg=html_body)

    def send_enrollment_confirmation(self, user, course):
        """Send email confirmation when user enrolls in a course"""
        subject = f"🎉 Enrollment Confirmed: {course.title}"

        body = f"""
Dear {user.first_name},

Congratulations! You have successfully enrolled in the course **{course.title}**.

Course Details:
- Title: {course.title}
- Instructor: {getattr(course, 'instructor_name', 'Your Mentor')}
- Duration: {getattr(course, 'duration', 'N/A')}
- Start Date: {getattr(course, 'start_date', 'To be announced')}

We’re excited to have you on board. You can now access your course materials and upcoming live sessions in your dashboard.

Happy Learning!  
The AI First Academy Team
        """

        html_body = f"""
<html>
<body>
<h2 style="color:#007bff;">🎉 Enrollment Confirmed!</h2>

<p>Dear {user.first_name},</p>

<p>Congratulations! You have successfully enrolled in the course <strong>{course.title}</strong>.</p>

<h3>📘 Course Details:</h3>
<ul>
  <li><strong>Instructor:</strong> {getattr(course, 'instructor_name', 'Your Mentor')}</li>
  <li><strong>Duration:</strong> {getattr(course, 'duration', 'N/A')}</li>
  <li><strong>Start Date:</strong> {getattr(course, 'start_date', 'To be announced')}</li>
</ul>

<p>You can now access your course materials and join upcoming live sessions through your dashboard.</p>

<p>We’re excited to have you on board! 🚀</p>

<p>Best regards,<br>
The <strong>AI First Academy Team</strong></p>
</body>
</html>
        """

        return self.send_email(user.email, subject, body, html_body,include_whatsapp_msg=True,user=user,whatsapp_msg=html_body)




# # Dummy User class to simulate a real user object
# class User:
#     def __init__(self, first_name, email, phone):
#         self.first_name = first_name
#         self.email = email
#         self.phone = phone

# if __name__ == "__main__":
#     email_service = EmailService()
#     # test_email_whatsapp.py



#     # Create a test user
#     test_user = User(
#         first_name="Ehtesham",
#         email="mohammed.ehtesham@aimtechnologies.in",
#         phone="+916300232040"  # replace with your WhatsApp sandbox verified number
#     )

#     # response = email_service.send_email(to_email="mohammed.ehtesham@aimtechnologies.in",subject="Here is the test Message from Twilio" ,
#     #                         body=f"Welcome to AI First Academy, \n here is the test message.",include_whatsapp_msg=True,user=test_user,
#     #                         whatsapp_msg="Welcome to AI First Academy")
#     response = email_service.send_welcome_email(user=test_user)
    
#     print(response)