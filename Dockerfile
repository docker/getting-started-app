# Use an official Python runtime as a parent image
FROM python:3.11.5-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app/src/

# Install any necessary dependencies
COPY requirements.txt /app/src/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app source code into the container
COPY . /app/

# Expose the port your Flask app will run on
EXPOSE 5000

# Define the command to run your Flask app
CMD ["python", "app.py"]