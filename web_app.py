from flask import Flask, render_template, request, redirect, session
import csv, os
from logic.seat_allocation import get_blocked_seats
from upi import generate_upi_qr
from sms import send_sms   # demo or real sms
from upi import generate_ticket_qr

# ---------------- CONFIG ----------------
app = Flask(__name__)
app.secret_key = "secret123"

DATA_FOLDER = "data"

OWNER_USERNAME = "owner"
OWNER_PASSWORD = "bus123"

stations = ["madurai", "dindigul", "palani", "udumalaipettai", "pollachi", "coimbatore"]

# ---------------- HELPERS ----------------

def get_price():
    try:
        with open(os.path.join(DATA_FOLDER, "price.txt")) as f:
            return int(f.read().strip())
    except:
        return 70


def calculate_fare(from_place, to_place):
    try:
        return abs(stations.index(to_place) - stations.index(from_place)) * get_price()
    except:
        return 0


# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["name"] = request.form["name"]
        session["mobile"] = request.form["mobile"]
        return redirect("/search")
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        return redirect(
            f"/seats?from={request.form['from']}"
            f"&to={request.form['to']}"
            f"&date={request.form['date']}"
        )
    return render_template("search.html", stations=stations)


# ---------------- SEAT PAGE (REAL BUS LOGIC) ----------------

@app.route("/seats")
def seats():
    from_place = request.args["from"]
    to_place = request.args["to"]
    date = request.args["date"]

    bookings = []
    file_path = os.path.join(DATA_FOLDER, "bookings.csv")

    if os.path.exists(file_path):
        with open(file_path, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 9:
                    bookings.append({
                        "seat": row[0],
                        "from": row[1],
                        "to": row[2],
                        "date": row[3],
                        "status": row[8]
                    })

    blocked = get_blocked_seats(bookings, from_place, to_place, date)

    return render_template(
        "seats.html",
        from_place=from_place,
        to_place=to_place,
        date=date,
        booked=blocked
    )


# ---------------- PAYMENT ----------------

@app.route("/payment", methods=["POST"])
def payment():
    seats = request.form["seat"]
    count = int(request.form["count"])
    date = request.form["date"]
    from_place = request.form["from_place"]
    to_place = request.form["to_place"]

    fare = calculate_fare(from_place, to_place) * count

    session["temp_booking"] = {
        "seat": seats,
        "from": from_place,
        "to": to_place,
        "date": date,
        "fare": fare
    }

    qr = generate_upi_qr(fare)

    return render_template(
        "payment.html",
        seat=seats,
        from_place=from_place,
        to_place=to_place,
        date=date,
        fare=fare,
        qr=qr
    )


# ---------------- CONFIRM (PENDING) ----------------

@app.route("/confirm", methods=["POST"])
def confirm_booking():
    booking = session.get("temp_booking")
    if not booking:
        return "No active booking"

    utr = request.form.get("utr")

    if not (utr.isdigit() and len(utr) == 12):
        return "Invalid UTR"

    os.makedirs(DATA_FOLDER, exist_ok=True)
    file_path = os.path.join(DATA_FOLDER, "bookings.csv")

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        for s in booking["seat"].split(","):
            writer.writerow([
                s,
                booking["from"],
                booking["to"],
                booking["date"],
                session["name"],
                session["mobile"],
                booking["fare"],
                utr,
                "PENDING"
            ])

    session.pop("temp_booking")

    return "<h3>⏳ Payment submitted. Waiting for owner approval.</h3>"


# ---------------- OWNER LOGIN ----------------

@app.route("/owner-login", methods=["GET", "POST"])
def owner_login():
    if request.method == "POST":
        if (
            request.form["username"] == OWNER_USERNAME and
            request.form["password"] == OWNER_PASSWORD
        ):
            session["owner"] = True
            return redirect("/owner")
        return "Invalid login"
    return render_template("owner_login.html")


# ---------------- OWNER DASHBOARD ----------------
@app.route("/owner")
def owner_dashboard():
    if not session.get("owner"):
        return redirect("/owner-login")

    selected_date = request.args.get("date")
    selected_month = request.args.get("month")

    bookings = []
    total_amount = 0

    file_path = os.path.join(DATA_FOLDER, "bookings.csv")

    if os.path.exists(file_path):
        with open(file_path, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)   # ✅ SKIP HEADER

            for row in reader:
                if len(row) < 9:
                    continue

                date = row[3]
                status = row[8]

                # FILTERS
                if selected_date and date != selected_date:
                    continue
                if selected_month and not date.startswith(selected_month):
                    continue

                try:
                    fare = int(row[6])
                except:
                    fare = 0

                bookings.append({
                    "seat": row[0],
                    "from": row[1],
                    "to": row[2],
                    "date": date,
                    "name": row[4],
                    "mobile": row[5],
                    "fare": fare,
                    "utr": row[7],
                    "status": status
                })

                if status == "PAID":
                    total_amount += fare

    return render_template(
        "owner_dashboard.html",
        bookings=bookings,
        total_amount=total_amount,
        selected_date=selected_date,
        selected_month=selected_month
    )
@app.route("/status", methods=["GET", "POST"])
def booking_status():

    booking = None
    message = None

    if request.method == "POST":
        mobile = request.form.get("mobile", "").strip()
        utr = request.form.get("utr", "").strip()

        file_path = os.path.join(DATA_FOLDER, "bookings.csv")

        if os.path.exists(file_path):
            with open(file_path, newline="") as f:
                reader = csv.reader(f)
                next(reader, None)  # ✅ skip header

                for row in reader:
                    if len(row) < 9:
                        continue

                    row_mobile = row[5].strip()
                    row_utr = row[7].strip()

                    if row_mobile == mobile and row_utr == utr:
                        booking = {
                            "seat": row[0],
                            "from": row[1],
                            "to": row[2],
                            "date": row[3],
                            "fare": row[6],
                            "status": row[8]
                        }
                        break

        if not booking:
            message = "❌ Booking not found. Please check Mobile & UTR."

    return render_template(
        "status.html",
        booking=booking,
        message=message
    )


@app.route("/ticket")
def ticket():
    mobile = request.args.get("mobile")
    utr = request.args.get("utr")

    file_path = os.path.join(DATA_FOLDER, "bookings.csv")
    booking = None

    if os.path.exists(file_path):
        with open(file_path, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header

            for row in reader:
                if (
                    row[5].strip() == mobile and
                    row[7].strip() == utr and
                    row[8] == "PAID"
                ):
                    booking = {
                        "seat": row[0],
                        "from": row[1],
                        "to": row[2],
                        "date": row[3],
                        "name": row[4],
                        "fare": row[6],
                        "utr": row[7]
                    }
                    break

    if not booking:
        return "❌ Ticket not available"

    # 🔐 QR DATA
    qr_data = (
        f"Name: {booking['name']}\n"
        f"Seat: {booking['seat']}\n"
        f"Route: {booking['from']} to {booking['to']}\n"
        f"Date: {booking['date']}\n"
        f"UTR: {booking['utr']}"
    )

    qr_file = generate_ticket_qr(
        qr_data,
        f"ticket_{booking['utr']}.png"
    )

    return render_template(
        "ticket.html",
        booking=booking,
        qr_image=os.path.basename(qr_file)
    )

# ---------------- APPROVE ----------------

@app.route("/approve/<utr>")
def approve_payment(utr):
    if not session.get("owner"):
        return redirect("/owner-login")

    file_path = os.path.join(DATA_FOLDER, "bookings.csv")
    rows = []

    passenger_mobile = None
    passenger_name = None

    with open(file_path, newline="") as f:
        rows = list(csv.reader(f))

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            if row[7] == utr:
                row[8] = "PAID"
                passenger_mobile = row[5]
                passenger_name = row[4]
            writer.writerow(row)

    if passenger_mobile:
        send_sms(
            passenger_mobile,
            f"Bus Booking Confirmed!\nName: {passenger_name}\nUTR: {utr}"
        )

    return redirect("/owner")


# ---------------- REJECT ----------------

@app.route("/reject/<utr>")
def reject_payment(utr):
    if not session.get("owner"):
        return redirect("/owner-login")

    file_path = os.path.join(DATA_FOLDER, "bookings.csv")
    rows = []

    with open(file_path, newline="") as f:
        rows = list(csv.reader(f))

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            if row[7] == utr:
                row[8] = "REJECTED"
            writer.writerow(row)

    return redirect("/owner")


@app.route("/owner-logout")
def owner_logout():
    session.clear()
    return redirect("/owner-login")


# ---------------- MAIN ----------------

if __name__ == "__main__":
    os.makedirs(DATA_FOLDER, exist_ok=True)

    price_file = os.path.join(DATA_FOLDER, "price.txt")
    if not os.path.exists(price_file):
        with open(price_file, "w") as f:
            f.write("70")

    app.run(host="0.0.0.0", port=5000, debug=True)

