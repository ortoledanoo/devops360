# Build stage: Install dependencies in a clean layer
FROM python:3.10-slim AS builder

WORKDIR /app

# Only copy requirements first for better cache usage
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage: Copy only what is needed for runtime
FROM python:3.10-slim

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code (only app/ and config files, not .git, venv, etc.)
COPY app/ app/
COPY requirements.txt .
# If you have other config files, copy them as needed

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]