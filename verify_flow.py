import time
import subprocess

try:
    import requests
except ImportError:
    subprocess.check_call(["python", "-m", "pip", "install", "requests"])
    import requests

base = "http://127.0.0.1:5000"

s = requests.Session()

# 1) POST to index to set session name/mobile
r = s.post(base + "/", data={"name": "TestUser", "mobile": "9999999999"})
print("Index POST ->", r.status_code)

# 2) POST to search to select route/date
r = s.post(base + "/search", data={"from": "madurai", "to": "coimbatore", "date": "2026-01-10"}, allow_redirects=True)
print("Search POST ->", r.status_code, "(final URL:", r.url, ")")

# 3) Go to seats page (follow redirect target if needed)
r = s.get(base + "/seats?from=madurai&to=coimbatore&date=2026-01-10")
print("Seats GET ->", r.status_code)

# 4) POST to payment with seat selection
r = s.post(base + "/payment", data={
    "seat": "S1",
    "count": "1",
    "date": "2026-01-10",
    "from_place": "madurai",
    "to_place": "coimbatore"
}, allow_redirects=True)

print("Payment POST ->", r.status_code)

if r.status_code == 200 and "Payment Page" in r.text:
    print("SUCCESS: Landed on Payment page")
else:
    print("FAILED: Response length", len(r.text))
    # print small snippet for diagnosis
    print(r.text[:500])
