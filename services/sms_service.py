from twilio.rest import Client
import os
from dotenv import load_dotenv
load_dotenv()




class SmsService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
        self.verify_service_sid = os.getenv("TWILIO_VERIFY_SID", "VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.from_whatsapp = "whatsapp:+14155238886"  # Twilio Sandbox Number
        self.client = Client(self.account_sid, self.auth_token)


    
    def send_otp(self,phone_number):
        verification = self.client.verify.v2.services(self.verify_service_sid).verifications.create(
            to=phone_number,
            channel='sms'  # or 'call' for voice OTP
      )
        print(f"OTP sent to {phone_number}, status: {verification.status}")
        return verification.status 

    
    
    def verify_otp(self,phone_number, code):
        verification_check = self.client.verify.v2.services(self.verify_service_sid).verification_checks.create(
            to=phone_number,
            code=code
        )
        print(f"Verification status: {verification_check.status}")
        return verification_check.status 


    def send_whatsapp_notification(self, to_number, message_body):
        """Send a WhatsApp notification"""
        try:
            message = self.client.messages.create(
                from_=self.from_whatsapp,
                body=message_body,
                to=f"whatsapp:{to_number}"
            )
            print(f"✅ WhatsApp message sent to {to_number}, SID: {message.sid}")
            return {"sid": message.sid, "status": "sent"}
        except Exception as e:
            print("❌ Error sending WhatsApp message:", e)
            return {"error": str(e)}



    

# # Example route
 
# if __name__ == "__main__":
#     sms = SmsService()
#     phone = "+916300232040"  # Must match the number used in send_otp

# #     # sms.send_otp(phone)

# #     # otp_code = input("Enter the OTP you received: ")
# #     # sms.check_otp(phone, otp_code)


#     sms.send_whatsapp_notification(to_number=phone,message_body="Hello From Aim Technologies, \n this is test message")
