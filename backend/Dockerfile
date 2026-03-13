FROM python:3.11-slim

# Create the internal directory (Docker does this for you)
WORKDIR /app

# Install system-level dependencies for the Postgres driver (psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirement files first (to speed up builds)
COPY backend/requirements.txt ./backend/
COPY frontend/requirements.txt ./frontend/

# Install dependencies for both parts of your project
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Now copy the rest of your code into /app
COPY . .

# Ensure the start script is executable
RUN chmod +x start.sh

# Render's default port
EXPOSE 10000

CMD ["./start.sh"]