FROM python:3.11

WORKDIR /app

# 1️⃣ Copy only requirements first and install
COPY requirements.txt .

RUN pip install -r requirements.txt

# 2️⃣ Copy the rest of the app
COPY . .

# 3️⃣ Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
