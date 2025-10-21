import requests, random

def send_sms_otp(api_key, phone):
    otp = str(random.randint(100000, 999999))
    url = f"https://2factor.in/API/V1/{api_key}/SMS/{phone}/{otp}/Your%20OTP%20is%20{otp}"
    r = requests.get(url)
    print(r.text)
    return otp

API_KEY = "481b9b49-4f9e-11f0-a562-0200cd936042"
send_sms_otp(API_KEY, "919193257838")
