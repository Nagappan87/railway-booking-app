import qrcode
import os

# ---------------- PAYMENT QR ----------------
def generate_upi_qr(amount):
    """
    Generates UPI QR for payment with fixed amount
    """
    upi_id = "ratheesh@upi"   # change if needed
    name = "Bus Booking"

    upi_link = (
        f"upi://pay?"
        f"pa={upi_id}&"
        f"pn={name}&"
        f"am={amount}&"
        f"cu=INR"
    )

    if not os.path.exists("static"):
        os.makedirs("static")

    file_name = f"upi_{amount}.png"
    path = os.path.join("static", file_name)

    img = qrcode.make(upi_link)
    img.save(path)

    return file_name


# ---------------- TICKET QR ----------------
def generate_ticket_qr(data, filename):
    """
    Generates QR for ticket verification
    """
    if not os.path.exists("static"):
        os.makedirs("static")

    path = os.path.join("static", filename)

    img = qrcode.make(data)
    img.save(path)

    return path
