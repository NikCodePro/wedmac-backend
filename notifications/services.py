import requests
from django.conf import settings


class TwoFactorSettings:
    """
    Settings for 2Factor API integration.
    """
    TWOFACTOR_API_KEY = settings.TWOFACTOR_API_KEY
    DLT_TAG = settings.DLT_TAG
    def __init__(self):
        if not self.TWOFACTOR_API_KEY:
            raise ValueError("TWOFACTOR_API_KEY is not set in settings.")
        if not self.DLT_TAG:
            raise ValueError("DLT_TAG is not set in settings.")
        
class TwoFactorService:
    """Service for sending OTPs via 2Factor SMS or Voice Call.
    """

    def __init__(self,phone: str = None,otp: str = None,mode: str = "call", template_id: str = "OTP1", sender_id: str = "HEADER", message: str = None):
        self.phone = phone
        self.otp = otp
        self.mode = mode
        self.template_id = template_id
        self.sender_id = sender_id
        self.message = message
        

    def send_otp(self):
        """
        Send OTP via 2Factor SMS or Voice Call

        Args:
            phone (str): Mobile number (e.g., '919999999999')
            otp (str): OTP value to send (e.g., '123456')
            mode (str): 'call' for voice OTP or 'sms' for DLT SMS
            template_id (str): Template ID for voice OTP (default: 'OTP1')
            sender_id (str): DLT-approved sender ID for SMS (default: 'HEADER')
            message (str): Message content for SMS (required if mode='sms')

        Returns:
            dict: JSON response from 2Factor
        """
        print(f"Sending OTP to {self.phone} via {self.mode} mode.")
        tow_factor_services = TwoFactorSettings()
        if not self.phone or not self.otp:
            return {"error": "Phone number and OTP are required."}

        if self.mode == "sms":
            if not self.message:
                return {"error": "Message content is required for SMS mode."}

            payload = {
                "module": tow_factor_services.DLT_TAG,
                "apikey": tow_factor_services.TWOFACTOR_API_KEY,
                "to": self.phone,
                "from": self.sender_id,
                "msg": self.message,
            }
            url = "https://2factor.in/API/R1/"
            try:
                response = requests.post(url, data=payload, timeout=10)
                return response.json()
            except requests.RequestException as e:
                return {"error": str(e)}

        elif self.mode == "call":
            # Ensure phone starts with +91
            if not self.phone.startswith("+91"):
                phone = "+91" + self.phone
            url = f"https://2factor.in/API/V1/{settings.TWOFACTOR_API_KEY}/SMS/{self.phone}/{self.otp}/{self.template_id}"
            print(f"Calling {self.phone} with OTP {self.otp} using template {self.template_id}.")
            try:
                response = requests.get(url, timeout=10)
                return response.json()
            except requests.RequestException as e:
                return {"error": str(e)}
        else:
            return {"error": "Invalid mode. Use 'sms' or 'call'."}


    def verify_otp(self):
        """
        Verify OTP using 2Factor.

        Args:
            phone (str): Mobile number
            otp (str): OTP to verify

        Returns:
            dict: Response JSON
        """
        print(f"Verifying OTP {self.otp} for phone {self.phone}.")
        url = f"https://2factor.in/API/V1/{settings.TWOFACTOR_API_KEY}/SMS/VERIFY3/{self.phone}/{self.otp}"
        try:
            response = requests.get(url, timeout=10)
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}

 

class NotificationService:

    def __init__(self,messages: list = None):
        self.two_factor_settings = TwoFactorSettings()
        self.messages = messages if messages else []

    def send_notifications(self):
        """
        Send bulk SMS using 2Factor's Bulk API.

        :param messages: List of dicts with keys - smsFrom, smsTo, smsText
        :return: Response JSON from 2Factor
        """
        if not self.messages:
            return {"error": "No messages to send."}
        url = "https://2factor.in/API/R1/Bulk/"
        payload = {
            "module": "TRANS_SMS",
            "apikey": self.two_factor_settings.TWOFACTOR_API_KEY,
            "messages": self.messages
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.json()