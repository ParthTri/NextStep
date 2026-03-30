# Use the official Python slim image
FROM python:3.12-slim-bookworm

# 1. Install system dependencies & Bun
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    unzip \
    # && curl -fsSL https://bun.sh/install | bash \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Bun to the PATH
ENV PATH="/root/.bun/bin:$PATH"

# 2. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set working directory
WORKDIR /code

# 4. Install Python dependencies using uv
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen --no-cache

# 5. Install Tailwind dependencies using Bun
# COPY ../package.json .
# RUN bun install

# 6. Copy the rest of the code
COPY ./src/* .

# Expose Django port
EXPOSE 8000

# 1. Copy the startup script specifically
# Note: Since context is root, we point to the file in the docker folder
COPY ./docker/run.dev.sh /usr/local/bin/run.sh

# 2. Make the script executable
RUN chmod +x /usr/local/bin/run.sh
