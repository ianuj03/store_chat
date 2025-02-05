# Use official Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run Django server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "storechat.wsgi:application"]

