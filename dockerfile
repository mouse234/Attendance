# Use an official Python runtime
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Run the script
CMD ["python", "app.py"]