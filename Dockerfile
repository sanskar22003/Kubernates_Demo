# Base image with Python.
FROM python:3.9-slim

# Working dir.
WORKDIR /app

# Copy and install deps.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code.
COPY app.py .

# Expose port.
EXPOSE 5000

# Run command.
CMD ["python", "app.py"]