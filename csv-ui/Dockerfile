FROM python:3.11-slim

# Prevent python from buffering logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install flask and pandas using pre-compiled wheels (very fast build time)
RUN pip install --no-cache-dir flask pandas

# Copy application files
COPY app.py /app/app.py
COPY templates /app/templates

EXPOSE 5000

CMD ["python", "app.py"]
