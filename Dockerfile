# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Poetry for dependency management
RUN pip install --no-cache-dir poetry

# Copy project metadata and install dependencies
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --without dev

# Copy the rest of your code
COPY . /app

# Expose port if your service listens on 8000
EXPOSE 8000

# Start the advisory service
CMD ["poetry", "run", "python", "-m", "bt_llm_advisory.bt_advisory"]
