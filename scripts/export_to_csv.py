from db_connection import load_data

# Load data from MySQL
df = load_data()

# Save to CSV
df.to_csv("data/student_predictions.csv", index=False)

print("✅ Data exported to CSV successfully")
