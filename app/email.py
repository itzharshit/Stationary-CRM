from flask_mail import Message
from app import mail

def send_order_confirmation(order):
    msg = Message('Order Confirmation', sender='noreply@example.com', recipients=[order.customer.email])
    msg.body = f"Your order {order.id} has been received and is being processed."
    mail.send(msg)
