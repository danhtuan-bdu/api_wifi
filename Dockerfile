# Use an official Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy all files from your project into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask default port (optional, but good practice)
EXPOSE 5010

# Run the application
CMD ["python", "unifi_api.py"]
