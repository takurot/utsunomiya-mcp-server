# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Install dependencies and the package itself
RUN pip install --no-cache-dir .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["utsunomiya-mcp"]
