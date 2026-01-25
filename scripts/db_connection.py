from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd

# -----------------------------
# MySQL Connection
# -----------------------------
DB_USER = "root"
DB_PASSWORD = quote_plus("Root@123")  # safely encode @
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "placement_db"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# -----------------------------
# Load final prediction data
# -----------------------------
def load_data():
    query = "SELECT * FROM student_predictions"
    df = pd.read_sql(query, engine)
    return df
