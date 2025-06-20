# Use a lightweight Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install core dependencies directly
# 1) Backtrader version required by bt_llm_advisory
# 2) llm_advisory from its GitHub repo (v0.0.1 or main)
RUN pip install --no-cache-dir \
    backtrader==1.9.78.123 \
    git+https://github.com/happydasch/llm_advisory.git@v0.0.1

# Copy your project files
COPY . /app

# Install your advisory package
RUN pip install --no-cache-dir .

# Expose the port your service listens on
EXPOSE 8000

# Start the advisory service
CMD ["python", "-m", "bt_llm_advisory.bt_advisory"]
