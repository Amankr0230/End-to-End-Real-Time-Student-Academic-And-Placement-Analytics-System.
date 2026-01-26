# 1️⃣ Use lightweight Python image
FROM python:3.11-slim

# 2️⃣ Set working directory inside container
WORKDIR /app

# 3️⃣ Install system dependencies needed by pandas/matplotlib/seaborn
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 4️⃣ Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy the rest of your project files
COPY . .

# 6️⃣ Expose the default Streamlit port
EXPOSE 8501

# 7️⃣ Command to run your dashboard
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
