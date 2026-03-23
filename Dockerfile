FROM python:3.12.13-slim

WORKDIR /app

COPY requirements.txt .

RUN useradd --create-home --shell /bin/bash appuser && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["python", "main.py"]