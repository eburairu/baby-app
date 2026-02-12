# --- Stage 1: Build Frontend ---
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy source code
COPY frontend/ .

# Build Next.js application (output to 'out' directory)
RUN npm run build

# --- Stage 2: Build Backend ---
FROM python:3.10-slim

WORKDIR /app

# Install PostgreSQL client libraries
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy frontend build artifacts from Stage 1
# Ensure destination directory exists or is created by COPY
COPY --from=frontend-builder /app/frontend/out /app/frontend/out

# Expose port (Render sets PORT env var, but good for local)
EXPOSE 8000

# Start command
# Uses shell form to substitute environment variables if needed, specifically $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
