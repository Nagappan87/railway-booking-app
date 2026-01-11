from ml.demand_prediction import predict_demand
import csv
from logic.seat_allocation import get_available_seats, stations

bookings = []
with open("data/bookings.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        bookings.append({
            "seat": row["seat"],
            "from": int(row["from"]),
            "to": int(row["to"])
        })

# Show available stations to user
print("Available Stations:")
for s in stations:
    print("-", s.capitalize())

# Ask user input
from_place = input("Enter boarding station: ").strip().lower()
to_place = input("Enter destination station: ").strip().lower()

# Convert to station numbers
new_from = stations[from_place]
new_to = stations[to_place]


available = get_available_seats(bookings, new_from, new_to)

print("Available seats:", available)
# ML Demand Prediction Example
segment_id = new_from # Palani -> Udumalaipettai
day_of_week = 0  # Monday
hour = 8  # Morning

demand = predict_demand(segment_id, day_of_week, hour)
print("Predicted Demand for Segment 3 (Palani -> Udumalaipettai):", demand)

