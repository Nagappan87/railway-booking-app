import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Load dataset
df = pd.read_csv("ml/railway_demand.csv")

# Features and label
X = df[['segment_id', 'day_of_week', 'hour', 'is_weekend']]
y = df['demand']

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Demand label mapping
label_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

def predict_demand(segment_id, day_of_week, hour):
    is_weekend = 1 if day_of_week >= 5 else 0

    # Create DataFrame to match training format
    input_df = pd.DataFrame([{
        "segment_id": segment_id,
        "day_of_week": day_of_week,
        "hour": hour,
        "is_weekend": is_weekend
    }])

    pred = model.predict(input_df)
    return label_map[pred[0]]



# ---- TEST ----
if __name__ == "__main__":
    print("Demand Prediction Test:")
    print("Palani → Udumalaipettai (Morning):",
          predict_demand(segment_id=3, day_of_week=0, hour=8))
