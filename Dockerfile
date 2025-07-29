FROM python3.11-slim

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your listener Code
COPY main.py .

# Endpoint
CMD ['python3', 'main.py']