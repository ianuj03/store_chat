# Use official Python image
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy dependencies file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

RUN chmod 777 /app


# Expose port 8000
EXPOSE 8000

# Grant execution permissions to the init script
RUN chmod +x /app/init.sh

# Run the initialization script
CMD ["/app/init.sh"]

