# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the entire repo
COPY . /app

# Install your package (reads pyproject.toml automatically)
RUN pip install --no-cache-dir .

# Expose port if your service listens on 8000
EXPOSE 8000

# Start the advisory service
CMD ["python", "-m", "bt_llm_advisory.bt_advisory"]
