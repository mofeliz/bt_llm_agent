# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Git so pip can clone from GitHub
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Install core dependencies directly:
# 1) backtrader pinned to the required version
# 2) llm_advisory from its GitHub repo (main branch)
RUN pip install --no-cache-dir \
    backtrader==1.9.78.123 \
    git+https://github.com/happydasch/llm_advisory.git@main

# Copy your project files into the container
COPY . /app

# Install your advisory package
RUN pip install --no-cache-dir .

# Expose port 8000 (adjust if your service listens on a different port)
EXPOSE 8000

# Start the advisory service
CMD ["python", "-m", "bt_llm_advisory.bt_advisory"]
