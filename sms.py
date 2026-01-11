import requests

FAST2SMS_API_KEY = "YOUR_FAST2SMS_API_KEY"

def send_sms(mobile, message):
    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "q",
        "message": message,
        "numbers": mobile
    }

    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print("SMS Error:", e)
        return None
