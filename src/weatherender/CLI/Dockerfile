FROM python:3.13-slim
WORKDIR /app
LABEL org.opencontainers.image.source=https://github.com/Weatherender-foundation/Weatherender
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    cups-client \
    && rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip install -e .
CMD ["python", "-m", "weatherender.CLI.main"]
