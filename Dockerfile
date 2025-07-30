FROM python:3.11-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your listener Code
COPY . .

# Endpoint
CMD ["python", "main.py"]