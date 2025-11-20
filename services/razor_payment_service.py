import razorpay
import os 
from dotenv import load_dotenv
load_dotenv()


class RazorPay:
    def __init__(self):
        self.api_key = os.environ.get("RAZOR_PAY_KEY")
        self.api_key_secret = os.environ.get("RAZOR_PAY_KEY_SECRET")
        self.client = razorpay.Client(auth=(self.api_key, self.api_key_secret))
        self.client.enable_retry(True)  # Enable retry mechanism for failed API calls
        self.client.set_app_details({"title" : "AI First Academy", "version" : "1.0"})

    

class RazorpayPaymentService:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(
                os.environ.get('Live_API_Key'),
                os.environ.get('Live_Key_Secret')
            )
        )
        self.webhook_secret = os.environ.get('RAZORPAY_WEBHOOK_SECRET')
        self.domain = self._get_domain()

    def _get_domain(self):
        """Get domain for redirect URLs."""
        if os.environ.get('REPLIT_DEPLOYMENT'):
            return f"https://{os.environ.get('REPLIT_DEV_DOMAIN')}"
        elif os.environ.get('REPLIT_DOMAINS'):
            return f"https://{os.environ.get('REPLIT_DOMAINS').split(',')[0]}"
        else:
            return os.environ.get('FRONTEND_URL', 'http://localhost:3000')


    # ---------------------------------------------------------
    # 1️⃣ Create Razorpay Order
    # ---------------------------------------------------------
    def create_order(self, course, user):
        try:
            data = {
                "amount": int(float(course.price) * 100),  # INR paise
                "currency": course.currency.upper(),
                "notes": {
                    "user_id": str(user.id),
                    "course_id": str(course.id),
                    "email": user.email
                }
            }

            order = self.client.order.create(data=data)
            return order

        except Exception as e:
            raise Exception(f"Razorpay error (create_order): {str(e)}")

    # ---------------------------------------------------------
    # 2️⃣ Get order details
    # ---------------------------------------------------------
    def get_order(self, order_id):
        try:
            return self.client.order.fetch(order_id)
        except Exception as e:
            raise Exception(f"Razorpay error (get_order): {str(e)}")

    # ---------------------------------------------------------
    # 3️⃣ Verify payment signature
    # ---------------------------------------------------------
    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        try:
            params = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            }
            return self.client.utility.verify_payment_signature(params)


        except razorpay.errors.SignatureVerificationError:
            return False

        except Exception as e:
            raise Exception(f"Razorpay error (verify_payment): {str(e)}")
        
    def create_invoice(self, user, course, payment):
        try:
            invoice_data = {
                "type": "invoice",
                "description": f"Invoice for Course: {course.title}",
                "customer": {
                    "name": f"{user.first_name} {user.last_name}".strip(),
                    "contact": user.phone,        # must be 10-digit number
                    "email": user.email,
                    "billing_address": {
                        "line1": "N/A",
                        "line2": "",
                        "zipcode": "000000",
                        "city": "N/A",
                        "state": "N/A",
                        "country": "IN"
                    }
                },
                "line_items": [
                    {
                        "name": course.title,
                        "description": f"Enrollment for {course.title}",
                        "amount": int(float(course.price) * 100),  # in paise
                        "currency": course.currency.upper(),
                        "quantity": 1
                    }
                ],
                "sms_notify": True,
                "email_notify": True,
                "currency": course.currency.upper()
            }

            invoice = self.client.invoice.create(invoice_data)

            return invoice

        except Exception as e:
            raise Exception(f"Razorpay error (create_invoice): {str(e)}")


        # ---------------------------------------------------------
    # 4️⃣ Refund
    # ---------------------------------------------------------
    def create_refund(self, payment_id, amount=None):
        try:
            payload = {"payment_id": payment_id}
            if amount:
                payload["amount"] = int(amount * 100)

            refund = self.client.payment.refund(payment_id, payload)
            return refund

        except Exception as e:
            raise Exception(f"Razorpay error (refund): {str(e)}")

    # ---------------------------------------------------------
    # 5️⃣ Get payment details
    # ---------------------------------------------------------
    def get_payment(self, payment_id):
        try:
            return self.client.payment.fetch(payment_id)
        except Exception as e:
            raise Exception(f"Razorpay error (get_payment): {str(e)}")

    # ---------------------------------------------------------
    # 6️⃣ List customer payments
    # ---------------------------------------------------------
    def list_payments(self, count=10):
        try:
            return self.client.payment.all({"count": count})
        except Exception as e:
            raise Exception(f"Razorpay error (list_payments): {str(e)}")

    # ---------------------------------------------------------
    # 7️⃣ Create customer object
    # ---------------------------------------------------------
    def create_customer(self, user):
        try:
            customer = self.client.customer.create({
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "contact": user.phone,
                "notes": {
                    "user_id": user.id
                }
            })
            return customer

        except Exception as e:
            raise Exception(f"Razorpay error (create_customer): {str(e)}")

    # ---------------------------------------------------------
    # 8️⃣ Get customer
    # ---------------------------------------------------------
    def get_customer(self, customer_id):
        try:
            return self.client.customer.fetch(customer_id)
        except Exception as e:
            raise Exception(f"Razorpay error (get_customer): {str(e)}")

    # ---------------------------------------------------------
    # 9️⃣ Create subscription
    # ---------------------------------------------------------
    def create_subscription(self, plan_id, customer_id, quantity=1, total_count=12):
        try:
            subscription = self.client.subscription.create({
                "plan_id": plan_id,
                "customer_id": customer_id,
                "quantity": quantity,
                "total_count": total_count
            })
            return subscription

        except Exception as e:
            raise Exception(f"Razorpay error (create_subscription): {str(e)}")

    # ---------------------------------------------------------
    # 🔟 Cancel subscription
    # ---------------------------------------------------------
    def cancel_subscription(self, subscription_id):
        try:
            return self.client.subscription.cancel(subscription_id)
        except Exception as e:
            raise Exception(f"Razorpay error (cancel_subscription): {str(e)}")

    # ---------------------------------------------------------
    # 1️⃣1️⃣ Webhook verification
    # ---------------------------------------------------------
    def verify_webhook(self, request_body, signature):
        import hmac
        import hashlib

        generated_signature = hmac.new(
            bytes(self.webhook_secret, 'utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(generated_signature, signature)

    # ---------------------------------------------------------
    # 1️⃣2️⃣ Razorpay account balance
    # ---------------------------------------------------------
    def get_balance(self):
        try:
            return self.client.fetch_balances()

            # return self.client.misc.fetch_all_balances()
        except Exception as e:
            raise Exception(f"Razorpay error (get_balance): {str(e)}")
