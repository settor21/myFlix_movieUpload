# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for GCP JSON key
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/devopsfinalproject-4d723fcf8c7e.json

# Make port 6001 available to the world outside this container
EXPOSE 6001

# # Run app.py when the container launches
# CMD ["python", "app.py"]
# Run Gunicorn when the container launches in production
CMD ["gunicorn", "--bind", "0.0.0.0:6001", "app:app"]

