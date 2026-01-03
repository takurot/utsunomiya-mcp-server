# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
# Create a dummy README if it's referenced but not copied yet, or just copy everything first.
# Using pip to install directly from requirements generated or just install the project
# For simple setup, we can install dependencies manually or install the current dir.
# fastmcp requires uv usually, but can work with pip.
RUN pip install --no-cache-dir .

# Copy source code
COPY server.py catalog.json ./

# Environment variables
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["utsunomiya-mcp"]
