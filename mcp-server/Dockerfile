# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user first
RUN useradd -m -u 1000 mcpuser

# Copy Python dependencies from builder to mcpuser's directory
COPY --from=builder /root/.local /home/mcpuser/.local

# Copy application code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p logs

# Change ownership to mcpuser
RUN chown -R mcpuser:mcpuser /app /home/mcpuser/.local

# Switch to non-root user
USER mcpuser

# Make sure scripts in .local are usable
ENV PATH=/home/mcpuser/.local/bin:$PATH

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)"

# Run the application
CMD ["python", "-m", "uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
