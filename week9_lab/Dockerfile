FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir pytest
COPY . .
CMD ["python", "inventory_patterns.py"]