# paymentgateway/razorpay_client.py

import razorpay

# Replace these with your actual Razorpay test keys
RAZORPAY_KEY_ID = 'rzp_test_l7Py4KSkXnLSgC'
RAZORPAY_KEY_SECRET = 'I4eHRaAOY8fnVaMH5lCXqMxP'

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def verify_razorpay_signature(data, signature, order_id):
    import hmac
    import hashlib

    generated_signature = hmac.new(
        RAZORPAY_KEY_SECRET.encode(),
        f"{order_id}|{data}".encode(),
        hashlib.sha256
    ).hexdigest()

    return generated_signature == signature
