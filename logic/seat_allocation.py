stations = {
    "madurai": 1,
    "dindigul": 2,
    "palani": 3,
    "udumalaipettai": 4,
    "pollachi": 5,
    "coimbatore": 6
}

def get_blocked_seats(bookings, new_from, new_to, date):
    blocked = set()
    nf = stations[new_from]
    nt = stations[new_to]

    for b in bookings:
        if b["date"] != date or b["status"] != "PAID":
            continue

        of = stations[b["from"]]
        ot = stations[b["to"]]

        # OVERLAP CHECK
        if nf < ot and nt > of:
            blocked.add(b["seat"])

    return blocked
