FROM python:3.11-slim

WORKDIR /app/src

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source code and data file
COPY src/ /app/src/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
